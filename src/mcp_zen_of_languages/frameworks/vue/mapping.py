"""Mapping module."""

from __future__ import annotations

from typing import Literal

from pydantic import create_model

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.frameworks.vue.detectors import VueConditionalLoopDetector
from mcp_zen_of_languages.frameworks.vue.detectors import VueListKeyDetector
from mcp_zen_of_languages.frameworks.vue.detectors import VueMultiWordNameDetector
from mcp_zen_of_languages.frameworks.vue.detectors import VuePropMutationDetector
from mcp_zen_of_languages.frameworks.vue.detectors import VueTypedPropsDetector
from mcp_zen_of_languages.languages.configs import DetectorConfig


def _rule_config(rule_id: str) -> type[DetectorConfig]:
    class_name = "".join(part.capitalize() for part in rule_id.split("-")) + "Config"
    return create_model(
        class_name,
        __base__=DetectorConfig,
        type=(Literal[rule_id], rule_id),
    )


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
