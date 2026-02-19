"""Terminal report compositor that assembles analysis output into Rich panels.

Orchestrates the full report layout: header panel (target / languages),
summary metrics table, per-file violation panels, gap analysis section,
and remediation prompt counts.  All widgets are built through the
factory helpers in ``factories.py`` so they inherit the shared width
cap and visual style.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.text import Text

from mcp_zen_of_languages.models import AnalysisResult

from .console import console
from .factories import zen_header_panel, zen_panel, zen_summary_table, zen_table
from .layout import get_output_width
from .tables import build_violation_table
from .themes import (
    file_glyph,
    score_glyph,
    severity_badge,
)

if TYPE_CHECKING:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    from mcp_zen_of_languages.reporting.models import ReportOutput


def _active_console(output_console: Console | None = None) -> Console:
    """Resolve the console instance for report rendering.

    Returns *output_console* when explicitly provided, otherwise falls
    back to the module-level ``console`` singleton so callers don't need
    to repeat the fallback logic.

    Args:
        output_console: Optional override console; ``None`` means use the
            module-level singleton.

    Returns:
        Console: The resolved Rich console instance.
    """
    return output_console or console


def render_report_terminal(
    report: ReportOutput,
    output_console: Console | None = None,
) -> None:
    """Print a complete analysis report to the terminal as structured Rich panels.

    Sections are rendered in order: header, summary, per-file analysis
    results, gap analysis, and remediation prompts.  Each section is
    skipped when its data key is absent from the report payload.

    Args:
        report: Structured ``ReportOutput`` whose ``.data`` dict contains
            ``target``, ``languages``, ``summary``, ``analysis``, ``gaps``,
            and ``prompts`` keys.
        output_console: Alternate console to write to; defaults to the
            module-level ``console`` singleton.
    """
    active_console = _active_console(output_console)
    width = get_output_width(active_console)
    data = report.data if isinstance(report.data, dict) else {}
    target = data.get("target", "n/a")
    raw_languages = data.get("languages")
    languages = (
        [str(item) for item in raw_languages if isinstance(item, str)]
        if isinstance(raw_languages, list)
        else []
    )
    header_lines = [
        f"{file_glyph()} Target: {target}",
        f"Languages: {', '.join(languages) if languages else 'n/a'}",
    ]
    active_console.print(
        zen_header_panel(
            *header_lines,
            title="Zen Report",
            output_console=active_console,
        ),
    )

    summary = data.get("summary")
    if isinstance(summary, dict):
        active_console.print(_build_summary_table(summary, width))

    analysis_data = data.get("analysis")
    results: list[AnalysisResult] = []
    if isinstance(analysis_data, list):
        results.extend(
            AnalysisResult.model_validate(item)
            for item in analysis_data
            if isinstance(item, dict)
        )
    for result in results:
        _render_result_panel(result, width, active_console)

    gaps = data.get("gaps")
    if isinstance(gaps, dict):
        active_console.print(_build_gap_panel(gaps, width))

    prompts = data.get("prompts")
    if isinstance(prompts, dict):
        active_console.print(_build_prompt_panel(prompts, width))


def _build_summary_table(summary: dict, width: int) -> Table:
    """Compose a summary metrics table from the report's ``summary`` dict.

    Renders total files, total violations, per-severity counts (with
    coloured badges), and an optional quality score.  Uses
    ``zen_summary_table`` for the heavy-bordered, headerless layout.

    Args:
        summary: Dictionary with ``total_files``, ``total_violations``,
            ``severity_counts``, and optional ``score`` keys.
        width: Column width passed through to the table factory.

    Returns:
        Table: Populated summary table ready for ``console.print()``.
    """
    counts = summary.get("severity_counts", {})
    table = zen_summary_table(title="Summary", width=width)
    table.add_column("Metric", style="metric")
    table.add_column("Value")
    table.add_row("Total files", str(summary.get("total_files", 0)))
    table.add_row("Total violations", str(summary.get("total_violations", 0)))
    table.add_row("Critical", f"{severity_badge(9)} {counts.get('critical', 0)}")
    table.add_row("High", f"{severity_badge(7)} {counts.get('high', 0)}")
    table.add_row("Medium", f"{severity_badge(4)} {counts.get('medium', 0)}")
    table.add_row("Low", f"{severity_badge(1)} {counts.get('low', 0)}")
    score = summary.get("score")
    if score is not None:
        table.add_row("Score", f"{score_glyph()} {score}")
    return table


def _render_result_panel(
    result: AnalysisResult,
    _width: int,
    output_console: Console,
) -> None:
    """Print a per-file analysis panel to the console.

    When the file has no violations, a dimmed placeholder message is
    shown.  Otherwise, ``build_violation_table`` produces a
    zebra-striped table of severity badges and detail messages, which
    is wrapped in a ``zen_panel`` titled with the file path.

    Args:
        result: Single-file ``AnalysisResult`` containing ``path`` and
            ``violations``.
        _width: Reserved width parameter kept for call-site compatibility.
            Panel width is derived from ``output_console``.
        output_console: Console instance to print the panel to.
    """
    title = result.path or "<input>"
    if not result.violations:
        output_console.print(
            zen_panel(
                Text("No violations detected.", style="dim"),
                title=title,
                output_console=output_console,
            ),
        )
        return
    table = build_violation_table(result.violations, title)
    output_console.print(zen_panel(table, title=title, output_console=output_console))


def _build_gap_panel(gaps: dict, width: int) -> Panel:
    """Compose a panel listing detector and feature coverage gaps.

    Iterates over ``detector_gaps`` and ``feature_gaps`` entries in the
    *gaps* dict, formatting each as a row in a two-column table
    (area label + detail string).  Shows a "No gaps" placeholder when
    both lists are empty.

    Args:
        gaps: Dictionary with ``detector_gaps`` and ``feature_gaps`` lists,
            each entry being a dict with descriptive keys.
        width: Column width for the enclosing panel.

    Returns:
        Panel: ``zen_panel``-wrapped table of coverage gaps.
    """
    table = zen_table(title="Gap Analysis", width=width)
    table.add_column("Area", style="metric", width=14)
    table.add_column("Detail", ratio=2)
    detector_gaps = gaps.get("detector_gaps", [])
    if isinstance(detector_gaps, list):
        for gap in detector_gaps:
            if not isinstance(gap, dict):
                continue
            detail = (
                f"{gap.get('language')} {gap.get('rule_id')} "
                f"({gap.get('severity')}): {gap.get('principle')} — {gap.get('reason')}"
            )
            table.add_row("Detector", detail)
    feature_gaps = gaps.get("feature_gaps", [])
    if isinstance(feature_gaps, list):
        for gap in feature_gaps:
            if not isinstance(gap, dict):
                continue
            detail = (
                f"{gap.get('area')}: {gap.get('description')} "
                f"(Next: {gap.get('suggested_next_step')})"
            )
            table.add_row("Feature", detail)
    if table.row_count == 0:
        table.add_row("None", "No gaps reported.")
    return zen_panel(table, output_console=None)


def _build_prompt_panel(prompts: dict, width: int) -> Panel:
    """Compose a compact panel summarising remediation prompt counts.

    Displays two rows — file-level prompt count and generic prompt
    count — in a headerless table, giving users a quick sense of
    how much remediation guidance was generated.

    Args:
        prompts: Dictionary with ``file_prompts`` and ``generic_prompts``
            lists whose lengths are counted.
        width: Column width for the enclosing panel.

    Returns:
        Panel: ``zen_panel``-wrapped table of prompt counts.
    """
    file_prompts = prompts.get("file_prompts", [])
    generic_prompts = prompts.get("generic_prompts", [])
    table = zen_table(
        title="Remediation Prompts",
        show_header=False,
        width=width,
    )
    table.add_column("Type", style="metric")
    table.add_column("Count")
    table.add_row(
        "File prompts",
        str(len(file_prompts) if isinstance(file_prompts, list) else 0),
    )
    table.add_row(
        "Generic prompts",
        str(len(generic_prompts) if isinstance(generic_prompts, list) else 0),
    )
    return zen_panel(table, output_console=None)
