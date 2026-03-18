from __future__ import annotations

from typing import Literal

import pytest

from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.analyzers.mapping_models import BindingPerspectiveBundle
from mcp_zen_of_languages.analyzers.mapping_models import DogmaPerspectiveModel
from mcp_zen_of_languages.analyzers.mapping_models import ProjectionPerspectiveModel
from mcp_zen_of_languages.analyzers.mapping_models import TestingPerspectiveModel
from mcp_zen_of_languages.analyzers.registry import DetectorMetadata
from mcp_zen_of_languages.analyzers.registry import DetectorRegistry
from mcp_zen_of_languages.languages.configs import DetectorConfig
from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
from mcp_zen_of_languages.rules.base_models import PrincipleCategory
from mcp_zen_of_languages.rules.base_models import ZenPrinciple


class DummyConfig(DetectorConfig):
    type: Literal["dummy"] = "dummy"


class SecondaryDummyConfig(DetectorConfig):
    type: Literal["dummy_two"] = "dummy_two"


class DummyDetector(ViolationDetector[DummyConfig]):
    @property
    def name(self) -> str:
        return "dummy"

    def detect(self, context, config):
        return []


def test_registry_duplicate_detector_id():
    registry = DetectorRegistry()

    metadata = DetectorMetadata(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        language="python",
    )
    registry.register(metadata)
    with pytest.raises(ValueError, match="Duplicate detector_id: dummy"):
        registry.register(metadata)


def test_registry_get_unknown():
    registry = DetectorRegistry()
    with pytest.raises(KeyError):
        registry.get("missing")


def test_registry_register_stores_synthetic_bundle():
    registry = DetectorRegistry()

    metadata = DetectorMetadata(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        language="python",
    )
    registry.register(metadata)

    assert registry.get_bundle("dummy", "python").require_rule_model() == metadata


def test_registry_get_config_union_no_detectors():
    registry = DetectorRegistry()
    with pytest.raises(ValueError, match="No detectors registered"):
        registry.get_config_union()


def test_registry_adapter_with_minimal_detector():
    registry = DetectorRegistry()

    metadata = DetectorMetadata(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        language="python",
    )
    registry.register(metadata)
    union_type = registry.get_config_union()
    assert union_type


def test_registry_exposes_family_models_without_collapsing_to_rule_metadata() -> None:
    registry = DetectorRegistry()
    metadata = DetectorMetadata(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        language="python",
        rule_ids=["python-001"],
    )
    testing_model = TestingPerspectiveModel(
        detector_id="dummy",
        language="python",
        testing_rule_map={"micro": ["python-001"]},
    )
    dogma_model = DogmaPerspectiveModel(
        detector_id="dummy",
        language="python",
        dogma_rule_map={"ZEN-EXPLICIT-INTENT": ["python-001"]},
    )
    projection_model = ProjectionPerspectiveModel(
        detector_id="dummy",
        language="python",
        projection_rule_map={"go": ["python-001"]},
    )
    bundle = BindingPerspectiveBundle(
        rule_model=metadata,
        dogma_model=dogma_model,
        testing_model=testing_model,
        projection_model=projection_model,
    )

    registry.register(metadata, bundle=bundle)

    assert registry.get_testing_model("dummy", "python") == testing_model
    assert registry.get_projection_model("dummy", "python") == projection_model
    assert registry.get_dogma_model("dummy", "python") == dogma_model
    assert registry.testing_ids_for("dummy", "python", "python-001") == ["micro"]
    assert registry.projection_ids_for("dummy", "python", "python-001") == ["go"]
    assert registry.dogma_models_for_rule("python-001", "python") == [dogma_model]
    assert registry.dogma_models_for_family("ZEN-EXPLICIT-INTENT", "python") == [
        dogma_model
    ]
    assert registry.testing_models_for_rule("python-001", "python") == [testing_model]
    assert registry.projection_models_for_rule("python-001", "python") == [
        projection_model,
    ]
    assert registry.testing_models_for_family("micro", "python") == [testing_model]
    assert registry.projection_models_for_family("go", "python") == [projection_model]
    assert registry.bundles_for_rule("python-001", "python") == [bundle]


