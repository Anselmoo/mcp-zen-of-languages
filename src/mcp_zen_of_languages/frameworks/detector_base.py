"""Shared framework detector helpers built on top of RulePatternDetector."""

from __future__ import annotations

import re

from typing import TYPE_CHECKING

from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector
from mcp_zen_of_languages.models import Location


if TYPE_CHECKING:
    from collections.abc import Callable

    from mcp_zen_of_languages.analyzers.base import AnalysisContext
    from mcp_zen_of_languages.languages.configs import DetectorConfig
    from mcp_zen_of_languages.models import Violation


class FrameworkRuleDetectorBase(RulePatternDetector):
    """Rule-aware framework detector with optional per-rule specialized handlers."""

    def _rule_handlers(
        self,
    ) -> dict[str, Callable[[AnalysisContext, DetectorConfig], list[Violation]]]:
        """Return per-rule handler overrides keyed by framework rule id."""
        return {}

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        """Dispatch to a specialized rule handler when one is registered."""
        handler = self._rule_handlers().get(config.type)
        if handler is None:
            return super().detect(context, config)
        return handler(context, config)

    def regex_violations(  # noqa: PLR0913
        self,
        context: AnalysisContext,
        config: DetectorConfig,
        pattern: str,
        *,
        contains: str | None = None,
        suggestion: str | None = None,
        message: str | None = None,
    ) -> list[Violation]:
        """Return one violation per regex match in the current source text."""
        return [
            self.build_violation(
                config,
                message=message,
                contains=contains,
                location=self.location_for_offset(context.code, match.start()),
                suggestion=suggestion or config.recommended_alternative,
            )
            for match in re.finditer(pattern, context.code, re.MULTILINE | re.DOTALL)
        ]

    def location_for_offset(self, code: str, offset: int) -> Location:
        """Convert a character offset into a one-based source location."""
        line = code.count("\n", 0, offset) + 1
        last_newline = code.rfind("\n", 0, offset)
        column = offset + 1 if last_newline == -1 else offset - last_newline
        return Location(line=line, column=column)

    def first_substring_violation(  # noqa: PLR0913
        self,
        context: AnalysisContext,
        config: DetectorConfig,
        substring: str,
        *,
        contains: str | None = None,
        suggestion: str | None = None,
        message: str | None = None,
    ) -> list[Violation]:
        """Return a single violation for the first matching substring, if any."""
        if substring not in context.code:
            return []
        return [
            self.build_violation(
                config,
                message=message,
                contains=contains or substring,
                location=self.find_location_by_substring(context.code, substring),
                suggestion=suggestion or config.recommended_alternative,
            )
        ]


__all__ = ["FrameworkRuleDetectorBase"]
