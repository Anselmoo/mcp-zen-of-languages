"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.languages.configs import TomlCommentClarityConfig
from mcp_zen_of_languages.languages.configs import TomlDuplicateKeysConfig
from mcp_zen_of_languages.languages.configs import TomlFloatIntegerConfig
from mcp_zen_of_languages.languages.configs import TomlIsoDatetimeConfig
from mcp_zen_of_languages.languages.configs import TomlLowercaseKeysConfig
from mcp_zen_of_languages.languages.configs import TomlNoInlineTablesConfig
from mcp_zen_of_languages.languages.configs import TomlOrderConfig
from mcp_zen_of_languages.languages.configs import TomlTrailingCommasConfig
from mcp_zen_of_languages.languages.toml.detectors import TomlCommentClarityDetector
from mcp_zen_of_languages.languages.toml.detectors import TomlDuplicateKeysDetector
from mcp_zen_of_languages.languages.toml.detectors import TomlFloatIntegerDetector
from mcp_zen_of_languages.languages.toml.detectors import TomlIsoDatetimeDetector
from mcp_zen_of_languages.languages.toml.detectors import TomlLowercaseKeysDetector
from mcp_zen_of_languages.languages.toml.detectors import TomlNoInlineTablesDetector
from mcp_zen_of_languages.languages.toml.detectors import TomlOrderDetector
from mcp_zen_of_languages.languages.toml.detectors import TomlTrailingCommasDetector


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="toml",
    bindings=[
        RuleDetectorBinding(
            detector_id="toml-001",
            detector_class=TomlNoInlineTablesDetector,
            config_model=TomlNoInlineTablesConfig,
            rules=[
                RuleBinding(
                    rule_id="toml-001", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="toml-002",
            detector_class=TomlDuplicateKeysDetector,
            config_model=TomlDuplicateKeysConfig,
            rules=[
                RuleBinding(
                    rule_id="toml-002",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
                    projection_ids=["python"],
                    verified_projection_ids=["python"],
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="toml-003",
            detector_class=TomlLowercaseKeysDetector,
            config_model=TomlLowercaseKeysConfig,
            rules=[
                RuleBinding(
                    rule_id="toml-003", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="toml-004",
            detector_class=TomlTrailingCommasDetector,
            config_model=TomlTrailingCommasConfig,
            rules=[
                RuleBinding(
                    rule_id="toml-004", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="toml-005",
            detector_class=TomlCommentClarityDetector,
            config_model=TomlCommentClarityConfig,
            rules=[
                RuleBinding(
                    rule_id="toml-005", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="toml-006",
            detector_class=TomlOrderDetector,
            config_model=TomlOrderConfig,
            rules=[
                RuleBinding(rule_id="toml-006", dogma_ids=_dogmas("ZEN-STRICT-FENCES"))
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="toml-007",
            detector_class=TomlIsoDatetimeDetector,
            config_model=TomlIsoDatetimeConfig,
            rules=[
                RuleBinding(
                    rule_id="toml-007",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
                    projection_ids=["python"],
                    verified_projection_ids=["python"],
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="toml-008",
            detector_class=TomlFloatIntegerDetector,
            config_model=TomlFloatIntegerConfig,
            rules=[
                RuleBinding(
                    rule_id="toml-008",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
                    projection_ids=["python"],
                    verified_projection_ids=["python"],
                )
            ],
            default_order=80,
        ),
    ],
)
