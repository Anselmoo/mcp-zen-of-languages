"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.languages.configs import SvgAbsolutePathOnlyConfig
from mcp_zen_of_languages.languages.configs import SvgAriaRoleConfig
from mcp_zen_of_languages.languages.configs import SvgBase64ImageConfig
from mcp_zen_of_languages.languages.configs import SvgDeprecatedXlinkHrefConfig
from mcp_zen_of_languages.languages.configs import SvgDescForComplexGraphicsConfig
from mcp_zen_of_languages.languages.configs import SvgDuplicateIdConfig
from mcp_zen_of_languages.languages.configs import SvgImageAltConfig
from mcp_zen_of_languages.languages.configs import SvgInlineStyleConfig
from mcp_zen_of_languages.languages.configs import SvgMissingTitleConfig
from mcp_zen_of_languages.languages.configs import SvgNestedGroupsConfig
from mcp_zen_of_languages.languages.configs import SvgNodeCountConfig
from mcp_zen_of_languages.languages.configs import SvgProductionBloatConfig
from mcp_zen_of_languages.languages.configs import SvgUnusedDefsConfig
from mcp_zen_of_languages.languages.configs import SvgViewBoxConfig
from mcp_zen_of_languages.languages.configs import SvgXmlnsConfig
from mcp_zen_of_languages.languages.svg.detectors import SvgAbsolutePathOnlyDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgAriaRoleDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgBase64ImageDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgDeprecatedXlinkHrefDetector
from mcp_zen_of_languages.languages.svg.detectors import (
    SvgDescForComplexGraphicsDetector,
)
from mcp_zen_of_languages.languages.svg.detectors import SvgDuplicateIdDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgImageAltDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgInlineStyleDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgMissingTitleDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgNestedGroupsDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgNodeCountDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgProductionBloatDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgUnusedDefsDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgViewBoxDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgXmlnsDetector


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="svg",
    bindings=[
        RuleDetectorBinding(
            detector_id="svg-001",
            detector_class=SvgMissingTitleDetector,
            config_model=SvgMissingTitleConfig,
            rules=[
                RuleBinding(
                    rule_id="svg-001", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="svg-002",
            detector_class=SvgAriaRoleDetector,
            config_model=SvgAriaRoleConfig,
            rules=[
                RuleBinding(
                    rule_id="svg-002", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="svg-003",
            detector_class=SvgImageAltDetector,
            config_model=SvgImageAltConfig,
            rules=[
                RuleBinding(
                    rule_id="svg-003", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="svg-004",
            detector_class=SvgDescForComplexGraphicsDetector,
            config_model=SvgDescForComplexGraphicsConfig,
            rules=[
                RuleBinding(
                    rule_id="svg-004", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="svg-005",
            detector_class=SvgInlineStyleDetector,
            config_model=SvgInlineStyleConfig,
            rules=[
                RuleBinding(
                    rule_id="svg-005",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
                    projection_ids=["react", "nextjs", "vue"],
                    verified_projection_ids=["react"],
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="svg-006",
            detector_class=SvgViewBoxDetector,
            config_model=SvgViewBoxConfig,
            rules=[
                RuleBinding(rule_id="svg-006", dogma_ids=_dogmas("ZEN-RETURN-EARLY"))
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="svg-007",
            detector_class=SvgUnusedDefsDetector,
            config_model=SvgUnusedDefsConfig,
            rules=[
                RuleBinding(
                    rule_id="svg-007",
                    dogma_ids=_dogmas(
                        "ZEN-STRICT-FENCES",
                        "ZEN-PROPORTIONATE-COMPLEXITY",
                        "ZEN-RUTHLESS-DELETION",
                    ),
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="svg-008",
            detector_class=SvgNestedGroupsDetector,
            config_model=SvgNestedGroupsConfig,
            rules=[
                RuleBinding(
                    rule_id="svg-008",
                    dogma_ids=_dogmas(
                        "ZEN-PROPORTIONATE-COMPLEXITY", "ZEN-RETURN-EARLY"
                    ),
                )
            ],
            default_order=80,
        ),
        RuleDetectorBinding(
            detector_id="svg-009",
            detector_class=SvgDuplicateIdDetector,
            config_model=SvgDuplicateIdConfig,
            rules=[
                RuleBinding(rule_id="svg-009", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=90,
        ),
        RuleDetectorBinding(
            detector_id="svg-010",
            detector_class=SvgAbsolutePathOnlyDetector,
            config_model=SvgAbsolutePathOnlyConfig,
            rules=[
                RuleBinding(
                    rule_id="svg-010", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=100,
        ),
        RuleDetectorBinding(
            detector_id="svg-011",
            detector_class=SvgBase64ImageDetector,
            config_model=SvgBase64ImageConfig,
            rules=[
                RuleBinding(
                    rule_id="svg-011", dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY")
                )
            ],
            default_order=110,
        ),
        RuleDetectorBinding(
            detector_id="svg-012",
            detector_class=SvgXmlnsDetector,
            config_model=SvgXmlnsConfig,
            rules=[
                RuleBinding(
                    rule_id="svg-012",
                    dogma_ids=_dogmas(
                        "ZEN-EXPLICIT-INTENT",
                        "ZEN-UNAMBIGUOUS-NAME",
                        "ZEN-STRICT-FENCES",
                    ),
                    testing_ids=["xmllint"],
                    verified_testing_ids=["xmllint"],
                    projection_ids=["react", "nextjs", "vue"],
                    verified_projection_ids=["react", "nextjs"],
                )
            ],
            default_order=120,
        ),
        RuleDetectorBinding(
            detector_id="svg-013",
            detector_class=SvgDeprecatedXlinkHrefDetector,
            config_model=SvgDeprecatedXlinkHrefConfig,
            rules=[
                RuleBinding(
                    rule_id="svg-013", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=130,
        ),
        RuleDetectorBinding(
            detector_id="svg-014",
            detector_class=SvgNodeCountDetector,
            config_model=SvgNodeCountConfig,
            rules=[
                RuleBinding(
                    rule_id="svg-014", dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY")
                )
            ],
            default_order=140,
        ),
        RuleDetectorBinding(
            detector_id="svg-015",
            detector_class=SvgProductionBloatDetector,
            config_model=SvgProductionBloatConfig,
            rules=[
                RuleBinding(
                    rule_id="svg-015",
                    dogma_ids=_dogmas(
                        "ZEN-PROPORTIONATE-COMPLEXITY",
                        "ZEN-UNAMBIGUOUS-NAME",
                        "ZEN-STRICT-FENCES",
                    ),
                )
            ],
            default_order=150,
        ),
    ],
)
