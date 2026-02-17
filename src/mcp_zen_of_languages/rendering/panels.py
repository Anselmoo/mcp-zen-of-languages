"""Panel builders for structured analysis sections in the terminal.

Each function in this module composes a Rich ``Table`` inside a Rich
``Panel`` to present a specific domain section — project-level summary
metrics or worst-offending files.  Panels use the shared ``console``
singleton and width cap so they align visually with factory-produced
widgets.
"""

from __future__ import annotations

from collections.abc import Sequence

from rich.panel import Panel
from rich.table import Table

from .console import console
from .layout import get_output_width
from .themes import BOX_CONTENT, BOX_SUMMARY


def build_project_summary_panel(summary: object) -> Panel:
    """Compose a heavy-bordered panel showing aggregate project metrics.

    Extracts severity counts (critical / high / medium / low), total
    files, and total violations from the *summary* object using
    ``getattr`` look-ups, so the function tolerates both Pydantic models
    and plain objects.  The inner table is headerless to keep the
    key-value layout compact.

    Args:
        summary: Result summary object carrying ``severity_counts``,
            ``total_files``, and ``total_violations`` attributes.

    Returns:
        Panel: ``BOX_SUMMARY``-bordered panel containing a two-column
            metric table.
    """

    width = get_output_width(console)
    counts = getattr(summary, "severity_counts", None)
    critical = getattr(counts, "critical", getattr(summary, "critical", 0))
    high = getattr(counts, "high", getattr(summary, "high", 0))
    medium = getattr(counts, "medium", getattr(summary, "medium", 0))
    low = getattr(counts, "low", getattr(summary, "low", 0))
    table = Table(show_header=False, box=None, width=width, pad_edge=False)
    table.add_column("Metric", style="metric")
    table.add_column("Value")
    table.add_row("Total files", str(getattr(summary, "total_files", 0)))
    table.add_row("Total violations", str(getattr(summary, "total_violations", 0)))
    table.add_row("Critical", str(critical))
    table.add_row("High", str(high))
    table.add_row("Medium", str(medium))
    table.add_row("Low", str(low))
    return Panel(
        table,
        title="Project Summary",
        expand=False,
        border_style="cyan",
        box=BOX_SUMMARY,
        width=width,
    )


def build_worst_offenders_panel(offenders: Sequence[object]) -> Panel:
    """Compose a panel listing the files with the highest violation counts.

    Renders a two-column table (path, violation count) inside a
    ``BOX_CONTENT``-bordered panel.  When the *offenders* sequence is
    empty a single "No violations detected" placeholder row is shown.

    Args:
        offenders: Sequence of objects exposing ``path`` and
            ``violations`` (or ``violation_count``) attributes.

    Returns:
        Panel: Rounded-bordered panel containing the worst-offenders table.
    """

    width = get_output_width(console)
    table = Table(
        title="Worst Offenders",
        show_header=True,
        header_style="metric",
        box=None,
        width=width,
        pad_edge=False,
    )
    table.add_column("Path", ratio=2)
    table.add_column("Violations", justify="right", width=12)
    if not offenders:
        table.add_row("No violations detected.", "0")
    else:
        for offender in offenders:
            path = getattr(offender, "path", "<unknown>")
            count = getattr(offender, "violations", None)
            if count is None:
                count = getattr(offender, "violation_count", 0)
            table.add_row(str(path), str(count))
    return Panel(
        table,
        expand=False,
        border_style="cyan",
        box=BOX_CONTENT,
        width=width,
    )
