"""Tests for core/universal_mapping.py — UNIVERSAL_DETECTOR_MAP and UNIVERSAL_TESTING_MAP."""

from __future__ import annotations

import pytest

from mcp_zen_of_languages.core.universal_dogmas import TESTING_TACTICS_IDS
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.core.universal_mapping import UNIVERSAL_DETECTOR_MAP
from mcp_zen_of_languages.core.universal_mapping import UNIVERSAL_TESTING_MAP


# ---------------------------------------------------------------------------
# UNIVERSAL_DETECTOR_MAP — structure
# ---------------------------------------------------------------------------


def test_universal_detector_map_language():
    assert UNIVERSAL_DETECTOR_MAP.language == "universal"


def test_universal_detector_map_has_five_bindings():
    assert len(UNIVERSAL_DETECTOR_MAP.bindings) == 5


def test_universal_detector_map_binding_ids():
    ids = {b.detector_id for b in UNIVERSAL_DETECTOR_MAP.bindings}
    assert ids == {
        "universal_clutter",
        "universal_control_flow",
        "universal_state_mutation",
        "universal_signature",
        "universal_shared_keyword",
    }


def test_universal_detector_map_all_have_empty_rule_ids():
    """Universal stubs use explicit dogma IDs, not rule-based inference."""
    for binding in UNIVERSAL_DETECTOR_MAP.bindings:
        assert binding.rule_ids == [], f"{binding.detector_id} must have empty rule_ids"


def test_universal_detector_map_all_have_dogma_ids():
    for binding in UNIVERSAL_DETECTOR_MAP.bindings:
        assert binding.universal_dogma_ids, (
            f"{binding.detector_id} must declare universal_dogma_ids"
        )


def test_universal_detector_map_dogma_ids_are_valid():
    universal_set = set(UNIVERSAL_DOGMA_IDS)
    for binding in UNIVERSAL_DETECTOR_MAP.bindings:
        for dogma_id in binding.universal_dogma_ids:
            assert dogma_id in universal_set, (
                f"{binding.detector_id} references unknown dogma {dogma_id!r}"
            )


def test_universal_detector_map_no_testing_dogma_ids():
    """Production map must not reference ZEN-TEST-* or ZEN-MACRO-* IDs."""
    testing_set = set(TESTING_TACTICS_IDS)
    for binding in UNIVERSAL_DETECTOR_MAP.bindings:
        leaked = set(binding.universal_dogma_ids) & testing_set
        assert not leaked, f"{binding.detector_id} leaks testing dogma IDs: {leaked}"


def test_universal_detector_map_covers_all_ten_dogmas():
    """Together the 5 bindings must cover every ZEN-* dogma."""
    covered = set()
    for binding in UNIVERSAL_DETECTOR_MAP.bindings:
        covered.update(binding.universal_dogma_ids)
    missing = set(UNIVERSAL_DOGMA_IDS) - covered
    assert not missing, f"Uncovered production dogmas: {missing}"


def test_universal_detector_map_orders_are_all_high():
    """Universal stubs should sit at the end of the pipeline (order ≥ 900)."""
    for binding in UNIVERSAL_DETECTOR_MAP.bindings:
        assert binding.default_order >= 900, (
            f"{binding.detector_id} order {binding.default_order} should be ≥ 900"
        )


# ---------------------------------------------------------------------------
# UNIVERSAL_TESTING_MAP — structure
# ---------------------------------------------------------------------------


def test_universal_testing_map_language():
    assert UNIVERSAL_TESTING_MAP.language == "universal_testing"


def test_universal_testing_map_has_bindings():
    assert len(UNIVERSAL_TESTING_MAP.bindings) >= 2


def test_universal_testing_map_binding_ids_unique():
    ids = [b.detector_id for b in UNIVERSAL_TESTING_MAP.bindings]
    assert len(ids) == len(set(ids))


def test_universal_testing_map_all_have_dogma_ids():
    for binding in UNIVERSAL_TESTING_MAP.bindings:
        assert binding.universal_dogma_ids, (
            f"{binding.detector_id} must declare universal_dogma_ids"
        )


def test_universal_testing_map_references_testing_dogmas():
    tactics_set = set(TESTING_TACTICS_IDS)
    all_dogma_ids: set[str] = set()
    for binding in UNIVERSAL_TESTING_MAP.bindings:
        all_dogma_ids.update(binding.universal_dogma_ids)
    assert all_dogma_ids & tactics_set, (
        "UNIVERSAL_TESTING_MAP must reference at least one ZEN-TEST-* dogma"
    )


def test_universal_testing_map_no_production_dogmas():
    """Testing map must not reference ZEN-* (production) dogmas."""
    production_set = set(UNIVERSAL_DOGMA_IDS)
    for binding in UNIVERSAL_TESTING_MAP.bindings:
        leaked = set(binding.universal_dogma_ids) & production_set
        assert not leaked, f"{binding.detector_id} leaks production dogma IDs: {leaked}"


# ---------------------------------------------------------------------------
# Integration: wired into production language pipelines
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "lang",
    ["python", "typescript", "go", "rust", "css", "javascript"],
)
def test_universal_detectors_wired_into_production_language(lang: str):
    import importlib

    mod = importlib.import_module(f"mcp_zen_of_languages.languages.{lang}.mapping")
    detector_map = getattr(mod, "DETECTOR_MAP", None)
    assert detector_map is not None, f"{lang}/mapping.py must have DETECTOR_MAP"
    binding_ids = {b.detector_id for b in detector_map.bindings}
    expected = {
        "universal_clutter",
        "universal_control_flow",
        "universal_state_mutation",
        "universal_signature",
        "universal_shared_keyword",
    }
    missing = expected - binding_ids
    assert not missing, f"{lang} DETECTOR_MAP missing universal bindings: {missing}"


# ---------------------------------------------------------------------------
# Integration: wired into framework pipelines
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "module_path",
    [
        "mcp_zen_of_languages.languages.python.testing.pytest.mapping",
        "mcp_zen_of_languages.languages.typescript.testing.jest.mapping",
        "mcp_zen_of_languages.languages.ruby.testing.rspec.mapping",
        "mcp_zen_of_languages.languages.go.testing.gotest.mapping",
    ],
)
def test_universal_testing_detectors_wired_into_framework(module_path: str):
    import importlib

    mod = importlib.import_module(module_path)
    detector_map = getattr(mod, "DETECTOR_MAP", None)
    assert detector_map is not None
    binding_ids = {b.detector_id for b in detector_map.bindings}
    expected_universal_test_ids = {
        "universal_test_proportional",
        "universal_test_documented_intent",
        "universal_test_single_reason",
    }
    missing = expected_universal_test_ids - binding_ids
    assert not missing, (
        f"{module_path} DETECTOR_MAP missing universal testing bindings: {missing}"
    )
