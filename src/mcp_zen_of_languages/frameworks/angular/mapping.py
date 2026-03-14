"""Mapping module."""

from __future__ import annotations

from typing import Literal

from pydantic import create_model

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.frameworks.angular.detectors import AngularLazyRouteDetector
from mcp_zen_of_languages.frameworks.angular.detectors import AngularNoAnyDetector
from mcp_zen_of_languages.frameworks.angular.detectors import AngularOnPushDetector
from mcp_zen_of_languages.frameworks.angular.detectors import (
    AngularSelectorPrefixDetector,
)
from mcp_zen_of_languages.frameworks.angular.detectors import (
    AngularSubscriptionLifecycleDetector,
)
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


DETECTOR_MAP = LanguageDetectorMap(
    language="angular",
    bindings=[
        RuleDetectorBinding(
            detector_id="angular-005",
            detector_class=AngularLazyRouteDetector,
            config_model=_rule_config("angular-005"),
            rules=[
                RuleBinding(
                    rule_id="angular-005",
                    dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="angular-002",
            detector_class=AngularNoAnyDetector,
            config_model=_rule_config("angular-002"),
            rules=[
                RuleBinding(
                    rule_id="angular-002", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="angular-001",
            detector_class=AngularOnPushDetector,
            config_model=_rule_config("angular-001"),
            rules=[
                RuleBinding(
                    rule_id="angular-001",
                    dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="angular-004",
            detector_class=AngularSelectorPrefixDetector,
            config_model=_rule_config("angular-004"),
            rules=[
                RuleBinding(
                    rule_id="angular-004", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="angular-003",
            detector_class=AngularSubscriptionLifecycleDetector,
            config_model=_rule_config("angular-003"),
            rules=[
                RuleBinding(
                    rule_id="angular-003",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-EXPLICIT-INTENT"),
                )
            ],
            default_order=50,
        ),
    ],
)
