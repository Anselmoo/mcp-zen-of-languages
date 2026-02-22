"""GitHub Actions workflow analyzer."""

from __future__ import annotations

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
from mcp_zen_of_languages.languages.ci_yaml_utils import load_ci_yaml
from mcp_zen_of_languages.models import ParserResult


class GitHubActionsAnalyzer(BaseAnalyzer):
    """Analyze GitHub Actions workflow YAML files."""

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        """Initialize analyzer with optional threshold and pipeline overrides."""
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        """Return default analyzer settings."""
        return AnalyzerConfig()

    def language(self) -> str:
        """Return canonical language identifier."""
        return "github-actions"

    def capabilities(self) -> AnalyzerCapabilities:
        """Declare GitHub Actions analyzer support for AST-like workflow parsing."""
        return AnalyzerCapabilities(supports_ast=True)

    def parse_code(self, code: str) -> ParserResult | None:
        """Parse workflow YAML into a lightweight parser result wrapper."""
        return ParserResult(type="yaml", tree=load_ci_yaml(code))

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Return line-count metrics for workflow files."""
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        """Build the detector pipeline from registered mappings."""
        return super().build_pipeline()

    def _build_dependency_analysis(self, _context: AnalysisContext) -> object | None:
        """Skip dependency analysis for workflow YAML files."""
        return None
