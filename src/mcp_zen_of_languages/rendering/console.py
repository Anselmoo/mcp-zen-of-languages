"""Console singleton and output primitives for the rendering pipeline.

This module bootstraps two ``rich.console.Console`` instances — one for
``stdout`` and one for ``stderr`` — both bound to the shared ``ZEN_THEME``
colour palette.  Colour support is probed at import time through
``NO_COLOR`` / ``TERM`` environment variables and ``isatty()`` detection,
so every downstream consumer inherits a coherent colour decision without
re-checking the environment.

A module-level ``_QUIET`` flag lets the CLI suppress decorative output
(banners, spinners) while still allowing programmatic error printing.
"""

from __future__ import annotations

import os
import sys
from importlib import import_module

from rich.console import Console
from rich.panel import Panel

from mcp_zen_of_languages import __version__

from .layout import get_output_width
from .themes import BOX_BANNER, ZEN_THEME, pass_fail_glyph


def _supports_color(stream) -> bool:
    """Probe whether a file stream can render ANSI colour sequences.

    Checks the ``NO_COLOR`` env-var first (unconditional off), then
    rejects ``TERM=dumb`` and non-TTY streams.  Used once at import
    time to configure both console singletons.

    Args:
        stream: Writable IO stream (typically ``sys.stdout`` or ``sys.stderr``).

    Returns:
        bool: True when the stream is a colour-capable TTY.
    """
    if os.getenv("NO_COLOR"):
        return False
    term = os.getenv("TERM", "").lower()
    if term in {"", "dumb"}:
        return False
    return bool(getattr(stream, "isatty", lambda: False)())


console = Console(theme=ZEN_THEME, no_color=not _supports_color(sys.stdout))
error_console = Console(
    theme=ZEN_THEME, stderr=True, no_color=not _supports_color(sys.stderr)
)
_QUIET = False

ZEN_BANNER = r"""
 _____
/__  /  ___  ____
  / /  / _ \/ __ \
 / /__/  __/ / / /
/____/\___/_/ /_/
"""

_ZEN_SUBTITLE = "of Languages"


def _render_banner_art() -> str:
    """Compose the ASCII-art banner, optionally enhanced by pyfiglet.

    Attempts to import ``pyfiglet`` and render the word *Zen* in the
    ``banner3-d`` font at a 55-column width.  Falls back to the
    hard-coded ``ZEN_BANNER`` constant when pyfiglet is unavailable.
    The subtitle *"of Languages"* is right-aligned beneath the art
    block so the two elements form a cohesive visual unit inside the
    88-column panel produced by ``print_banner``.

    Returns:
        str: Multi-line ASCII art string with appended subtitle.
    """

    try:
        figlet_format = getattr(import_module("pyfiglet"), "figlet_format")
        art = figlet_format(
            "Zen", font="banner3-d", direction="auto", justify="center", width=55
        ).rstrip()
    except Exception:
        art = ZEN_BANNER.strip()

    # Right-align the subtitle to the width of the art block
    art_width = max((len(line) for line in art.splitlines()), default=0)
    subtitle = _ZEN_SUBTITLE.rjust(art_width)
    return f"{art}\n{subtitle}"


def get_banner_art() -> str:
    """Return banner art as plain text for embedding in composite renderables.

    Delegates to ``_render_banner_art`` and exposes the result as a
    stable public API.  Callers that build their own ``Panel`` or
    ``Group`` around the banner should use this instead of calling
    ``print_banner``, which writes directly to the console.

    Returns:
        str: Multi-line ASCII art including the *"of Languages"* subtitle.
    """

    return _render_banner_art()


def set_quiet(value: bool) -> None:
    """Toggle the module-level quiet flag for decorative output.

    When quiet mode is active, ``print_banner`` and the progress
    spinner are suppressed.  Error output via ``print_error`` remains
    unaffected so that fatal messages always reach the user.

    Args:
        value: True to suppress banners and spinners, False to re-enable them.
    """

    global _QUIET
    _QUIET = value


def is_quiet() -> bool:
    """Check whether decorative output is currently suppressed.

    Returns:
        bool: True when quiet mode has been activated via ``set_quiet``.
    """

    return _QUIET


def print_banner(output_console: Console | None = None) -> None:
    """Render the Zen ASCII-art banner inside a double-bordered panel.

    Skipped silently when quiet mode is active or stdout is not a TTY.
    The panel is sized via ``get_output_width`` (capped at 88 columns)
    and styled with the ``BOX_BANNER`` (``DOUBLE``) box and a cyan
    border, producing the distinctive header shown at CLI startup.

    Args:
        output_console: Alternate console to print to; defaults to the
            module-level ``console`` singleton.
    """

    if _QUIET or not sys.stdout.isatty():
        return
    target_console = output_console or console
    banner = f"[bold cyan]{_render_banner_art()}[/]\n[dim]v{__version__}[/]"
    width = get_output_width(target_console)
    target_console.print(
        Panel(
            banner,
            style="banner",
            expand=False,
            border_style="cyan",
            box=BOX_BANNER,
            width=width,
        )
    )


def print_error(message: str) -> None:
    """Write a bold-red error line to stderr, prefixed with a fail glyph.

    Always prints regardless of quiet mode so that fatal messages are
    never swallowed.  Rich markup is disabled to avoid interpreting
    user-supplied text as style tags.

    Args:
        message: Human-readable error description to display.
    """

    error_console.print(
        f"{pass_fail_glyph(False)} {message}", style="bold red", markup=False
    )
