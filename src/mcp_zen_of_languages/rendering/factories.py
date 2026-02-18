"""Widget factories that enforce the Zen CLI visual contract.

Every ``Panel`` and ``Table`` produced by this module shares the same
width cap (88 columns via ``get_output_width``), box style, border colour,
and padding.  CLI commands should always build renderables through these
factories rather than constructing ``Panel`` or ``Table`` directly, so that
welcome screens, help text, reports, prompts, and rule listings stay
visually consistent across the entire tool surface.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.panel import Panel
from rich.table import Table

from .console import console as _default_console
from .layout import get_output_width
from .themes import BOX_CONTENT, BOX_SUMMARY

if TYPE_CHECKING:
    from rich.console import RenderableType
    from collections.abc import Sequence
    from rich import box as _box_module
    from rich.console import Console

# ── Panels ──────────────────────────────────────────────────────────


def zen_panel(
    content: RenderableType,
    *,
    title: str | None = None,
    subtitle: str | None = None,
    box: _box_module.Box = BOX_CONTENT,
    border_style: str = "cyan",
    output_console: Console | None = None,
    width: int | None = None,
    expand: bool = False,
    padding: tuple[int, int] = (0, 1),
) -> Panel:
    """Build a ``Panel`` that honours the 88-column width contract.

    Resolves the output width from the active console (falling back to
    the module-level singleton) and applies the standard ``BOX_CONTENT``
    (``ROUNDED``) box with a cyan border.  Callers may override any
    visual parameter, but the width cap is always enforced.

    Args:
        content: Any Rich renderable — ``Text``, ``Group``, ``Table``, etc.
        title: Optional heading rendered in the top border.
        subtitle: Optional text rendered in the bottom border.
        box: Box drawing style; defaults to ``BOX_CONTENT`` (``ROUNDED``).
        border_style: Rich colour token for the panel border.
        output_console: Console used to derive the width cap; falls back
            to the module-level ``console`` singleton.
        width: Explicit width override.  When ``None``, computed via
            ``get_output_width()``.
        expand: When True the panel stretches to fill available width;
            defaults to ``False`` to honour *width* exactly.
        padding: Inner ``(vertical, horizontal)`` padding in character cells.

    Returns:
        Panel: Styled Rich panel ready for ``console.print()``.
    """

    active = output_console or _default_console
    resolved_width = width or get_output_width(active)
    return Panel(
        content,
        title=title,
        subtitle=subtitle,
        box=box,
        border_style=border_style,
        width=resolved_width,
        expand=expand,
        padding=padding,
    )


def zen_header_panel(
    *lines: str,
    title: str,
    output_console: Console | None = None,
) -> Panel:
    """Build the standard command-header panel displayed at the top of reports.

    Joins the positional *lines* with newlines and wraps them in a
    ``zen_panel``.  Typically used for the "Target / Languages" header
    shown above analysis output.

    Args:
        *lines: Content lines rendered inside the panel body.
        title: Heading text rendered in the panel's top border.
        output_console: Console used to derive the width cap.

    Returns:
        Panel: Header panel styled with the default ``BOX_CONTENT`` box.
    """

    return zen_panel(
        "\n".join(lines),
        title=title,
        output_console=output_console,
    )


# ── Tables ──────────────────────────────────────────────────────────


def zen_table(
    *,
    title: str | None = None,
    box: _box_module.Box = BOX_CONTENT,
    show_header: bool = True,
    show_lines: bool = False,
    output_console: Console | None = None,
    width: int | None = None,
    header_style: str | None = "metric",
    row_styles: Sequence[str] | None = None,
) -> Table:
    """Build a ``Table`` that honours the 88-column width contract.

    Horizontal rules between rows are disabled by default to avoid the
    "white stripes" artefact common in dense violation listings.  Use
    *row_styles* (e.g. ``("", "dim")``) for zebra-striped visual
    separation instead.

    Args:
        title: Optional table caption rendered above the header row.
        box: Box drawing style; defaults to ``BOX_CONTENT`` (``ROUNDED``).
        show_header: Whether to render the column header row.
        show_lines: Whether to draw horizontal rules between data rows.
        output_console: Console used to derive the width cap.
        width: Explicit width override; computed via ``get_output_width``
            when ``None``.
        header_style: Rich style token applied to the header row;
            defaults to ``"metric"`` (magenta).
        row_styles: Alternating row styles for zebra-striped readability.

    Returns:
        Table: Width-capped Rich table ready for column and row additions.
    """

    active = output_console or _default_console
    resolved_width = width or get_output_width(active)
    kwargs: dict[str, object] = {
        "title": title,
        "box": box,
        "show_header": show_header,
        "show_lines": show_lines,
        "width": resolved_width,
    }
    if header_style is not None:
        kwargs["header_style"] = header_style
    if row_styles is not None:
        kwargs["row_styles"] = list(row_styles)
    return Table(**kwargs)


def zen_summary_table(
    *,
    title: str | None = None,
    output_console: Console | None = None,
    width: int | None = None,
) -> Table:
    """Build a headerless summary table using the ``BOX_SUMMARY`` (``HEAVY``) box.

    Designed for key-value metric displays (e.g. total violations,
    severity counts) where column headers add noise.  Delegates to
    ``zen_table`` with ``show_header=False`` and a ``None`` header style.

    Args:
        title: Optional caption rendered above the table body.
        output_console: Console used to derive the width cap.
        width: Explicit width override.

    Returns:
        Table: Heavy-bordered Rich table without a header row.
    """

    return zen_table(
        title=title,
        box=BOX_SUMMARY,
        show_header=False,
        output_console=output_console,
        width=width,
        header_style=None,
    )
