"""Explicit universal dogma detector bindings."""

from __future__ import annotations

from mcp_zen_of_languages.core.universal_dogmas import UniversalDogmaID
from mcp_zen_of_languages.dogmas.detectors import ExplicitIntentDogmaDetector
from mcp_zen_of_languages.dogmas.detectors import FailFastDogmaDetector
from mcp_zen_of_languages.dogmas.detectors import ProportionateComplexityDogmaDetector
from mcp_zen_of_languages.dogmas.detectors import ReturnEarlyDogmaDetector
from mcp_zen_of_languages.dogmas.detectors import RightAbstractionDogmaDetector
from mcp_zen_of_languages.dogmas.detectors import RuthlessDeletionDogmaDetector
from mcp_zen_of_languages.dogmas.detectors import StrictFencesDogmaDetector
from mcp_zen_of_languages.dogmas.detectors import UnambiguousNameDogmaDetector
from mcp_zen_of_languages.dogmas.detectors import UtilizeArgumentsDogmaDetector
from mcp_zen_of_languages.dogmas.detectors import VisibleStateDogmaDetector
from mcp_zen_of_languages.dogmas.mapping_models import DogmaDetectorBinding
from mcp_zen_of_languages.dogmas.mapping_models import DogmaDetectorMap


DOGMA_DETECTOR_MAP = DogmaDetectorMap(
    bindings=[
        DogmaDetectorBinding(
            dogma_id=UniversalDogmaID.UTILIZE_ARGUMENTS.value,
            detector_class=UtilizeArgumentsDogmaDetector,
            default_order=10,
        ),
        DogmaDetectorBinding(
            dogma_id=UniversalDogmaID.EXPLICIT_INTENT.value,
            detector_class=ExplicitIntentDogmaDetector,
            default_order=20,
        ),
        DogmaDetectorBinding(
            dogma_id=UniversalDogmaID.RETURN_EARLY.value,
            detector_class=ReturnEarlyDogmaDetector,
            default_order=30,
        ),
        DogmaDetectorBinding(
            dogma_id=UniversalDogmaID.FAIL_FAST.value,
            detector_class=FailFastDogmaDetector,
            default_order=40,
        ),
        DogmaDetectorBinding(
            dogma_id=UniversalDogmaID.RIGHT_ABSTRACTION.value,
            detector_class=RightAbstractionDogmaDetector,
            default_order=50,
        ),
        DogmaDetectorBinding(
            dogma_id=UniversalDogmaID.UNAMBIGUOUS_NAME.value,
            detector_class=UnambiguousNameDogmaDetector,
            default_order=60,
        ),
        DogmaDetectorBinding(
            dogma_id=UniversalDogmaID.VISIBLE_STATE.value,
            detector_class=VisibleStateDogmaDetector,
            default_order=70,
        ),
        DogmaDetectorBinding(
            dogma_id=UniversalDogmaID.STRICT_FENCES.value,
            detector_class=StrictFencesDogmaDetector,
            default_order=80,
        ),
        DogmaDetectorBinding(
            dogma_id=UniversalDogmaID.RUTHLESS_DELETION.value,
            detector_class=RuthlessDeletionDogmaDetector,
            default_order=90,
        ),
        DogmaDetectorBinding(
            dogma_id=UniversalDogmaID.PROPORTIONATE_COMPLEXITY.value,
            detector_class=ProportionateComplexityDogmaDetector,
            default_order=100,
        ),
    ],
)


__all__ = ["DOGMA_DETECTOR_MAP"]
