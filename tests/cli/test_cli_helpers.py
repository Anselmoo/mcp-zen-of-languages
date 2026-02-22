from __future__ import annotations

from mcp_zen_of_languages import cli
from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    ExternalAnalysisResult,
    ExternalToolResult,
    Metrics,
)


def test_summarize_violations_counts():
    violations = [
        type("V", (), {"severity": 9}),
        type("V", (), {"severity": 7}),
        type("V", (), {"severity": 4}),
        type("V", (), {"severity": 1}),
    ]
    summary = cli._summarize_violations(violations)
    assert summary.critical == 1
    assert summary.high == 1
    assert summary.medium == 1
    assert summary.low == 1


def test_summarize_violation_dicts_counts():
    summary = cli._summarize_violation_dicts(
        [{"severity": 9}, {"severity": 7}, {"severity": 4}, {"severity": 1}],
    )
    assert summary.critical == 1
    assert summary.high == 1
    assert summary.medium == 1
    assert summary.low == 1


def test_filter_result_returns_same_when_no_filter():
    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    metrics = Metrics(cyclomatic=cyclomatic, maintainability_index=0.0, lines_of_code=0)
    result = AnalysisResult(
        language="python",
        path=None,
        metrics=metrics,
        violations=[],
        overall_score=100.0,
    )
    assert cli._filter_result(result, None) is result


def test_collect_targets_file_uses_override(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("data", encoding="utf-8")
    targets = cli._collect_targets(sample, "python")
    assert targets == [(sample, "python")]


def test_collect_targets_directory_filters_unknown(tmp_path):
    known = tmp_path / "sample.py"
    unknown = tmp_path / "sample.unknown"
    known.write_text("def foo():\n    pass\n", encoding="utf-8")
    unknown.write_text("data", encoding="utf-8")
    targets = cli._collect_targets(tmp_path, None)
    assert any(path == known for path, _ in targets)
    assert all(path != unknown for path, _ in targets)


def test_collect_targets_directory_with_override_filters_language(tmp_path):
    py_file = tmp_path / "sample.py"
    js_file = tmp_path / "sample.js"
    nested = tmp_path / "nested"
    nested.mkdir()
    py_file.write_text("def foo():\n    pass\n", encoding="utf-8")
    js_file.write_text("function foo() {}\n", encoding="utf-8")
    targets = cli._collect_targets(tmp_path, "python")
    assert (py_file, "python") in targets
    assert all(path != js_file for path, _ in targets)


def test_analyze_targets_placeholder(tmp_path):
    sample = tmp_path / "sample.lang"
    sample.write_text("data", encoding="utf-8")
    targets = [(sample, "unknownlang")]
    results = cli._analyze_targets(targets, None)
    assert results
    assert results[0].language == "unknownlang"


def test_build_log_summary_outputs_counts():
    report = type(
        "R",
        (),
        {
            "data": {
                "target": "sample.py",
                "languages": ["python"],
                "summary": {
                    "total_files": 1,
                    "total_violations": 2,
                    "severity_counts": {
                        "critical": 1,
                        "high": 0,
                        "medium": 1,
                        "low": 0,
                    },
                },
            },
        },
    )
    output = cli._build_log_summary(report)
    assert "target: sample.py" in output
    assert "languages: python" in output
    assert "total_files: 1" in output
    assert "total_violations: 2" in output
    assert "critical: 1" in output
    assert "medium: 1" in output


def test_emit_external_tool_guidance_shows_opt_in_tip(capsys):
    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    metrics = Metrics(cyclomatic=cyclomatic, maintainability_index=0.0, lines_of_code=1)
    result = AnalysisResult(
        language="python",
        path="sample.py",
        metrics=metrics,
        violations=[],
        overall_score=100.0,
    )

    cli._emit_external_tool_guidance(
        [result],
        enable_external_tools=False,
        allow_temporary_tools=False,
    )

    output = capsys.readouterr().out
    assert "--enable-external-tools" in output


def test_emit_external_tool_guidance_shows_missing_tool_recommendation(capsys):
    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    metrics = Metrics(cyclomatic=cyclomatic, maintainability_index=0.0, lines_of_code=1)
    result = AnalysisResult(
        language="python",
        path="sample.py",
        metrics=metrics,
        violations=[],
        overall_score=100.0,
        external_analysis=ExternalAnalysisResult(
            enabled=True,
            language="python",
            quality_note="best effort",
            tools=[
                ExternalToolResult(
                    tool="ruff",
                    status="unavailable",
                    message="missing",
                    recommendation="Install 'ruff' to improve analysis.",
                ),
            ],
        ),
    )

    cli._emit_external_tool_guidance(
        [result],
        enable_external_tools=True,
        allow_temporary_tools=False,
    )

    output = capsys.readouterr().out
    assert "Install 'ruff'" in output
