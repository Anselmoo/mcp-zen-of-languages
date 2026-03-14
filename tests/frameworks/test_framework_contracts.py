from __future__ import annotations

import importlib

import pytest

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer
from mcp_zen_of_languages.frameworks import FRAMEWORK_DESCRIPTORS
from mcp_zen_of_languages.frameworks import FRAMEWORK_KEYS
from mcp_zen_of_languages.frameworks import framework_descriptor


def test_framework_descriptor_registry_matches_framework_keys() -> None:
    assert {descriptor.key for descriptor in FRAMEWORK_DESCRIPTORS} == FRAMEWORK_KEYS


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
