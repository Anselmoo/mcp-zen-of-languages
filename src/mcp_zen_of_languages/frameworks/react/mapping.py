"""Mapping module."""

from __future__ import annotations

from typing import Literal

from pydantic import create_model

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.frameworks.dogmas import framework_rule_dogmas
from mcp_zen_of_languages.frameworks.react.detectors import ReactConditionalHookDetector
from mcp_zen_of_languages.frameworks.react.detectors import ReactDirectDomAccessDetector
from mcp_zen_of_languages.frameworks.react.detectors import ReactEffectCleanupDetector
from mcp_zen_of_languages.frameworks.react.detectors import ReactInlineHandlerDetector
from mcp_zen_of_languages.frameworks.react.detectors import ReactStableKeyDetector
from mcp_zen_of_languages.languages.configs import DetectorConfig


def _rule_config(rule_id: str) -> type[DetectorConfig]:
    class_name = "".join(part.capitalize() for part in rule_id.split("-")) + "Config"
    return create_model(
        class_name,
        __base__=DetectorConfig,
        type=(Literal[rule_id], rule_id),
    )


DETECTOR_MAP = LanguageDetectorMap(
    language="react",
    bindings=[
        DetectorBinding(
            detector_id="react-004",
            detector_class=ReactConditionalHookDetector,
            config_model=_rule_config("react-004"),
            rule_ids=["react-004"],
            universal_dogma_ids=list(framework_rule_dogmas("react-004")),
            default_order=10,
        ),
        DetectorBinding(
            detector_id="react-003",
            detector_class=ReactDirectDomAccessDetector,
            config_model=_rule_config("react-003"),
            rule_ids=["react-003"],
            universal_dogma_ids=list(framework_rule_dogmas("react-003")),
            default_order=20,
        ),
        DetectorBinding(
            detector_id="react-005",
            detector_class=ReactEffectCleanupDetector,
            config_model=_rule_config("react-005"),
            rule_ids=["react-005"],
            universal_dogma_ids=list(framework_rule_dogmas("react-005")),
            default_order=30,
        ),
        DetectorBinding(
            detector_id="react-002",
            detector_class=ReactInlineHandlerDetector,
            config_model=_rule_config("react-002"),
            rule_ids=["react-002"],
            universal_dogma_ids=list(framework_rule_dogmas("react-002")),
            default_order=40,
        ),
        DetectorBinding(
            detector_id="react-001",
            detector_class=ReactStableKeyDetector,
            config_model=_rule_config("react-001"),
            rule_ids=["react-001"],
            universal_dogma_ids=list(framework_rule_dogmas("react-001")),
            default_order=50,
        ),
    ],
)
