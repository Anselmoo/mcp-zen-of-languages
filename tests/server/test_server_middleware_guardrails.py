from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from mcp_zen_of_languages.middleware import (
    DuplicateCallSuppressionMiddleware,
    MiddlewareSettings,
    RateLimitingMiddleware,
    ResponseCachingMiddleware,
    ResponseLimitingMiddleware,
    build_default_middleware,
)
from mcp_zen_of_languages.storage import InMemoryCacheBackend

DEFAULT_RATE_LIMIT_MAX_CALLS = 40


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
async def test_response_cache_returns_normalized_payload_consistently():
    class _Payload(BaseModel):
        value: int

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
        return _Payload(value=state["calls"])

    first = await middleware.on_call_tool(context, call_next)
    second = await middleware.on_call_tool(context, call_next)
    assert first == {"value": 1}
    assert second == {"value": 1}
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
async def test_duplicate_call_suppression_evicts_stale_sessions():
    middleware = DuplicateCallSuppressionMiddleware(max_repeats=2, window_seconds=1)
    old_context = _tool_context(
        name="analyze_zen_violations",
        arguments={"code": "", "language": "python"},
        session_id="old-session",
    )
    fresh_context = _tool_context(
        name="analyze_zen_violations",
        arguments={"code": "", "language": "python"},
        session_id="fresh-session",
    )

    async def call_next(_context: object) -> object:
        return {"ok": True}

    await middleware.on_call_tool(old_context, call_next)
    middleware._state["old-session"] = (middleware._state["old-session"][0], 0.0, 1)
    await middleware.on_call_tool(fresh_context, call_next)
    assert "old-session" not in middleware._state
    assert "fresh-session" in middleware._state


@pytest.mark.asyncio
async def test_rate_limiter_evicts_oldest_bucket_when_capacity_exceeded():
    middleware = RateLimitingMiddleware(max_calls=2, window_seconds=30, max_buckets=1)

    async def call_next(_context: object) -> object:
        return {"ok": True}

    await middleware.on_call_tool(
        _tool_context(name="detect_languages", arguments={}, session_id="s1"),
        call_next,
    )
    await middleware.on_call_tool(
        _tool_context(name="detect_languages", arguments={}, session_id="s2"),
        call_next,
    )
    assert len(middleware._calls) == 1
    assert any(key.startswith("s2:") for key in middleware._calls)


def test_middleware_settings_invalid_env_falls_back_to_defaults(monkeypatch):
    monkeypatch.setenv("ZEN_RATE_LIMIT_MAX_CALLS", "invalid")
    settings = MiddlewareSettings.from_env()
    assert settings.rate_limit_max_calls == DEFAULT_RATE_LIMIT_MAX_CALLS


def test_build_default_middleware_uses_validated_defaults(monkeypatch):
    monkeypatch.setenv("ZEN_RATE_LIMIT_MAX_CALLS", "invalid")
    middleware_chain = build_default_middleware(cache_backend=InMemoryCacheBackend())
    rate_limiter = next(
        middleware
        for middleware in middleware_chain
        if isinstance(middleware, RateLimitingMiddleware)
    )
    assert rate_limiter.max_calls == DEFAULT_RATE_LIMIT_MAX_CALLS


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
