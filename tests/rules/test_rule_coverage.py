from __future__ import annotations

import pytest

from mcp_zen_of_languages.analyzers import registry as registry_module
from mcp_zen_of_languages.rules import coverage as coverage_module
from mcp_zen_of_languages.rules import (
    get_all_languages,
    get_language_zen,
    get_rule_id_coverage,
)
from mcp_zen_of_languages.rules.base_models import (
    LanguageZenPrinciples,
    PrincipleCategory,
    ZenPrinciple,
)
from mcp_zen_of_languages.rules.coverage import (
    build_all_explicit_rule_coverage,
    build_all_rule_coverage,
    build_explicit_rule_coverage,
    build_rule_coverage,
)


def test_build_rule_coverage_python() -> None:
    coverage = build_rule_coverage("python")
    lang_zen = get_language_zen("python")
    assert lang_zen is not None
    rule_ids = {principle.id for principle in lang_zen.principles}
    assert set(coverage.rules) == rule_ids
    missing = {
        rule_id for rule_id, detectors in coverage.rules.items() if not detectors
    }
    assert not missing
    assert "nesting_depth" in coverage.rules["python-005"]


def test_build_all_rule_coverage_has_no_missing_rules() -> None:
    coverages = build_all_rule_coverage()
    coverage_by_language = {coverage.language: coverage for coverage in coverages}
    for language in get_all_languages():
        coverage = coverage_by_language[language]
        lang_zen = get_language_zen(language)
        assert lang_zen is not None
        expected_rules = {principle.id for principle in lang_zen.principles}
        assert set(coverage.rules) == expected_rules
        counts = coverage.detector_counts()
        assert all(counts.values())
        for detectors in coverage.rules.values():
            assert detectors
            assert "placeholder_detector" not in detectors


def test_build_explicit_rule_coverage_powershell() -> None:
    coverage = build_explicit_rule_coverage("powershell")
    for detectors in coverage.rules.values():
        assert detectors


def test_build_explicit_rule_coverage_languages() -> None:
    for language in (
        "powershell",
        "ruby",
        "go",
        "javascript",
        "typescript",
        "python",
        "cpp",
        "csharp",
        "yaml",
        "toml",
        "json",
        "xml",
        "docker_compose",
        "dockerfile",
    ):
        coverage = build_explicit_rule_coverage(language)
        assert coverage.rules
        assert all(coverage.detector_counts().values())


def test_rule_id_coverage_has_no_gaps() -> None:
    for language in get_all_languages():
        lang_zen = get_language_zen(language)
        assert lang_zen is not None
        missing, unknown = get_rule_id_coverage(lang_zen)
        assert missing == []
        assert unknown == []


def test_build_rule_coverage_unknown_language() -> None:
    with pytest.raises(ValueError, match="Unknown language"):
        build_rule_coverage("unknownlang")


def test_build_explicit_rule_coverage_unknown_language() -> None:
    with pytest.raises(ValueError, match="Unknown language"):
        build_explicit_rule_coverage("unknownlang")


def test_build_all_explicit_rule_coverage_with_subset() -> None:
    coverages = build_all_explicit_rule_coverage(["python"])
    assert len(coverages) == 1
    assert coverages[0].language == "python"


def test_build_explicit_rule_coverage_missing_detector(monkeypatch) -> None:
    language = LanguageZenPrinciples(
        language="fake",
        name="Fake",
        philosophy="Testing",
        source_text="Test",
        source_url="https://example.com",
        principles=[
            ZenPrinciple(
                id="fake-1",
                principle="Test principle",
                category=PrincipleCategory.CLARITY,
                severity=5,
                description="Test description",
            ),
        ],
    )

    monkeypatch.setattr(coverage_module, "get_language_zen", lambda _: language)
    monkeypatch.setattr(registry_module.REGISTRY, "detectors_for_rule", lambda *_: [])

    with pytest.raises(ValueError, match="Explicit coverage missing"):
        coverage_module.build_explicit_rule_coverage("fake")
