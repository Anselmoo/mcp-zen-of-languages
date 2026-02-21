"""SQL analyzer for query hygiene and maintainability checks."""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlglot

if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
    from mcp_zen_of_languages.models import CyclomaticSummary, ParserResult

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    AnalyzerConfig,
    BaseAnalyzer,
    DetectionPipeline,
)
from mcp_zen_of_languages.models import ParserResult


class SqlAnalyzer(BaseAnalyzer):
    """Analyze SQL text with SQL-specific detector pipeline."""

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        """Initialize analyzer with optional threshold and pipeline overrides."""
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        """Return baseline analyzer configuration for SQL."""
        return AnalyzerConfig()

    def language(self) -> str:
        """Return canonical language key."""
        return "sql"

    def parse_code(self, code: str) -> ParserResult | None:
        """Parse SQL source into sqlglot AST list when possible."""
        try:
            return ParserResult(type="sqlglot", tree=sqlglot.parse(code))
        except (sqlglot.errors.ParseError, ValueError):
            return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Return SQL line count; complexity metrics are not applicable."""
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        """Assemble SQL detection pipeline from registry mappings."""
        return super().build_pipeline()

    def _build_dependency_analysis(self, _context: AnalysisContext) -> object | None:
        """Return ``None`` because SQL files are analyzed independently."""
        return None


SQLAnalyzer = SqlAnalyzer
