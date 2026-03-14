"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.languages.configs import GitHubActionsWorkflowConfig
from mcp_zen_of_languages.languages.github_actions.detectors import (
    GitHubActionsWorkflowDetector,
)


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="github-actions",
    bindings=[
        RuleDetectorBinding(
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
            universal_dogma_ids=_dogmas(
                "ZEN-STRICT-FENCES",
                "ZEN-EXPLICIT-INTENT",
                "ZEN-FAIL-FAST",
                "ZEN-PROPORTIONATE-COMPLEXITY",
                "ZEN-RIGHT-ABSTRACTION",
                "ZEN-VISIBLE-STATE",
            ),
            default_order=10,
        ),
    ],
)
