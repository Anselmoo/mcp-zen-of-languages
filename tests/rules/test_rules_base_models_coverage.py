from __future__ import annotations

from mcp_zen_of_languages.rules.base_models import ZenPrinciple


def test_compiled_patterns_fallback():
    principle = ZenPrinciple(
        id="demo",
        principle="Demo",
        category="readability",
        severity=5,
        description="desc",
        violations=[],
        detectable_patterns=["["],
    )
    compiled = principle.compiled_patterns()
    assert compiled
