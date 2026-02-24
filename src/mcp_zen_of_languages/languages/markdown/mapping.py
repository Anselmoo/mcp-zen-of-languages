"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import (
    DetectorBinding,
    LanguageDetectorMap,
)
from mcp_zen_of_languages.core.universal_dogmas import DOGMA_RULE_IDS
from mcp_zen_of_languages.languages.configs import (
    MarkdownAltTextConfig,
    MarkdownBareUrlConfig,
    MarkdownCodeFenceLanguageConfig,
    MarkdownFrontMatterConfig,
    MarkdownHeadingHierarchyConfig,
    MarkdownMdxImportHygieneConfig,
    MarkdownMdxNamedDefaultExportConfig,
)
from mcp_zen_of_languages.languages.markdown.detectors import (
    MarkdownAltTextDetector,
    MarkdownBareUrlDetector,
    MarkdownCodeFenceLanguageDetector,
    MarkdownFrontMatterDetector,
    MarkdownHeadingHierarchyDetector,
    MarkdownMdxImportHygieneDetector,
    MarkdownMdxNamedDefaultExportDetector,
)

FULL_DOGMA_IDS = list(DOGMA_RULE_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="markdown",
    bindings=[
        DetectorBinding(
            detector_id="md-001",
            detector_class=MarkdownHeadingHierarchyDetector,
            config_model=MarkdownHeadingHierarchyConfig,
            rule_ids=["md-001"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=10,
        ),
        DetectorBinding(
            detector_id="md-002",
            detector_class=MarkdownAltTextDetector,
            config_model=MarkdownAltTextConfig,
            rule_ids=["md-002"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=20,
        ),
        DetectorBinding(
            detector_id="md-003",
            detector_class=MarkdownBareUrlDetector,
            config_model=MarkdownBareUrlConfig,
            rule_ids=["md-003"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=30,
        ),
        DetectorBinding(
            detector_id="md-004",
            detector_class=MarkdownCodeFenceLanguageDetector,
            config_model=MarkdownCodeFenceLanguageConfig,
            rule_ids=["md-004"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=40,
        ),
        DetectorBinding(
            detector_id="md-005",
            detector_class=MarkdownFrontMatterDetector,
            config_model=MarkdownFrontMatterConfig,
            rule_ids=["md-005"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=50,
        ),
        DetectorBinding(
            detector_id="md-006",
            detector_class=MarkdownMdxNamedDefaultExportDetector,
            config_model=MarkdownMdxNamedDefaultExportConfig,
            rule_ids=["md-006"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=60,
        ),
        DetectorBinding(
            detector_id="md-007",
            detector_class=MarkdownMdxImportHygieneDetector,
            config_model=MarkdownMdxImportHygieneConfig,
            rule_ids=["md-007"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=70,
        ),
    ],
)
