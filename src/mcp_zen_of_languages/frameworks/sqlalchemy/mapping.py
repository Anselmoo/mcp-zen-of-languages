"""Mapping module."""

from __future__ import annotations

from typing import Literal

from pydantic import create_model

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.frameworks.sqlalchemy.detectors import SqlalchemyRuleDetector
from mcp_zen_of_languages.languages.configs import DetectorConfig


_RULE_IDS = [
    "sqlalchemy-001",
    "sqlalchemy-002",
    "sqlalchemy-003",
    "sqlalchemy-004",
    "sqlalchemy-005",
    "sqlalchemy-006",
]


def _rule_config(rule_id: str) -> type[DetectorConfig]:
    class_name = "".join(part.capitalize() for part in rule_id.split("-")) + "Config"
    return create_model(
        class_name,
        __base__=DetectorConfig,
        type=(Literal[rule_id], rule_id),
    )


DETECTOR_MAP = LanguageDetectorMap(
    language="sqlalchemy",
    bindings=[
        DetectorBinding(
            detector_id=rule_id,
            detector_class=SqlalchemyRuleDetector,
            config_model=_rule_config(rule_id),
            rule_ids=[rule_id],
            default_order=index * 10,
        )
        for index, rule_id in enumerate(_RULE_IDS, start=1)
    ],
)
