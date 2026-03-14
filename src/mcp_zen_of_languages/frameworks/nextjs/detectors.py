"""Rule-aware detectors for Next.js framework conventions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_zen_of_languages.frameworks.detector_base import FrameworkRuleDetectorBase
from mcp_zen_of_languages.models import Location


if TYPE_CHECKING:
    from collections.abc import Callable

    from mcp_zen_of_languages.analyzers.base import AnalysisContext
    from mcp_zen_of_languages.languages.configs import DetectorConfig
    from mcp_zen_of_languages.models import Violation


class NextjsRuleDetector(FrameworkRuleDetectorBase):
    """Framework-specific rule detector for Next.js rule coverage."""

    def _rule_handlers(
        self,
    ) -> dict[str, Callable[[AnalysisContext, DetectorConfig], list[Violation]]]:
        return {
            "nextjs-001": self._detect_raw_internal_anchors,
            "nextjs-002": self._detect_raw_images,
            "nextjs-003": self._detect_app_router_gssp,
            "nextjs-004": self._detect_raw_error_serialization,
            "nextjs-005": self._detect_client_fetch_in_effects,
        }

    def _detect_raw_internal_anchors(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        pattern = r"<a\b[^>]*\bhref=['\"]/(?!/)[^'\"]*['\"][^>]*>"
        return self.regex_violations(context, config, pattern, contains='href="/')

    def _detect_raw_images(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self.regex_violations(context, config, r"<img\s+", contains="<img")

    def _detect_app_router_gssp(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self.first_substring_violation(
            context,
            config,
            "getServerSideProps",
            contains="getServerSideProps",
        )

    def _detect_raw_error_serialization(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        pattern = (
            r"(?:NextResponse|Response)\.json\(\s*error\b"
            r"|new\s+Response\(\s*JSON\.stringify\(\s*error\b"
        )
        return self.regex_violations(context, config, pattern, contains="error")

    def _detect_client_fetch_in_effects(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for offset, effect_block in _hook_call_blocks(context.code, "useEffect"):
            if "fetch(" not in effect_block:
                continue
            line, column = self._line_and_column_for_offset(context.code, offset)
            violations.append(
                self.build_violation(
                    config,
                    contains="fetch(",
                    location=Location(line=line, column=column),
                    suggestion=config.recommended_alternative,
                )
            )
        return violations


def _hook_call_blocks(code: str, hook_name: str) -> list[tuple[int, str]]:
    """Return balanced hook call slices keyed by source offset."""
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


class _BoundNextjsDetector(NextjsRuleDetector):
    """Base class for rule-bound nextjs detectors."""

    _handler_name: str

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        """Run the bound nextjs detector handler."""
        handler = getattr(self, self._handler_name)
        return handler(context, config)


class NextjsAppRouterDetector(_BoundNextjsDetector):
    """Concrete detector binding for NextjsAppRouterDetector."""

    _handler_name = "_detect_app_router_gssp"


class NextjsErrorResponseDetector(_BoundNextjsDetector):
    """Concrete detector binding for NextjsErrorResponseDetector."""

    _handler_name = "_detect_raw_error_serialization"


class NextjsImageOptimizationDetector(_BoundNextjsDetector):
    """Concrete detector binding for NextjsImageOptimizationDetector."""

    _handler_name = "_detect_raw_images"


class NextjsLinkDetector(_BoundNextjsDetector):
    """Concrete detector binding for NextjsLinkDetector."""

    _handler_name = "_detect_raw_internal_anchors"


class NextjsServerDataDetector(_BoundNextjsDetector):
    """Concrete detector binding for NextjsServerDataDetector."""

    _handler_name = "_detect_client_fetch_in_effects"


__all__ = [
    "NextjsAppRouterDetector",
    "NextjsErrorResponseDetector",
    "NextjsImageOptimizationDetector",
    "NextjsLinkDetector",
    "NextjsServerDataDetector",
]
