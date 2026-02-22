"""Docker Compose analyzer for service-definition best-practice checks."""

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
)
from mcp_zen_of_languages.models import ParserResult

logger = logging.getLogger(__name__)


class DockerComposeAnalyzer(BaseAnalyzer):
    """Analyzes docker-compose files using compose-specific text detectors."""

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        """Initialize the Docker Compose analyzer."""
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        """Return default analyzer thresholds."""
        return AnalyzerConfig()

    def language(self) -> str:
        """Return the canonical language key."""
        return "docker_compose"

    def capabilities(self) -> AnalyzerCapabilities:
        """Declare support for YAML structure parsing of compose files."""
        return AnalyzerCapabilities(supports_ast=True)

    def parse_code(self, code: str) -> ParserResult | None:
        """Parse compose YAML into a structured mapping via ``yaml.safe_load``.

        Args:
            code: Raw docker-compose YAML text.

        Returns:
            ParserResult wrapping the parsed mapping, or ``None`` on parse failure.
        """
        try:
            tree = yaml.safe_load(code)
            return ParserResult(type="yaml", tree=tree)
        except yaml.YAMLError:
            logger.debug("Failed to parse Docker Compose YAML")
            return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Return line-count metrics for compose YAML files."""
        return None, None, len(code.splitlines())

    def _build_dependency_analysis(self, _context: AnalysisContext) -> object | None:
        """Return ``None`` because compose analysis is file-local."""
        return None
