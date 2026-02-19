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

    def detect(self, context: AnalysisContext, config: CssSpecificityConfig) -> list[Violation]:
        """Detect specificity creep indicators in stylesheet text."""
        lines = context.code.splitlines()
        depth = 0
        for idx, line in enumerate(lines, start=1):
            depth += line.count("{")
            if depth > config.max_selector_nesting:
                return [
                    self.build_violation(
                        config,
                        contains="nested",
                        location=Location(line=idx, column=1),
                        suggestion="Reduce selector nesting depth (prefer <= 3 levels).",
                    ),
                ]
            depth = max(0, depth - line.count("}"))
        important_count = context.code.count("!important")
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

    def detect(self, context: AnalysisContext, config: CssMagicPixelsConfig) -> list[Violation]:
        """Detect raw pixel literals above configured threshold."""
        matches = list(re.finditer(r"(?<![\w-])([1-9]\d*)px\b", context.code))
        if len(matches) > config.max_raw_pixel_literals:
            return [
                self.build_violation(
                    config,
                    contains="pixel",
                    location=Location(line=context.code[: matches[0].start()].count("\n") + 1, column=1),
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

    def detect(self, context: AnalysisContext, config: CssColorLiteralConfig) -> list[Violation]:
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
                    location=Location(line=context.code[: matches[0].start()].count("\n") + 1, column=1),
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

    def detect(self, context: AnalysisContext, config: CssGodStylesheetConfig) -> list[Violation]:
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

    def detect(self, context: AnalysisContext, config: CssImportChainConfig) -> list[Violation]:
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

    def detect(self, context: AnalysisContext, config: CssZIndexScaleConfig) -> list[Violation]:
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

    def detect(self, context: AnalysisContext, config: CssVendorPrefixConfig) -> list[Violation]:
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

    def detect(self, context: AnalysisContext, config: CssMediaQueryScaleConfig) -> list[Violation]:
        """Detect media-query breakpoints that are off the allowed scale."""
        pattern = re.compile(r"@media[^{]*(?:min-width|max-width)\s*:\s*(\d+)(px|rem|em)")
        for idx, line in enumerate(context.code.splitlines(), start=1):
            match = pattern.search(line)
            if not match:
                continue
            value = int(match[1])
            unit = match[2]
            if unit == "px" and value not in config.allowed_breakpoint_values:
                return [
                    self.build_violation(
                        config,
                        contains="breakpoint",
                        location=Location(line=idx, column=1),
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
