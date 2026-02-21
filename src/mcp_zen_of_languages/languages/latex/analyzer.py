"""LaTeX analyzer based on regex-driven detectors."""

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


class LatexAnalyzer(BaseAnalyzer):
    """Analyze LaTeX files for structural clarity, correctness, and maintainability."""

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        """Initialize analyzer with optional global and detector-level overrides."""
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        """Return default analyzer configuration for LaTeX."""
        return AnalyzerConfig()

    def language(self) -> str:
        """Return the canonical language key."""
        return "latex"

    def parse_code(self, _code: str) -> ParserResult | None:
        """Return ``None`` because LaTeX checks are regex-based."""
        return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Return line count only for LaTeX sources."""
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        """Build the registered LaTeX detector pipeline."""
        return super().build_pipeline()

    def _build_dependency_analysis(self, _context: AnalysisContext) -> object | None:
        """Return ``None`` because dependency graphs are not used for LaTeX."""
        return None
