"""FastMCP middleware helpers for server-wide observability."""

from __future__ import annotations

import json
import logging
from time import perf_counter
from typing import cast

from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext

logger = logging.getLogger(__name__)


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
            message = cast("object", context.message)
            logger.info(
                json.dumps(
                    {
                        "event": "mcp.tool.duration",
                        "tool": getattr(message, "name", "unknown"),
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
            logger.exception("Unhandled MCP request error for method=%s", context.method)
            raise


def build_default_middleware() -> list[Middleware]:
    """Return the default middleware chain for the MCP server."""
    return [ErrorHandlingMiddleware(), LoggingMiddleware(), TimingMiddleware()]
