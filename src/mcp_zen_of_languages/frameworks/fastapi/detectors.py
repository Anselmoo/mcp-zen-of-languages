"""Explicit detector exports for the fastapi framework language."""

from __future__ import annotations

from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector


class FastapiRuleDetector(RulePatternDetector):
    """Framework-specific rule-pattern detector for fastapi rule coverage."""


__all__ = ["FastapiRuleDetector"]
