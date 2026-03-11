"""RSpec framework detector bindings."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import DetectorGearbox
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import TESTING_TACTICS_IDS
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.core.universal_mapping import UNIVERSAL_TESTING_MAP
from mcp_zen_of_languages.languages.ruby.testing.rspec.detectors import AnonItDetector
from mcp_zen_of_languages.languages.ruby.testing.rspec.detectors import (
    AnyInstanceDetector,
)
from mcp_zen_of_languages.languages.ruby.testing.rspec.detectors import (
    BeforeAllMutationDetector,
)
from mcp_zen_of_languages.languages.ruby.testing.rspec.detectors import (
    FocusMarkerDetector,
)
from mcp_zen_of_languages.languages.ruby.testing.rspec.detectors import (
    InstanceVarInBeforeDetector,
)
from mcp_zen_of_languages.languages.ruby.testing.rspec.detectors import LetBangDetector
from mcp_zen_of_languages.languages.ruby.testing.rspec.detectors import (
    PendingExampleDetector,
)


FULL_DOGMA_IDS = list(TESTING_TACTICS_IDS) + list(UNIVERSAL_DOGMA_IDS)

DETECTOR_MAP = LanguageDetectorMap(
    language="rspec",
    bindings=[
        DetectorBinding(
            detector_id="rspec-anon-it",
            detector_class=AnonItDetector,
            config_model=AnalyzerConfig,
            rule_ids=["rspec-001"],
            universal_dogma_ids=["ZEN-TEST-NAMED-BEHAVIOR"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="rspec-instance-var",
            detector_class=InstanceVarInBeforeDetector,
            config_model=AnalyzerConfig,
            rule_ids=["rspec-002"],
            universal_dogma_ids=["ZEN-TEST-DETERMINISTIC"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="rspec-let-bang",
            detector_class=LetBangDetector,
            config_model=AnalyzerConfig,
            rule_ids=["rspec-003"],
            universal_dogma_ids=["ZEN-TEST-FAST"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="rspec-before-all",
            detector_class=BeforeAllMutationDetector,
            config_model=AnalyzerConfig,
            rule_ids=["rspec-006"],
            universal_dogma_ids=["ZEN-TEST-ISOLATED"],
            default_order=40,
        ),
        DetectorBinding(
            detector_id="rspec-any-instance",
            detector_class=AnyInstanceDetector,
            config_model=AnalyzerConfig,
            rule_ids=["rspec-007"],
            universal_dogma_ids=["ZEN-TEST-ISOLATED"],
            default_order=50,
        ),
        DetectorBinding(
            detector_id="rspec-pending-example",
            detector_class=PendingExampleDetector,
            config_model=AnalyzerConfig,
            rule_ids=["rspec-008"],
            universal_dogma_ids=["ZEN-TEST-CLEAN-CODE"],
            default_order=60,
        ),
        DetectorBinding(
            detector_id="rspec-focus-marker",
            detector_class=FocusMarkerDetector,
            config_model=AnalyzerConfig,
            rule_ids=["rspec-010"],
            universal_dogma_ids=["ZEN-TEST-CLEAN-CODE"],
            default_order=70,
        ),
    ],
)

GEARBOX = DetectorGearbox(language="rspec")
GEARBOX.extend(DETECTOR_MAP.bindings)
GEARBOX.extend(UNIVERSAL_TESTING_MAP.bindings)
DETECTOR_MAP = GEARBOX.build_map()
