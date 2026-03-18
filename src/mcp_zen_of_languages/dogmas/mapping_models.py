"""Explicit binding models for universal dogma detector families."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Literal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


if TYPE_CHECKING:
    from mcp_zen_of_languages.dogmas.detectors import DogmaDetector


class DogmaDetectorBinding(BaseModel):
    """Explicit binding between one universal dogma id and one detector class."""

    binding_kind: Literal["dogma"] = "dogma"
    dogma_id: str
    detector_class: type[object]
    default_order: int = 0
    enabled_by_default: bool = True

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def build_detector(self) -> DogmaDetector:
        """Instantiate the bound detector and validate its declared dogma id."""
        detector = self.detector_class()
        detector_dogma_id = getattr(detector, "dogma_id", None)
        if detector_dogma_id != self.dogma_id:
            msg = (
                f"Dogma detector binding mismatch for {self.detector_class.__name__}: "
                f"binding declares {self.dogma_id!r}, detector declares "
                f"{detector_dogma_id!r}"
            )
            raise ValueError(msg)
        return detector


class DogmaDetectorMap(BaseModel):
    """Ordered collection of dogma detector bindings."""

    bindings: list[DogmaDetectorBinding] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def build_detectors(self) -> list[DogmaDetector]:
        """Instantiate enabled dogma detectors in deterministic order."""
        enabled_bindings = [
            binding for binding in self.bindings if binding.enabled_by_default
        ]
        enabled_bindings.sort(
            key=lambda binding: (
                binding.default_order,
                binding.dogma_id,
                binding.detector_class.__name__,
            ),
        )
        return [binding.build_detector() for binding in enabled_bindings]


__all__ = ["DogmaDetectorBinding", "DogmaDetectorMap"]
