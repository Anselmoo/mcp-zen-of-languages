from __future__ import annotations

import pytest

from mcp_zen_of_languages.analyzers.registry import DetectorMetadata, DetectorRegistry
from mcp_zen_of_languages.languages.configs import DetectorConfig


def test_registry_duplicate_detector_id():
    registry = DetectorRegistry()

    class DummyConfig(DetectorConfig):
        type: str = "dummy"

    from mcp_zen_of_languages.analyzers.base import ViolationDetector

    class DummyDetector(ViolationDetector[DummyConfig]):
        @property
        def name(self) -> str:
            return "dummy"

        def detect(self, context, config):
            return []

    metadata = DetectorMetadata(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        language="python",
    )
    registry.register(metadata)
    with pytest.raises(ValueError):
        registry.register(metadata)


def test_registry_get_unknown():
    registry = DetectorRegistry()
    with pytest.raises(KeyError):
        registry.get("missing")


def test_registry_get_config_union_no_detectors():
    registry = DetectorRegistry()
    with pytest.raises(ValueError):
        registry.get_config_union()


def test_registry_adapter_with_minimal_detector():
    registry = DetectorRegistry()

    class DummyConfig(DetectorConfig):
        type: str = "dummy"

    from mcp_zen_of_languages.analyzers.base import ViolationDetector

    class DummyDetector(ViolationDetector[DummyConfig]):
        @property
        def name(self) -> str:
            return "dummy"

        def detect(self, context, config):
            return []

    metadata = DetectorMetadata(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        language="python",
    )
    registry.register(metadata)
    union_type = registry.get_config_union()
    assert union_type