def test_registry_family_accessors_ignore_missing_family_metadata() -> None:
    registry = DetectorRegistry()
    metadata = DetectorMetadata(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        language="python",
        rule_ids=["python-001"],
    )

    registry.register(metadata)

    assert registry.get_testing_model("dummy", "python") is None
    assert registry.get_projection_model("dummy", "python") is None
    assert registry.get_dogma_model("dummy", "python") is None
    assert registry.testing_ids_for("dummy", "python", "python-001") == []
    assert registry.projection_ids_for("dummy", "python", "python-001") == []
    assert registry.dogma_models_for_rule("python-001", "python") == []
    assert registry.dogma_models_for_family("ZEN-EXPLICIT-INTENT", "python") == []
    assert registry.testing_models_for_rule("python-001", "python") == []
    assert registry.projection_models_for_rule("python-001", "python") == []
    assert registry.testing_models_for_family("micro", "python") == []
    assert registry.projection_models_for_family("go", "python") == []


def test_registry_family_indexes_use_preserved_bundle_metadata() -> None:
    registry = DetectorRegistry()
    metadata = DetectorMetadata(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        language="python",
        rule_ids=[],
    )
    testing_model = TestingPerspectiveModel(
        detector_id="dummy",
        language="python",
        testing_rule_map={"micro": ["python-201"]},
        testing_verified_rule_map={"micro": ["python-201"]},
    )
    dogma_model = DogmaPerspectiveModel(
        detector_id="dummy",
        language="python",
        dogma_rule_map={"ZEN-FAIL-FAST": ["python-101"]},
        dogma_verified_rule_map={"ZEN-FAIL-FAST": ["python-101"]},
    )
    projection_model = ProjectionPerspectiveModel(
        detector_id="dummy",
        language="python",
        projection_rule_map={"go": ["python-301"]},
        projection_verified_rule_map={"go": ["python-301"]},
    )
    bundle = BindingPerspectiveBundle(
        rule_model=metadata,
        dogma_model=dogma_model,
        testing_model=testing_model,
        projection_model=projection_model,
    )

    registry.register(metadata, bundle=bundle)

    assert registry.dogma_models_for_rule("python-101", "python") == [dogma_model]
    assert registry.dogma_models_for_family("ZEN-FAIL-FAST", "python") == [dogma_model]
    assert registry.testing_models_for_rule("python-201", "python") == [testing_model]
    assert registry.projection_models_for_rule("python-301", "python") == [
        projection_model,
    ]
    assert registry.testing_models_for_family("micro", "python") == [testing_model]
    assert registry.projection_models_for_family("go", "python") == [projection_model]
    assert registry.verified_testing_ids_for("dummy", "python", "python-201") == [
        "micro",
    ]
    assert registry.verified_projection_ids_for("dummy", "python", "python-301") == [
        "go",
    ]
    assert registry.bundles_for_rule("python-201", "python") == []


def test_configs_from_rules_preserves_testing_ids_in_rule_contexts() -> None:
    registry = DetectorRegistry()
    metadata = DetectorMetadata(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        language="python",
        rule_ids=["python-001"],
        rule_map={"python-001": ["*"]},
    )
    bundle = BindingPerspectiveBundle(
        rule_model=metadata,
        testing_model=TestingPerspectiveModel(
            detector_id="dummy",
            language="python",
            testing_rule_map={"pytest": ["python-001"]},
            testing_verified_rule_map={"pytest": ["python-001"]},
        ),
    )
    registry.register(metadata, bundle=bundle)
    registry.register(
        DetectorMetadata(
            detector_id="dummy_two",
            detector_class=DummyDetector,
            config_model=SecondaryDummyConfig,
            language="python",
            rule_ids=[],
        ),
    )
    lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="Test",
        source_text="Test",
        source_url="https://example.com/python",
        principles=[
            ZenPrinciple(
                id="python-001",
                principle="Use clear tests",
                category=PrincipleCategory.CLARITY,
                severity=5,
                description="desc",
                violations=["violation"],
            ),
        ],
    )

    config = next(
        detector
        for detector in registry.configs_from_rules(lang_zen)
        if detector.type == "dummy"
    )
    context = config.rule_contexts["python-001"]

    assert context.linked_testing_ids == ["pytest"]
    assert context.verified_testing_ids == ["pytest"]
    assert config.linked_testing_ids_for_rule("python-001") == ["pytest"]
    assert config.verified_testing_ids_for_rule("python-001") == ["pytest"]
