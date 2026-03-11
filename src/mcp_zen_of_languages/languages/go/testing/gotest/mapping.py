"""Go testing framework detector bindings."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import DetectorGearbox
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import TESTING_TACTICS_IDS
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.core.universal_mapping import UNIVERSAL_TESTING_MAP
from mcp_zen_of_languages.languages.go.testing.gotest.detectors import (
    EmptySubtestNameDetector,
)
from mcp_zen_of_languages.languages.go.testing.gotest.detectors import (
    FatalInAssertDetector,
)
from mcp_zen_of_languages.languages.go.testing.gotest.detectors import (
    GlobalMutableStateDetector,
)
from mcp_zen_of_languages.languages.go.testing.gotest.detectors import (
    MissingTHelperDetector,
)
from mcp_zen_of_languages.languages.go.testing.gotest.detectors import (
    OsExitInTestDetector,
)
from mcp_zen_of_languages.languages.go.testing.gotest.detectors import (
    ParallelTestDetector,
)
from mcp_zen_of_languages.languages.go.testing.gotest.detectors import (
    TimeSleepInTestDetector,
)


FULL_DOGMA_IDS = list(TESTING_TACTICS_IDS) + list(UNIVERSAL_DOGMA_IDS)

DETECTOR_MAP = LanguageDetectorMap(
    language="gotest",
    bindings=[
        DetectorBinding(
            detector_id="gotest-parallel",
            detector_class=ParallelTestDetector,
            config_model=AnalyzerConfig,
            rule_ids=["gotest-001"],
            universal_dogma_ids=["ZEN-TEST-DETERMINISTIC"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="gotest-fatal-assert",
            detector_class=FatalInAssertDetector,
            config_model=AnalyzerConfig,
            rule_ids=["gotest-003"],
            universal_dogma_ids=["ZEN-TEST-FAST"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="gotest-missing-t-helper",
            detector_class=MissingTHelperDetector,
            config_model=AnalyzerConfig,
            rule_ids=["gotest-004"],
            universal_dogma_ids=["ZEN-TEST-CLEAN-CODE"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="gotest-os-exit",
            detector_class=OsExitInTestDetector,
            config_model=AnalyzerConfig,
            rule_ids=["gotest-005"],
            universal_dogma_ids=["ZEN-TEST-TRUSTWORTHY"],
            default_order=40,
        ),
        DetectorBinding(
            detector_id="gotest-time-sleep",
            detector_class=TimeSleepInTestDetector,
            config_model=AnalyzerConfig,
            rule_ids=["gotest-006"],
            universal_dogma_ids=["ZEN-TEST-FAST", "ZEN-TEST-DETERMINISTIC"],
            default_order=50,
        ),
        DetectorBinding(
            detector_id="gotest-empty-subtest-name",
            detector_class=EmptySubtestNameDetector,
            config_model=AnalyzerConfig,
            rule_ids=["gotest-007"],
            universal_dogma_ids=["ZEN-TEST-NAMED-BEHAVIOR"],
            default_order=60,
        ),
        DetectorBinding(
            detector_id="gotest-global-state",
            detector_class=GlobalMutableStateDetector,
            config_model=AnalyzerConfig,
            rule_ids=["gotest-010"],
            universal_dogma_ids=["ZEN-TEST-ISOLATED"],
            default_order=70,
        ),
    ],
)

GEARBOX = DetectorGearbox(language="gotest")
GEARBOX.extend(DETECTOR_MAP.bindings)
GEARBOX.extend(UNIVERSAL_TESTING_MAP.bindings)
DETECTOR_MAP = GEARBOX.build_map()
