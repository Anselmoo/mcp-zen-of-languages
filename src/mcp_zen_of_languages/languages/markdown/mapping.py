"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import DetectorGearbox
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.core.universal_mapping import UNIVERSAL_DETECTOR_MAP
from mcp_zen_of_languages.languages.configs import MarkdownAltTextConfig
from mcp_zen_of_languages.languages.configs import MarkdownBareUrlConfig
from mcp_zen_of_languages.languages.configs import MarkdownCodeFenceLanguageConfig
from mcp_zen_of_languages.languages.configs import MarkdownFrontMatterConfig
from mcp_zen_of_languages.languages.configs import MarkdownHeadingHierarchyConfig
from mcp_zen_of_languages.languages.configs import MarkdownMdxImportHygieneConfig
from mcp_zen_of_languages.languages.configs import MarkdownMdxNamedDefaultExportConfig
from mcp_zen_of_languages.languages.markdown.detectors import MarkdownAltTextDetector
from mcp_zen_of_languages.languages.markdown.detectors import MarkdownBareUrlDetector
from mcp_zen_of_languages.languages.markdown.detectors import (
    MarkdownCodeFenceLanguageDetector,
)
from mcp_zen_of_languages.languages.markdown.detectors import (
    MarkdownFrontMatterDetector,
)
from mcp_zen_of_languages.languages.markdown.detectors import (
    MarkdownHeadingHierarchyDetector,
)
from mcp_zen_of_languages.languages.markdown.detectors import (
    MarkdownMdxImportHygieneDetector,
)
from mcp_zen_of_languages.languages.markdown.detectors import (
    MarkdownMdxNamedDefaultExportDetector,
)


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="markdown",
    bindings=[
        DetectorBinding(
            detector_id="md-001",
            detector_class=MarkdownHeadingHierarchyDetector,
            config_model=MarkdownHeadingHierarchyConfig,
            rule_ids=["md-001"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="md-002",
            detector_class=MarkdownAltTextDetector,
            config_model=MarkdownAltTextConfig,
            rule_ids=["md-002"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="md-003",
            detector_class=MarkdownBareUrlDetector,
            config_model=MarkdownBareUrlConfig,
            rule_ids=["md-003"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="md-004",
            detector_class=MarkdownCodeFenceLanguageDetector,
            config_model=MarkdownCodeFenceLanguageConfig,
            rule_ids=["md-004"],
            default_order=40,
        ),
        DetectorBinding(
            detector_id="md-005",
            detector_class=MarkdownFrontMatterDetector,
            config_model=MarkdownFrontMatterConfig,
            rule_ids=["md-005"],
            default_order=50,
        ),
        DetectorBinding(
            detector_id="md-006",
            detector_class=MarkdownMdxNamedDefaultExportDetector,
            config_model=MarkdownMdxNamedDefaultExportConfig,
            rule_ids=["md-006"],
            default_order=60,
        ),
        DetectorBinding(
            detector_id="md-007",
            detector_class=MarkdownMdxImportHygieneDetector,
            config_model=MarkdownMdxImportHygieneConfig,
            rule_ids=["md-007"],
            default_order=70,
        ),
    ],
)

GEARBOX = DetectorGearbox(language="markdown")
GEARBOX.extend(DETECTOR_MAP.bindings)
GEARBOX.extend(UNIVERSAL_DETECTOR_MAP.bindings)
DETECTOR_MAP = GEARBOX.build_map()
