"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import DetectorGearbox
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.core.universal_mapping import UNIVERSAL_DETECTOR_MAP
from mcp_zen_of_languages.languages.configs import TerraformBackendConfig
from mcp_zen_of_languages.languages.configs import TerraformHardcodedIdConfig
from mcp_zen_of_languages.languages.configs import TerraformModuleVersionPinningConfig
from mcp_zen_of_languages.languages.configs import TerraformNamingConventionConfig
from mcp_zen_of_languages.languages.configs import TerraformNoHardcodedSecretsConfig
from mcp_zen_of_languages.languages.configs import TerraformProviderVersionPinningConfig
from mcp_zen_of_languages.languages.configs import (
    TerraformVariableOutputDescriptionConfig,
)
from mcp_zen_of_languages.languages.terraform.detectors import (
    TerraformBackendConfigDetector,
)
from mcp_zen_of_languages.languages.terraform.detectors import (
    TerraformHardcodedIdDetector,
)
from mcp_zen_of_languages.languages.terraform.detectors import (
    TerraformModuleVersionPinningDetector,
)
from mcp_zen_of_languages.languages.terraform.detectors import (
    TerraformNamingConventionDetector,
)
from mcp_zen_of_languages.languages.terraform.detectors import (
    TerraformNoHardcodedSecretsDetector,
)
from mcp_zen_of_languages.languages.terraform.detectors import (
    TerraformProviderVersionPinningDetector,
)
from mcp_zen_of_languages.languages.terraform.detectors import (
    TerraformVariableOutputDescriptionDetector,
)


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="terraform",
    bindings=[
        DetectorBinding(
            detector_id="tf-001",
            detector_class=TerraformProviderVersionPinningDetector,
            config_model=TerraformProviderVersionPinningConfig,
            rule_ids=["tf-001"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="tf-002",
            detector_class=TerraformModuleVersionPinningDetector,
            config_model=TerraformModuleVersionPinningConfig,
            rule_ids=["tf-002"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="tf-003",
            detector_class=TerraformVariableOutputDescriptionDetector,
            config_model=TerraformVariableOutputDescriptionConfig,
            rule_ids=["tf-003"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="tf-004",
            detector_class=TerraformHardcodedIdDetector,
            config_model=TerraformHardcodedIdConfig,
            rule_ids=["tf-004"],
            default_order=40,
        ),
        DetectorBinding(
            detector_id="tf-005",
            detector_class=TerraformNoHardcodedSecretsDetector,
            config_model=TerraformNoHardcodedSecretsConfig,
            rule_ids=["tf-005"],
            default_order=50,
        ),
        DetectorBinding(
            detector_id="tf-006",
            detector_class=TerraformBackendConfigDetector,
            config_model=TerraformBackendConfig,
            rule_ids=["tf-006"],
            default_order=60,
        ),
        DetectorBinding(
            detector_id="tf-007",
            detector_class=TerraformNamingConventionDetector,
            config_model=TerraformNamingConventionConfig,
            rule_ids=["tf-007"],
            default_order=70,
        ),
    ],
)

GEARBOX = DetectorGearbox(language="terraform")
GEARBOX.extend(DETECTOR_MAP.bindings)
GEARBOX.extend(UNIVERSAL_DETECTOR_MAP.bindings)
DETECTOR_MAP = GEARBOX.build_map()
