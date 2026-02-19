from __future__ import annotations

from mcp_zen_of_languages.reporting.models import (
    FilePrompt,
    GapAnalysis,
    GenericPrompt,
    PromptBundle,
    ReportContext,
)
from mcp_zen_of_languages.reporting.report import (
    _format_prompts_markdown,
    generate_report,
)


def test_format_prompts_markdown_with_prompts():
    context = ReportContext(
        target_path="tmp",
        languages=["python"],
        analysis_results=[],
        gap_analysis=GapAnalysis(detector_gaps=[], feature_gaps=[]),
        prompts=PromptBundle(
            file_prompts=[FilePrompt(path="x", language="python", prompt="do it")],
            generic_prompts=[GenericPrompt(title="t", prompt="p")],
        ),
    )
    lines = _format_prompts_markdown(context)
    assert any("Remediation Prompts" in line for line in lines)


def test_generate_report_invalid_path(tmp_path):
    report = generate_report(str(tmp_path / "missing"), include_analysis=False)
    assert report.data["analysis"] == []
