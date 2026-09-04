from __future__ import annotations

import pytest

from mcp_zen_of_languages.server import mcp


@pytest.mark.asyncio
async def test_server_lifespan_starts_cleanly():
    """Boot the real server lifespan, not just the module import.

    fastmcp 4 validates inside ``_lifespan_manager`` that every ``task=``-enabled
    tool has the tasks extension registered. Importing ``server`` succeeds even
    when that registration is missing, so only an actual lifespan entry proves the
    server can start.

    Two separate fastmcp 4 breakages reached main because nothing in this suite
    started the server: the ``TaskConfig`` import move, and the tasks-extension
    registration. Both left ``docker-image-check`` as the only detector, and that
    job runs after ``test`` and only on PR, main, and tags.
    """
    async with mcp._lifespan_manager():
        pass
