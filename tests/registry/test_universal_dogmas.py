from __future__ import annotations

import importlib

from mcp_zen_of_languages.analyzers.analyzer_factory import supported_languages
from mcp_zen_of_languages.analyzers.registry import REGISTRY
from mcp_zen_of_languages.core.universal_dogmas import (
    DOGMA_RULE_IDS,
    UniversalDogmaID,
    dogmas_for_rule,
    dogmas_for_rule_ids,
)
from mcp_zen_of_languages.languages.python.mapping import (
    DETECTOR_MAP as PYTHON_DETECTOR_MAP,
)
from mcp_zen_of_languages.languages.rust.mapping import (
    DETECTOR_MAP as RUST_DETECTOR_MAP,
)
from mcp_zen_of_languages.languages.sql.mapping import (
    DETECTOR_MAP as SQL_DETECTOR_MAP,
)
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
    dogmas = dogmas_for_rule("python", "python-009")
    assert UniversalDogmaID.FAIL_FAST.value in dogmas


def test_dogmas_for_rule_ids_deduplicate_results() -> None:
    dogmas = dogmas_for_rule_ids("typescript", ["ts-001", "ts-004", "ts-001"])
    assert dogmas.count(UniversalDogmaID.EXPLICIT_INTENT.value) == 1


def test_registry_metadata_contains_inferred_universal_dogmas() -> None:
    REGISTRY.adapter()
    meta = REGISTRY.get("ts_any_usage")
    assert meta.universal_dogma_ids
    assert UniversalDogmaID.EXPLICIT_INTENT.value in meta.universal_dogma_ids


def test_pilot_mappings_define_explicit_universal_dogma_overlays() -> None:
    for detector_map, detector_id, expected_dogma in PILOT_DETECTOR_EXPECTATIONS:
        binding = next(
            item for item in detector_map.bindings if item.detector_id == detector_id
        )
        assert binding.universal_dogma_ids
        assert expected_dogma in binding.universal_dogma_ids


def test_registry_pilot_languages_have_universal_dogma_matrix_coverage() -> None:
    REGISTRY.adapter()
    pilot_metas = [
        meta
        for meta in REGISTRY.items()
        if meta.language in {"python", "typescript", "rust", "sql"}
        and meta.detector_id != "analyzer_defaults"
    ]

    assert pilot_metas
    assert all(meta.universal_dogma_ids for meta in pilot_metas)


def test_all_supported_language_mappings_have_full_dogma_overlay() -> None:
    for language in supported_languages():
        module_name = "github_actions" if language == "github-actions" else language
        mapping = importlib.import_module(
            f"mcp_zen_of_languages.languages.{module_name}.mapping"
        ).DETECTOR_MAP
        for binding in mapping.bindings:
            assert tuple(binding.universal_dogma_ids) == DOGMA_RULE_IDS


def test_registry_all_supported_languages_have_full_dogma_metadata() -> None:
    REGISTRY.adapter()
    languages = set(supported_languages())
    for language in languages:
        language_metas = [
            meta
            for meta in REGISTRY.items()
            if meta.language == language and meta.detector_id != "analyzer_defaults"
        ]
        assert language_metas
        assert all(tuple(meta.universal_dogma_ids) == DOGMA_RULE_IDS for meta in language_metas)
