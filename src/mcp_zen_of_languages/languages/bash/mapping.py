"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
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


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="bash",
    bindings=[
        DetectorBinding(
            detector_id="bash_strict_mode",
            detector_class=BashStrictModeDetector,
            config_model=BashStrictModeConfig,
            rule_ids=["bash-001"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="bash_quote_variables",
            detector_class=BashQuoteVariablesDetector,
            config_model=BashQuoteVariablesConfig,
            rule_ids=["bash-002"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="bash-005",
            detector_class=BashExitCodeChecksDetector,
            config_model=BashExitCodeConfig,
            rule_ids=["bash-005"],
            default_order=25,
        ),
        DetectorBinding(
            detector_id="bash-006",
            detector_class=BashFunctionUsageDetector,
            config_model=Bash006Config,
            rule_ids=["bash-006"],
            default_order=27,
        ),
        DetectorBinding(
            detector_id="bash-007",
            detector_class=BashLocalVariablesDetector,
            config_model=BashLocalVariablesConfig,
            rule_ids=["bash-007"],
            default_order=28,
        ),
        DetectorBinding(
            detector_id="bash_eval_usage",
            detector_class=BashEvalUsageDetector,
            config_model=BashEvalUsageConfig,
            rule_ids=["bash-008"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="bash_double_brackets",
            detector_class=BashDoubleBracketsDetector,
            config_model=BashDoubleBracketsConfig,
            rule_ids=["bash-003"],
            default_order=40,
        ),
        DetectorBinding(
            detector_id="bash_command_substitution",
            detector_class=BashCommandSubstitutionDetector,
            config_model=BashCommandSubstitutionConfig,
            rule_ids=["bash-004"],
            default_order=50,
        ),
        DetectorBinding(
            detector_id="bash_readonly_constants",
            detector_class=BashReadonlyConstantsDetector,
            config_model=BashReadonlyConstantsConfig,
            rule_ids=["bash-009"],
            default_order=60,
        ),
        DetectorBinding(
            detector_id="bash-010",
            detector_class=BashArgumentValidationDetector,
            config_model=BashArgumentValidationConfig,
            rule_ids=["bash-010"],
            default_order=70,
        ),
        DetectorBinding(
            detector_id="bash-011",
            detector_class=BashMeaningfulNamesDetector,
            config_model=Bash011Config,
            rule_ids=["bash-011"],
            default_order=80,
        ),
        DetectorBinding(
            detector_id="bash-012",
            detector_class=BashSignalHandlingDetector,
            config_model=BashSignalHandlingConfig,
            rule_ids=["bash-012"],
            default_order=90,
        ),
        DetectorBinding(
            detector_id="bash-013",
            detector_class=BashArrayUsageDetector,
            config_model=BashArrayUsageConfig,
            rule_ids=["bash-013"],
            default_order=100,
        ),
        DetectorBinding(
            detector_id="bash-014",
            detector_class=BashUsageInfoDetector,
            config_model=BashUsageInfoConfig,
            rule_ids=["bash-014"],
            default_order=110,
        ),
    ],
)
