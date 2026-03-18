"""Composition helpers for attaching universal dogma analysis to results."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_zen_of_languages.dogmas.analyzer import UniversalDogmaAnalyzer


if TYPE_CHECKING:
    from mcp_zen_of_languages.models import AnalysisResult


def attach_dogma_analysis(
    result: AnalysisResult,
    analyzer: UniversalDogmaAnalyzer | None = None,
) -> AnalysisResult:
    """Return a copy of ``result`` with universal dogma analysis attached."""
    dogma_analyzer = analyzer or UniversalDogmaAnalyzer()
    return dogma_analyzer.enrich_result(result)


__all__ = ["attach_dogma_analysis"]
