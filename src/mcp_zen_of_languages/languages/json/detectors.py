"""Detectors for JSON/JSON5 structural and semantic quality checks."""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import (
    JsonArrayOrderConfig,
    JsonDateFormatConfig,
    JsonDuplicateKeyConfig,
    JsonKeyCasingConfig,
    JsonMagicStringConfig,
    JsonNullHandlingConfig,
    JsonNullSprawlConfig,
    JsonSchemaConsistencyConfig,
    JsonStrictnessConfig,
)
from mcp_zen_of_languages.models import Location, Violation


def _load_json_document(code: str) -> object | None:
    """Parse JSON text and return Python objects, or ``None`` when invalid."""
    try:
        return json.loads(code)
    except (json.JSONDecodeError, ValueError):
        return None


def _iter_values(value: object) -> Iterator[object]:
    """Yield every nested value in a parsed JSON document."""
    yield value
    if isinstance(value, dict):
        for item in value.values():
            yield from _iter_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_values(item)


def _json_key_style(key: str) -> str:
    """Return a coarse key-casing style label."""
    if key.islower() and "_" not in key:
        return "lowercase"
    if "_" in key and key.lower() == key:
        return "snake_case"
    if key and key[0].isupper() and "_" not in key:
        return "PascalCase"
    if key and key[0].islower() and any(ch.isupper() for ch in key) and "_" not in key:
        return "camelCase"
    return "other"


def _find_mixed_key(node: object) -> str | None:
    """Find the first key in a dict level that mixes casing conventions."""
    if isinstance(node, dict):
        styles = {
            _json_key_style(key) for key in node if _json_key_style(key) != "other"
        }
        if len(styles) > 1:
            return next((key for key in node if isinstance(key, str)), None)
        for value in node.values():
            mixed = _find_mixed_key(value)
            if mixed:
                return mixed
    elif isinstance(node, list):
        for value in node:
            mixed = _find_mixed_key(value)
            if mixed:
                return mixed
    return None


class JsonStrictnessDetector(
    ViolationDetector[JsonStrictnessConfig],
    LocationHelperMixin,
):
    """Flag trailing commas when strict JSON output is expected."""

    @property
    def name(self) -> str:
        """Return the detector identifier."""
        return "json-001"

    def detect(
        self,
        context: AnalysisContext,
        config: JsonStrictnessConfig,
    ) -> list[Violation]:
        """Detect strict-mode trailing comma violations."""
        if config.target_format == "json5" or config.allow_trailing_commas:
            return []
        match = re.search(r",\s*[\]}]", context.code)
        if match:
            line = context.code.count("\n", 0, match.start()) + 1
            return [
                self.build_violation(
                    config,
                    contains="Trailing",
                    location=Location(line=line, column=1),
                    suggestion="Remove trailing commas or set target_format=json5.",
                ),
            ]
        return []


class JsonSchemaConsistencyDetector(
    ViolationDetector[JsonSchemaConsistencyConfig],
    LocationHelperMixin,
):
    """Detect excessive JSON nesting depth."""

    @property
    def name(self) -> str:
        """Return the detector identifier."""
        return "json-002"

    def detect(
        self,
        context: AnalysisContext,
        config: JsonSchemaConsistencyConfig,
    ) -> list[Violation]:
        """Detect deep nesting beyond the configured threshold."""
        data = _load_json_document(context.code)
        if data is None:
            return []

        def max_depth(node: object, depth: int = 1) -> int:
            if isinstance(node, dict):
                if not node:
                    return depth
                return max(max_depth(value, depth + 1) for value in node.values())
            if isinstance(node, list):
                if not node:
                    return depth
                return max(max_depth(value, depth + 1) for value in node)
            return depth

        depth = max_depth(data)
        if depth > config.max_depth:
            return [
                self.build_violation(
                    config,
                    location=Location(line=1, column=1),
                    suggestion=f"Reduce nesting depth to {config.max_depth} or below.",
                ),
            ]
        return []


