"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
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


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="powershell",
    bindings=[
        RuleDetectorBinding(
            detector_id="powershell_approved_verbs",
            detector_class=PowerShellApprovedVerbDetector,
            config_model=PowerShellApprovedVerbConfig,
            rules=[
                RuleBinding(rule_id="ps-001", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME"))
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="powershell_error_handling",
            detector_class=PowerShellErrorHandlingDetector,
            config_model=PowerShellErrorHandlingConfig,
            rules=[RuleBinding(rule_id="ps-002", dogma_ids=_dogmas("ZEN-FAIL-FAST"))],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="powershell_pascal_case",
            detector_class=PowerShellPascalCaseDetector,
            config_model=PowerShellPascalCaseConfig,
            rules=[
                RuleBinding(rule_id="ps-004", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME"))
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="powershell_cmdlet_binding",
            detector_class=PowerShellCmdletBindingDetector,
            config_model=PowerShellCmdletBindingConfig,
            rules=[
                RuleBinding(
                    rule_id="ps-003", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="powershell_verbose_debug",
            detector_class=PowerShellVerboseDebugDetector,
            config_model=PowerShellVerboseDebugConfig,
            rules=[
                RuleBinding(rule_id="ps-005", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="powershell_positional_params",
            detector_class=PowerShellPositionalParamsDetector,
            config_model=PowerShellPositionalParamsConfig,
            rules=[
                RuleBinding(rule_id="ps-006", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME"))
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="powershell_pipeline_usage",
            detector_class=PowerShellPipelineUsageDetector,
            config_model=PowerShellPipelineUsageConfig,
            rules=[
                RuleBinding(
                    rule_id="ps-007", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="powershell_should_process",
            detector_class=PowerShellShouldProcessDetector,
            config_model=PowerShellShouldProcessConfig,
            rules=[RuleBinding(rule_id="ps-008", dogma_ids=_dogmas("ZEN-FAIL-FAST"))],
            default_order=80,
        ),
        RuleDetectorBinding(
            detector_id="powershell_splatting",
            detector_class=PowerShellSplattingDetector,
            config_model=PowerShellSplattingConfig,
            rules=[
                RuleBinding(rule_id="ps-009", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME"))
            ],
            default_order=90,
        ),
        RuleDetectorBinding(
            detector_id="powershell_parameter_validation",
            detector_class=PowerShellParameterValidationDetector,
            config_model=PowerShellParameterValidationConfig,
            rules=[RuleBinding(rule_id="ps-010", dogma_ids=_dogmas("ZEN-FAIL-FAST"))],
            default_order=100,
        ),
        RuleDetectorBinding(
            detector_id="powershell_comment_help",
            detector_class=PowerShellCommentHelpDetector,
            config_model=PowerShellCommentHelpConfig,
            rules=[
                RuleBinding(rule_id="ps-011", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME"))
            ],
            default_order=110,
        ),
        RuleDetectorBinding(
            detector_id="powershell_alias_usage",
            detector_class=PowerShellAliasUsageDetector,
            config_model=PowerShellAliasUsageConfig,
            rules=[
                RuleBinding(
                    rule_id="ps-012",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-UNAMBIGUOUS-NAME"),
                )
            ],
            default_order=120,
        ),
        RuleDetectorBinding(
            detector_id="powershell_return_objects",
            detector_class=PowerShellReturnObjectsDetector,
            config_model=PowerShellReturnObjectsConfig,
            rules=[
                RuleBinding(
                    rule_id="ps-013", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=130,
        ),
        RuleDetectorBinding(
            detector_id="powershell_scope_usage",
            detector_class=PowerShellScopeUsageDetector,
            config_model=PowerShellScopeUsageConfig,
            rules=[
                RuleBinding(
                    rule_id="ps-014",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-EXPLICIT-INTENT"),
                )
            ],
            default_order=140,
        ),
        RuleDetectorBinding(
            detector_id="powershell_null_handling",
            detector_class=PowerShellNullHandlingDetector,
            config_model=PowerShellNullHandlingConfig,
            rules=[
                RuleBinding(
                    rule_id="ps-015",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-FAIL-FAST"),
                )
            ],
            default_order=150,
        ),
    ],
)
