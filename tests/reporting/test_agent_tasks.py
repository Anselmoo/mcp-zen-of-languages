from __future__ import annotations

from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    Metrics,
    Violation,
)
from mcp_zen_of_languages.reporting.agent_tasks import build_agent_tasks


def _make_result(path: str, severity: int) -> AnalysisResult:
    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    metrics = Metrics(cyclomatic=cyclomatic, maintainability_index=0.0, lines_of_code=0)
    violation = Violation(
        principle="Rule",
        severity=severity,
        message="Fix it",
        location=None,
    )
    return AnalysisResult(
        language="python",
        path=path,
        metrics=metrics,
        violations=[violation],
        overall_score=100.0,
    )


def test_build_agent_tasks_filters_by_severity():
    results = [_make_result("a.py", 9), _make_result("b.py", 3)]
    task_list = build_agent_tasks(results, project=".", min_severity=5)
    assert task_list.total_tasks == 1
    assert task_list.tasks[0].file == "a.py"
    assert task_list.tasks[0].theme
    assert task_list.tasks[0].effort in {"S", "M", "L"}
    assert task_list.health_score >= 0
    assert task_list.clusters
