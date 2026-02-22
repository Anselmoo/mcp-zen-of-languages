"""YAML configuration file analyzer for indentation, key clarity, and structural consistency."""

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


class YamlAnalyzer(BaseAnalyzer):
    """Analyzes YAML files for indentation discipline, key naming, and formatting consistency.

    Delegates detection of indentation irregularities, tab characters, duplicate
    keys, casing violations, short key names, list-marker inconsistencies,
    missing comments, and unquoted special strings to a configurable pipeline
    of YAML-specific detectors.

    See Also:
        [`BaseAnalyzer`][BaseAnalyzer]: Template method base defining the analysis lifecycle.
    """

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        """Set up the YAML analyzer with optional threshold and pipeline overrides.

        Args:
            config: Analyzer configuration controlling detection thresholds
                such as indentation width or minimum key length.
            pipeline_config: Optional overrides that customize which YAML
                detectors run and their individual settings.
        """
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        """Provide baseline YAML analysis thresholds when no explicit config is supplied.

        Returns:
            AnalyzerConfig: Default settings suitable for general-purpose YAML files.
        """
        return AnalyzerConfig()

    def language(self) -> str:
        """Return ``'yaml'`` as the language key for factory and registry look-ups.

        Returns:
            str: The literal ``'yaml'`` identifier.
        """
        return "yaml"

    def capabilities(self) -> AnalyzerCapabilities:
        """Declare support for YAML structure parsing via PyYAML."""
        return AnalyzerCapabilities(supports_ast=True)

    def parse_code(self, code: str) -> ParserResult | None:
        """Parse YAML text into a structured mapping via ``yaml.safe_load``.

        Args:
            code: Raw YAML text to parse.

        Returns:
            ParserResult wrapping the parsed mapping, or ``None`` on parse failure.
        """
        try:
            tree = yaml.safe_load(code)
            return ParserResult(type="yaml", tree=tree)
        except yaml.YAMLError:
            logger.debug("Failed to parse YAML")
            return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Compute a line count for the YAML file; complexity metrics are not applicable.

        Args:
            code: Raw YAML text whose lines are counted.
            ast_tree: Unused; included for interface compatibility with [`BaseAnalyzer`][BaseAnalyzer].

        Returns:
            tuple[CyclomaticSummary | None, float | None, int]: ``(None, None, line_count)``
                since cyclomatic complexity and maintainability index are not meaningful for YAML.
        """
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        """Assemble the YAML detection pipeline from registered detectors.

        Returns:
            DetectionPipeline: Pipeline wired with YAML-specific detectors for
                indentation, tabs, duplicate keys, casing, and string style checks.
        """
        return super().build_pipeline()

    def _build_dependency_analysis(self, _context: AnalysisContext) -> object | None:
        """Return ``None`` because YAML files have no cross-file dependency semantics.

        Args:
            context: Current analysis context (unused for YAML).

        Returns:
            object | None: Always ``None``; YAML documents are self-contained.
        """
        return None
