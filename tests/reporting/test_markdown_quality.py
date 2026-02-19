from __future__ import annotations

import re

from mcp_zen_of_languages import cli
from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    Metrics,
    Violation,
)
from mcp_zen_of_languages.reporting.prompts import build_prompt_bundle
from mcp_zen_of_languages.reporting.report import generate_report
from mcp_zen_of_languages.utils.markdown_quality import validate_markdown


def _sample_result() -> AnalysisResult:
    metrics = Metrics(
        cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
        maintainability_index=0.0,
        lines_of_code=12,
    )
    return AnalysisResult(
        language="python",
        path="sample.py",
        metrics=metrics,
        violations=[
            Violation(
                principle="Flat is better than nested",
                severity=7,
                message="Nesting depth > 3 levels",
            ),
        ],
        overall_score=80.0,
    )


def test_report_markdown_quality(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    return 1\n", encoding="utf-8")
    report = generate_report(str(sample), include_prompts=True)
    quality = validate_markdown(report.markdown)
    assert quality.consistent_heading_levels
    assert quality.consistent_bullet_markers
    assert quality.no_trailing_whitespace
    assert quality.tables_aligned


def test_prompt_markdown_quality():
    bundle = build_prompt_bundle([_sample_result()])
    markdown = cli._format_prompt_markdown(bundle)
    quality = validate_markdown(markdown)
    assert quality.consistent_heading_levels
    assert quality.consistent_bullet_markers
    assert quality.code_blocks_have_language
    assert quality.no_trailing_whitespace


def test_prompt_export_matches_analysis():
    result = _sample_result()
    bundle = build_prompt_bundle([result])
    markdown = cli._format_prompt_markdown(bundle)
    for violation in result.violations:
        assert violation.message in markdown
    for match in re.finditer(r"^```(\S*)\s*$", markdown, flags=re.MULTILINE):
        assert match.group(1)
