"""Jest framework detector bindings."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import TESTING_TACTICS_IDS
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.languages.typescript.testing.jest.detectors import (
    AssertionsZeroDetector,
)
from mcp_zen_of_languages.languages.typescript.testing.jest.detectors import (
    DeepDescribeDetector,
)
from mcp_zen_of_languages.languages.typescript.testing.jest.detectors import (
    EmptyDescribeDetector,
)
from mcp_zen_of_languages.languages.typescript.testing.jest.detectors import (
    NoExpectDetector,
)
from mcp_zen_of_languages.languages.typescript.testing.jest.detectors import (
    NoRestoreMocksDetector,
)
from mcp_zen_of_languages.languages.typescript.testing.jest.detectors import (
    RealTimerInTestDetector,
)
from mcp_zen_of_languages.languages.typescript.testing.jest.detectors import (
    UnawaitedPromiseDetector,
)
from mcp_zen_of_languages.languages.typescript.testing.jest.detectors import (
    VagueTitleDetector,
)


FULL_DOGMA_IDS = list(TESTING_TACTICS_IDS) + list(UNIVERSAL_DOGMA_IDS)

DETECTOR_MAP = LanguageDetectorMap(
    language="jest",
    bindings=[
        DetectorBinding(
            detector_id="jest-no-expect",
            detector_class=NoExpectDetector,
            config_model=AnalyzerConfig,
            rule_ids=["jest-001"],
            universal_dogma_ids=["ZEN-TEST-TRUSTWORTHY"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="jest-unawaited-promise",
            detector_class=UnawaitedPromiseDetector,
            config_model=AnalyzerConfig,
            rule_ids=["jest-003"],
            universal_dogma_ids=["ZEN-TEST-DETERMINISTIC"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="jest-real-timer",
            detector_class=RealTimerInTestDetector,
            config_model=AnalyzerConfig,
            rule_ids=["jest-005"],
            universal_dogma_ids=["ZEN-TEST-DETERMINISTIC", "ZEN-TEST-FAST"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="jest-empty-describe",
            detector_class=EmptyDescribeDetector,
            config_model=AnalyzerConfig,
            rule_ids=["jest-006"],
            universal_dogma_ids=["ZEN-TEST-SINGLE-REASON"],
            default_order=40,
        ),
        DetectorBinding(
            detector_id="jest-assertions-zero",
            detector_class=AssertionsZeroDetector,
            config_model=AnalyzerConfig,
            rule_ids=["jest-007"],
            universal_dogma_ids=["ZEN-TEST-TRUSTWORTHY"],
            default_order=50,
        ),
        DetectorBinding(
            detector_id="jest-vague-title",
            detector_class=VagueTitleDetector,
            config_model=AnalyzerConfig,
            rule_ids=["jest-008"],
            universal_dogma_ids=["ZEN-TEST-NAMED-BEHAVIOR"],
            default_order=60,
        ),
        DetectorBinding(
            detector_id="jest-deep-describe",
            detector_class=DeepDescribeDetector,
            config_model=AnalyzerConfig,
            rule_ids=["jest-009"],
            universal_dogma_ids=["ZEN-TEST-SINGLE-REASON"],
            default_order=70,
        ),
        DetectorBinding(
            detector_id="jest-no-restore-mocks",
            detector_class=NoRestoreMocksDetector,
            config_model=AnalyzerConfig,
            rule_ids=["jest-010"],
            universal_dogma_ids=["ZEN-TEST-ISOLATED"],
            default_order=80,
        ),
    ],
)
