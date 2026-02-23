"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import (
    DetectorBinding,
    LanguageDetectorMap,
)
from mcp_zen_of_languages.core.universal_dogmas import DOGMA_RULE_IDS
from mcp_zen_of_languages.languages.configs import (
    XmlAttributeUsageConfig,
    XmlClosingTagsConfig,
    XmlHierarchyConfig,
    XmlNamespaceConfig,
    XmlSemanticMarkupConfig,
    XmlValidityConfig,
)
from mcp_zen_of_languages.languages.xml.detectors import (
    XmlAttributeUsageDetector,
    XmlClosingTagsDetector,
    XmlHierarchyDetector,
    XmlNamespaceDetector,
    XmlSemanticMarkupDetector,
    XmlValidityDetector,
)

FULL_DOGMA_IDS = list(DOGMA_RULE_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="xml",
    bindings=[
        DetectorBinding(
            detector_id="xml-001",
            detector_class=XmlSemanticMarkupDetector,
            config_model=XmlSemanticMarkupConfig,
            rule_ids=["xml-001"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=10,
        ),
        DetectorBinding(
            detector_id="xml-002",
            detector_class=XmlAttributeUsageDetector,
            config_model=XmlAttributeUsageConfig,
            rule_ids=["xml-002"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=20,
        ),
        DetectorBinding(
            detector_id="xml-003",
            detector_class=XmlNamespaceDetector,
            config_model=XmlNamespaceConfig,
            rule_ids=["xml-003"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=30,
        ),
        DetectorBinding(
            detector_id="xml-004",
            detector_class=XmlValidityDetector,
            config_model=XmlValidityConfig,
            rule_ids=["xml-004"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=40,
        ),
        DetectorBinding(
            detector_id="xml-005",
            detector_class=XmlHierarchyDetector,
            config_model=XmlHierarchyConfig,
            rule_ids=["xml-005"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=50,
        ),
        DetectorBinding(
            detector_id="xml-006",
            detector_class=XmlClosingTagsDetector,
            config_model=XmlClosingTagsConfig,
            rule_ids=["xml-006"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=60,
        ),
    ],
)