class JsonDuplicateKeyDetector(
    ViolationDetector[JsonDuplicateKeyConfig],
    LocationHelperMixin,
):
    """Detect duplicate keys in JSON objects.

    Duplicate object keys silently override earlier values in most parsers,
    leading to hard-to-diagnose bugs. This detector uses a parse-time
    ``object_pairs_hook`` to catch duplicates before they are lost.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier."""
        return "json-003"

    def detect(
        self,
        context: AnalysisContext,
        config: JsonDuplicateKeyConfig,
    ) -> list[Violation]:
        """Detect duplicate keys while preserving parse-time key order."""
        duplicates: list[str] = []

        def track_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
            seen: set[str] = set()
            obj: dict[str, object] = {}
            for key, value in pairs:
                if key in seen and key not in duplicates:
                    duplicates.append(key)
                seen.add(key)
                obj[key] = value
            return obj

        try:
            json.loads(context.code, object_pairs_hook=track_duplicates)
        except (json.JSONDecodeError, ValueError):
            return []
        if duplicates:
            duplicate_key = duplicates[0]
            return [
                self.build_violation(
                    config,
                    location=self.find_location_by_substring(
                        context.code,
                        f'"{duplicate_key}"',
                    ),
                    suggestion="Keep object keys unique to avoid silent overrides.",
                ),
            ]
        return []


class JsonMagicStringDetector(
    ViolationDetector[JsonMagicStringConfig],
    LocationHelperMixin,
):
    """Detect repeated magic-string values.

    Repeated literal strings scattered across a JSON file make maintenance
    hazardous — updating one instance while missing others leads to
    inconsistency. This detector flags string values that appear at least
    ``min_repetition`` times and are at least ``min_length`` characters
    long (ignoring semver-like strings such as ``^1.2.3``).
    """

    @property
    def name(self) -> str:
        """Return the detector identifier."""
        return "json-004"

    def detect(
        self,
        context: AnalysisContext,
        config: JsonMagicStringConfig,
    ) -> list[Violation]:
        """Detect repeated literal strings that behave like magic constants."""
        data = _load_json_document(context.code)
        if data is None:
            return []
        values = [
            value
            for value in _iter_values(data)
            if isinstance(value, str)
            and len(value) >= config.min_length
            and not re.fullmatch(r"[\^~]?\d+\.\d+\.\d+.*", value)
        ]
        if not values:
            return []
        repeated = [
            value
            for value, count in Counter(values).items()
            if count >= config.min_repetition
        ]
        if repeated:
            repeated_value = repeated[0]
            return [
                self.build_violation(
                    config,
                    location=self.find_location_by_substring(
                        context.code,
                        f'"{repeated_value}"',
                    ),
                    suggestion=(
                        "Extract repeated string values into shared "
                        "constants or $ref anchors."
                    ),
                ),
            ]
        return []


# ISO 8601 full datetime or date-only (YYYY-MM-DD)
_ISO_DATE_RE = re.compile(
    r"^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])"
    r"(?:T(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?"
    r"(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d))?$"
)
# Locale-style dates: MM/DD/YYYY, DD.MM.YYYY, DD-MM-YYYY (NOT ISO)
_NON_ISO_DATE_RE = re.compile(
    r"^(?:\d{1,2}[/.]\d{1,2}[/.](\d{2}|\d{4})"
    r"|\d{4}[/.]\d{1,2}[/.]\d{1,2})$"
)


def _iter_pairs(value: object) -> Iterator[tuple[str, str]]:
    """Yield (key, string_value) pairs recursively from a parsed JSON document."""
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(k, str) and isinstance(v, str):
                yield k, v
            else:
                yield from _iter_pairs(v)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_pairs(item)


class JsonDateFormatDetector(
    ViolationDetector[JsonDateFormatConfig],
    LocationHelperMixin,
):
    """Identify date strings that deviate from ISO 8601 formatting.

    JSON has no native date type, so dates are encoded as strings. Using
    locale-dependent formats like ``MM/DD/YYYY`` creates ambiguity (is
    ``02/03/2024`` the 2nd of March or the 3rd of February?). Prefer
    ``YYYY-MM-DD`` or the full ``YYYY-MM-DDTHH:MM:SSZ`` for unambiguous,
    sortable date representation.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier."""
        return "json-008"

    def detect(
        self,
        context: AnalysisContext,
        config: JsonDateFormatConfig,
    ) -> list[Violation]:
        """Detect string values that look like dates but are not ISO 8601."""
        data = _load_json_document(context.code)
        if data is None:
            return []
        key_fragments = [kf.lower() for kf in config.common_date_keys]
        for key, value in _iter_pairs(data):
            key_lower = key.lower()
            is_date_key = any(frag in key_lower for frag in key_fragments)
            is_non_iso = bool(_NON_ISO_DATE_RE.fullmatch(value))
            is_iso = bool(_ISO_DATE_RE.fullmatch(value))
            # Flag explicit non-ISO dates and date-keyed fields that are not ISO.
            if is_non_iso or (is_date_key and value and not is_iso):
                return [
                    self.build_violation(
                        config,
                        location=self.find_location_by_substring(
                            context.code,
                            f'"{value}"',
                        ),
                        suggestion=(
                            "Use ISO 8601 format (YYYY-MM-DD or "
                            "YYYY-MM-DDTHH:MM:SSZ) for date strings."
                        ),
                    ),
                ]
        return []


