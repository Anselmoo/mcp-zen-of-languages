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


# ---------------------------------------------------------------------------
# frameworks/base.py — uncovered helpers
# ---------------------------------------------------------------------------


def test_is_framework_key_true_for_react() -> None:
    from mcp_zen_of_languages.frameworks.base import is_framework_key

    assert is_framework_key("react") is True


def test_is_framework_key_false_for_python() -> None:
    from mcp_zen_of_languages.frameworks.base import is_framework_key

    assert is_framework_key("python") is False


def test_module_prefix_for_framework_key() -> None:
    from mcp_zen_of_languages.frameworks.base import module_prefix_for_language

    assert module_prefix_for_language("react") == "frameworks"


def test_module_prefix_for_language_key() -> None:
    from mcp_zen_of_languages.frameworks.base import module_prefix_for_language

    assert module_prefix_for_language("python") == "languages"


def test_module_import_path_framework() -> None:
    from mcp_zen_of_languages.frameworks.base import module_import_path

    path = module_import_path("react", "rules")
    assert path == "mcp_zen_of_languages.frameworks.react.rules"


def test_module_import_path_language() -> None:
    from mcp_zen_of_languages.frameworks.base import module_import_path

    path = module_import_path("python", "detectors")
    assert path == "mcp_zen_of_languages.languages.python.detectors"


# ---------------------------------------------------------------------------
# frameworks/dogmas.py — ValueError on unknown rule id
# ---------------------------------------------------------------------------


def test_framework_rule_dogmas_raises_for_unknown_rule() -> None:
    import pytest

    from mcp_zen_of_languages.frameworks.dogmas import framework_rule_dogmas

    with pytest.raises(ValueError, match="Unknown framework rule id"):
        framework_rule_dogmas("nonexistent-999")


def test_framework_rule_dogmas_returns_tuple_for_known_rule() -> None:
    from mcp_zen_of_languages.frameworks.dogmas import framework_rule_dogmas

    result = framework_rule_dogmas("react-001")
    assert isinstance(result, tuple)
    assert len(result) >= 1


# ---------------------------------------------------------------------------
# frameworks/detector_base.py — default dispatch and custom handler path
# ---------------------------------------------------------------------------


def test_framework_rule_detector_base_default_rule_handlers() -> None:
    from mcp_zen_of_languages.analyzers.base import AnalysisContext
    from mcp_zen_of_languages.frameworks.detector_base import FrameworkRuleDetectorBase
    from mcp_zen_of_languages.languages.configs import DetectorConfig

    class _Bare(FrameworkRuleDetectorBase):
        pass

    detector = _Bare()
    config = DetectorConfig(type="no-such-rule", principle="test")
    context = AnalysisContext(code="x = 1", language="python")

    violations = detector.detect(context, config)
    assert violations == []


def test_framework_rule_detector_base_custom_handler_called() -> None:
    from mcp_zen_of_languages.analyzers.base import AnalysisContext
    from mcp_zen_of_languages.frameworks.detector_base import FrameworkRuleDetectorBase
    from mcp_zen_of_languages.languages.configs import DetectorConfig

    class _WithHandler(FrameworkRuleDetectorBase):
        def _rule_handlers(self):
            return {"custom-rule": lambda ctx, cfg: []}

    detector = _WithHandler()
    config = DetectorConfig(type="custom-rule", principle="test")
    context = AnalysisContext(code="x = 1", language="python")

    violations = detector.detect(context, config)
    assert violations == []
