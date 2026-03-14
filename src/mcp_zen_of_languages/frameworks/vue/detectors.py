"""Rule-aware detectors for Vue framework conventions."""

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


class VueRuleDetector(FrameworkRuleDetectorBase):
    """Framework-specific rule detector for Vue rule coverage."""

    def _rule_handlers(
        self,
    ) -> dict[str, Callable[[AnalysisContext, DetectorConfig], list[Violation]]]:
        return {
            "vue-001": self._detect_single_word_component_names,
            "vue-002": self._detect_untyped_props,
            "vue-003": self._detect_v_for_without_key,
            "vue-004": self._detect_v_if_with_v_for,
            "vue-005": self._detect_prop_mutation,
        }

    def _detect_single_word_component_names(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        patterns = [
            r"\bname\s*:\s*['\"](?P<name>[^'\"]+)['\"]",
            r"defineOptions\(\s*\{[\s\S]*?\bname\s*:\s*['\"](?P<name>[^'\"]+)['\"]",
        ]
        seen_offsets: set[int] = set()
        for pattern in patterns:
            for match in re.finditer(pattern, context.code, re.MULTILINE | re.DOTALL):
                component_name = match.group("name")
                if _is_multi_word_component_name(component_name):
                    continue
                offset = match.start("name")
                if offset in seen_offsets:
                    continue
                seen_offsets.add(offset)
                line, column = self._line_and_column_for_offset(context.code, offset)
                violations.append(
                    self.build_violation(
                        config,
                        contains=component_name,
                        location=Location(line=line, column=column),
                        suggestion=config.recommended_alternative,
                    )
                )
        return violations

    def _detect_untyped_props(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        pattern = (
            r"defineProps\(\s*\[[^\]]+\]\s*\)"
            r"|props\s*:\s*\[[^\]]+\]"
        )
        return self.regex_violations(context, config, pattern, contains="props")

    def _detect_v_for_without_key(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for match in re.finditer(r"<(?P<tag>[^>]+)>", context.code):
            opening_tag = match.group(0)
            if "v-for=" not in opening_tag:
                continue
            if ":key=" in opening_tag or "v-bind:key=" in opening_tag:
                continue
            line, column = self._line_and_column_for_offset(context.code, match.start())
            violations.append(
                self.build_violation(
                    config,
                    contains="v-for",
                    location=Location(line=line, column=column),
                    suggestion=config.recommended_alternative,
                )
            )
        return violations

    def _detect_v_if_with_v_for(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for match in re.finditer(r"<[^>]+>", context.code):
            opening_tag = match.group(0)
            if "v-if=" not in opening_tag or "v-for=" not in opening_tag:
                continue
            line, column = self._line_and_column_for_offset(context.code, match.start())
            violations.append(
                self.build_violation(
                    config,
                    contains="v-if",
                    location=Location(line=line, column=column),
                    suggestion=config.recommended_alternative,
                )
            )
        return violations

    def _detect_prop_mutation(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        pattern = r"\bprops\.\w+\s*="
        return self.regex_violations(context, config, pattern, contains="props.")


def _is_multi_word_component_name(component_name: str) -> bool:
    """Return whether a Vue component name is clearly multi-word."""
    if "-" in component_name:
        return True
    return re.search(r"[a-z0-9][A-Z]", component_name) is not None


class _BoundVueDetector(VueRuleDetector):
    """Base class for rule-bound vue detectors."""

    _handler_name: str

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        """Run the bound vue detector handler."""
        handler = getattr(self, self._handler_name)
        return handler(context, config)


class VueConditionalLoopDetector(_BoundVueDetector):
    """Concrete detector binding for VueConditionalLoopDetector."""

    _handler_name = "_detect_v_if_with_v_for"


class VueListKeyDetector(_BoundVueDetector):
    """Concrete detector binding for VueListKeyDetector."""

    _handler_name = "_detect_v_for_without_key"


class VueMultiWordNameDetector(_BoundVueDetector):
    """Concrete detector binding for VueMultiWordNameDetector."""

    _handler_name = "_detect_single_word_component_names"


class VuePropMutationDetector(_BoundVueDetector):
    """Concrete detector binding for VuePropMutationDetector."""

    _handler_name = "_detect_prop_mutation"


class VueTypedPropsDetector(_BoundVueDetector):
    """Concrete detector binding for VueTypedPropsDetector."""

    _handler_name = "_detect_untyped_props"


__all__ = [
    "VueConditionalLoopDetector",
    "VueListKeyDetector",
    "VueMultiWordNameDetector",
    "VuePropMutationDetector",
    "VueTypedPropsDetector",
]
