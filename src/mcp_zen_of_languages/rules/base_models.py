"""Canonical Pydantic models that define the shape of every zen principle.

This module is the single source of truth for the ``ZenPrinciple`` /
``LanguageZenPrinciples`` hierarchy.  Language rule files (e.g.
``languages/python/rules.py``) instantiate these models; analyzers,
detectors, and the ``DetectionPipeline`` consume them.

Key concepts:

* Each **ZenPrinciple** pairs a human-readable principle statement with
  machine-readable ``metrics``, ``detectable_patterns``, and ``violations``
  that drive the detection pipeline.
* **Severity** (1-10) controls violation priority and is persisted into
  every ``ViolationReport``.
* ``LanguageZenPrinciples`` groups all principles for a language together
  with provenance metadata (philosophy, source URL).
"""

import re
from enum import Enum, StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class SeverityLevel(int, Enum):
    """Numeric severity scale (1-10) used to rank zen violations.

    Levels are grouped into four bands:

    * **Informational** (1-3): Style suggestions with no functional impact.
    * **Warning** (4-6): Likely maintainability or readability concerns.
    * **Error** (7-8): Strong anti-patterns that hinder correctness.
    * **Critical** (9-10): Severe violations requiring immediate attention.
    """

    INFORMATIONAL_LOW = 1
    INFORMATIONAL_MEDIUM = 2
    INFORMATIONAL_HIGH = 3
    WARNING_LOW = 4
    WARNING_MEDIUM = 5
    WARNING_HIGH = 6
    ERROR_LOW = 7
    ERROR_HIGH = 8
    CRITICAL_LOW = 9
    CRITICAL_HIGH = 10


class PrincipleCategory(StrEnum):
    """Taxonomy tag that groups related zen principles.

    Analyzers and reporters use these categories to organise output (e.g.
    "show all readability violations") and to build per-category coverage
    reports.  Each ``ZenPrinciple`` carries exactly one category.
    """

    READABILITY = "readability"
    CLARITY = "clarity"
    COMPLEXITY = "complexity"
    ARCHITECTURE = "architecture"
    STRUCTURE = "structure"
    CONSISTENCY = "consistency"
    ERROR_HANDLING = "error_handling"
    CORRECTNESS = "correctness"
    IDIOMS = "idioms"
    ORGANIZATION = "organization"
    ASYNC = "async"
    IMMUTABILITY = "immutability"
    TYPE_SAFETY = "type_safety"
    DESIGN = "design"
    FUNCTIONAL = "functional"
    CONFIGURATION = "configuration"
    CONCURRENCY = "concurrency"
    INITIALIZATION = "initialization"
    PERFORMANCE = "performance"
    DEBUGGING = "debugging"
    SAFETY = "safety"
    OWNERSHIP = "ownership"
    RESOURCE_MANAGEMENT = "resource_management"
    MEMORY_MANAGEMENT = "memory_management"
    SCOPE = "scope"
    SECURITY = "security"
    ROBUSTNESS = "robustness"
    USABILITY = "usability"
    NAMING = "naming"
    DOCUMENTATION = "documentation"


class ViolationSpec(BaseModel):
    """A single concrete way in which a zen principle can be violated.

    Principles may list multiple ``ViolationSpec`` entries — each describes
    one observable symptom.  The ``id`` must be stable across releases so
    that suppression rules and audit trails remain valid.

    Attributes:
        id: Stable, slug-style identifier (e.g. ``"bare-except-clause"``).
        description: Human-readable explanation of the specific violation.
    """

    id: str = Field(..., description="Stable identifier for this specific check")
    description: str


def _slugify_violation(value: str) -> str:
    """Convert a free-text violation description into a URL-safe slug.

    Non-alphanumeric characters are collapsed into hyphens.  Leading and
    trailing hyphens are stripped.

    Args:
        value: Free-text description to slugify.

    Returns:
        Lowercase hyphen-separated slug suitable for use as a ``ViolationSpec.id``.
    """
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


