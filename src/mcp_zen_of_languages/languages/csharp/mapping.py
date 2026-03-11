"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
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


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="csharp",
    bindings=[
        DetectorBinding(
            detector_id="csharp_async_await",
            detector_class=CSharpAsyncAwaitDetector,
            config_model=CSharpAsyncAwaitConfig,
            rule_ids=["cs-004"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=10,
        ),
        DetectorBinding(
            detector_id="csharp_string_interpolation",
            detector_class=CSharpStringInterpolationDetector,
            config_model=CSharpStringInterpolationConfig,
            rule_ids=["cs-006"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=20,
        ),
        DetectorBinding(
            detector_id="cs-001",
            detector_class=CSharpNullableDetector,
            config_model=CSharpNullableConfig,
            rule_ids=["cs-001"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=5,
        ),
        DetectorBinding(
            detector_id="cs-002",
            detector_class=CSharpExpressionBodiedDetector,
            config_model=CSharpExpressionBodiedConfig,
            rule_ids=["cs-002"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=15,
        ),
        DetectorBinding(
            detector_id="cs-003",
            detector_class=CSharpVarDetector,
            config_model=CSharpVarConfig,
            rule_ids=["cs-003"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=25,
        ),
        DetectorBinding(
            detector_id="cs-005",
            detector_class=CSharpPatternMatchingDetector,
            config_model=CSharpPatternMatchingConfig,
            rule_ids=["cs-005"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=35,
        ),
        DetectorBinding(
            detector_id="cs-007",
            detector_class=CSharpCollectionExpressionDetector,
            config_model=CSharpCollectionExpressionConfig,
            rule_ids=["cs-007"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=45,
        ),
        DetectorBinding(
            detector_id="cs-008",
            detector_class=CSharpNamingConventionDetector,
            config_model=Cs008Config,
            rule_ids=["cs-008"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=55,
        ),
        DetectorBinding(
            detector_id="cs-009",
            detector_class=CSharpDisposableDetector,
            config_model=CSharpDisposableConfig,
            rule_ids=["cs-009"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=65,
        ),
        DetectorBinding(
            detector_id="cs-010",
            detector_class=CSharpMagicNumberDetector,
            config_model=CSharpMagicNumberConfig,
            rule_ids=["cs-010"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=75,
        ),
        DetectorBinding(
            detector_id="cs-011",
            detector_class=CSharpLinqDetector,
            config_model=CSharpLinqConfig,
            rule_ids=["cs-011"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=85,
        ),
        DetectorBinding(
            detector_id="cs-012",
            detector_class=CSharpExceptionHandlingDetector,
            config_model=CSharpExceptionHandlingConfig,
            rule_ids=["cs-012"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=95,
        ),
        DetectorBinding(
            detector_id="cs-013",
            detector_class=CSharpRecordDetector,
            config_model=CSharpRecordConfig,
            rule_ids=["cs-013"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=105,
        ),
    ],
)
