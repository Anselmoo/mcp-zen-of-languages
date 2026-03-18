"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
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


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="json",
    bindings=[
        RuleDetectorBinding(
            detector_id="json-001",
            detector_class=JsonStrictnessDetector,
            config_model=JsonStrictnessConfig,
            rules=[
                RuleBinding(
                    rule_id="json-001", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="json-002",
            detector_class=JsonSchemaConsistencyDetector,
            config_model=JsonSchemaConsistencyConfig,
            rules=[
                RuleBinding(
                    rule_id="json-002",
                    dogma_ids=_dogmas("ZEN-RETURN-EARLY"),
                    testing_ids=["jsonschema"],
                    verified_testing_ids=["jsonschema"],
                    projection_ids=["jsonschema", "openapi"],
                    verified_projection_ids=["jsonschema"],
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="json-003",
            detector_class=JsonDuplicateKeyDetector,
            config_model=JsonDuplicateKeyConfig,
            rules=[
                RuleBinding(
                    rule_id="json-003", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="json-004",
            detector_class=JsonMagicStringDetector,
            config_model=JsonMagicStringConfig,
            rules=[
                RuleBinding(
                    rule_id="json-004", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="json-005",
            detector_class=JsonKeyCasingDetector,
            config_model=JsonKeyCasingConfig,
            rules=[
                RuleBinding(
                    rule_id="json-005", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="json-006",
            detector_class=JsonArrayOrderDetector,
            config_model=JsonArrayOrderConfig,
            rules=[
                RuleBinding(rule_id="json-006", dogma_ids=_dogmas("ZEN-RETURN-EARLY"))
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="json-007",
            detector_class=JsonNullSprawlDetector,
            config_model=JsonNullSprawlConfig,
            rules=[
                RuleBinding(
                    rule_id="json-007", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="json-008",
            detector_class=JsonDateFormatDetector,
            config_model=JsonDateFormatConfig,
            rules=[
                RuleBinding(
                    rule_id="json-008",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
                    testing_ids=["jsonschema"],
                    verified_testing_ids=["jsonschema"],
                    projection_ids=["jsonschema", "openapi"],
                    verified_projection_ids=["jsonschema"],
                )
            ],
            default_order=80,
        ),
        RuleDetectorBinding(
            detector_id="json-009",
            detector_class=JsonNullHandlingDetector,
            config_model=JsonNullHandlingConfig,
            rules=[
                RuleBinding(
                    rule_id="json-009",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
                    testing_ids=["jsonschema"],
                    verified_testing_ids=["jsonschema"],
                    projection_ids=["jsonschema", "openapi"],
                    verified_projection_ids=["jsonschema"],
                )
            ],
            default_order=90,
        ),
    ],
)
