from __future__ import annotations

from mcp_zen_of_languages.adapters.rules_adapter import RulesAdapter
from mcp_zen_of_languages.models import CyclomaticSummary
from mcp_zen_of_languages.rules.base_models import PrincipleCategory, ZenPrinciple


def test_check_cyclomatic_complexity_handles_missing_avg():
    adapter = RulesAdapter(language="python")
    principle = ZenPrinciple(
        id="x-1",
        principle="Test",
        description="desc",
        severity=5,
        category=PrincipleCategory.COMPLEXITY,
        violations=[],
        metrics={"max_cyclomatic_complexity": 1},
    )
    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    results = adapter._check_cyclomatic_complexity(
        cyclomatic, principle, principle.metrics or {}
    )
    assert isinstance(results, list)


def test_check_maintainability_index_handles_missing_metric():
    adapter = RulesAdapter(language="python")
    principle = ZenPrinciple(
        id="x-2",
        principle="Test",
        description="desc",
        severity=5,
        category=PrincipleCategory.MAINTAINABILITY
        if hasattr(PrincipleCategory, "MAINTAINABILITY")
        else PrincipleCategory.READABILITY,
        violations=[],
        metrics={},
    )
    results = adapter._check_maintainability_index(
        0.0, principle, principle.metrics or {}
    )
    assert results == []


def test_check_dependencies_handles_dict():
    adapter = RulesAdapter(language="python")
    principle = ZenPrinciple(
        id="x-3",
        principle="Test",
        description="desc",
        severity=5,
        category=PrincipleCategory.STRUCTURE,
        violations=[],
        metrics={"max_dependencies": 1},
    )
    results = adapter._check_dependencies(
        {"edges": [("a", "b"), ("a", "c")]}, principle, principle.metrics or {}
    )
    assert results


def test_check_dependencies_handles_cycles():
    adapter = RulesAdapter(language="python")
    principle = ZenPrinciple(
        id="x-4",
        principle="Test",
        description="desc",
        severity=5,
        category=PrincipleCategory.STRUCTURE,
        violations=[],
        metrics={"detect_circular_dependencies": True},
    )
    results = adapter._check_dependencies(
        {"cycles": [["a", "b", "a"]]}, principle, principle.metrics or {}
    )
    assert results


def test_check_patterns_detects_match():
    adapter = RulesAdapter(language="python")
    principle = ZenPrinciple(
        id="x-5",
        principle="Test",
        description="desc",
        severity=5,
        category=PrincipleCategory.READABILITY,
        violations=[],
        detectable_patterns=["foo"],
    )
    results = adapter._check_patterns("foo", principle)
    assert results
