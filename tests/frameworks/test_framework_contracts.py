from __future__ import annotations

import importlib

import pytest

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer
from mcp_zen_of_languages.frameworks import FRAMEWORK_DESCRIPTORS
from mcp_zen_of_languages.frameworks import FRAMEWORK_KEYS
from mcp_zen_of_languages.frameworks import FRAMEWORK_RULE_DOGMAS
from mcp_zen_of_languages.frameworks import framework_descriptor


def test_framework_descriptor_registry_matches_framework_keys() -> None:
    assert {descriptor.key for descriptor in FRAMEWORK_DESCRIPTORS} == FRAMEWORK_KEYS


def test_framework_rule_dogma_matrix_covers_every_framework_rule() -> None:
    for descriptor in FRAMEWORK_DESCRIPTORS:
        rules_module = importlib.import_module(
            f"mcp_zen_of_languages.frameworks.{descriptor.key}.rules",
        )
        zen = next(
            value
            for name, value in vars(rules_module).items()
            if name.endswith("_ZEN")
            and getattr(value, "language", None) == descriptor.key
        )
        rule_ids = {principle.id for principle in zen.principles}
        assert rule_ids.issubset(FRAMEWORK_RULE_DOGMAS)


@pytest.mark.parametrize(
    ("framework", "parent_language"),
    [
        (descriptor.key, descriptor.parent_language)
        for descriptor in FRAMEWORK_DESCRIPTORS
    ],
)
def test_framework_analyzers_expose_framework_contract(
    framework: str,
    parent_language: str,
) -> None:
    analyzer = create_analyzer(framework)

    assert analyzer.language() == framework
    assert analyzer.framework_language() == framework
    assert analyzer.parent_language() == parent_language
    assert framework_descriptor(framework) is not None


@pytest.mark.parametrize("framework", sorted(FRAMEWORK_KEYS))
def test_framework_mapping_modules_load_from_frameworks_package(framework: str) -> None:
    mapping_module = importlib.import_module(
        f"mcp_zen_of_languages.frameworks.{framework}.mapping",
    )

    assert mapping_module.DETECTOR_MAP.language == framework
    assert all(
        all(binding.rule_dogma_map.values())
        for binding in mapping_module.DETECTOR_MAP.bindings
    )


@pytest.mark.parametrize("framework", sorted(FRAMEWORK_KEYS))
def test_framework_mappings_bind_each_rule_to_a_concrete_detector_class(
    framework: str,
) -> None:
    mapping_module = importlib.import_module(
        f"mcp_zen_of_languages.frameworks.{framework}.mapping",
    )
    detector_class_names = [
        binding.detector_class.__name__
        for binding in mapping_module.DETECTOR_MAP.bindings
    ]

    assert len(detector_class_names) == len(set(detector_class_names))
    assert all(not name.endswith("RuleDetector") for name in detector_class_names)
