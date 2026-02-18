"""Legacy bridge that adapts canonical zen principles into flat Violation models.

The ``RulesAdapter`` implements the Adapter pattern: it translates the rich
``ZenPrinciple`` / ``LanguageZenPrinciples`` hierarchy defined in
``rules/base_models.py`` into the ``Violation`` list that the original monolithic
analyzer pipeline expected.  New code should prefer the ``DetectionPipeline``
architecture; this adapter exists so that callers written against the old
dictionary-based API continue to work without modification.

All data access uses Pydantic model attributes — never raw dictionary keys.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from mcp_zen_of_languages.models import (
    CyclomaticSummary,
    DependencyAnalysis,
    Violation,
)
from mcp_zen_of_languages.rules import get_language_zen
from mcp_zen_of_languages.rules.base_models import (
    DetectorConfig,
    LanguageZenPrinciples,
    ZenPrinciple,
)


class RulesAdapterConfig(BaseModel):
    """Threshold overrides that callers pass to ``RulesAdapter``.

    When a field is ``None`` the adapter falls back to the threshold
    embedded in the ``ZenPrinciple.metrics`` dictionary.  Setting an
    explicit value here takes precedence, allowing project-level
    customisation without editing the canonical rule definitions.

    Attributes:
        max_nesting_depth: Override for the maximum indentation depth before
            a nesting violation is emitted.
        max_cyclomatic_complexity: Override for the cyclomatic-complexity ceiling.
        min_maintainability_index: Override for the minimum acceptable
            maintainability index (Radon scale).
        severity_threshold: Floor used by ``get_critical_violations`` to
            filter low-severity findings.  Defaults to 5 (1–10 scale).
    """

    max_nesting_depth: int | None = None
    max_cyclomatic_complexity: int | None = None
    min_maintainability_index: float | None = None
    severity_threshold: int = Field(default=5, ge=1, le=10)


class RulesAdapter:
    """Legacy bridge that projects ``ZenPrinciple`` definitions onto flat ``Violation`` lists.

    The adapter iterates every principle registered for a language, inspects its
    ``metrics`` dictionary, and applies lightweight heuristic checks (nesting depth,
    cyclomatic complexity, maintainability index, dependency cycles, and regex-based
    pattern matching).  Each failed check produces a ``Violation`` that downstream
    reporters can render.

    This class exists to preserve backward-compatibility with the pre-pipeline
    analysis path.  New detectors should be implemented as ``ViolationDetector``
    subclasses and registered via ``DetectionPipeline``.

    See Also:
        ``analyzers.pipeline.DetectionPipeline`` — the modern replacement.
        ``rules.base_models.ZenPrinciple`` — canonical principle definitions.
    """

    def __init__(self, language: str, config: RulesAdapterConfig | None = None):
        """Bind the adapter to a language and optional threshold overrides.

        Loads the ``LanguageZenPrinciples`` for *language* from the global
        ``ZEN_REGISTRY`` on construction so that subsequent ``find_violations``
        calls can iterate the principle set without repeated lookups.

        Args:
            language: Lowercase language key (e.g. ``"python"``, ``"rust"``).
            config: Threshold overrides.  When ``None``, a default
                ``RulesAdapterConfig`` with all overrides unset is created.
        """
        self.language = language
        self.config = config or RulesAdapterConfig()
        self.lang_zen: LanguageZenPrinciples | None = get_language_zen(language)

    def find_violations(
        self,
        code: str,
        cyclomatic_summary: CyclomaticSummary | None = None,
        maintainability_index: float | None = None,
        dependency_analysis: DependencyAnalysis | None = None,
    ) -> list[Violation]:
        """Walk every zen principle for this language and apply lightweight heuristic checks.

        Each principle's ``metrics`` dictionary determines which checks fire.
        For example, a principle containing ``max_nesting_depth`` triggers the
        nesting check, while ``detect_circular_dependencies`` triggers the
        dependency-cycle check.  Results from all principles are concatenated
        into a single flat list.

        Args:
            code: Source code to analyse.
            cyclomatic_summary: Pre-computed cyclomatic-complexity metrics,
                typically produced by ``radon``.
            maintainability_index: Radon maintainability index (0–100 scale).
            dependency_analysis: Import-graph analysis produced by upstream
                dependency resolution.

        Returns:
            All violations found across every registered principle.
        """
        violations: list[Violation] = []

        if not self.lang_zen:
            return violations

        for principle in self.lang_zen.principles:
            # Get metrics from the principle (Pydantic model attribute)
            principle_metrics = principle.metrics or {}

            # Check nesting depth
            violations.extend(
                self._check_nesting_depth(code, principle, principle_metrics)
            )

            # Check cyclomatic complexity
            if cyclomatic_summary is not None:
                violations.extend(
                    self._check_cyclomatic_complexity(
                        cyclomatic_summary, principle, principle_metrics
                    )
                )

            # Check maintainability index
            if maintainability_index is not None:
                violations.extend(
                    self._check_maintainability_index(
                        maintainability_index, principle, principle_metrics
                    )
                )

            # Check dependency issues
            if dependency_analysis is not None:
                violations.extend(
                    self._check_dependencies(
                        dependency_analysis, principle, principle_metrics
                    )
                )

            # Check detectable patterns
            violations.extend(self._check_patterns(code, principle))

        return violations

    def _check_nesting_depth(
        self,
        code: str,
        principle: ZenPrinciple,
        metrics: dict,
    ) -> list[Violation]:
        """Measure indentation depth and flag code exceeding the allowed limit.

        Depth is approximated by counting leading 4-space indents.  The
        threshold comes from ``config.max_nesting_depth`` if set, otherwise
        from the principle's ``max_nesting_depth`` metric.

        Args:
            code: Source text whose indentation levels are measured.
            principle: The zen principle supplying severity and fallback threshold.
            metrics: The principle's ``metrics`` dict; skipped when
                ``max_nesting_depth`` is absent.

        Returns:
            A single-element list when the deepest nesting exceeds the limit,
            otherwise an empty list.
        """
        violations: list[Violation] = []

        if "max_nesting_depth" not in metrics:
            return violations

        # Use config override if provided, otherwise use principle metric
        max_allowed = (
            self.config.max_nesting_depth
            if self.config.max_nesting_depth is not None
            else metrics["max_nesting_depth"]
        )

        # Calculate actual nesting depth
        depth = max((line.count("    ") for line in code.splitlines()), default=0)

        if depth > max_allowed:
            violations.append(
                Violation(
                    principle=principle.principle,
                    severity=principle.severity,
                    message=f"Nesting depth {depth} exceeds maximum {max_allowed}",
                )
            )

        return violations

    def _check_cyclomatic_complexity(
        self,
        cyclomatic_summary: CyclomaticSummary,
        principle: ZenPrinciple,
        metrics: dict,
    ) -> list[Violation]:
        """Compare average cyclomatic complexity against the allowed ceiling.

        Reads ``cyclomatic_summary.average`` and checks it against
        ``config.max_cyclomatic_complexity`` (or the principle metric
        fallback).  Errors during attribute access are swallowed so that
        malformed summaries never crash the adapter.

        Args:
            cyclomatic_summary: Pre-computed summary whose ``average`` field
                is compared against the threshold.
            principle: Supplies severity and the fallback complexity ceiling.
            metrics: Skipped when ``max_cyclomatic_complexity`` is absent.

        Returns:
            A single-element list when average complexity is too high,
            otherwise an empty list.
        """
        violations: list[Violation] = []

        if "max_cyclomatic_complexity" not in metrics:
            return violations

        try:
            # Access Pydantic model attribute
            avg_complexity = cyclomatic_summary.average

            # Use config override if provided
            max_allowed = (
                self.config.max_cyclomatic_complexity
                if self.config.max_cyclomatic_complexity is not None
                else metrics["max_cyclomatic_complexity"]
            )

            if avg_complexity > max_allowed:
                violations.append(
                    Violation(
                        principle=principle.principle,
                        severity=principle.severity,
                        message=(
                            f"Average cyclomatic complexity {avg_complexity:.2f} "
                            f"exceeds maximum {max_allowed}"
                        ),
                    )
                )
        except (AttributeError, KeyError, TypeError):
            # Log error but don't fail - graceful degradation
            pass

        return violations

    def _check_maintainability_index(
        self,
        maintainability_index: float,
        principle: ZenPrinciple,
        metrics: dict,
    ) -> list[Violation]:
        """Flag source whose maintainability index falls below the required floor.

        Args:
            maintainability_index: Radon MI score (0–100).  Lower values
                indicate harder-to-maintain code.
            principle: Supplies severity and the fallback MI floor.
            metrics: Skipped when ``min_maintainability_index`` is absent.

        Returns:
            A single-element list when the MI is below the threshold,
            otherwise an empty list.
        """
        violations: list[Violation] = []

        if "min_maintainability_index" not in metrics:
            return violations

        try:
            # Use config override if provided
            min_required = (
                self.config.min_maintainability_index
                if self.config.min_maintainability_index is not None
                else metrics["min_maintainability_index"]
            )

            if maintainability_index < min_required:
                violations.append(
                    Violation(
                        principle=principle.principle,
                        severity=principle.severity,
                        message=(
                            f"Maintainability index {maintainability_index:.2f} "
                            f"below minimum {min_required}"
                        ),
                    )
                )
        except (KeyError, TypeError):
            pass

        return violations

    def _check_dependencies(
        self,
        dependency_analysis: DependencyAnalysis | dict | None,
        principle: ZenPrinciple,
        metrics: dict,
    ) -> list[Violation]:
        """Detect circular-dependency and god-module violations from an import graph.

        This method is defensive: it accepts ``DependencyAnalysis`` Pydantic
        models **or** legacy dictionaries and normalises cycles and edges
        into plain Python lists before analysis.

        Two independent checks run when the relevant metric keys are present:

        * **Circular dependencies** — reported when ``detect_circular_dependencies``
          is truthy and at least one cycle exists.
        * **Excessive dependencies** (god module) — reported when any node in the
          edge list exceeds ``max_dependencies``.

        Args:
            dependency_analysis: Import-graph data (Pydantic model or dict).
            principle: Supplies severity and the principle name for messages.
            metrics: Must contain ``detect_circular_dependencies`` and/or
                ``max_dependencies`` for the respective checks to fire.

        Returns:
            Zero or more violations from the dependency checks.
        """
        violations: list[Violation] = []

        if dependency_analysis is None:
            return violations

        # Normalize cycles into list[list[str]]
        cycles_list: list[list[str]] = []
        try:
            if hasattr(dependency_analysis, "cycles"):
                raw_cycles = dependency_analysis.cycles or []
            elif isinstance(dependency_analysis, dict):
                raw_cycles = dependency_analysis.get("cycles", [])
            else:
                # Fallback: we don't know the shape; attempt to read `cycles`
                # attr or treat as empty
                raw_cycles = []

            # Normalize into a list of iterables safely
            normalized_cycles: list[list[str]] = []
            # Only handle well-known iterable shapes (list/tuple) to keep
            # type-checker happy
            iterable_cycles = (
                raw_cycles if isinstance(raw_cycles, (list, tuple)) else []
            )

            for c in iterable_cycles:
                try:
                    if hasattr(c, "cycle") and isinstance(
                        getattr(c, "cycle"), (list, tuple)
                    ):
                        seq = c.cycle
                    elif isinstance(c, (list, tuple)):
                        seq = c
                    else:
                        seq = [str(c)]

                    # Only iterate sequences to satisfy type-checker
                    if isinstance(seq, (list, tuple)):
                        normalized_cycles.append([str(x) for x in seq])
                    else:
                        # Fallback single item
                        normalized_cycles.append([str(seq)])
                except Exception:
                    continue

            cycles_list = normalized_cycles
        except Exception:
            cycles_list = []

        # Check for circular dependencies
        if metrics.get("detect_circular_dependencies") and cycles_list:
            cycle_count = len(cycles_list)
            pretty = []
            for c in cycles_list[:3]:
                pretty.append(" -> ".join(c))
            violations.append(
                Violation(
                    principle=principle.principle,
                    severity=principle.severity,
                    message=(
                        f"Circular dependencies detected: {cycle_count} cycle(s). "
                        f"Cycles: {', '.join(pretty)}"
                        f"{'...' if cycle_count > 3 else ''}"
                    ),
                )
            )

        # Check for excessive dependencies (God module)
        if "max_dependencies" in metrics:
            try:
                max_allowed = metrics["max_dependencies"]

                # Build deps_map from edges; support model or dict shapes
                deps_map: dict[str, list[str]] = {}
                raw_edges = []
                if hasattr(dependency_analysis, "edges"):
                    raw_edges = dependency_analysis.edges or []
                elif isinstance(dependency_analysis, dict):
                    raw_edges = dependency_analysis.get("edges", [])

                # Ensure iterable
                # Only accept list/tuple edges; ignore unknown shapes
                raw_edges = raw_edges if isinstance(raw_edges, (list, tuple)) else []

                for edge in raw_edges:
                    # edge may be tuple/list or model; normalize
                    if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                        a, b = edge[0], edge[1]
                    else:
                        # Try to unpack dataclass-like objects
                        try:
                            a = getattr(edge, "from")
                            b = getattr(edge, "to")
                        except Exception:
                            continue
                    deps_map.setdefault(str(a), []).append(str(b))

                for node, deps in deps_map.items():
                    if len(deps) > max_allowed:
                        violations.append(
                            Violation(
                                principle=principle.principle,
                                severity=principle.severity,
                                message=(
                                    f"Module '{node}' has {len(deps)} dependencies, "
                                    f"exceeds maximum {max_allowed}"
                                ),
                            )
                        )
            except Exception:
                pass

        return violations

    def _check_patterns(
        self,
        code: str,
        principle: ZenPrinciple,
    ) -> list[Violation]:
        """Scan source text against the principle's ``detectable_patterns`` regexes.

        Each pattern is compiled once via ``ZenPrinciple.compiled_patterns``
        and matched with ``re.search``.  A violation is emitted for every
        pattern that matches anywhere in *code*.

        Args:
            code: Source text to search.
            principle: Supplies the regex patterns and violation metadata.

        Returns:
            One violation per matching pattern, or an empty list.
        """
        violations: list[Violation] = []

        # Use compiled patterns helper on the Pydantic model
        try:
            compiled = principle.compiled_patterns()
        except Exception:
            compiled = []

        for cre in compiled:
            try:
                if cre.search(code):
                    violations.append(
                        Violation(
                            principle=principle.principle,
                            severity=principle.severity,
                            message=f"Detected anti-pattern matching: '{cre.pattern}'",
                        )
                    )
            except Exception:
                continue

        return violations

    def get_critical_violations(self, violations: list[Violation]) -> list[Violation]:
        """Return only violations whose severity meets or exceeds ``config.severity_threshold``.

        Args:
            violations: Full violation list, typically from ``find_violations``.

        Returns:
            Subset of *violations* at or above the configured severity floor.
        """
        return [v for v in violations if v.severity >= self.config.severity_threshold]

    def get_detector_config(self, detector_name: str) -> DetectorConfig:
        """Aggregate zen-principle metrics into a single ``DetectorConfig``.

        Walks every principle for the bound language and collects thresholds,
        regex patterns, and metadata that match *detector_name*.  The result
        lets detectors stay language-agnostic — they only consume the config
        shape, never raw principle objects.

        Args:
            detector_name: Key used to filter relevant metrics (e.g.
                ``"cyclomatic_complexity"``).

        Returns:
            A ``DetectorConfig`` ready to be passed into a
            ``ViolationDetector.detect`` call.

        See Also:
            ``rules.base_models.DetectorConfig`` — the returned Pydantic model.
        """
        from mcp_zen_of_languages.rules.base_models import DetectorConfig

        thresholds: dict[str, float] = {}
        patterns: list[str] = []
        metadata: dict[str, object] = {}

        if not self.lang_zen:
            return DetectorConfig(
                name=detector_name,
                thresholds=thresholds,
                patterns=patterns,
                metadata=metadata,
            )

        # Aggregate metrics across principles and choose values relevant to detector
        for p in self.lang_zen.principles:
            if p.metrics:
                for k, v in p.metrics.items():
                    # Simple heuristic: include metrics that mention detector name
                    # or common keys
                    if detector_name in k or k in (
                        "max_function_length",
                        "max_cyclomatic_complexity",
                        "max_nesting_depth",
                        "max_class_length",
                        "min_maintainability_index",
                    ):
                        try:
                            thresholds[k] = float(v)
                        except Exception:
                            metadata[k] = v
            if p.detectable_patterns:
                patterns.extend(p.detectable_patterns)

        return DetectorConfig(
            name=detector_name,
            thresholds=thresholds,
            patterns=patterns,
            metadata=metadata,
        )

    def summarize_violations(self, violations: list[Violation]) -> dict[str, int]:
        """Bucket violations into four severity bands and return per-band counts.

        Bands: *critical* (9–10), *high* (7–8), *medium* (4–6), *low* (1–3).

        Args:
            violations: Violation list to summarise.

        Returns:
            Dict with keys ``"critical"``, ``"high"``, ``"medium"``, ``"low"``
            mapped to integer counts.
        """
        summary = {
            "critical": 0,  # 9-10
            "high": 0,  # 7-8
            "medium": 0,  # 4-6
            "low": 0,  # 1-3
        }

        for violation in violations:
            if violation.severity >= 9:
                summary["critical"] += 1
            elif violation.severity >= 7:
                summary["high"] += 1
            elif violation.severity >= 4:
                summary["medium"] += 1
            else:
                summary["low"] += 1

        return summary
