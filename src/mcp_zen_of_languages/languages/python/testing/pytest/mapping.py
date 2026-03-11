"""Pytest framework detector bindings."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import TESTING_TACTICS_IDS
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.languages.python.testing.pytest.detectors import (
    BareExceptInTestDetector,
)
from mcp_zen_of_languages.languages.python.testing.pytest.detectors import (
    LoopInTestDetector,
)
from mcp_zen_of_languages.languages.python.testing.pytest.detectors import (
    ModuleLevelMockDetector,
)
from mcp_zen_of_languages.languages.python.testing.pytest.detectors import (
    NoAssertInTestDetector,
)
from mcp_zen_of_languages.languages.python.testing.pytest.detectors import (
    PytestRaisesDetector,
)
from mcp_zen_of_languages.languages.python.testing.pytest.detectors import (
    SleepInTestDetector,
)
from mcp_zen_of_languages.languages.python.testing.pytest.detectors import (
    UnittestAssertDetector,
)
from mcp_zen_of_languages.languages.python.testing.pytest.detectors import (
    VagueTestNameDetector,
)


FULL_DOGMA_IDS = list(TESTING_TACTICS_IDS) + list(UNIVERSAL_DOGMA_IDS)

DETECTOR_MAP = LanguageDetectorMap(
    language="pytest",
    bindings=[
        DetectorBinding(
            detector_id="pytest-unittest-assert",
            detector_class=UnittestAssertDetector,
            config_model=AnalyzerConfig,
            rule_ids=["pytest-001"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=10,
        ),
        DetectorBinding(
            detector_id="pytest-sleep-in-test",
            detector_class=SleepInTestDetector,
            config_model=AnalyzerConfig,
            rule_ids=["pytest-003"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=20,
        ),
        DetectorBinding(
            detector_id="pytest-loop-in-test",
            detector_class=LoopInTestDetector,
            config_model=AnalyzerConfig,
            rule_ids=["pytest-004"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=30,
        ),
        DetectorBinding(
            detector_id="pytest-no-assert",
            detector_class=NoAssertInTestDetector,
            config_model=AnalyzerConfig,
            rule_ids=["pytest-005"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=40,
        ),
        DetectorBinding(
            detector_id="pytest-vague-test-name",
            detector_class=VagueTestNameDetector,
            config_model=AnalyzerConfig,
            rule_ids=["pytest-006"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=50,
        ),
        DetectorBinding(
            detector_id="pytest-bare-except",
            detector_class=BareExceptInTestDetector,
            config_model=AnalyzerConfig,
            rule_ids=["pytest-007"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=60,
        ),
        DetectorBinding(
            detector_id="pytest-use-raises",
            detector_class=PytestRaisesDetector,
            config_model=AnalyzerConfig,
            rule_ids=["pytest-009"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=70,
        ),
        DetectorBinding(
            detector_id="pytest-module-level-mock",
            detector_class=ModuleLevelMockDetector,
            config_model=AnalyzerConfig,
            rule_ids=["pytest-010"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=80,
        ),
    ],
)
