"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorGearbox
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleAutomationJourneyDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleAutomationOpportunityDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleBecomeDetector
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleComplexityProductivityDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleContinuousImprovementDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleConventionOverConfigDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleDeclarativeBiasDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleExplainabilityDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleFocusDetector
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleFqcnDetector
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleFrictionDetector
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleIdempotencyDetector
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleJinjaSpacingDetector
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleMagicAutomationDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleNamingDetector
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleNoCleartextPasswordDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleReadabilityCountsDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleStateExplicitDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleUserExperienceDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleUserOutcomeDetector
from mcp_zen_of_languages.languages.configs import AnsibleAutomationJourneyConfig
from mcp_zen_of_languages.languages.configs import AnsibleAutomationOpportunityConfig
from mcp_zen_of_languages.languages.configs import AnsibleBecomeConfig
from mcp_zen_of_languages.languages.configs import (
    AnsibleComplexityKillsProductivityConfig,
)
from mcp_zen_of_languages.languages.configs import AnsibleContinuousImprovementConfig
from mcp_zen_of_languages.languages.configs import AnsibleConventionOverConfigConfig
from mcp_zen_of_languages.languages.configs import AnsibleDeclarativeBiasConfig
from mcp_zen_of_languages.languages.configs import AnsibleExplainabilityConfig
from mcp_zen_of_languages.languages.configs import AnsibleFocusConfig
from mcp_zen_of_languages.languages.configs import AnsibleFqcnConfig
from mcp_zen_of_languages.languages.configs import AnsibleFrictionConfig
from mcp_zen_of_languages.languages.configs import AnsibleIdempotencyConfig
from mcp_zen_of_languages.languages.configs import AnsibleJinjaSpacingConfig
from mcp_zen_of_languages.languages.configs import AnsibleMagicAutomationConfig
from mcp_zen_of_languages.languages.configs import AnsibleNamingConfig
from mcp_zen_of_languages.languages.configs import AnsibleNoCleartextPasswordConfig
from mcp_zen_of_languages.languages.configs import AnsibleReadabilityCountsConfig
from mcp_zen_of_languages.languages.configs import AnsibleStateExplicitConfig
from mcp_zen_of_languages.languages.configs import AnsibleUserExperienceConfig
from mcp_zen_of_languages.languages.configs import AnsibleUserOutcomeConfig


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


GEARBOX = DetectorGearbox(language="ansible")
GEARBOX.extend(
    [
        RuleDetectorBinding(
            detector_id="ansible-001",
            detector_class=AnsibleNamingDetector,
            config_model=AnsibleNamingConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-001", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="ansible-002",
            detector_class=AnsibleFqcnDetector,
            config_model=AnsibleFqcnConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-002", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="ansible-003",
            detector_class=AnsibleIdempotencyDetector,
            config_model=AnsibleIdempotencyConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-003", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="ansible-004",
            detector_class=AnsibleBecomeDetector,
            config_model=AnsibleBecomeConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-004", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="ansible-005",
            detector_class=AnsibleStateExplicitDetector,
            config_model=AnsibleStateExplicitConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-005",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-VISIBLE-STATE"),
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="ansible-006",
            detector_class=AnsibleNoCleartextPasswordDetector,
            config_model=AnsibleNoCleartextPasswordConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-006", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="ansible-007",
            detector_class=AnsibleJinjaSpacingDetector,
            config_model=AnsibleJinjaSpacingConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-007",
                    dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="ansible-008",
            detector_class=AnsibleReadabilityCountsDetector,
            config_model=AnsibleReadabilityCountsConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-008", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=80,
        ),
        RuleDetectorBinding(
            detector_id="ansible-009",
            detector_class=AnsibleUserOutcomeDetector,
            config_model=AnsibleUserOutcomeConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-009",
                    dogma_ids=_dogmas(
                        "ZEN-UNAMBIGUOUS-NAME", "ZEN-EXPLICIT-INTENT", "ZEN-FAIL-FAST"
                    ),
                )
            ],
            default_order=90,
        ),
        RuleDetectorBinding(
            detector_id="ansible-010",
            detector_class=AnsibleUserExperienceDetector,
            config_model=AnsibleUserExperienceConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-010", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=100,
        ),
        RuleDetectorBinding(
            detector_id="ansible-011",
            detector_class=AnsibleMagicAutomationDetector,
            config_model=AnsibleMagicAutomationConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-011",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-EXPLICIT-INTENT"),
                )
            ],
            default_order=110,
        ),
        RuleDetectorBinding(
            detector_id="ansible-012",
            detector_class=AnsibleConventionOverConfigDetector,
            config_model=AnsibleConventionOverConfigConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-012", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=120,
        ),
        RuleDetectorBinding(
            detector_id="ansible-013",
            detector_class=AnsibleDeclarativeBiasDetector,
            config_model=AnsibleDeclarativeBiasConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-013",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-VISIBLE-STATE"),
                )
            ],
            default_order=130,
        ),
        RuleDetectorBinding(
            detector_id="ansible-014",
            detector_class=AnsibleFocusDetector,
            config_model=AnsibleFocusConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-014",
                    dogma_ids=_dogmas(
                        "ZEN-STRICT-FENCES", "ZEN-PROPORTIONATE-COMPLEXITY"
                    ),
                )
            ],
            default_order=140,
        ),
        RuleDetectorBinding(
            detector_id="ansible-015",
            detector_class=AnsibleComplexityProductivityDetector,
            config_model=AnsibleComplexityKillsProductivityConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-015",
                    dogma_ids=_dogmas(
                        "ZEN-PROPORTIONATE-COMPLEXITY", "ZEN-RETURN-EARLY"
                    ),
                )
            ],
            default_order=150,
        ),
        RuleDetectorBinding(
            detector_id="ansible-016",
            detector_class=AnsibleExplainabilityDetector,
            config_model=AnsibleExplainabilityConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-016", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=160,
        ),
        RuleDetectorBinding(
            detector_id="ansible-017",
            detector_class=AnsibleAutomationOpportunityDetector,
            config_model=AnsibleAutomationOpportunityConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-017", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=170,
        ),
        RuleDetectorBinding(
            detector_id="ansible-018",
            detector_class=AnsibleContinuousImprovementDetector,
            config_model=AnsibleContinuousImprovementConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-018", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=180,
        ),
        RuleDetectorBinding(
            detector_id="ansible-019",
            detector_class=AnsibleFrictionDetector,
            config_model=AnsibleFrictionConfig,
            rules=[
                RuleBinding(
                    rule_id="ansible-019", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=190,
        ),
        RuleDetectorBinding(
            detector_id="ansible-020",
            detector_class=AnsibleAutomationJourneyDetector,
            config_model=AnsibleAutomationJourneyConfig,
            rules=[
                RuleBinding(rule_id="ansible-020", dogma_ids=_dogmas("ZEN-FAIL-FAST"))
            ],
            default_order=200,
        ),
    ]
)


DETECTOR_MAP = GEARBOX.build_map()
