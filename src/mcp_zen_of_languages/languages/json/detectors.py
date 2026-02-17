"""Detectors for JSON document quality, enforcing strictness, schema consistency, and data formatting."""

from __future__ import annotations

import json
import re
from collections import Counter

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import (
    JsonArrayOrderConfig,
    JsonDateFormatConfig,
    JsonKeyCasingConfig,
    JsonNullHandlingConfig,
    JsonSchemaConsistencyConfig,
    JsonStrictnessConfig,
)
from mcp_zen_of_languages.models import Location, Violation


class JsonStrictnessDetector(
    ViolationDetector[JsonStrictnessConfig], LocationHelperMixin
):
    """Flags non-standard JSON extensions such as comments and trailing commas.

    Standard JSON (RFC 8259) forbids ``//`` line comments, ``/* */`` block
    comments, and trailing commas after the last element in arrays or objects.
    Many editors and parsers silently accept these extensions, but they cause
    failures in strict parsers and interoperability problems across toolchains.

    Note:
        Only the first violation per category is reported to keep output concise.
    """

    @property
    def name(self) -> str:
        """Return ``'json-001'`` identifying the JSON strictness detector.

        Returns:
            str: The ``'json-001'`` rule identifier.
        """
        return "json-001"

    def detect(
        self, context: AnalysisContext, config: JsonStrictnessConfig
    ) -> list[Violation]:
        """Scan each line for comments (``//``, ``/*``) and trailing commas before ``]`` or ``}``.

        Args:
            context: Analysis context holding the raw JSON text.
            config: Strictness thresholds and violation message templates.

        Returns:
            list[Violation]: At most one violation per strictness category found.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if "//" in line or "/*" in line:
                violations.append(
                    self.build_violation(
                        config,
                        contains="comment",
                        location=Location(line=idx, column=line.find("/") + 1),
                        suggestion="Remove comments to keep JSON strict.",
                    )
                )
                break
            if re.search(r",\s*[\]\}]", line):
                violations.append(
                    self.build_violation(
                        config,
                        contains="trailing comma",
                        location=Location(line=idx, column=1),
                        suggestion="Remove trailing commas in JSON.",
                    )
                )
                break
        return violations


class JsonSchemaConsistencyDetector(
    ViolationDetector[JsonSchemaConsistencyConfig], LocationHelperMixin
):
    """Detects inconsistent object shapes inside top-level JSON arrays.

    When a JSON document is an array of objects, each object should expose the
    same set of keys so consumers can rely on a predictable schema.  Mixed key
    sets indicate schema drift—some records may be missing required fields or
    carrying stale ones—leading to brittle downstream processing.

    Note:
        Arrays with fewer than two objects, or documents that are not arrays,
        are silently skipped.
    """

    @property
    def name(self) -> str:
        """Return ``'json-002'`` identifying the JSON schema consistency detector.

        Returns:
            str: The ``'json-002'`` rule identifier.
        """
        return "json-002"

    def detect(
        self, context: AnalysisContext, config: JsonSchemaConsistencyConfig
    ) -> list[Violation]:
        """Parse the JSON document and compare key sets across array elements.

        Args:
            context: Analysis context holding the raw JSON text.
            config: Schema consistency thresholds and violation message templates.

        Returns:
            list[Violation]: A single violation when objects in an array have divergent key sets.
        """
        try:
            data = json.loads(context.code)
        except Exception:
            return []
        if not isinstance(data, list) or len(data) < 2:
            return []
        if not all(isinstance(item, dict) for item in data):
            return []
        key_sets = [frozenset(item.keys()) for item in data]
        if len(set(key_sets)) > 1:
            return [
                self.build_violation(
                    config,
                    contains="schema",
                    location=Location(line=1, column=1),
                    suggestion="Ensure objects in arrays share a consistent schema.",
                )
            ]
        return []


class JsonDateFormatDetector(
    ViolationDetector[JsonDateFormatConfig], LocationHelperMixin
):
    """Identifies date strings that deviate from ISO 8601 formatting.

    JSON has no native date type, so dates are encoded as strings.  Using
    locale-dependent formats like ``MM/DD/YYYY`` creates ambiguity (is
    ``01/02/2024`` January 2nd or February 1st?).  This detector flags such
    patterns and recommends ISO 8601 (``YYYY-MM-DD`` or ``YYYY-MM-DDTHH:MM:SSZ``)
    for unambiguous, sortable date representation.
    """

    @property
    def name(self) -> str:
        """Return ``'json-003'`` identifying the JSON date format detector.

        Returns:
            str: The ``'json-003'`` rule identifier.
        """
        return "json-003"

    def detect(
        self, context: AnalysisContext, config: JsonDateFormatConfig
    ) -> list[Violation]:
        """Search for non-ISO date patterns such as ``MM/DD/YYYY`` in string values.

        Args:
            context: Analysis context holding the raw JSON text.
            config: Date format thresholds and violation message templates.

        Returns:
            list[Violation]: Violations for the first non-ISO date occurrence found.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if re.search(r"\d{2}/\d{2}/\d{4}", line):
                violations.append(
                    self.build_violation(
                        config,
                        contains="date",
                        location=Location(line=idx, column=1),
                        suggestion="Use ISO 8601 date strings.",
                    )
                )
                break
        for idx, line in enumerate(context.code.splitlines(), start=1):
            match = re.search(r"\"([^\"]+)\"", line)
            if not match:
                continue
            value = match.group(1)
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}Z?)?", value):
                continue
            if re.search(r"\d{2}/\d{2}/\d{4}", value):
                violations.append(
                    self.build_violation(
                        config,
                        contains=value,
                        location=Location(line=idx, column=1),
                        suggestion="Use ISO 8601 date strings.",
                    )
                )
                break
        return violations


