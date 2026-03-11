"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import DetectorGearbox
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
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


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
GEARBOX = DetectorGearbox(language="ansible")
GEARBOX.extend(
    [
        DetectorBinding(
            detector_id="ansible-001",
            detector_class=AnsibleNamingDetector,
            config_model=AnsibleNamingConfig,
            rule_ids=["ansible-001"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=10,
        ),
        DetectorBinding(
            detector_id="ansible-002",
            detector_class=AnsibleFqcnDetector,
            config_model=AnsibleFqcnConfig,
            rule_ids=["ansible-002"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=20,
        ),
        DetectorBinding(
            detector_id="ansible-003",
            detector_class=AnsibleIdempotencyDetector,
            config_model=AnsibleIdempotencyConfig,
            rule_ids=["ansible-003"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=30,
        ),
        DetectorBinding(
            detector_id="ansible-004",
            detector_class=AnsibleBecomeDetector,
            config_model=AnsibleBecomeConfig,
            rule_ids=["ansible-004"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=40,
        ),
        DetectorBinding(
            detector_id="ansible-005",
            detector_class=AnsibleStateExplicitDetector,
            config_model=AnsibleStateExplicitConfig,
            rule_ids=["ansible-005"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=50,
        ),
        DetectorBinding(
            detector_id="ansible-006",
            detector_class=AnsibleNoCleartextPasswordDetector,
            config_model=AnsibleNoCleartextPasswordConfig,
            rule_ids=["ansible-006"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=60,
        ),
        DetectorBinding(
            detector_id="ansible-007",
            detector_class=AnsibleJinjaSpacingDetector,
            config_model=AnsibleJinjaSpacingConfig,
            rule_ids=["ansible-007"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=70,
        ),
        DetectorBinding(
            detector_id="ansible-008",
            detector_class=AnsibleReadabilityCountsDetector,
            config_model=AnsibleReadabilityCountsConfig,
            rule_ids=["ansible-008"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=80,
        ),
        DetectorBinding(
            detector_id="ansible-009",
            detector_class=AnsibleUserOutcomeDetector,
            config_model=AnsibleUserOutcomeConfig,
            rule_ids=["ansible-009"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=90,
        ),
        DetectorBinding(
            detector_id="ansible-010",
            detector_class=AnsibleUserExperienceDetector,
            config_model=AnsibleUserExperienceConfig,
            rule_ids=["ansible-010"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=100,
        ),
        DetectorBinding(
            detector_id="ansible-011",
            detector_class=AnsibleMagicAutomationDetector,
            config_model=AnsibleMagicAutomationConfig,
            rule_ids=["ansible-011"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=110,
        ),
        DetectorBinding(
            detector_id="ansible-012",
            detector_class=AnsibleConventionOverConfigDetector,
            config_model=AnsibleConventionOverConfigConfig,
            rule_ids=["ansible-012"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=120,
        ),
        DetectorBinding(
            detector_id="ansible-013",
            detector_class=AnsibleDeclarativeBiasDetector,
            config_model=AnsibleDeclarativeBiasConfig,
            rule_ids=["ansible-013"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=130,
        ),
        DetectorBinding(
            detector_id="ansible-014",
            detector_class=AnsibleFocusDetector,
            config_model=AnsibleFocusConfig,
            rule_ids=["ansible-014"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=140,
        ),
        DetectorBinding(
            detector_id="ansible-015",
            detector_class=AnsibleComplexityProductivityDetector,
            config_model=AnsibleComplexityKillsProductivityConfig,
            rule_ids=["ansible-015"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=150,
        ),
        DetectorBinding(
            detector_id="ansible-016",
            detector_class=AnsibleExplainabilityDetector,
            config_model=AnsibleExplainabilityConfig,
            rule_ids=["ansible-016"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=160,
        ),
        DetectorBinding(
            detector_id="ansible-017",
            detector_class=AnsibleAutomationOpportunityDetector,
            config_model=AnsibleAutomationOpportunityConfig,
            rule_ids=["ansible-017"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=170,
        ),
        DetectorBinding(
            detector_id="ansible-018",
            detector_class=AnsibleContinuousImprovementDetector,
            config_model=AnsibleContinuousImprovementConfig,
            rule_ids=["ansible-018"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=180,
        ),
        DetectorBinding(
            detector_id="ansible-019",
            detector_class=AnsibleFrictionDetector,
            config_model=AnsibleFrictionConfig,
            rule_ids=["ansible-019"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=190,
        ),
        DetectorBinding(
            detector_id="ansible-020",
            detector_class=AnsibleAutomationJourneyDetector,
            config_model=AnsibleAutomationJourneyConfig,
            rule_ids=["ansible-020"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=200,
        ),
    ]
)
DETECTOR_MAP = GEARBOX.build_map()
