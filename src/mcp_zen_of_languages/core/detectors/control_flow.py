"""Control-flow dogma detector built on the shared rule-pattern engine."""

from __future__ import annotations

from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector


class ControlFlowDetector(RulePatternDetector):
    """Cross-language detector for return-early and fail-fast style rules."""

    UNIVERSAL_RULE_IDS = ("ZEN-RETURN-EARLY", "ZEN-FAIL-FAST")

    def __init__(self) -> None:
        """Initialize with the universal rule IDs for the control-flow domain."""
        super().__init__()
        self.rule_ids = list(self.UNIVERSAL_RULE_IDS)

    @property
    def name(self) -> str:
        """Return stable detector name for future pipeline wiring."""
        return "universal_control_flow"
