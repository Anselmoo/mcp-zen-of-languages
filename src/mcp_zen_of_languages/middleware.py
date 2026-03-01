"""FastMCP middleware helpers for server-wide observability and guardrails."""

from __future__ import annotations

import json
import logging
import os

from collections import deque
from hashlib import sha256
from time import monotonic
from time import perf_counter
from typing import TYPE_CHECKING

from fastmcp.server.middleware import CallNext
from fastmcp.server.middleware import Middleware
from fastmcp.server.middleware import MiddlewareContext
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import ValidationError


if TYPE_CHECKING:
    from mcp_zen_of_languages.storage import CacheBackend

logger = logging.getLogger(__name__)


class MiddlewareSettings(BaseModel):
    """Validated environment-backed defaults for middleware guardrails."""

    model_config = ConfigDict(extra="forbid")

    rate_limit_max_calls: int = Field(default=40, ge=1)
    rate_limit_window_seconds: int = Field(default=30, ge=1)
    repeat_limit: int = Field(default=6, ge=1)
    cache_ttl_seconds: int = Field(default=30, ge=1)
    response_max_bytes: int = Field(default=2_000_000, ge=1)

    @classmethod
    def from_env(cls) -> MiddlewareSettings:
        """Load and validate middleware settings from environment variables."""
        raw = {
            "rate_limit_max_calls": os.environ.get("ZEN_RATE_LIMIT_MAX_CALLS", "40"),
            "rate_limit_window_seconds": os.environ.get(
                "ZEN_RATE_LIMIT_WINDOW_SECONDS", "30"
            ),
            "repeat_limit": os.environ.get("ZEN_REPEAT_LIMIT", "6"),
            "cache_ttl_seconds": os.environ.get("ZEN_CACHE_TTL_SECONDS", "30"),
            "response_max_bytes": os.environ.get("ZEN_RESPONSE_MAX_BYTES", "2000000"),
        }
        try:
            return cls.model_validate(raw)
        except ValidationError:
            logger.warning(
                "Invalid middleware env config detected; falling back to defaults.",
                exc_info=True,
            )
            return cls()


def _tool_name(context: MiddlewareContext[object]) -> str:
    """Return MCP tool name from middleware context, if available."""
    params = getattr(context.message, "params", None)
    return str(getattr(params, "name", "unknown"))


def _tool_arguments(context: MiddlewareContext[object]) -> dict[str, object]:
    """Return MCP tool arguments from middleware context."""
    params = getattr(context.message, "params", None)
    arguments = getattr(params, "arguments", None)
    return arguments if isinstance(arguments, dict) else {}


def _session_key(context: MiddlewareContext[object]) -> str:
    """Build a stable session key for rate-limit and duplicate-call controls."""
    fastmcp_context = getattr(context, "fastmcp_context", None)
    if fastmcp_context is None:
        return "unknown-session"
    session_id = getattr(fastmcp_context, "session_id", None)
    return str(session_id) if session_id is not None else "unknown-session"


def _normalized_result(payload: object) -> object:
    """Convert pydantic models to plain dicts for deterministic caching."""
    dump = getattr(payload, "model_dump", None)
    if callable(dump):
        return dump()
    return payload


class LoggingMiddleware(Middleware):
    """Emit structured JSON logs for incoming MCP requests."""

    async def on_request(
        self,
        context: MiddlewareContext[object],
        call_next: CallNext[object, object],
    ) -> object:
        """Log request metadata before handing execution to the next middleware."""
        method = context.method or "unknown"
        logger.info(
            json.dumps(
                {
                    "event": "mcp.request",
                    "method": method,
                    "source": context.source,
                    "type": context.type,
                }
            )
        )
        return await call_next(context)


class TimingMiddleware(Middleware):
    """Track tool call durations for performance monitoring."""

    async def on_call_tool(
        self,
        context: MiddlewareContext[object],
        call_next: CallNext[object, object],
    ) -> object:
        """Measure tool execution duration and log it in milliseconds."""
        started = perf_counter()
        try:
            return await call_next(context)
        finally:
            elapsed_ms = (perf_counter() - started) * 1000
            logger.info(
                json.dumps(
                    {
                        "event": "mcp.tool.duration",
                        "tool": _tool_name(context),
                        "duration_ms": round(elapsed_ms, 2),
                    }
                )
            )


