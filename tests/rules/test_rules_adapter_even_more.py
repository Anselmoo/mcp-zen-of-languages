from __future__ import annotations

from mcp_zen_of_languages.adapters.rules_adapter import RulesAdapter
from mcp_zen_of_languages.rules.base_models import PrincipleCategory, ZenPrinciple


def _build_principle(metrics=None, patterns=None):
    return ZenPrinciple(
        id="x-1",
        principle="Test",
        description="desc",
        severity=5,
        category=PrincipleCategory.READABILITY,
        violations=[],
        metrics=metrics,
        detectable_patterns=patterns,
    )


def test_check_maintainability_index_handles_key_error():
    adapter = RulesAdapter(language="python")
    principle = _build_principle(metrics={"min_maintainability_index": "bad"})
    results = adapter._check_maintainability_index(
        0.0, principle, principle.metrics or {}
    )
    assert results == []


def test_check_cyclomatic_complexity_handles_type_error():
    adapter = RulesAdapter(language="python")
    principle = _build_principle(metrics={"max_cyclomatic_complexity": "bad"})
    results = adapter._check_cyclomatic_complexity(
        type("C", (), {})(), principle, principle.metrics or {}
    )
    assert results == []


def test_check_dependencies_handles_unknown_shape():
    adapter = RulesAdapter(language="python")
    principle = _build_principle(metrics={"detect_circular_dependencies": True})
    results = adapter._check_dependencies(object(), principle, principle.metrics or {})
    assert results == []


def test_check_patterns_handles_bad_pattern():
    adapter = RulesAdapter(language="python")
    principle = _build_principle(patterns=["["], metrics=None)
    results = adapter._check_patterns("foo", principle)
    assert isinstance(results, list)
