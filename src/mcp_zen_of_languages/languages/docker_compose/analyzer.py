"""Docker Compose analyzer for service-definition best-practice checks."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
    from mcp_zen_of_languages.models import CyclomaticSummary, ParserResult

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    AnalyzerConfig,
    BaseAnalyzer,
)


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

    def parse_code(self, _code: str) -> ParserResult | None:
        """Return ``None`` because compose checks are text-oriented."""
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
