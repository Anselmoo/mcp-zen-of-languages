from __future__ import annotations

from types import SimpleNamespace

import pytest

from mcp_zen_of_languages.middleware import (
    DuplicateCallSuppressionMiddleware,
    ResponseCachingMiddleware,
    ResponseLimitingMiddleware,
)
from mcp_zen_of_languages.storage import InMemoryCacheBackend


def _tool_context(
    *,
    name: str,
    arguments: dict[str, object],
    session_id: str = "session-1",
) -> object:
    params = SimpleNamespace(name=name, arguments=arguments)
    message = SimpleNamespace(params=params)
    return SimpleNamespace(
        message=message,
        method="tools/call",
        source="client",
        type="request",
        fastmcp_context=SimpleNamespace(session_id=session_id),
    )


@pytest.mark.asyncio
async def test_response_cache_short_circuits_duplicate_requests():
    middleware = ResponseCachingMiddleware(
        cache_backend=InMemoryCacheBackend(),
        ttl_seconds=60,
        tools={"analyze_zen_violations"},
    )
    context = _tool_context(
        name="analyze_zen_violations",
        arguments={"code": "print('hi')", "language": "python"},
    )
    state = {"calls": 0}

    async def call_next(_context: object) -> object:
        state["calls"] += 1
        return {"calls": state["calls"]}

    first = await middleware.on_call_tool(context, call_next)
    second = await middleware.on_call_tool(context, call_next)
    assert first == {"calls": 1}
    assert second == {"calls": 1}
    assert state["calls"] == 1


@pytest.mark.asyncio
async def test_duplicate_call_suppression_rejects_repeated_loops():
    middleware = DuplicateCallSuppressionMiddleware(max_repeats=2, window_seconds=30)
    context = _tool_context(
        name="analyze_zen_violations",
        arguments={"code": "", "language": "python"},
    )

    async def call_next(_context: object) -> object:
        return {"ok": True}

    await middleware.on_call_tool(context, call_next)
    await middleware.on_call_tool(context, call_next)
    with pytest.raises(ValueError, match="Suppressed repeated"):
        await middleware.on_call_tool(context, call_next)


@pytest.mark.asyncio
async def test_response_limit_rejects_oversized_payloads():
    middleware = ResponseLimitingMiddleware(max_response_bytes=64)
    context = _tool_context(
        name="analyze_repository",
        arguments={"repo_path": "repo"},
    )

    async def call_next(_context: object) -> object:
        return {"payload": "x" * 512}

    with pytest.raises(ValueError, match="exceeded"):
        await middleware.on_call_tool(context, call_next)
