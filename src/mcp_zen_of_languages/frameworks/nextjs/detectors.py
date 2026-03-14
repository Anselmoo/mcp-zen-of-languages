"""Explicit detector exports for the nextjs framework language."""

from __future__ import annotations

from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector


class NextjsRuleDetector(RulePatternDetector):
    """Framework-specific rule-pattern detector for nextjs rule coverage."""


__all__ = ["NextjsRuleDetector"]
