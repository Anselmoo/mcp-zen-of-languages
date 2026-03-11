"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import DetectorGearbox
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.core.universal_mapping import UNIVERSAL_DETECTOR_MAP
from mcp_zen_of_languages.languages.configs import DockerfileAddInstructionConfig
from mcp_zen_of_languages.languages.configs import DockerfileDockerignoreConfig
from mcp_zen_of_languages.languages.configs import DockerfileHealthcheckConfig
from mcp_zen_of_languages.languages.configs import DockerfileLatestTagConfig
from mcp_zen_of_languages.languages.configs import DockerfileLayerDisciplineConfig
from mcp_zen_of_languages.languages.configs import DockerfileMultiStageConfig
from mcp_zen_of_languages.languages.configs import DockerfileNonRootUserConfig
from mcp_zen_of_languages.languages.configs import DockerfileSecretHygieneConfig
from mcp_zen_of_languages.languages.dockerfile.detectors import (
    DockerfileAddInstructionDetector,
)
from mcp_zen_of_languages.languages.dockerfile.detectors import (
    DockerfileDockerignoreDetector,
)
from mcp_zen_of_languages.languages.dockerfile.detectors import (
    DockerfileHealthcheckDetector,
)
from mcp_zen_of_languages.languages.dockerfile.detectors import (
    DockerfileLatestTagDetector,
)
from mcp_zen_of_languages.languages.dockerfile.detectors import (
    DockerfileLayerDisciplineDetector,
)
from mcp_zen_of_languages.languages.dockerfile.detectors import (
    DockerfileMultiStageDetector,
)
from mcp_zen_of_languages.languages.dockerfile.detectors import (
    DockerfileNonRootUserDetector,
)
from mcp_zen_of_languages.languages.dockerfile.detectors import (
    DockerfileSecretHygieneDetector,
)


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="dockerfile",
    bindings=[
        DetectorBinding(
            detector_id="dockerfile-001",
            detector_class=DockerfileLatestTagDetector,
            config_model=DockerfileLatestTagConfig,
            rule_ids=["dockerfile-001"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="dockerfile-002",
            detector_class=DockerfileNonRootUserDetector,
            config_model=DockerfileNonRootUserConfig,
            rule_ids=["dockerfile-002"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="dockerfile-003",
            detector_class=DockerfileAddInstructionDetector,
            config_model=DockerfileAddInstructionConfig,
            rule_ids=["dockerfile-003"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="dockerfile-004",
            detector_class=DockerfileHealthcheckDetector,
            config_model=DockerfileHealthcheckConfig,
            rule_ids=["dockerfile-004"],
            default_order=40,
        ),
        DetectorBinding(
            detector_id="dockerfile-005",
            detector_class=DockerfileMultiStageDetector,
            config_model=DockerfileMultiStageConfig,
            rule_ids=["dockerfile-005"],
            default_order=50,
        ),
        DetectorBinding(
            detector_id="dockerfile-006",
            detector_class=DockerfileSecretHygieneDetector,
            config_model=DockerfileSecretHygieneConfig,
            rule_ids=["dockerfile-006"],
            default_order=60,
        ),
        DetectorBinding(
            detector_id="dockerfile-007",
            detector_class=DockerfileLayerDisciplineDetector,
            config_model=DockerfileLayerDisciplineConfig,
            rule_ids=["dockerfile-007"],
            default_order=70,
        ),
        DetectorBinding(
            detector_id="dockerfile-008",
            detector_class=DockerfileDockerignoreDetector,
            config_model=DockerfileDockerignoreConfig,
            rule_ids=["dockerfile-008"],
            default_order=80,
        ),
    ],
)

GEARBOX = DetectorGearbox(language="dockerfile")
GEARBOX.extend(DETECTOR_MAP.bindings)
GEARBOX.extend(UNIVERSAL_DETECTOR_MAP.bindings)
DETECTOR_MAP = GEARBOX.build_map()
