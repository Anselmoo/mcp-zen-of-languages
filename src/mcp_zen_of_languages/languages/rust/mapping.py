"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
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


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="rust",
    bindings=[
        RuleDetectorBinding(
            detector_id="rust_unwrap_usage",
            detector_class=RustUnwrapUsageDetector,
            config_model=RustUnwrapUsageConfig,
            rule_ids=["rust-001"],
            universal_dogma_ids=_dogmas("ZEN-FAIL-FAST"),
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="rust-002",
            detector_class=RustTypeSafetyDetector,
            config_model=RustTypeSafetyConfig,
            rule_ids=["rust-002"],
            universal_dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-VISIBLE-STATE"),
            default_order=15,
        ),
        RuleDetectorBinding(
            detector_id="rust-003",
            detector_class=RustIteratorPreferenceDetector,
            config_model=RustIteratorPreferenceConfig,
            rule_ids=["rust-003"],
            universal_dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION"),
            default_order=18,
        ),
        RuleDetectorBinding(
            detector_id="rust_unsafe_blocks",
            detector_class=RustUnsafeBlocksDetector,
            config_model=RustUnsafeBlocksConfig,
            rule_ids=["rust-008"],
            universal_dogma_ids=_dogmas("ZEN-FAIL-FAST"),
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="rust_clone_overhead",
            detector_class=RustCloneOverheadDetector,
            config_model=RustCloneOverheadConfig,
            rule_ids=["rust-004"],
            universal_dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="rust_error_handling",
            detector_class=RustErrorHandlingDetector,
            config_model=RustErrorHandlingConfig,
            rule_ids=["rust-001"],
            universal_dogma_ids=_dogmas("ZEN-FAIL-FAST"),
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="rust-005",
            detector_class=RustMustUseDetector,
            config_model=RustMustUseConfig,
            rule_ids=["rust-005"],
            universal_dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="rust-006",
            detector_class=RustDebugDeriveDetector,
            config_model=RustDebugDeriveConfig,
            rule_ids=["rust-006"],
            universal_dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="rust-007",
            detector_class=RustNewtypePatternDetector,
            config_model=RustNewtypePatternConfig,
            rule_ids=["rust-007"],
            universal_dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION"),
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="rust-009",
            detector_class=RustStdTraitsDetector,
            config_model=RustStdTraitsConfig,
            rule_ids=["rust-009"],
            universal_dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION"),
            default_order=80,
        ),
        RuleDetectorBinding(
            detector_id="rust-010",
            detector_class=RustEnumOverBoolDetector,
            config_model=RustEnumOverBoolConfig,
            rule_ids=["rust-010"],
            universal_dogma_ids=_dogmas(
                "ZEN-RIGHT-ABSTRACTION", "ZEN-EXPLICIT-INTENT", "ZEN-VISIBLE-STATE"
            ),
            default_order=90,
        ),
        RuleDetectorBinding(
            detector_id="rust-011",
            detector_class=RustLifetimeUsageDetector,
            config_model=RustLifetimeUsageConfig,
            rule_ids=["rust-011"],
            universal_dogma_ids=_dogmas("ZEN-VISIBLE-STATE", "ZEN-EXPLICIT-INTENT"),
            default_order=100,
        ),
        RuleDetectorBinding(
            detector_id="rust-012",
            detector_class=RustInteriorMutabilityDetector,
            config_model=RustInteriorMutabilityConfig,
            rule_ids=["rust-012"],
            universal_dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-VISIBLE-STATE"),
            default_order=110,
        ),
        RuleDetectorBinding(
            detector_id="rust_send_sync",
            detector_class=RustSendSyncDetector,
            config_model=RustSendSyncConfig,
            rule_ids=["rust-013"],
            universal_dogma_ids=_dogmas("ZEN-VISIBLE-STATE"),
            default_order=120,
        ),
        RuleDetectorBinding(
            detector_id="rust_error_traits",
            detector_class=RustErrorTraitsDetector,
            config_model=RustErrorTraitsConfig,
            rule_ids=["rust-014"],
            universal_dogma_ids=_dogmas("ZEN-FAIL-FAST"),
            default_order=130,
        ),
        RuleDetectorBinding(
            detector_id="rust_naming",
            detector_class=RustNamingDetector,
            config_model=RustNamingConfig,
            rule_ids=["rust-015"],
            universal_dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME"),
            default_order=140,
        ),
        RuleDetectorBinding(
            detector_id="rust_default_impl",
            detector_class=RustDefaultImplDetector,
            config_model=RustDefaultImplConfig,
            rule_ids=["rust-016"],
            universal_dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-VISIBLE-STATE"),
            default_order=150,
        ),
        RuleDetectorBinding(
            detector_id="rust_from_into",
            detector_class=RustFromIntoDetector,
            config_model=RustFromIntoConfig,
            rule_ids=["rust-017"],
            universal_dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION"),
            default_order=160,
        ),
    ],
)
