from __future__ import annotations

import importlib
import types

import pytest

from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.analyzers.mapping_models import BindingPerspectiveBundle
from mcp_zen_of_languages.analyzers.mapping_models import DogmaPerspectiveModel
from mcp_zen_of_languages.analyzers.mapping_models import FullDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import NonRuleDetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import ProjectionPerspectiveModel
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import TestingPerspectiveModel
from mcp_zen_of_languages.analyzers.registry import DetectorMetadata
from mcp_zen_of_languages.analyzers.registry import DetectorRegistry
from mcp_zen_of_languages.core.universal_dogmas import UniversalDogmaID
from mcp_zen_of_languages.languages.configs import DetectorConfig


DEFAULT_DETECTOR_ORDER = 5


class DummyConfig(DetectorConfig):
    type: str = "dummy"


class DummyDetector(ViolationDetector[DummyConfig]):
    @property
    def name(self) -> str:
        return "dummy"

    def detect(self, context, config):
        return []


def test_mapping_models_defaults():
    binding = NonRuleDetectorBinding(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
    )
    lang_map = LanguageDetectorMap(language="python", bindings=[binding])
    full_map = FullDetectorMap(languages={"python": lang_map})
    bundle = binding.build_bundle("python")

    assert binding.to_metadata("python").rule_ids == []
    assert full_map.languages["python"].bindings[0].detector_id == "dummy"
    assert isinstance(bundle, BindingPerspectiveBundle)
    assert bundle.dogma_model is None


def test_rule_binding_to_metadata():
    binding = RuleDetectorBinding(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        rules=[
            RuleBinding(
                rule_id="python-001",
                dogma_ids=[UniversalDogmaID.UNAMBIGUOUS_NAME.value],
            ),
        ],
        default_order=DEFAULT_DETECTOR_ORDER,
        enabled_by_default=False,
    )
    bundle = binding.build_bundle("python")
    metadata = bundle.require_rule_model()

    assert metadata.language == "python"
    assert metadata.rule_ids == ["python-001"]
    assert metadata.rule_dogma_map == {
        "python-001": [UniversalDogmaID.UNAMBIGUOUS_NAME.value],
    }
    assert metadata.rule_verified_dogma_map == {
        "python-001": [UniversalDogmaID.UNAMBIGUOUS_NAME.value],
    }
    assert metadata.default_order == DEFAULT_DETECTOR_ORDER
    assert metadata.enabled_by_default is False
    assert bundle.rule_model is metadata
    assert bundle.rule_model.rule_ids == ["python-001"]
    assert isinstance(bundle.dogma_model, DogmaPerspectiveModel)
    assert bundle.dogma_model.detector_id == "dummy"
    assert bundle.dogma_model.language == "python"
    assert bundle.dogma_model.dogma_ids == [UniversalDogmaID.UNAMBIGUOUS_NAME.value]
    assert bundle.dogma_model.dogma_rule_map == {
        UniversalDogmaID.UNAMBIGUOUS_NAME.value: ["python-001"],
    }
    assert bundle.dogma_model.dogma_verified_rule_map == {
        UniversalDogmaID.UNAMBIGUOUS_NAME.value: ["python-001"],
    }
    assert bundle.dogma_model.dogma_ids_for_rule("python-001") == [
        UniversalDogmaID.UNAMBIGUOUS_NAME.value,
    ]


def test_registry_bootstrap_from_mappings():
    registry = DetectorRegistry()
    registry.bootstrap_from_mappings()
    registry.bootstrap_from_mappings()

    assert registry.items()
    assert registry.get("analyzer_defaults").language == "python"
    assert (
        registry.get_bundle("analyzer_defaults", "python")
        .require_rule_model()
        .detector_id
        == "analyzer_defaults"
    )


def test_detector_metadata_rule_map_sets_rule_ids():
    metadata = DetectorMetadata(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        language="python",
        rule_map={"python-001": ["*"]},
    )
    assert metadata.rule_ids == ["python-001"]
    assert metadata.rule_dogma_map == {"python-001": []}
    assert metadata.rule_verified_dogma_map == {"python-001": []}


