"""Analyze CSS-family stylesheets with the shared zen analyzer pipeline."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
    from mcp_zen_of_languages.models import CyclomaticSummary, ParserResult

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    AnalyzerCapabilities,
    AnalyzerConfig,
    BaseAnalyzer,
    DetectionPipeline,
)

_IMPORT_RE = re.compile(r"""@import\s+(?:url\s*\(\s*)?['"](.+?)['"]""")


class CssAnalyzer(BaseAnalyzer):
    """Analyzer for CSS-family stylesheets."""

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        """Initialize analyzer with optional config and pipeline overrides."""
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        """Return default analyzer thresholds."""
        return AnalyzerConfig()

    def language(self) -> str:
        """Return canonical language key."""
        return "css"

    def capabilities(self) -> AnalyzerCapabilities:
        """Declare support for ``@import`` dependency extraction."""
        return AnalyzerCapabilities(supports_dependency_analysis=True)

    def parse_code(self, _code: str) -> ParserResult | None:
        """Return ``None`` for text-scanned stylesheet analysis."""
        return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Compute line count metrics for stylesheet content."""
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        """Build detector pipeline from registered CSS detectors."""
        return super().build_pipeline()

    def _build_dependency_analysis(self, context: AnalysisContext) -> object | None:
        """Extract ``@import`` directives and build a stylesheet dependency graph.

        Args:
            context: Current analysis context with stylesheet source text.

        Returns:
            DependencyAnalysis with import edges, or ``None`` when no imports found.
        """
        imports: list[str] = []
        for line in context.code.splitlines():
            m = _IMPORT_RE.search(line.strip())
            if m:
                imports.append(m.group(1))
        if not imports:
            return None
        from mcp_zen_of_languages.metrics.dependency_graph import build_import_graph

        return build_import_graph({(context.path or "<current>"): imports})