class ZenPrinciple(BaseModel):
    """A single zen principle with its detection rules, metrics, and patterns.

    This is the atomic unit of the zen rule system.  Each principle carries
    enough metadata for the ``DetectionPipeline`` to decide **what** to detect
    (``detectable_patterns``, ``metrics``) and **how** to report it
    (``severity``, ``recommended_alternative``).

    Attributes:
        id: Globally unique identifier following ``{language}-{number}``
            convention (e.g. ``"python-001"``).
        principle: The idiomatic best-practice statement, written as a short
            imperative sentence.
        category: Taxonomy tag for grouping related principles.
        severity: Impact score on a 1-10 scale (9-10 is critical).
        description: Paragraph-length explanation of *why* this principle
            matters.
        violations: Concrete symptoms that indicate a breach of the
            principle.  Accepts raw strings (auto-slugified) or
            ``ViolationSpec`` dicts.
        detectable_patterns: Regex strings matched against source code by
            ``compiled_patterns``.
        metrics: Threshold key/value pairs consumed by detectors (e.g.
            ``{"max_nesting_depth": 3}``).
        recommended_alternative: Suggested refactoring or idiom to replace
            the violating pattern.
        required_config: Tool or linter settings that must be active for the
            principle to be enforceable.

    See Also:
        ``LanguageZenPrinciples`` — the per-language collection that holds
        these principles.
    """

    id: str = Field(
        ...,
        description="Unique identifier (e.g., 'python-001')",
        examples=["python-001", "js-005"],
    )
    principle: str = Field(
        ...,
        description="The zen principle statement",
        examples=["Explicit is better than implicit"],
    )
    category: PrincipleCategory = Field(..., description="Category of the principle")
    severity: int = Field(
        ..., ge=1, le=10, description="Severity level (1-10, where 9-10 is critical)"
    )
    description: str = Field(..., description="Detailed explanation of the principle")
    violations: list[ViolationSpec | str] = Field(
        default_factory=list, description="Common violations of this principle"
    )
    detectable_patterns: list[str] | None = Field(
        default=None, description="Specific code patterns that indicate violations"
    )
    metrics: dict[str, Any] | None = Field(
        default=None, description="Quantifiable thresholds (e.g., max_complexity: 10)"
    )
    recommended_alternative: str | None = Field(
        default=None, description="Suggested fix or better approach"
    )
    required_config: dict[str, Any] | None = Field(
        default=None, description="Required configuration settings"
    )

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("violations", mode="before")
    @classmethod
    def _normalize_violations(cls, value: object) -> list[ViolationSpec]:
        """Coerce raw violation data into a deduplicated ``ViolationSpec`` list.

        Accepts ``None``, a single item, or a heterogeneous list of strings,
        dicts, and ``ViolationSpec`` instances.  Strings are slugified into
        stable IDs; collisions are resolved by appending a positional suffix.

        Args:
            value: Raw violations payload from YAML/JSON rule definitions.

        Returns:
            Normalised list of ``ViolationSpec`` models with unique IDs.
        """
        if value is None:
            return []
        if not isinstance(value, list):
            value = [value]
        normalized: list[ViolationSpec] = []
        seen: set[str] = set()
        for index, item in enumerate(value, start=1):
            if isinstance(item, ViolationSpec):
                spec = item
            elif isinstance(item, dict):
                spec = ViolationSpec(**item)
            else:
                description = str(item)
                slug = _slugify_violation(description) or f"violation-{index}"
                if slug in seen:
                    slug = f"{slug}-{index}"
                spec = ViolationSpec(id=slug, description=description)
            if spec.id in seen:
                spec = ViolationSpec(
                    id=f"{spec.id}-{index}", description=spec.description
                )
            seen.add(spec.id)
            normalized.append(spec)
        return normalized

    @property
    def violation_specs(self) -> list[ViolationSpec]:
        """Return the normalised ``ViolationSpec`` list for this principle.

        Returns:
            Deduplicated violation specs, identical to reading ``violations``
            after validator processing.
        """
        return self._normalize_violations(self.violations)

    def compiled_patterns(self) -> list["re.Pattern"]:
        """Compile ``detectable_patterns`` into ``re.Pattern`` objects for reuse.

        Invalid regex strings are silently escaped so they behave as literal
        substring matchers.  Returns an empty list when no patterns are defined.

        Returns:
            Compiled regex objects, one per entry in ``detectable_patterns``.
        """
        import re

        patterns = self.detectable_patterns or []
        compiled: list[re.Pattern] = []
        for p in patterns:
            try:
                compiled.append(re.compile(p))
            except re.error:
                # Fall back to literal substring match by escaping
                compiled.append(re.compile(re.escape(p)))
        return compiled


