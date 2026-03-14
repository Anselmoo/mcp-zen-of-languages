"""Mapping module."""

from __future__ import annotations

from typing import Literal

from pydantic import create_model

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
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


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="react",
    bindings=[
        RuleDetectorBinding(
            detector_id="react-004",
            detector_class=ReactConditionalHookDetector,
            config_model=_rule_config("react-004"),
            rules=[
                RuleBinding(
                    rule_id="react-004", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="react-003",
            detector_class=ReactDirectDomAccessDetector,
            config_model=_rule_config("react-003"),
            rules=[
                RuleBinding(
                    rule_id="react-003",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-STRICT-FENCES"),
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="react-005",
            detector_class=ReactEffectCleanupDetector,
            config_model=_rule_config("react-005"),
            rules=[
                RuleBinding(
                    rule_id="react-005",
                    dogma_ids=_dogmas("ZEN-FAIL-FAST", "ZEN-STRICT-FENCES"),
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="react-002",
            detector_class=ReactInlineHandlerDetector,
            config_model=_rule_config("react-002"),
            rules=[
                RuleBinding(
                    rule_id="react-002",
                    dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="react-001",
            detector_class=ReactStableKeyDetector,
            config_model=_rule_config("react-001"),
            rules=[
                RuleBinding(
                    rule_id="react-001",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-VISIBLE-STATE"),
                )
            ],
            default_order=50,
        ),
    ],
)
