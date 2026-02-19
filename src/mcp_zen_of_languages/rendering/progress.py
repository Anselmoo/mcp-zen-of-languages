"""Progress indicators for transient CLI feedback during analysis runs.

Provides a context-manager that yields a Rich ``Progress`` bar combining
a spinner, task description, ``M/N`` counter, bar column, and elapsed
timer.  The progress bar renders transiently (erased on completion) and
is suppressed when quiet mode is active, stdout is not a TTY, or the
caller opts out via the *enabled* flag.
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from .console import console, is_quiet

if TYPE_CHECKING:
    from collections.abc import Iterator


@contextmanager
def analysis_progress(*, enabled: bool = True) -> Iterator[Progress | None]:
    """Yield a transient Rich progress bar scoped to an analysis run.

    The progress bar is suppressed (yields ``None``) when any of the
    following conditions hold: *enabled* is False, quiet mode is active,
    stdout is not a TTY, or the console is non-interactive.  When active,
    the bar is rendered with ``transient=True`` so it disappears once
    the context exits, leaving only the final report output.

    Args:
        enabled: Master switch — set to False to unconditionally suppress
            the progress display.

    Yields:
        Progress | None: A running ``Progress`` instance when the terminal
            supports it, or ``None`` when progress display is suppressed.
    """

    if not enabled or is_quiet() or not sys.stdout.isatty() or not console.is_terminal:
        yield None
        return
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        MofNCompleteColumn(),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    )
    with progress:
        yield progress
