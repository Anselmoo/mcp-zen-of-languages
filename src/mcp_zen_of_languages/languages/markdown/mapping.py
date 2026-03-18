"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
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
            rules=[
                RuleBinding(
                    rule_id="md-001",
                    dogma_ids=_dogmas("ZEN-RETURN-EARLY"),
                    testing_ids=["markdownlint"],
                    verified_testing_ids=["markdownlint"],
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="md-002",
            detector_class=MarkdownAltTextDetector,
            config_model=MarkdownAltTextConfig,
            rules=[
                RuleBinding(
                    rule_id="md-002",
                    dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME"),
                    testing_ids=["markdownlint"],
                    verified_testing_ids=["markdownlint"],
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="md-003",
            detector_class=MarkdownBareUrlDetector,
            config_model=MarkdownBareUrlConfig,
            rules=[
                RuleBinding(
                    rule_id="md-003",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
                    testing_ids=["markdownlint"],
                    verified_testing_ids=["markdownlint"],
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="md-004",
            detector_class=MarkdownCodeFenceLanguageDetector,
            config_model=MarkdownCodeFenceLanguageConfig,
            rules=[
                RuleBinding(
                    rule_id="md-004",
                    dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME", "ZEN-EXPLICIT-INTENT"),
                    testing_ids=["markdownlint"],
                    verified_testing_ids=["markdownlint"],
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="md-005",
            detector_class=MarkdownFrontMatterDetector,
            config_model=MarkdownFrontMatterConfig,
            rules=[
                RuleBinding(
                    rule_id="md-005",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
                    projection_ids=["react", "nextjs"],
                    verified_projection_ids=["nextjs"],
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="md-006",
            detector_class=MarkdownMdxNamedDefaultExportDetector,
            config_model=MarkdownMdxNamedDefaultExportConfig,
            rules=[
                RuleBinding(
                    rule_id="md-006",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-UNAMBIGUOUS-NAME"),
                    projection_ids=["react", "nextjs"],
                    verified_projection_ids=["nextjs"],
                )
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="md-007",
            detector_class=MarkdownMdxImportHygieneDetector,
            config_model=MarkdownMdxImportHygieneConfig,
            rules=[
                RuleBinding(
                    rule_id="md-007",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES"),
                    projection_ids=["react", "nextjs"],
                    verified_projection_ids=["nextjs"],
                )
            ],
            default_order=70,
        ),
    ],
)
