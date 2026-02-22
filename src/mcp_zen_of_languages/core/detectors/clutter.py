"""Clutter dogma detector stubs (Dogmas 6, 9, and 10)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.models import Violation


class ClutterDetector:
    """Stub detector for naming, dead-code, and complexity dogmas."""

    rule_ids = (
        "ZEN-UNAMBIGUOUS-NAME",
        "ZEN-RUTHLESS-DELETION",
        "ZEN-PROPORTIONATE-COMPLEXITY",
    )

    def detect(self, code: str) -> list[Violation]:
        """Return no violations until clutter detectors are implemented."""
        _ = code
        return []
