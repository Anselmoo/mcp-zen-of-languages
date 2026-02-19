"""Analyzer implementation for GitLab CI pipeline YAML."""

from __future__ import annotations

# ruff: noqa: D102, D107
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


class GitLabCIAnalyzer(BaseAnalyzer):
    """Analyze GitLab CI YAML files."""

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        return AnalyzerConfig()

    def language(self) -> str:
        return "gitlab_ci"

    def parse_code(self, _code: str) -> ParserResult | None:
        return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        return super().build_pipeline()

    def _build_dependency_analysis(self, _context: AnalysisContext) -> object | None:
        return None
