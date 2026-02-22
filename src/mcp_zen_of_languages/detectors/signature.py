"""Signature dogma detector stubs (Dogmas 1, 2, and 5)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.models import Violation


class SignatureDetector:
    """Stub detector for argument-use, explicit-intent, and abstraction dogmas."""

    rule_ids = (
        "ZEN-UTILIZE-ARGUMENTS",
        "ZEN-EXPLICIT-INTENT",
        "ZEN-RIGHT-ABSTRACTION",
    )

    def detect(self, code: str) -> list[Violation]:
        """Return no violations until signature detectors are implemented."""
        _ = code
        return []
