"""Detectors for TOML file quality, enforcing table structure, key conventions, and value formatting."""

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import (
    TomlCommentClarityConfig,
    TomlDuplicateKeysConfig,
    TomlFloatIntegerConfig,
    TomlIsoDatetimeConfig,
    TomlLowercaseKeysConfig,
    TomlNoInlineTablesConfig,
    TomlOrderConfig,
    TomlTrailingCommasConfig,
)
from mcp_zen_of_languages.models import Location, Violation

# Minimum number of table headers needed to check for large inter-table gaps
MIN_TABLE_HEADERS_FOR_GAP = 2

# Maximum allowed line gap between consecutive TOML table sections
MAX_TABLE_GAP_LINES = 10


class TomlNoInlineTablesDetector(
    ViolationDetector[TomlNoInlineTablesConfig], LocationHelperMixin
):
    """Flags inline table syntax (``key = { ... }``) that should use full table sections.

    Inline tables are compact but become hard to read and diff when they grow
    beyond a few key-value pairs.  The TOML specification intentionally limits
    inline tables to a single line, so complex structures are better expressed
    as standard ``[table]`` sections for clarity and version-control friendliness.
    """

    @property
    def name(self) -> str:
        """Return ``'toml-001'`` identifying the inline tables detector.

        Returns:
            str: The ``'toml-001'`` rule identifier.
        """
        return "toml-001"

    def detect(
        self, context: AnalysisContext, config: TomlNoInlineTablesConfig
    ) -> list[Violation]:
        """Scan for ``= {`` patterns indicating inline table assignments.

        Args:
            context: Analysis context holding the raw TOML text.
            config: Inline table thresholds and violation message templates.

        Returns:
            list[Violation]: One violation per line containing an inline table.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="{",
                location=Location(line=idx, column=line.find("{") + 1),
                suggestion="Prefer full tables over inline tables.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if re.search(r"=\s*\{", line)
        ]
        return violations


class TomlDuplicateKeysDetector(
    ViolationDetector[TomlDuplicateKeysConfig], LocationHelperMixin
):
    """Catches repeated bare keys within the same scope of a TOML file.

    TOML forbids duplicate keys at the same level; most parsers will either
    error or silently use the last value.  This detector performs a linear scan
    of top-level assignments (outside ``[table]`` headers) to surface
    duplicates before they cause parser failures or data loss.
    """

    @property
    def name(self) -> str:
        """Return ``'toml-002'`` identifying the duplicate keys detector.

        Returns:
            str: The ``'toml-002'`` rule identifier.
        """
        return "toml-002"

    def detect(
        self, context: AnalysisContext, config: TomlDuplicateKeysConfig
    ) -> list[Violation]:
        """Track seen keys and flag any that appear more than once at the same level.

        Args:
            context: Analysis context holding the raw TOML text.
            config: Duplicate key thresholds and violation message templates.

        Returns:
            list[Violation]: One violation per duplicate key occurrence.
        """
        violations: list[Violation] = []
        seen: set[str] = set()
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if line.strip().startswith("["):
                continue
            match = re.match(r"^\s*([A-Za-z0-9_.-]+)\s*=", line)
            if not match:
                continue
            key = match[1]
            if key in seen:
                violations.append(
                    self.build_violation(
                        config,
                        contains=key,
                        location=Location(line=idx, column=1),
                        suggestion="Avoid duplicate keys in TOML files.",
                    )
                )
            seen.add(key)
        return violations


class TomlLowercaseKeysDetector(
    ViolationDetector[TomlLowercaseKeysConfig], LocationHelperMixin
):
    """Enforces lowercase key names throughout the TOML document.

    TOML keys are case-sensitive, so ``Name`` and ``name`` are distinct keys.
    Mixing cases within a project invites hard-to-spot bugs where a consumer
    references the wrong variant.  Standardising on lowercase (with hyphens or
    underscores for word separation) improves predictability and grep-ability.
    """

    @property
    def name(self) -> str:
        """Return ``'toml-003'`` identifying the lowercase keys detector.

        Returns:
            str: The ``'toml-003'`` rule identifier.
        """
        return "toml-003"

    def detect(
        self, context: AnalysisContext, config: TomlLowercaseKeysConfig
    ) -> list[Violation]:
        """Scan key assignments and flag any containing uppercase characters.

        Args:
            context: Analysis context holding the raw TOML text.
            config: Lowercase key thresholds and violation message templates.

        Returns:
            list[Violation]: One violation per key that contains uppercase letters.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            match = re.match(r"^\s*([A-Za-z0-9_.-]+)\s*=", line)
            if not match:
                continue
            key = match[1]
            if any(char.isupper() for char in key):
                violations.append(
                    self.build_violation(
                        config,
                        contains=key,
                        location=Location(line=idx, column=1),
                        suggestion="Use lowercase keys for TOML consistency.",
                    )
                )
        return violations


