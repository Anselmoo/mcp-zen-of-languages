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
from rich.console import Group as RichGroup
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from mcp_zen_of_languages import __version__

from .layout import get_output_width
from .themes import BORDER_STYLE
from .themes import BOX_BANNER
from .themes import ZEN_THEME
from .themes import pass_fail_glyph


def _supports_color(stream: object) -> bool:
    """Probe whether a file stream can render ANSI colour sequences.

    Checks the ``NO_COLOR`` env-var first (unconditional off), then
    rejects ``TERM=dumb`` and non-TTY streams.  Used once at import
    time to configure both console singletons.

    Args:
        stream (object): Writable IO stream (typically ``sys.stdout`` or ``sys.stderr``).

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
    theme=ZEN_THEME,
    stderr=True,
    no_color=not _supports_color(sys.stderr),
)


class _ConsoleState:
    quiet = False


_STATE = _ConsoleState()

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

    Attempts to render *Zen* in the ``slant`` font at 55 columns.
    Falls back to the hard-coded ``ZEN_BANNER`` constant when pyfiglet
    is unavailable.  Returns only the art block — callers are
    responsible for appending the *"of Languages"* subtitle.

    Returns:
        str: Multi-line ASCII art string.
    """
    try:
        figlet_format = import_module("pyfiglet").figlet_format
        art = figlet_format(
            "Zen",
            font="banner3-d",
            direction="auto",
            justify="center",
            width=55,
        ).rstrip()
    except Exception:  # noqa: BLE001
        art = ZEN_BANNER.strip()
    return art


def get_banner_art() -> str:
    """Return banner art as plain text for embedding in composite renderables.

    Delegates to ``_render_banner_art`` and exposes the result as a
    stable public API.  Callers that build their own ``Panel`` or
    ``Group`` around the banner should use this instead of calling
    ``print_banner``, which writes directly to the console.  The
    returned string does **not** include the *"of Languages"* subtitle;
    callers are responsible for appending it (e.g. via a ``Rule``).

    Returns:
        str: Multi-line ASCII art (no subtitle).
    """
    return _render_banner_art()


def set_quiet(*, value: bool) -> None:
    """Toggle the module-level quiet flag for decorative output.

    When quiet mode is active, ``print_banner`` and the progress
    spinner are suppressed.  Error output via ``print_error`` remains
    unaffected so that fatal messages always reach the user.

    Args:
        value (bool): True to suppress banners and spinners, False to re-enable them.
    """
    _STATE.quiet = value


def is_quiet() -> bool:
    """Check whether decorative output is currently suppressed.

    Returns:
        bool: True when quiet mode has been activated via ``set_quiet``.
    """
    return _STATE.quiet


def print_banner(output_console: Console | None = None) -> None:
    """Render the Zen ASCII-art banner with a Rule subtitle and version.

    Skipped silently when quiet mode is active or stdout is not a TTY.
    Composes a ``RichGroup`` containing the art, a brand-blue ``Rule``
    carrying the *"of Languages"* subtitle, and the version string —
    all wrapped in a ``BOX_BANNER`` (``DOUBLE``) panel sized to the
    88-column contract.

    Args:
        output_console (Console | None, optional): Alternate console to print to; defaults to the
            module-level ``console`` singleton.
    """
    if _STATE.quiet or not sys.stdout.isatty():
        return
    target_console = output_console or console
    width = get_output_width(target_console)
    banner_group = RichGroup(
        Text(_render_banner_art(), style="banner", justify="center"),
        Rule(_ZEN_SUBTITLE, style=BORDER_STYLE),
        Text(f"  v{__version__}", style="muted"),
    )
    target_console.print(
        Panel(
            banner_group,
            expand=False,
            border_style=BORDER_STYLE,
            box=BOX_BANNER,
            width=width,
        ),
    )


def print_error(message: str) -> None:
    """Write a bold-red error line to stderr, prefixed with a fail glyph.

    Always prints regardless of quiet mode so that fatal messages are
    never swallowed.  Rich markup is disabled to avoid interpreting
    user-supplied text as style tags.

    Args:
        message (str): Human-readable error description to display.
    """
    error_console.print(
        f"{pass_fail_glyph(passed=False)} {message}",
        style="bold red",
        markup=False,
    )