def test_dogma_perspective_model_normalizes_dogma_maps() -> None:
    dogma_model = DogmaPerspectiveModel(
        detector_id="dummy",
        language="python",
        dogma_rule_map={
            UniversalDogmaID.UNAMBIGUOUS_NAME.value: ["python-001"],
        },
        dogma_verified_rule_map={
            UniversalDogmaID.EXPLICIT_INTENT.value: ["python-002"],
        },
    )

    assert dogma_model.dogma_ids == [
        UniversalDogmaID.UNAMBIGUOUS_NAME.value,
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ]
    assert dogma_model.dogma_rule_map == {
        UniversalDogmaID.UNAMBIGUOUS_NAME.value: ["python-001"],
        UniversalDogmaID.EXPLICIT_INTENT.value: [],
    }
    assert dogma_model.dogma_verified_rule_map == {
        UniversalDogmaID.UNAMBIGUOUS_NAME.value: [],
        UniversalDogmaID.EXPLICIT_INTENT.value: ["python-002"],
    }
    assert dogma_model.rule_ids_for_dogma(UniversalDogmaID.UNAMBIGUOUS_NAME.value) == [
        "python-001",
    ]
    assert dogma_model.verified_dogma_ids_for_rule("python-002") == [
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ]


def test_testing_perspective_model_normalizes_testing_maps() -> None:
    testing_model = TestingPerspectiveModel(
        detector_id="dummy",
        language="python",
        testing_rule_map={
            "micro": ["python-001"],
        },
        testing_verified_rule_map={
            "macro": ["python-002"],
        },
    )

    assert testing_model.testing_ids == ["micro", "macro"]
    assert testing_model.testing_rule_map == {
        "micro": ["python-001"],
        "macro": [],
    }
    assert testing_model.testing_verified_rule_map == {
        "micro": [],
        "macro": ["python-002"],
    }
    assert testing_model.rule_ids_for_testing("micro") == ["python-001"]
    assert testing_model.verified_testing_ids_for_rule("python-002") == ["macro"]


def test_projection_perspective_model_normalizes_projection_maps() -> None:
    projection_model = ProjectionPerspectiveModel(
        detector_id="dummy",
        language="python",
        projection_rule_map={
            "go": ["python-001"],
        },
        projection_verified_rule_map={
            "typescript": ["python-002"],
        },
    )

    assert projection_model.projection_ids == ["go", "typescript"]
    assert projection_model.projection_rule_map == {
        "go": ["python-001"],
        "typescript": [],
    }
    assert projection_model.projection_verified_rule_map == {
        "go": [],
        "typescript": ["python-002"],
    }
    assert projection_model.rule_ids_for_projection("go") == ["python-001"]
    assert projection_model.verified_projection_ids_for_rule("python-002") == [
        "typescript",
    ]


def test_rule_binding_defaults_single_family_ids_to_authored_verification() -> None:
    rule = RuleBinding(
        rule_id="python-001",
        testing_ids=["micro"],
        projection_ids=["go"],
    )

    assert rule.verified_testing_ids == ["micro"]
    assert rule.verified_projection_ids == ["go"]


def test_rule_binding_defaults_multi_family_ids_to_unverified_state() -> None:
    rule = RuleBinding(
        rule_id="python-001",
        testing_ids=["micro", "macro"],
        projection_ids=["go", "typescript"],
    )

    assert rule.verified_testing_ids == []
    assert rule.verified_projection_ids == []


