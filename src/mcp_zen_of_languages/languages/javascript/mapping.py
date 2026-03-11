"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import DetectorGearbox
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.core.universal_mapping import UNIVERSAL_DETECTOR_MAP
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


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="javascript",
    bindings=[
        DetectorBinding(
            detector_id="js_callback_nesting",
            detector_class=JsCallbackNestingDetector,
            config_model=JsCallbackNestingConfig,
            rule_ids=["js-001"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="js_no_var",
            detector_class=JsNoVarDetector,
            config_model=JsNoVarConfig,
            rule_ids=["js-002"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="js_strict_equality",
            detector_class=JsStrictEqualityDetector,
            config_model=JsStrictEqualityConfig,
            rule_ids=["js-003"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="js_async_error_handling",
            detector_class=JsAsyncErrorHandlingDetector,
            config_model=JsAsyncErrorHandlingConfig,
            rule_ids=["js-007"],
            default_order=40,
        ),
        DetectorBinding(
            detector_id="js_function_length",
            detector_class=JsFunctionLengthDetector,
            config_model=JsFunctionLengthConfig,
            rule_ids=["js-005"],
            default_order=50,
        ),
        DetectorBinding(
            detector_id="js_global_state",
            detector_class=JsGlobalStateDetector,
            config_model=JsGlobalStateConfig,
            rule_ids=["js-004"],
            default_order=60,
        ),
        DetectorBinding(
            detector_id="js_modern_features",
            detector_class=JsModernFeaturesDetector,
            config_model=JsModernFeaturesConfig,
            rule_ids=["js-006"],
            default_order=70,
        ),
        DetectorBinding(
            detector_id="js_magic_numbers",
            detector_class=JsMagicNumbersDetector,
            config_model=JsMagicNumbersConfig,
            rule_ids=["js-008"],
            default_order=80,
        ),
        DetectorBinding(
            detector_id="js-009",
            detector_class=JsInheritanceDepthDetector,
            config_model=Js009Config,
            rule_ids=["js-009"],
            default_order=90,
        ),
        DetectorBinding(
            detector_id="js_pure_functions",
            detector_class=JsPureFunctionDetector,
            config_model=JsPureFunctionConfig,
            rule_ids=["js-010"],
            default_order=100,
        ),
        DetectorBinding(
            detector_id="js-011",
            detector_class=JsMeaningfulNamesDetector,
            config_model=Js011Config,
            rule_ids=["js-011"],
            default_order=110,
        ),
        DetectorBinding(
            detector_id="js_destructuring",
            detector_class=JsDestructuringDetector,
            config_model=JsDestructuringConfig,
            rule_ids=["js-012"],
            default_order=120,
        ),
        DetectorBinding(
            detector_id="js_object_spread",
            detector_class=JsObjectSpreadDetector,
            config_model=JsObjectSpreadConfig,
            rule_ids=["js-013"],
            default_order=130,
        ),
        DetectorBinding(
            detector_id="js_no_with",
            detector_class=JsNoWithDetector,
            config_model=JsNoWithConfig,
            rule_ids=["js-014"],
            default_order=140,
        ),
        DetectorBinding(
            detector_id="js_param_count",
            detector_class=JsParamCountDetector,
            config_model=JsParamCountConfig,
            rule_ids=["js-015"],
            default_order=150,
        ),
        DetectorBinding(
            detector_id="js_no_eval",
            detector_class=JsNoEvalDetector,
            config_model=JsNoEvalConfig,
            rule_ids=["js-016"],
            default_order=160,
        ),
        DetectorBinding(
            detector_id="js_no_arguments",
            detector_class=JsNoArgumentsDetector,
            config_model=JsNoArgumentsConfig,
            rule_ids=["js-017"],
            default_order=170,
        ),
        DetectorBinding(
            detector_id="js_no_prototype_mutation",
            detector_class=JsNoPrototypeMutationDetector,
            config_model=JsNoPrototypeMutationConfig,
            rule_ids=["js-018"],
            default_order=180,
        ),
    ],
)

GEARBOX = DetectorGearbox(language="javascript")
GEARBOX.extend(DETECTOR_MAP.bindings)
GEARBOX.extend(UNIVERSAL_DETECTOR_MAP.bindings)
DETECTOR_MAP = GEARBOX.build_map()
