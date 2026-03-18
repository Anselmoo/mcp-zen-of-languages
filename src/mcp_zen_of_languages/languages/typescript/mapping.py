"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
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


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="typescript",
    bindings=[
        RuleDetectorBinding(
            detector_id="ts_any_usage",
            detector_class=TsAnyUsageDetector,
            config_model=TsAnyUsageConfig,
            rules=[
                RuleBinding(rule_id="ts-001", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="ts_async_await",
            detector_class=TsAsyncAwaitDetector,
            config_model=TsAsyncAwaitConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-013",
                    dogma_ids=_dogmas("ZEN-FAIL-FAST", "ZEN-RETURN-EARLY"),
                    testing_ids=["jest"],
                    verified_testing_ids=["jest"],
                    projection_ids=["angular", "nextjs", "vue"],
                    verified_projection_ids=["nextjs"],
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="ts_catch_all_types",
            detector_class=TsCatchAllTypeDetector,
            config_model=TsCatchAllTypeConfig,
            rules=[
                RuleBinding(rule_id="ts-015", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="ts_console_usage",
            detector_class=TsConsoleUsageDetector,
            config_model=TsConsoleUsageConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-016",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-FAIL-FAST"),
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="ts_default_exports",
            detector_class=TsDefaultExportDetector,
            config_model=TsDefaultExportConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-014",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-UNAMBIGUOUS-NAME"),
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="ts_enum_const",
            detector_class=TsEnumConstDetector,
            config_model=TsEnumConstConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-009", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="ts_for_of",
            detector_class=TsForOfDetector,
            config_model=TsForOfConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-012",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-FAIL-FAST"),
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="ts_import_order",
            detector_class=TsImportOrderDetector,
            config_model=TsImportOrderConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-017", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=80,
        ),
        RuleDetectorBinding(
            detector_id="ts_index_loops",
            detector_class=TsIndexLoopDetector,
            config_model=TsIndexLoopConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-012",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-FAIL-FAST"),
                )
            ],
            default_order=90,
        ),
        RuleDetectorBinding(
            detector_id="ts_interface_preference",
            detector_class=TsInterfacePreferenceDetector,
            config_model=TsInterfacePreferenceConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-003",
                    dogma_ids=_dogmas(
                        "ZEN-RIGHT-ABSTRACTION",
                        "ZEN-UNAMBIGUOUS-NAME",
                        "ZEN-PROPORTIONATE-COMPLEXITY",
                    ),
                    testing_ids=["jest"],
                    verified_testing_ids=["jest"],
                    projection_ids=["angular", "vue"],
                    verified_projection_ids=["angular"],
                )
            ],
            default_order=100,
        ),
        RuleDetectorBinding(
            detector_id="ts_named_export",
            detector_class=TsNamedExportDetector,
            config_model=TsNamedExportConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-014",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-UNAMBIGUOUS-NAME"),
                )
            ],
            default_order=110,
        ),
        RuleDetectorBinding(
            detector_id="ts_no_console",
            detector_class=TsNoConsoleDetector,
            config_model=TsNoConsoleConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-016",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-FAIL-FAST"),
                )
            ],
            default_order=120,
        ),
        RuleDetectorBinding(
            detector_id="ts_non_null_assertions",
            detector_class=TsNonNullAssertionDetector,
            config_model=TsNonNullAssertionConfig,
            rules=[
                RuleBinding(rule_id="ts-008", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=130,
        ),
        RuleDetectorBinding(
            detector_id="ts_object_type",
            detector_class=TsObjectTypeDetector,
            config_model=TsObjectTypeConfig,
            rules=[
                RuleBinding(rule_id="ts-015", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=140,
        ),
        RuleDetectorBinding(
            detector_id="ts_optional_chaining",
            detector_class=TsOptionalChainingDetector,
            config_model=TsOptionalChainingConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-011",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-RETURN-EARLY"),
                    testing_ids=["jest"],
                    verified_testing_ids=["jest"],
                    projection_ids=["angular", "nextjs", "vue"],
                    verified_projection_ids=["angular", "nextjs"],
                )
            ],
            default_order=150,
        ),
        RuleDetectorBinding(
            detector_id="ts_promise_chains",
            detector_class=TsPromiseChainDetector,
            config_model=TsPromiseChainConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-013",
                    dogma_ids=_dogmas("ZEN-FAIL-FAST", "ZEN-RETURN-EARLY"),
                )
            ],
            default_order=160,
        ),
        RuleDetectorBinding(
            detector_id="ts_readonly",
            detector_class=TsReadonlyDetector,
            config_model=TsReadonlyConfig,
            rules=[
                RuleBinding(rule_id="ts-005", dogma_ids=_dogmas("ZEN-VISIBLE-STATE"))
            ],
            default_order=170,
        ),
        RuleDetectorBinding(
            detector_id="ts_require_imports",
            detector_class=TsRequireImportDetector,
            config_model=TsRequireImportConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-017", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=180,
        ),
        RuleDetectorBinding(
            detector_id="ts_return_types",
            detector_class=TsReturnTypeDetector,
            config_model=TsReturnTypeConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-004",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-FAIL-FAST"),
                )
            ],
            default_order=190,
        ),
        RuleDetectorBinding(
            detector_id="ts_strict_mode",
            detector_class=TsStrictModeDetector,
            config_model=TsStrictModeConfig,
            rules=[
                RuleBinding(rule_id="ts-002", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=200,
        ),
        RuleDetectorBinding(
            detector_id="ts_string_concats",
            detector_class=TsStringConcatDetector,
            config_model=TsStringConcatConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-018",
                    dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME", "ZEN-FAIL-FAST"),
                )
            ],
            default_order=210,
        ),
        RuleDetectorBinding(
            detector_id="ts_template_literal",
            detector_class=TsTemplateLiteralDetector,
            config_model=TsTemplateLiteralConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-018",
                    dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME", "ZEN-FAIL-FAST"),
                )
            ],
            default_order=220,
        ),
        RuleDetectorBinding(
            detector_id="ts_type_guards",
            detector_class=TsTypeGuardDetector,
            config_model=TsTypeGuardConfig,
            rules=[
                RuleBinding(rule_id="ts-006", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=230,
        ),
        RuleDetectorBinding(
            detector_id="ts_unknown_over_any",
            detector_class=TsUnknownOverAnyDetector,
            config_model=TsUnknownOverAnyConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-010",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-FAIL-FAST"),
                )
            ],
            default_order=240,
        ),
        RuleDetectorBinding(
            detector_id="ts_utility_types",
            detector_class=TsUtilityTypesDetector,
            config_model=TsUtilityTypesConfig,
            rules=[
                RuleBinding(
                    rule_id="ts-007", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=250,
        ),
    ],
)
