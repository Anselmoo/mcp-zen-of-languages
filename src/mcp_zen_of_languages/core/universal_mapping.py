"""Universal detector map — cross-language production and testing detector bindings.

This module defines two ``LanguageDetectorMap`` objects that are merged into
every language pipeline via the ``DetectorGearbox``:

``UNIVERSAL_DETECTOR_MAP``
    Five stub detector bindings that together cover all 10 ``ZEN-*`` universal
    dogmas.  Every production language analyzer merges these bindings so that
    every dogma is represented in the pipeline even when a particular language
    has no rule that infers to a given dogma.

``UNIVERSAL_TESTING_MAP``
    Stub detector bindings covering ``ZEN-TEST-*`` dogmas not yet addressed
    by any framework-specific detector.  Test framework analyzers (pytest,
    Jest, RSpec, Go test) merge these to ensure complete testing-tier dogma
    coverage.

Wiring pattern
--------------
Language ``mapping.py`` files close with::

    from mcp_zen_of_languages.core.universal_mapping import UNIVERSAL_DETECTOR_MAP

    GEARBOX = DetectorGearbox(language="python")
    GEARBOX.extend(DETECTOR_MAP.bindings)
    GEARBOX.extend(UNIVERSAL_DETECTOR_MAP.bindings)
    DETECTOR_MAP = GEARBOX.build_map()

Framework ``mapping.py`` files use ``UNIVERSAL_TESTING_MAP`` in the same way.
"""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.detectors.clutter import ClutterDetector
from mcp_zen_of_languages.core.detectors.control_flow import ControlFlowDetector
from mcp_zen_of_languages.core.detectors.shared_keyword import (
    SharedDogmaKeywordDetector,
)
from mcp_zen_of_languages.core.detectors.signature import SignatureDetector
from mcp_zen_of_languages.core.detectors.state_mutation import StateMutationDetector
from mcp_zen_of_languages.languages.configs import DetectorConfig


# ---------------------------------------------------------------------------
# Production (Yang) — covers all 10 ZEN-* universal dogmas
# ---------------------------------------------------------------------------

UNIVERSAL_DETECTOR_MAP: LanguageDetectorMap = LanguageDetectorMap(
    language="universal",
    bindings=[
        # ZEN-UNAMBIGUOUS-NAME · ZEN-RUTHLESS-DELETION · ZEN-PROPORTIONATE-COMPLEXITY
        DetectorBinding(
            detector_id="universal_clutter",
            detector_class=ClutterDetector,
            config_model=DetectorConfig,
            rule_ids=[],
            universal_dogma_ids=list(ClutterDetector.UNIVERSAL_RULE_IDS),
            default_order=900,
            enabled_by_default=False,
        ),
        # ZEN-RETURN-EARLY · ZEN-FAIL-FAST
        DetectorBinding(
            detector_id="universal_control_flow",
            detector_class=ControlFlowDetector,
            config_model=DetectorConfig,
            rule_ids=[],
            universal_dogma_ids=list(ControlFlowDetector.UNIVERSAL_RULE_IDS),
            default_order=910,
            enabled_by_default=False,
        ),
        # ZEN-VISIBLE-STATE · ZEN-STRICT-FENCES
        DetectorBinding(
            detector_id="universal_state_mutation",
            detector_class=StateMutationDetector,
            config_model=DetectorConfig,
            rule_ids=[],
            universal_dogma_ids=list(StateMutationDetector.UNIVERSAL_RULE_IDS),
            default_order=920,
            enabled_by_default=False,
        ),
        # ZEN-UTILIZE-ARGUMENTS · ZEN-EXPLICIT-INTENT · ZEN-RIGHT-ABSTRACTION
        DetectorBinding(
            detector_id="universal_signature",
            detector_class=SignatureDetector,
            config_model=DetectorConfig,
            rule_ids=[],
            universal_dogma_ids=list(SignatureDetector.UNIVERSAL_RULE_IDS),
            default_order=930,
            enabled_by_default=False,
        ),
        # ZEN-EXPLICIT-INTENT · ZEN-UNAMBIGUOUS-NAME  (keyword / cross-cutting)
        DetectorBinding(
            detector_id="universal_shared_keyword",
            detector_class=SharedDogmaKeywordDetector,
            config_model=DetectorConfig,
            rule_ids=[],
            universal_dogma_ids=["ZEN-EXPLICIT-INTENT", "ZEN-UNAMBIGUOUS-NAME"],
            default_order=940,
            enabled_by_default=False,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Testing (Yin) — covers ZEN-TEST-* dogmas not tied to a specific framework rule
# ---------------------------------------------------------------------------
# These stubs ensure that all 10 testing tactics dogmas appear in framework
# analysis results even when a framework has no explicit rule for a given dogma.

# Import testing dogma IDs only (avoid cross-tier leakage)
_TESTING_STUBS: list[DetectorBinding] = [
    DetectorBinding(
        detector_id="universal_test_proportional",
        detector_class=ClutterDetector,  # reuse stub; real impl TBD
        config_model=DetectorConfig,
        rule_ids=[],
        universal_dogma_ids=["ZEN-TEST-PROPORTIONAL"],
        default_order=950,
        enabled_by_default=False,
    ),
    DetectorBinding(
        detector_id="universal_test_documented_intent",
        detector_class=SignatureDetector,  # reuse stub; real impl TBD
        config_model=DetectorConfig,
        rule_ids=[],
        universal_dogma_ids=["ZEN-TEST-DOCUMENTED-INTENT"],
        default_order=960,
        enabled_by_default=False,
    ),
    DetectorBinding(
        detector_id="universal_test_single_reason",
        detector_class=ControlFlowDetector,  # reuse stub; real impl TBD
        config_model=DetectorConfig,
        rule_ids=[],
        universal_dogma_ids=["ZEN-TEST-SINGLE-REASON"],
        default_order=970,
        enabled_by_default=False,
    ),
]

UNIVERSAL_TESTING_MAP: LanguageDetectorMap = LanguageDetectorMap(
    language="universal_testing",
    bindings=_TESTING_STUBS,
)
