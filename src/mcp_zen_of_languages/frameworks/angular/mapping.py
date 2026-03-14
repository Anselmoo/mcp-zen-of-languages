"""Mapping module."""

from __future__ import annotations

from typing import Literal

from pydantic import create_model

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.frameworks.angular.detectors import AngularLazyRouteDetector
from mcp_zen_of_languages.frameworks.angular.detectors import AngularNoAnyDetector
from mcp_zen_of_languages.frameworks.angular.detectors import AngularOnPushDetector
from mcp_zen_of_languages.frameworks.angular.detectors import (
    AngularSelectorPrefixDetector,
)
from mcp_zen_of_languages.frameworks.angular.detectors import (
    AngularSubscriptionLifecycleDetector,
)
from mcp_zen_of_languages.frameworks.dogmas import framework_rule_dogmas
from mcp_zen_of_languages.languages.configs import DetectorConfig


def _rule_config(rule_id: str) -> type[DetectorConfig]:
    class_name = "".join(part.capitalize() for part in rule_id.split("-")) + "Config"
    return create_model(
        class_name,
        __base__=DetectorConfig,
        type=(Literal[rule_id], rule_id),
    )


DETECTOR_MAP = LanguageDetectorMap(
    language="angular",
    bindings=[
        DetectorBinding(
            detector_id="angular-005",
            detector_class=AngularLazyRouteDetector,
            config_model=_rule_config("angular-005"),
            rule_ids=["angular-005"],
            universal_dogma_ids=list(framework_rule_dogmas("angular-005")),
            default_order=10,
        ),
        DetectorBinding(
            detector_id="angular-002",
            detector_class=AngularNoAnyDetector,
            config_model=_rule_config("angular-002"),
            rule_ids=["angular-002"],
            universal_dogma_ids=list(framework_rule_dogmas("angular-002")),
            default_order=20,
        ),
        DetectorBinding(
            detector_id="angular-001",
            detector_class=AngularOnPushDetector,
            config_model=_rule_config("angular-001"),
            rule_ids=["angular-001"],
            universal_dogma_ids=list(framework_rule_dogmas("angular-001")),
            default_order=30,
        ),
        DetectorBinding(
            detector_id="angular-004",
            detector_class=AngularSelectorPrefixDetector,
            config_model=_rule_config("angular-004"),
            rule_ids=["angular-004"],
            universal_dogma_ids=list(framework_rule_dogmas("angular-004")),
            default_order=40,
        ),
        DetectorBinding(
            detector_id="angular-003",
            detector_class=AngularSubscriptionLifecycleDetector,
            config_model=_rule_config("angular-003"),
            rule_ids=["angular-003"],
            universal_dogma_ids=list(framework_rule_dogmas("angular-003")),
            default_order=50,
        ),
    ],
)
