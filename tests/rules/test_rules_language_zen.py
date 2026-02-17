from __future__ import annotations

from mcp_zen_of_languages.rules.base_models import (
    LanguageZenPrinciples,
    PrincipleCategory,
    ZenPrinciple,
)


def test_language_zen_get_by_id():
    principle = ZenPrinciple(
        id="x-1",
        principle="Test",
        description="desc",
        severity=5,
        category=PrincipleCategory.READABILITY,
        violations=[],
    )
    language = LanguageZenPrinciples(
        language="x",
        name="X",
        philosophy="Test",
        source_text="source",
        source_url="https://example.com/source",
        principles=[principle],
    )
    assert language.get_by_id("x-1") == principle


def test_language_zen_get_by_category():
    principle = ZenPrinciple(
        id="x-2",
        principle="Test",
        description="desc",
        severity=5,
        category=PrincipleCategory.READABILITY,
        violations=[],
    )
    language = LanguageZenPrinciples(
        language="x",
        name="X",
        philosophy="Test",
        source_text="source",
        source_url="https://example.com/source",
        principles=[principle],
    )
    result = language.get_by_category(PrincipleCategory.READABILITY)
    assert result == [principle]


def test_language_zen_get_by_severity():
    principle = ZenPrinciple(
        id="x-3",
        principle="Test",
        description="desc",
        severity=9,
        category=PrincipleCategory.READABILITY,
        violations=[],
    )
    language = LanguageZenPrinciples(
        language="x",
        name="X",
        philosophy="Test",
        source_text="source",
        source_url="https://example.com/source",
        principles=[principle],
    )
    assert language.get_by_severity(min_severity=9) == [principle]
