"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import (
    DetectorBinding,
    LanguageDetectorMap,
)
from mcp_zen_of_languages.languages.configs import (
    JsonArrayOrderConfig,
    JsonDateFormatConfig,
    JsonKeyCasingConfig,
    JsonNullHandlingConfig,
    JsonSchemaConsistencyConfig,
    JsonStrictnessConfig,
)
from mcp_zen_of_languages.languages.json.detectors import (
    JsonArrayOrderDetector,
    JsonDateFormatDetector,
    JsonKeyCasingDetector,
    JsonNullHandlingDetector,
    JsonSchemaConsistencyDetector,
    JsonStrictnessDetector,
)

DETECTOR_MAP = LanguageDetectorMap(
    language="json",
    bindings=[
        DetectorBinding(
            detector_id="json-001",
            detector_class=JsonStrictnessDetector,
            config_model=JsonStrictnessConfig,
            rule_ids=["json-001"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="json-002",
            detector_class=JsonSchemaConsistencyDetector,
            config_model=JsonSchemaConsistencyConfig,
            rule_ids=["json-002"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="json-003",
            detector_class=JsonDateFormatDetector,
            config_model=JsonDateFormatConfig,
            rule_ids=["json-003"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="json-004",
            detector_class=JsonNullHandlingDetector,
            config_model=JsonNullHandlingConfig,
            rule_ids=["json-004"],
            default_order=40,
        ),
        DetectorBinding(
            detector_id="json-005",
            detector_class=JsonKeyCasingDetector,
            config_model=JsonKeyCasingConfig,
            rule_ids=["json-005"],
            default_order=50,
        ),
        DetectorBinding(
            detector_id="json-006",
            detector_class=JsonArrayOrderDetector,
            config_model=JsonArrayOrderConfig,
            rule_ids=["json-006"],
            default_order=60,
        ),
    ],
)
