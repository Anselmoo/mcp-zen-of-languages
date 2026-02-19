"""Detectors for YAML file quality, enforcing indentation, key conventions, and structural consistency."""

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import (
    YamlCommentIntentConfig,
    YamlConsistencyConfig,
    YamlDuplicateKeysConfig,
    YamlIndentationConfig,
    YamlKeyClarityConfig,
    YamlLowercaseKeysConfig,
    YamlNoTabsConfig,
    YamlStringStyleConfig,
)
from mcp_zen_of_languages.models import Location, Violation


class YamlIndentationDetector(
    ViolationDetector[YamlIndentationConfig],
    LocationHelperMixin,
):
    """Enforces uniform indentation width across all non-blank, non-comment lines.

    YAML's block structure relies entirely on whitespace indentation, so
    inconsistent widths can silently change document semantics.  This detector
    verifies that every indented line uses a multiple of the configured indent
    size (defaulting to two spaces) and flags deviations before they cause
    parsing surprises.
    """

    @property
    def name(self) -> str:
        """Return ``'yaml-001'`` identifying the indentation detector.

        Returns:
            str: The ``'yaml-001'`` rule identifier.
        """
        return "yaml-001"

    def detect(
        self,
        context: AnalysisContext,
        config: YamlIndentationConfig,
    ) -> list[Violation]:
        """Check each non-blank line's leading spaces against the configured indent width.

        Args:
            context: Analysis context holding the raw YAML text.
            config: Indentation thresholds including ``indent_size``.

        Returns:
            list[Violation]: One violation per line whose leading whitespace is not a multiple of *indent_size*.
        """
        violations: list[Violation] = []
        indent_size = config.indent_size
        for idx, line in enumerate(context.code.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            leading_spaces = len(line) - len(line.lstrip(" "))
            if "\t" in line[:leading_spaces]:
                continue
            if leading_spaces % indent_size != 0:
                violations.append(
                    self.build_violation(
                        config,
                        contains="indentation",
                        location=Location(line=idx, column=1),
                        suggestion=f"Use {indent_size}-space indentation consistently.",
                    ),
                )
        return violations


class YamlNoTabsDetector(ViolationDetector[YamlNoTabsConfig], LocationHelperMixin):
    """Detects tab characters anywhere in YAML content.

    The YAML specification explicitly prohibits tab characters for indentation;
    only spaces are allowed.  Tabs embedded in values are technically legal
    but often indicate copy-paste errors.  This detector flags every line
    containing a tab to prevent subtle parsing failures.
    """

    @property
    def name(self) -> str:
        """Return ``'yaml-002'`` identifying the no-tabs detector.

        Returns:
            str: The ``'yaml-002'`` rule identifier.
        """
        return "yaml-002"

    def detect(
        self,
        context: AnalysisContext,
        config: YamlNoTabsConfig,
    ) -> list[Violation]:
        """Scan every line for tab characters and report their positions.

        Args:
            context: Analysis context holding the raw YAML text.
            config: No-tabs thresholds and violation message templates.

        Returns:
            list[Violation]: One violation per line containing a tab character.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="tabs",
                location=Location(line=idx, column=line.find("\t") + 1),
                suggestion="Replace tabs with spaces.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if "\t" in line
        ]
        return violations


class YamlDuplicateKeysDetector(
    ViolationDetector[YamlDuplicateKeysConfig],
    LocationHelperMixin,
):
    """Catches repeated top-level mapping keys that cause silent data loss.

    YAML 1.1 allows duplicate keys with "last wins" semantics, while YAML 1.2
    discourages them.  Either way, duplicates usually indicate a merge
    conflict remnant or copy-paste mistake.  This detector tracks seen
    top-level keys and flags any that appear more than once.
    """

    @property
    def name(self) -> str:
        """Return ``'yaml-003'`` identifying the duplicate keys detector.

        Returns:
            str: The ``'yaml-003'`` rule identifier.
        """
        return "yaml-003"

    def detect(
        self,
        context: AnalysisContext,
        config: YamlDuplicateKeysConfig,
    ) -> list[Violation]:
        """Track top-level keys and flag any that appear more than once.

        Args:
            context: Analysis context holding the raw YAML text.
            config: Duplicate key thresholds and violation message templates.

        Returns:
            list[Violation]: One violation per duplicate key occurrence.
        """
        violations: list[Violation] = []
        seen: set[str] = set()
        for idx, line in enumerate(context.code.splitlines(), start=1):
            match = re.match(r"^([A-Za-z0-9_-]+)\s*:", line)
            if not match:
                continue
            key = match[1]
            if key in seen:
                violations.append(
                    self.build_violation(
                        config,
                        contains=key,
                        location=Location(line=idx, column=1),
                        suggestion="Avoid duplicate keys in YAML mappings.",
                    ),
                )
            seen.add(key)
        return violations


class YamlLowercaseKeysDetector(
    ViolationDetector[YamlLowercaseKeysConfig],
    LocationHelperMixin,
):
    """Enforces lowercase mapping keys throughout the YAML document.

    YAML keys are case-sensitive, so ``Name`` and ``name`` are distinct.
    Mixing cases within a project causes confusion and breaks tools that rely
    on consistent key naming.  This detector flags any key containing
    uppercase characters to encourage a uniform lowercase convention.
    """

    @property
    def name(self) -> str:
        """Return ``'yaml-004'`` identifying the lowercase keys detector.

        Returns:
            str: The ``'yaml-004'`` rule identifier.
        """
        return "yaml-004"

    def detect(
        self,
        context: AnalysisContext,
        config: YamlLowercaseKeysConfig,
    ) -> list[Violation]:
        """Scan mapping keys and flag any containing uppercase characters.

        Args:
            context: Analysis context holding the raw YAML text.
            config: Lowercase key thresholds and violation message templates.

        Returns:
            list[Violation]: One violation per key with uppercase letters.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            match = re.match(r"^\s*([A-Za-z0-9_-]+)\s*:", line)
            if not match:
                continue
            key = match[1]
            if any(char.isupper() for char in key):
                violations.append(
                    self.build_violation(
                        config,
                        contains=key,
                        location=Location(line=idx, column=1),
                        suggestion="Use lowercase keys for consistency.",
                    ),
                )
        return violations


class YamlKeyClarityDetector(
    ViolationDetector[YamlKeyClarityConfig],
    LocationHelperMixin,
):
    """Flags overly short mapping keys that sacrifice readability for brevity.

    Single- or two-character keys like ``x`` or ``id`` are acceptable in some
    contexts but often indicate a missed opportunity for self-documenting
    names.  This detector compares each key's length against a configurable
    minimum (default 3) and reports the first offender.
    """

    @property
    def name(self) -> str:
        """Return ``'yaml-005'`` identifying the key clarity detector.

        Returns:
            str: The ``'yaml-005'`` rule identifier.
        """
        return "yaml-005"

    def detect(
        self,
        context: AnalysisContext,
        config: YamlKeyClarityConfig,
    ) -> list[Violation]:
        """Check each key's length and flag the first one shorter than *min_key_length*.

        Args:
            context: Analysis context holding the raw YAML text.
            config: Key clarity thresholds including ``min_key_length``.

        Returns:
            list[Violation]: A single violation for the first overly short key found.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            match = re.match(r"^\s*([A-Za-z0-9_-]+)\s*:", line)
            if not match:
                continue
            key = match[1]
            if len(key) < config.min_key_length:
                violations.append(
                    self.build_violation(
                        config,
                        contains=key,
                        location=Location(line=idx, column=1),
                        suggestion="Use more descriptive YAML keys.",
                    ),
                )
                break
        return violations


class YamlConsistencyDetector(
    ViolationDetector[YamlConsistencyConfig],
    LocationHelperMixin,
):
    """Ensures a single, consistent list-marker style is used throughout the document.

    YAML allows ``-`` and ``*`` as sequence entry indicators, but mixing them
    in the same file confuses readers and may trip strict linters.  This
    detector collects all markers used and flags the document when more than
    one style appears or when a disallowed marker is used.
    """

    @property
    def name(self) -> str:
        """Return ``'yaml-006'`` identifying the list-marker consistency detector.

        Returns:
            str: The ``'yaml-006'`` rule identifier.
        """
        return "yaml-006"

    def detect(
        self,
        context: AnalysisContext,
        config: YamlConsistencyConfig,
    ) -> list[Violation]:
        """Collect list markers (``-`` vs ``*``) and flag mixed or disallowed usage.

        Args:
            context: Analysis context holding the raw YAML text.
            config: Consistency thresholds including ``allowed_list_markers``.

        Returns:
            list[Violation]: A single violation when marker styles are inconsistent or disallowed.
        """
        markers: set[str] = set()
        for line in context.code.splitlines():
            stripped = line.lstrip()
            if stripped.startswith("- "):
                markers.add("-")
            elif stripped.startswith("* "):
                markers.add("*")
        if len(markers) > 1:
            return [
                self.build_violation(
                    config,
                    contains="list markers",
                    location=Location(line=1, column=1),
                    suggestion="Use a consistent list marker style (e.g., '-').",
                ),
            ]
        if (
            markers
            and config.allowed_list_markers
            and not markers.issubset(set(config.allowed_list_markers))
        ):
            return [
                self.build_violation(
                    config,
                    contains="list markers",
                    location=Location(line=1, column=1),
                    suggestion="Use allowed YAML list markers only.",
                ),
            ]
        return []


class YamlCommentIntentDetector(
    ViolationDetector[YamlCommentIntentConfig],
    LocationHelperMixin,
):
    """Ensures complex YAML files include explanatory comments.

    Configuration files that exceed a minimum line count without any ``#``
    comments are difficult for new contributors to understand.  This detector
    counts non-empty content lines and comment lines, flagging documents that
    fall below the configured comment threshold relative to their size.
    """

    @property
    def name(self) -> str:
        """Return ``'yaml-007'`` identifying the comment intent detector.

        Returns:
            str: The ``'yaml-007'`` rule identifier.
        """
        return "yaml-007"

    def detect(
        self,
        context: AnalysisContext,
        config: YamlCommentIntentConfig,
    ) -> list[Violation]:
        """Count non-empty and comment lines, flagging when comment coverage is too low.

        Args:
            context: Analysis context holding the raw YAML text.
            config: Comment intent thresholds including ``min_comment_lines`` and ``min_nonempty_lines``.

        Returns:
            list[Violation]: A single violation when the file is large enough but lacks sufficient comments.
        """
        nonempty_lines = [
            line
            for line in context.code.splitlines()
            if line.strip() and not line.strip().startswith("---")
        ]
        comment_lines = [
            line for line in nonempty_lines if line.strip().startswith("#")
        ]
        if (
            len(nonempty_lines) >= config.min_nonempty_lines
            and len(comment_lines) < config.min_comment_lines
        ):
            return [
                self.build_violation(
                    config,
                    contains="comment",
                    location=Location(line=1, column=1),
                    suggestion="Add comments to explain intent in complex YAML.",
                ),
            ]
        return []


class YamlStringStyleDetector(
    ViolationDetector[YamlStringStyleConfig],
    LocationHelperMixin,
):
    """Flags unquoted string values that contain spaces or special YAML characters.

    Unquoted strings with colons, hashes, or spaces can be misinterpreted by
    parsers—for example, ``key: value: extra`` may be parsed differently than
    intended.  This detector identifies such values and recommends wrapping
    them in single or double quotes to eliminate ambiguity.

    Note:
        Boolean literals (``true``, ``false``, ``null``) and plain numbers
        are excluded from this check.
    """

    @property
    def name(self) -> str:
        """Return ``'yaml-008'`` identifying the string style detector.

        Returns:
            str: The ``'yaml-008'`` rule identifier.
        """
        return "yaml-008"

    def detect(
        self,
        context: AnalysisContext,
        config: YamlStringStyleConfig,
    ) -> list[Violation]:
        """Search for unquoted values containing spaces, colons, or hashes that need quoting.

        Args:
            context: Analysis context holding the raw YAML text.
            config: String style thresholds including ``require_quotes_for_specials``.

        Returns:
            list[Violation]: A single violation for the first unquoted special-character value found.
        """
        if not config.require_quotes_for_specials:
            return []
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            match = re.match(r"^\s*([A-Za-z0-9_-]+)\s*:\s*(.+)$", line)
            if not match:
                continue
            value = match[2].strip()
            if not value or value.startswith(("#", "|", ">")):
                continue
            if value[0] in {"'", '"'}:
                continue
            if re.fullmatch(r"(true|false|null)", value):
                continue
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?", value):
                continue
            if re.search(r"[\s:#]", value):
                violations.append(
                    self.build_violation(
                        config,
                        contains=value,
                        location=Location(line=idx, column=1),
                        suggestion="Quote strings containing spaces or special characters.",
                    ),
                )
                break
        return violations


__all__ = [
    "YamlCommentIntentDetector",
    "YamlConsistencyDetector",
    "YamlDuplicateKeysDetector",
    "YamlIndentationDetector",
    "YamlKeyClarityDetector",
    "YamlLowercaseKeysDetector",
    "YamlNoTabsDetector",
    "YamlStringStyleDetector",
]
