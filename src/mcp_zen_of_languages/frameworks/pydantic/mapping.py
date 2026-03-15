"""Mapping module."""

from __future__ import annotations

from typing import Literal

from pydantic import create_model

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.frameworks.pydantic.detectors import (
    PydanticDefaultFactoryDetector,
)
from mcp_zen_of_languages.frameworks.pydantic.detectors import (
    PydanticFieldValidatorDetector,
)
from mcp_zen_of_languages.frameworks.pydantic.detectors import (
    PydanticFromAttributesDetector,
)
from mcp_zen_of_languages.frameworks.pydantic.detectors import (
    PydanticModelConfigDetector,
)
from mcp_zen_of_languages.frameworks.pydantic.detectors import PydanticModelDumpDetector
from mcp_zen_of_languages.frameworks.pydantic.detectors import (
    PydanticModelFieldsDetector,
)
from mcp_zen_of_languages.frameworks.pydantic.detectors import (
    PydanticModelValidateDetector,
)
from mcp_zen_of_languages.frameworks.pydantic.detectors import (
    PydanticModernTypingDetector,
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


def _testing(*testing_ids: str) -> list[str]:
    """Return explicit testing family ids for the binding."""
    return list(testing_ids)


def _projection(*projection_ids: str) -> list[str]:
    """Return explicit projection family ids for the binding."""
    return list(projection_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="pydantic",
    bindings=[
        RuleDetectorBinding(
            detector_id="pydantic-003",
            detector_class=PydanticDefaultFactoryDetector,
            config_model=_rule_config("pydantic-003"),
            rules=[
                RuleBinding(
                    rule_id="pydantic-003",
                    dogma_ids=_dogmas("ZEN-VISIBLE-STATE", "ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("pytest"),
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="pydantic-005",
            detector_class=PydanticFieldValidatorDetector,
            config_model=_rule_config("pydantic-005"),
            rules=[
                RuleBinding(
                    rule_id="pydantic-005",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("pytest"),
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="pydantic-008",
            detector_class=PydanticFromAttributesDetector,
            config_model=_rule_config("pydantic-008"),
            rules=[
                RuleBinding(
                    rule_id="pydantic-008",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("pytest"),
                    projection_ids=_projection("openapi"),
                    verified_projection_ids=[],
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="pydantic-004",
            detector_class=PydanticModelConfigDetector,
            config_model=_rule_config("pydantic-004"),
            rules=[
                RuleBinding(
                    rule_id="pydantic-004",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("pytest"),
                    projection_ids=_projection("jsonschema", "openapi"),
                    verified_projection_ids=_projection("jsonschema"),
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="pydantic-001",
            detector_class=PydanticModelDumpDetector,
            config_model=_rule_config("pydantic-001"),
            rules=[
                RuleBinding(
                    rule_id="pydantic-001",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("pytest"),
                    projection_ids=_projection("openapi"),
                    verified_projection_ids=[],
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="pydantic-006",
            detector_class=PydanticModelFieldsDetector,
            config_model=_rule_config("pydantic-006"),
            rules=[
                RuleBinding(
                    rule_id="pydantic-006",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-UNAMBIGUOUS-NAME"),
                    testing_ids=_testing("pytest"),
                )
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="pydantic-002",
            detector_class=PydanticModelValidateDetector,
            config_model=_rule_config("pydantic-002"),
            rules=[
                RuleBinding(
                    rule_id="pydantic-002",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION"),
                    testing_ids=_testing("pytest"),
                    projection_ids=_projection("openapi"),
                    verified_projection_ids=[],
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="pydantic-007",
            detector_class=PydanticModernTypingDetector,
            config_model=_rule_config("pydantic-007"),
            rules=[
                RuleBinding(
                    rule_id="pydantic-007",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("pytest"),
                    projection_ids=_projection("jsonschema"),
                )
            ],
            default_order=80,
        ),
    ],
)
