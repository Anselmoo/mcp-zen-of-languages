from __future__ import annotations

import pytest

from mcp_zen_of_languages import server
from mcp_zen_of_languages.middleware import DuplicateCallSuppressionMiddleware
from mcp_zen_of_languages.middleware import ErrorHandlingMiddleware
from mcp_zen_of_languages.middleware import LoggingMiddleware
from mcp_zen_of_languages.middleware import RateLimitingMiddleware
from mcp_zen_of_languages.middleware import ResponseCachingMiddleware
from mcp_zen_of_languages.middleware import ResponseLimitingMiddleware
from mcp_zen_of_languages.middleware import TimingMiddleware


LIST_PAGE_SIZE = 100
ICON_URL_PREFIX = "https://anselmoo.github.io/mcp-zen-of-languages/assets/icons/"


def _icon_srcs(items: list[object]) -> list[str]:
    srcs: list[str] = []
    for item in items:
        srcs.extend(icon.src for icon in getattr(item, "icons", []) or [])
    return srcs


def test_server_uses_pagination_and_middleware():
    # FastMCP 3.0.x stores this constructor setting only on the private field.
    assert server.mcp._list_page_size == LIST_PAGE_SIZE
    assert any(isinstance(m, ErrorHandlingMiddleware) for m in server.mcp.middleware)
    assert any(isinstance(m, LoggingMiddleware) for m in server.mcp.middleware)
    assert any(isinstance(m, RateLimitingMiddleware) for m in server.mcp.middleware)
    assert any(
        isinstance(m, DuplicateCallSuppressionMiddleware) for m in server.mcp.middleware
    )
    assert any(isinstance(m, ResponseCachingMiddleware) for m in server.mcp.middleware)
    assert any(isinstance(m, TimingMiddleware) for m in server.mcp.middleware)
    assert any(isinstance(m, ResponseLimitingMiddleware) for m in server.mcp.middleware)


@pytest.mark.asyncio
async def test_versioned_tool_metadata_is_exposed():
    tools = await server.mcp.list_tools()
    versions_by_name: dict[str, set[str]] = {}
    for tool in tools:
        versions_by_name.setdefault(tool.name, set()).add(str(tool.version))
    assert versions_by_name["analyze_zen_violations"] == {"1.0", "2.0"}
    assert versions_by_name["generate_prompts"] == {"1.0", "2.0"}


@pytest.mark.asyncio
async def test_analyze_v2_rejects_empty_code():
    with pytest.raises(ValueError, match="Empty code"):
        await server.analyze_zen_violations_v2.fn("", "python")


@pytest.mark.asyncio
async def test_tool_icon_metadata_uses_canonical_github_pages_urls():
    icon_srcs = _icon_srcs(await server.mcp.list_tools())
    assert icon_srcs
    assert all(
        src.startswith(ICON_URL_PREFIX) and src.endswith(".svg") for src in icon_srcs
    )


@pytest.mark.asyncio
async def test_resource_icon_metadata_uses_canonical_github_pages_urls():
    icon_srcs = _icon_srcs(await server.mcp.list_resources())
    assert icon_srcs
    assert all(
        src.startswith(ICON_URL_PREFIX) and src.endswith(".svg") for src in icon_srcs
    )


@pytest.mark.asyncio
async def test_prompt_icon_metadata_uses_canonical_github_pages_urls():
    icon_srcs = _icon_srcs(await server.mcp.list_prompts())
    assert icon_srcs
    assert all(
        src.startswith(ICON_URL_PREFIX) and src.endswith(".svg") for src in icon_srcs
    )
