"""Language-specific analyzer implementation for typescript source files."""

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
    TypeScriptAnalyzerConfig,
)


class TypeScriptAnalyzer(BaseAnalyzer):
    """Analyzer for TypeScript source files focusing on type-system discipline.

    TypeScript analysis is unique because the language offers an opt-in type
    system layered over JavaScript.  Without enforcement, codebases drift
    toward ``any``-heavy, loosely-typed patterns that negate TypeScript's
    value.  This analyzer uses regex-based heuristic detectors (no TS AST
    parser yet) to surface anti-patterns such as ``any`` abuse, missing
    return types, and non-null assertion overuse.

    Note:
        Because no tree-sitter or TypeScript compiler API parser is wired,
        ``parse_code`` returns ``None`` and all detectors operate on raw
        source text via regular expressions.

    See Also:
        ``TypeScriptAnalyzerConfig`` for language-specific threshold defaults.
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

    def default_config(self) -> TypeScriptAnalyzerConfig:
        """Return default analyzer configuration for this language.

        Returns:
            TypeScriptAnalyzerConfig: Default analyzer settings for the current language implementation.
        """
        return TypeScriptAnalyzerConfig()

    def language(self) -> str:
        """Return the analyzer language key.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "typescript"

    def parse_code(self, _code: str) -> ParserResult | None:
        """Parse source text into a language parser result when available.

        Args:
            code (str): Source code text being parsed or analyzed.

        Returns:
            ParserResult | None: Normalized parser output, or ``None`` when parsing is unavailable.
        """
        # No TS parser wired yet; return None to allow heuristic detectors to run.
        return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
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
