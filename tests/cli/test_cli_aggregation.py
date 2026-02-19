from __future__ import annotations

from mcp_zen_of_languages import cli
from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    Metrics,
    Violation,
)

EXPECTED_FILES = 2
EXPECTED_VIOLATIONS = 2


def _make_result(path: str, violations: list[Violation]) -> AnalysisResult:
    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    metrics = Metrics(cyclomatic=cyclomatic, maintainability_index=0.0, lines_of_code=0)
    return AnalysisResult(
        language="python",
        path=path,
        metrics=metrics,
        violations=violations,
        overall_score=100.0,
    )


def test_aggregate_results_counts_and_order():
    result_a = _make_result(
        "a.py",
        [Violation(principle="P", severity=9, message="msg", location=None)],
    )
    result_b = _make_result(
        "b.py",
        [Violation(principle="P", severity=4, message="msg", location=None)],
    )
    summary = cli._aggregate_results([result_a, result_b])
    assert summary.total_files == EXPECTED_FILES
    assert summary.total_violations == EXPECTED_VIOLATIONS
    assert summary.severity_counts.critical == 1
    assert summary.severity_counts.medium == 1
    assert summary.worst_offenders[0].path == "a.py"
