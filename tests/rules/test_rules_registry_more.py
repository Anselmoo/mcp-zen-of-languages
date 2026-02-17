from __future__ import annotations

from mcp_zen_of_languages.rules import (
    get_all_critical_principles,
    get_registry_stats,
)


def test_get_all_critical_principles_returns_mapping():
    critical = get_all_critical_principles()
    assert isinstance(critical, dict)
    assert "python" in critical


def test_get_registry_stats_summary():
    stats = get_registry_stats()
    assert stats.total_languages >= 1
    assert stats.total_principles > 0
