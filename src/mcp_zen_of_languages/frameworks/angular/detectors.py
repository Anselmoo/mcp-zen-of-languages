"""Rule-aware detectors for Angular framework conventions."""

from __future__ import annotations

import re

from typing import TYPE_CHECKING

from mcp_zen_of_languages.frameworks.detector_base import FrameworkRuleDetectorBase
from mcp_zen_of_languages.models import Location


if TYPE_CHECKING:
    from collections.abc import Callable

    from mcp_zen_of_languages.analyzers.base import AnalysisContext
    from mcp_zen_of_languages.languages.configs import DetectorConfig
    from mcp_zen_of_languages.models import Violation


class AngularRuleDetector(FrameworkRuleDetectorBase):
    """Framework-specific rule detector for Angular rule coverage."""

    def _rule_handlers(
        self,
    ) -> dict[str, Callable[[AnalysisContext, DetectorConfig], list[Violation]]]:
        return {
            "angular-001": self._detect_missing_onpush,
            "angular-002": self._detect_any_annotations,
            "angular-003": self._detect_unsafe_subscriptions,
            "angular-004": self._detect_selector_prefixes,
            "angular-005": self._detect_eager_feature_routes,
        }

    def _detect_missing_onpush(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for offset, decorator in _decorator_blocks(context.code, "@Component"):
            if "ChangeDetectionStrategy.OnPush" in decorator:
                continue
            line, column = self._line_and_column_for_offset(context.code, offset)
            violations.append(
                self.build_violation(
                    config,
                    contains="@Component",
                    location=Location(line=line, column=column),
                    suggestion=config.recommended_alternative,
                )
            )
        return violations

    def _detect_any_annotations(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        pattern = r":\s*any\b|\bas\s+any\b|<any>"
        return self.regex_violations(context, config, pattern, contains="any")

    def _detect_unsafe_subscriptions(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for match in re.finditer(r"\.subscribe\s*\(", context.code):
            window_start = max(0, match.start() - 160)
            nearby_code = context.code[window_start : match.end() + 80]
            if re.search(
                r"\b(?:takeUntilDestroyed|takeUntil|firstValueFrom|lastValueFrom)\s*\(",
                nearby_code,
            ):
                continue
            line, column = self._line_and_column_for_offset(context.code, match.start())
            violations.append(
                self.build_violation(
                    config,
                    contains=".subscribe(",
                    location=Location(line=line, column=column),
                    suggestion=config.recommended_alternative,
                )
            )
        return violations

    def _detect_selector_prefixes(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        pattern = r"selector\s*:\s*['\"](?!app-|lib-)[^'\"]+['\"]"
        return self.regex_violations(context, config, pattern, contains="selector")

    def _detect_eager_feature_routes(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        pattern = r"path\s*:\s*['\"][^'\"]+['\"]\s*,\s*component\s*:"
        return self.regex_violations(context, config, pattern, contains="component")


def _decorator_blocks(code: str, decorator_name: str) -> list[tuple[int, str]]:
    """Return balanced decorator call blocks keyed by source offset."""
    blocks: list[tuple[int, str]] = []
    start = 0
    marker = f"{decorator_name}("
    while True:
        offset = code.find(marker, start)
        if offset == -1:
            return blocks
        open_paren = code.find("(", offset)
        if open_paren == -1:
            return blocks
        depth = 0
        end = open_paren
        while end < len(code):
            char = code[end]
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    blocks.append((offset, code[offset : end + 1]))
                    start = end + 1
                    break
            end += 1
        else:
            return blocks


class _BoundAngularDetector(AngularRuleDetector):
    """Base class for rule-bound angular detectors."""

    _handler_name: str

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        """Run the bound angular detector handler."""
        handler = getattr(self, self._handler_name)
        return handler(context, config)


class AngularLazyRouteDetector(_BoundAngularDetector):
    """Concrete detector binding for AngularLazyRouteDetector."""

    _handler_name = "_detect_eager_feature_routes"


class AngularNoAnyDetector(_BoundAngularDetector):
    """Concrete detector binding for AngularNoAnyDetector."""

    _handler_name = "_detect_any_annotations"


class AngularOnPushDetector(_BoundAngularDetector):
    """Concrete detector binding for AngularOnPushDetector."""

    _handler_name = "_detect_missing_onpush"


class AngularSelectorPrefixDetector(_BoundAngularDetector):
    """Concrete detector binding for AngularSelectorPrefixDetector."""

    _handler_name = "_detect_selector_prefixes"


class AngularSubscriptionLifecycleDetector(_BoundAngularDetector):
    """Concrete detector binding for AngularSubscriptionLifecycleDetector."""

    _handler_name = "_detect_unsafe_subscriptions"


__all__ = [
    "AngularLazyRouteDetector",
    "AngularNoAnyDetector",
    "AngularOnPushDetector",
    "AngularSelectorPrefixDetector",
    "AngularSubscriptionLifecycleDetector",
]
