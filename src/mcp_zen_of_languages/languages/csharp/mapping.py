"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.languages.configs import CSharpAsyncAwaitConfig
from mcp_zen_of_languages.languages.configs import CSharpCollectionExpressionConfig
from mcp_zen_of_languages.languages.configs import CSharpDisposableConfig
from mcp_zen_of_languages.languages.configs import CSharpExceptionHandlingConfig
from mcp_zen_of_languages.languages.configs import CSharpExpressionBodiedConfig
from mcp_zen_of_languages.languages.configs import CSharpLinqConfig
from mcp_zen_of_languages.languages.configs import CSharpMagicNumberConfig
from mcp_zen_of_languages.languages.configs import CSharpNullableConfig
from mcp_zen_of_languages.languages.configs import CSharpPatternMatchingConfig
from mcp_zen_of_languages.languages.configs import CSharpRecordConfig
from mcp_zen_of_languages.languages.configs import CSharpStringInterpolationConfig
from mcp_zen_of_languages.languages.configs import CSharpVarConfig
from mcp_zen_of_languages.languages.configs import Cs008Config
from mcp_zen_of_languages.languages.csharp.detectors import CSharpAsyncAwaitDetector
from mcp_zen_of_languages.languages.csharp.detectors import (
    CSharpCollectionExpressionDetector,
)
from mcp_zen_of_languages.languages.csharp.detectors import CSharpDisposableDetector
from mcp_zen_of_languages.languages.csharp.detectors import (
    CSharpExceptionHandlingDetector,
)
from mcp_zen_of_languages.languages.csharp.detectors import (
    CSharpExpressionBodiedDetector,
)
from mcp_zen_of_languages.languages.csharp.detectors import CSharpLinqDetector
from mcp_zen_of_languages.languages.csharp.detectors import CSharpMagicNumberDetector
from mcp_zen_of_languages.languages.csharp.detectors import (
    CSharpNamingConventionDetector,
)
from mcp_zen_of_languages.languages.csharp.detectors import CSharpNullableDetector
from mcp_zen_of_languages.languages.csharp.detectors import (
    CSharpPatternMatchingDetector,
)
from mcp_zen_of_languages.languages.csharp.detectors import CSharpRecordDetector
from mcp_zen_of_languages.languages.csharp.detectors import (
    CSharpStringInterpolationDetector,
)
from mcp_zen_of_languages.languages.csharp.detectors import CSharpVarDetector


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="csharp",
    bindings=[
        RuleDetectorBinding(
            detector_id="csharp_async_await",
            detector_class=CSharpAsyncAwaitDetector,
            config_model=CSharpAsyncAwaitConfig,
            rules=[RuleBinding(rule_id="cs-004", dogma_ids=_dogmas("ZEN-FAIL-FAST"))],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="csharp_string_interpolation",
            detector_class=CSharpStringInterpolationDetector,
            config_model=CSharpStringInterpolationConfig,
            rules=[
                RuleBinding(
                    rule_id="cs-006",
                    dogma_ids=_dogmas(
                        "ZEN-UNAMBIGUOUS-NAME", "ZEN-PROPORTIONATE-COMPLEXITY"
                    ),
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="cs-001",
            detector_class=CSharpNullableDetector,
            config_model=CSharpNullableConfig,
            rules=[
                RuleBinding(rule_id="cs-001", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=5,
        ),
        RuleDetectorBinding(
            detector_id="cs-002",
            detector_class=CSharpExpressionBodiedDetector,
            config_model=CSharpExpressionBodiedConfig,
            rules=[
                RuleBinding(
                    rule_id="cs-002",
                    dogma_ids=_dogmas(
                        "ZEN-RIGHT-ABSTRACTION",
                        "ZEN-VISIBLE-STATE",
                        "ZEN-PROPORTIONATE-COMPLEXITY",
                    ),
                )
            ],
            default_order=15,
        ),
        RuleDetectorBinding(
            detector_id="cs-003",
            detector_class=CSharpVarDetector,
            config_model=CSharpVarConfig,
            rules=[
                RuleBinding(
                    rule_id="cs-003",
                    dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME", "ZEN-EXPLICIT-INTENT"),
                )
            ],
            default_order=25,
        ),
        RuleDetectorBinding(
            detector_id="cs-005",
            detector_class=CSharpPatternMatchingDetector,
            config_model=CSharpPatternMatchingConfig,
            rules=[
                RuleBinding(
                    rule_id="cs-005", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=35,
        ),
        RuleDetectorBinding(
            detector_id="cs-007",
            detector_class=CSharpCollectionExpressionDetector,
            config_model=CSharpCollectionExpressionConfig,
            rules=[
                RuleBinding(
                    rule_id="cs-007", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=45,
        ),
        RuleDetectorBinding(
            detector_id="cs-008",
            detector_class=CSharpNamingConventionDetector,
            config_model=Cs008Config,
            rules=[
                RuleBinding(rule_id="cs-008", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME"))
            ],
            default_order=55,
        ),
        RuleDetectorBinding(
            detector_id="cs-009",
            detector_class=CSharpDisposableDetector,
            config_model=CSharpDisposableConfig,
            rules=[
                RuleBinding(
                    rule_id="cs-009",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-VISIBLE-STATE"),
                )
            ],
            default_order=65,
        ),
        RuleDetectorBinding(
            detector_id="cs-010",
            detector_class=CSharpMagicNumberDetector,
            config_model=CSharpMagicNumberConfig,
            rules=[
                RuleBinding(
                    rule_id="cs-010",
                    dogma_ids=_dogmas(
                        "ZEN-EXPLICIT-INTENT",
                        "ZEN-UNAMBIGUOUS-NAME",
                        "ZEN-VISIBLE-STATE",
                    ),
                )
            ],
            default_order=75,
        ),
        RuleDetectorBinding(
            detector_id="cs-011",
            detector_class=CSharpLinqDetector,
            config_model=CSharpLinqConfig,
            rules=[
                RuleBinding(
                    rule_id="cs-011", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=85,
        ),
        RuleDetectorBinding(
            detector_id="cs-012",
            detector_class=CSharpExceptionHandlingDetector,
            config_model=CSharpExceptionHandlingConfig,
            rules=[RuleBinding(rule_id="cs-012", dogma_ids=_dogmas("ZEN-FAIL-FAST"))],
            default_order=95,
        ),
        RuleDetectorBinding(
            detector_id="cs-013",
            detector_class=CSharpRecordDetector,
            config_model=CSharpRecordConfig,
            rules=[
                RuleBinding(
                    rule_id="cs-013",
                    dogma_ids=_dogmas(
                        "ZEN-RIGHT-ABSTRACTION", "ZEN-PROPORTIONATE-COMPLEXITY"
                    ),
                )
            ],
            default_order=105,
        ),
    ],
)
