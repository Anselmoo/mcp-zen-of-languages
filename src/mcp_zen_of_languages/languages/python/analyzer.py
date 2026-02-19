"""Python-specific analyzer built on the Template Method / Strategy architecture.

This module houses ``PythonAnalyzer``, the reference language implementation.
It plugs Python parsing (stdlib ``ast``), radon-based metrics, and the
Python detector pipeline into the shared ``BaseAnalyzer`` skeleton so that
every zen-principle check runs in a deterministic, fail-safe sequence.

See Also:
    ``mcp_zen_of_languages.analyzers.base.BaseAnalyzer`` for the template
    method that orchestrates parsing → metrics → detection → result building.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
    from mcp_zen_of_languages.models import (
        CyclomaticSummary,
        ParserResult,
    )

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    AnalyzerConfig,
    BaseAnalyzer,
    DetectionPipeline,
    LocationHelperMixin,
    PythonAnalyzerConfig,
)

# Minimum number of whitespace-split tokens in an import statement to extract the module name
MIN_IMPORT_PARTS = 2


class PythonAnalyzer(BaseAnalyzer, LocationHelperMixin):
    """Analyze Python source code against zen principles.

    ``PythonAnalyzer`` is the reference language implementation.  It overrides
    the three Template Method hooks — ``parse_code``, ``compute_metrics``, and
    ``build_pipeline`` — to wire stdlib ``ast`` parsing, radon-based metrics
    collection, and the full suite of Python-specific violation detectors.

    The analyzer also builds an import-level dependency graph so that
    cross-file detectors (circular dependencies, duplicate implementations,
    deep inheritance) can reason about the broader codebase.

    Attributes:
        _pipeline_config: Optional overrides applied on top of the rule-derived
            detector defaults when constructing the detection pipeline.
    """

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        """Initialise the Python analyzer with optional config overrides.

        Args:
            config: Typed analyzer configuration controlling thresholds such as
                max cyclomatic complexity or nesting depth.  When ``None``,
                ``default_config()`` supplies sensible defaults.
            pipeline_config: Pipeline-level overrides merged on top of the
                rule-derived detector defaults.  Typically loaded from the
                ``pipelines:`` section of ``zen-config.yaml``.
        """
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> PythonAnalyzerConfig:
        """Return the baseline Python configuration.

        These defaults are used when no explicit ``config`` is passed to the
        constructor.  They encode the recommended thresholds for idiomatic
        Python code (e.g. max nesting depth of 3, max cyclomatic complexity
        of 10).

        Returns:
            PythonAnalyzerConfig: A fresh config instance with community-standard
                thresholds pre-populated.
        """
        return PythonAnalyzerConfig()

    def language(self) -> str:
        """Return ``"python"`` as the language identifier.

        This string keys into the analyzer factory and the detector registry,
        ensuring the correct set of detectors is loaded for Python source.

        Returns:
            str: Always ``"python"``.
        """
        return "python"

    def parse_code(self, code: str) -> ParserResult | None:
        """Parse Python source into a ``ParserResult`` representation.

        Delegates to ``parse_python``, which already handles backend selection
        and returns the canonical ``ParserResult`` consumed by detectors.

        Args:
            code: Raw Python source text to parse.

        Returns:
            ParserResult | None: Parse tree, or ``None`` if a
                ``SyntaxError`` or other parse failure occurs.
        """
        from mcp_zen_of_languages.utils.parsers import parse_python

        try:
            return parse_python(code)
        except Exception:  # noqa: BLE001
            return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Collect cyclomatic complexity, maintainability index, and line count.

        Uses ``MetricsCollector`` which internally calls radon for cyclomatic
        complexity per function block and Halstead-based maintainability index.
        These metrics feed into several detectors (e.g.
        ``CyclomaticComplexityDetector``, severity scaling).

        Args:
            code: Python source text to measure.
            ast_tree: Parsed syntax tree (currently unused by radon but
                accepted for API symmetry with other language analyzers).

        Returns:
            tuple[CyclomaticSummary | None, float | None, int]: Three-element
                tuple of (cyclomatic summary, maintainability index, total
                lines).
        """
        from mcp_zen_of_languages.metrics.collector import MetricsCollector

        return MetricsCollector.collect(code)

    def build_pipeline(self) -> DetectionPipeline:
        """Assemble the Python detection pipeline from the detector registry.

        Delegates to the base class which looks up all detectors registered
        for ``"python"`` in the global registry and wires them with configs
        derived from the active zen rules and any ``pipeline_config`` overrides.

        Returns:
            DetectionPipeline: Ordered pipeline of Python violation detectors.
        """
        return super().build_pipeline()

    def _build_dependency_analysis(self, context: AnalysisContext) -> object | None:
        """Build an import-level dependency graph for cross-file analysis.

        When ``repository_imports`` are available (multi-file analysis mode),
        a full graph is constructed.  Otherwise, a lightweight single-file
        graph is derived by scanning ``import`` and ``from … import``
        statements with simple string splitting.

        The resulting graph powers detectors such as
        ``CircularDependencyDetector`` and ``DeepInheritanceDetector``.

        Args:
            context: Current analysis context carrying the source code, file
                path, and optionally the repository-wide import map.

        Returns:
            object | None: A ``DependencyGraph`` when construction succeeds,
                or ``None`` on failure.
        """
        from mcp_zen_of_languages.metrics.dependency_graph import build_import_graph

        try:
            if context.repository_imports:
                return build_import_graph(context.repository_imports)

            # Simple import extraction
            imports = []
            for line in context.code.splitlines():
                stripped = line.strip()
                if stripped.startswith(("import ", "from ")):
                    parts = stripped.split()
                    if len(parts) >= MIN_IMPORT_PARTS:
                        imports.append(parts[1].split(".")[0])

            file_imports = {(context.path or "<current>"): imports}
            return build_import_graph(file_imports)
        except Exception:  # noqa: BLE001
            return None
