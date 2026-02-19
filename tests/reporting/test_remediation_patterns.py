from __future__ import annotations

from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    Metrics,
    Violation,
)
from mcp_zen_of_languages.reporting.remediation_patterns import resolve_pattern
from mcp_zen_of_languages.reporting.theme_clustering import build_big_picture_analysis

MAX_HEALTH_SCORE = 100


def _make_result(violations: list[Violation]) -> AnalysisResult:
    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    metrics = Metrics(cyclomatic=cyclomatic, maintainability_index=0.0, lines_of_code=0)
    return AnalysisResult(
        language="python",
        path="sample.py",
        metrics=metrics,
        violations=violations,
        overall_score=90.0,
    )


def test_resolve_pattern_matches_docstring():
    violation = Violation(
        principle="Missing docstring",
        severity=5,
        message="Add docstring",
        location=None,
    )
    pattern = resolve_pattern(violation, "python")
    assert pattern.theme == "Documentation"
    assert "docstring" in pattern.action.lower()


def test_big_picture_analysis_clusters():
    violations = [
        Violation(principle="Cyclomatic complexity", severity=9, message="Too complex"),
        Violation(principle="Missing docstring", severity=4, message="Add docstring"),
    ]
    analysis = build_big_picture_analysis([_make_result(violations)])
    assert analysis.clusters
    assert analysis.refactoring_roadmap
    assert analysis.health_score <= MAX_HEALTH_SCORE
