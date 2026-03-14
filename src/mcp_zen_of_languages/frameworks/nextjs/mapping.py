"""Mapping module."""

from __future__ import annotations

from typing import Literal

from pydantic import create_model

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.frameworks.nextjs.detectors import NextjsRuleDetector
from mcp_zen_of_languages.languages.configs import DetectorConfig


_RULE_IDS = ["nextjs-001", "nextjs-002", "nextjs-003", "nextjs-004", "nextjs-005"]


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
            detector_id=rule_id,
            detector_class=NextjsRuleDetector,
            config_model=_rule_config(rule_id),
            rule_ids=[rule_id],
            default_order=index * 10,
        )
        for index, rule_id in enumerate(_RULE_IDS, start=1)
    ],
)
