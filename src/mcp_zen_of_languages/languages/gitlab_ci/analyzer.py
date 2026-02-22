"""Analyzer implementation for GitLab CI pipeline YAML."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
    from mcp_zen_of_languages.models import CyclomaticSummary

import yaml

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    AnalyzerCapabilities,
    AnalyzerConfig,
    BaseAnalyzer,
    DetectionPipeline,
)
from mcp_zen_of_languages.models import ParserResult

logger = logging.getLogger(__name__)


class GitLabCIAnalyzer(BaseAnalyzer):
    """Analyze GitLab CI YAML files."""

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
        return "gitlab_ci"

    def capabilities(self) -> AnalyzerCapabilities:
        """Declare support for YAML structure parsing of GitLab CI pipelines."""
        return AnalyzerCapabilities(supports_ast=True)

    def parse_code(self, code: str) -> ParserResult | None:
        """Parse GitLab CI YAML into a structured mapping via ``yaml.safe_load``.

        Args:
            code: Raw GitLab CI YAML text.

        Returns:
            ParserResult wrapping the parsed mapping, or ``None`` on parse failure.
        """
        try:
            tree = yaml.safe_load(code)
            return ParserResult(type="yaml", tree=tree)
        except yaml.YAMLError:
            logger.debug("Failed to parse GitLab CI YAML")
            return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Return line-count metrics for GitLab CI files."""
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        """Build the detector pipeline from registered mappings."""
        return super().build_pipeline()

    def _build_dependency_analysis(self, _context: AnalysisContext) -> object | None:
        """Return ``None``; GitLab CI dependency analysis is not yet implemented."""
        return None
