"""Control flow dogma detector stubs (Dogmas 3 and 4)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.models import Violation


class ControlFlowDetector:
    """Stub detector for return-early and fail-fast dogmas."""

    rule_ids = ("ZEN-RETURN-EARLY", "ZEN-FAIL-FAST")

    def detect(self, code: str) -> list[Violation]:
        """Return no violations until control-flow detectors are implemented."""
        _ = code
        return []
