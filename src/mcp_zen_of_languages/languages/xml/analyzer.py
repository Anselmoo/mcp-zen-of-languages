"""XML document analyzer for semantic markup, namespace usage, and structural quality."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
    from mcp_zen_of_languages.models import CyclomaticSummary

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    AnalyzerCapabilities,
    AnalyzerConfig,
    BaseAnalyzer,
    DetectionPipeline,
)
from mcp_zen_of_languages.models import ParserResult

logger = logging.getLogger(__name__)


class XmlAnalyzer(BaseAnalyzer):
    """Analyzes XML documents for semantic correctness, namespace hygiene, and element hierarchy.

    Delegates detection of presentational markup, oversized attributes, missing
    namespace declarations, absent schema references, repeated elements, and
    self-closing tag misuse to a configurable pipeline of XML-specific detectors.

    See Also:
        [`BaseAnalyzer`][BaseAnalyzer]: Template method base defining the analysis lifecycle.
    """

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        """Set up the XML analyzer with optional threshold and pipeline overrides.

        Args:
            config: Analyzer configuration controlling detection thresholds
                such as hierarchy depth or namespace strictness.
            pipeline_config: Optional overrides that customize which XML
                detectors run and their individual settings.
        """
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        """Provide baseline XML analysis thresholds when no explicit config is supplied.

        Returns:
            AnalyzerConfig: Default settings suitable for general-purpose XML documents.
        """
        return AnalyzerConfig()

    def language(self) -> str:
        """Return ``'xml'`` as the language key for factory and registry look-ups.

        Returns:
            str: The literal ``'xml'`` identifier.
        """
        return "xml"

    def capabilities(self) -> AnalyzerCapabilities:
        """Declare support for XML structure parsing via stdlib ``xml.etree``."""
        return AnalyzerCapabilities(supports_ast=True)

    def parse_code(self, code: str) -> ParserResult | None:
        """Parse XML text into an ElementTree via ``xml.etree.ElementTree``.

        Args:
            code: Raw XML markup to parse.

        Returns:
            ParserResult wrapping the root Element, or ``None`` on parse failure.
        """
        try:
            tree = ET.fromstring(code)  # noqa: S314
            return ParserResult(type="xml", tree=tree)
        except ET.ParseError:
            logger.debug("Failed to parse XML")
            return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Compute a line count for the XML document; complexity metrics are not applicable.

        Args:
            code: Raw XML markup whose lines are counted.
            ast_tree: Unused; included for interface compatibility with [`BaseAnalyzer`][BaseAnalyzer].

        Returns:
            tuple[CyclomaticSummary | None, float | None, int]: ``(None, None, line_count)``
                since cyclomatic complexity and maintainability index are not meaningful for XML.
        """
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        """Assemble the XML detection pipeline from registered detectors.

        Returns:
            DetectionPipeline: Pipeline wired with XML-specific detectors for
                semantic markup, attributes, namespaces, validity, and hierarchy checks.
        """
        return super().build_pipeline()

    def _build_dependency_analysis(self, _context: AnalysisContext) -> object | None:
        """Return ``None`` because XML files have no cross-file dependency semantics.

        Args:
            context: Current analysis context (unused for XML).

        Returns:
            object | None: Always ``None``; XML documents are analyzed in isolation.
        """
        return None
