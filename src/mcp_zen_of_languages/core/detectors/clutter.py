"""Clutter dogma detector built on the shared rule-pattern engine."""

from __future__ import annotations

from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector


class ClutterDetector(RulePatternDetector):
    """Cross-language detector for clutter, naming, and complexity rules."""

    UNIVERSAL_RULE_IDS = (
        "ZEN-UNAMBIGUOUS-NAME",
        "ZEN-RUTHLESS-DELETION",
        "ZEN-PROPORTIONATE-COMPLEXITY",
    )

    def __init__(self) -> None:
        """Initialize with the universal rule IDs for the clutter domain."""
        super().__init__()
        self.rule_ids = list(self.UNIVERSAL_RULE_IDS)

    @property
    def name(self) -> str:
        """Return stable detector name for future pipeline wiring."""
        return "universal_clutter"
