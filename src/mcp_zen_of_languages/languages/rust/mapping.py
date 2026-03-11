"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import DetectorGearbox
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.core.universal_mapping import UNIVERSAL_DETECTOR_MAP
from mcp_zen_of_languages.languages.configs import RustCloneOverheadConfig
from mcp_zen_of_languages.languages.configs import RustDebugDeriveConfig
from mcp_zen_of_languages.languages.configs import RustDefaultImplConfig
from mcp_zen_of_languages.languages.configs import RustEnumOverBoolConfig
from mcp_zen_of_languages.languages.configs import RustErrorHandlingConfig
from mcp_zen_of_languages.languages.configs import RustErrorTraitsConfig
from mcp_zen_of_languages.languages.configs import RustFromIntoConfig
from mcp_zen_of_languages.languages.configs import RustInteriorMutabilityConfig
from mcp_zen_of_languages.languages.configs import RustIteratorPreferenceConfig
from mcp_zen_of_languages.languages.configs import RustLifetimeUsageConfig
from mcp_zen_of_languages.languages.configs import RustMustUseConfig
from mcp_zen_of_languages.languages.configs import RustNamingConfig
from mcp_zen_of_languages.languages.configs import RustNewtypePatternConfig
from mcp_zen_of_languages.languages.configs import RustSendSyncConfig
from mcp_zen_of_languages.languages.configs import RustStdTraitsConfig
from mcp_zen_of_languages.languages.configs import RustTypeSafetyConfig
from mcp_zen_of_languages.languages.configs import RustUnsafeBlocksConfig
from mcp_zen_of_languages.languages.configs import RustUnwrapUsageConfig
from mcp_zen_of_languages.languages.rust.detectors import RustCloneOverheadDetector
from mcp_zen_of_languages.languages.rust.detectors import RustDebugDeriveDetector
from mcp_zen_of_languages.languages.rust.detectors import RustDefaultImplDetector
from mcp_zen_of_languages.languages.rust.detectors import RustEnumOverBoolDetector
from mcp_zen_of_languages.languages.rust.detectors import RustErrorHandlingDetector
from mcp_zen_of_languages.languages.rust.detectors import RustErrorTraitsDetector
from mcp_zen_of_languages.languages.rust.detectors import RustFromIntoDetector
from mcp_zen_of_languages.languages.rust.detectors import RustInteriorMutabilityDetector
from mcp_zen_of_languages.languages.rust.detectors import RustIteratorPreferenceDetector
from mcp_zen_of_languages.languages.rust.detectors import RustLifetimeUsageDetector
from mcp_zen_of_languages.languages.rust.detectors import RustMustUseDetector
from mcp_zen_of_languages.languages.rust.detectors import RustNamingDetector
from mcp_zen_of_languages.languages.rust.detectors import RustNewtypePatternDetector
from mcp_zen_of_languages.languages.rust.detectors import RustSendSyncDetector
from mcp_zen_of_languages.languages.rust.detectors import RustStdTraitsDetector
from mcp_zen_of_languages.languages.rust.detectors import RustTypeSafetyDetector
from mcp_zen_of_languages.languages.rust.detectors import RustUnsafeBlocksDetector
from mcp_zen_of_languages.languages.rust.detectors import RustUnwrapUsageDetector


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="rust",
    bindings=[
        DetectorBinding(
            detector_id="rust_unwrap_usage",
            detector_class=RustUnwrapUsageDetector,
            config_model=RustUnwrapUsageConfig,
            rule_ids=["rust-001"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="rust-002",
            detector_class=RustTypeSafetyDetector,
            config_model=RustTypeSafetyConfig,
            rule_ids=["rust-002"],
            default_order=15,
        ),
        DetectorBinding(
            detector_id="rust-003",
            detector_class=RustIteratorPreferenceDetector,
            config_model=RustIteratorPreferenceConfig,
            rule_ids=["rust-003"],
            default_order=18,
        ),
        DetectorBinding(
            detector_id="rust_unsafe_blocks",
            detector_class=RustUnsafeBlocksDetector,
            config_model=RustUnsafeBlocksConfig,
            rule_ids=["rust-008"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="rust_clone_overhead",
            detector_class=RustCloneOverheadDetector,
            config_model=RustCloneOverheadConfig,
            rule_ids=["rust-004"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="rust_error_handling",
            detector_class=RustErrorHandlingDetector,
            config_model=RustErrorHandlingConfig,
            rule_ids=["rust-001"],
            default_order=40,
        ),
        DetectorBinding(
            detector_id="rust-005",
            detector_class=RustMustUseDetector,
            config_model=RustMustUseConfig,
            rule_ids=["rust-005"],
            default_order=50,
        ),
        DetectorBinding(
            detector_id="rust-006",
            detector_class=RustDebugDeriveDetector,
            config_model=RustDebugDeriveConfig,
            rule_ids=["rust-006"],
            default_order=60,
        ),
        DetectorBinding(
            detector_id="rust-007",
            detector_class=RustNewtypePatternDetector,
            config_model=RustNewtypePatternConfig,
            rule_ids=["rust-007"],
            default_order=70,
        ),
        DetectorBinding(
            detector_id="rust-009",
            detector_class=RustStdTraitsDetector,
            config_model=RustStdTraitsConfig,
            rule_ids=["rust-009"],
            default_order=80,
        ),
        DetectorBinding(
            detector_id="rust-010",
            detector_class=RustEnumOverBoolDetector,
            config_model=RustEnumOverBoolConfig,
            rule_ids=["rust-010"],
            default_order=90,
        ),
        DetectorBinding(
            detector_id="rust-011",
            detector_class=RustLifetimeUsageDetector,
            config_model=RustLifetimeUsageConfig,
            rule_ids=["rust-011"],
            default_order=100,
        ),
        DetectorBinding(
            detector_id="rust-012",
            detector_class=RustInteriorMutabilityDetector,
            config_model=RustInteriorMutabilityConfig,
            rule_ids=["rust-012"],
            default_order=110,
        ),
        DetectorBinding(
            detector_id="rust_send_sync",
            detector_class=RustSendSyncDetector,
            config_model=RustSendSyncConfig,
            rule_ids=["rust-013"],
            default_order=120,
        ),
        DetectorBinding(
            detector_id="rust_error_traits",
            detector_class=RustErrorTraitsDetector,
            config_model=RustErrorTraitsConfig,
            rule_ids=["rust-014"],
            default_order=130,
        ),
        DetectorBinding(
            detector_id="rust_naming",
            detector_class=RustNamingDetector,
            config_model=RustNamingConfig,
            rule_ids=["rust-015"],
            default_order=140,
        ),
        DetectorBinding(
            detector_id="rust_default_impl",
            detector_class=RustDefaultImplDetector,
            config_model=RustDefaultImplConfig,
            rule_ids=["rust-016"],
            default_order=150,
        ),
        DetectorBinding(
            detector_id="rust_from_into",
            detector_class=RustFromIntoDetector,
            config_model=RustFromIntoConfig,
            rule_ids=["rust-017"],
            default_order=160,
        ),
    ],
)

GEARBOX = DetectorGearbox(language="rust")
GEARBOX.extend(DETECTOR_MAP.bindings)
GEARBOX.extend(UNIVERSAL_DETECTOR_MAP.bindings)
DETECTOR_MAP = GEARBOX.build_map()