class TomlTrailingCommasDetector(
    ViolationDetector[TomlTrailingCommasConfig], LocationHelperMixin
):
    """Detects trailing commas inside TOML arrays and inline tables.

    Unlike JSON5 or JavaScript, TOML does not permit trailing commas in arrays
    or inline tables.  Their presence causes parser errors, and some editors
    may silently insert them during copy-paste.  This detector catches the
    pattern early to prevent downstream parsing failures.
    """

    @property
    def name(self) -> str:
        """Return ``'toml-004'`` identifying the trailing commas detector.

        Returns:
            str: The ``'toml-004'`` rule identifier.
        """
        return "toml-004"

    def detect(
        self, context: AnalysisContext, config: TomlTrailingCommasConfig
    ) -> list[Violation]:
        """Search for comma-then-closing-bracket patterns on each line.

        Args:
            context: Analysis context holding the raw TOML text.
            config: Trailing comma thresholds and violation message templates.

        Returns:
            list[Violation]: One violation per line containing a trailing comma.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="trailing comma",
                location=Location(line=idx, column=1),
                suggestion="Remove trailing commas for TOML clarity.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if re.search(r",\s*[\]\}]", line)
        ]
        return violations


class TomlCommentClarityDetector(
    ViolationDetector[TomlCommentClarityConfig], LocationHelperMixin
):
    """Ensures TOML files with non-trivial configuration include explanatory comments.

    Configuration files often contain "magic" values whose purpose is unclear
    without context.  A TOML file that assigns values but lacks any ``#``
    comments forces readers to guess intent.  This detector compares the
    number of comment lines against a configurable minimum and flags
    under-documented files.
    """

    @property
    def name(self) -> str:
        """Return ``'toml-005'`` identifying the comment clarity detector.

        Returns:
            str: The ``'toml-005'`` rule identifier.
        """
        return "toml-005"

    def detect(
        self, context: AnalysisContext, config: TomlCommentClarityConfig
    ) -> list[Violation]:
        """Count comment lines and flag the file when fewer than *min_comment_lines* exist.

        Args:
            context: Analysis context holding the raw TOML text.
            config: Comment clarity thresholds including ``min_comment_lines``.

        Returns:
            list[Violation]: A single violation when comment coverage is below the threshold.
        """
        comments = [
            line for line in context.code.splitlines() if line.strip().startswith("#")
        ]
        if len(comments) < config.min_comment_lines and " = " in context.code:
            return [
                self.build_violation(
                    config,
                    contains="comment",
                    location=Location(line=1, column=1),
                    suggestion="Add comments for magic values.",
                )
            ]
        return []


class TomlOrderDetector(ViolationDetector[TomlOrderConfig], LocationHelperMixin):
    """Detects poorly grouped table sections that are separated by excessive whitespace.

    Logically related TOML tables should appear near each other so readers can
    scan the file top-to-bottom without jumping.  When two consecutive
    ``[table]`` headers are separated by more than ten lines, this detector
    flags the gap to encourage tighter grouping and optional blank-line
    separators.
    """

    @property
    def name(self) -> str:
        """Return ``'toml-006'`` identifying the table order detector.

        Returns:
            str: The ``'toml-006'`` rule identifier.
        """
        return "toml-006"

    def detect(
        self, context: AnalysisContext, config: TomlOrderConfig
    ) -> list[Violation]:
        """Measure line gaps between consecutive ``[table]`` headers and flag large separations.

        Args:
            context: Analysis context holding the raw TOML text.
            config: Table order thresholds and violation message templates.

        Returns:
            list[Violation]: A single violation when any inter-table gap exceeds ten lines.
        """
        table_headers = [
            idx
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if line.strip().startswith("[") and line.strip().endswith("]")
        ]
        if len(table_headers) >= MIN_TABLE_HEADERS_FOR_GAP:
            gaps = [b - a for a, b in zip(table_headers, table_headers[1:], strict=False)]
            if any(gap > MAX_TABLE_GAP_LINES for gap in gaps):
                return [
                    self.build_violation(
                        config,
                        contains="table order",
                        location=Location(line=table_headers[0], column=1),
                        suggestion="Group related TOML tables together.",
                    )
                ]
        return []


class TomlIsoDatetimeDetector(
    ViolationDetector[TomlIsoDatetimeConfig], LocationHelperMixin
):
    """Enforces ISO 8601 datetime formatting in quoted TOML string values.

    TOML supports native datetime literals, but quoted strings with
    locale-specific formats like ``MM/DD/YYYY`` are still common in
    hand-edited files.  This detector identifies such patterns and recommends
    ISO 8601 (``YYYY-MM-DD`` or ``YYYY-MM-DDTHH:MM:SSZ``) for consistency
    and unambiguous parsing.
    """

    @property
    def name(self) -> str:
        """Return ``'toml-007'`` identifying the ISO datetime detector.

        Returns:
            str: The ``'toml-007'`` rule identifier.
        """
        return "toml-007"

    def detect(
        self, context: AnalysisContext, config: TomlIsoDatetimeConfig
    ) -> list[Violation]:
        """Search quoted string values for non-ISO date patterns like ``MM/DD/YYYY``.

        Args:
            context: Analysis context holding the raw TOML text.
            config: ISO datetime thresholds and violation message templates.

        Returns:
            list[Violation]: Violations for the first non-ISO date string found.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            match = re.search(r"=\s*\"([^\"]+)\"", line)
            if not match:
                continue
            value = match[1]
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}Z?", value):
                continue
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                continue
            if re.search(r"\d{2}/\d{2}/\d{4}", value):
                violations.append(
                    self.build_violation(
                        config,
                        contains=value,
                        location=Location(line=idx, column=1),
                        suggestion="Use ISO 8601 date/time strings.",
                    )
                )
                break
        return violations