class ErrorHandlingMiddleware(Middleware):
    """Centralize request error logging while preserving current behavior."""

    async def on_request(
        self,
        context: MiddlewareContext[object],
        call_next: CallNext[object, object],
    ) -> object:
        """Capture unhandled request exceptions, log, and re-raise."""
        try:
            return await call_next(context)
        except Exception:
            logger.exception(
                "Unhandled MCP request error for method=%s", context.method
            )
            raise


class RateLimitingMiddleware(Middleware):
    """Apply per-session tool-call rate limits using a sliding window."""

    def __init__(
        self,
        max_calls: int = 40,
        window_seconds: int = 30,
        *,
        max_buckets: int = 4096,
    ) -> None:
        """Initialize rate-limit thresholds for call frequency control."""
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.max_buckets = max_buckets
        self._calls: dict[str, deque[float]] = {}
        self._last_seen: dict[str, float] = {}

    def _prune_stale_buckets(self, now: float) -> None:
        """Drop stale buckets to bound memory in long-lived sessions."""
        for key in list(self._calls):
            bucket = self._calls.get(key)
            if bucket is None:
                continue
            while bucket and now - bucket[0] > self.window_seconds:
                bucket.popleft()
            if not bucket:
                self._calls.pop(key, None)
                self._last_seen.pop(key, None)

    async def on_call_tool(
        self,
        context: MiddlewareContext[object],
        call_next: CallNext[object, object],
    ) -> object:
        """Enforce per-tool call ceilings per session and forward when allowed."""
        now = monotonic()
        self._prune_stale_buckets(now)
        tool = _tool_name(context)
        key = f"{_session_key(context)}:{tool}"
        if key not in self._calls and len(self._calls) >= self.max_buckets:
            oldest_key = min(
                self._last_seen.items(),
                key=lambda item: item[1],
            )[0]
            self._calls.pop(oldest_key, None)
            self._last_seen.pop(oldest_key, None)
        bucket = self._calls.setdefault(key, deque())
        self._last_seen[key] = now
        if len(bucket) >= self.max_calls:
            msg = (
                f"Rate limit exceeded for '{tool}' "
                f"({self.max_calls} calls/{self.window_seconds}s)."
            )
            raise ValueError(msg)
        bucket.append(now)
        return await call_next(context)


class DuplicateCallSuppressionMiddleware(Middleware):
    """Reject identical rapid tool-call loops and force workflow rethinking."""

    def __init__(
        self,
        max_repeats: int = 6,
        window_seconds: int = 30,
        *,
        max_sessions: int = 4096,
    ) -> None:
        """Configure repeat thresholds for identical call suppression."""
        self.max_repeats = max_repeats
        self.window_seconds = window_seconds
        self.max_sessions = max_sessions
        self._state: dict[str, tuple[str, float, int]] = {}

    async def on_call_tool(
        self,
        context: MiddlewareContext[object],
        call_next: CallNext[object, object],
    ) -> object:
        """Abort repeated identical snippet-tool loops beyond configured limits."""
        tool = _tool_name(context)
        if tool not in {"analyze_zen_violations", "generate_prompts"}:
            return await call_next(context)
        arguments = _tool_arguments(context)
        fingerprint_raw = json.dumps(arguments, sort_keys=True, default=str)
        fingerprint = sha256(f"{tool}:{fingerprint_raw}".encode()).hexdigest()
        session = _session_key(context)
        now = monotonic()
        stale_sessions = [
            session_id
            for session_id, (_fingerprint, last_seen, _count) in self._state.items()
            if now - last_seen > self.window_seconds
        ]
        for session_id in stale_sessions:
            self._state.pop(session_id, None)
        if session not in self._state and len(self._state) >= self.max_sessions:
            oldest_session = min(
                self._state,
                key=lambda session_id: self._state[session_id][1],
            )
            self._state.pop(oldest_session, None)
        previous = self._state.get(session)
        if (
            previous is None
            or previous[0] != fingerprint
            or now - previous[1] > self.window_seconds
        ):
            self._state[session] = (fingerprint, now, 1)
            return await call_next(context)
        repeats = previous[2] + 1
        self._state[session] = (fingerprint, now, repeats)
        if repeats > self.max_repeats:
            msg = (
                f"Suppressed repeated '{tool}' call loop after {self.max_repeats} repeats. "
                "Rethink parameters or switch to repository-level analysis."
            )
            raise ValueError(msg)
        return await call_next(context)


