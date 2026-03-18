"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.frameworks.mapping_helpers import dogma_ids as _dogmas
from mcp_zen_of_languages.frameworks.mapping_helpers import (
    make_rule_config as _rule_config,
)
from mcp_zen_of_languages.frameworks.mapping_helpers import (
    projection_ids as _projection,
)
from mcp_zen_of_languages.frameworks.mapping_helpers import testing_ids as _testing
from mcp_zen_of_languages.frameworks.react.detectors import ReactConditionalHookDetector
from mcp_zen_of_languages.frameworks.react.detectors import ReactDirectDomAccessDetector
from mcp_zen_of_languages.frameworks.react.detectors import ReactEffectCleanupDetector
from mcp_zen_of_languages.frameworks.react.detectors import ReactInlineHandlerDetector
from mcp_zen_of_languages.frameworks.react.detectors import ReactStableKeyDetector


DETECTOR_MAP = LanguageDetectorMap(
    language="react",
    bindings=[
        RuleDetectorBinding(
            detector_id="react-004",
            detector_class=ReactConditionalHookDetector,
            config_model=_rule_config("react-004"),
            rules=[
                RuleBinding(
                    rule_id="react-004",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("jest"),
                    projection_ids=_projection("nextjs"),
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="react-003",
            detector_class=ReactDirectDomAccessDetector,
            config_model=_rule_config("react-003"),
            rules=[
                RuleBinding(
                    rule_id="react-003",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-STRICT-FENCES"),
                    verified_dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION"),
                    testing_ids=_testing("jest"),
                    projection_ids=_projection("nextjs"),
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="react-005",
            detector_class=ReactEffectCleanupDetector,
            config_model=_rule_config("react-005"),
            rules=[
                RuleBinding(
                    rule_id="react-005",
                    dogma_ids=_dogmas("ZEN-FAIL-FAST", "ZEN-STRICT-FENCES"),
                    verified_dogma_ids=_dogmas("ZEN-FAIL-FAST"),
                    testing_ids=_testing("jest"),
                    projection_ids=_projection("nextjs"),
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="react-002",
            detector_class=ReactInlineHandlerDetector,
            config_model=_rule_config("react-002"),
            rules=[
                RuleBinding(
                    rule_id="react-002",
                    dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
                    testing_ids=_testing("jest"),
                    projection_ids=_projection("nextjs"),
                    verified_projection_ids=[],
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="react-001",
            detector_class=ReactStableKeyDetector,
            config_model=_rule_config("react-001"),
            rules=[
                RuleBinding(
                    rule_id="react-001",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-VISIBLE-STATE"),
                    verified_dogma_ids=_dogmas("ZEN-VISIBLE-STATE"),
                    testing_ids=_testing("jest"),
                    projection_ids=_projection("nextjs"),
                )
            ],
            default_order=50,
        ),
    ],
)
