"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.languages.configs import DockerComposeHealthcheckConfig
from mcp_zen_of_languages.languages.configs import DockerComposeLatestTagConfig
from mcp_zen_of_languages.languages.configs import DockerComposeNonRootUserConfig
from mcp_zen_of_languages.languages.configs import DockerComposeSecretHygieneConfig
from mcp_zen_of_languages.languages.docker_compose.detectors import (
    DockerComposeHealthcheckDetector,
)
from mcp_zen_of_languages.languages.docker_compose.detectors import (
    DockerComposeLatestTagDetector,
)
from mcp_zen_of_languages.languages.docker_compose.detectors import (
    DockerComposeNonRootUserDetector,
)
from mcp_zen_of_languages.languages.docker_compose.detectors import (
    DockerComposeSecretHygieneDetector,
)


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="docker_compose",
    bindings=[
        DetectorBinding(
            detector_id="docker-compose-001",
            detector_class=DockerComposeLatestTagDetector,
            config_model=DockerComposeLatestTagConfig,
            rule_ids=["docker-compose-001"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="docker-compose-002",
            detector_class=DockerComposeNonRootUserDetector,
            config_model=DockerComposeNonRootUserConfig,
            rule_ids=["docker-compose-002"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="docker-compose-003",
            detector_class=DockerComposeHealthcheckDetector,
            config_model=DockerComposeHealthcheckConfig,
            rule_ids=["docker-compose-003"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="docker-compose-004",
            detector_class=DockerComposeSecretHygieneDetector,
            config_model=DockerComposeSecretHygieneConfig,
            rule_ids=["docker-compose-004"],
            default_order=40,
        ),
    ],
)
