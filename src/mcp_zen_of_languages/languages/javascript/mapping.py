"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.languages.configs import Js009Config
from mcp_zen_of_languages.languages.configs import Js011Config
from mcp_zen_of_languages.languages.configs import JsAsyncErrorHandlingConfig
from mcp_zen_of_languages.languages.configs import JsCallbackNestingConfig
from mcp_zen_of_languages.languages.configs import JsDestructuringConfig
from mcp_zen_of_languages.languages.configs import JsFunctionLengthConfig
from mcp_zen_of_languages.languages.configs import JsGlobalStateConfig
from mcp_zen_of_languages.languages.configs import JsMagicNumbersConfig
from mcp_zen_of_languages.languages.configs import JsModernFeaturesConfig
from mcp_zen_of_languages.languages.configs import JsNoArgumentsConfig
from mcp_zen_of_languages.languages.configs import JsNoEvalConfig
from mcp_zen_of_languages.languages.configs import JsNoPrototypeMutationConfig
from mcp_zen_of_languages.languages.configs import JsNoVarConfig
from mcp_zen_of_languages.languages.configs import JsNoWithConfig
from mcp_zen_of_languages.languages.configs import JsObjectSpreadConfig
from mcp_zen_of_languages.languages.configs import JsParamCountConfig
from mcp_zen_of_languages.languages.configs import JsPureFunctionConfig
from mcp_zen_of_languages.languages.configs import JsStrictEqualityConfig
from mcp_zen_of_languages.languages.javascript.detectors import (
    JsAsyncErrorHandlingDetector,
)
from mcp_zen_of_languages.languages.javascript.detectors import (
    JsCallbackNestingDetector,
)
from mcp_zen_of_languages.languages.javascript.detectors import JsDestructuringDetector
from mcp_zen_of_languages.languages.javascript.detectors import JsFunctionLengthDetector
from mcp_zen_of_languages.languages.javascript.detectors import JsGlobalStateDetector
from mcp_zen_of_languages.languages.javascript.detectors import (
    JsInheritanceDepthDetector,
)
from mcp_zen_of_languages.languages.javascript.detectors import JsMagicNumbersDetector
from mcp_zen_of_languages.languages.javascript.detectors import (
    JsMeaningfulNamesDetector,
)
from mcp_zen_of_languages.languages.javascript.detectors import JsModernFeaturesDetector
from mcp_zen_of_languages.languages.javascript.detectors import JsNoArgumentsDetector
from mcp_zen_of_languages.languages.javascript.detectors import JsNoEvalDetector
from mcp_zen_of_languages.languages.javascript.detectors import (
    JsNoPrototypeMutationDetector,
)
from mcp_zen_of_languages.languages.javascript.detectors import JsNoVarDetector
from mcp_zen_of_languages.languages.javascript.detectors import JsNoWithDetector
from mcp_zen_of_languages.languages.javascript.detectors import JsObjectSpreadDetector
from mcp_zen_of_languages.languages.javascript.detectors import JsParamCountDetector
from mcp_zen_of_languages.languages.javascript.detectors import JsPureFunctionDetector
from mcp_zen_of_languages.languages.javascript.detectors import JsStrictEqualityDetector


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="javascript",
    bindings=[
        RuleDetectorBinding(
            detector_id="js_callback_nesting",
            detector_class=JsCallbackNestingDetector,
            config_model=JsCallbackNestingConfig,
            rules=[
                RuleBinding(
                    rule_id="js-001",
                    dogma_ids=_dogmas("ZEN-FAIL-FAST", "ZEN-RETURN-EARLY"),
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="js_no_var",
            detector_class=JsNoVarDetector,
            config_model=JsNoVarConfig,
            rules=[
                RuleBinding(rule_id="js-002", dogma_ids=_dogmas("ZEN-VISIBLE-STATE"))
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="js_strict_equality",
            detector_class=JsStrictEqualityDetector,
            config_model=JsStrictEqualityConfig,
            rules=[
                RuleBinding(rule_id="js-003", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="js_async_error_handling",
            detector_class=JsAsyncErrorHandlingDetector,
            config_model=JsAsyncErrorHandlingConfig,
            rules=[
                RuleBinding(
                    rule_id="js-007",
                    dogma_ids=_dogmas("ZEN-FAIL-FAST", "ZEN-EXPLICIT-INTENT"),
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="js_function_length",
            detector_class=JsFunctionLengthDetector,
            config_model=JsFunctionLengthConfig,
            rules=[
                RuleBinding(
                    rule_id="js-005", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="js_global_state",
            detector_class=JsGlobalStateDetector,
            config_model=JsGlobalStateConfig,
            rules=[
                RuleBinding(
                    rule_id="js-004",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-VISIBLE-STATE"),
                )
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="js_modern_features",
            detector_class=JsModernFeaturesDetector,
            config_model=JsModernFeaturesConfig,
            rules=[
                RuleBinding(
                    rule_id="js-006", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="js_magic_numbers",
            detector_class=JsMagicNumbersDetector,
            config_model=JsMagicNumbersConfig,
            rules=[
                RuleBinding(
                    rule_id="js-008",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-UNAMBIGUOUS-NAME"),
                )
            ],
            default_order=80,
        ),
        RuleDetectorBinding(
            detector_id="js-009",
            detector_class=JsInheritanceDepthDetector,
            config_model=Js009Config,
            rules=[
                RuleBinding(
                    rule_id="js-009", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=90,
        ),
        RuleDetectorBinding(
            detector_id="js_pure_functions",
            detector_class=JsPureFunctionDetector,
            config_model=JsPureFunctionConfig,
            rules=[
                RuleBinding(
                    rule_id="js-010",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-VISIBLE-STATE"),
                )
            ],
            default_order=100,
        ),
        RuleDetectorBinding(
            detector_id="js-011",
            detector_class=JsMeaningfulNamesDetector,
            config_model=Js011Config,
            rules=[
                RuleBinding(rule_id="js-011", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME"))
            ],
            default_order=110,
        ),
        RuleDetectorBinding(
            detector_id="js_destructuring",
            detector_class=JsDestructuringDetector,
            config_model=JsDestructuringConfig,
            rules=[
                RuleBinding(
                    rule_id="js-012", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=120,
        ),
        RuleDetectorBinding(
            detector_id="js_object_spread",
            detector_class=JsObjectSpreadDetector,
            config_model=JsObjectSpreadConfig,
            rules=[
                RuleBinding(
                    rule_id="js-013", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=130,
        ),
        RuleDetectorBinding(
            detector_id="js_no_with",
            detector_class=JsNoWithDetector,
            config_model=JsNoWithConfig,
            rules=[
                RuleBinding(
                    rule_id="js-014",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-VISIBLE-STATE"),
                )
            ],
            default_order=140,
        ),
        RuleDetectorBinding(
            detector_id="js_param_count",
            detector_class=JsParamCountDetector,
            config_model=JsParamCountConfig,
            rules=[
                RuleBinding(
                    rule_id="js-015", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=150,
        ),
        RuleDetectorBinding(
            detector_id="js_no_eval",
            detector_class=JsNoEvalDetector,
            config_model=JsNoEvalConfig,
            rules=[
                RuleBinding(rule_id="js-016", dogma_ids=_dogmas("ZEN-STRICT-FENCES"))
            ],
            default_order=160,
        ),
        RuleDetectorBinding(
            detector_id="js_no_arguments",
            detector_class=JsNoArgumentsDetector,
            config_model=JsNoArgumentsConfig,
            rules=[
                RuleBinding(
                    rule_id="js-017",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-UTILIZE-ARGUMENTS"),
                )
            ],
            default_order=170,
        ),
        RuleDetectorBinding(
            detector_id="js_no_prototype_mutation",
            detector_class=JsNoPrototypeMutationDetector,
            config_model=JsNoPrototypeMutationConfig,
            rules=[
                RuleBinding(
                    rule_id="js-018", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=180,
        ),
    ],
)
