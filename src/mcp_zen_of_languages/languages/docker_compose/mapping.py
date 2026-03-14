"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
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


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="docker_compose",
    bindings=[
        RuleDetectorBinding(
            detector_id="docker-compose-001",
            detector_class=DockerComposeLatestTagDetector,
            config_model=DockerComposeLatestTagConfig,
            rules=[
                RuleBinding(
                    rule_id="docker-compose-001", dogma_ids=_dogmas("ZEN-STRICT-FENCES")
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="docker-compose-002",
            detector_class=DockerComposeNonRootUserDetector,
            config_model=DockerComposeNonRootUserConfig,
            rules=[
                RuleBinding(
                    rule_id="docker-compose-002",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-EXPLICIT-INTENT"),
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="docker-compose-003",
            detector_class=DockerComposeHealthcheckDetector,
            config_model=DockerComposeHealthcheckConfig,
            rules=[
                RuleBinding(
                    rule_id="docker-compose-003", dogma_ids=_dogmas("ZEN-FAIL-FAST")
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="docker-compose-004",
            detector_class=DockerComposeSecretHygieneDetector,
            config_model=DockerComposeSecretHygieneConfig,
            rules=[
                RuleBinding(
                    rule_id="docker-compose-004", dogma_ids=_dogmas("ZEN-STRICT-FENCES")
                )
            ],
            default_order=40,
        ),
    ],
)
