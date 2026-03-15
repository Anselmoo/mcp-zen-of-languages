"""Mapping module."""

from __future__ import annotations

from typing import Literal

from pydantic import create_model

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
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


def _testing(*testing_ids: str) -> list[str]:
    """Return explicit testing family ids for the binding."""
    return list(testing_ids)


def _projection(*projection_ids: str) -> list[str]:
    """Return explicit projection family ids for the binding."""
    return list(projection_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="django",
    bindings=[
        RuleDetectorBinding(
            detector_id="django-003",
            detector_class=DjangoDebugConfigDetector,
            config_model=_rule_config("django-003"),
            rules=[
                RuleBinding(
                    rule_id="django-003",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-FAIL-FAST"),
                    testing_ids=_testing("pytest"),
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="django-001",
            detector_class=DjangoParameterizedSqlDetector,
            config_model=_rule_config("django-001"),
            rules=[
                RuleBinding(
                    rule_id="django-001",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-FAIL-FAST"),
                    testing_ids=_testing("pytest"),
                    projection_ids=_projection("sql"),
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="django-006",
            detector_class=DjangoQuerysetLoadingDetector,
            config_model=_rule_config("django-006"),
            rules=[
                RuleBinding(
                    rule_id="django-006",
                    dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
                    testing_ids=_testing("pytest"),
                    projection_ids=_projection("sql"),
                    verified_projection_ids=[],
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="django-004",
            detector_class=DjangoReverseUrlDetector,
            config_model=_rule_config("django-004"),
            rules=[
                RuleBinding(
                    rule_id="django-004",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-RIGHT-ABSTRACTION"),
                    testing_ids=_testing("pytest"),
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="django-002",
            detector_class=DjangoSecretSettingsDetector,
            config_model=_rule_config("django-002"),
            rules=[
                RuleBinding(
                    rule_id="django-002",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES"),
                    testing_ids=_testing("pytest"),
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="django-005",
            detector_class=DjangoSignalHookDetector,
            config_model=_rule_config("django-005"),
            rules=[
                RuleBinding(
                    rule_id="django-005",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION"),
                    testing_ids=_testing("pytest"),
                )
            ],
            default_order=60,
        ),
    ],
)
