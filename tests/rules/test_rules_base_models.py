from __future__ import annotations

from mcp_zen_of_languages.models import DependencyAnalysis
from mcp_zen_of_languages.models import DependencyCycle
from mcp_zen_of_languages.models import Violation
from mcp_zen_of_languages.rules import base_models


DEFAULT_SEVERITY = 5


def test_violation_get_and_getitem():
    violation = Violation(
        principle="Test",
        severity=DEFAULT_SEVERITY,
        message="msg",
        suggestion="fix",
    )
    assert violation.get("severity") == DEFAULT_SEVERITY
    assert violation["message"] == "msg"


def test_dependency_cycle_model():
    cycle = DependencyCycle(cycle=["a", "b", "a"])
    analysis = DependencyAnalysis(nodes=["a", "b"], edges=[("a", "b")], cycles=[cycle])
    assert analysis.cycles[0].cycle == ["a", "b", "a"]


def test_registry_stats_from_registry():
    zen = base_models.ZenPrinciple(
        id="x-1",
        principle="Test",
        description="desc",
        severity=DEFAULT_SEVERITY,
        category=base_models.PrincipleCategory.READABILITY,
        violations=[],
    )
    language = base_models.LanguageZenPrinciples(
        language="x",
        name="X",
        philosophy="Test",
        source_text="source",
        source_url="https://example.com/source",
        principles=[zen],
    )
    stats = base_models.RegistryStats.from_registry({"x": language})
    assert stats.total_languages == 1
    assert stats.total_principles == 1


def test_principle_helpers():
    zen = base_models.ZenPrinciple(
        id="x-1",
        principle="Test",
        description="desc",
        severity=DEFAULT_SEVERITY,
        category=base_models.PrincipleCategory.READABILITY,
        violations=[],
    )
    language = base_models.LanguageZenPrinciples(
        language="x",
        name="X",
        philosophy="Test",
        source_text="source",
        source_url="https://example.com/source",
        principles=[zen],
    )
    assert base_models.get_number_of_principles(language) == 1
    assert base_models.get_number_of_priniciple(language) == 1
    assert base_models.get_rule_ids(language) == {"x-1"}
    assert base_models.get_total_principles({"x": language}) == 1


def test_detector_gap_helpers():
    zen = base_models.ZenPrinciple(
        id="x-1",
        principle="Test",
        description="desc",
        severity=DEFAULT_SEVERITY,
        category=base_models.PrincipleCategory.READABILITY,
        violations=[],
    )
    language = base_models.LanguageZenPrinciples(
        language="x",
        name="X",
        philosophy="Test",
        source_text="source",
        source_url="https://example.com/source",
        principles=[zen],
    )
    assert base_models.get_missing_detector_rules(language) == ["x-1"]
    missing, unknown = base_models.get_rule_id_coverage(language)
    assert missing == ["x-1"]
    assert unknown == []
    assert base_models.get_registry_detector_gaps({"x": language}) == {"x": ["x-1"]}
    assert base_models.get_registry_rule_id_gaps({"x": language}) == {
        "x": {"missing": ["x-1"], "unknown": []},
    }


def test_zen_principle_retains_per_principle_source_url():
    """A principle may cite its own upstream guidance, not just its language's."""
    from pydantic import HttpUrl

    from mcp_zen_of_languages.rules.base_models import PrincipleCategory
    from mcp_zen_of_languages.rules.base_models import ZenPrinciple

    principle = ZenPrinciple(
        id="js-012",
        principle="Use destructuring for assignment",
        category=PrincipleCategory.IDIOMS,
        severity=5,
        description="Prefer destructuring over manual extraction",
        source_url=HttpUrl("https://github.com/airbnb/javascript#destructuring"),
    )

    assert principle.source_url is not None
    assert str(principle.source_url).endswith("#destructuring")


def test_zen_principle_source_url_defaults_to_none():
    """Principles without their own citation fall back to the language-level URL."""
    from mcp_zen_of_languages.rules.base_models import PrincipleCategory
    from mcp_zen_of_languages.rules.base_models import ZenPrinciple

    principle = ZenPrinciple(
        id="python-001",
        principle="Explicit is better than implicit",
        category=PrincipleCategory.IDIOMS,
        severity=5,
        description="Say what you mean",
    )

    assert principle.source_url is None
