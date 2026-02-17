"""Re-export convenience module for [`RulePatternDetector`][mcp_zen_of_languages.languages.rules.RulePatternDetector].

Provides a stable import path so callers can write
``from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector``
without depending on the private ``rules`` module directly.
"""

from __future__ import annotations

from mcp_zen_of_languages.languages.rules import RulePatternDetector

__all__ = ["RulePatternDetector"]
