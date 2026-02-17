"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import (
    DetectorBinding,
    LanguageDetectorMap,
)
from mcp_zen_of_languages.languages.configs import (
    YamlCommentIntentConfig,
    YamlConsistencyConfig,
    YamlDuplicateKeysConfig,
    YamlIndentationConfig,
    YamlKeyClarityConfig,
    YamlLowercaseKeysConfig,
    YamlNoTabsConfig,
    YamlStringStyleConfig,
)
from mcp_zen_of_languages.languages.yaml.detectors import (
    YamlCommentIntentDetector,
    YamlConsistencyDetector,
    YamlDuplicateKeysDetector,
    YamlIndentationDetector,
    YamlKeyClarityDetector,
    YamlLowercaseKeysDetector,
    YamlNoTabsDetector,
    YamlStringStyleDetector,
)

DETECTOR_MAP = LanguageDetectorMap(
    language="yaml",
    bindings=[
        DetectorBinding(
            detector_id="yaml-001",
            detector_class=YamlIndentationDetector,
            config_model=YamlIndentationConfig,
            rule_ids=["yaml-001"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="yaml-002",
            detector_class=YamlNoTabsDetector,
            config_model=YamlNoTabsConfig,
            rule_ids=["yaml-002"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="yaml-003",
            detector_class=YamlDuplicateKeysDetector,
            config_model=YamlDuplicateKeysConfig,
            rule_ids=["yaml-003"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="yaml-004",
            detector_class=YamlLowercaseKeysDetector,
            config_model=YamlLowercaseKeysConfig,
            rule_ids=["yaml-004"],
            default_order=40,
        ),
        DetectorBinding(
            detector_id="yaml-005",
            detector_class=YamlKeyClarityDetector,
            config_model=YamlKeyClarityConfig,
            rule_ids=["yaml-005"],
            default_order=50,
        ),
        DetectorBinding(
            detector_id="yaml-006",
            detector_class=YamlConsistencyDetector,
            config_model=YamlConsistencyConfig,
            rule_ids=["yaml-006"],
            default_order=60,
        ),
        DetectorBinding(
            detector_id="yaml-007",
            detector_class=YamlCommentIntentDetector,
            config_model=YamlCommentIntentConfig,
            rule_ids=["yaml-007"],
            default_order=70,
        ),
        DetectorBinding(
            detector_id="yaml-008",
            detector_class=YamlStringStyleDetector,
            config_model=YamlStringStyleConfig,
            rule_ids=["yaml-008"],
            default_order=80,
        ),
    ],
)
