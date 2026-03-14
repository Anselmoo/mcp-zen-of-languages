"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
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


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="ruby",
    bindings=[
        RuleDetectorBinding(
            detector_id="ruby_naming_convention",
            detector_class=RubyNamingConventionDetector,
            config_model=RubyNamingConventionConfig,
            rules=[
                RuleBinding(
                    rule_id="ruby-001", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="ruby_method_chain",
            detector_class=RubyMethodChainDetector,
            config_model=RubyMethodChainConfig,
            rules=[
                RuleBinding(
                    rule_id="ruby-006", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="ruby_dry",
            detector_class=RubyDryDetector,
            config_model=RubyDryConfig,
            rules=[
                RuleBinding(
                    rule_id="ruby-002", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="ruby_block_preference",
            detector_class=RubyBlockPreferenceDetector,
            config_model=RubyBlockPreferenceConfig,
            rules=[
                RuleBinding(
                    rule_id="ruby-003",
                    dogma_ids=_dogmas(
                        "ZEN-RIGHT-ABSTRACTION", "ZEN-PROPORTIONATE-COMPLEXITY"
                    ),
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="ruby_monkey_patch",
            detector_class=RubyMonkeyPatchDetector,
            config_model=RubyMonkeyPatchConfig,
            rules=[
                RuleBinding(
                    rule_id="ruby-004", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="ruby_method_naming",
            detector_class=RubyMethodNamingDetector,
            config_model=RubyMethodNamingConfig,
            rules=[
                RuleBinding(
                    rule_id="ruby-005", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="ruby_symbol_keys",
            detector_class=RubySymbolKeysDetector,
            config_model=RubySymbolKeysConfig,
            rules=[
                RuleBinding(
                    rule_id="ruby-007",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-UNAMBIGUOUS-NAME"),
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="ruby_guard_clause",
            detector_class=RubyGuardClauseDetector,
            config_model=RubyGuardClauseConfig,
            rules=[
                RuleBinding(rule_id="ruby-008", dogma_ids=_dogmas("ZEN-RETURN-EARLY"))
            ],
            default_order=80,
        ),
        RuleDetectorBinding(
            detector_id="ruby_metaprogramming",
            detector_class=RubyMetaprogrammingDetector,
            config_model=RubyMetaprogrammingConfig,
            rules=[
                RuleBinding(
                    rule_id="ruby-009",
                    dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
                )
            ],
            default_order=90,
        ),
        RuleDetectorBinding(
            detector_id="ruby_expressive_syntax",
            detector_class=RubyExpressiveSyntaxDetector,
            config_model=RubyExpressiveSyntaxConfig,
            rules=[
                RuleBinding(
                    rule_id="ruby-010", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=100,
        ),
        RuleDetectorBinding(
            detector_id="ruby_prefer_fail",
            detector_class=RubyPreferFailDetector,
            config_model=RubyPreferFailConfig,
            rules=[RuleBinding(rule_id="ruby-011", dogma_ids=_dogmas("ZEN-FAIL-FAST"))],
            default_order=110,
        ),
    ],
)
