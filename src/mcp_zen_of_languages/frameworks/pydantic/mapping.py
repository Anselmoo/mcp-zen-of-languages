"""Mapping module."""

from __future__ import annotations

from typing import Literal

from pydantic import create_model

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.frameworks.pydantic.detectors import PydanticRuleDetector
from mcp_zen_of_languages.languages.configs import DetectorConfig


_RULE_IDS = [
    "pydantic-001",
    "pydantic-002",
    "pydantic-003",
    "pydantic-004",
    "pydantic-005",
    "pydantic-006",
    "pydantic-007",
    "pydantic-008",
]


def _rule_config(rule_id: str) -> type[DetectorConfig]:
    class_name = "".join(part.capitalize() for part in rule_id.split("-")) + "Config"
    return create_model(
        class_name,
        __base__=DetectorConfig,
        type=(Literal[rule_id], rule_id),
    )


DETECTOR_MAP = LanguageDetectorMap(
    language="pydantic",
    bindings=[
        DetectorBinding(
            detector_id=rule_id,
            detector_class=PydanticRuleDetector,
            config_model=_rule_config(rule_id),
            rule_ids=[rule_id],
            default_order=index * 10,
        )
        for index, rule_id in enumerate(_RULE_IDS, start=1)
    ],
)
