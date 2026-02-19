"""Layout constants and width helpers for consistent terminal rendering.

Defines ``MAX_OUTPUT_WIDTH`` (88 columns) as the single source of truth
for the maximum renderable width.  All factory functions and panel
builders route through ``get_output_width`` to enforce this cap,
preventing wide terminals from stretching tables and panels beyond
comfortable reading width.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.console import Console

MAX_OUTPUT_WIDTH = 88


def get_output_width(console: Console) -> int:
    """Return the effective output width, capped at ``MAX_OUTPUT_WIDTH``.

    Takes the lesser of the console's detected terminal width and the
    88-column cap so that renderables remain readable on ultra-wide
    displays while still adapting to narrower windows.

    Args:
        console: Rich console instance whose ``.width`` is inspected.

    Returns:
        int: Resolved column width that all renderables should use.
    """
    return min(console.width, MAX_OUTPUT_WIDTH)
