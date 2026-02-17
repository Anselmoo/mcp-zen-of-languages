from __future__ import annotations

from mcp_zen_of_languages.rules import (
    PrincipleCategory,
    get_all_languages,
    get_all_principles_by_category,
    get_principle_by_id,
)


def test_get_all_languages_includes_python():
    assert "python" in get_all_languages()


def test_get_principle_by_id_returns_principle():
    principle = get_principle_by_id("python-001")
    assert principle is not None
    assert principle.id == "python-001"


def test_get_all_principles_by_category():
    result = get_all_principles_by_category(PrincipleCategory.READABILITY)
    assert result
