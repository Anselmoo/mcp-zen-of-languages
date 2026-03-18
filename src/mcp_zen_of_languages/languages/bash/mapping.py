"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.languages.bash.detectors import BashArgumentValidationDetector
from mcp_zen_of_languages.languages.bash.detectors import BashArrayUsageDetector
from mcp_zen_of_languages.languages.bash.detectors import (
    BashCommandSubstitutionDetector,
)
from mcp_zen_of_languages.languages.bash.detectors import BashDoubleBracketsDetector
from mcp_zen_of_languages.languages.bash.detectors import BashEvalUsageDetector
from mcp_zen_of_languages.languages.bash.detectors import BashExitCodeChecksDetector
from mcp_zen_of_languages.languages.bash.detectors import BashFunctionUsageDetector
from mcp_zen_of_languages.languages.bash.detectors import BashLocalVariablesDetector
from mcp_zen_of_languages.languages.bash.detectors import BashMeaningfulNamesDetector
from mcp_zen_of_languages.languages.bash.detectors import BashQuoteVariablesDetector
from mcp_zen_of_languages.languages.bash.detectors import BashReadonlyConstantsDetector
from mcp_zen_of_languages.languages.bash.detectors import BashSignalHandlingDetector
from mcp_zen_of_languages.languages.bash.detectors import BashStrictModeDetector
from mcp_zen_of_languages.languages.bash.detectors import BashUsageInfoDetector
from mcp_zen_of_languages.languages.configs import Bash006Config
from mcp_zen_of_languages.languages.configs import Bash011Config
from mcp_zen_of_languages.languages.configs import BashArgumentValidationConfig
from mcp_zen_of_languages.languages.configs import BashArrayUsageConfig
from mcp_zen_of_languages.languages.configs import BashCommandSubstitutionConfig
from mcp_zen_of_languages.languages.configs import BashDoubleBracketsConfig
from mcp_zen_of_languages.languages.configs import BashEvalUsageConfig
from mcp_zen_of_languages.languages.configs import BashExitCodeConfig
from mcp_zen_of_languages.languages.configs import BashLocalVariablesConfig
from mcp_zen_of_languages.languages.configs import BashQuoteVariablesConfig
from mcp_zen_of_languages.languages.configs import BashReadonlyConstantsConfig
from mcp_zen_of_languages.languages.configs import BashSignalHandlingConfig
from mcp_zen_of_languages.languages.configs import BashStrictModeConfig
from mcp_zen_of_languages.languages.configs import BashUsageInfoConfig


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


def _testing(*testing_ids: str) -> list[str]:
    """Return explicit testing family ids for the binding."""
    return list(testing_ids)


def _projection(*projection_ids: str) -> list[str]:
    """Return explicit projection family ids for the binding."""
    return list(projection_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="bash",
    bindings=[
        RuleDetectorBinding(
            detector_id="bash-005",
            detector_class=BashExitCodeChecksDetector,
            config_model=BashExitCodeConfig,
            rules=[
                RuleBinding(
                    rule_id="bash-005",
                    dogma_ids=_dogmas("ZEN-FAIL-FAST"),
                    testing_ids=_testing("shellcheck"),
                    verified_testing_ids=_testing("shellcheck"),
                    projection_ids=_projection("bash", "powershell", "python"),
                    verified_projection_ids=_projection("bash"),
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="bash-006",
            detector_class=BashFunctionUsageDetector,
            config_model=Bash006Config,
            rules=[
                RuleBinding(rule_id="bash-006", dogma_ids=_dogmas("ZEN-STRICT-FENCES"))
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="bash-007",
            detector_class=BashLocalVariablesDetector,
            config_model=BashLocalVariablesConfig,
            rules=[
                RuleBinding(rule_id="bash-007", dogma_ids=_dogmas("ZEN-STRICT-FENCES"))
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="bash-010",
            detector_class=BashArgumentValidationDetector,
            config_model=BashArgumentValidationConfig,
            rules=[
                RuleBinding(
                    rule_id="bash-010",
                    dogma_ids=_dogmas("ZEN-FAIL-FAST"),
                    testing_ids=_testing("shellcheck"),
                    verified_testing_ids=_testing("shellcheck"),
                    projection_ids=_projection("bash", "powershell"),
                    verified_projection_ids=_projection("bash"),
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="bash-011",
            detector_class=BashMeaningfulNamesDetector,
            config_model=Bash011Config,
            rules=[
                RuleBinding(
                    rule_id="bash-011", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="bash-012",
            detector_class=BashSignalHandlingDetector,
            config_model=BashSignalHandlingConfig,
            rules=[
                RuleBinding(
                    rule_id="bash-012",
                    dogma_ids=_dogmas("ZEN-FAIL-FAST"),
                    testing_ids=_testing("shellcheck"),
                    verified_testing_ids=_testing("shellcheck"),
                    projection_ids=_projection("bash", "powershell"),
                    verified_projection_ids=_projection("bash"),
                )
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="bash-013",
            detector_class=BashArrayUsageDetector,
            config_model=BashArrayUsageConfig,
            rules=[
                RuleBinding(
                    rule_id="bash-013", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="bash-014",
            detector_class=BashUsageInfoDetector,
            config_model=BashUsageInfoConfig,
            rules=[
                RuleBinding(
                    rule_id="bash-014", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=80,
        ),
        RuleDetectorBinding(
            detector_id="bash_command_substitution",
            detector_class=BashCommandSubstitutionDetector,
            config_model=BashCommandSubstitutionConfig,
            rules=[
                RuleBinding(
                    rule_id="bash-004",
                    dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME", "ZEN-RETURN-EARLY"),
                )
            ],
            default_order=90,
        ),
        RuleDetectorBinding(
            detector_id="bash_double_brackets",
            detector_class=BashDoubleBracketsDetector,
            config_model=BashDoubleBracketsConfig,
            rules=[
                RuleBinding(
                    rule_id="bash-003", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=100,
        ),
        RuleDetectorBinding(
            detector_id="bash_eval_usage",
            detector_class=BashEvalUsageDetector,
            config_model=BashEvalUsageConfig,
            rules=[
                RuleBinding(rule_id="bash-008", dogma_ids=_dogmas("ZEN-STRICT-FENCES"))
            ],
            default_order=110,
        ),
        RuleDetectorBinding(
            detector_id="bash_quote_variables",
            detector_class=BashQuoteVariablesDetector,
            config_model=BashQuoteVariablesConfig,
            rules=[
                RuleBinding(
                    rule_id="bash-002", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=120,
        ),
        RuleDetectorBinding(
            detector_id="bash_readonly_constants",
            detector_class=BashReadonlyConstantsDetector,
            config_model=BashReadonlyConstantsConfig,
            rules=[
                RuleBinding(
                    rule_id="bash-009",
                    dogma_ids=_dogmas("ZEN-VISIBLE-STATE", "ZEN-EXPLICIT-INTENT"),
                )
            ],
            default_order=130,
        ),
        RuleDetectorBinding(
            detector_id="bash_strict_mode",
            detector_class=BashStrictModeDetector,
            config_model=BashStrictModeConfig,
            rules=[
                RuleBinding(
                    rule_id="bash-001",
                    dogma_ids=_dogmas("ZEN-FAIL-FAST"),
                    testing_ids=_testing("shellcheck"),
                    verified_testing_ids=_testing("shellcheck"),
                    projection_ids=_projection("bash", "powershell", "python"),
                    verified_projection_ids=_projection("bash"),
                )
            ],
            default_order=140,
        ),
    ],
)
