"""Mapping module."""

from __future__ import annotations

from typing import Literal

from pydantic import create_model

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.frameworks.sqlalchemy.detectors import (
    SqlalchemyBulkInsertDetector,
)
from mcp_zen_of_languages.frameworks.sqlalchemy.detectors import (
    SqlalchemyDeclarativeBaseDetector,
)
from mcp_zen_of_languages.frameworks.sqlalchemy.detectors import (
    SqlalchemyMappedColumnDetector,
)
from mcp_zen_of_languages.frameworks.sqlalchemy.detectors import (
    SqlalchemyParameterizedTextDetector,
)
from mcp_zen_of_languages.frameworks.sqlalchemy.detectors import (
    SqlalchemyRelationshipLoadingDetector,
)
from mcp_zen_of_languages.frameworks.sqlalchemy.detectors import (
    SqlalchemySessionScopeDetector,
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
    language="sqlalchemy",
    bindings=[
        RuleDetectorBinding(
            detector_id="sqlalchemy-006",
            detector_class=SqlalchemyBulkInsertDetector,
            config_model=_rule_config("sqlalchemy-006"),
            rule_ids=["sqlalchemy-006"],
            universal_dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="sqlalchemy-004",
            detector_class=SqlalchemyDeclarativeBaseDetector,
            config_model=_rule_config("sqlalchemy-004"),
            rule_ids=["sqlalchemy-004"],
            universal_dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION"),
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="sqlalchemy-003",
            detector_class=SqlalchemyMappedColumnDetector,
            config_model=_rule_config("sqlalchemy-003"),
            rule_ids=["sqlalchemy-003"],
            universal_dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION"),
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="sqlalchemy-001",
            detector_class=SqlalchemyParameterizedTextDetector,
            config_model=_rule_config("sqlalchemy-001"),
            rule_ids=["sqlalchemy-001"],
            universal_dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-FAIL-FAST"),
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="sqlalchemy-005",
            detector_class=SqlalchemyRelationshipLoadingDetector,
            config_model=_rule_config("sqlalchemy-005"),
            rule_ids=["sqlalchemy-005"],
            universal_dogma_ids=_dogmas(
                "ZEN-PROPORTIONATE-COMPLEXITY", "ZEN-EXPLICIT-INTENT"
            ),
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="sqlalchemy-002",
            detector_class=SqlalchemySessionScopeDetector,
            config_model=_rule_config("sqlalchemy-002"),
            rule_ids=["sqlalchemy-002"],
            universal_dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-EXPLICIT-INTENT"),
            default_order=60,
        ),
    ],
)