def test_rule_binding_builds_testing_and_projection_models() -> None:
    binding = RuleDetectorBinding(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        rules=[
            RuleBinding(
                rule_id="python-001",
                testing_ids=["micro"],
                projection_ids=["go"],
            ),
            RuleBinding(
                rule_id="python-002",
                testing_ids=["macro"],
                verified_testing_ids=["macro"],
                projection_ids=["typescript"],
                verified_projection_ids=["typescript"],
            ),
        ],
    )

    bundle = binding.build_bundle("python")

    assert isinstance(bundle.testing_model, TestingPerspectiveModel)
    assert bundle.testing_model.testing_rule_map == {
        "micro": ["python-001"],
        "macro": ["python-002"],
    }
    assert bundle.testing_model.testing_verified_rule_map == {
        "micro": ["python-001"],
        "macro": ["python-002"],
    }
    assert bundle.testing_model.testing_ids_for_rule("python-002") == ["macro"]
    assert isinstance(bundle.projection_model, ProjectionPerspectiveModel)
    assert bundle.projection_model.projection_rule_map == {
        "go": ["python-001"],
        "typescript": ["python-002"],
    }
    assert bundle.projection_model.projection_verified_rule_map == {
        "go": ["python-001"],
        "typescript": ["python-002"],
    }
    assert bundle.projection_model.projection_ids_for_rule("python-001") == ["go"]
    assert bundle.require_rule_model().rule_ids == ["python-001", "python-002"]


def test_rule_binding_defaults_empty_selectors_to_wildcard() -> None:
    rule = RuleBinding(rule_id="python-001", violation_selectors=[])
    assert rule.violation_selectors == ["*"]


def test_rule_binding_defaults_single_dogma_to_authored_verification() -> None:
    rule = RuleBinding(
        rule_id="python-001",
        dogma_ids=[UniversalDogmaID.UNAMBIGUOUS_NAME.value],
    )

    assert rule.verified_dogma_ids == [UniversalDogmaID.UNAMBIGUOUS_NAME.value]


def test_rule_binding_defaults_multi_dogma_to_unverified_state() -> None:
    rule = RuleBinding(
        rule_id="ruby-007",
        dogma_ids=[
            UniversalDogmaID.RIGHT_ABSTRACTION.value,
            UniversalDogmaID.UNAMBIGUOUS_NAME.value,
        ],
    )

    assert rule.verified_dogma_ids == []


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


def test_bootstrap_from_mappings_builds_bundle_once_and_preserves_it(
    monkeypatch,
    tmp_path,
):
    registry = DetectorRegistry()
    path_cls = importlib.import_module("pathlib").Path
    original_iterdir = path_cls.iterdir
    fake_subdir = tmp_path / "fake_language"
    fake_subdir.mkdir()

    class CountingBinding(NonRuleDetectorBinding):
        build_calls: int = 0

        def build_bundle(self, language: str) -> BindingPerspectiveBundle:
            self.build_calls += 1
            return super().build_bundle(language)

        def to_metadata(self, language: str) -> DetectorMetadata:
            msg = "bootstrap_from_mappings should use build_bundle"
            raise AssertionError(msg)

    binding = CountingBinding(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
    )
    detector_map = LanguageDetectorMap(language="python", bindings=[binding])

    def fake_iterdir(self):
        if self.name in {"languages", "frameworks"}:
            return iter([fake_subdir])
        return original_iterdir(self)

    def fake_import(name):
        if name == "mcp_zen_of_languages.languages.fake_language.mapping":
            return types.SimpleNamespace(DETECTOR_MAP=detector_map)
        error = ModuleNotFoundError(name)
        error.name = name
        raise error

    monkeypatch.setattr(path_cls, "iterdir", fake_iterdir)
    monkeypatch.setattr(importlib, "import_module", fake_import)

    registry.bootstrap_from_mappings()

    assert binding.build_calls == 1
    assert registry.get("dummy").language == "python"
    assert (
        registry.get_bundle("dummy", "python").require_rule_model().detector_id
        == "dummy"
    )


