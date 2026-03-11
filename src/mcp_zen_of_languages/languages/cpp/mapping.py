"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.languages.configs import CppAutoConfig
from mcp_zen_of_languages.languages.configs import CppAvoidGlobalsConfig
from mcp_zen_of_languages.languages.configs import CppCStyleCastConfig
from mcp_zen_of_languages.languages.configs import CppConstCorrectnessConfig
from mcp_zen_of_languages.languages.configs import CppManualAllocationConfig
from mcp_zen_of_languages.languages.configs import CppMoveConfig
from mcp_zen_of_languages.languages.configs import CppNullptrConfig
from mcp_zen_of_languages.languages.configs import CppOptionalConfig
from mcp_zen_of_languages.languages.configs import CppOverrideFinalConfig
from mcp_zen_of_languages.languages.configs import CppRaiiConfig
from mcp_zen_of_languages.languages.configs import CppRangeForConfig
from mcp_zen_of_languages.languages.configs import CppRuleOfFiveConfig
from mcp_zen_of_languages.languages.configs import CppSmartPointerConfig
from mcp_zen_of_languages.languages.cpp.detectors import CppAutoDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppAvoidGlobalsDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppCStyleCastDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppConstCorrectnessDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppManualAllocationDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppMoveDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppNullptrDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppOptionalDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppOverrideFinalDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppRaiiDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppRangeForDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppRuleOfFiveDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppSmartPointerDetector


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="cpp",
    bindings=[
        DetectorBinding(
            detector_id="cpp_smart_pointers",
            detector_class=CppSmartPointerDetector,
            config_model=CppSmartPointerConfig,
            rule_ids=["cpp-002"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=10,
        ),
        DetectorBinding(
            detector_id="cpp_nullptr",
            detector_class=CppNullptrDetector,
            config_model=CppNullptrConfig,
            rule_ids=["cpp-004"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=20,
        ),
        DetectorBinding(
            detector_id="cpp-001",
            detector_class=CppRaiiDetector,
            config_model=CppRaiiConfig,
            rule_ids=["cpp-001"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=5,
        ),
        DetectorBinding(
            detector_id="cpp-003",
            detector_class=CppAutoDetector,
            config_model=CppAutoConfig,
            rule_ids=["cpp-003"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=15,
        ),
        DetectorBinding(
            detector_id="cpp-005",
            detector_class=CppRangeForDetector,
            config_model=CppRangeForConfig,
            rule_ids=["cpp-005"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=25,
        ),
        DetectorBinding(
            detector_id="cpp-006",
            detector_class=CppManualAllocationDetector,
            config_model=CppManualAllocationConfig,
            rule_ids=["cpp-006"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=35,
        ),
        DetectorBinding(
            detector_id="cpp-007",
            detector_class=CppConstCorrectnessDetector,
            config_model=CppConstCorrectnessConfig,
            rule_ids=["cpp-007"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=45,
        ),
        DetectorBinding(
            detector_id="cpp-008",
            detector_class=CppCStyleCastDetector,
            config_model=CppCStyleCastConfig,
            rule_ids=["cpp-008"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=55,
        ),
        DetectorBinding(
            detector_id="cpp-009",
            detector_class=CppRuleOfFiveDetector,
            config_model=CppRuleOfFiveConfig,
            rule_ids=["cpp-009"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=65,
        ),
        DetectorBinding(
            detector_id="cpp-010",
            detector_class=CppMoveDetector,
            config_model=CppMoveConfig,
            rule_ids=["cpp-010"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=75,
        ),
        DetectorBinding(
            detector_id="cpp-011",
            detector_class=CppAvoidGlobalsDetector,
            config_model=CppAvoidGlobalsConfig,
            rule_ids=["cpp-011"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=85,
        ),
        DetectorBinding(
            detector_id="cpp-012",
            detector_class=CppOverrideFinalDetector,
            config_model=CppOverrideFinalConfig,
            rule_ids=["cpp-012"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=95,
        ),
        DetectorBinding(
            detector_id="cpp-013",
            detector_class=CppOptionalDetector,
            config_model=CppOptionalConfig,
            rule_ids=["cpp-013"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=105,
        ),
    ],
)
