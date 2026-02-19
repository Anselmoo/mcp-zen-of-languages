"""Terminal rendering that presents analysis, prompts, and agent tasks as Rich panels.

While ``report.py`` serialises the pipeline output as Markdown for file or MCP
consumption, this module targets interactive terminals.  It uses the Rich
library to render structured panels, tables, and syntax-highlighted code blocks
that make remediation guidance immediately scannable.

Key rendering functions:

* ``render_prompt_panel`` — Full prompt output with header, roadmap table,
  big-picture health metrics, per-file summary, file prompt panels (with
  syntax-highlighted before/after blocks), and generic prompt table.
* ``build_agent_tasks_table`` — Compact task table showing ID, file:line,
  severity badge, and action text for every generated agent task.

All rendering functions accept an optional ``Console`` override so that tests
can capture output without printing to stdout.  Layout widths are resolved
via ``rendering.layout.get_output_width`` to adapt to narrow terminals.

See Also:
    ``reporting.prompts.build_prompt_bundle``: Produces the ``PromptBundle`` rendered here.
    ``reporting.agent_tasks.build_agent_tasks``: Produces the ``AgentTaskList`` rendered here.
    ``rendering.factories``: Zen-styled Rich component constructors used throughout.
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

from mcp_zen_of_languages.rendering import console, file_glyph, severity_badge
from mcp_zen_of_languages.rendering.factories import (
    zen_header_panel,
    zen_panel,
    zen_summary_table,
    zen_table,
)
from mcp_zen_of_languages.rendering.layout import get_output_width
from mcp_zen_of_languages.rendering.themes import BOX_CODE
from mcp_zen_of_languages.reporting.theme_clustering import classify_violation

if TYPE_CHECKING:
    from rich.table import Table

    from mcp_zen_of_languages.models import AnalysisResult
    from mcp_zen_of_languages.reporting.agent_tasks import AgentTaskList
    from mcp_zen_of_languages.reporting.models import PromptBundle


def _active_console(output_console: Console | None = None) -> Console:
    """Return the console instance to use for all rendering in this call.

    Falls back to the module-level shared console when no override is given,
    ensuring consistent theme and width settings across the rendering session.

    Args:
        output_console: Optional console override for testing or redirection.

    Returns:
        Console: Active console instance for subsequent Rich operations.
    """
    return output_console or console


def _build_prompt_file_summary(
    results: list[AnalysisResult],
    output_console: Console | None = None,
) -> Table:
    """Build a compact file-summary table showing violation counts and top themes.

    Each row displays the file path, total issue count, top two violation themes,
    and a severity badge for the highest-severity violation in that file.

    Args:
        results: Analysis results to summarise, one row per file with violations.
        output_console: Optional console override for width calculation.

    Returns:
        Table: Rich table renderable with File / Issues / Summary columns.
    """
    active_console = _active_console(output_console)
    table = zen_table(title="File Summary", output_console=active_console)
    table.add_column("File", ratio=2, no_wrap=True)
    table.add_column("Issues", justify="right", width=8)
    table.add_column("Summary", ratio=2)
    rows = 0
    for result in results:
        if not result.violations:
            continue
        counts = Counter(classify_violation(v) for v in result.violations)
        top_themes = ", ".join([theme for theme, _ in counts.most_common(2)])
        max_severity = max(v.severity for v in result.violations)
        table.add_row(
            result.path or "<input>",
            str(len(result.violations)),
            f"{top_themes or 'n/a'} · {severity_badge(max_severity)}",
        )
        rows += 1
    if rows == 0:
        table.add_row("-", "0", "No violations")
    return table


def _build_generic_prompts_table(
    bundle: PromptBundle,
    output_console: Console | None = None,
) -> Table | None:
    """Build a table listing generic (language-level) remediation prompts.

    Each row shows the prompt title and the first line of its guidance text,
    giving a quick overview without expanding full descriptions.

    Args:
        bundle: Prompt bundle whose ``generic_prompts`` are rendered.
        output_console: Optional console override for width calculation.

    Returns:
        Table | None: Rich table renderable, or ``None`` when no generic prompts exist.
    """
    if not bundle.generic_prompts:
        return None
    active_console = _active_console(output_console)
    table = zen_table(title="Generic Prompts", output_console=active_console)
    table.add_column("Title", style="metric", ratio=1)
    table.add_column("Focus", ratio=2)
    for prompt in bundle.generic_prompts:
        first_line = prompt.prompt.strip().splitlines()[0]
        table.add_row(prompt.title, first_line)
    return table


def _build_prompt_details_renderable(prompt: str, language: str, width: int) -> Group:  # noqa: C901
    """Parse a Markdown prompt into a Rich ``Group`` with styled prose and code blocks.

    Code fences (``````` … ```````) are extracted and rendered as
    syntax-highlighted ``Syntax`` panels using the detected language, while
    surrounding prose lines are collected into ``Text`` renderables.  Heading
    lines (``###``) are suppressed because the enclosing panel already provides
    a title.

    Args:
        prompt: Raw Markdown prompt text containing interleaved prose and code.
        language: Default language for syntax highlighting when fences omit it.
        width: Available width used to size code panels.

    Returns:
        Group: Composite Rich renderable combining prose text and code panels.
    """
    renderables: list[RenderableType] = []
    prose_lines: list[str] = []
    code_lines: list[str] = []
    in_code = False
    code_language = language or "text"
    code_width = max(24, width - 8)

    def _flush_prose() -> None:
        if prose_lines:
            renderables.append(Text("\n".join(prose_lines), style="default"))
            prose_lines.clear()

    def _flush_code() -> None:
        if code_lines:
            syntax = Syntax(
                "\n".join(code_lines),
                code_language or "text",
                line_numbers=False,
                word_wrap=True,
            )
            renderables.append(
                Panel(
                    syntax,
                    title="Code",
                    box=BOX_CODE,
                    width=code_width,
                    expand=False,
                ),
            )
            code_lines.clear()

    for raw_line in prompt.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("### "):
            continue
        if stripped.startswith("```"):
            if in_code:
                _flush_code()
                in_code = False
            else:
                _flush_prose()
                in_code = True
                code_language = stripped[3:].strip() or language or "text"
            continue
        if in_code:
            code_lines.append(raw_line.removeprefix("  "))
            continue
        prose_lines.append(raw_line)

    if in_code:
        _flush_code()
    _flush_prose()
    if not renderables:
        renderables.append(Text("No prompt details available.", style="dim"))
    return Group(*renderables)


def _render_file_prompt_panels(
    bundle: PromptBundle,
    width: int,
    output_console: Console,
) -> None:
    """Print a zen-styled panel for each file prompt in the bundle.

    Each panel carries a title showing the file path and a subtitle with the
    language and approximate violation count.  The body is a ``Group`` of
    prose and syntax-highlighted code blocks produced by
    ``_build_prompt_details_renderable``.

    Args:
        bundle: Prompt bundle whose ``file_prompts`` are expanded into panels.
        width: Available terminal width for panel sizing.
        output_console: Console used to print the panels.
    """
    for file_prompt in bundle.file_prompts:
        violation_count = file_prompt.prompt.count("\n- [") + int(
            file_prompt.prompt.strip().startswith("- ["),
        )
        details = _build_prompt_details_renderable(
            file_prompt.prompt,
            file_prompt.language,
            width,
        )
        output_console.print(
            zen_panel(
                details,
                title=f"File Prompt - {file_prompt.path}",
                subtitle=f"{file_prompt.language} · {violation_count} violations",
                output_console=output_console,
            ),
        )


def render_prompt_panel(
    bundle: PromptBundle,
    results: list[AnalysisResult],
    output_console: Console | None = None,
) -> None:
    """Render the full prompt output as a series of Rich panels and tables.

    Produces, in order: a zen header panel, a remediation roadmap table, a
    big-picture health/trajectory table, a file summary table, per-file prompt
    panels with syntax-highlighted code, and a generic prompts table.

    Args:
        bundle: Prompt bundle containing all remediation guidance.
        results: Analysis results used to populate the file summary table.
        output_console: Optional console override for testing or redirection.
    """
    active_console = _active_console(output_console)
    width = get_output_width(active_console)
    target_paths = sorted({result.path for result in results if result.path})
    if len(target_paths) == 1:
        target = target_paths[0]
    elif target_paths:
        target = f"{len(target_paths)} files"
    else:
        target = "n/a"
    languages = sorted({result.language for result in results if result.language})
    active_console.print(
        zen_header_panel(
            f"{file_glyph()} Target: {target}",
            f"Languages: {', '.join(languages) if languages else 'n/a'}",
            title="Zen Prompts",
            output_console=active_console,
        ),
    )
    if bundle.big_picture:
        roadmap = bundle.big_picture.refactoring_roadmap or []
        roadmap_table = zen_table(
            title="Remediation Roadmap",
            show_header=False,
            output_console=active_console,
        )
        roadmap_table.add_column("Step", style="metric", width=6, justify="right")
        roadmap_table.add_column("Action", ratio=1)
        if roadmap:
            for index, step in enumerate(roadmap, start=1):
                roadmap_table.add_row(str(index), step)
        else:
            roadmap_table.add_row("-", "No roadmap available.")
        active_console.print(roadmap_table)

        big_picture_table = zen_summary_table(
            title="Big Picture",
            output_console=active_console,
        )
        big_picture_table.add_column("Metric", style="metric", width=18)
        big_picture_table.add_column("Detail", ratio=1)
        big_picture_table.add_row(
            "Health score",
            f"{bundle.big_picture.health_score:.1f}/100",
        )
        big_picture_table.add_row(
            "Trajectory",
            bundle.big_picture.improvement_trajectory,
        )
        if patterns := bundle.big_picture.systemic_patterns or []:
            for pattern in patterns:
                big_picture_table.add_row("Pattern", pattern)
        else:
            big_picture_table.add_row("Pattern", "No systemic patterns detected.")
        active_console.print(big_picture_table)
    active_console.print(_build_prompt_file_summary(results, active_console))
    _render_file_prompt_panels(bundle, width, active_console)
    generic_table = _build_generic_prompts_table(bundle, active_console)
    if generic_table is not None:
        active_console.print(generic_table)


def build_agent_tasks_table(
    task_list: AgentTaskList,
    output_console: Console | None = None,
) -> Table:
    """Build a Rich table listing all agent tasks with ID, file, and action columns.

    Each row shows the task's sequential ID, the ``file:line`` location, a
    severity badge, and the remediation action text.  When the task list is
    empty, a single placeholder row is rendered.

    Args:
        task_list: Agent task list to render.
        output_console: Optional console override for width calculation.

    Returns:
        Table: Rich table renderable with ``#`` / ``File`` / ``Task`` columns.
    """
    active_console = _active_console(output_console)
    table = zen_table(
        title=f"Agent Tasks - {task_list.total_tasks}",
        output_console=active_console,
    )
    table.add_column("#", justify="right", width=4)
    table.add_column("File", ratio=2)
    table.add_column("Task", ratio=2)
    if not task_list.tasks:
        table.add_row("-", "No tasks generated.", "-")
        return table
    for task in task_list.tasks:
        path = f"{task.file}:{task.line}" if task.line else task.file
        table.add_row(
            str(task.task_id),
            path,
            f"{severity_badge(task.severity)} {task.action}",
        )
    return table
