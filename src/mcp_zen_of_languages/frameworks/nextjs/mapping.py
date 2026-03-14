"""Mapping module."""

from __future__ import annotations

from typing import Literal

from pydantic import create_model

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.frameworks.dogmas import framework_rule_dogmas
from mcp_zen_of_languages.frameworks.nextjs.detectors import NextjsAppRouterDetector
from mcp_zen_of_languages.frameworks.nextjs.detectors import NextjsErrorResponseDetector
from mcp_zen_of_languages.frameworks.nextjs.detectors import (
    NextjsImageOptimizationDetector,
)
from mcp_zen_of_languages.frameworks.nextjs.detectors import NextjsLinkDetector
from mcp_zen_of_languages.frameworks.nextjs.detectors import NextjsServerDataDetector
from mcp_zen_of_languages.languages.configs import DetectorConfig


def _rule_config(rule_id: str) -> type[DetectorConfig]:
    class_name = "".join(part.capitalize() for part in rule_id.split("-")) + "Config"
    return create_model(
        class_name,
        __base__=DetectorConfig,
        type=(Literal[rule_id], rule_id),
    )


DETECTOR_MAP = LanguageDetectorMap(
    language="nextjs",
    bindings=[
        DetectorBinding(
            detector_id="nextjs-003",
            detector_class=NextjsAppRouterDetector,
            config_model=_rule_config("nextjs-003"),
            rule_ids=["nextjs-003"],
            universal_dogma_ids=list(framework_rule_dogmas("nextjs-003")),
            default_order=10,
        ),
        DetectorBinding(
            detector_id="nextjs-004",
            detector_class=NextjsErrorResponseDetector,
            config_model=_rule_config("nextjs-004"),
            rule_ids=["nextjs-004"],
            universal_dogma_ids=list(framework_rule_dogmas("nextjs-004")),
            default_order=20,
        ),
        DetectorBinding(
            detector_id="nextjs-002",
            detector_class=NextjsImageOptimizationDetector,
            config_model=_rule_config("nextjs-002"),
            rule_ids=["nextjs-002"],
            universal_dogma_ids=list(framework_rule_dogmas("nextjs-002")),
            default_order=30,
        ),
        DetectorBinding(
            detector_id="nextjs-001",
            detector_class=NextjsLinkDetector,
            config_model=_rule_config("nextjs-001"),
            rule_ids=["nextjs-001"],
            universal_dogma_ids=list(framework_rule_dogmas("nextjs-001")),
            default_order=40,
        ),
        DetectorBinding(
            detector_id="nextjs-005",
            detector_class=NextjsServerDataDetector,
            config_model=_rule_config("nextjs-005"),
            rule_ids=["nextjs-005"],
            universal_dogma_ids=list(framework_rule_dogmas("nextjs-005")),
            default_order=50,
        ),
    ],
)
