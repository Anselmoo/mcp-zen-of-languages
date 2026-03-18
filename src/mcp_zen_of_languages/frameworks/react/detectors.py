"""Rule-aware detectors for React framework conventions."""

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


class ReactRuleDetector(FrameworkRuleDetectorBase):
    """Framework-specific rule detector for React rule coverage."""

    def _rule_handlers(
        self,
    ) -> dict[str, Callable[[AnalysisContext, DetectorConfig], list[Violation]]]:
        return {
            "react-001": self._detect_index_keys,
            "react-002": self._detect_inline_handlers,
            "react-003": self._detect_dom_queries,
            "react-004": self._detect_conditional_hooks,
            "react-005": self._detect_effects_missing_cleanup,
        }

    def _detect_index_keys(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        pattern = (
            r"key=\{\s*(?:index|i|idx|itemIndex)\s*\}"
            r"|key=\{\s*`?\$\{(?:index|i|idx|itemIndex)\}`?\s*\}"
        )
        return self.regex_violations(context, config, pattern, contains="key={")

    def _detect_inline_handlers(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        pattern = (
            r"on(?:Click|Change|Submit|Input|KeyDown|KeyUp|MouseEnter|MouseLeave)"
            r"\s*=\s*\{\s*(?:async\s+)?(?:\([^)]*\)|[A-Za-z_]\w*)\s*=>"
        )
        return self.regex_violations(context, config, pattern, contains="on")

    def _detect_dom_queries(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        pattern = (
            r"\bdocument\.(?:getElementById|querySelector|querySelectorAll)\("
            r"|\.\s*innerHTML\s*="
        )
        return self.regex_violations(context, config, pattern, contains="document.")

    def _detect_conditional_hooks(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        patterns = [
            r"\bif\s*\([^)]*\)\s*\{[\s\S]{0,400}?\buse[A-Z]\w*\(",
            r"\b(?:for|while)\s*\([^)]*\)\s*\{[\s\S]{0,400}?\buse[A-Z]\w*\(",
            r"\b(?:switch|case)\b[\s\S]{0,400}?\buse[A-Z]\w*\(",
        ]
        violations: list[Violation] = []
        for pattern in patterns:
            violations.extend(self.regex_violations(context, config, pattern))
        return violations

    def _detect_effects_missing_cleanup(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for offset, effect_block in _hook_call_blocks(context.code, "useEffect"):
            if not re.search(r"\b(?:setInterval|addEventListener)\s*\(", effect_block):
                continue
            has_cleanup = (
                "return () =>" in effect_block
                or "return () => {" in effect_block
                or re.search(
                    r"\b(?:clearInterval|clearTimeout|removeEventListener)\s*\(",
                    effect_block,
                )
                is not None
            )
            if has_cleanup:
                continue
            line, column = self._line_and_column_for_offset(context.code, offset)
            violations.append(
                self.build_violation(
                    config,
                    location=Location(line=line, column=column),
                    suggestion=config.recommended_alternative,
                )
            )
        return violations


def _hook_call_blocks(code: str, hook_name: str) -> list[tuple[int, str]]:
    """Return balanced hook call slices keyed by their source offset."""
    blocks: list[tuple[int, str]] = []
    start = 0
    marker = f"{hook_name}("
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


class _BoundReactDetector(ReactRuleDetector):
    """Base class for rule-bound react detectors."""

    _handler_name: str

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        """Run the bound react detector handler."""
        handler = getattr(self, self._handler_name)
        return handler(context, config)


class ReactConditionalHookDetector(_BoundReactDetector):
    """Concrete detector binding for ReactConditionalHookDetector."""

    _handler_name = "_detect_conditional_hooks"


class ReactDirectDomAccessDetector(_BoundReactDetector):
    """Concrete detector binding for ReactDirectDomAccessDetector."""

    _handler_name = "_detect_dom_queries"


class ReactEffectCleanupDetector(_BoundReactDetector):
    """Concrete detector binding for ReactEffectCleanupDetector."""

    _handler_name = "_detect_effects_missing_cleanup"


class ReactInlineHandlerDetector(_BoundReactDetector):
    """Concrete detector binding for ReactInlineHandlerDetector."""

    _handler_name = "_detect_inline_handlers"


class ReactStableKeyDetector(_BoundReactDetector):
    """Concrete detector binding for ReactStableKeyDetector."""

    _handler_name = "_detect_index_keys"


__all__ = [
    "ReactConditionalHookDetector",
    "ReactDirectDomAccessDetector",
    "ReactEffectCleanupDetector",
    "ReactInlineHandlerDetector",
    "ReactStableKeyDetector",
]
