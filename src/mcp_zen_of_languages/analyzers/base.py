"""Analyzer architecture built on Template Method and Strategy patterns.

This module is the architectural backbone of the zen analysis engine. It
replaces a monolithic 400-line ``analyze()`` method with a composable
pipeline of focused components, each governed by a well-known design
pattern:

- **Template Method** ([`BaseAnalyzer`][mcp_zen_of_languages.analyzers.base.BaseAnalyzer])
  defines the invariant analysis skeleton — parse → metrics → detect →
  result — while language subclasses override only the hooks that differ
  (``parse_code``, ``compute_metrics``, ``build_pipeline``).
- **Strategy** ([`ViolationDetector`][mcp_zen_of_languages.analyzers.base.ViolationDetector])
  encapsulates each detection algorithm behind a uniform ``detect()``
  contract, so detectors can be swapped, reordered, or shared across
  languages without touching the pipeline.
- **Context Object** ([`AnalysisContext`][mcp_zen_of_languages.analyzers.base.AnalysisContext])
  carries all intermediate state — AST, metrics, dependency graph — as a
  single Pydantic model, eliminating parameter explosion and giving every
  detector type-safe access to upstream results.
- **Pipeline / Chain of Responsibility** ([`DetectionPipeline`][mcp_zen_of_languages.analyzers.base.DetectionPipeline])
  runs detectors sequentially, isolating failures so one broken detector
  never silences the rest.

Data flows through these layers as::

    server / cli
      → AnalyzerFactory.create(language)
        → BaseAnalyzer.analyze(code)
          → parse_code()          # Template hook
          → compute_metrics()     # Template hook
          → DetectionPipeline.run()
            → ViolationDetector.detect()  × N
          → _build_result()
        → AnalysisResult

Tip: Adding a new language
    Subclass [`BaseAnalyzer`][mcp_zen_of_languages.analyzers.base.BaseAnalyzer],
    implement three hooks, and register language-specific detectors — the
    base class handles everything else.
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from typing import Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from mcp_zen_of_languages.languages.configs import DetectorConfig
from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    Location,
    Metrics,
    ParserResult,
    RulesSummary,
    Violation,
)

logger = logging.getLogger(__name__)
logger.setLevel(
    getattr(
        logging, os.environ.get("ZEN_LOG_LEVEL", "WARNING").upper(), logging.WARNING
    )
)

# ============================================================================
# Configuration Models
# ============================================================================


class AnalyzerConfig(DetectorConfig):
    """Baseline thresholds shared by every language analyzer.

    ``AnalyzerConfig`` acts as the *root configuration* for the analysis
    engine. It inherits discriminated-union plumbing from
    [`DetectorConfig`][mcp_zen_of_languages.languages.configs.DetectorConfig]
    and adds the knobs that every language needs — complexity caps, length
    limits, and feature flags.

    Language-specific subclasses (e.g.
    [`PythonAnalyzerConfig`][mcp_zen_of_languages.analyzers.base.PythonAnalyzerConfig])
    extend this with additional fields without repeating the common ones.

    Attributes:
        type: Discriminator fixed to ``"analyzer_defaults"``.
        max_cyclomatic_complexity: Upper bound on average cyclomatic
            complexity before a violation is emitted (1–50, default 10).
        max_nesting_depth: Maximum permitted indentation nesting depth
            (1–10, default 3).
        max_function_length: Line count ceiling for a single function
            body (10–500, default 50).
        max_class_length: Line count ceiling for a class definition
            (1–1000, default 300).
        max_magic_methods: Allowed dunder-method count per class
            (0–50, default 3).
        severity_threshold: Minimum severity a violation must reach to
            appear in final results (1–10, default 5).
        enable_dependency_analysis: When ``True``, the analyzer builds a
            dependency graph before running detectors.
        enable_pattern_detection: When ``True``, the
            [`RulesAdapter`][mcp_zen_of_languages.adapters.rules_adapter.RulesAdapter]
            is invoked to merge rule-derived violations.

    Note:
        Field boundaries are enforced by Pydantic ``ge`` / ``le``
        constraints — passing an out-of-range value raises a
        ``ValidationError`` at construction time, not at analysis time.

    See Also:
        [`PythonAnalyzerConfig`][mcp_zen_of_languages.analyzers.base.PythonAnalyzerConfig]:
            Python-specific extensions.
        [`BaseAnalyzer`][mcp_zen_of_languages.analyzers.base.BaseAnalyzer]:
            Consumer that reads these thresholds during analysis.
    """

    type: Literal["analyzer_defaults"] = "analyzer_defaults"
    max_cyclomatic_complexity: int = Field(default=10, ge=1, le=50)
    max_nesting_depth: int = Field(default=3, ge=1, le=10)
    max_function_length: int = Field(default=50, ge=10, le=500)
    max_class_length: int = Field(default=300, ge=1, le=1000)
    max_magic_methods: int = Field(default=3, ge=0, le=50)
    severity_threshold: int = Field(default=5, ge=1, le=10)
    enable_dependency_analysis: bool = Field(default=True)
    enable_pattern_detection: bool = Field(default=True)


class PythonAnalyzerConfig(AnalyzerConfig):
    """Python-specific analyzer settings layered on top of the base defaults.

    Python analysis adds checks that only make sense for CPython semantics:
    magic-method proliferation (``__init__``, ``__str__``, …) and God Class
    detection. These flags let callers selectively enable or tune those
    detectors without affecting the shared thresholds inherited from
    [`AnalyzerConfig`][mcp_zen_of_languages.analyzers.base.AnalyzerConfig].

    Attributes:
        detect_magic_methods: Enable the magic-method-count detector that
            flags classes overloading too many dunder protocols.
        detect_god_classes: Enable the God Class detector that identifies
            classes with excessive responsibility.
        max_magic_methods: Ceiling on dunder methods per class before a
            violation is raised (overrides the base default of 3).

    See Also:
        [`AnalyzerConfig`][mcp_zen_of_languages.analyzers.base.AnalyzerConfig]:
            Inherited base thresholds.
    """

    detect_magic_methods: bool = Field(default=True)
    detect_god_classes: bool = Field(default=True)
    max_magic_methods: int = Field(default=3)


class TypeScriptAnalyzerConfig(AnalyzerConfig):
    """TypeScript-specific analyzer settings.

    TypeScript analysis extends the base thresholds with checks targeting
    the type system: unrestrained ``any`` usage and overly-generic type
    parameter lists. These flags complement — rather than replace — the
    complexity and length limits inherited from
    [`AnalyzerConfig`][mcp_zen_of_languages.analyzers.base.AnalyzerConfig].

    Attributes:
        detect_any_usage: Enable detection of ``any`` type annotations
            that bypass the TypeScript type checker.
        max_type_parameters: Maximum generic type parameters allowed on a
            single declaration before a violation is emitted.

    See Also:
        [`AnalyzerConfig`][mcp_zen_of_languages.analyzers.base.AnalyzerConfig]:
            Inherited base thresholds.
    """

    detect_any_usage: bool = Field(default=True)
    max_type_parameters: int = Field(default=5)


class RustAnalyzerConfig(AnalyzerConfig):
    """Rust-specific analyzer settings.

    Rust analysis adds safety-oriented checks that are unique to the
    language's ownership model: ``unwrap()`` calls that can panic at
    runtime and ``unsafe`` blocks that opt out of borrow-checker
    guarantees. Inherits shared complexity limits from
    [`AnalyzerConfig`][mcp_zen_of_languages.analyzers.base.AnalyzerConfig].

    Attributes:
        detect_unwrap_usage: Enable detection of ``.unwrap()`` calls on
            ``Result`` and ``Option`` types that risk runtime panics.
        detect_unsafe_blocks: Enable detection of ``unsafe { … }``
            blocks that bypass Rust's memory-safety guarantees.

    See Also:
        [`AnalyzerConfig`][mcp_zen_of_languages.analyzers.base.AnalyzerConfig]:
            Inherited base thresholds.
    """

    detect_unwrap_usage: bool = Field(default=True)
    detect_unsafe_blocks: bool = Field(default=True)


# ============================================================================
# Analysis Context (holds all intermediate data)
# ============================================================================


class AnalysisContext(BaseModel):
    """Type-safe state container that flows through the analysis pipeline.

    ``AnalysisContext`` implements the **Context Object** pattern: instead
    of threading a growing list of positional arguments through every
    detector, the analyzer populates a single Pydantic model with the
    raw source, parsed AST, computed metrics, and cross-file metadata.
    Each [`ViolationDetector`][mcp_zen_of_languages.analyzers.base.ViolationDetector]
    reads only the fields it needs, and the model's type annotations give
    IDE autocomplete for free.

    The lifecycle of a context mirrors the steps inside
    [`BaseAnalyzer.analyze`][mcp_zen_of_languages.analyzers.base.BaseAnalyzer.analyze]:

    1. **Created** with raw ``code`` and optional ``path``.
    2. **Enriched** by ``parse_code()`` (sets ``ast_tree``).
    3. **Enriched** by ``compute_metrics()`` (sets ``cyclomatic_summary``,
       ``maintainability_index``, ``lines_of_code``).
    4. **Enriched** by ``_build_dependency_analysis()`` (sets
       ``dependency_analysis``).
    5. **Consumed** by each detector in the pipeline.

    Attributes:
        code: Raw source text submitted for analysis.
        path: Filesystem path associated with the source, when known.
        language: Language identifier (e.g. ``"python"``, ``"typescript"``).
        ast_tree: Parsed syntax tree produced by the language-specific
            ``parse_code()`` hook, or ``None`` if parsing failed.
        cyclomatic_summary: Aggregated cyclomatic-complexity statistics
            for every block in the source.
        maintainability_index: Halstead / McCabe maintainability score
            (0–100 scale).
        lines_of_code: Physical line count of the source text.
        dependency_analysis: Language-specific dependency graph payload,
            or ``None`` when dependency analysis is disabled.
        violations: Mutable list of violations accumulated during
            pipeline execution.
        other_files: Sibling file contents keyed by path, enabling
            cross-file detectors (e.g. duplicate-code).
        repository_imports: Per-file import index built from the wider
            repository, enabling coupling analysis.

    See Also:
        [`BaseAnalyzer.analyze`][mcp_zen_of_languages.analyzers.base.BaseAnalyzer.analyze]:
            Orchestrator that creates and enriches this context.
        [`ViolationDetector.detect`][mcp_zen_of_languages.analyzers.base.ViolationDetector.detect]:
            Consumer interface that reads context fields.
    """

    # Input
    code: str
    path: str | None = None
    language: str

    # Parsed artifacts
    ast_tree: ParserResult | None = None

    # Metrics
    cyclomatic_summary: CyclomaticSummary | None = None
    maintainability_index: float | None = None
    lines_of_code: int = 0

    # Analysis results
    dependency_analysis: object | None = None  # DependencyAnalysis model
    violations: list[Violation] = Field(default_factory=list)

    # Other files for cross-file analysis
    other_files: dict[str, str] | None = None
    repository_imports: dict[str, list[str]] | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


# ============================================================================
# Detector Interface (Strategy Pattern)
# ============================================================================

ConfigT = TypeVar("ConfigT", bound="DetectorConfig")


class ViolationDetector[ConfigT: "DetectorConfig"](ABC):
    """Abstract base for individual violation-detection strategies.

    Every concrete detector encapsulates exactly *one* kind of code-smell
    check — cyclomatic complexity, nesting depth, God Class, etc. — behind
    the uniform ``detect()`` contract defined here. This is the **Strategy
    pattern**: the [`DetectionPipeline`][mcp_zen_of_languages.analyzers.base.DetectionPipeline]
    iterates over a list of ``ViolationDetector`` instances without knowing
    (or caring) which algorithm each one uses.

    Subclasses must implement:

    - ``detect()`` — inspect the
      [`AnalysisContext`][mcp_zen_of_languages.analyzers.base.AnalysisContext]
      and return zero or more ``Violation`` objects.
    - ``name`` (property) — return a human-readable identifier used in
      error logging.

    The helper ``build_violation()`` is provided so detectors never have
    to manually wire up principle IDs, severity defaults, or message
    selection — those are resolved from the detector's own
    [`DetectorConfig`][mcp_zen_of_languages.languages.configs.DetectorConfig].

    Attributes:
        config: Per-detector configuration injected by the pipeline
            builder. Contains thresholds, severity, and violation
            message templates.
        rule_ids: Zen rule identifiers this detector is responsible for.

    See Also:
        [`DetectionPipeline`][mcp_zen_of_languages.analyzers.base.DetectionPipeline]:
            Runner that invokes ``detect()`` on every registered detector.
        [`AnalysisContext`][mcp_zen_of_languages.analyzers.base.AnalysisContext]:
            Shared state read by detectors.
        [`DetectorConfig`][mcp_zen_of_languages.languages.configs.DetectorConfig]:
            Base configuration schema for typed detector settings.
    """

    config: ConfigT | None = None
    rule_ids: list[str]

    def __init__(self) -> None:
        """Initialize the detector with an empty rule-ID list.

        Concrete rule IDs are injected later by the pipeline builder in
        [`BaseAnalyzer.build_pipeline`][mcp_zen_of_languages.analyzers.base.BaseAnalyzer.build_pipeline]
        after matching this detector to its zen-rule definitions.
        """
        self.rule_ids = []

    @abstractmethod
    def detect(self, context: AnalysisContext, config: ConfigT) -> list[Violation]:
        """Run this detector's algorithm and return any violations found.

        Implementations should read only the fields they need from
        *context* (e.g. ``cyclomatic_summary`` for a complexity check) and
        compare against thresholds stored in *config*. Use
        [`build_violation`][mcp_zen_of_languages.analyzers.base.ViolationDetector.build_violation]
        to construct ``Violation`` instances with correct principle IDs and
        severity.

        Args:
            context: Pipeline state carrying parsed AST, metrics, and
                source text populated by earlier analysis stages.
            config: Typed detector configuration holding thresholds,
                severity, and violation-message templates for this
                detector.

        Returns:
            Zero or more violations discovered by this strategy. An empty
            list signals clean code for this detector's concern.
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable identifier for this detector.

        Used in log messages and error reports emitted by
        [`DetectionPipeline.run`][mcp_zen_of_languages.analyzers.base.DetectionPipeline.run]
        when a detector raises an unexpected exception.

        Returns:
            Short, unique name such as ``"cyclomatic_complexity"`` or
            ``"god_class"``.
        """

    def build_violation(
        self,
        config: ConfigT,
        *,
        message: str | None = None,
        contains: str | None = None,
        index: int = 0,
        severity: int | None = None,
        location: Location | None = None,
        suggestion: str | None = None,
        files: list[str] | None = None,
    ) -> Violation:
        """Construct a ``Violation`` from detector config with optional overrides.

        This convenience factory saves every detector from repeating the
        same principle-ID look-up, severity resolution, and message
        selection logic. The algorithm is:

        1. Resolve ``principle`` from ``config.principle``,
           ``config.principle_id``, or ``config.type`` (first non-``None``
           wins).
        2. If *message* is not given explicitly, delegate to
           ``config.select_violation_message()`` using *contains* or
           *index* to pick the right template.
        3. If *severity* is not given, fall back to ``config.severity``
           or a default of ``5``.

        Args:
            config: Detector configuration carrying principle metadata,
                severity, and violation-message templates.
            message: Explicit violation message. When ``None``, the
                message is auto-selected from the config's template list.
            contains: Substring filter passed to
                ``select_violation_message`` to pick a matching template.
            index: Zero-based position selecting one template from the
                config's ``violation_messages`` list (default ``0``).
            severity: Override severity score (1–10). Falls back to the
                config-level severity when omitted.
            location: Source location to attach to the violation, typically
                produced by
                [`LocationHelperMixin`][mcp_zen_of_languages.analyzers.base.LocationHelperMixin].
            suggestion: Remediation hint shown alongside the violation in
                reports and IDE integrations.
            files: Related file paths included for cross-file violations
                such as duplicate-code detection.

        Returns:
            Fully populated ``Violation`` ready for collection by the
            [`DetectionPipeline`][mcp_zen_of_languages.analyzers.base.DetectionPipeline].
        """
        principle = (
            getattr(config, "principle", None)
            or getattr(config, "principle_id", None)
            or getattr(config, "type", "violation")
        )
        if message is None:
            selector = getattr(config, "select_violation_message", None)
            if callable(selector):
                message = selector(contains=contains, index=index)
            else:
                message = principle
        resolved_severity = severity
        if resolved_severity is None:
            resolved_severity = getattr(config, "severity", None) or 5
        return Violation(
            principle=principle,
            severity=resolved_severity,
            message=message,
            location=location,
            suggestion=suggestion,
            files=files,
        )


# ============================================================================
# Detection Pipeline
# ============================================================================


class DetectionPipeline:
    """Fail-safe runner that executes detectors in sequence and collects violations.

    ``DetectionPipeline`` implements the **Pipeline / Chain of
    Responsibility** pattern. It owns an ordered list of
    [`ViolationDetector`][mcp_zen_of_languages.analyzers.base.ViolationDetector]
    instances and calls each one's ``detect()`` method against the shared
    [`AnalysisContext`][mcp_zen_of_languages.analyzers.base.AnalysisContext].
    Violations from every detector are merged into a single flat list.

    Crucially, a failure in one detector is caught and logged but *never*
    aborts the remaining detectors. This isolation guarantee means a
    newly added or experimental detector cannot break production analysis.

    See Also:
        [`ViolationDetector`][mcp_zen_of_languages.analyzers.base.ViolationDetector]:
            Strategy interface executed by this pipeline.
        [`BaseAnalyzer.build_pipeline`][mcp_zen_of_languages.analyzers.base.BaseAnalyzer.build_pipeline]:
            Factory that assembles the detector list from zen rules.
    """

    def __init__(self, detectors: list[ViolationDetector]):
        """Prepare the pipeline with an ordered detector sequence.

        Args:
            detectors: Detector instances to execute, in the order they
                should run. Order can matter when later detectors depend
                on side-effects written to ``AnalysisContext.violations``
                by earlier ones.
        """
        self.detectors = detectors

    def run(
        self, context: AnalysisContext, config: AnalyzerConfig | DetectorConfig
    ) -> list[Violation]:
        """Execute every detector against the shared context and merge results.

        For each detector the pipeline resolves which configuration to
        use: if the detector carries its own ``config`` (injected during
        pipeline construction), that takes precedence; otherwise the
        analyzer-level *config* is used as a fallback.

        If a detector raises an exception, the error is printed and the
        pipeline continues with the next detector — no violations from
        healthy detectors are lost.

        Args:
            context: Shared analysis state populated by
                [`BaseAnalyzer.analyze`][mcp_zen_of_languages.analyzers.base.BaseAnalyzer.analyze]
                before the pipeline starts.
            config: Fallback configuration used when a detector does not
                carry its own per-detector config.

        Returns:
            Flat list of violations aggregated from all detectors that
            executed successfully.
        """
        all_violations: list[Violation] = []

        for detector in self.detectors:
            try:
                detector_config = detector.config or config
                violations = detector.detect(context, detector_config)
                all_violations.extend(violations)
            except Exception as e:  # noqa: BLE001
                # Log error but continue with other detectors
                print(f"Error in detector {detector.name}: {e}")

        return all_violations


# ============================================================================
# Base Analyzer (Template Method Pattern)
# ============================================================================


class BaseAnalyzer(ABC):
    """Abstract skeleton for language-specific code analyzers.

    ``BaseAnalyzer`` is the **Template Method** at the heart of the
    architecture. Its concrete ``analyze()`` method defines a fixed
    seven-step workflow — context creation → parsing → metrics →
    dependency analysis → detector pipeline → rules adapter → result
    assembly — while three abstract hooks let each language plug in its
    own behaviour:

    | Hook | Responsibility |
    |---|---|
    | ``parse_code()`` | Turn raw source text into a language AST |
    | ``compute_metrics()`` | Produce cyclomatic, maintainability, LOC |
    | ``build_pipeline()`` | Assemble the detector list from zen rules |

    Subclasses such as ``PythonAnalyzer`` implement *only* these hooks;
    the invariant orchestration logic is never duplicated.

    Attributes:
        config: Resolved analyzer configuration (base defaults merged
            with any overrides from ``zen-config.yaml``).
        pipeline: Pre-built
            [`DetectionPipeline`][mcp_zen_of_languages.analyzers.base.DetectionPipeline]
            ready to execute against an
            [`AnalysisContext`][mcp_zen_of_languages.analyzers.base.AnalysisContext].

    See Also:
        [`ViolationDetector`][mcp_zen_of_languages.analyzers.base.ViolationDetector]:
            Strategy objects executed inside the pipeline.
        [`AnalysisContext`][mcp_zen_of_languages.analyzers.base.AnalysisContext]:
            State container flowing through every stage.
        [`AnalyzerConfig`][mcp_zen_of_languages.analyzers.base.AnalyzerConfig]:
            Configuration consumed by the analyzer and its detectors.
    """

    def __init__(self, config: AnalyzerConfig | None = None):
        """Bootstrap the analyzer with configuration and a detector pipeline.

        If no *config* is supplied, the language-specific ``default_config()``
        hook provides sensible defaults.  ``build_pipeline()`` is called
        immediately so the detector list is ready before the first
        ``analyze()`` invocation.

        Args:
            config: Explicit analyzer configuration. When ``None``, the
                subclass's ``default_config()`` is used.

        Raises:
            TypeError: If *config* is not ``None`` and not an
                ``AnalyzerConfig`` instance.
        """
        if config is not None and not isinstance(config, AnalyzerConfig):
            msg = "AnalyzerConfig instance required"
            raise TypeError(msg)
        self.config: AnalyzerConfig = config or self.default_config()
        self.pipeline: DetectionPipeline = self.build_pipeline()

    @abstractmethod
    def default_config(self) -> AnalyzerConfig:
        """Provide the default configuration for this language.

        Called by ``__init__`` when the caller does not pass an explicit
        config. Language subclasses return their own typed config (e.g.
        [`PythonAnalyzerConfig`][mcp_zen_of_languages.analyzers.base.PythonAnalyzerConfig])
        pre-populated with sensible defaults.

        Returns:
            Language-appropriate configuration with default thresholds.
        """

    @abstractmethod
    def language(self) -> str:
        """Return the language identifier this analyzer handles.

        The string must match the keys used in ``zen-config.yaml`` and
        the language registry (e.g. ``"python"``, ``"typescript"``,
        ``"rust"``).

        Returns:
            Lowercase language name used for rule lookup and result
            tagging.
        """

    @abstractmethod
    def parse_code(self, code: str) -> ParserResult | None:
        """Parse raw source text into a language-specific syntax tree.

        This is the first Template Method hook called by ``analyze()``.
        Python subclasses typically delegate to the ``ast`` module; other
        languages may use tree-sitter or custom parsers.

        Args:
            code: Complete source text of the file being analyzed.

        Returns:
            Wrapped parse result, or ``None`` when the source cannot be
            parsed (e.g. syntax errors). A ``None`` return does not abort
            analysis — metric computation and detectors will proceed
            with whatever data is available.
        """

    @abstractmethod
    def compute_metrics(
        self, code: str, ast_tree: ParserResult | None
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Compute quantitative code-quality metrics for the given source.

        This is the second Template Method hook. Implementations should
        calculate at least cyclomatic complexity, a maintainability index,
        and a physical line count. The returned tuple is unpacked by
        ``analyze()`` and stored on the
        [`AnalysisContext`][mcp_zen_of_languages.analyzers.base.AnalysisContext]
        for downstream detectors.

        Args:
            code: Source text to measure.
            ast_tree: Previously parsed syntax tree (may be ``None`` if
                parsing failed), useful for AST-driven metric tools.

        Returns:
            Three-element tuple of ``(cyclomatic_summary,
            maintainability_index, lines_of_code)``. Any element may be
            ``None`` when the corresponding metric is unavailable.
        """

    # Template Method - defines the algorithm structure
    def analyze(
        self,
        code: str,
        path: str | None = None,
        other_files: dict[str, str] | None = None,
        repository_imports: dict[str, list[str]] | None = None,
    ) -> AnalysisResult:
        """Run the full analysis workflow against a single source file.

        This is the **Template Method**: it defines the invariant
        seven-step algorithm that every language analyzer follows, calling
        abstract hooks (``parse_code``, ``compute_metrics``) and the
        pre-built [`DetectionPipeline`][mcp_zen_of_languages.analyzers.base.DetectionPipeline]
        at the appropriate moments.

        **Workflow steps:**

        1. Create an [`AnalysisContext`][mcp_zen_of_languages.analyzers.base.AnalysisContext]
           from the inputs.
        2. Parse source via ``parse_code()`` → ``context.ast_tree``.
        3. Compute metrics via ``compute_metrics()`` → cyclomatic,
           maintainability, LOC.
        4. (Optional) Build dependency graph →
           ``context.dependency_analysis``.
        5. Run the detector pipeline → initial violation list.
        6. Merge with ``RulesAdapter`` violations and attach
           ``rules_summary`` (gracefully skipped if the adapter is
           unavailable).
        7. Assemble and return the final ``AnalysisResult``.

        Args:
            code: Complete source text to analyze.
            path: Filesystem path of the source file, used for
                cross-file detectors and result metadata.
            other_files: Map of sibling file paths to their contents,
                enabling detectors like duplicate-code that compare
                across files.
            repository_imports: Per-file import lists from the wider
                repository, enabling coupling and dependency-fan
                detectors.

        Returns:
            Fully populated analysis result containing metrics,
            violations, an overall quality score, and (when available)
            a ``rules_summary``.
        """
        # 1. Create analysis context
        context = self._create_context(
            code=code,
            path=path,
            other_files=other_files,
            repository_imports=repository_imports,
        )

        # 2. Parse code (language-specific hook)
        context.ast_tree = self.parse_code(code)

        # 3. Compute metrics (language-specific hook)
        cc, mi, loc = self.compute_metrics(code, context.ast_tree)
        context.cyclomatic_summary = cc
        context.maintainability_index = mi
        context.lines_of_code = loc

        # 4. Build dependency analysis (optional)
        if self.config.enable_dependency_analysis:
            context.dependency_analysis = self._build_dependency_analysis(context)

        # 5. Run detection pipeline
        violations = self.pipeline.run(context, self.config)

        # 6. Build and return result
        result = self._build_result(context, violations)

        # 7. If RulesAdapter is available, attach rules_summary
        try:
            from mcp_zen_of_languages.adapters.rules_adapter import (
                RulesAdapter,
                RulesAdapterConfig,
            )
            from mcp_zen_of_languages.models import DependencyAnalysis

            adapter_config = RulesAdapterConfig(
                max_nesting_depth=self.config.max_nesting_depth,
                max_cyclomatic_complexity=self.config.max_cyclomatic_complexity,
                min_maintainability_index=None,
            )

            adapter = RulesAdapter(language=self.language(), config=adapter_config)

            # Normalize dependency_analysis into DependencyAnalysis if possible to
            # satisfy type-checker
            dep_analysis: DependencyAnalysis | None = None
            raw_dep = context.dependency_analysis
            if isinstance(raw_dep, DependencyAnalysis):
                dep_analysis = raw_dep
            elif isinstance(raw_dep, dict):
                try:
                    dep_analysis = DependencyAnalysis.model_validate(raw_dep)
                except (ValueError, TypeError):
                    dep_analysis = None

            rules_violations = (
                adapter.find_violations(
                    code=code,
                    cyclomatic_summary=context.cyclomatic_summary,
                    maintainability_index=context.maintainability_index,
                    dependency_analysis=dep_analysis,
                )
                if self.config.enable_pattern_detection
                else []
            )
            # Merge pipeline violations with rules-derived violations
            all_violations = violations + rules_violations
            result.rules_summary = RulesSummary(
                **adapter.summarize_violations(all_violations)
            )
            result.violations = all_violations
        except Exception:  # noqa: BLE001
            # If adapter missing or fails, proceed without rules_summary
            pass

        return result

    # Helper methods (can be overridden if needed)

    def build_pipeline(self) -> DetectionPipeline:
        """Assemble the detector pipeline from zen rules and config overrides.

        The default implementation follows a four-stage process:

        1. Load canonical zen rules for ``self.language()`` via
           ``get_language_zen()``.
        2. Project those rules into
           [`DetectorConfig`][mcp_zen_of_languages.languages.configs.DetectorConfig]
           instances using the detector registry.
        3. Merge any overrides from ``zen-config.yaml`` (matched by
           detector ``type``).
        4. Instantiate each registered detector, inject its config and
           rule IDs, and wrap them in a
           [`DetectionPipeline`][mcp_zen_of_languages.analyzers.base.DetectionPipeline].

        Language subclasses may override this method entirely to build a
        hand-crafted pipeline, but the rule-driven default covers most
        use-cases.

        Returns:
            Ready-to-run pipeline containing all detectors registered
            for this language.

        Raises:
            ValueError: If no zen rules are found for the language.
        """
        from mcp_zen_of_languages.analyzers import registry_bootstrap  # noqa: F401
        from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
        from mcp_zen_of_languages.analyzers.registry import REGISTRY
        from mcp_zen_of_languages.rules import get_language_zen

        lang_zen = get_language_zen(self.language())
        if lang_zen is None:
            msg = f"No zen rules for language: {self.language()}"
            raise ValueError(msg)
        if self._pipeline_config is None:
            self._pipeline_config = PipelineConfig(
                language=self.language(),
                detectors=[],
            )

        base_config = PipelineConfig(
            language=self.language(),
            detectors=REGISTRY.configs_from_rules(lang_zen),
        )
        if self._pipeline_config:
            merged = REGISTRY.merge_configs(
                base_config.detectors, self._pipeline_config.detectors
            )
            pipeline_config = PipelineConfig(
                language=base_config.language,
                detectors=merged,
            )
        else:
            pipeline_config = base_config

        analyzer_defaults = AnalyzerConfig()
        detectors: list[ViolationDetector] = []
        for detector_config in pipeline_config.detectors:
            if detector_config.type == "analyzer_defaults":
                if isinstance(detector_config, AnalyzerConfig):
                    analyzer_defaults = detector_config
                continue
            meta = REGISTRY.get(detector_config.type)
            detector = meta.detector_class()
            detector.config = detector_config
            detector.rule_ids = list(meta.rule_ids)
            detectors.append(detector)

        self.config = analyzer_defaults
        return DetectionPipeline(detectors)

    def _create_context(
        self,
        code: str,
        path: str | None,
        other_files: dict[str, str] | None,
        repository_imports: dict[str, list[str]] | None,
    ) -> AnalysisContext:
        """Instantiate a fresh analysis context from the caller's inputs.

        This is the first step in the ``analyze()`` workflow.  The
        returned context is initially *sparse* — only the raw inputs are
        set; subsequent hooks populate ``ast_tree``, metrics, and
        dependency data.

        Args:
            code: Source text to analyze.
            path: Filesystem path associated with the source, or
                ``None`` for ad-hoc snippets.
            other_files: Sibling file contents for cross-file analysis,
                or ``None`` when unavailable.
            repository_imports: Per-file import index for coupling
                analysis, or ``None`` when unavailable.

        Returns:
            Minimally populated context ready for enrichment by
            ``parse_code()`` and ``compute_metrics()``.
        """
        return AnalysisContext(
            code=code,
            path=path,
            language=self.language(),
            other_files=other_files,
            repository_imports=repository_imports,
        )

    def _build_dependency_analysis(self, _context: AnalysisContext) -> object | None:
        """Build a language-specific dependency graph from the analysis context.

        The base implementation returns ``None`` (no dependency analysis).
        Language subclasses that support import-graph or coupling
        detection override this to return a populated
        ``DependencyAnalysis`` model.

        Called by ``analyze()`` only when
        ``config.enable_dependency_analysis`` is ``True``.

        Args:
            context: Current analysis state containing parsed AST and
                cross-file metadata needed for dependency resolution.

        Returns:
            Language-specific dependency payload consumed by downstream
            detectors, or ``None`` when the language does not support
            dependency analysis.
        """
        return None

    def _build_result(
        self,
        context: AnalysisContext,
        violations: list[Violation],
    ) -> AnalysisResult:
        """Assemble the final ``AnalysisResult`` from context and violations.

        Computes the overall quality score (``100 − 2 × total_severity``,
        floored at 0) and packages metrics together with violations into
        the result model returned to callers.

        Args:
            context: Fully enriched analysis state carrying metrics
                computed during earlier workflow steps.
            violations: Violation entries collected from the detector
                pipeline.

        Returns:
            Complete analysis payload ready for serialization or
            rendering.
        """
        overall_score = max(0.0, 100.0 - (sum(v.severity for v in violations) * 2))

        metrics = Metrics(
            cyclomatic=context.cyclomatic_summary
            or CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=context.maintainability_index or 0.0,
            lines_of_code=context.lines_of_code,
        )

        return AnalysisResult(
            language=self.language(),
            path=context.path,
            metrics=metrics,
            violations=violations,
            overall_score=overall_score,
        )

    def _calculate_overall_score(self, violations: list[Violation]) -> float:
        """Derive a 0–100 quality score from accumulated violation severities.

        The formula is intentionally simple:
        ``score = max(0, 100 − 2 × Σ severity)``.  A file with no
        violations scores a perfect 100; each severity point costs two
        score points.

        Args:
            violations: Violation entries whose ``severity`` values are
                summed to compute the penalty.

        Returns:
            Clamped quality score between ``0.0`` and ``100.0``.
        """
        if not violations:
            return 100.0

        total_severity = sum(v.severity for v in violations)
        # Deduct 2 points per severity point
        return max(0.0, 100.0 - (total_severity * 2))


