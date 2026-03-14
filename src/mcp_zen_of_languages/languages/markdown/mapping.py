"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
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


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="markdown",
    bindings=[
        RuleDetectorBinding(
            detector_id="md-001",
            detector_class=MarkdownHeadingHierarchyDetector,
            config_model=MarkdownHeadingHierarchyConfig,
            rule_ids=["md-001"],
            universal_dogma_ids=_dogmas("ZEN-RETURN-EARLY"),
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="md-002",
            detector_class=MarkdownAltTextDetector,
            config_model=MarkdownAltTextConfig,
            rule_ids=["md-002"],
            universal_dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME"),
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="md-003",
            detector_class=MarkdownBareUrlDetector,
            config_model=MarkdownBareUrlConfig,
            rule_ids=["md-003"],
            universal_dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="md-004",
            detector_class=MarkdownCodeFenceLanguageDetector,
            config_model=MarkdownCodeFenceLanguageConfig,
            rule_ids=["md-004"],
            universal_dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME", "ZEN-EXPLICIT-INTENT"),
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="md-005",
            detector_class=MarkdownFrontMatterDetector,
            config_model=MarkdownFrontMatterConfig,
            rule_ids=["md-005"],
            universal_dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="md-006",
            detector_class=MarkdownMdxNamedDefaultExportDetector,
            config_model=MarkdownMdxNamedDefaultExportConfig,
            rule_ids=["md-006"],
            universal_dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-UNAMBIGUOUS-NAME"),
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="md-007",
            detector_class=MarkdownMdxImportHygieneDetector,
            config_model=MarkdownMdxImportHygieneConfig,
            rule_ids=["md-007"],
            universal_dogma_ids=_dogmas("ZEN-STRICT-FENCES"),
            default_order=70,
        ),
    ],
)
