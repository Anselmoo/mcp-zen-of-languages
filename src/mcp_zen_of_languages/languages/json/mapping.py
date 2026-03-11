"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import DetectorGearbox
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.core.universal_mapping import UNIVERSAL_DETECTOR_MAP
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


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
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
            detector_class=JsonDuplicateKeyDetector,
            config_model=JsonDuplicateKeyConfig,
            rule_ids=["json-003"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="json-004",
            detector_class=JsonMagicStringDetector,
            config_model=JsonMagicStringConfig,
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
        DetectorBinding(
            detector_id="json-007",
            detector_class=JsonNullSprawlDetector,
            config_model=JsonNullSprawlConfig,
            rule_ids=["json-007"],
            default_order=70,
        ),
        DetectorBinding(
            detector_id="json-008",
            detector_class=JsonDateFormatDetector,
            config_model=JsonDateFormatConfig,
            rule_ids=["json-008"],
            default_order=80,
        ),
        DetectorBinding(
            detector_id="json-009",
            detector_class=JsonNullHandlingDetector,
            config_model=JsonNullHandlingConfig,
            rule_ids=["json-009"],
            default_order=90,
        ),
    ],
)

GEARBOX = DetectorGearbox(language="json")
GEARBOX.extend(DETECTOR_MAP.bindings)
GEARBOX.extend(UNIVERSAL_DETECTOR_MAP.bindings)
DETECTOR_MAP = GEARBOX.build_map()
