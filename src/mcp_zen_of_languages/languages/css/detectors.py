"""Detectors for CSS/SCSS/Less stylesheets."""

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import AnalysisContext, ViolationDetector
from mcp_zen_of_languages.languages.configs import (
    CssColorLiteralConfig,
    CssGodStylesheetConfig,
    CssImportChainConfig,
    CssMagicPixelsConfig,
    CssMediaQueryScaleConfig,
    CssSpecificityConfig,
    CssVendorPrefixConfig,
    CssZIndexScaleConfig,
)
from mcp_zen_of_languages.models import Location, Violation


class CssSpecificityDetector(ViolationDetector[CssSpecificityConfig]):
    """Detect excessive selector nesting and ``!important`` usage."""

    @property
    def name(self) -> str:
        """Return detector rule ID."""
        return "css-001"

    @staticmethod
    def _preserve_newlines(match: re.Match[str]) -> str:
        """Replace matched content while preserving line offsets."""
        return "\n" * match.group(0).count("\n")

    @classmethod
    def _sanitize_for_nesting_scan(cls, code: str) -> str:
        """Strip comments, strings, and interpolation blocks for brace scanning."""
        pattern = re.compile(
            r"/\*[\s\S]*?\*/|//[^\n]*|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|#\{[\s\S]*?\}",
        )
        return pattern.sub(cls._preserve_newlines, code)

    @classmethod
    def _find_nesting_violation_line(cls, code: str, max_depth: int) -> int | None:
        """Return the first line where selector nesting exceeds ``max_depth``."""
        clean_code = cls._sanitize_for_nesting_scan(code)
        depth = 0
        stack: list[bool] = []
        line = 1

        for index, char in enumerate(clean_code):
            if char == "\n":
                line += 1
                continue
            if char == "{":
                prelude_start = max(
                    clean_code.rfind("{", 0, index),
                    clean_code.rfind("}", 0, index),
                    clean_code.rfind(";", 0, index),
                    clean_code.rfind("\n", 0, index),
                )
                prelude = clean_code[prelude_start + 1 : index].lstrip()
                is_selector_block = bool(prelude) and not prelude.startswith("@")
                stack.append(is_selector_block)
                if is_selector_block:
                    depth += 1
                    if depth > max_depth:
                        return line
                continue
            if char == "}" and stack and stack.pop() and depth > 0:
                depth -= 1

        return None

    def detect(
        self, context: AnalysisContext, config: CssSpecificityConfig
    ) -> list[Violation]:
        """Detect specificity creep indicators in stylesheet text."""
        nesting_line = self._find_nesting_violation_line(
            context.code, config.max_selector_nesting
        )
        if nesting_line is not None:
            return [
                self.build_violation(
                    config,
                    contains="nested",
                    location=Location(line=nesting_line, column=1),
                    suggestion="Reduce selector nesting depth (prefer <= 3 levels).",
                ),
            ]
        important_count = len(
            re.findall(r"!\s*important\b", context.code, flags=re.IGNORECASE)
        )
        if important_count > config.max_important_usages:
            return [
                self.build_violation(
                    config,
                    contains="!important",
                    location=Location(line=1, column=1),
                    suggestion="Replace !important with lower-specificity, token-based architecture.",
                ),
            ]
        return []


class CssMagicPixelsDetector(ViolationDetector[CssMagicPixelsConfig]):
    """Detect raw pixel literals."""

    @property
    def name(self) -> str:
        """Return detector rule ID."""
        return "css-002"

    def detect(
        self, context: AnalysisContext, config: CssMagicPixelsConfig
    ) -> list[Violation]:
        """Detect raw pixel literals above configured threshold."""
        matches = list(re.finditer(r"(?<![\w-])(?:\d+\.?\d*|\.\d+)px\b", context.code))
        if len(matches) > config.max_raw_pixel_literals:
            return [
                self.build_violation(
                    config,
                    contains="pixel",
                    location=Location(
                        line=context.code[: matches[0].start()].count("\n") + 1,
                        column=1,
                    ),
                    suggestion="Use CSS variables/design tokens for spacing and sizing.",
                ),
            ]
        return []


class CssColorLiteralDetector(ViolationDetector[CssColorLiteralConfig]):
    """Detect inline color literals."""

    @property
    def name(self) -> str:
        """Return detector rule ID."""
        return "css-003"

    def detect(
        self, context: AnalysisContext, config: CssColorLiteralConfig
    ) -> list[Violation]:
        """Detect hard-coded color literals above configured threshold."""
        matches = list(
            re.finditer(
                r"(#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b|rgb[a]?\(|hsl[a]?\()",
                context.code,
            ),
        )
        if len(matches) > config.max_color_literals:
            return [
                self.build_violation(
                    config,
                    contains="color",
                    location=Location(
                        line=context.code[: matches[0].start()].count("\n") + 1,
                        column=1,
                    ),
                    suggestion="Prefer semantic design tokens or CSS variables for colors.",
                ),
            ]
        return []


