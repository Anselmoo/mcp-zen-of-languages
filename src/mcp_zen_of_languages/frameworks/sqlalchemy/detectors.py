"""Explicit detector exports for the sqlalchemy framework language."""

from __future__ import annotations

from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector


class SqlalchemyRuleDetector(RulePatternDetector):
    """Framework-specific rule-pattern detector for sqlalchemy rule coverage."""


__all__ = ["SqlalchemyRuleDetector"]
