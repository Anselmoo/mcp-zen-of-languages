"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import NonRuleDetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.languages.configs import GoBenchmarkConfig
from mcp_zen_of_languages.languages.configs import GoConcurrencyCallerConfig
from mcp_zen_of_languages.languages.configs import GoContextUsageConfig
from mcp_zen_of_languages.languages.configs import GoDeferUsageConfig
from mcp_zen_of_languages.languages.configs import GoEarlyReturnConfig
from mcp_zen_of_languages.languages.configs import GoEmbeddingDepthConfig
from mcp_zen_of_languages.languages.configs import GoErrorHandlingConfig
from mcp_zen_of_languages.languages.configs import GoGoroutineLeakConfig
from mcp_zen_of_languages.languages.configs import GoInitUsageConfig
from mcp_zen_of_languages.languages.configs import GoInterfacePointerConfig
from mcp_zen_of_languages.languages.configs import GoInterfaceReturnConfig
from mcp_zen_of_languages.languages.configs import GoInterfaceSizeConfig
from mcp_zen_of_languages.languages.configs import GoMaintainabilityConfig
from mcp_zen_of_languages.languages.configs import GoModerationConfig
from mcp_zen_of_languages.languages.configs import GoNamingConventionConfig
from mcp_zen_of_languages.languages.configs import GoPackageNamingConfig
from mcp_zen_of_languages.languages.configs import GoPackageStateConfig
from mcp_zen_of_languages.languages.configs import GoSimplicityConfig
from mcp_zen_of_languages.languages.configs import GoSinglePurposePackageConfig
from mcp_zen_of_languages.languages.configs import GoTestPresenceConfig
from mcp_zen_of_languages.languages.configs import GoZeroValueConfig
from mcp_zen_of_languages.languages.go.detectors import GoBenchmarkDetector
from mcp_zen_of_languages.languages.go.detectors import GoConcurrencyCallerDetector
from mcp_zen_of_languages.languages.go.detectors import GoContextUsageDetector
from mcp_zen_of_languages.languages.go.detectors import GoDeferUsageDetector
from mcp_zen_of_languages.languages.go.detectors import GoEarlyReturnDetector
from mcp_zen_of_languages.languages.go.detectors import GoEmbeddingDepthDetector
from mcp_zen_of_languages.languages.go.detectors import GoErrorHandlingDetector
from mcp_zen_of_languages.languages.go.detectors import GoGoroutineLeakDetector
from mcp_zen_of_languages.languages.go.detectors import GoInitUsageDetector
from mcp_zen_of_languages.languages.go.detectors import GoInterfacePointerDetector
from mcp_zen_of_languages.languages.go.detectors import GoInterfaceReturnDetector
from mcp_zen_of_languages.languages.go.detectors import GoInterfaceSizeDetector
from mcp_zen_of_languages.languages.go.detectors import GoMaintainabilityDetector
from mcp_zen_of_languages.languages.go.detectors import GoModerationDetector
from mcp_zen_of_languages.languages.go.detectors import GoNamingConventionDetector
from mcp_zen_of_languages.languages.go.detectors import GoOrganizeResponsibilityDetector
from mcp_zen_of_languages.languages.go.detectors import GoPackageNamingDetector
from mcp_zen_of_languages.languages.go.detectors import GoPackageStateDetector
from mcp_zen_of_languages.languages.go.detectors import GoSimplicityDetector
from mcp_zen_of_languages.languages.go.detectors import GoTestPresenceDetector
from mcp_zen_of_languages.languages.go.detectors import GoZeroValueDetector


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
    language="go",
    bindings=[
        RuleDetectorBinding(
            detector_id="go_benchmark",
            detector_class=GoBenchmarkDetector,
            config_model=GoBenchmarkConfig,
            rules=[
                RuleBinding(
                    rule_id="go-018",
                    dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
                    testing_ids=_testing("gotest"),
                    verified_testing_ids=_testing("gotest"),
                    projection_ids=_projection("go"),
                    verified_projection_ids=_projection("go"),
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="go_concurrency_caller",
            detector_class=GoConcurrencyCallerDetector,
            config_model=GoConcurrencyCallerConfig,
            rules=[
                RuleBinding(rule_id="go-015", dogma_ids=_dogmas("ZEN-VISIBLE-STATE"))
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="go_context_usage",
            detector_class=GoContextUsageDetector,
            config_model=GoContextUsageConfig,
            rules=[
                RuleBinding(rule_id="go-011", dogma_ids=_dogmas("ZEN-VISIBLE-STATE"))
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="go_defer_usage",
            detector_class=GoDeferUsageDetector,
            config_model=GoDeferUsageConfig,
            rules=[
                RuleBinding(
                    rule_id="go-007", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="go_early_return",
            detector_class=GoEarlyReturnDetector,
            config_model=GoEarlyReturnConfig,
            rules=[
                RuleBinding(
                    rule_id="go-017",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-FAIL-FAST"),
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="go_embedding_depth",
            detector_class=GoEmbeddingDepthDetector,
            config_model=GoEmbeddingDepthConfig,
            rules=[
                RuleBinding(
                    rule_id="go-014",
                    dogma_ids=_dogmas("ZEN-RETURN-EARLY", "ZEN-UNAMBIGUOUS-NAME"),
                )
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="go_error_handling",
            detector_class=GoErrorHandlingDetector,
            config_model=GoErrorHandlingConfig,
            rules=[
                RuleBinding(
                    rule_id="go-001",
                    dogma_ids=_dogmas("ZEN-FAIL-FAST", "ZEN-EXPLICIT-INTENT"),
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="go_goroutine_leaks",
            detector_class=GoGoroutineLeakDetector,
            config_model=GoGoroutineLeakConfig,
            rules=[
                RuleBinding(rule_id="go-006", dogma_ids=_dogmas("ZEN-VISIBLE-STATE"))
            ],
            default_order=80,
        ),
        RuleDetectorBinding(
            detector_id="go_init_usage",
            detector_class=GoInitUsageDetector,
            config_model=GoInitUsageConfig,
            rules=[
                RuleBinding(rule_id="go-012", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=90,
        ),
        RuleDetectorBinding(
            detector_id="go_interface_pointer",
            detector_class=GoInterfacePointerDetector,
            config_model=GoInterfacePointerConfig,
            rules=[
                RuleBinding(
                    rule_id="go-005", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=100,
        ),
        RuleDetectorBinding(
            detector_id="go_interface_return",
            detector_class=GoInterfaceReturnDetector,
            config_model=GoInterfaceReturnConfig,
            rules=[
                RuleBinding(
                    rule_id="go-002", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=110,
        ),
        RuleDetectorBinding(
            detector_id="go_interface_size",
            detector_class=GoInterfaceSizeDetector,
            config_model=GoInterfaceSizeConfig,
            rules=[
                RuleBinding(
                    rule_id="go-010", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=120,
        ),
        RuleDetectorBinding(
            detector_id="go_maintainability",
            detector_class=GoMaintainabilityDetector,
            config_model=GoMaintainabilityConfig,
            rules=[
                RuleBinding(
                    rule_id="go-020",
                    dogma_ids=_dogmas(
                        "ZEN-UNAMBIGUOUS-NAME",
                        "ZEN-EXPLICIT-INTENT",
                        "ZEN-VISIBLE-STATE",
                    ),
                )
            ],
            default_order=130,
        ),
        NonRuleDetectorBinding(
            detector_id="go_moderation",
            detector_class=GoModerationDetector,
            config_model=GoModerationConfig,
            default_order=140,
        ),
        RuleDetectorBinding(
            detector_id="go_naming_convention",
            detector_class=GoNamingConventionDetector,
            config_model=GoNamingConventionConfig,
            rules=[
                RuleBinding(rule_id="go-004", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME"))
            ],
            default_order=150,
        ),
        RuleDetectorBinding(
            detector_id="go_package_naming",
            detector_class=GoPackageNamingDetector,
            config_model=GoPackageNamingConfig,
            rules=[
                RuleBinding(
                    rule_id="go-008",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-UNAMBIGUOUS-NAME"),
                )
            ],
            default_order=160,
        ),
        RuleDetectorBinding(
            detector_id="go_package_state",
            detector_class=GoPackageStateDetector,
            config_model=GoPackageStateConfig,
            rules=[
                RuleBinding(
                    rule_id="go-009",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-VISIBLE-STATE"),
                )
            ],
            default_order=170,
        ),
        RuleDetectorBinding(
            detector_id="go_simplicity",
            detector_class=GoSimplicityDetector,
            config_model=GoSimplicityConfig,
            rules=[
                RuleBinding(
                    rule_id="go-016",
                    dogma_ids=_dogmas(
                        "ZEN-PROPORTIONATE-COMPLEXITY", "ZEN-RETURN-EARLY"
                    ),
                )
            ],
            default_order=180,
        ),
        RuleDetectorBinding(
            detector_id="go_single_purpose_package",
            detector_class=GoOrganizeResponsibilityDetector,
            config_model=GoSinglePurposePackageConfig,
            rules=[
                RuleBinding(
                    rule_id="go-013",
                    dogma_ids=_dogmas(
                        "ZEN-STRICT-FENCES", "ZEN-RETURN-EARLY", "ZEN-UNAMBIGUOUS-NAME"
                    ),
                )
            ],
            default_order=190,
        ),
        RuleDetectorBinding(
            detector_id="go_test_presence",
            detector_class=GoTestPresenceDetector,
            config_model=GoTestPresenceConfig,
            rules=[
                RuleBinding(
                    rule_id="go-019",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-VISIBLE-STATE"),
                    testing_ids=_testing("gotest"),
                    verified_testing_ids=_testing("gotest"),
                    projection_ids=_projection("go"),
                    verified_projection_ids=_projection("go"),
                )
            ],
            default_order=200,
        ),
        RuleDetectorBinding(
            detector_id="go_zero_value",
            detector_class=GoZeroValueDetector,
            config_model=GoZeroValueConfig,
            rules=[
                RuleBinding(
                    rule_id="go-003",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-EXPLICIT-INTENT"),
                )
            ],
            default_order=210,
        ),
    ],
)