class LanguageZenPrinciples(BaseModel):
    """The complete set of zen principles for a single programming language.

    Each instance records provenance (source document, URL) and holds the
    ordered list of ``ZenPrinciple`` entries that analyzers iterate over.

    Attributes:
        language: Lowercase key used throughout the registry (e.g. ``"python"``).
        name: Display-friendly language name (e.g. ``"Python"``).
        philosophy: Name of the guiding document or philosophy (e.g.
            ``"The Zen of Python (PEP 20)"``).
        source_text: Title of the authoritative style guide.
        source_url: URL to the upstream style guide or specification.
        principles: Ordered list of zen principles for this language.
    """

    language: str = Field(
        ...,
        description="Programming language identifier",
        examples=["python", "javascript", "rust"],
    )
    name: str = Field(
        ...,
        description="Human-readable language name",
        examples=["Python", "JavaScript", "Rust"],
    )
    philosophy: str = Field(..., description="Core philosophy or guiding document")
    source_text: str = Field(
        ..., description="Source documentation or style guide name"
    )
    source_url: HttpUrl = Field(
        ..., description="Source documentation or style guide URL"
    )
    principles: list[ZenPrinciple] = Field(
        default_factory=list, description="List of zen principles for this language"
    )

    @property
    def principle_count(self) -> int:
        """Total number of principles registered for this language.

        Returns:
            Length of the ``principles`` list.
        """
        return len(self.principles)

    def get_by_id(self, principle_id: str) -> ZenPrinciple | None:
        """Look up a principle by its unique ID (e.g. ``"python-003"``).

        Args:
            principle_id: The ``ZenPrinciple.id`` to search for.

        Returns:
            The matching principle, or ``None`` if no principle has that ID.
        """
        return next(
            (
                principle
                for principle in self.principles
                if principle.id == principle_id
            ),
            None,
        )

    def get_by_category(self, category: PrincipleCategory) -> list[ZenPrinciple]:
        """Filter principles belonging to *category*.

        Args:
            category: The ``PrincipleCategory`` to match against.

        Returns:
            Principles whose ``category`` field equals *category* (may be empty).
        """
        return [p for p in self.principles if p.category == category]

    def get_by_severity(self, min_severity: int = 7) -> list[ZenPrinciple]:
        """Return principles at or above *min_severity*.

        Args:
            min_severity: Inclusive lower bound on the 1-10 severity scale.

        Returns:
            Principles whose ``severity`` is ≥ *min_severity*.
        """
        return [p for p in self.principles if p.severity >= min_severity]


def get_number_of_principles(language: LanguageZenPrinciples) -> int:
    """Count principles defined for a single language.

    Args:
        language: The ``LanguageZenPrinciples`` instance to inspect.

    Returns:
        Number of ``ZenPrinciple`` entries in *language*.
    """
    return language.principle_count


def get_number_of_priniciple(language: LanguageZenPrinciples) -> int:
    """Backward-compatible alias for ``get_number_of_principles`` (typo preserved).

    Args:
        language: Delegated to ``get_number_of_principles``.

    Returns:
        Same as ``get_number_of_principles``.
    """
    return get_number_of_principles(language)


def get_rule_ids(language: LanguageZenPrinciples) -> set[str]:
    """Collect the unique ``ZenPrinciple.id`` values for a language.

    Args:
        language: The ``LanguageZenPrinciples`` to extract IDs from.

    Returns:
        Set of principle IDs (e.g. ``{"python-001", "python-002", …}``).
    """
    return {principle.id for principle in language.principles}


def get_total_principles(
    registry: dict[str, LanguageZenPrinciples],
) -> int:
    """Sum principle counts across every language in *registry*.

    Args:
        registry: The ``ZEN_REGISTRY`` mapping (language key → principles).

    Returns:
        Aggregate principle count.
    """
    return sum(language.principle_count for language in registry.values())


def get_missing_detector_rules(
    language: LanguageZenPrinciples,
    *,
    explicit_only: bool = True,
) -> list[str]:
    """Identify principle IDs that have no dedicated detector registered.

    When *explicit_only* is ``True`` (the default), the generic
    ``RulePatternDetector`` fallback is ignored — only purpose-built
    detectors count as coverage.

    Args:
        language: The ``LanguageZenPrinciples`` whose coverage is checked.
        explicit_only: If ``True``, exclude the catch-all pattern detector
            from the coverage calculation.

    Returns:
        Sorted list of principle IDs without detector coverage.

    See Also:
        ``get_rule_id_coverage`` — also reports *unknown* detector mappings.
    """
    from mcp_zen_of_languages.analyzers import registry_bootstrap  # noqa: F401
    from mcp_zen_of_languages.analyzers.registry import REGISTRY
    from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector

    missing: list[str] = []
    for principle in language.principles:
        metas = REGISTRY.detectors_for_rule(principle.id, language.language)
        if explicit_only:
            metas = [
                meta for meta in metas if meta.detector_class is not RulePatternDetector
            ]
        if not metas:
            missing.append(principle.id)
    return missing


