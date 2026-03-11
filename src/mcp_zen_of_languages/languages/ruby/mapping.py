"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import DetectorGearbox
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.core.universal_mapping import UNIVERSAL_DETECTOR_MAP
from mcp_zen_of_languages.languages.configs import RubyBlockPreferenceConfig
from mcp_zen_of_languages.languages.configs import RubyDryConfig
from mcp_zen_of_languages.languages.configs import RubyExpressiveSyntaxConfig
from mcp_zen_of_languages.languages.configs import RubyGuardClauseConfig
from mcp_zen_of_languages.languages.configs import RubyMetaprogrammingConfig
from mcp_zen_of_languages.languages.configs import RubyMethodChainConfig
from mcp_zen_of_languages.languages.configs import RubyMethodNamingConfig
from mcp_zen_of_languages.languages.configs import RubyMonkeyPatchConfig
from mcp_zen_of_languages.languages.configs import RubyNamingConventionConfig
from mcp_zen_of_languages.languages.configs import RubyPreferFailConfig
from mcp_zen_of_languages.languages.configs import RubySymbolKeysConfig
from mcp_zen_of_languages.languages.ruby.detectors import RubyBlockPreferenceDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubyDryDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubyExpressiveSyntaxDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubyGuardClauseDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubyMetaprogrammingDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubyMethodChainDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubyMethodNamingDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubyMonkeyPatchDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubyNamingConventionDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubyPreferFailDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubySymbolKeysDetector


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="ruby",
    bindings=[
        DetectorBinding(
            detector_id="ruby_naming_convention",
            detector_class=RubyNamingConventionDetector,
            config_model=RubyNamingConventionConfig,
            rule_ids=["ruby-001"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="ruby_method_chain",
            detector_class=RubyMethodChainDetector,
            config_model=RubyMethodChainConfig,
            rule_ids=["ruby-006"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="ruby_dry",
            detector_class=RubyDryDetector,
            config_model=RubyDryConfig,
            rule_ids=["ruby-002"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="ruby_block_preference",
            detector_class=RubyBlockPreferenceDetector,
            config_model=RubyBlockPreferenceConfig,
            rule_ids=["ruby-003"],
            default_order=40,
        ),
        DetectorBinding(
            detector_id="ruby_monkey_patch",
            detector_class=RubyMonkeyPatchDetector,
            config_model=RubyMonkeyPatchConfig,
            rule_ids=["ruby-004"],
            default_order=50,
        ),
        DetectorBinding(
            detector_id="ruby_method_naming",
            detector_class=RubyMethodNamingDetector,
            config_model=RubyMethodNamingConfig,
            rule_ids=["ruby-005"],
            default_order=60,
        ),
        DetectorBinding(
            detector_id="ruby_symbol_keys",
            detector_class=RubySymbolKeysDetector,
            config_model=RubySymbolKeysConfig,
            rule_ids=["ruby-007"],
            default_order=70,
        ),
        DetectorBinding(
            detector_id="ruby_guard_clause",
            detector_class=RubyGuardClauseDetector,
            config_model=RubyGuardClauseConfig,
            rule_ids=["ruby-008"],
            default_order=80,
        ),
        DetectorBinding(
            detector_id="ruby_metaprogramming",
            detector_class=RubyMetaprogrammingDetector,
            config_model=RubyMetaprogrammingConfig,
            rule_ids=["ruby-009"],
            default_order=90,
        ),
        DetectorBinding(
            detector_id="ruby_expressive_syntax",
            detector_class=RubyExpressiveSyntaxDetector,
            config_model=RubyExpressiveSyntaxConfig,
            rule_ids=["ruby-010"],
            default_order=100,
        ),
        DetectorBinding(
            detector_id="ruby_prefer_fail",
            detector_class=RubyPreferFailDetector,
            config_model=RubyPreferFailConfig,
            rule_ids=["ruby-011"],
            default_order=110,
        ),
    ],
)

GEARBOX = DetectorGearbox(language="ruby")
GEARBOX.extend(DETECTOR_MAP.bindings)
GEARBOX.extend(UNIVERSAL_DETECTOR_MAP.bindings)
DETECTOR_MAP = GEARBOX.build_map()
