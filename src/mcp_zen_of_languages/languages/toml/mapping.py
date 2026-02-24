"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import (
    DetectorBinding,
    LanguageDetectorMap,
)
from mcp_zen_of_languages.core.universal_dogmas import DOGMA_RULE_IDS
from mcp_zen_of_languages.languages.configs import (
    TomlCommentClarityConfig,
    TomlDuplicateKeysConfig,
    TomlFloatIntegerConfig,
    TomlIsoDatetimeConfig,
    TomlLowercaseKeysConfig,
    TomlNoInlineTablesConfig,
    TomlOrderConfig,
    TomlTrailingCommasConfig,
)
from mcp_zen_of_languages.languages.toml.detectors import (
    TomlCommentClarityDetector,
    TomlDuplicateKeysDetector,
    TomlFloatIntegerDetector,
    TomlIsoDatetimeDetector,
    TomlLowercaseKeysDetector,
    TomlNoInlineTablesDetector,
    TomlOrderDetector,
    TomlTrailingCommasDetector,
)

FULL_DOGMA_IDS = list(DOGMA_RULE_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="toml",
    bindings=[
        DetectorBinding(
            detector_id="toml-001",
            detector_class=TomlNoInlineTablesDetector,
            config_model=TomlNoInlineTablesConfig,
            rule_ids=["toml-001"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=10,
        ),
        DetectorBinding(
            detector_id="toml-002",
            detector_class=TomlDuplicateKeysDetector,
            config_model=TomlDuplicateKeysConfig,
            rule_ids=["toml-002"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=20,
        ),
        DetectorBinding(
            detector_id="toml-003",
            detector_class=TomlLowercaseKeysDetector,
            config_model=TomlLowercaseKeysConfig,
            rule_ids=["toml-003"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=30,
        ),
        DetectorBinding(
            detector_id="toml-004",
            detector_class=TomlTrailingCommasDetector,
            config_model=TomlTrailingCommasConfig,
            rule_ids=["toml-004"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=40,
        ),
        DetectorBinding(
            detector_id="toml-005",
            detector_class=TomlCommentClarityDetector,
            config_model=TomlCommentClarityConfig,
            rule_ids=["toml-005"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=50,
        ),
        DetectorBinding(
            detector_id="toml-006",
            detector_class=TomlOrderDetector,
            config_model=TomlOrderConfig,
            rule_ids=["toml-006"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=60,
        ),
        DetectorBinding(
            detector_id="toml-007",
            detector_class=TomlIsoDatetimeDetector,
            config_model=TomlIsoDatetimeConfig,
            rule_ids=["toml-007"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=70,
        ),
        DetectorBinding(
            detector_id="toml-008",
            detector_class=TomlFloatIntegerDetector,
            config_model=TomlFloatIntegerConfig,
            rule_ids=["toml-008"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=80,
        ),
    ],
)
