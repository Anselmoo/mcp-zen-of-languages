"""Signature dogma detector stubs (Dogmas 1, 2, and 5)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.languages.configs import DetectorConfig

if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.base import AnalysisContext
    from mcp_zen_of_languages.models import Violation


class SignatureDetector(ViolationDetector[DetectorConfig]):
    """Stub detector for argument-use, explicit-intent, and abstraction dogmas."""

    UNIVERSAL_RULE_IDS = (
        "ZEN-UTILIZE-ARGUMENTS",
        "ZEN-EXPLICIT-INTENT",
        "ZEN-RIGHT-ABSTRACTION",
    )

    def __init__(self) -> None:
        """Initialize with the universal rule IDs for this stub domain."""
        super().__init__()
        self.rule_ids = list(self.UNIVERSAL_RULE_IDS)

    @property
    def name(self) -> str:
        """Return stable detector name for future pipeline wiring."""
        return "universal_signature_stub"

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        """Return no violations until signature detectors are implemented."""
        _ = (context, config)
        return []
