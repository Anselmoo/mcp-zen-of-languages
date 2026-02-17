from __future__ import annotations

from mcp_zen_of_languages.reporting.models import (
    FilePrompt,
    GapAnalysis,
    GenericPrompt,
    PromptBundle,
    ReportContext,
)
from mcp_zen_of_languages.reporting.report import (
    _format_gap_markdown,
    _format_prompts_markdown,
)


def test_format_gap_markdown_no_gaps():
    gaps = GapAnalysis(detector_gaps=[], feature_gaps=[])
    lines = _format_gap_markdown(gaps)
    assert "No gaps reported." in " ".join(lines)


def test_format_prompts_markdown_empty_prompts():
    context = ReportContext(
        target_path="/tmp",
        languages=["python"],
        analysis_results=[],
        gap_analysis=GapAnalysis(detector_gaps=[], feature_gaps=[]),
        prompts=PromptBundle(file_prompts=[], generic_prompts=[]),
    )
    lines = _format_prompts_markdown(context)
    assert any("No file-specific prompts generated." in line for line in lines)
    assert any("No generic prompts available." in line for line in lines)


def test_format_prompts_markdown_with_prompts():
    context = ReportContext(
        target_path="/tmp",
        languages=["python"],
        analysis_results=[],
        gap_analysis=GapAnalysis(detector_gaps=[], feature_gaps=[]),
        prompts=PromptBundle(
            file_prompts=[FilePrompt(path="x", language="python", prompt="fix")],
            generic_prompts=[GenericPrompt(title="t", prompt="p")],
        ),
    )
    lines = _format_prompts_markdown(context)
    assert any("Remediation Prompts" in line for line in lines)
