"""Dockerfile analyzer for container image best-practice checks."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
    from mcp_zen_of_languages.models import CyclomaticSummary, ParserResult

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    AnalyzerCapabilities,
    AnalyzerConfig,
    BaseAnalyzer,
)

_FROM_RE = re.compile(r"^FROM\s+(\S+)", re.IGNORECASE)
_COPY_FROM_RE = re.compile(r"^COPY\s+--from=(\S+)", re.IGNORECASE)


class DockerfileAnalyzer(BaseAnalyzer):
    """Analyzes Dockerfiles using rule-driven text detectors."""

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        """Initialize the Dockerfile analyzer."""
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        """Return default analyzer thresholds."""
        return AnalyzerConfig()

    def language(self) -> str:
        """Return the canonical language key."""
        return "dockerfile"

    def capabilities(self) -> AnalyzerCapabilities:
        """Declare support for FROM/COPY --from dependency extraction."""
        return AnalyzerCapabilities(supports_dependency_analysis=True)

    def parse_code(self, _code: str) -> ParserResult | None:
        """Return ``None`` because Dockerfile checks are text-oriented."""
        return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Return line-count metrics for Dockerfiles."""
        return None, None, len(code.splitlines())

    def _build_dependency_analysis(self, context: AnalysisContext) -> object | None:
        """Extract ``FROM`` and ``COPY --from`` references as image dependencies.

        Args:
            context: Current analysis context with Dockerfile source text.

        Returns:
            DependencyAnalysis with image dependency edges, or ``None`` when none found.
        """
        imports: list[str] = []
        for line in context.code.splitlines():
            stripped = line.strip()
            m = _FROM_RE.match(stripped)
            if m:
                imports.append(m.group(1))
                continue
            m = _COPY_FROM_RE.match(stripped)
            if m:
                imports.append(m.group(1))
        if not imports:
            return None
        from mcp_zen_of_languages.metrics.dependency_graph import build_import_graph

        return build_import_graph({(context.path or "<current>"): imports})
