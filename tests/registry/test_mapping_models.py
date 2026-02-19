from __future__ import annotations

import importlib
import types

import pytest

from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.analyzers.mapping_models import (
    DetectorBinding,
    FullDetectorMap,
    LanguageDetectorMap,
)
from mcp_zen_of_languages.analyzers.registry import DetectorMetadata, DetectorRegistry
from mcp_zen_of_languages.languages.configs import DetectorConfig


class DummyConfig(DetectorConfig):
    type: str = "dummy"


class DummyDetector(ViolationDetector[DummyConfig]):
    @property
    def name(self) -> str:
        return "dummy"

    def detect(self, context, config):
        return []


def test_mapping_models_defaults():
    binding = DetectorBinding(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
    )
    lang_map = LanguageDetectorMap(language="python", bindings=[binding])
    full_map = FullDetectorMap(languages={"python": lang_map})

    assert binding.rule_ids == []
    assert binding.coverage == "partial"
    assert full_map.languages["python"].bindings[0].detector_id == "dummy"


def test_detector_metadata_from_binding():
    binding = DetectorBinding(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        rule_ids=["python-001"],
        default_order=5,
        enabled_by_default=False,
    )
    metadata = DetectorMetadata.from_binding(binding, "python")

    assert metadata.language == "python"
    assert metadata.rule_ids == ["python-001"]
    assert metadata.default_order == 5
    assert metadata.enabled_by_default is False


def test_registry_bootstrap_from_mappings():
    registry = DetectorRegistry()
    registry.bootstrap_from_mappings()
    registry.bootstrap_from_mappings()

    assert registry.items()
    assert registry.get("analyzer_defaults").language == "python"


def test_detector_metadata_rule_map_sets_rule_ids():
    metadata = DetectorMetadata(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        language="python",
        rule_map={"python-001": ["*"]},
    )
    assert metadata.rule_ids == ["python-001"]


def test_bootstrap_from_mappings_propagates_unrelated_import_error(monkeypatch):
    registry = DetectorRegistry()

    def fake_import(name):
        error = ModuleNotFoundError("missing_dep")
        error.name = "missing_dep"
        raise error

    monkeypatch.setattr(importlib, "import_module", fake_import)
    with pytest.raises(ModuleNotFoundError):
        registry.bootstrap_from_mappings()


def test_bootstrap_from_mappings_requires_detector_map(monkeypatch):
    registry = DetectorRegistry()

    def fake_import(name):
        return types.SimpleNamespace()

    monkeypatch.setattr(importlib, "import_module", fake_import)
    with pytest.raises(ValueError, match="Missing DETECTOR_MAP"):
        registry.bootstrap_from_mappings()


def test_bootstrap_from_mappings_skips_missing_module(monkeypatch):
    registry = DetectorRegistry()

    def fake_import(name):
        error = ModuleNotFoundError(name)
        error.name = name
        raise error

    monkeypatch.setattr(importlib, "import_module", fake_import)
    registry.bootstrap_from_mappings()
    assert registry.items() == []
