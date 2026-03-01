"""Clutter dogma detector stubs (Dogmas 6, 9, and 10)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.languages.configs import DetectorConfig


if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.base import AnalysisContext
    from mcp_zen_of_languages.models import Violation


class ClutterDetector(ViolationDetector[DetectorConfig]):
    """Stub detector for naming, dead-code, and complexity dogmas."""

    UNIVERSAL_RULE_IDS = (
        "ZEN-UNAMBIGUOUS-NAME",
        "ZEN-RUTHLESS-DELETION",
        "ZEN-PROPORTIONATE-COMPLEXITY",
    )

    def __init__(self) -> None:
        """Initialize with the universal rule IDs for this stub domain."""
        super().__init__()
        self.rule_ids = list(self.UNIVERSAL_RULE_IDS)

    @property
    def name(self) -> str:
        """Return stable detector name for future pipeline wiring."""
        return "universal_clutter_stub"

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        """Return no violations until clutter detectors are implemented."""
        _ = (context, config)
        return []
