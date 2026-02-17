from __future__ import annotations

from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    Metrics,
    Violation,
)
from mcp_zen_of_languages.rendering.report import render_report_terminal
from mcp_zen_of_languages.reporting.models import ReportOutput


def _build_result(path: str, violations: list[Violation]) -> AnalysisResult:
    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    metrics = Metrics(cyclomatic=cyclomatic, maintainability_index=0.0, lines_of_code=1)
    return AnalysisResult(
        language="python",
        path=path,
        metrics=metrics,
        violations=violations,
        overall_score=90.0,
    )


def test_render_report_terminal_with_gaps_and_prompts(capsys):
    violations = [Violation(principle="p", severity=7, message="m")]
    analysis = [
        _build_result("a.py", violations).model_dump(),
        _build_result("b.py", []).model_dump(),
    ]
    report = ReportOutput(
        markdown="md",
        data={
            "target": "repo",
            "languages": ["python"],
            "summary": {
                "total_files": 2,
                "total_violations": 1,
                "severity_counts": {"critical": 0, "high": 1, "medium": 0, "low": 0},
                "score": 85,
            },
            "analysis": analysis,
            "gaps": {
                "detector_gaps": [
                    {
                        "language": "python",
                        "rule_id": "python-999",
                        "principle": "Test",
                        "severity": 5,
                        "reason": "missing",
                    }
                ],
                "feature_gaps": [
                    {
                        "area": "docs",
                        "description": "Missing docs",
                        "suggested_next_step": "Add docs",
                    }
                ],
            },
            "prompts": {
                "file_prompts": [
                    {"path": "a.py", "language": "python", "prompt": "fix"}
                ],
                "generic_prompts": [{"title": "t", "prompt": "p"}],
            },
        },
    )
    render_report_terminal(report)
    captured = capsys.readouterr()
    assert "Zen Report" in captured.out
    assert "Gap Analysis" in captured.out
    assert "HIGH" in captured.out
    assert "Total violations" in captured.out


def test_render_report_terminal_no_gaps(capsys):
    report = ReportOutput(
        markdown="md",
        data={
            "target": "repo",
            "languages": ["python"],
            "summary": {
                "total_files": 0,
                "total_violations": 0,
                "severity_counts": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            },
            "analysis": [],
            "gaps": {"detector_gaps": [], "feature_gaps": []},
            "prompts": {"file_prompts": [], "generic_prompts": []},
        },
    )
    render_report_terminal(report)
    captured = capsys.readouterr()
    assert "No gaps reported." in captured.out


def test_render_report_terminal_skips_invalid_gaps(capsys):
    report = ReportOutput(
        markdown="md",
        data={
            "target": "repo",
            "languages": ["python"],
            "summary": {
                "total_files": 0,
                "total_violations": 0,
                "severity_counts": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            },
            "analysis": [],
            "gaps": {"detector_gaps": ["bad"], "feature_gaps": ["bad"]},
            "prompts": {"file_prompts": [], "generic_prompts": []},
        },
    )
    render_report_terminal(report)
    captured = capsys.readouterr()
    assert "Gap Analysis" in captured.out
