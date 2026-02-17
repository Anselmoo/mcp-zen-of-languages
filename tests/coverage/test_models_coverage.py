from __future__ import annotations

from mcp_zen_of_languages.models import AnalysisResult, CyclomaticSummary, Metrics


def test_analysis_result_getitem():
    metrics = Metrics(
        cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
        maintainability_index=0.0,
        lines_of_code=1,
    )
    result = AnalysisResult(
        language="python", metrics=metrics, violations=[], overall_score=100.0
    )
    assert result["language"] == "python"
