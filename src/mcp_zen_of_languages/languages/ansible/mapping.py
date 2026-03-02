"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import DOGMA_RULE_IDS
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleBecomeDetector
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleFqcnDetector
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleIdempotencyDetector
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleJinjaSpacingDetector
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleNamingDetector
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleNoCleartextPasswordDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleStateExplicitDetector
from mcp_zen_of_languages.languages.configs import AnsibleBecomeConfig
from mcp_zen_of_languages.languages.configs import AnsibleFqcnConfig
from mcp_zen_of_languages.languages.configs import AnsibleIdempotencyConfig
from mcp_zen_of_languages.languages.configs import AnsibleJinjaSpacingConfig
from mcp_zen_of_languages.languages.configs import AnsibleNamingConfig
from mcp_zen_of_languages.languages.configs import AnsibleNoCleartextPasswordConfig
from mcp_zen_of_languages.languages.configs import AnsibleStateExplicitConfig


FULL_DOGMA_IDS = list(DOGMA_RULE_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="ansible",
    bindings=[
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
    ],
)