def test_bootstrap_from_mappings_discovers_testing_family_overlays(
    monkeypatch,
    tmp_path,
) -> None:
    registry = DetectorRegistry()
    path_cls = importlib.import_module("pathlib").Path
    original_iterdir = path_cls.iterdir

    language_dir = tmp_path / "python"
    language_dir.mkdir()
    testing_dir = language_dir / "testing"
    testing_dir.mkdir()
    family_dir = testing_dir / "pytest"
    family_dir.mkdir()

    base_map = LanguageDetectorMap(
        language="python",
        bindings=[
            RuleDetectorBinding(
                detector_id="dummy",
                detector_class=DummyDetector,
                config_model=DummyConfig,
                rules=[RuleBinding(rule_id="python-001")],
            ),
        ],
    )
    testing_map = LanguageDetectorMap(
        language="python",
        bindings=[
            RuleDetectorBinding(
                detector_id="dummy",
                detector_class=DummyDetector,
                config_model=DummyConfig,
                rules=[RuleBinding(rule_id="python-001")],
            ),
        ],
    )

    def fake_iterdir(self):
        if self.name in {"languages", "frameworks"}:
            return iter([language_dir] if self.name == "languages" else [])
        if self == testing_dir:
            return iter([family_dir])
        return original_iterdir(self)

    def fake_import(name):
        if name == "mcp_zen_of_languages.languages.python.mapping":
            return types.SimpleNamespace(DETECTOR_MAP=base_map)
        if name == "mcp_zen_of_languages.languages.python.testing.pytest.mapping":
            return types.SimpleNamespace(DETECTOR_MAP=testing_map)
        error = ModuleNotFoundError(name)
        error.name = name
        raise error

    monkeypatch.setattr(path_cls, "iterdir", fake_iterdir)
    monkeypatch.setattr(importlib, "import_module", fake_import)

    registry.bootstrap_from_mappings()

    assert [metadata.detector_id for metadata in registry.items()] == ["dummy"]
    testing_model = registry.get_testing_model("dummy", "python")
    assert isinstance(testing_model, TestingPerspectiveModel)
    assert testing_model.testing_rule_map == {"pytest": ["python-001"]}
    assert testing_model.testing_verified_rule_map == {"pytest": ["python-001"]}
    assert registry.testing_models_for_family("pytest", "python") == [testing_model]
    assert registry.testing_ids_for("dummy", "python", "python-001") == ["pytest"]


def test_registry_preserves_authored_dogma_bundle() -> None:
    registry = DetectorRegistry()
    binding = RuleDetectorBinding(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        rules=[
            RuleBinding(
                rule_id="python-001",
                dogma_ids=[UniversalDogmaID.UNAMBIGUOUS_NAME.value],
                verified_dogma_ids=[UniversalDogmaID.UNAMBIGUOUS_NAME.value],
            ),
        ],
    )

    bundle = binding.build_bundle("python")
    registry.register(bundle.require_rule_model(), bundle=bundle)

    preserved = registry.get_bundle("dummy", "python")
    assert preserved == bundle
    assert isinstance(preserved.dogma_model, DogmaPerspectiveModel)
    assert preserved.dogma_model.dogma_rule_map == {
        UniversalDogmaID.UNAMBIGUOUS_NAME.value: ["python-001"],
    }


def test_registry_dogma_lookup_prefers_preserved_bundle_model() -> None:
    registry = DetectorRegistry()
    metadata = DetectorMetadata(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        language="python",
        rule_ids=["python-001"],
        rule_map={"python-001": ["*"]},
        rule_dogma_map={"python-001": []},
        rule_verified_dogma_map={"python-001": []},
    )
    bundle = BindingPerspectiveBundle(
        rule_model=metadata,
        dogma_model=DogmaPerspectiveModel(
            detector_id="dummy",
            language="python",
            dogma_rule_map={
                UniversalDogmaID.UNAMBIGUOUS_NAME.value: ["python-001"],
            },
            dogma_verified_rule_map={
                UniversalDogmaID.EXPLICIT_INTENT.value: ["python-001"],
            },
        ),
    )

    registry.register(metadata, bundle=bundle)

    assert registry.linked_dogma_ids_for("dummy", "python", "python-001") == [
        UniversalDogmaID.UNAMBIGUOUS_NAME.value,
    ]
    assert registry.verified_dogma_ids_for("dummy", "python", "python-001") == [
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ]
