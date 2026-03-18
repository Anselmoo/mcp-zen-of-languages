from __future__ import annotations

import importlib
import warnings

from mcp_zen_of_languages.analyzers.analyzer_factory import supported_languages
from mcp_zen_of_languages.analyzers.registry import REGISTRY
from mcp_zen_of_languages.core.universal_dogmas import DOGMA_RULE_IDS
from mcp_zen_of_languages.core.universal_dogmas import UniversalDogmaID
from mcp_zen_of_languages.core.universal_dogmas import dogmas_for_rule
from mcp_zen_of_languages.core.universal_dogmas import dogmas_for_rule_id
from mcp_zen_of_languages.core.universal_dogmas import dogmas_for_rule_ids
from mcp_zen_of_languages.frameworks import FRAMEWORK_KEYS
from mcp_zen_of_languages.frameworks import FRAMEWORK_RULE_DOGMAS
from mcp_zen_of_languages.frameworks.react.mapping import (
    DETECTOR_MAP as REACT_DETECTOR_MAP,
)
from mcp_zen_of_languages.languages.ansible.dogmas import ANSIBLE_RULE_DOGMAS
from mcp_zen_of_languages.languages.ansible.mapping import (
    DETECTOR_MAP as ANSIBLE_DETECTOR_MAP,
)
from mcp_zen_of_languages.languages.python.mapping import (
    DETECTOR_MAP as PYTHON_DETECTOR_MAP,
)
from mcp_zen_of_languages.languages.ruby.mapping import (
    DETECTOR_MAP as RUBY_DETECTOR_MAP,
)
from mcp_zen_of_languages.languages.rust.mapping import (
    DETECTOR_MAP as RUST_DETECTOR_MAP,
)
from mcp_zen_of_languages.languages.sql.mapping import DETECTOR_MAP as SQL_DETECTOR_MAP
from mcp_zen_of_languages.languages.typescript.mapping import (
    DETECTOR_MAP as TYPESCRIPT_DETECTOR_MAP,
)


PILOT_DETECTOR_EXPECTATIONS = [
    (
        PYTHON_DETECTOR_MAP,
        "explicitness",
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ),
    (
        TYPESCRIPT_DETECTOR_MAP,
        "ts_return_types",
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ),
    (
        RUST_DETECTOR_MAP,
        "rust_error_handling",
        UniversalDogmaID.FAIL_FAST.value,
    ),
    (
        SQL_DETECTOR_MAP,
        "sql-007",
        UniversalDogmaID.UNAMBIGUOUS_NAME.value,
    ),
]


def test_dogmas_for_rule_maps_error_handling_to_fail_fast() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        dogmas = dogmas_for_rule("python", "python-009")
    assert UniversalDogmaID.FAIL_FAST.value in dogmas
    assert any(item.category is DeprecationWarning for item in caught)


def test_dogmas_for_rule_id_maps_error_handling_to_fail_fast() -> None:
    dogmas = dogmas_for_rule_id("python-009")
    assert UniversalDogmaID.FAIL_FAST.value in dogmas


def test_dogmas_for_rule_ids_deduplicate_results() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        dogmas = dogmas_for_rule_ids("typescript", ["ts-001", "ts-004", "ts-001"])
    assert dogmas.count(UniversalDogmaID.EXPLICIT_INTENT.value) == 1
    assert any(item.category is DeprecationWarning for item in caught)


def test_registry_metadata_contains_inferred_universal_dogmas() -> None:
    REGISTRY.adapter()
    meta = REGISTRY.get("ts_any_usage")
    assert meta.rule_dogma_map
    assert UniversalDogmaID.EXPLICIT_INTENT.value in meta.dogma_ids_for_rule("ts-001")
    assert meta.verified_dogma_ids_for_rule("ts-001") == [
        UniversalDogmaID.EXPLICIT_INTENT.value
    ]


def test_pilot_mappings_define_explicit_universal_dogma_overlays() -> None:
    for detector_map, detector_id, expected_dogma in PILOT_DETECTOR_EXPECTATIONS:
        binding = next(
            item for item in detector_map.bindings if item.detector_id == detector_id
        )
        rule_id = binding.rule_ids[0]
        assert binding.rule_dogma_map[rule_id]
        assert expected_dogma in binding.rule_dogma_map[rule_id]


def test_multi_dogma_mappings_can_author_verified_subsets() -> None:
    ruby_binding = next(
        binding
        for binding in RUBY_DETECTOR_MAP.bindings
        if binding.detector_id == "ruby_symbol_keys"
    )
    react_binding = next(
        binding
        for binding in REACT_DETECTOR_MAP.bindings
        if binding.detector_id == "react-003"
    )

    assert ruby_binding.rule_verified_dogma_map["ruby-007"] == [
        UniversalDogmaID.RIGHT_ABSTRACTION.value
    ]
    assert react_binding.rule_verified_dogma_map["react-003"] == [
        UniversalDogmaID.RIGHT_ABSTRACTION.value
    ]


