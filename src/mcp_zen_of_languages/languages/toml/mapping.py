"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
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
            rule_ids=["toml-001"],
            universal_dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME"),
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="toml-002",
            detector_class=TomlDuplicateKeysDetector,
            config_model=TomlDuplicateKeysConfig,
            rule_ids=["toml-002"],
            universal_dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="toml-003",
            detector_class=TomlLowercaseKeysDetector,
            config_model=TomlLowercaseKeysConfig,
            rule_ids=["toml-003"],
            universal_dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="toml-004",
            detector_class=TomlTrailingCommasDetector,
            config_model=TomlTrailingCommasConfig,
            rule_ids=["toml-004"],
            universal_dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME"),
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="toml-005",
            detector_class=TomlCommentClarityDetector,
            config_model=TomlCommentClarityConfig,
            rule_ids=["toml-005"],
            universal_dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="toml-006",
            detector_class=TomlOrderDetector,
            config_model=TomlOrderConfig,
            rule_ids=["toml-006"],
            universal_dogma_ids=_dogmas("ZEN-STRICT-FENCES"),
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="toml-007",
            detector_class=TomlIsoDatetimeDetector,
            config_model=TomlIsoDatetimeConfig,
            rule_ids=["toml-007"],
            universal_dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="toml-008",
            detector_class=TomlFloatIntegerDetector,
            config_model=TomlFloatIntegerConfig,
            rule_ids=["toml-008"],
            universal_dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
            default_order=80,
        ),
    ],
)
