"""State mutation dogma detector stubs (Dogmas 7 and 8)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.models import Violation


class StateMutationDetector:
    """Stub detector for visible-state and strict-fences dogmas."""

    rule_ids = ("ZEN-VISIBLE-STATE", "ZEN-STRICT-FENCES")

    def detect(self, code: str) -> list[Violation]:
        """Return no violations until state-mutation detectors are implemented."""
        _ = code
        return []
