"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import DOGMA_RULE_IDS
from mcp_zen_of_languages.languages.configs import JsonArrayOrderConfig
from mcp_zen_of_languages.languages.configs import JsonDateFormatConfig
from mcp_zen_of_languages.languages.configs import JsonDuplicateKeyConfig
from mcp_zen_of_languages.languages.configs import JsonKeyCasingConfig
from mcp_zen_of_languages.languages.configs import JsonMagicStringConfig
from mcp_zen_of_languages.languages.configs import JsonNullHandlingConfig
from mcp_zen_of_languages.languages.configs import JsonNullSprawlConfig
from mcp_zen_of_languages.languages.configs import JsonSchemaConsistencyConfig
from mcp_zen_of_languages.languages.configs import JsonStrictnessConfig
from mcp_zen_of_languages.languages.json.detectors import JsonArrayOrderDetector
from mcp_zen_of_languages.languages.json.detectors import JsonDateFormatDetector
from mcp_zen_of_languages.languages.json.detectors import JsonDuplicateKeyDetector
from mcp_zen_of_languages.languages.json.detectors import JsonKeyCasingDetector
from mcp_zen_of_languages.languages.json.detectors import JsonMagicStringDetector
from mcp_zen_of_languages.languages.json.detectors import JsonNullHandlingDetector
from mcp_zen_of_languages.languages.json.detectors import JsonNullSprawlDetector
from mcp_zen_of_languages.languages.json.detectors import JsonSchemaConsistencyDetector
from mcp_zen_of_languages.languages.json.detectors import JsonStrictnessDetector


FULL_DOGMA_IDS = list(DOGMA_RULE_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="json",
    bindings=[
        DetectorBinding(
            detector_id="json-001",
            detector_class=JsonStrictnessDetector,
            config_model=JsonStrictnessConfig,
            rule_ids=["json-001"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=10,
        ),
        DetectorBinding(
            detector_id="json-002",
            detector_class=JsonSchemaConsistencyDetector,
            config_model=JsonSchemaConsistencyConfig,
            rule_ids=["json-002"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=20,
        ),
        DetectorBinding(
            detector_id="json-003",
            detector_class=JsonDuplicateKeyDetector,
            config_model=JsonDuplicateKeyConfig,
            rule_ids=["json-003"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=30,
        ),
        DetectorBinding(
            detector_id="json-004",
            detector_class=JsonMagicStringDetector,
            config_model=JsonMagicStringConfig,
            rule_ids=["json-004"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=40,
        ),
        DetectorBinding(
            detector_id="json-005",
            detector_class=JsonKeyCasingDetector,
            config_model=JsonKeyCasingConfig,
            rule_ids=["json-005"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=50,
        ),
        DetectorBinding(
            detector_id="json-006",
            detector_class=JsonArrayOrderDetector,
            config_model=JsonArrayOrderConfig,
            rule_ids=["json-006"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=60,
        ),
        DetectorBinding(
            detector_id="json-007",
            detector_class=JsonNullSprawlDetector,
            config_model=JsonNullSprawlConfig,
            rule_ids=["json-007"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=70,
        ),
        DetectorBinding(
            detector_id="json-008",
            detector_class=JsonDateFormatDetector,
            config_model=JsonDateFormatConfig,
            rule_ids=["json-008"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=80,
        ),
        DetectorBinding(
            detector_id="json-009",
            detector_class=JsonNullHandlingDetector,
            config_model=JsonNullHandlingConfig,
            rule_ids=["json-009"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=90,
        ),
    ],
)
