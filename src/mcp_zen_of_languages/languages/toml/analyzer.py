"""TOML configuration file analyzer for section structure, key quality, and value formatting."""

from __future__ import annotations

import logging
import tomllib
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


class TomlAnalyzer(BaseAnalyzer):
    """Analyzes TOML files for table organization, key naming, and value clarity.

    Delegates detection of inline-table overuse, duplicate keys, casing
    inconsistencies, trailing commas, comment coverage, section ordering,
    datetime formatting, and numeric precision to a configurable pipeline
    of TOML-specific detectors.

    See Also:
        [`BaseAnalyzer`][BaseAnalyzer]: Template method base defining the analysis lifecycle.
    """

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        """Set up the TOML analyzer with optional threshold and pipeline overrides.

        Args:
            config: Analyzer configuration controlling detection thresholds
                such as comment clarity or key casing limits.
            pipeline_config: Optional overrides that customize which TOML
                detectors run and their individual settings.
        """
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        """Provide baseline TOML analysis thresholds when no explicit config is supplied.

        Returns:
            AnalyzerConfig: Default settings suitable for general-purpose TOML files.
        """
        return AnalyzerConfig()

    def language(self) -> str:
        """Return ``'toml'`` as the language key for factory and registry look-ups.

        Returns:
            str: The literal ``'toml'`` identifier.
        """
        return "toml"

    def capabilities(self) -> AnalyzerCapabilities:
        """Declare support for TOML structure parsing via stdlib ``tomllib``."""
        return AnalyzerCapabilities(supports_ast=True)

    def parse_code(self, code: str) -> ParserResult | None:
        """Parse TOML text into a mapping via ``tomllib.loads``.

        Args:
            code: Raw TOML text to parse.

        Returns:
            ParserResult wrapping the parsed mapping, or ``None`` on parse failure.
        """
        try:
            tree = tomllib.loads(code)
            return ParserResult(type="toml", tree=tree)
        except (tomllib.TOMLDecodeError, ValueError):
            logger.debug("Failed to parse TOML")
            return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Compute a line count for the TOML file; complexity metrics are not applicable.

        Args:
            code: Raw TOML text whose lines are counted.
            ast_tree: Unused; included for interface compatibility with [`BaseAnalyzer`][BaseAnalyzer].

        Returns:
            tuple[CyclomaticSummary | None, float | None, int]: ``(None, None, line_count)``
                since cyclomatic complexity and maintainability index are not meaningful for TOML.
        """
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        """Assemble the TOML detection pipeline from registered detectors.

        Returns:
            DetectionPipeline: Pipeline wired with TOML-specific detectors for
                inline tables, duplicate keys, casing, ordering, and formatting checks.
        """
        return super().build_pipeline()

    def _build_dependency_analysis(self, _context: AnalysisContext) -> object | None:
        """Return ``None`` because TOML files have no cross-file dependency semantics.

        Args:
            context: Current analysis context (unused for TOML).

        Returns:
            object | None: Always ``None``; TOML documents are self-contained.
        """
        return None
