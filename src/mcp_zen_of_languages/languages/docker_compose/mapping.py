"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import (
    DetectorBinding,
    LanguageDetectorMap,
)
from mcp_zen_of_languages.core.universal_dogmas import DOGMA_RULE_IDS
from mcp_zen_of_languages.languages.configs import (
    DockerComposeHealthcheckConfig,
    DockerComposeLatestTagConfig,
    DockerComposeNonRootUserConfig,
    DockerComposeSecretHygieneConfig,
)
from mcp_zen_of_languages.languages.docker_compose.detectors import (
    DockerComposeHealthcheckDetector,
    DockerComposeLatestTagDetector,
    DockerComposeNonRootUserDetector,
    DockerComposeSecretHygieneDetector,
)

FULL_DOGMA_IDS = list(DOGMA_RULE_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="docker_compose",
    bindings=[
        DetectorBinding(
            detector_id="docker-compose-001",
            detector_class=DockerComposeLatestTagDetector,
            config_model=DockerComposeLatestTagConfig,
            rule_ids=["docker-compose-001"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=10,
        ),
        DetectorBinding(
            detector_id="docker-compose-002",
            detector_class=DockerComposeNonRootUserDetector,
            config_model=DockerComposeNonRootUserConfig,
            rule_ids=["docker-compose-002"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=20,
        ),
        DetectorBinding(
            detector_id="docker-compose-003",
            detector_class=DockerComposeHealthcheckDetector,
            config_model=DockerComposeHealthcheckConfig,
            rule_ids=["docker-compose-003"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=30,
        ),
        DetectorBinding(
            detector_id="docker-compose-004",
            detector_class=DockerComposeSecretHygieneDetector,
            config_model=DockerComposeSecretHygieneConfig,
            rule_ids=["docker-compose-004"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=40,
        ),
    ],
)
