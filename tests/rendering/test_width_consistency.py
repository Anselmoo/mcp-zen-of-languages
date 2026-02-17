from __future__ import annotations

import re
from io import StringIO

import pytest
from rich.console import Console

from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    Metrics,
    Violation,
)
from mcp_zen_of_languages.rendering.report import render_report_terminal
from mcp_zen_of_languages.rendering.themes import ZEN_THEME
from mcp_zen_of_languages.reporting.models import (
    GenericPrompt,
    PromptBundle,
    ReportOutput,
)
from mcp_zen_of_languages.reporting.terminal import render_prompt_panel
from mcp_zen_of_languages.reporting.theme_clustering import BigPictureAnalysis


def _sample_result() -> AnalysisResult:
    metrics = Metrics(
        cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
        maintainability_index=0.0,
        lines_of_code=10,
    )
    return AnalysisResult(
        language="python",
        path="sample.py",
        metrics=metrics,
        violations=[Violation(principle="P", severity=7, message="Nesting depth > 3")],
        overall_score=80.0,
    )


def _assert_max_width(output: str, expected: int) -> None:
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")
    for line in output.splitlines():
        assert len(ansi_re.sub("", line)) <= expected


@pytest.mark.parametrize("terminal_width", [40, 60, 80, 120, 200])
def test_prompt_panel_respects_capped_width(terminal_width: int):
    buffer = StringIO()
    capture_console = Console(
        file=buffer,
        theme=ZEN_THEME,
        width=terminal_width,
        force_terminal=True,
        no_color=True,
    )
    bundle = PromptBundle(
        file_prompts=[],
        generic_prompts=[
            GenericPrompt(title="Quick", prompt="Focus on severity first.")
        ],
        big_picture=BigPictureAnalysis(
            health_score=67.5,
            improvement_trajectory="Fix complexity first.",
            refactoring_roadmap=["1. Reduce complexity"],
            systemic_patterns=["Complexity pressure in parser"],
        ),
    )

    render_prompt_panel(bundle, [_sample_result()], output_console=capture_console)
    _assert_max_width(buffer.getvalue(), min(terminal_width, 88))


@pytest.mark.parametrize("terminal_width", [40, 60, 88, 120, 200])
def test_report_terminal_respects_capped_width(terminal_width: int):
    buffer = StringIO()
    capture_console = Console(
        file=buffer,
        theme=ZEN_THEME,
        width=terminal_width,
        force_terminal=True,
        no_color=True,
    )
    report = ReportOutput(
        markdown="md",
        data={
            "target": "repo",
            "languages": ["python"],
            "summary": {
                "total_files": 1,
                "total_violations": 1,
                "severity_counts": {"critical": 0, "high": 1, "medium": 0, "low": 0},
            },
            "analysis": [_sample_result().model_dump()],
            "gaps": {"detector_gaps": [], "feature_gaps": []},
            "prompts": {"file_prompts": [], "generic_prompts": []},
        },
    )

    render_report_terminal(report, output_console=capture_console)
    _assert_max_width(buffer.getvalue(), min(terminal_width, 88))