def test_registry_pilot_languages_have_universal_dogma_matrix_coverage() -> None:
    REGISTRY.adapter()
    pilot_metas = [
        meta
        for meta in REGISTRY.items()
        if meta.language in {"python", "typescript", "rust", "sql"}
        and meta.detector_id != "analyzer_defaults"
    ]

    assert pilot_metas
    assert all(meta.rule_dogma_map for meta in pilot_metas)


def test_all_supported_language_mappings_have_dogma_coverage() -> None:
    for language in supported_languages():
        module_name = "github_actions" if language == "github-actions" else language
        package_name = "frameworks" if language in FRAMEWORK_KEYS else "languages"
        mapping = importlib.import_module(
            f"mcp_zen_of_languages.{package_name}.{module_name}.mapping"
        ).DETECTOR_MAP
        for binding in mapping.bindings:
            if not binding.rule_ids:
                continue
            bound_dogmas = [
                dogma for dogmas in binding.rule_dogma_map.values() for dogma in dogmas
            ]
            dogmas = bound_dogmas or list(
                dogmas_for_rule_ids(language, binding.rule_ids)
            )
            assert dogmas
            assert set(dogmas).issubset(set(DOGMA_RULE_IDS))


def test_all_supported_language_mappings_define_explicit_universal_dogmas() -> None:
    for language in supported_languages():
        module_name = "github_actions" if language == "github-actions" else language
        package_name = "frameworks" if language in FRAMEWORK_KEYS else "languages"
        mapping = importlib.import_module(
            f"mcp_zen_of_languages.{package_name}.{module_name}.mapping"
        ).DETECTOR_MAP
        assert all(
            all(binding.rule_dogma_map.values())
            for binding in mapping.bindings
            if binding.rule_ids
        )


def test_all_supported_language_mappings_define_authored_verification_state() -> None:
    for language in supported_languages():
        module_name = "github_actions" if language == "github-actions" else language
        package_name = "frameworks" if language in FRAMEWORK_KEYS else "languages"
        mapping = importlib.import_module(
            f"mcp_zen_of_languages.{package_name}.{module_name}.mapping"
        ).DETECTOR_MAP
        assert all(
            set(binding.rule_verified_dogma_map).issuperset(set(binding.rule_dogma_map))
            for binding in mapping.bindings
            if binding.rule_ids
        )
        assert all(
            set(binding.rule_verified_dogma_map[rule_id]).issubset(
                set(binding.rule_dogma_map[rule_id])
            )
            for binding in mapping.bindings
            for rule_id in binding.rule_ids
        )


def test_framework_mappings_use_targeted_dogmas() -> None:
    for language in FRAMEWORK_KEYS:
        mapping = importlib.import_module(
            f"mcp_zen_of_languages.frameworks.{language}.mapping",
        ).DETECTOR_MAP
        for binding in mapping.bindings:
            dogmas = binding.rule_dogma_map[binding.rule_ids[0]]
            assert dogmas
            assert len(dogmas) < len(DOGMA_RULE_IDS)
            assert tuple(dogmas) == FRAMEWORK_RULE_DOGMAS[binding.rule_ids[0]]


def test_ansible_mappings_use_explicit_targeted_dogmas() -> None:
    for binding in ANSIBLE_DETECTOR_MAP.bindings:
        dogmas = binding.rule_dogma_map[binding.rule_ids[0]]
        assert dogmas
        assert len(dogmas) < len(DOGMA_RULE_IDS)
        assert dogmas == ANSIBLE_RULE_DOGMAS[binding.rule_ids[0]]


def test_registry_all_supported_languages_have_full_dogma_metadata() -> None:
    REGISTRY.adapter()
    languages = set(supported_languages())
    for language in languages:
        language_metas = [
            meta
            for meta in REGISTRY.items()
            if meta.language == language
            and meta.detector_id != "analyzer_defaults"
            and meta.rule_ids
        ]
        assert language_metas
        assert all(meta.rule_dogma_map for meta in language_metas)
        assert all(meta.rule_verified_dogma_map for meta in language_metas)
        assert all(
            {
                dogma for dogmas in meta.rule_dogma_map.values() for dogma in dogmas
            }.issubset(set(DOGMA_RULE_IDS))
            for meta in language_metas
        )
        assert all(
            {
                dogma
                for dogmas in meta.rule_verified_dogma_map.values()
                for dogma in dogmas
            }.issubset(set(DOGMA_RULE_IDS))
            for meta in language_metas
        )
