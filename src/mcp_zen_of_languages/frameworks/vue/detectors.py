"""Explicit detector exports for the vue framework language."""

from __future__ import annotations

from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector


class VueRuleDetector(RulePatternDetector):
    """Framework-specific rule-pattern detector for vue rule coverage."""


__all__ = ["VueRuleDetector"]