class CssGodStylesheetDetector(ViolationDetector[CssGodStylesheetConfig]):
    """Detect oversized stylesheet files."""

    @property
    def name(self) -> str:
        """Return detector rule ID."""
        return "css-004"

    def detect(
        self, context: AnalysisContext, config: CssGodStylesheetConfig
    ) -> list[Violation]:
        """Detect when line count exceeds configured maximum."""
        line_count = context.lines_of_code or len(context.code.splitlines())
        if line_count > config.max_stylesheet_lines:
            return [
                self.build_violation(
                    config,
                    contains="threshold",
                    location=Location(line=1, column=1),
                    suggestion="Split stylesheet into modular partials/components.",
                ),
            ]
        return []


class CssImportChainDetector(ViolationDetector[CssImportChainConfig]):
    """Detect ``@import`` overuse."""

    @property
    def name(self) -> str:
        """Return detector rule ID."""
        return "css-005"

    def detect(
        self, context: AnalysisContext, config: CssImportChainConfig
    ) -> list[Violation]:
        """Detect ``@import`` count above configured threshold."""
        imports = len(re.findall(r"^\s*@import\b", context.code, flags=re.MULTILINE))
        if imports > config.max_import_statements:
            return [
                self.build_violation(
                    config,
                    contains="@import",
                    location=Location(line=1, column=1),
                    suggestion="Prefer @use/@forward in SCSS and bundler-managed imports.",
                ),
            ]
        return []


class CssZIndexScaleDetector(ViolationDetector[CssZIndexScaleConfig]):
    """Detect z-index values outside allowed scale."""

    @property
    def name(self) -> str:
        """Return detector rule ID."""
        return "css-006"

    def detect(
        self, context: AnalysisContext, config: CssZIndexScaleConfig
    ) -> list[Violation]:
        """Detect off-scale z-index values."""
        for idx, line in enumerate(context.code.splitlines(), start=1):
            match = re.search(r"\bz-index\s*:\s*(-?\d+)\b", line)
            if not match:
                continue
            value = int(match[1])
            if value not in config.allowed_z_index_values:
                return [
                    self.build_violation(
                        config,
                        contains="z-index",
                        location=Location(line=idx, column=1),
                        suggestion="Use the shared z-index scale from the design system.",
                    ),
                ]
        return []


class CssVendorPrefixDetector(ViolationDetector[CssVendorPrefixConfig]):
    """Detect manual vendor-prefixed properties."""

    @property
    def name(self) -> str:
        """Return detector rule ID."""
        return "css-007"

    def detect(
        self, context: AnalysisContext, config: CssVendorPrefixConfig
    ) -> list[Violation]:
        """Detect vendor-prefixed properties above configured threshold."""
        matches = re.findall(r"-(webkit|moz|ms|o)-[a-z-]+\s*:", context.code)
        if len(matches) > config.max_vendor_prefixed_properties:
            return [
                self.build_violation(
                    config,
                    contains="vendor",
                    location=Location(line=1, column=1),
                    suggestion="Remove manual prefixes and rely on autoprefixer/browserslist.",
                ),
            ]
        return []


class CssMediaQueryScaleDetector(ViolationDetector[CssMediaQueryScaleConfig]):
    """Detect inconsistent media query breakpoints."""

    @property
    def name(self) -> str:
        """Return detector rule ID."""
        return "css-008"

    def detect(
        self, context: AnalysisContext, config: CssMediaQueryScaleConfig
    ) -> list[Violation]:
        """Detect media-query breakpoints that are off the allowed scale."""
        pattern = re.compile(
            r"@media[\s\S]*?(?:min-width|max-width)\s*:\s*(\d+)(px|rem|em)",
            flags=re.IGNORECASE,
        )
        for match in pattern.finditer(context.code):
            value = int(match[1])
            unit = match[2]
            if unit == "px" and value not in config.allowed_breakpoint_values:
                line_number = context.code.count("\n", 0, match.start()) + 1
                return [
                    self.build_violation(
                        config,
                        contains="breakpoint",
                        location=Location(line=line_number, column=1),
                        suggestion="Align media query breakpoints to the agreed scale.",
                    ),
                ]
        return []


__all__ = [
    "CssColorLiteralDetector",
    "CssGodStylesheetDetector",
    "CssImportChainDetector",
    "CssMagicPixelsDetector",
    "CssMediaQueryScaleDetector",
    "CssSpecificityDetector",
    "CssVendorPrefixDetector",
    "CssZIndexScaleDetector",
]
