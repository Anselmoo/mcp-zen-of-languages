"""Explicit detector exports for the django framework language."""

from __future__ import annotations

from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector


class DjangoRuleDetector(RulePatternDetector):
    """Framework-specific rule-pattern detector for django rule coverage."""


__all__ = ["DjangoRuleDetector"]
