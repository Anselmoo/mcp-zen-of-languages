from __future__ import annotations

from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    Metrics,
    Violation,
)
from mcp_zen_of_languages.reporting.prompts import _format_file_prompt


def test_format_file_prompt_limits():
    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    metrics = Metrics(cyclomatic=cyclomatic, maintainability_index=0.0, lines_of_code=1)
    violations = [Violation(principle="p", severity=4, message="m") for _ in range(9)]
    result = AnalysisResult(
        language="python",
        path="file.py",
        metrics=metrics,
        violations=violations,
        overall_score=80.0,
    )
    prompt = _format_file_prompt(result, violations)
    assert "more" in prompt


def test_format_file_prompt_includes_context():
    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    metrics = Metrics(cyclomatic=cyclomatic, maintainability_index=0.0, lines_of_code=1)
    violations = [Violation(principle="p", severity=4, message="m")]
    result = AnalysisResult(
        language="python",
        path="file.py",
        metrics=metrics,
        violations=violations,
        overall_score=80.0,
    )
    prompt = _format_file_prompt(result, violations)
    assert "### File: file.py" in prompt
    assert "Target: file.py (python)" in prompt
    assert "Violations:" in prompt
