from __future__ import annotations

from io import StringIO

from rich.console import Console

from mcp_zen_of_languages.models import AnalysisResult, CyclomaticSummary, Metrics
from mcp_zen_of_languages.rendering.themes import ZEN_THEME
from mcp_zen_of_languages.reporting.agent_tasks import AgentTaskList
from mcp_zen_of_languages.reporting.models import (
    FilePrompt,
    GenericPrompt,
    PromptBundle,
)
from mcp_zen_of_languages.reporting.terminal import (
    _build_generic_prompts_table,
    _build_prompt_file_summary,
    build_agent_tasks_table,
    render_prompt_panel,
)
from mcp_zen_of_languages.reporting.theme_clustering import BigPictureAnalysis


def _empty_result() -> AnalysisResult:
    metrics = Metrics(
        cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
        maintainability_index=0.0,
        lines_of_code=0,
    )
    return AnalysisResult(
        language="python",
        path="sample.py",
        metrics=metrics,
        violations=[],
        overall_score=100.0,
    )


def test_prompt_file_summary_no_violations():
    table = _build_prompt_file_summary([_empty_result()])
    assert table.row_count == 1


def test_generic_prompts_table_none():
    bundle = PromptBundle(file_prompts=[], generic_prompts=[])
    assert _build_generic_prompts_table(bundle) is None


def test_agent_tasks_table_empty():
    task_list = AgentTaskList(
        project=".",
        total_tasks=0,
        tasks=[],
        health_score=100.0,
        clusters=[],
        roadmap=[],
    )
    table = build_agent_tasks_table(task_list)
    assert table.row_count == 1


def test_render_prompt_panel_roundtrip_values():
    buffer = StringIO()
    capture_console = Console(
        file=buffer, width=88, force_terminal=True, no_color=True, theme=ZEN_THEME
    )
    metrics = Metrics(
        cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
        maintainability_index=0.0,
        lines_of_code=10,
    )
    result = AnalysisResult(
        language="python",
        path="sample.py",
        metrics=metrics,
        violations=[],
        overall_score=90.0,
    )
    bundle = PromptBundle(
        file_prompts=[
            FilePrompt(
                path="sample.py",
                language="python",
                prompt=(
                    "### File: sample.py\n"
                    "Context: Improve readability.\n"
                    "Violations:\n"
                    "- [7] Test principle: Nested block\n"
                    "  Before:\n"
                    "  ```python\n"
                    "  if cond:\n"
                    "      pass\n"
                    "  ```\n"
                    "  After:\n"
                    "  ```python\n"
                    "  if not cond:\n"
                    "      return\n"
                    "  ```\n"
                ),
            )
        ],
        generic_prompts=[
            GenericPrompt(title="Quick", prompt="- Fix severity hotspots first.")
        ],
        big_picture=BigPictureAnalysis(
            health_score=67.5,
            improvement_trajectory="Fix complexity first.",
            refactoring_roadmap=["1. Reduce nesting depth."],
            systemic_patterns=["Complexity pressure in parser."],
        ),
    )
    render_prompt_panel(bundle, [result], output_console=capture_console)
    output = buffer.getvalue()
    assert "67.5/100" in output
    assert "sample.py" in output
    assert "python" in output


def test_render_prompt_panel_hides_raw_markdown_headers():
    buffer = StringIO()
    capture_console = Console(
        file=buffer, width=88, force_terminal=True, no_color=True, theme=ZEN_THEME
    )
    bundle = PromptBundle(
        file_prompts=[
            FilePrompt(
                path="x.py",
                language="python",
                prompt="### File: x.py\nContext: Demo prompt\n",
            )
        ],
        generic_prompts=[],
    )
    render_prompt_panel(bundle, [_empty_result()], output_console=capture_console)
    assert "### File:" not in buffer.getvalue()
