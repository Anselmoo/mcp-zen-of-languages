"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import DOGMA_RULE_IDS
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
from mcp_zen_of_languages.languages.svg.detectors import (
    SvgDeprecatedXlinkHrefDetector,
)
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


FULL_DOGMA_IDS = list(DOGMA_RULE_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="svg",
    bindings=[
        DetectorBinding(
            detector_id="svg-001",
            detector_class=SvgMissingTitleDetector,
            config_model=SvgMissingTitleConfig,
            rule_ids=["svg-001"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=10,
        ),
        DetectorBinding(
            detector_id="svg-002",
            detector_class=SvgAriaRoleDetector,
            config_model=SvgAriaRoleConfig,
            rule_ids=["svg-002"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=20,
        ),
        DetectorBinding(
            detector_id="svg-003",
            detector_class=SvgImageAltDetector,
            config_model=SvgImageAltConfig,
            rule_ids=["svg-003"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=30,
        ),
        DetectorBinding(
            detector_id="svg-004",
            detector_class=SvgDescForComplexGraphicsDetector,
            config_model=SvgDescForComplexGraphicsConfig,
            rule_ids=["svg-004"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=40,
        ),
        DetectorBinding(
            detector_id="svg-005",
            detector_class=SvgInlineStyleDetector,
            config_model=SvgInlineStyleConfig,
            rule_ids=["svg-005"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=50,
        ),
        DetectorBinding(
            detector_id="svg-006",
            detector_class=SvgViewBoxDetector,
            config_model=SvgViewBoxConfig,
            rule_ids=["svg-006"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=60,
        ),
        DetectorBinding(
            detector_id="svg-007",
            detector_class=SvgUnusedDefsDetector,
            config_model=SvgUnusedDefsConfig,
            rule_ids=["svg-007"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=70,
        ),
        DetectorBinding(
            detector_id="svg-008",
            detector_class=SvgNestedGroupsDetector,
            config_model=SvgNestedGroupsConfig,
            rule_ids=["svg-008"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=80,
        ),
        DetectorBinding(
            detector_id="svg-009",
            detector_class=SvgDuplicateIdDetector,
            config_model=SvgDuplicateIdConfig,
            rule_ids=["svg-009"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=90,
        ),
        DetectorBinding(
            detector_id="svg-010",
            detector_class=SvgAbsolutePathOnlyDetector,
            config_model=SvgAbsolutePathOnlyConfig,
            rule_ids=["svg-010"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=100,
        ),
        DetectorBinding(
            detector_id="svg-011",
            detector_class=SvgBase64ImageDetector,
            config_model=SvgBase64ImageConfig,
            rule_ids=["svg-011"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=110,
        ),
        DetectorBinding(
            detector_id="svg-012",
            detector_class=SvgXmlnsDetector,
            config_model=SvgXmlnsConfig,
            rule_ids=["svg-012"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=120,
        ),
        DetectorBinding(
            detector_id="svg-013",
            detector_class=SvgDeprecatedXlinkHrefDetector,
            config_model=SvgDeprecatedXlinkHrefConfig,
            rule_ids=["svg-013"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=130,
        ),
        DetectorBinding(
            detector_id="svg-014",
            detector_class=SvgNodeCountDetector,
            config_model=SvgNodeCountConfig,
            rule_ids=["svg-014"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=140,
        ),
        DetectorBinding(
            detector_id="svg-015",
            detector_class=SvgProductionBloatDetector,
            config_model=SvgProductionBloatConfig,
            rule_ids=["svg-015"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=150,
        ),
    ],
)
