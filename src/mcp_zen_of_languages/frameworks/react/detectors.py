"""Explicit detector exports for the react framework language."""

from __future__ import annotations

from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector


class ReactRuleDetector(RulePatternDetector):
    """Framework-specific rule-pattern detector for react rule coverage."""


__all__ = ["ReactRuleDetector"]
