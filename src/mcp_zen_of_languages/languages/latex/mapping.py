"""Detector bindings for LaTeX analysis."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.languages.configs import LatexBibliographyHygieneConfig
from mcp_zen_of_languages.languages.configs import LatexCaptionCompletenessConfig
from mcp_zen_of_languages.languages.configs import LatexEncodingDeclarationConfig
from mcp_zen_of_languages.languages.configs import LatexIncludeLoopConfig
from mcp_zen_of_languages.languages.configs import LatexLabelRefDisciplineConfig
from mcp_zen_of_languages.languages.configs import LatexMacroDefinitionConfig
from mcp_zen_of_languages.languages.configs import LatexSemanticMarkupConfig
from mcp_zen_of_languages.languages.configs import LatexUnusedPackagesConfig
from mcp_zen_of_languages.languages.configs import LatexWidthAbstractionConfig
from mcp_zen_of_languages.languages.latex.detectors import (
    LatexBibliographyHygieneDetector,
)
from mcp_zen_of_languages.languages.latex.detectors import (
    LatexCaptionCompletenessDetector,
)
from mcp_zen_of_languages.languages.latex.detectors import (
    LatexEncodingDeclarationDetector,
)
from mcp_zen_of_languages.languages.latex.detectors import LatexIncludeLoopDetector
from mcp_zen_of_languages.languages.latex.detectors import (
    LatexLabelRefDisciplineDetector,
)
from mcp_zen_of_languages.languages.latex.detectors import LatexMacroDefinitionDetector
from mcp_zen_of_languages.languages.latex.detectors import LatexSemanticMarkupDetector
from mcp_zen_of_languages.languages.latex.detectors import LatexUnusedPackagesDetector
from mcp_zen_of_languages.languages.latex.detectors import LatexWidthAbstractionDetector


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="latex",
    bindings=[
        RuleDetectorBinding(
            detector_id="latex-001",
            detector_class=LatexMacroDefinitionDetector,
            config_model=LatexMacroDefinitionConfig,
            rules=[
                RuleBinding(
                    rule_id="latex-001", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="latex-002",
            detector_class=LatexLabelRefDisciplineDetector,
            config_model=LatexLabelRefDisciplineConfig,
            rules=[
                RuleBinding(
                    rule_id="latex-002",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
                    testing_ids=["chktex"],
                    verified_testing_ids=["chktex"],
                    projection_ids=["pdf"],
                    verified_projection_ids=["pdf"],
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="latex-003",
            detector_class=LatexCaptionCompletenessDetector,
            config_model=LatexCaptionCompletenessConfig,
            rules=[
                RuleBinding(
                    rule_id="latex-003", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="latex-004",
            detector_class=LatexBibliographyHygieneDetector,
            config_model=LatexBibliographyHygieneConfig,
            rules=[
                RuleBinding(
                    rule_id="latex-004",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES"),
                    testing_ids=["chktex"],
                    verified_testing_ids=["chktex"],
                    projection_ids=["pdf"],
                    verified_projection_ids=["pdf"],
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="latex-005",
            detector_class=LatexWidthAbstractionDetector,
            config_model=LatexWidthAbstractionConfig,
            rules=[
                RuleBinding(
                    rule_id="latex-005", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="latex-006",
            detector_class=LatexSemanticMarkupDetector,
            config_model=LatexSemanticMarkupConfig,
            rules=[
                RuleBinding(
                    rule_id="latex-006", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="latex-007",
            detector_class=LatexIncludeLoopDetector,
            config_model=LatexIncludeLoopConfig,
            rules=[
                RuleBinding(
                    rule_id="latex-007", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="latex-008",
            detector_class=LatexEncodingDeclarationDetector,
            config_model=LatexEncodingDeclarationConfig,
            rules=[
                RuleBinding(
                    rule_id="latex-008",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
                    testing_ids=["chktex"],
                    verified_testing_ids=["chktex"],
                    projection_ids=["pdf"],
                    verified_projection_ids=["pdf"],
                )
            ],
            default_order=80,
        ),
        RuleDetectorBinding(
            detector_id="latex-009",
            detector_class=LatexUnusedPackagesDetector,
            config_model=LatexUnusedPackagesConfig,
            rules=[
                RuleBinding(
                    rule_id="latex-009",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-RUTHLESS-DELETION"),
                )
            ],
            default_order=90,
        ),
    ],
)
