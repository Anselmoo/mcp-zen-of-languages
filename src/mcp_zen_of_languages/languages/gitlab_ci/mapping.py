"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.languages.configs import GitLabCIAllowFailureConfig
from mcp_zen_of_languages.languages.configs import GitLabCIArtifactExpiryConfig
from mcp_zen_of_languages.languages.configs import GitLabCIDuplicatedBeforeScriptConfig
from mcp_zen_of_languages.languages.configs import GitLabCIExposedVariablesConfig
from mcp_zen_of_languages.languages.configs import GitLabCIGodPipelineConfig
from mcp_zen_of_languages.languages.configs import GitLabCIMissingCacheConfig
from mcp_zen_of_languages.languages.configs import GitLabCIMissingInterruptibleConfig
from mcp_zen_of_languages.languages.configs import GitLabCIMissingNeedsConfig
from mcp_zen_of_languages.languages.configs import GitLabCIOnlyExceptConfig
from mcp_zen_of_languages.languages.configs import GitLabCIUnpinnedImageConfig
from mcp_zen_of_languages.languages.gitlab_ci.detectors import (
    AllowFailureWithoutRulesDetector,
)
from mcp_zen_of_languages.languages.gitlab_ci.detectors import ArtifactExpiryDetector
from mcp_zen_of_languages.languages.gitlab_ci.detectors import (
    DuplicatedBeforeScriptDetector,
)
from mcp_zen_of_languages.languages.gitlab_ci.detectors import ExposedVariablesDetector
from mcp_zen_of_languages.languages.gitlab_ci.detectors import GodPipelineDetector
from mcp_zen_of_languages.languages.gitlab_ci.detectors import MissingCacheKeyDetector
from mcp_zen_of_languages.languages.gitlab_ci.detectors import (
    MissingInterruptibleDetector,
)
from mcp_zen_of_languages.languages.gitlab_ci.detectors import MissingNeedsDetector
from mcp_zen_of_languages.languages.gitlab_ci.detectors import OnlyExceptDetector
from mcp_zen_of_languages.languages.gitlab_ci.detectors import UnpinnedImageTagDetector


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="gitlab_ci",
    bindings=[
        RuleDetectorBinding(
            detector_id="gitlab-ci-001",
            detector_class=UnpinnedImageTagDetector,
            config_model=GitLabCIUnpinnedImageConfig,
            rules=[
                RuleBinding(
                    rule_id="gitlab-ci-001", dogma_ids=_dogmas("ZEN-STRICT-FENCES")
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="gitlab-ci-002",
            detector_class=ExposedVariablesDetector,
            config_model=GitLabCIExposedVariablesConfig,
            rules=[
                RuleBinding(
                    rule_id="gitlab-ci-002", dogma_ids=_dogmas("ZEN-STRICT-FENCES")
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="gitlab-ci-003",
            detector_class=AllowFailureWithoutRulesDetector,
            config_model=GitLabCIAllowFailureConfig,
            rules=[
                RuleBinding(
                    rule_id="gitlab-ci-003",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-EXPLICIT-INTENT"),
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="gitlab-ci-004",
            detector_class=GodPipelineDetector,
            config_model=GitLabCIGodPipelineConfig,
            rules=[
                RuleBinding(
                    rule_id="gitlab-ci-004", dogma_ids=_dogmas("ZEN-RETURN-EARLY")
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="gitlab-ci-005",
            detector_class=DuplicatedBeforeScriptDetector,
            config_model=GitLabCIDuplicatedBeforeScriptConfig,
            rules=[
                RuleBinding(
                    rule_id="gitlab-ci-005", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="gitlab-ci-006",
            detector_class=MissingInterruptibleDetector,
            config_model=GitLabCIMissingInterruptibleConfig,
            rules=[
                RuleBinding(
                    rule_id="gitlab-ci-006",
                    dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
                )
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="gitlab-ci-007",
            detector_class=MissingNeedsDetector,
            config_model=GitLabCIMissingNeedsConfig,
            rules=[
                RuleBinding(
                    rule_id="gitlab-ci-007",
                    dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="gitlab-ci-008",
            detector_class=OnlyExceptDetector,
            config_model=GitLabCIOnlyExceptConfig,
            rules=[
                RuleBinding(
                    rule_id="gitlab-ci-008", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=80,
        ),
        RuleDetectorBinding(
            detector_id="gitlab-ci-009",
            detector_class=MissingCacheKeyDetector,
            config_model=GitLabCIMissingCacheConfig,
            rules=[
                RuleBinding(
                    rule_id="gitlab-ci-009",
                    dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
                )
            ],
            default_order=90,
        ),
        RuleDetectorBinding(
            detector_id="gitlab-ci-010",
            detector_class=ArtifactExpiryDetector,
            config_model=GitLabCIArtifactExpiryConfig,
            rules=[
                RuleBinding(
                    rule_id="gitlab-ci-010", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=100,
        ),
    ],
)
