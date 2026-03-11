"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.languages.configs import PowerShellAliasUsageConfig
from mcp_zen_of_languages.languages.configs import PowerShellApprovedVerbConfig
from mcp_zen_of_languages.languages.configs import PowerShellCmdletBindingConfig
from mcp_zen_of_languages.languages.configs import PowerShellCommentHelpConfig
from mcp_zen_of_languages.languages.configs import PowerShellErrorHandlingConfig
from mcp_zen_of_languages.languages.configs import PowerShellNullHandlingConfig
from mcp_zen_of_languages.languages.configs import PowerShellParameterValidationConfig
from mcp_zen_of_languages.languages.configs import PowerShellPascalCaseConfig
from mcp_zen_of_languages.languages.configs import PowerShellPipelineUsageConfig
from mcp_zen_of_languages.languages.configs import PowerShellPositionalParamsConfig
from mcp_zen_of_languages.languages.configs import PowerShellReturnObjectsConfig
from mcp_zen_of_languages.languages.configs import PowerShellScopeUsageConfig
from mcp_zen_of_languages.languages.configs import PowerShellShouldProcessConfig
from mcp_zen_of_languages.languages.configs import PowerShellSplattingConfig
from mcp_zen_of_languages.languages.configs import PowerShellVerboseDebugConfig
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellAliasUsageDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellApprovedVerbDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellCmdletBindingDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellCommentHelpDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellErrorHandlingDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellNullHandlingDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellParameterValidationDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellPascalCaseDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellPipelineUsageDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellPositionalParamsDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellReturnObjectsDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellScopeUsageDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellShouldProcessDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellSplattingDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellVerboseDebugDetector,
)


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="powershell",
    bindings=[
        DetectorBinding(
            detector_id="powershell_approved_verbs",
            detector_class=PowerShellApprovedVerbDetector,
            config_model=PowerShellApprovedVerbConfig,
            rule_ids=["ps-001"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=10,
        ),
        DetectorBinding(
            detector_id="powershell_error_handling",
            detector_class=PowerShellErrorHandlingDetector,
            config_model=PowerShellErrorHandlingConfig,
            rule_ids=["ps-002"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=20,
        ),
        DetectorBinding(
            detector_id="powershell_pascal_case",
            detector_class=PowerShellPascalCaseDetector,
            config_model=PowerShellPascalCaseConfig,
            rule_ids=["ps-004"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=30,
        ),
        DetectorBinding(
            detector_id="powershell_cmdlet_binding",
            detector_class=PowerShellCmdletBindingDetector,
            config_model=PowerShellCmdletBindingConfig,
            rule_ids=["ps-003"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=40,
        ),
        DetectorBinding(
            detector_id="powershell_verbose_debug",
            detector_class=PowerShellVerboseDebugDetector,
            config_model=PowerShellVerboseDebugConfig,
            rule_ids=["ps-005"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=50,
        ),
        DetectorBinding(
            detector_id="powershell_positional_params",
            detector_class=PowerShellPositionalParamsDetector,
            config_model=PowerShellPositionalParamsConfig,
            rule_ids=["ps-006"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=60,
        ),
        DetectorBinding(
            detector_id="powershell_pipeline_usage",
            detector_class=PowerShellPipelineUsageDetector,
            config_model=PowerShellPipelineUsageConfig,
            rule_ids=["ps-007"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=70,
        ),
        DetectorBinding(
            detector_id="powershell_should_process",
            detector_class=PowerShellShouldProcessDetector,
            config_model=PowerShellShouldProcessConfig,
            rule_ids=["ps-008"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=80,
        ),
        DetectorBinding(
            detector_id="powershell_splatting",
            detector_class=PowerShellSplattingDetector,
            config_model=PowerShellSplattingConfig,
            rule_ids=["ps-009"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=90,
        ),
        DetectorBinding(
            detector_id="powershell_parameter_validation",
            detector_class=PowerShellParameterValidationDetector,
            config_model=PowerShellParameterValidationConfig,
            rule_ids=["ps-010"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=100,
        ),
        DetectorBinding(
            detector_id="powershell_comment_help",
            detector_class=PowerShellCommentHelpDetector,
            config_model=PowerShellCommentHelpConfig,
            rule_ids=["ps-011"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=110,
        ),
        DetectorBinding(
            detector_id="powershell_alias_usage",
            detector_class=PowerShellAliasUsageDetector,
            config_model=PowerShellAliasUsageConfig,
            rule_ids=["ps-012"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=120,
        ),
        DetectorBinding(
            detector_id="powershell_return_objects",
            detector_class=PowerShellReturnObjectsDetector,
            config_model=PowerShellReturnObjectsConfig,
            rule_ids=["ps-013"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=130,
        ),
        DetectorBinding(
            detector_id="powershell_scope_usage",
            detector_class=PowerShellScopeUsageDetector,
            config_model=PowerShellScopeUsageConfig,
            rule_ids=["ps-014"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=140,
        ),
        DetectorBinding(
            detector_id="powershell_null_handling",
            detector_class=PowerShellNullHandlingDetector,
            config_model=PowerShellNullHandlingConfig,
            rule_ids=["ps-015"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=150,
        ),
    ],
)
