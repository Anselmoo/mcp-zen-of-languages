"""Control flow dogma detector stubs (Dogmas 3 and 4)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.languages.configs import DetectorConfig


if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.base import AnalysisContext
    from mcp_zen_of_languages.models import Violation


class ControlFlowDetector(ViolationDetector[DetectorConfig]):
    """Stub detector for return-early and fail-fast dogmas."""

    UNIVERSAL_RULE_IDS = ("ZEN-RETURN-EARLY", "ZEN-FAIL-FAST")

    def __init__(self) -> None:
        """Initialize with the universal rule IDs for this stub domain."""
        super().__init__()
        self.rule_ids = list(self.UNIVERSAL_RULE_IDS)

    @property
    def name(self) -> str:
        """Return stable detector name for future pipeline wiring."""
        return "universal_control_flow_stub"

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        """Return no violations until control-flow detectors are implemented."""
        _ = (context, config)
        return []
