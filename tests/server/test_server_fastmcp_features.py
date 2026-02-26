from __future__ import annotations

import pytest

from mcp_zen_of_languages import server
from mcp_zen_of_languages.middleware import (
    ErrorHandlingMiddleware,
    LoggingMiddleware,
    TimingMiddleware,
)

LIST_PAGE_SIZE = 100


def test_server_uses_pagination_and_middleware():
    assert server.mcp._list_page_size == LIST_PAGE_SIZE
    assert any(isinstance(m, ErrorHandlingMiddleware) for m in server.mcp.middleware)
    assert any(isinstance(m, LoggingMiddleware) for m in server.mcp.middleware)
    assert any(isinstance(m, TimingMiddleware) for m in server.mcp.middleware)


@pytest.mark.asyncio
async def test_versioned_tool_metadata_is_exposed():
    tools = await server.mcp.list_tools()
    versions = {tool.name: tool.version for tool in tools}
    assert versions["analyze_zen_violations"] == "1.0"
    assert versions["generate_prompts"] == "1.0"
