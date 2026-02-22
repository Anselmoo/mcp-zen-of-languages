"""Shared data-model layer for every analyser, detector, and MCP tool.

Every struct that crosses a boundary — between an analyser and the MCP
server, between the detection pipeline and the CLI, or between a detector
and its caller — lives here.  The models are built on **Pydantic v2** so
they carry automatic validation, JSON-round-trip fidelity, and IDE-friendly
autocompletion, yet several of them expose a *dict-like* access shim
(``__getitem__`` / ``get``) so that legacy test suites written against
plain-dict results keep passing without changes.

Design principles:

* **Single source of truth** — if a field appears in an analysis result,
  its schema is defined here, not duplicated across analysers.
* **Immutable value objects** — models are typically frozen after creation;
  mutability is reserved for ``AnalysisContext`` in the pipeline.
* **Composable hierarchy** — small models (``Location``, ``Violation``)
  compose into larger ones (``Metrics``, ``AnalysisResult``,
  ``ProjectSummary``) without deep inheritance.

See Also:
    ``analyzers.base``: The ``BaseAnalyzer`` that produces ``AnalysisResult``.
    ``analyzers.pipeline``: The ``DetectionPipeline`` that emits ``Violation`` lists.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Location(BaseModel):
    """Pin-point position inside a source file.

    Detectors attach a ``Location`` to every ``Violation`` they emit so
    that downstream consumers — IDE extensions, CLI reporters, dashboard
    renderers — can jump straight to the offending line.  Both fields use
    **1-based indexing** to match what editors display to users.

    Attributes:
        line (int): 1-based line number where the issue begins.
        column (int): 1-based column offset within that line.

    Example:
        >>> loc = Location(line=42, column=5)
        >>> loc.line
        42

    See Also:
        ``Violation``: Carries an optional ``Location`` for each detected issue.
        ``PatternFinding``: Reuses ``Location`` to mark architectural pattern sites.
    """

    line: int
    column: int


class Violation(BaseModel):
    """A single zen-principle violation detected in analysed code.

    When a detector in the pipeline spots code that breaks an idiomatic
    rule — say, a function whose cyclomatic complexity exceeds the
    configured ceiling — it creates a ``Violation`` carrying the rule
    identity, a human-readable explanation, and an optional fix hint.

    The model deliberately exposes ``get()`` and ``__getitem__()`` so that
    older test suites that treated results as plain dictionaries keep
    working unchanged.  New code should use attribute access directly.

    Attributes:
        principle: Canonical rule identifier, e.g. ``"zen-of-python.flat"``.
        severity: Impact weight from 1 (cosmetic) to 10 (critical defect).
        message: One-sentence description of what went wrong.
        suggestion: Actionable fix hint, or ``None`` when self-evident.
        location: Source position (line + column), if determinable.
        files: Paths involved when a violation spans multiple files.

    Example:
        >>> v = Violation(
        ...     principle="zen-of-python.flat",
        ...     severity=6,
        ...     message="Function nesting exceeds 3 levels",
        ...     suggestion="Extract the inner block into a helper function",
        ...     location=Location(line=87, column=1),
        ... )
        >>> v["severity"]
        6
        >>> v.get("suggestion")
        'Extract the inner block into a helper function'

    See Also:
        ``Location``: Positional anchor embedded inside each violation.
        ``AnalysisResult``: Aggregates a list of violations for one file.
    """

    principle: str
    severity: int = Field(..., ge=1, le=10)
    message: str
    suggestion: str | None = None
    location: Location | None = None
    files: list[str] | None = None

    # Provide dict-like access for legacy tests that expect .get()
    def get(self, key: str, default: object | None = None) -> object | None:
        """Retrieve a field value by name, falling back to *default*.

        This bridge keeps older test code that calls ``violation.get("severity")``
        running without modification.  Under the hood it delegates to
        ``getattr``, so any Pydantic field is reachable.

        Args:
            key: Attribute name matching one of the model fields
                (e.g. ``"principle"``, ``"severity"``).
            default: Fallback returned when *key* does not correspond to an
                existing attribute.  Defaults to ``None``.

        Returns:
            The field value when *key* exists, otherwise *default*.

        Example:
            >>> v = Violation(principle="flat", severity=4, message="too deep")
            >>> v.get("severity")
            4
            >>> v.get("nonexistent", "fallback")
            'fallback'
        """
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> object:
        """Support bracket-style access (``violation["field"]``).

        Legacy consumers indexed violations as if they were plain dicts.
        This dunder lets ``violation["principle"]`` resolve to the Pydantic
        field of the same name, raising ``AttributeError`` for unknown keys.

        Args:
            key: Field name to look up on the model instance.

        Returns:
            The corresponding field value.

        Raises:
            AttributeError: When *key* does not match any model field.

        Example:
            >>> v = Violation(principle="flat", severity=7, message="deep nesting")
            >>> v["principle"]
            'flat'
        """
        return getattr(self, key)


class CyclomaticBlock(BaseModel):
    """Complexity measurement for a single callable block.

    Radon (or an equivalent metric engine) walks the AST and produces one
    ``CyclomaticBlock`` per function, method, or top-level code block.
    The block records the callable's name, its McCabe complexity score,
    and the line where the definition starts — enough for a detector to
    decide whether the block breaches the configured threshold.

    Attributes:
        name: Qualified name of the function or method.
        complexity: McCabe cyclomatic complexity score (≥ 1).
        lineno: 1-based line where the callable is defined.

    Example:
        >>> block = CyclomaticBlock(name="parse_header", complexity=12, lineno=55)
        >>> block.complexity > 10
        True

    See Also:
        ``CyclomaticSummary``: Aggregates multiple blocks into an average score.
    """

    name: str
    complexity: int
    lineno: int


class CyclomaticSummary(BaseModel):
    """Aggregate complexity profile for an entire file or snippet.

    After every callable has been scored individually, the analyser
    rolls the per-block numbers into a ``CyclomaticSummary``.  The
    ``average`` gives a quick health indicator, while the full ``blocks``
    list lets detectors flag only the functions that actually exceed the
    threshold — avoiding noisy blanket warnings.

    Attributes:
        blocks: Ordered list of per-callable complexity measurements.
        average: Arithmetic mean of all block complexities in the file.

    Example:
        >>> summary = CyclomaticSummary(
        ...     blocks=[
        ...         CyclomaticBlock(name="read", complexity=3, lineno=10),
        ...         CyclomaticBlock(name="write", complexity=7, lineno=40),
        ...     ],
        ...     average=5.0,
        ... )
        >>> len(summary.blocks)
        2

    See Also:
        ``CyclomaticBlock``: The per-function detail record.
        ``Metrics``: Wraps this summary alongside maintainability and LOC.
    """

    blocks: list[CyclomaticBlock]
    average: float


class Metrics(BaseModel):
    """Container for every numeric measurement extracted from a source file.

    The analyser's ``compute_metrics`` hook populates this model after
    parsing is complete.  Downstream, the detection pipeline reads these
    numbers to decide which zen-principle thresholds have been crossed,
    and the MCP server serialises them back to the client alongside the
    violation list.

    Attributes:
        cyclomatic: Full complexity profile with per-block detail.
        maintainability_index: Halstead-derived maintainability score (0-100).
        lines_of_code: Physical line count of the analysed source.

    Example:
        >>> m = Metrics(
        ...     cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
        ...     maintainability_index=72.5,
        ...     lines_of_code=340,
        ... )
        >>> m.maintainability_index > 65
        True

    See Also:
        ``CyclomaticSummary``: Detailed breakdown stored inside ``cyclomatic``.
        ``AnalysisResult``: Final output that embeds ``Metrics``.
    """

    cyclomatic: CyclomaticSummary
    maintainability_index: float
    lines_of_code: int


class RulesSummary(BaseModel):
    """Quick-glance severity histogram for a single analysis run.

    After the pipeline finishes, violations are bucketed into four tiers
    so that reporters can display a compact traffic-light summary without
    iterating the full violation list.  The buckets mirror the tier
    boundaries defined in ``zen-config.yaml``.

    Attributes:
        critical: Number of violations with severity in the 8-10 range.
        high: Number of violations with severity in the 6-7 range.
        medium: Number of violations with severity in the 4-5 range.
        low: Number of violations with severity in the 1-3 range.

    Example:
        >>> rs = RulesSummary(critical=1, high=3, medium=5, low=12)
        >>> rs.critical + rs.high
        4

    See Also:
        ``SeverityCounts``: Identical shape used at the *project* level.
        ``AnalysisResult``: Optionally embeds a ``RulesSummary``.
    """

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class SeverityCounts(BaseModel):
    """Project-wide severity breakdown across all analysed files.

    While ``RulesSummary`` counts violations inside a *single* file,
    ``SeverityCounts`` rolls those numbers up to the whole repository or
    project scope.  The ``ProjectSummary`` model embeds one instance so
    that dashboards can render a top-level health badge in a single read.

    Attributes:
        critical: Total critical-severity violations across all files.
        high: Total high-severity violations across all files.
        medium: Total medium-severity violations across all files.
        low: Total low-severity violations across all files.

    Example:
        >>> sc = SeverityCounts(critical=0, high=2, medium=14, low=31)
        >>> sc.critical == 0
        True

    See Also:
        ``RulesSummary``: Per-file equivalent with the same bucket shape.
        ``ProjectSummary``: Parent model that carries ``SeverityCounts``.
    """

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class WorstOffender(BaseModel):
    """Spotlight on the file that accumulated the most violations.

    After a repository scan, the server sorts files by violation count
    and surfaces the top offenders so that developers know where to focus
    remediation effort first.  Each entry records the file path, the raw
    count, and — when determinable — the language that was used for analysis.

    Attributes:
        path: Repository-relative path to the offending file.
        violations: Total number of zen-principle violations in the file.
        language: Analysis language (``None`` if detection was skipped).

    Example:
        >>> wo = WorstOffender(path="src/legacy.py", violations=23, language="python")
        >>> wo.violations
        23

    See Also:
        ``ProjectSummary``: Carries a ranked list of ``WorstOffender`` entries.
    """

    path: str
    violations: int
    language: str | None = None


class ProjectSummary(BaseModel):
    """Bird's-eye health report spanning an entire repository scan.

    When the MCP server analyses a multi-file project, it folds individual
    ``AnalysisResult`` objects into a single ``ProjectSummary`` — giving
    the caller total file and violation counts, a severity histogram, and
    a ranked list of the worst-offending files.  This is the payload
    behind the ``analyze_zen_repository`` tool's summary section.

    Attributes:
        total_files: Number of source files that were analysed.
        total_violations: Sum of all violations across every file.
        severity_counts: Project-wide severity bucket breakdown.
        worst_offenders: Files ranked by descending violation count.

    Example:
        >>> ps = ProjectSummary(
        ...     total_files=42,
        ...     total_violations=108,
        ...     severity_counts=SeverityCounts(critical=2, high=10, medium=40, low=56),
        ...     worst_offenders=[
        ...         WorstOffender(path="core/engine.py", violations=31, language="python"),
        ...     ],
        ... )
        >>> ps.total_files
        42

    See Also:
        ``SeverityCounts``: The histogram embedded inside this summary.
        ``WorstOffender``: Individual entries in the offender list.
        ``AnalysisResult``: Per-file detail that feeds into this aggregate.
    """

    total_files: int
    total_violations: int
    severity_counts: SeverityCounts
    worst_offenders: list[WorstOffender] = Field(default_factory=list)


class ExternalToolResult(BaseModel):
    """Execution metadata for one optional external analysis tool."""

    tool: str
    status: str
    message: str
    strategy: str | None = None
    command: list[str] = Field(default_factory=list)
    resolution_attempts: list[str] = Field(default_factory=list)
    recommendation: str | None = None
    returncode: int | None = None
    stdout: str | None = None
    stderr: str | None = None


class ExternalAnalysisResult(BaseModel):
    """Optional external-analysis envelope attached to ``AnalysisResult``."""

    enabled: bool = False
    temporary_runners_enabled: bool = False
    language: str
    quality_note: str
    tools: list[ExternalToolResult] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    """Primary output produced by every language analyser.

    A call to ``BaseAnalyzer.analyze()`` returns exactly one
    ``AnalysisResult``.  It bundles the computed metrics, the full
    violation list, and a composite health score into a single,
    JSON-serialisable envelope.  The MCP server forwards this model
    directly to the client; the CLI formats it for terminal display.

    Like ``Violation``, this model supports bracket access
    (``result["violations"]``) so that legacy dict-oriented test
    assertions continue to pass without rewrites.

    Attributes:
        language: Language key used for analysis (e.g. ``"python"``).
        path: File path, or ``None`` for inline snippets.
        metrics: Computed complexity, maintainability, and LOC.
        violations: Ordered list of detected zen-principle violations.
        overall_score: Composite quality score from 0.0 (worst) to 10.0.
        rules_summary: Optional severity histogram for quick triage.

    Example:
        >>> result = AnalysisResult(
        ...     language="python",
        ...     path="app/routes.py",
        ...     metrics=Metrics(
        ...         cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
        ...         maintainability_index=80.0,
        ...         lines_of_code=150,
        ...     ),
        ...     violations=[],
        ...     overall_score=9.2,
        ... )
        >>> result["overall_score"]
        9.2

    See Also:
        ``Metrics``: The numeric measurements embedded in this result.
        ``Violation``: Individual issues inside the ``violations`` list.
        ``RepositoryAnalysis``: Wraps an ``AnalysisResult`` with file metadata.
    """

    language: str
    path: str | None = None
    metrics: Metrics
    violations: list[Violation]
    overall_score: float
    rules_summary: RulesSummary | None = None
    external_analysis: ExternalAnalysisResult | None = None

    def __getitem__(self, item: str) -> object:
        """Support bracket-style access (``result["field"]``).

        Legacy test suites indexed analysis results as plain dictionaries.
        This dunder translates ``result["violations"]`` into
        ``result.violations``, keeping old assertions green while new code
        uses standard attribute access.

        Args:
            item: Field name to look up on the model instance.

        Returns:
            The corresponding field value.

        Raises:
            AttributeError: When *item* does not match any model field.

        Example:
            >>> result["language"]
            'python'
        """
        # Allow legacy tests that index into results like dicts
        return getattr(self, item)


class RepositoryAnalysis(BaseModel):
    """Per-file wrapper used when scanning an entire repository.

    During a repository-wide analysis the server produces one
    ``RepositoryAnalysis`` per source file, pairing the file's path and
    detected language with the full ``AnalysisResult``.  Collecting these
    into a list gives the MCP client an iterable, JSON-friendly manifest
    of every file that was inspected.

    Attributes:
        path: Repository-relative path to the analysed file.
        language: Language key that the analyser factory resolved.
        result: Complete analysis output for this file.

    Example:
        >>> entry = RepositoryAnalysis(
        ...     path="lib/parser.py",
        ...     language="python",
        ...     result=analysis_result,
        ... )
        >>> entry.path
        'lib/parser.py'

    See Also:
        ``AnalysisResult``: The per-file detail carried inside ``result``.
        ``ProjectSummary``: Aggregate statistics derived from all entries.
    """

    path: str
    language: str
    result: AnalysisResult


class PatternFinding(BaseModel):
    """Record of a recognised architectural or design pattern.

    Pattern detectors walk the AST looking for well-known structures —
    factory functions, observer registrations, strategy switches — and
    emit a ``PatternFinding`` for each match.  The finding carries the
    pattern's canonical name, an optional source location, and a free-form
    detail string for context that doesn't fit a structured field.

    Attributes:
        name: Canonical pattern name (e.g. ``"factory_method"``).
        location: Source position where the pattern was detected.
        details: Free-form context string explaining the match.

    Example:
        >>> pf = PatternFinding(
        ...     name="singleton",
        ...     location=Location(line=12, column=1),
        ...     details="Module-level instance guarded by __new__ override",
        ... )
        >>> pf.name
        'singleton'

    See Also:
        ``PatternsResult``: Collects multiple findings into one response.
        ``Location``: Positional anchor reused here for pattern sites.
    """

    name: str
    location: Location | None = None
    details: str | None = None


class PatternsResult(BaseModel):
    """Bundled response from the architectural-pattern detection pass.

    The ``analyze_zen_patterns`` MCP tool returns a ``PatternsResult``
    containing every pattern that was matched in the target code.  An
    empty ``patterns`` list simply means no known patterns were detected —
    it is not an error condition.

    Attributes:
        patterns: Ordered list of detected pattern findings.

    Example:
        >>> pr = PatternsResult(patterns=[
        ...     PatternFinding(name="observer", details="event bus in signals.py"),
        ... ])
        >>> len(pr.patterns)
        1

    See Also:
        ``PatternFinding``: Individual match carried inside the list.
    """

    patterns: list[PatternFinding]


class ParserResult(BaseModel):
    """Opaque wrapper around a language-specific parse tree.

    Each analyser's ``parse_code`` hook returns a ``ParserResult`` so
    that the pipeline can carry the tree through the ``AnalysisContext``
    without knowing whether the underlying parser produced a ``tree-sitter``
    node, a stdlib ``ast.Module``, or something else entirely.  The
    ``type`` tag lets downstream consumers branch on the parser kind when
    they need to inspect the tree directly.

    Attributes:
        type: Parser backend identifier (e.g. ``"ast"``, ``"treesitter"``).
        tree: The actual parse tree object, opaque to the pipeline.

    Example:
        >>> import ast
        >>> pr = ParserResult(type="ast", tree=ast.parse("x = 1"))
        >>> pr.type
        'ast'

    Note:
        ``tree`` is typed as ``object | None`` because Pydantic cannot
        validate arbitrary third-party AST nodes.  Treat it as an opaque
        handle and cast to the expected type inside language-specific code.

    See Also:
        ``BaseAnalyzer.parse_code``: The hook that creates this wrapper.
    """

    type: str
    tree: object | None = None


class DependencyCycle(BaseModel):
    """A single circular dependency path found in the import graph.

    When the dependency analyser builds a directed graph of module
    imports and detects a strongly-connected component, it records each
    cycle as a ``DependencyCycle``.  The ``cycle`` list names the modules
    in traversal order — the last element implicitly links back to the
    first, closing the loop.

    Attributes:
        cycle: Module names forming the circular import chain.

    Example:
        >>> dc = DependencyCycle(cycle=["auth", "users", "auth"])
        >>> "auth" in dc.cycle
        True

    See Also:
        ``DependencyAnalysis``: Parent model that collects all cycles.
    """

    cycle: list[str]


class DependencyAnalysis(BaseModel):
    """Full dependency-graph report for a codebase or file set.

    The dependency analyser constructs a directed graph where each node
    is a module and each edge is an import statement.  After graph
    construction it runs cycle detection (e.g. Tarjan's algorithm) and
    packages the raw topology together with any circular paths into this
    model.  Detectors use it to flag architectural violations such as
    layering breaches or tangled dependency clusters.

    Attributes:
        nodes: Unique module identifiers present in the import graph.
        edges: Directed ``(importer, imported)`` pairs.
        cycles: Circular dependency paths detected in the graph.

    Example:
        >>> da = DependencyAnalysis(
        ...     nodes=["app", "db", "cache"],
        ...     edges=[("app", "db"), ("app", "cache"), ("cache", "db")],
        ...     cycles=[],
        ... )
        >>> len(da.cycles)
        0

    See Also:
        ``DependencyCycle``: Individual cycle record inside ``cycles``.
        ``Violation``: The pipeline converts flagged cycles into violations.
    """

    nodes: list[str]
    edges: list[tuple[str, str]]
    cycles: list[DependencyCycle]


class LanguagesResult(BaseModel):
    """Enumeration of every language the server can currently analyse.

    The ``list_zen_languages`` MCP tool returns a ``LanguagesResult`` so
    clients can discover which language keys are valid before calling
    analysis endpoints.  The list is populated at startup from the
    ``AnalyzerFactory`` registry and stays stable for the lifetime of the
    server process.

    Attributes:
        languages: Sorted list of supported language identifiers.

    Example:
        >>> lr = LanguagesResult(languages=["python", "rust", "typescript"])
        >>> "python" in lr.languages
        True

    See Also:
        ``AnalyzerFactory``: The registry that defines available languages.
    """

    languages: list[str]
