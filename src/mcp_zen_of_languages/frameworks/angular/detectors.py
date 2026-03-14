"""Explicit detector exports for the angular framework language."""

from __future__ import annotations

from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector


class AngularRuleDetector(RulePatternDetector):
    """Framework-specific rule-pattern detector for angular rule coverage."""


__all__ = ["AngularRuleDetector"]