class TomlFloatIntegerDetector(
    ViolationDetector[TomlFloatIntegerConfig], LocationHelperMixin
):
    """Flags float literals ending in ``.0`` that should be plain integers.

    Writing ``count = 5.0`` when the value is conceptually an integer
    introduces unnecessary type ambiguity.  Downstream consumers may treat it
    as a float, leading to unexpected behaviour in integer-only contexts.
    This detector identifies ``N.0`` patterns and suggests using the integer
    form instead.
    """

    @property
    def name(self) -> str:
        """Return ``'toml-008'`` identifying the float/integer precision detector.

        Returns:
            str: The ``'toml-008'`` rule identifier.
        """
        return "toml-008"

    def detect(
        self, context: AnalysisContext, config: TomlFloatIntegerConfig
    ) -> list[Violation]:
        """Scan assignments for numeric values matching the ``N.0`` pattern.

        Args:
            context: Analysis context holding the raw TOML text.
            config: Float/integer thresholds and violation message templates.

        Returns:
            list[Violation]: A single violation for the first ``.0`` float found.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if match := re.search(r"=\s*([0-9]+)\.0\b", line):
                violations.append(
                    self.build_violation(
                        config,
                        contains=match[0],
                        location=Location(line=idx, column=1),
                        suggestion="Use integers instead of floats ending in .0.",
                    )
                )
                break
        return violations


__all__ = [
    "TomlCommentClarityDetector",
    "TomlDuplicateKeysDetector",
    "TomlFloatIntegerDetector",
    "TomlIsoDatetimeDetector",
    "TomlLowercaseKeysDetector",
    "TomlNoInlineTablesDetector",
    "TomlOrderDetector",
    "TomlTrailingCommasDetector",
]