class JsonNullHandlingDetector(
    ViolationDetector[JsonNullHandlingConfig],
    LocationHelperMixin,
):
    """Report top-level object keys whose values are explicitly ``null``.

    Explicit ``null`` values in JSON can signal intentional absence or simply
    forgotten clean-up. At the top level of a configuration document they
    almost always mean the key should be omitted rather than set to null.
    This detector flags documents where more than ``max_top_level_nulls``
    top-level keys carry a null value.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier."""
        return "json-009"

    def detect(
        self,
        context: AnalysisContext,
        config: JsonNullHandlingConfig,
    ) -> list[Violation]:
        """Detect top-level object keys explicitly set to null."""
        data = _load_json_document(context.code)
        if not isinstance(data, dict):
            return []
        null_keys = [k for k, v in data.items() if v is None]
        if len(null_keys) > config.max_top_level_nulls:
            first_null_key = null_keys[0]
            return [
                self.build_violation(
                    config,
                    location=self.find_location_by_substring(
                        context.code,
                        f'"{first_null_key}"',
                    ),
                    suggestion=(
                        "Omit top-level keys instead of setting them "
                        "explicitly to null."
                    ),
                ),
            ]
        return []


class JsonKeyCasingDetector(
    ViolationDetector[JsonKeyCasingConfig],
    LocationHelperMixin,
):
    """Detect mixed key casing at the same object level."""

    @property
    def name(self) -> str:
        """Return the detector identifier."""
        return "json-005"

    def detect(
        self,
        context: AnalysisContext,
        config: JsonKeyCasingConfig,
    ) -> list[Violation]:
        """Detect mixed key casing at the same object level."""
        data = _load_json_document(context.code)
        if data is None:
            return []
        mixed_key = _find_mixed_key(data)
        if mixed_key:
            return [
                self.build_violation(
                    config,
                    location=self.find_location_by_substring(
                        context.code, f'"{mixed_key}"'
                    ),
                    suggestion="Use one key naming convention per object level.",
                ),
            ]
        return []


class JsonArrayOrderDetector(
    ViolationDetector[JsonArrayOrderConfig],
    LocationHelperMixin,
):
    """Detect oversized inline arrays."""

    @property
    def name(self) -> str:
        """Return the detector identifier."""
        return "json-006"

    def detect(
        self,
        context: AnalysisContext,
        config: JsonArrayOrderConfig,
    ) -> list[Violation]:
        """Detect arrays that exceed the allowed inline size."""
        data = _load_json_document(context.code)
        if data is None:
            return []
        for node in _iter_values(data):
            if isinstance(node, list) and len(node) > config.max_inline_array_size:
                return [
                    self.build_violation(
                        config,
                        location=Location(line=1, column=1),
                        suggestion=(
                            "Move large arrays to separate files or reduce inline "
                            f"size to <= {config.max_inline_array_size}."
                        ),
                    ),
                ]
        return []


class JsonNullSprawlDetector(
    ViolationDetector[JsonNullSprawlConfig],
    LocationHelperMixin,
):
    """Detect excessive null values across JSON objects/arrays."""

    @property
    def name(self) -> str:
        """Return the detector identifier."""
        return "json-007"

    def detect(
        self,
        context: AnalysisContext,
        config: JsonNullSprawlConfig,
    ) -> list[Violation]:
        """Detect excessive use of null across a document."""
        data = _load_json_document(context.code)
        if data is None:
            return []
        null_count = sum(1 for value in _iter_values(data) if value is None)
        if null_count > config.max_null_values:
            return [
                self.build_violation(
                    config,
                    location=Location(line=1, column=1),
                    suggestion="Omit optional keys instead of spreading null values.",
                ),
            ]
        return []


__all__ = [
    "JsonArrayOrderDetector",
    "JsonDateFormatDetector",
    "JsonDuplicateKeyDetector",
    "JsonKeyCasingDetector",
    "JsonMagicStringDetector",
    "JsonNullHandlingDetector",
    "JsonNullSprawlDetector",
    "JsonSchemaConsistencyDetector",
    "JsonStrictnessDetector",
]
