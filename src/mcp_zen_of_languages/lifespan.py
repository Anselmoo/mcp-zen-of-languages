"""FastMCP lifespan hooks for startup precomputation and shutdown cleanup."""

from __future__ import annotations

from fastmcp.server.lifespan import lifespan


@lifespan
async def zen_server_lifespan(server: object) -> object:
    """Precompute language metadata on startup and cleanup cache on shutdown."""
    from mcp_zen_of_languages.analyzers import registry_bootstrap as _registry_bootstrap
    from mcp_zen_of_languages.rules import get_all_languages

    _ = _registry_bootstrap
    yield {"supported_language_count": len(get_all_languages())}
    cache_backend = getattr(server, "zen_cache_backend", None)
    clear_fn = getattr(cache_backend, "clear", None)
    if callable(clear_fn):
        clear_fn()
