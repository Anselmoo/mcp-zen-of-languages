"""Mapping module."""

from __future__ import annotations

from typing import Literal

from pydantic import create_model

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.frameworks.dogmas import framework_rule_dogmas
from mcp_zen_of_languages.frameworks.fastapi.detectors import FastapiAsyncIoDetector
from mcp_zen_of_languages.frameworks.fastapi.detectors import (
    FastapiBackgroundTasksDetector,
)
from mcp_zen_of_languages.frameworks.fastapi.detectors import (
    FastapiHttpExceptionDetector,
)
from mcp_zen_of_languages.frameworks.fastapi.detectors import (
    FastapiResponseModelDetector,
)
from mcp_zen_of_languages.frameworks.fastapi.detectors import FastapiStatusCodeDetector
from mcp_zen_of_languages.frameworks.fastapi.detectors import (
    FastapiVerbDecoratorDetector,
)
from mcp_zen_of_languages.languages.configs import DetectorConfig


def _rule_config(rule_id: str) -> type[DetectorConfig]:
    class_name = "".join(part.capitalize() for part in rule_id.split("-")) + "Config"
    return create_model(
        class_name,
        __base__=DetectorConfig,
        type=(Literal[rule_id], rule_id),
    )


DETECTOR_MAP = LanguageDetectorMap(
    language="fastapi",
    bindings=[
        DetectorBinding(
            detector_id="fastapi-005",
            detector_class=FastapiAsyncIoDetector,
            config_model=_rule_config("fastapi-005"),
            rule_ids=["fastapi-005"],
            universal_dogma_ids=list(framework_rule_dogmas("fastapi-005")),
            default_order=10,
        ),
        DetectorBinding(
            detector_id="fastapi-004",
            detector_class=FastapiBackgroundTasksDetector,
            config_model=_rule_config("fastapi-004"),
            rule_ids=["fastapi-004"],
            universal_dogma_ids=list(framework_rule_dogmas("fastapi-004")),
            default_order=20,
        ),
        DetectorBinding(
            detector_id="fastapi-003",
            detector_class=FastapiHttpExceptionDetector,
            config_model=_rule_config("fastapi-003"),
            rule_ids=["fastapi-003"],
            universal_dogma_ids=list(framework_rule_dogmas("fastapi-003")),
            default_order=30,
        ),
        DetectorBinding(
            detector_id="fastapi-001",
            detector_class=FastapiResponseModelDetector,
            config_model=_rule_config("fastapi-001"),
            rule_ids=["fastapi-001"],
            universal_dogma_ids=list(framework_rule_dogmas("fastapi-001")),
            default_order=40,
        ),
        DetectorBinding(
            detector_id="fastapi-002",
            detector_class=FastapiStatusCodeDetector,
            config_model=_rule_config("fastapi-002"),
            rule_ids=["fastapi-002"],
            universal_dogma_ids=list(framework_rule_dogmas("fastapi-002")),
            default_order=50,
        ),
        DetectorBinding(
            detector_id="fastapi-006",
            detector_class=FastapiVerbDecoratorDetector,
            config_model=_rule_config("fastapi-006"),
            rule_ids=["fastapi-006"],
            universal_dogma_ids=list(framework_rule_dogmas("fastapi-006")),
            default_order=60,
        ),
    ],
)
