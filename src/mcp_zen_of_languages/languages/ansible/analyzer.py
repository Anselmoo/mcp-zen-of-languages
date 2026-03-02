"""Analyzer implementation for Ansible playbook and role YAML files."""

from __future__ import annotations

import logging

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
    from mcp_zen_of_languages.models import CyclomaticSummary

import yaml

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.base import AnalyzerCapabilities
from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.base import BaseAnalyzer
from mcp_zen_of_languages.models import ParserResult


logger = logging.getLogger(__name__)


class AnsibleAnalyzer(BaseAnalyzer):
    """Analyze Ansible YAML files."""

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
        return "ansible"

    def capabilities(self) -> AnalyzerCapabilities:
        """Declare support for YAML structure parsing of Ansible files."""
        return AnalyzerCapabilities(supports_ast=True)

    def parse_code(self, code: str) -> ParserResult | None:
        """Parse Ansible YAML into a structured mapping via ``yaml.safe_load``."""
        try:
            tree = yaml.safe_load(code)
            return ParserResult(type="yaml", tree=tree)
        except yaml.YAMLError:
            logger.debug("Failed to parse Ansible YAML")
            return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Return line-count metrics for Ansible files."""
        return None, None, len(code.splitlines())

    def _build_dependency_analysis(self, _context: AnalysisContext) -> object | None:
        """Return ``None`` because Ansible analysis is file-local."""
        return None
