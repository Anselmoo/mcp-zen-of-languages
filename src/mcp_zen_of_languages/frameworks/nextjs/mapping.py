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
from mcp_zen_of_languages.frameworks.nextjs.detectors import NextjsAppRouterDetector
from mcp_zen_of_languages.frameworks.nextjs.detectors import NextjsErrorResponseDetector
from mcp_zen_of_languages.frameworks.nextjs.detectors import (
    NextjsImageOptimizationDetector,
)
from mcp_zen_of_languages.frameworks.nextjs.detectors import NextjsLinkDetector
from mcp_zen_of_languages.frameworks.nextjs.detectors import NextjsServerDataDetector


DETECTOR_MAP = LanguageDetectorMap(
    language="nextjs",
    bindings=[
        RuleDetectorBinding(
            detector_id="nextjs-001",
            detector_class=NextjsLinkDetector,
            config_model=_rule_config("nextjs-001"),
            rules=[
                RuleBinding(
                    rule_id="nextjs-001",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("jest"),
                    projection_ids=_projection("nextjs"),
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="nextjs-002",
            detector_class=NextjsImageOptimizationDetector,
            config_model=_rule_config("nextjs-002"),
            rules=[
                RuleBinding(
                    rule_id="nextjs-002",
                    dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
                    testing_ids=_testing("jest"),
                    projection_ids=_projection("nextjs"),
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="nextjs-003",
            detector_class=NextjsAppRouterDetector,
            config_model=_rule_config("nextjs-003"),
            rules=[
                RuleBinding(
                    rule_id="nextjs-003",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("jest"),
                    projection_ids=_projection("nextjs"),
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="nextjs-004",
            detector_class=NextjsErrorResponseDetector,
            config_model=_rule_config("nextjs-004"),
            rules=[
                RuleBinding(
                    rule_id="nextjs-004",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-FAIL-FAST"),
                    testing_ids=_testing("jest"),
                    projection_ids=_projection("nextjs"),
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="nextjs-005",
            detector_class=NextjsServerDataDetector,
            config_model=_rule_config("nextjs-005"),
            rules=[
                RuleBinding(
                    rule_id="nextjs-005",
                    dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
                    testing_ids=_testing("jest"),
                    projection_ids=_projection("nextjs"),
                )
            ],
            default_order=50,
        ),
    ],
)
