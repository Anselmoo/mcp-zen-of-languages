"""Mapping module."""

from __future__ import annotations

from typing import Literal

from pydantic import create_model

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.frameworks.django.detectors import DjangoDebugConfigDetector
from mcp_zen_of_languages.frameworks.django.detectors import (
    DjangoParameterizedSqlDetector,
)
from mcp_zen_of_languages.frameworks.django.detectors import (
    DjangoQuerysetLoadingDetector,
)
from mcp_zen_of_languages.frameworks.django.detectors import DjangoReverseUrlDetector
from mcp_zen_of_languages.frameworks.django.detectors import (
    DjangoSecretSettingsDetector,
)
from mcp_zen_of_languages.frameworks.django.detectors import DjangoSignalHookDetector
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
    language="django",
    bindings=[
        RuleDetectorBinding(
            detector_id="django-003",
            detector_class=DjangoDebugConfigDetector,
            config_model=_rule_config("django-003"),
            rule_ids=["django-003"],
            universal_dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-FAIL-FAST"),
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="django-001",
            detector_class=DjangoParameterizedSqlDetector,
            config_model=_rule_config("django-001"),
            rule_ids=["django-001"],
            universal_dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-FAIL-FAST"),
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="django-006",
            detector_class=DjangoQuerysetLoadingDetector,
            config_model=_rule_config("django-006"),
            rule_ids=["django-006"],
            universal_dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="django-004",
            detector_class=DjangoReverseUrlDetector,
            config_model=_rule_config("django-004"),
            rule_ids=["django-004"],
            universal_dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-RIGHT-ABSTRACTION"),
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="django-002",
            detector_class=DjangoSecretSettingsDetector,
            config_model=_rule_config("django-002"),
            rule_ids=["django-002"],
            universal_dogma_ids=_dogmas("ZEN-STRICT-FENCES"),
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="django-005",
            detector_class=DjangoSignalHookDetector,
            config_model=_rule_config("django-005"),
            rule_ids=["django-005"],
            universal_dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION"),
            default_order=60,
        ),
    ],
)
