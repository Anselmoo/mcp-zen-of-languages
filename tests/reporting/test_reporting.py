from __future__ import annotations

from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    Metrics,
    Violation,
)
from mcp_zen_of_languages.reporting.gaps import build_gap_analysis
from mcp_zen_of_languages.reporting.prompts import (
    GENERIC_PROMPTS_BY_LANGUAGE,
    build_prompt_bundle,
)
from mcp_zen_of_languages.reporting.report import generate_report
from mcp_zen_of_languages.rules import get_all_languages


def _build_result(path: str, language: str, severity: int) -> AnalysisResult:
    violation = Violation(
        principle="Test",
        severity=severity,
        message="Example violation",
    )
    metrics = Metrics(
        cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
        maintainability_index=0.0,
        lines_of_code=1,
    )
    return AnalysisResult(
        language=language,
        path=path,
        metrics=metrics,
        violations=[violation],
        overall_score=90.0,
    )


def test_build_prompt_bundle_includes_file_and_generic():
    results = [
        _build_result("sample.py", "python", 7),
        _build_result("sample.ts", "typescript", 5),
    ]
    prompts = build_prompt_bundle(results)
    assert prompts.file_prompts
    assert prompts.generic_prompts
    assert any(p.language == "python" for p in prompts.file_prompts)


def test_build_prompt_bundle_includes_bash_generic():
    results = [_build_result("sample.sh", "bash", 4)]
    prompts = build_prompt_bundle(results)
    assert any(p.title == "Harden shell safety" for p in prompts.generic_prompts)


def test_generic_prompts_cover_all_languages():
    languages = set(get_all_languages())
    assert languages.issubset(set(GENERIC_PROMPTS_BY_LANGUAGE))
    for language in languages:
        prompts = GENERIC_PROMPTS_BY_LANGUAGE.get(language)
        assert prompts, f"No generic prompts defined for language: {language}"
        for title, prompt in prompts:
            assert title.strip()
            assert prompt.strip()


def test_gap_analysis_no_missing_detectors():
    gaps = build_gap_analysis(["bash"])
    assert gaps.detector_gaps == []


def test_generate_report_includes_sections(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    report = generate_report(str(sample), include_prompts=True)
    assert report.markdown.startswith("# Zen of Languages Report")
    assert "Gap Analysis" in report.markdown
    assert report.data["prompts"]