class JsonNullHandlingDetector(
    ViolationDetector[JsonNullHandlingConfig], LocationHelperMixin
):
    """Reports top-level object keys whose values are explicitly ``null``.

    Explicit ``null`` values in JSON can signal intentional absence or simply
    uninitialized data.  When keys are optional, omitting them entirely is
    often cleaner than including ``null``, which forces consumers to handle an
    extra sentinel.  This detector highlights ``null`` usage so authors can
    decide whether each case is intentional or accidental.
    """

    @property
    def name(self) -> str:
        """Return ``'json-004'`` identifying the JSON null handling detector.

        Returns:
            str: The ``'json-004'`` rule identifier.
        """
        return "json-004"

    def detect(
        self, context: AnalysisContext, config: JsonNullHandlingConfig
    ) -> list[Violation]:
        """Parse JSON and check whether any top-level values are ``None``.

        Args:
            context: Analysis context holding the raw JSON text.
            config: Null-handling thresholds and violation message templates.

        Returns:
            list[Violation]: A single violation when at least one ``null`` value exists.
        """
        try:
            data = json.loads(context.code)
        except Exception:
            return []
        if not isinstance(data, dict):
            return []
        if any(value is None for value in data.values()):
            return [
                self.build_violation(
                    config,
                    contains="null",
                    location=Location(line=1, column=1),
                    suggestion="Use explicit nulls for optional keys when needed.",
                )
            ]
        return []


class JsonKeyCasingDetector(
    ViolationDetector[JsonKeyCasingConfig], LocationHelperMixin
):
    """Enforces consistent letter casing across all keys in a JSON object.

    Mixing ``camelCase``, ``snake_case``, and ``PascalCase`` keys within the
    same object makes the document harder to navigate and increases the chance
    of typos in consuming code.  This detector classifies each key as
    upper-containing or all-lowercase and flags the document when both styles
    coexist.
    """

    @property
    def name(self) -> str:
        """Return ``'json-005'`` identifying the JSON key casing detector.

        Returns:
            str: The ``'json-005'`` rule identifier.
        """
        return "json-005"

    def detect(
        self, context: AnalysisContext, config: JsonKeyCasingConfig
    ) -> list[Violation]:
        """Parse the JSON object and compare casing styles of its keys.

        Args:
            context: Analysis context holding the raw JSON text.
            config: Key casing thresholds and violation message templates.

        Returns:
            list[Violation]: A single violation when mixed casing styles are detected.
        """
        try:
            data = json.loads(context.code)
        except Exception:
            return []
        if not isinstance(data, dict):
            return []
        keys = list(data.keys())
        casing = [
            "upper" if any(ch.isupper() for ch in key) else "lower" for key in keys
        ]
        if len(set(casing)) > 1:
            return [
                self.build_violation(
                    config,
                    contains="casing",
                    location=Location(line=1, column=1),
                    suggestion="Use consistent casing for JSON keys.",
                )
            ]
        return []


class JsonArrayOrderDetector(
    ViolationDetector[JsonArrayOrderConfig], LocationHelperMixin
):
    """Checks for ordered collections and duplicate keys that hint at misused objects.

    JSON objects are unordered by specification, so relying on key insertion
    order is fragile.  When data naturally forms an ordered sequence—or when
    duplicate keys appear in an object—an array is a more appropriate
    structure.  This detector surfaces both nested arrays and duplicate-key
    objects to encourage intentional collection design.
    """

    @property
    def name(self) -> str:
        """Return ``'json-006'`` identifying the JSON array order detector.

        Returns:
            str: The ``'json-006'`` rule identifier.
        """
        return "json-006"

    def detect(
        self, context: AnalysisContext, config: JsonArrayOrderConfig
    ) -> list[Violation]:
        """Parse JSON and flag nested arrays or duplicate keys signalling order dependence.

        Args:
            context: Analysis context holding the raw JSON text.
            config: Array order thresholds and violation message templates.

        Returns:
            list[Violation]: A single violation when arrays or duplicate keys are found.
        """

        def contains_list(value: object) -> bool:
            """Recursively check whether *value* contains a list at any depth.

            Args:
                value: A parsed JSON fragment (dict, list, or scalar).

            Returns:
                bool: ``True`` when a list is found anywhere within *value*.
            """
            if isinstance(value, list):
                return True
            if isinstance(value, dict):
                return any(contains_list(item) for item in value.values())
            return False

        try:
            data = json.loads(context.code)
        except Exception:
            return []
        if contains_list(data):
            return [
                self.build_violation(
                    config,
                    contains="array",
                    location=Location(line=1, column=1),
                    suggestion="Use arrays for ordered collections.",
                )
            ]
        if isinstance(data, dict):
            duplicates = [k for k, v in Counter(data.keys()).items() if v > 1]
            if duplicates:
                return [
                    self.build_violation(
                        config,
                        contains=duplicates[0],
                        location=Location(line=1, column=1),
                        suggestion="Use arrays for ordered collections.",
                    )
                ]
        return []


__all__ = [
    "JsonStrictnessDetector",
    "JsonSchemaConsistencyDetector",
    "JsonDateFormatDetector",
    "JsonNullHandlingDetector",
    "JsonKeyCasingDetector",
    "JsonArrayOrderDetector",
]
