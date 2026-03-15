"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.languages.configs import GitHubActionsWorkflowConfig
from mcp_zen_of_languages.languages.github_actions.detectors import (
    GitHubActionsWorkflowDetector,
)


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


def _testing(*testing_ids: str) -> list[str]:
    """Return explicit testing family ids for the binding."""
    return list(testing_ids)


def _projection(*projection_ids: str) -> list[str]:
    """Return explicit projection family ids for the binding."""
    return list(projection_ids)


_WORKFLOW_RULES = [
    RuleBinding(rule_id="gha-001", dogma_ids=_dogmas("ZEN-STRICT-FENCES")),
    RuleBinding(rule_id="gha-002", dogma_ids=_dogmas("ZEN-STRICT-FENCES")),
    RuleBinding(rule_id="gha-003", dogma_ids=_dogmas("ZEN-STRICT-FENCES")),
    RuleBinding(rule_id="gha-004", dogma_ids=_dogmas("ZEN-STRICT-FENCES")),
    RuleBinding(rule_id="gha-005", dogma_ids=_dogmas("ZEN-STRICT-FENCES")),
    RuleBinding(rule_id="gha-006", dogma_ids=_dogmas("ZEN-STRICT-FENCES")),
    RuleBinding(
        rule_id="gha-007",
        dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
        testing_ids=_testing("actionlint"),
        verified_testing_ids=_testing("actionlint"),
        projection_ids=_projection("github-actions", "gitlab_ci"),
        verified_projection_ids=_projection("github-actions"),
    ),
    RuleBinding(rule_id="gha-008", dogma_ids=_dogmas("ZEN-FAIL-FAST")),
    RuleBinding(rule_id="gha-009", dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY")),
    RuleBinding(rule_id="gha-010", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")),
    RuleBinding(rule_id="gha-011", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")),
    RuleBinding(
        rule_id="gha-012",
        dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-VISIBLE-STATE"),
    ),
    RuleBinding(rule_id="gha-013", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")),
    RuleBinding(rule_id="gha-014", dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY")),
    RuleBinding(
        rule_id="gha-015",
        dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-EXPLICIT-INTENT"),
    ),
]


DETECTOR_MAP = LanguageDetectorMap(
    language="github-actions",
    bindings=[
        RuleDetectorBinding(
            detector_id="gha-workflow",
            detector_class=GitHubActionsWorkflowDetector,
            config_model=GitHubActionsWorkflowConfig,
            rules=_WORKFLOW_RULES,
            default_order=10,
        ),
    ],
)
