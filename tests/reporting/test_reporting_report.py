from __future__ import annotations

from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    Metrics,
    Violation,
)
from mcp_zen_of_languages.reporting.gaps import GapAnalysis
from mcp_zen_of_languages.reporting.models import ReportContext
from mcp_zen_of_languages.reporting.report import (
    _format_analysis_markdown,
    _format_gap_markdown,
    _format_prompts_markdown,
    _summarize_results,
    generate_report,
)

EXPECTED_FILES = 2
EXPECTED_VIOLATIONS = 2


def _build_result(path: str, language: str, severity: int) -> AnalysisResult:
    return AnalysisResult(
        language=language,
        path=path,
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=0.0,
            lines_of_code=1,
        ),
        violations=[Violation(principle="Test", severity=severity, message="Example")],
        overall_score=90.0,
    )


def test_summarize_results_counts_severity():
    results = [_build_result("a.py", "python", 9), _build_result("b.py", "python", 4)]
    summary = _summarize_results(results)
    assert summary.total_files == EXPECTED_FILES
    assert summary.total_violations == EXPECTED_VIOLATIONS
    assert summary.severity_counts["critical"] == 1
    assert summary.severity_counts["medium"] == 1


def test_summarize_results_counts_low():
    results = [_build_result("c.py", "python", 1)]
    summary = _summarize_results(results)
    assert summary.severity_counts["low"] == 1


def test_format_analysis_markdown_includes_more_count():
    base = _build_result("a.py", "python", 5)
    results = [base.model_copy(update={"violations": base.violations * 12})]
    lines = _format_analysis_markdown(results)
    assert any("...and" in line for line in lines)


def test_format_gap_markdown_empty():
    gaps = GapAnalysis(detector_gaps=[], feature_gaps=[])
    lines = _format_gap_markdown(gaps)
    assert "No gaps reported." in " ".join(lines)


def test_format_prompts_markdown_handles_missing():
    context = ReportContext(
        target_path="/tmp",
        languages=["python"],
        analysis_results=[],
        gap_analysis=GapAnalysis(detector_gaps=[], feature_gaps=[]),
        prompts=None,
    )
    assert _format_prompts_markdown(context) == []


def test_generate_report_without_analysis_or_gaps(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    report = generate_report(
        str(sample), include_analysis=False, include_gaps=False, include_prompts=False
    )
    assert "Gap Analysis" not in report.markdown
    assert report.data["analysis"] == []
    assert report.data["gaps"]["detector_gaps"] == []
