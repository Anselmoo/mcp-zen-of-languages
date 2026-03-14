"""Explicit detector exports for the pydantic framework language."""

from __future__ import annotations

from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector


class PydanticRuleDetector(RulePatternDetector):
    """Framework-specific rule-pattern detector for pydantic rule coverage."""


__all__ = ["PydanticRuleDetector"]
