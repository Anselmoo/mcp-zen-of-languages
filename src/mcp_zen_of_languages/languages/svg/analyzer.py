"""SVG analyzer for accessibility and maintainability checks."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
    from mcp_zen_of_languages.models import CyclomaticSummary

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.base import AnalyzerCapabilities
from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.base import BaseAnalyzer
from mcp_zen_of_languages.models import ParserResult


logger = logging.getLogger(__name__)


class SvgAnalyzer(BaseAnalyzer):
    """Analyzes SVG files using stdlib XML parsing and SVG detectors."""

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
        return "svg"

    def capabilities(self) -> AnalyzerCapabilities:
        return AnalyzerCapabilities(supports_ast=True)

    def parse_code(self, code: str) -> ParserResult | None:
        try:
            tree = ET.fromstring(code)  # noqa: S314
            return ParserResult(type="svg", tree=tree)
        except ET.ParseError:
            logger.debug("Failed to parse SVG")
            return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        return None, None, len(code.splitlines())

    def _build_dependency_analysis(self, _context: AnalysisContext) -> object | None:
        return None
