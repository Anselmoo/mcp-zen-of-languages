"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import DOGMA_RULE_IDS
from mcp_zen_of_languages.languages.configs import Js009Config
from mcp_zen_of_languages.languages.configs import Js011Config
from mcp_zen_of_languages.languages.configs import JsAsyncErrorHandlingConfig
from mcp_zen_of_languages.languages.configs import JsCallbackNestingConfig
from mcp_zen_of_languages.languages.configs import JsFunctionLengthConfig
from mcp_zen_of_languages.languages.configs import JsGlobalStateConfig
from mcp_zen_of_languages.languages.configs import JsMagicNumbersConfig
from mcp_zen_of_languages.languages.configs import JsModernFeaturesConfig
from mcp_zen_of_languages.languages.configs import JsNoVarConfig
from mcp_zen_of_languages.languages.configs import JsPureFunctionConfig
from mcp_zen_of_languages.languages.configs import JsStrictEqualityConfig
from mcp_zen_of_languages.languages.javascript.detectors import (
    JsAsyncErrorHandlingDetector,
)
from mcp_zen_of_languages.languages.javascript.detectors import (
    JsCallbackNestingDetector,
)
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
from mcp_zen_of_languages.languages.javascript.detectors import JsNoVarDetector
from mcp_zen_of_languages.languages.javascript.detectors import JsPureFunctionDetector
from mcp_zen_of_languages.languages.javascript.detectors import JsStrictEqualityDetector


FULL_DOGMA_IDS = list(DOGMA_RULE_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="javascript",
    bindings=[
        DetectorBinding(
            detector_id="js_callback_nesting",
            detector_class=JsCallbackNestingDetector,
            config_model=JsCallbackNestingConfig,
            rule_ids=["js-001"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=10,
        ),
        DetectorBinding(
            detector_id="js_no_var",
            detector_class=JsNoVarDetector,
            config_model=JsNoVarConfig,
            rule_ids=["js-002"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=20,
        ),
        DetectorBinding(
            detector_id="js_strict_equality",
            detector_class=JsStrictEqualityDetector,
            config_model=JsStrictEqualityConfig,
            rule_ids=["js-003"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=30,
        ),
        DetectorBinding(
            detector_id="js_async_error_handling",
            detector_class=JsAsyncErrorHandlingDetector,
            config_model=JsAsyncErrorHandlingConfig,
            rule_ids=["js-007"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=40,
        ),
        DetectorBinding(
            detector_id="js_function_length",
            detector_class=JsFunctionLengthDetector,
            config_model=JsFunctionLengthConfig,
            rule_ids=["js-005"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=50,
        ),
        DetectorBinding(
            detector_id="js_global_state",
            detector_class=JsGlobalStateDetector,
            config_model=JsGlobalStateConfig,
            rule_ids=["js-004"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=60,
        ),
        DetectorBinding(
            detector_id="js_modern_features",
            detector_class=JsModernFeaturesDetector,
            config_model=JsModernFeaturesConfig,
            rule_ids=["js-006"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=70,
        ),
        DetectorBinding(
            detector_id="js_magic_numbers",
            detector_class=JsMagicNumbersDetector,
            config_model=JsMagicNumbersConfig,
            rule_ids=["js-008"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=80,
        ),
        DetectorBinding(
            detector_id="js-009",
            detector_class=JsInheritanceDepthDetector,
            config_model=Js009Config,
            rule_ids=["js-009"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=90,
        ),
        DetectorBinding(
            detector_id="js_pure_functions",
            detector_class=JsPureFunctionDetector,
            config_model=JsPureFunctionConfig,
            rule_ids=["js-010"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=100,
        ),
        DetectorBinding(
            detector_id="js-011",
            detector_class=JsMeaningfulNamesDetector,
            config_model=Js011Config,
            rule_ids=["js-011"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=110,
        ),
    ],
)
