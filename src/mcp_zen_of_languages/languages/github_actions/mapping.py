"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import DetectorGearbox
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.core.universal_mapping import UNIVERSAL_DETECTOR_MAP
from mcp_zen_of_languages.languages.configs import GitHubActionsWorkflowConfig
from mcp_zen_of_languages.languages.github_actions.detectors import (
    GitHubActionsWorkflowDetector,
)


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="github-actions",
    bindings=[
        DetectorBinding(
            detector_id="gha-workflow",
            detector_class=GitHubActionsWorkflowDetector,
            config_model=GitHubActionsWorkflowConfig,
            rule_ids=[
                "gha-001",
                "gha-002",
                "gha-003",
                "gha-004",
                "gha-005",
                "gha-006",
                "gha-007",
                "gha-008",
                "gha-009",
                "gha-010",
                "gha-011",
                "gha-012",
                "gha-013",
                "gha-014",
                "gha-015",
            ],
            default_order=10,
        ),
    ],
)

GEARBOX = DetectorGearbox(language="github-actions")
GEARBOX.extend(DETECTOR_MAP.bindings)
GEARBOX.extend(UNIVERSAL_DETECTOR_MAP.bindings)
DETECTOR_MAP = GEARBOX.build_map()
