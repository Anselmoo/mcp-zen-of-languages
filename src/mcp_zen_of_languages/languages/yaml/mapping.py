"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.languages.configs import YamlCommentIntentConfig
from mcp_zen_of_languages.languages.configs import YamlConsistencyConfig
from mcp_zen_of_languages.languages.configs import YamlDuplicateKeysConfig
from mcp_zen_of_languages.languages.configs import YamlIndentationConfig
from mcp_zen_of_languages.languages.configs import YamlKeyClarityConfig
from mcp_zen_of_languages.languages.configs import YamlLowercaseKeysConfig
from mcp_zen_of_languages.languages.configs import YamlNoTabsConfig
from mcp_zen_of_languages.languages.configs import YamlStringStyleConfig
from mcp_zen_of_languages.languages.yaml.detectors import YamlCommentIntentDetector
from mcp_zen_of_languages.languages.yaml.detectors import YamlConsistencyDetector
from mcp_zen_of_languages.languages.yaml.detectors import YamlDuplicateKeysDetector
from mcp_zen_of_languages.languages.yaml.detectors import YamlIndentationDetector
from mcp_zen_of_languages.languages.yaml.detectors import YamlKeyClarityDetector
from mcp_zen_of_languages.languages.yaml.detectors import YamlLowercaseKeysDetector
from mcp_zen_of_languages.languages.yaml.detectors import YamlNoTabsDetector
from mcp_zen_of_languages.languages.yaml.detectors import YamlStringStyleDetector


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="yaml",
    bindings=[
        RuleDetectorBinding(
            detector_id="yaml-001",
            detector_class=YamlIndentationDetector,
            config_model=YamlIndentationConfig,
            rules=[
                RuleBinding(
                    rule_id="yaml-001", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="yaml-002",
            detector_class=YamlNoTabsDetector,
            config_model=YamlNoTabsConfig,
            rules=[
                RuleBinding(
                    rule_id="yaml-002", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="yaml-003",
            detector_class=YamlDuplicateKeysDetector,
            config_model=YamlDuplicateKeysConfig,
            rules=[
                RuleBinding(
                    rule_id="yaml-003", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="yaml-004",
            detector_class=YamlLowercaseKeysDetector,
            config_model=YamlLowercaseKeysConfig,
            rules=[
                RuleBinding(
                    rule_id="yaml-004", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="yaml-005",
            detector_class=YamlKeyClarityDetector,
            config_model=YamlKeyClarityConfig,
            rules=[
                RuleBinding(
                    rule_id="yaml-005", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="yaml-006",
            detector_class=YamlConsistencyDetector,
            config_model=YamlConsistencyConfig,
            rules=[
                RuleBinding(
                    rule_id="yaml-006", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="yaml-007",
            detector_class=YamlCommentIntentDetector,
            config_model=YamlCommentIntentConfig,
            rules=[
                RuleBinding(
                    rule_id="yaml-007", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="yaml-008",
            detector_class=YamlStringStyleDetector,
            config_model=YamlStringStyleConfig,
            rules=[
                RuleBinding(
                    rule_id="yaml-008", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=80,
        ),
    ],
)
