"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import DetectorGearbox
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.core.universal_mapping import UNIVERSAL_DETECTOR_MAP
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


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="go",
    bindings=[
        DetectorBinding(
            detector_id="go_error_handling",
            detector_class=GoErrorHandlingDetector,
            config_model=GoErrorHandlingConfig,
            rule_ids=["go-001"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="go_interface_size",
            detector_class=GoInterfaceSizeDetector,
            config_model=GoInterfaceSizeConfig,
            rule_ids=["go-010"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="go_context_usage",
            detector_class=GoContextUsageDetector,
            config_model=GoContextUsageConfig,
            rule_ids=["go-011"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="go_defer_usage",
            detector_class=GoDeferUsageDetector,
            config_model=GoDeferUsageConfig,
            rule_ids=["go-007"],
            default_order=40,
        ),
        DetectorBinding(
            detector_id="go_naming_convention",
            detector_class=GoNamingConventionDetector,
            config_model=GoNamingConventionConfig,
            rule_ids=["go-004"],
            default_order=50,
        ),
        DetectorBinding(
            detector_id="go_interface_return",
            detector_class=GoInterfaceReturnDetector,
            config_model=GoInterfaceReturnConfig,
            rule_ids=["go-002"],
            default_order=60,
        ),
        DetectorBinding(
            detector_id="go_zero_value",
            detector_class=GoZeroValueDetector,
            config_model=GoZeroValueConfig,
            rule_ids=["go-003"],
            default_order=70,
        ),
        DetectorBinding(
            detector_id="go_interface_pointer",
            detector_class=GoInterfacePointerDetector,
            config_model=GoInterfacePointerConfig,
            rule_ids=["go-005"],
            default_order=80,
        ),
        DetectorBinding(
            detector_id="go_goroutine_leaks",
            detector_class=GoGoroutineLeakDetector,
            config_model=GoGoroutineLeakConfig,
            rule_ids=["go-006"],
            default_order=90,
        ),
        DetectorBinding(
            detector_id="go_package_naming",
            detector_class=GoPackageNamingDetector,
            config_model=GoPackageNamingConfig,
            rule_ids=["go-008"],
            default_order=100,
        ),
        DetectorBinding(
            detector_id="go_package_state",
            detector_class=GoPackageStateDetector,
            config_model=GoPackageStateConfig,
            rule_ids=["go-009"],
            default_order=110,
        ),
        DetectorBinding(
            detector_id="go_init_usage",
            detector_class=GoInitUsageDetector,
            config_model=GoInitUsageConfig,
            rule_ids=["go-012"],
            default_order=120,
        ),
        DetectorBinding(
            detector_id="go_single_purpose_package",
            detector_class=GoOrganizeResponsibilityDetector,
            config_model=GoSinglePurposePackageConfig,
            rule_ids=["go-013"],
            default_order=130,
        ),
        DetectorBinding(
            detector_id="go_embedding_depth",
            detector_class=GoEmbeddingDepthDetector,
            config_model=GoEmbeddingDepthConfig,
            rule_ids=["go-014"],
            default_order=135,
        ),
        DetectorBinding(
            detector_id="go_early_return",
            detector_class=GoEarlyReturnDetector,
            config_model=GoEarlyReturnConfig,
            rule_ids=["go-017"],
            default_order=140,
        ),
        DetectorBinding(
            detector_id="go_concurrency_caller",
            detector_class=GoConcurrencyCallerDetector,
            config_model=GoConcurrencyCallerConfig,
            rule_ids=["go-015"],
            default_order=150,
        ),
        DetectorBinding(
            detector_id="go_simplicity",
            detector_class=GoSimplicityDetector,
            config_model=GoSimplicityConfig,
            rule_ids=["go-016"],
            default_order=160,
        ),
        DetectorBinding(
            detector_id="go_test_presence",
            detector_class=GoTestPresenceDetector,
            config_model=GoTestPresenceConfig,
            rule_ids=["go-019"],
            default_order=170,
        ),
        DetectorBinding(
            detector_id="go_benchmark",
            detector_class=GoBenchmarkDetector,
            config_model=GoBenchmarkConfig,
            rule_ids=["go-018"],
            default_order=180,
        ),
        DetectorBinding(
            detector_id="go_moderation",
            detector_class=GoModerationDetector,
            config_model=GoModerationConfig,
            rule_ids=[],
            universal_dogma_ids=["ZEN-VISIBLE-STATE", "ZEN-PROPORTIONATE-COMPLEXITY"],
            default_order=190,
        ),
        DetectorBinding(
            detector_id="go_maintainability",
            detector_class=GoMaintainabilityDetector,
            config_model=GoMaintainabilityConfig,
            rule_ids=["go-020"],
            default_order=200,
        ),
    ],
)

GEARBOX = DetectorGearbox(language="go")
GEARBOX.extend(DETECTOR_MAP.bindings)
GEARBOX.extend(UNIVERSAL_DETECTOR_MAP.bindings)
DETECTOR_MAP = GEARBOX.build_map()