def get_rule_id_coverage(
    language: LanguageZenPrinciples,
    *,
    explicit_only: bool = True,
) -> tuple[list[str], list[str]]:
    """Compute bidirectional coverage between principles and detectors.

    Returns two lists:

    * **missing** — principle IDs with no mapped detector.
    * **unknown** — detector rule-IDs that reference principles not defined
      in the canonical rule set (potential stale registrations).

    Args:
        language: The ``LanguageZenPrinciples`` to audit.
        explicit_only: When ``True``, ignore ``RulePatternDetector`` fallbacks.

    Returns:
        ``(missing, unknown)`` — both lists sorted alphabetically.
    """
    from mcp_zen_of_languages.analyzers import registry_bootstrap  # noqa: F401
    from mcp_zen_of_languages.analyzers.registry import REGISTRY
    from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector

    expected = get_rule_ids(language)
    mapped: set[str] = set()
    for meta in REGISTRY.items():
        if meta.language != language.language:
            continue
        if explicit_only and meta.detector_class is RulePatternDetector:
            continue
        mapped.update(meta.rule_ids)
    missing = sorted(expected - mapped)
    unknown = sorted(mapped - expected)
    return missing, unknown


def get_registry_rule_id_gaps(
    registry: dict[str, LanguageZenPrinciples],
    *,
    explicit_only: bool = True,
) -> dict[str, dict[str, list[str]]]:
    """Run ``get_rule_id_coverage`` across every language and collect gaps.

    Languages with no gaps are omitted from the result.

    Args:
        registry: Full ``ZEN_REGISTRY`` mapping.
        explicit_only: Passed through to ``get_rule_id_coverage``.

    Returns:
        ``{language: {"missing": [...], "unknown": [...]}}`` for each
        language that has at least one gap.
    """
    gaps: dict[str, dict[str, list[str]]] = {}
    for language in registry.values():
        missing, unknown = get_rule_id_coverage(language, explicit_only=explicit_only)
        if missing or unknown:
            gaps[language.language] = {"missing": missing, "unknown": unknown}
    return gaps


def get_registry_detector_gaps(
    registry: dict[str, LanguageZenPrinciples],
    *,
    explicit_only: bool = True,
) -> dict[str, list[str]]:
    """Return principle IDs lacking a dedicated detector for each language.

    This is a convenience wrapper around ``get_missing_detector_rules``
    applied to every language in *registry*.

    Args:
        registry: Full ``ZEN_REGISTRY`` mapping.
        explicit_only: Passed through to ``get_missing_detector_rules``.

    Returns:
        ``{language: [rule_id, …]}`` for each language with missing detectors.
    """
    gaps: dict[str, list[str]] = {}
    for language in registry.values():
        if missing := get_missing_detector_rules(language, explicit_only=explicit_only):
            gaps[language.language] = missing
    return gaps


class ViolationReport(BaseModel):
    """Structured report emitted when a zen principle is violated.

    Carries everything a reporter needs: the violated principle's identity,
    severity, location in source, a human-readable message, and an optional
    suggested fix.

    Attributes:
        principle_id: ID of the violated ``ZenPrinciple``.
        principle_name: Display name / statement of the principle.
        severity: 1-10 severity copied from the principle.
        category: Taxonomy tag of the violated principle.
        location: Optional ``{"line": int, "column": int}`` pointing into
            the source file.
        message: One-line human-readable violation description.
        suggestion: Recommended refactoring to resolve the violation.
        code_snippet: Extract of the offending source code.
    """

    principle_id: str = Field(..., description="ID of violated principle")
    principle_name: str = Field(..., description="Name of the principle")
    severity: int = Field(..., description="Severity level (1-10)")
    category: PrincipleCategory = Field(..., description="Category of violation")
    location: dict[str, int] | None = Field(
        default=None, description="Location in code (line, column)"
    )
    message: str = Field(..., description="Human-readable violation message")
    suggestion: str | None = Field(default=None, description="Suggested fix")
    code_snippet: str | None = Field(default=None, description="Relevant code snippet")