class ResponseCachingMiddleware(Middleware):
    """Cache deterministic tool results for a short window to reduce overlap."""

    def __init__(
        self,
        *,
        cache_backend: CacheBackend,
        ttl_seconds: int = 30,
        tools: set[str] | None = None,
    ) -> None:
        """Initialize short-window cache behavior and cacheable tool set."""
        self.cache_backend = cache_backend
        self.ttl_seconds = ttl_seconds
        self.tools = tools or {
            "analyze_zen_violations",
            "generate_prompts",
            "detect_languages",
            "get_supported_languages",
        }

    async def on_call_tool(
        self,
        context: MiddlewareContext[object],
        call_next: CallNext[object, object],
    ) -> object:
        """Serve cached deterministic responses when available."""
        tool = _tool_name(context)
        if tool not in self.tools:
            return await call_next(context)
        arguments = _tool_arguments(context)
        cache_key = self._cache_key(tool, arguments)
        cached = self.cache_backend.get(cache_key)
        if cached is not None:
            logger.info(
                json.dumps({"event": "mcp.cache.hit", "tool": tool, "key": cache_key})
            )
            return cached
        result = await call_next(context)
        normalized = _normalized_result(result)
        self.cache_backend.set(cache_key, normalized, ttl_seconds=self.ttl_seconds)
        logger.info(
            json.dumps({"event": "mcp.cache.set", "tool": tool, "key": cache_key})
        )
        return normalized

    @staticmethod
    def _cache_key(tool: str, arguments: dict[str, object]) -> str:
        payload = json.dumps(arguments, sort_keys=True, default=str)
        fingerprint = sha256(payload.encode("utf-8")).hexdigest()
        return f"{tool}:{fingerprint}"


class ResponseLimitingMiddleware(Middleware):
    """Reject oversized responses to keep editor clients responsive."""

    def __init__(self, max_response_bytes: int = 2_000_000) -> None:
        """Configure maximum response payload size in bytes."""
        self.max_response_bytes = max_response_bytes

    async def on_call_tool(
        self,
        context: MiddlewareContext[object],
        call_next: CallNext[object, object],
    ) -> object:
        """Validate serialized response size before returning to client."""
        result = await call_next(context)
        serialized = json.dumps(_normalized_result(result), default=str).encode("utf-8")
        if len(serialized) > self.max_response_bytes:
            tool = _tool_name(context)
            msg = (
                f"Response from '{tool}' exceeded {self.max_response_bytes} bytes. "
                "Reduce scope (languages/max_files) and retry."
            )
            raise ValueError(msg)
        return result


def build_default_middleware(*, cache_backend: CacheBackend) -> list[Middleware]:
    """Return the default middleware chain for the MCP server."""
    settings = MiddlewareSettings.from_env()
    return [
        ErrorHandlingMiddleware(),
        LoggingMiddleware(),
        RateLimitingMiddleware(
            max_calls=settings.rate_limit_max_calls,
            window_seconds=settings.rate_limit_window_seconds,
        ),
        DuplicateCallSuppressionMiddleware(
            max_repeats=settings.repeat_limit,
            window_seconds=settings.rate_limit_window_seconds,
        ),
        ResponseCachingMiddleware(
            cache_backend=cache_backend,
            ttl_seconds=settings.cache_ttl_seconds,
        ),
        TimingMiddleware(),
        ResponseLimitingMiddleware(max_response_bytes=settings.response_max_bytes),
    ]
