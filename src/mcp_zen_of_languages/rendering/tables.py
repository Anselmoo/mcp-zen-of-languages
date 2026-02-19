"""Table builders for violation listings in reports and prompt views.

Provides ``build_violation_table``, which converts a flat list of
``Violation`` objects into a zebra-striped Rich ``Table`` with severity
badges, principle names, and location-annotated detail messages.
"""

from __future__ import annotations

from rich.table import Table

from .themes import BOX_CONTENT, severity_badge, severity_style


def build_violation_table(violations: list, path: str) -> Table:
    """Build a zebra-striped Rich table of violations for a single file.

    Each row displays a coloured severity badge (via ``severity_badge``),
    the violated zen principle name, and the detail message.  When the
    violation carries a source location, the ``line:column`` pair is
    appended to the message in parentheses.

    Args:
        violations: ``Violation`` objects to render, each exposing
            ``severity``, ``principle``, ``message``, and optional
            ``location`` attributes.
        path: File path used in the table's title caption.

    Returns:
        Table: ``BOX_CONTENT``-styled table with alternating ``""`` / ``"dim"``
            row styles for visual separation.
    """
    table = Table(
        title=f"Violations - {path}",
        box=BOX_CONTENT,
        row_styles=["", "dim"],
    )
    table.add_column("Sev", width=12, justify="center")
    table.add_column("Principle", min_width=20)
    table.add_column("Details", ratio=2)
    for violation in violations:
        loc = (
            f"{violation.location.line}:{violation.location.column}"
            if violation.location
            else "-"
        )
        details = violation.message if loc == "-" else f"{violation.message} ({loc})"
        table.add_row(
            severity_badge(violation.severity),
            violation.principle,
            details,
            style=severity_style(violation.severity),
        )
    return table
