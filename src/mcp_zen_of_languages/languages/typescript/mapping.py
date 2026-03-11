"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import DetectorGearbox
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.core.universal_mapping import UNIVERSAL_DETECTOR_MAP
from mcp_zen_of_languages.languages.configs import TsAnyUsageConfig
from mcp_zen_of_languages.languages.configs import TsAsyncAwaitConfig
from mcp_zen_of_languages.languages.configs import TsCatchAllTypeConfig
from mcp_zen_of_languages.languages.configs import TsConsoleUsageConfig
from mcp_zen_of_languages.languages.configs import TsDefaultExportConfig
from mcp_zen_of_languages.languages.configs import TsEnumConstConfig
from mcp_zen_of_languages.languages.configs import TsForOfConfig
from mcp_zen_of_languages.languages.configs import TsImportOrderConfig
from mcp_zen_of_languages.languages.configs import TsIndexLoopConfig
from mcp_zen_of_languages.languages.configs import TsInterfacePreferenceConfig
from mcp_zen_of_languages.languages.configs import TsNamedExportConfig
from mcp_zen_of_languages.languages.configs import TsNoConsoleConfig
from mcp_zen_of_languages.languages.configs import TsNonNullAssertionConfig
from mcp_zen_of_languages.languages.configs import TsObjectTypeConfig
from mcp_zen_of_languages.languages.configs import TsOptionalChainingConfig
from mcp_zen_of_languages.languages.configs import TsPromiseChainConfig
from mcp_zen_of_languages.languages.configs import TsReadonlyConfig
from mcp_zen_of_languages.languages.configs import TsRequireImportConfig
from mcp_zen_of_languages.languages.configs import TsReturnTypeConfig
from mcp_zen_of_languages.languages.configs import TsStrictModeConfig
from mcp_zen_of_languages.languages.configs import TsStringConcatConfig
from mcp_zen_of_languages.languages.configs import TsTemplateLiteralConfig
from mcp_zen_of_languages.languages.configs import TsTypeGuardConfig
from mcp_zen_of_languages.languages.configs import TsUnknownOverAnyConfig
from mcp_zen_of_languages.languages.configs import TsUtilityTypesConfig
from mcp_zen_of_languages.languages.typescript.detectors import TsAnyUsageDetector
from mcp_zen_of_languages.languages.typescript.detectors import TsAsyncAwaitDetector
from mcp_zen_of_languages.languages.typescript.detectors import TsCatchAllTypeDetector
from mcp_zen_of_languages.languages.typescript.detectors import TsConsoleUsageDetector
from mcp_zen_of_languages.languages.typescript.detectors import TsDefaultExportDetector
from mcp_zen_of_languages.languages.typescript.detectors import TsEnumConstDetector
from mcp_zen_of_languages.languages.typescript.detectors import TsForOfDetector
from mcp_zen_of_languages.languages.typescript.detectors import TsImportOrderDetector
from mcp_zen_of_languages.languages.typescript.detectors import TsIndexLoopDetector
from mcp_zen_of_languages.languages.typescript.detectors import (
    TsInterfacePreferenceDetector,
)
from mcp_zen_of_languages.languages.typescript.detectors import TsNamedExportDetector
from mcp_zen_of_languages.languages.typescript.detectors import TsNoConsoleDetector
from mcp_zen_of_languages.languages.typescript.detectors import (
    TsNonNullAssertionDetector,
)
from mcp_zen_of_languages.languages.typescript.detectors import TsObjectTypeDetector
from mcp_zen_of_languages.languages.typescript.detectors import (
    TsOptionalChainingDetector,
)
from mcp_zen_of_languages.languages.typescript.detectors import TsPromiseChainDetector
from mcp_zen_of_languages.languages.typescript.detectors import TsReadonlyDetector
from mcp_zen_of_languages.languages.typescript.detectors import TsRequireImportDetector
from mcp_zen_of_languages.languages.typescript.detectors import TsReturnTypeDetector
from mcp_zen_of_languages.languages.typescript.detectors import TsStrictModeDetector
from mcp_zen_of_languages.languages.typescript.detectors import TsStringConcatDetector
from mcp_zen_of_languages.languages.typescript.detectors import (
    TsTemplateLiteralDetector,
)
from mcp_zen_of_languages.languages.typescript.detectors import TsTypeGuardDetector
from mcp_zen_of_languages.languages.typescript.detectors import TsUnknownOverAnyDetector
from mcp_zen_of_languages.languages.typescript.detectors import TsUtilityTypesDetector


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="typescript",
    bindings=[
        DetectorBinding(
            detector_id="ts_any_usage",
            detector_class=TsAnyUsageDetector,
            config_model=TsAnyUsageConfig,
            rule_ids=["ts-001"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="ts_strict_mode",
            detector_class=TsStrictModeDetector,
            config_model=TsStrictModeConfig,
            rule_ids=["ts-002"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="ts_interface_preference",
            detector_class=TsInterfacePreferenceDetector,
            config_model=TsInterfacePreferenceConfig,
            rule_ids=["ts-003"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="ts_return_types",
            detector_class=TsReturnTypeDetector,
            config_model=TsReturnTypeConfig,
            rule_ids=["ts-004"],
            default_order=40,
        ),
        DetectorBinding(
            detector_id="ts_readonly",
            detector_class=TsReadonlyDetector,
            config_model=TsReadonlyConfig,
            rule_ids=["ts-005"],
            default_order=50,
        ),
        DetectorBinding(
            detector_id="ts_type_guards",
            detector_class=TsTypeGuardDetector,
            config_model=TsTypeGuardConfig,
            rule_ids=["ts-006"],
            default_order=60,
        ),
        DetectorBinding(
            detector_id="ts_utility_types",
            detector_class=TsUtilityTypesDetector,
            config_model=TsUtilityTypesConfig,
            rule_ids=["ts-007"],
            default_order=70,
        ),
        DetectorBinding(
            detector_id="ts_non_null_assertions",
            detector_class=TsNonNullAssertionDetector,
            config_model=TsNonNullAssertionConfig,
            rule_ids=["ts-008"],
            default_order=80,
        ),
        DetectorBinding(
            detector_id="ts_enum_const",
            detector_class=TsEnumConstDetector,
            config_model=TsEnumConstConfig,
            rule_ids=["ts-009"],
            default_order=90,
        ),
        DetectorBinding(
            detector_id="ts_unknown_over_any",
            detector_class=TsUnknownOverAnyDetector,
            config_model=TsUnknownOverAnyConfig,
            rule_ids=["ts-010"],
            default_order=100,
        ),
        DetectorBinding(
            detector_id="ts_optional_chaining",
            detector_class=TsOptionalChainingDetector,
            config_model=TsOptionalChainingConfig,
            rule_ids=["ts-011"],
            default_order=110,
        ),
        DetectorBinding(
            detector_id="ts_index_loops",
            detector_class=TsIndexLoopDetector,
            config_model=TsIndexLoopConfig,
            rule_ids=["ts-012"],
            default_order=120,
        ),
        DetectorBinding(
            detector_id="ts_promise_chains",
            detector_class=TsPromiseChainDetector,
            config_model=TsPromiseChainConfig,
            rule_ids=["ts-013"],
            default_order=130,
        ),
        DetectorBinding(
            detector_id="ts_default_exports",
            detector_class=TsDefaultExportDetector,
            config_model=TsDefaultExportConfig,
            rule_ids=["ts-014"],
            default_order=140,
        ),
        DetectorBinding(
            detector_id="ts_catch_all_types",
            detector_class=TsCatchAllTypeDetector,
            config_model=TsCatchAllTypeConfig,
            rule_ids=["ts-015"],
            default_order=150,
        ),
        DetectorBinding(
            detector_id="ts_console_usage",
            detector_class=TsConsoleUsageDetector,
            config_model=TsConsoleUsageConfig,
            rule_ids=["ts-016"],
            default_order=160,
        ),
        DetectorBinding(
            detector_id="ts_require_imports",
            detector_class=TsRequireImportDetector,
            config_model=TsRequireImportConfig,
            rule_ids=["ts-017"],
            default_order=170,
        ),
        DetectorBinding(
            detector_id="ts_string_concats",
            detector_class=TsStringConcatDetector,
            config_model=TsStringConcatConfig,
            rule_ids=["ts-018"],
            default_order=180,
        ),
        DetectorBinding(
            detector_id="ts_for_of",
            detector_class=TsForOfDetector,
            config_model=TsForOfConfig,
            rule_ids=["ts-012"],
            default_order=190,
        ),
        DetectorBinding(
            detector_id="ts_async_await",
            detector_class=TsAsyncAwaitDetector,
            config_model=TsAsyncAwaitConfig,
            rule_ids=["ts-013"],
            default_order=200,
        ),
        DetectorBinding(
            detector_id="ts_named_export",
            detector_class=TsNamedExportDetector,
            config_model=TsNamedExportConfig,
            rule_ids=["ts-014"],
            default_order=210,
        ),
        DetectorBinding(
            detector_id="ts_object_type",
            detector_class=TsObjectTypeDetector,
            config_model=TsObjectTypeConfig,
            rule_ids=["ts-015"],
            default_order=220,
        ),
        DetectorBinding(
            detector_id="ts_no_console",
            detector_class=TsNoConsoleDetector,
            config_model=TsNoConsoleConfig,
            rule_ids=["ts-016"],
            default_order=230,
        ),
        DetectorBinding(
            detector_id="ts_import_order",
            detector_class=TsImportOrderDetector,
            config_model=TsImportOrderConfig,
            rule_ids=["ts-017"],
            default_order=240,
        ),
        DetectorBinding(
            detector_id="ts_template_literal",
            detector_class=TsTemplateLiteralDetector,
            config_model=TsTemplateLiteralConfig,
            rule_ids=["ts-018"],
            default_order=250,
        ),
    ],
)

GEARBOX = DetectorGearbox(language="typescript")
GEARBOX.extend(DETECTOR_MAP.bindings)
GEARBOX.extend(UNIVERSAL_DETECTOR_MAP.bindings)
DETECTOR_MAP = GEARBOX.build_map()
