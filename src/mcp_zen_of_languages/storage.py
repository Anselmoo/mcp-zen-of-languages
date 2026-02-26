"""Storage abstractions for FastMCP middleware and stateful server features."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from time import monotonic
from typing import Protocol

logger = logging.getLogger(__name__)


class CacheBackend(Protocol):
    """Minimal cache backend contract used by middleware and lifespan hooks."""

    def get(self, key: str) -> object | None:
        """Return cached value for key, or ``None`` when absent/expired."""

    def set(self, key: str, value: object, *, ttl_seconds: int) -> None:
        """Store a value under key for *ttl_seconds* seconds."""

    def clear(self) -> None:
        """Remove all stored entries."""


@dataclass
class _CacheItem:
    """Single in-memory cache entry."""

    value: object
    expires_at: float


class InMemoryCacheBackend:
    """Simple process-local cache backend with TTL support."""

    def __init__(self) -> None:
        """Initialize in-memory entry store."""
        self._entries: dict[str, _CacheItem] = {}

    def get(self, key: str) -> object | None:
        """Return a non-expired entry or ``None`` when absent/expired."""
        item = self._entries.get(key)
        if item is None:
            return None
        if monotonic() >= item.expires_at:
            self._entries.pop(key, None)
            return None
        return item.value

    def set(self, key: str, value: object, *, ttl_seconds: int) -> None:
        """Store entry with monotonic-clock expiration."""
        self._entries[key] = _CacheItem(
            value=value,
            expires_at=monotonic() + max(ttl_seconds, 1),
        )

    def clear(self) -> None:
        """Remove all cached entries."""
        self._entries.clear()


def create_cache_backend() -> CacheBackend:
    """Create cache backend from environment-backed configuration."""
    backend_name = os.environ.get("ZEN_CACHE_BACKEND", "memory").strip().lower()
    if backend_name == "memory":
        return InMemoryCacheBackend()
    logger.warning(
        "Unsupported cache backend '%s'; falling back to in-memory backend.",
        backend_name,
    )
    return InMemoryCacheBackend()
