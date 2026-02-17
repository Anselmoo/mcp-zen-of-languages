from __future__ import annotations

from io import StringIO

import pytest
from rich.console import Console

from mcp_zen_of_languages.rendering.themes import ZEN_THEME


@pytest.fixture
def capture_console() -> tuple[Console, StringIO]:
    """Provide a deterministic Rich console capture fixture."""

    buffer = StringIO()
    console = Console(
        file=buffer,
        theme=ZEN_THEME,
        width=88,
        force_terminal=True,
        no_color=True,
    )
    return console, buffer
