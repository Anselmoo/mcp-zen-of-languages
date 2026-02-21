from __future__ import annotations

from types import SimpleNamespace

import pytest

from mcp_zen_of_languages.analyzers import registry as registry_module
from mcp_zen_of_languages.languages.configs import (
    DetectorConfig,
    PowerShellApprovedVerbConfig,
    PowerShellCmdletBindingConfig,
)
from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector
from mcp_zen_of_languages.rules import coverage as coverage_module
from mcp_zen_of_languages.rules import get_all_languages, get_language_zen
from mcp_zen_of_languages.rules.base_models import (
    LanguageZenPrinciples,
    PrincipleCategory,
    ZenPrinciple,
)
from mcp_zen_of_languages.rules.coverage import (
    build_all_explicit_rule_config_coverage,
    build_all_rule_config_coverage,
    build_explicit_rule_config_coverage,
    build_rule_config_coverage,
)


def test_build_rule_config_coverage_powershell() -> None:
    coverage = build_rule_config_coverage("powershell")
    assert PowerShellApprovedVerbConfig in coverage.rules["ps-001"]
    assert coverage.rules["ps-002"]
    assert all(
        issubclass(config, DetectorConfig) for config in coverage.rules["ps-001"]
    )


def test_build_explicit_rule_config_coverage_powershell() -> None:
    coverage = build_explicit_rule_config_coverage("powershell")
    assert PowerShellCmdletBindingConfig in coverage.rules["ps-003"]
    for configs in coverage.rules.values():
        assert configs
        assert all(issubclass(config, DetectorConfig) for config in configs)


def test_build_explicit_rule_config_coverage_languages() -> None:
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
        coverage = build_explicit_rule_config_coverage(language)
        assert coverage.rules
        assert all(coverage.config_counts().values())


def test_build_all_rule_config_coverage_has_no_missing_rules() -> None:
    coverages = build_all_rule_config_coverage()
    coverage_by_language = {coverage.language: coverage for coverage in coverages}
    for language in get_all_languages():
        coverage = coverage_by_language[language]
        lang_zen = get_language_zen(language)
        assert lang_zen is not None
        expected_rules = {principle.id for principle in lang_zen.principles}
        assert set(coverage.rules) == expected_rules
        assert all(coverage.config_counts().values())
        for configs in coverage.rules.values():
            assert configs
            assert all(issubclass(config, DetectorConfig) for config in configs)


def test_build_rule_config_coverage_unknown_language() -> None:
    with pytest.raises(ValueError, match="Unknown language"):
        build_rule_config_coverage("unknownlang")


def test_build_explicit_rule_config_coverage_unknown_language() -> None:
    with pytest.raises(ValueError, match="Unknown language"):
        build_explicit_rule_config_coverage("unknownlang")


def test_build_explicit_rule_config_coverage_missing_configs(monkeypatch) -> None:
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

    with pytest.raises(ValueError, match="Explicit config coverage missing"):
        coverage_module.build_explicit_rule_config_coverage("fake")


def test_build_rule_config_coverage_deduplicates_configs(monkeypatch) -> None:
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
    metas = [
        SimpleNamespace(
            detector_id="a",
            config_model=DetectorConfig,
            detector_class=object,
        ),
        SimpleNamespace(
            detector_id="b",
            config_model=DetectorConfig,
            detector_class=object,
        ),
    ]

    monkeypatch.setattr(coverage_module, "get_language_zen", lambda _: language)
    monkeypatch.setattr(
        registry_module.REGISTRY,
        "detectors_for_rule",
        lambda *_: metas,
    )

    coverage = coverage_module.build_rule_config_coverage("fake")
    assert coverage.rules["fake-1"] == [DetectorConfig]


def test_build_explicit_rule_config_coverage_deduplicates_configs(
    monkeypatch,
) -> None:
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
    metas = [
        SimpleNamespace(
            detector_id="a",
            config_model=DetectorConfig,
            detector_class=object,
        ),
        SimpleNamespace(
            detector_id="b",
            config_model=DetectorConfig,
            detector_class=object,
        ),
        SimpleNamespace(
            detector_id="c",
            config_model=DetectorConfig,
            detector_class=RulePatternDetector,
        ),
    ]

    monkeypatch.setattr(coverage_module, "get_language_zen", lambda _: language)
    monkeypatch.setattr(
        registry_module.REGISTRY,
        "detectors_for_rule",
        lambda *_: metas,
    )

    coverage = coverage_module.build_explicit_rule_config_coverage("fake")
    assert coverage.rules["fake-1"] == [DetectorConfig]


def test_build_all_explicit_rule_config_coverage_with_subset() -> None:
    coverages = build_all_explicit_rule_config_coverage(["python"])
    assert len(coverages) == 1
    assert coverages[0].language == "python"