class AnalysisResult(BaseModel):
    """Aggregate outcome of analysing a source file against zen principles.

    Contains the full violation list, a normalized 0-100 score, and any
    metrics (complexity, LOC, etc.) computed during analysis.

    Attributes:
        language: Lowercase language key that was analysed.
        violations: Ordered list of ``ViolationReport`` entries.
        overall_score: Zen score where 100 means no violations.
        metrics: Free-form metric dictionary (keys vary by analyzer).
        summary: Human-readable prose summarising the analysis.
    """

    language: str = Field(..., description="Analyzed language")
    violations: list[ViolationReport] = Field(
        default_factory=list, description="Detected violations"
    )
    overall_score: float = Field(
        default=100.0, ge=0.0, le=100.0, description="Overall zen score (100 = perfect)"
    )
    metrics: dict[str, Any] = Field(
        default_factory=dict, description="Computed metrics (complexity, LOC, etc.)"
    )
    summary: str = Field(default="", description="Summary of analysis")

    @property
    def critical_violations(self) -> list[ViolationReport]:
        """Subset of violations with severity ≥ 9 (critical band).

        Returns:
            ``ViolationReport`` entries at the critical severity level.
        """
        return [v for v in self.violations if v.severity >= SeverityLevel.CRITICAL_LOW]

    @property
    def violation_count(self) -> int:
        """Total number of violations recorded in this result.

        Returns:
            Length of the ``violations`` list.
        """
        return len(self.violations)


class LanguageSummary(BaseModel):
    """Lightweight snapshot of a language's presence in the registry.

    Used by ``RegistryStats`` to avoid serialising the full principle list
    when only high-level metadata is needed.

    Attributes:
        name: Human-readable language name.
        principle_count: How many principles are registered.
        philosophy: Core philosophy or guiding document title.
        source_text: Name of the upstream style guide (optional).
        source_url: URL of the upstream style guide (optional).
    """

    name: str = Field(..., description="Human-readable language name")
    principle_count: int = Field(..., description="Number of principles")
    philosophy: str = Field(..., description="Core philosophy or guiding document")
    source_text: str | None = Field(
        None, description="Source documentation or style guide name"
    )
    source_url: HttpUrl | None = Field(
        None, description="Source documentation or style guide URL"
    )


class DetectorConfig(BaseModel):
    """Language-agnostic configuration bundle passed to individual detectors.

    Built by ``RulesAdapter.get_detector_config`` or by the
    ``DetectionPipeline`` from ``ZenPrinciple.metrics``.  Detectors
    read thresholds and patterns from this model instead of inspecting
    raw principle objects, keeping them decoupled from the rule schema.

    Attributes:
        name: Detector identifier (e.g. ``"cyclomatic_complexity"``).
        thresholds: Numeric limits keyed by metric name
            (e.g. ``{"max_nesting_depth": 3.0}``).
        patterns: Regex strings the detector should match against source.
        metadata: Arbitrary non-numeric configuration values.
    """

    name: str
    thresholds: dict[str, float] = Field(default_factory=dict)
    patterns: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RegistryStats(BaseModel):
    """Aggregated statistics across the entire ``ZEN_REGISTRY``.

    Constructed via the ``from_registry`` classmethod.  Useful for
    dashboard rendering and health-check endpoints.

    Attributes:
        total_languages: Number of languages with registered principles.
        total_principles: Sum of principles across all languages.
        languages: Per-language ``LanguageSummary`` keyed by language identifier.
    """

    total_languages: int = Field(..., description="Total supported languages")
    total_principles: int = Field(
        ..., description="Total number of principles across all languages"
    )
    languages: dict[str, LanguageSummary] = Field(
        default_factory=dict,
        description="Per-language summary keyed by language identifier",
    )

    @classmethod
    def from_registry(
        cls, registry: dict[str, "LanguageZenPrinciples"]
    ) -> "RegistryStats":
        """Snapshot the live registry into a serialisable ``RegistryStats`` model.

        Args:
            registry: The ``ZEN_REGISTRY`` mapping to summarise.

        Returns:
            A fully populated ``RegistryStats`` instance.
        """
        total_languages = len(registry)
        total_principles = sum(lang.principle_count for lang in registry.values())

        languages: dict[str, LanguageSummary] = {
            key: LanguageSummary(
                name=lang.name,
                principle_count=lang.principle_count,
                philosophy=lang.philosophy,
                source_text=getattr(lang, "source_text", None),
                source_url=getattr(lang, "source_url", None),
            )
            for key, lang in registry.items()
        }
        return cls(
            total_languages=total_languages,
            total_principles=total_principles,
            languages=languages,
        )