# ============================================================================
# Location Helper Mixin
# ============================================================================


class LocationHelperMixin:
    """Reusable utilities for mapping code artefacts to source locations.

    This mixin is designed to be mixed into
    [`ViolationDetector`][mcp_zen_of_languages.analyzers.base.ViolationDetector]
    subclasses that need to pin violations to exact line/column
    positions. It provides two complementary strategies:

    - **Substring search** — scan raw source text for a token and
      return the first matching ``Location``.
    - **AST-node conversion** — extract ``lineno`` / ``col_offset``
      from a Python (or compatible) AST node.

    See Also:
        [`ViolationDetector.build_violation`][mcp_zen_of_languages.analyzers.base.ViolationDetector.build_violation]:
            Accepts a ``location`` kwarg typically produced by these
            helpers.
    """

    def find_location_by_substring(self, code: str, substring: str) -> Location:
        """Locate the first occurrence of *substring* in the source text.

        Scans *code* line-by-line and returns a one-based ``Location``
        pointing to the first character of the match. When the substring
        is not found the method returns ``Location(line=1, column=1)``
        as a safe fallback rather than raising.

        Args:
            code: Full source text to search, potentially multi-line.
            substring: Token or identifier to locate (exact,
                case-sensitive match).

        Returns:
            One-based ``Location`` of the first match, or ``(1, 1)``
            when the substring does not appear in *code*.
        """
        lines = code.splitlines()
        for i, line in enumerate(lines, start=1):
            col = line.find(substring)
            if col >= 0:
                return Location(line=i, column=col + 1)
        return Location(line=1, column=1)

    def ast_node_to_location(
        self, _ast_tree: ParserResult | None, node: object | None
    ) -> Location | None:
        """Extract a ``Location`` from a Python-style AST node.

        Reads ``lineno`` and ``col_offset`` attributes via ``getattr``
        so this helper works with any AST node that exposes those fields
        (stdlib ``ast``, tree-sitter adapters, etc.). Column offsets are
        converted from zero-based to one-based to match the ``Location``
        convention.

        Args:
            ast_tree: Parsed tree wrapper (currently unused but reserved
                for future tree-sitter adapters that need the root).
            node: AST node expected to carry ``lineno`` (int) and
                ``col_offset`` (int) attributes.

        Returns:
            One-based ``Location`` when both attributes are present,
            otherwise ``None``.
        """
        if node is None:
            return None

        try:
            # Extract tree if ParserResult wrapper
            # Try to get line/column from node
            lineno = getattr(node, "lineno", None)
            col_offset = getattr(node, "col_offset", None)

            if lineno is not None and col_offset is not None:
                return Location(line=int(lineno), column=int(col_offset) + 1)
        except (TypeError, ValueError):
            pass

        return None
