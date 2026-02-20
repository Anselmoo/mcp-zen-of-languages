"""JSON configuration file analyzer for structure, consistency, and formatting quality."""

from __future__ import annotations

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


class JsonAnalyzer(BaseAnalyzer):
    """Analyzes JSON documents for structural quality, key consistency, and data formatting.

    Delegates detection of strictness violations, schema drift, date formats,
    null handling, key casing, and array ordering to a configurable pipeline of
    JSON-specific detectors.

    See Also:
        [`BaseAnalyzer`][BaseAnalyzer]: Template method base defining the analysis lifecycle.
    """

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        """Set up the JSON analyzer with optional threshold and pipeline overrides.

        Args:
            config: Analyzer configuration controlling detection thresholds
                such as strictness or schema consistency limits.
            pipeline_config: Optional overrides that customize which JSON
                detectors run and their individual settings.
        """
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        """Provide baseline JSON analysis thresholds when no explicit config is supplied.

        Returns:
            AnalyzerConfig: Default settings suitable for general-purpose JSON documents.
        """
        return AnalyzerConfig()

    def language(self) -> str:
        """Return ``'json'`` as the language key for factory and registry look-ups.

        Returns:
            str: The literal ``'json'`` identifier.
        """
        return "json"

    def parse_code(self, _code: str) -> ParserResult | None:
        """Return ``None`` because JSON analysis uses direct text scanning rather than AST parsing.

        Args:
            code: Raw JSON text to analyze.

        Returns:
            ParserResult | None: Always ``None`` for JSON; detectors operate on raw text.
        """
        return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Compute a line count for the JSON document; complexity metrics are not applicable.

        Args:
            code: Raw JSON text whose lines are counted.
            ast_tree: Unused; included for interface compatibility with [`BaseAnalyzer`][BaseAnalyzer].

        Returns:
            tuple[CyclomaticSummary | None, float | None, int]: ``(None, None, line_count)``
                since cyclomatic complexity and maintainability index are not meaningful for JSON.
        """
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        """Assemble the JSON detection pipeline from registered detectors.

        Returns:
            DetectionPipeline: Pipeline wired with JSON-specific detectors such as
                strictness, schema consistency, date format, and key casing checks.
        """
        return super().build_pipeline()

    def _build_dependency_analysis(self, _context: AnalysisContext) -> object | None:
        """Return ``None`` because JSON files have no cross-file dependency semantics.

        Args:
            context: Current analysis context (unused for JSON).

        Returns:
            object | None: Always ``None``; JSON documents are self-contained.
        """
        return None


JSONAnalyzer = JsonAnalyzer
