from __future__ import annotations

from mcp_zen_of_languages.adapters.rules_adapter import RulesAdapter
from mcp_zen_of_languages.models import (
    CyclomaticSummary,
    DependencyAnalysis,
    DependencyCycle,
)


def test_rules_adapter_no_language_returns_empty():
    adapter = RulesAdapter(language="unknown")
    assert adapter.find_violations("def foo():\n    pass\n") == []


def test_rules_adapter_nesting_and_patterns():
    adapter = RulesAdapter(language="python")
    code = "def foo():\n    if True:\n        if True:\n            if True:\n                if True:\n                    pass\n"
    violations = adapter.find_violations(code)
    assert any("Nesting depth" in v.message for v in violations)


def test_rules_adapter_cyclomatic_and_maintainability():
    adapter = RulesAdapter(language="python")
    cyclomatic = CyclomaticSummary(blocks=[], average=20.0)
    violations = adapter.find_violations(
        "def foo():\n    pass\n",
        cyclomatic_summary=cyclomatic,
        maintainability_index=0.0,
    )
    assert any("cyclomatic" in v.message for v in violations)


def test_rules_adapter_dependency_cycle():
    adapter = RulesAdapter(language="python")
    dep = DependencyAnalysis(
        nodes=["a", "b"],
        edges=[("a", "b"), ("b", "a")],
        cycles=[DependencyCycle(cycle=["a", "b", "a"])],
    )
    violations = adapter.find_violations(
        "def foo():\n    pass\n", dependency_analysis=dep
    )
    assert isinstance(violations, list)
