"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
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


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="cpp",
    bindings=[
        RuleDetectorBinding(
            detector_id="cpp-001",
            detector_class=CppRaiiDetector,
            config_model=CppRaiiConfig,
            rules=[
                RuleBinding(
                    rule_id="cpp-001",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES"),
                    testing_ids=["gtest"],
                    verified_testing_ids=["gtest"],
                    projection_ids=["cpp"],
                    verified_projection_ids=["cpp"],
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="cpp-003",
            detector_class=CppAutoDetector,
            config_model=CppAutoConfig,
            rules=[
                RuleBinding(
                    rule_id="cpp-003", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="cpp-005",
            detector_class=CppRangeForDetector,
            config_model=CppRangeForConfig,
            rules=[
                RuleBinding(
                    rule_id="cpp-005", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="cpp-006",
            detector_class=CppManualAllocationDetector,
            config_model=CppManualAllocationConfig,
            rules=[
                RuleBinding(rule_id="cpp-006", dogma_ids=_dogmas("ZEN-VISIBLE-STATE"))
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="cpp-007",
            detector_class=CppConstCorrectnessDetector,
            config_model=CppConstCorrectnessConfig,
            rules=[
                RuleBinding(rule_id="cpp-007", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="cpp-008",
            detector_class=CppCStyleCastDetector,
            config_model=CppCStyleCastConfig,
            rules=[
                RuleBinding(rule_id="cpp-008", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="cpp-009",
            detector_class=CppRuleOfFiveDetector,
            config_model=CppRuleOfFiveConfig,
            rules=[
                RuleBinding(
                    rule_id="cpp-009", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="cpp-010",
            detector_class=CppMoveDetector,
            config_model=CppMoveConfig,
            rules=[
                RuleBinding(
                    rule_id="cpp-010", dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY")
                )
            ],
            default_order=80,
        ),
        RuleDetectorBinding(
            detector_id="cpp-011",
            detector_class=CppAvoidGlobalsDetector,
            config_model=CppAvoidGlobalsConfig,
            rules=[
                RuleBinding(
                    rule_id="cpp-011",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-VISIBLE-STATE"),
                )
            ],
            default_order=90,
        ),
        RuleDetectorBinding(
            detector_id="cpp-012",
            detector_class=CppOverrideFinalDetector,
            config_model=CppOverrideFinalConfig,
            rules=[
                RuleBinding(rule_id="cpp-012", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=100,
        ),
        RuleDetectorBinding(
            detector_id="cpp-013",
            detector_class=CppOptionalDetector,
            config_model=CppOptionalConfig,
            rules=[
                RuleBinding(
                    rule_id="cpp-013", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=110,
        ),
        RuleDetectorBinding(
            detector_id="cpp_nullptr",
            detector_class=CppNullptrDetector,
            config_model=CppNullptrConfig,
            rules=[
                RuleBinding(rule_id="cpp-004", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=120,
        ),
        RuleDetectorBinding(
            detector_id="cpp_smart_pointers",
            detector_class=CppSmartPointerDetector,
            config_model=CppSmartPointerConfig,
            rules=[
                RuleBinding(
                    rule_id="cpp-002",
                    dogma_ids=_dogmas("ZEN-VISIBLE-STATE"),
                    testing_ids=["gtest"],
                    verified_testing_ids=["gtest"],
                    projection_ids=["cpp"],
                    verified_projection_ids=["cpp"],
                )
            ],
            default_order=130,
        ),
    ],
)
