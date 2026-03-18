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
from mcp_zen_of_languages.frameworks.vue.detectors import VueConditionalLoopDetector
from mcp_zen_of_languages.frameworks.vue.detectors import VueListKeyDetector
from mcp_zen_of_languages.frameworks.vue.detectors import VueMultiWordNameDetector
from mcp_zen_of_languages.frameworks.vue.detectors import VuePropMutationDetector
from mcp_zen_of_languages.frameworks.vue.detectors import VueTypedPropsDetector


DETECTOR_MAP = LanguageDetectorMap(
    language="vue",
    bindings=[
        RuleDetectorBinding(
            detector_id="vue-001",
            detector_class=VueMultiWordNameDetector,
            config_model=_rule_config("vue-001"),
            rules=[
                RuleBinding(
                    rule_id="vue-001",
                    dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME"),
                    testing_ids=_testing("jest"),
                    projection_ids=_projection("vue"),
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="vue-002",
            detector_class=VueTypedPropsDetector,
            config_model=_rule_config("vue-002"),
            rules=[
                RuleBinding(
                    rule_id="vue-002",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("jest"),
                    projection_ids=_projection("vue"),
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="vue-003",
            detector_class=VueListKeyDetector,
            config_model=_rule_config("vue-003"),
            rules=[
                RuleBinding(
                    rule_id="vue-003",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-VISIBLE-STATE"),
                    testing_ids=_testing("jest"),
                    projection_ids=_projection("vue"),
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="vue-004",
            detector_class=VueConditionalLoopDetector,
            config_model=_rule_config("vue-004"),
            rules=[
                RuleBinding(
                    rule_id="vue-004",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("jest"),
                    projection_ids=_projection("vue"),
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="vue-005",
            detector_class=VuePropMutationDetector,
            config_model=_rule_config("vue-005"),
            rules=[
                RuleBinding(
                    rule_id="vue-005",
                    dogma_ids=_dogmas("ZEN-VISIBLE-STATE", "ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("jest"),
                    projection_ids=_projection("vue"),
                )
            ],
            default_order=50,
        ),
    ],
)
