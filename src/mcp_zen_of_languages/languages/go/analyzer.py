"""Language-specific analyzer implementation for go source files."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
    from mcp_zen_of_languages.models import CyclomaticSummary, ParserResult

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    AnalyzerConfig,
    BaseAnalyzer,
    DetectionPipeline,
)


class GoAnalyzer(BaseAnalyzer):
    """Analyzer for Go source files emphasizing simplicity and explicit error handling.

    Go analysis is unique because the language intentionally omits exceptions,
    generics-heavy abstractions, and inheritance in favor of composition,
    small interfaces, and explicit ``if err != nil`` checks.  This analyzer
    uses regex-based detectors to flag Go-specific anti-patterns such as
    ignored errors, ``init()`` abuse, goroutine leaks, and oversized
    interfaces that violate Go's philosophy of keeping things small and
    obvious.

    Note:
        No Go AST parser is currently wired; ``parse_code`` returns ``None``
        and detectors operate on raw source text.

    See Also:
        ``GoErrorHandlingDetector``, ``GoGoroutineLeakDetector`` for the
        highest-impact detectors in this pipeline.
    """

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        """Initialize instance.

        Args:
            config (AnalyzerConfig | None): Typed detector or analyzer configuration that controls thresholds.
            pipeline_config ('PipelineConfig' | None): Optional pipeline overrides used to customize detector configuration.
        """
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        """Return default analyzer configuration for this language.

        Returns:
            AnalyzerConfig: Default analyzer settings for the current language implementation.
        """
        return AnalyzerConfig()

    def language(self) -> str:
        """Return the analyzer language key.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "go"

    def parse_code(self, _code: str) -> ParserResult | None:
        """Parse source text into a language parser result when available.

        Args:
            code (str): Source code text being parsed or analyzed.

        Returns:
            ParserResult | None: Normalized parser output, or ``None`` when parsing is unavailable.
        """
        return None

    def compute_metrics(
        self, code: str, _ast_tree: ParserResult | None
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Compute complexity, maintainability, and line-count metrics.

        Args:
            code (str): Source code text being parsed or analyzed.
            ast_tree (ParserResult | None): Parsed syntax tree produced by the language parser, when available.

        Returns:
            tuple[CyclomaticSummary | None, float | None, int]: Tuple containing computed metrics in analyzer-defined order.
        """
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        """Build the detector pipeline for this analyzer.

        Returns:
            DetectionPipeline: Pipeline instance used to run configured detectors.
        """
        return super().build_pipeline()

    def _build_dependency_analysis(self, _context: AnalysisContext) -> object | None:
        """Build dependency analysis data for cross-file checks.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.

        Returns:
            object | None: Language-specific dependency analysis payload, or ``None`` when unsupported.
        """
        return None
