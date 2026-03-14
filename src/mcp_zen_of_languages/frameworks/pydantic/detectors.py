"""Rule-aware detectors for Pydantic framework guidance."""

from __future__ import annotations

import io
import re
import tokenize

from typing import TYPE_CHECKING

from mcp_zen_of_languages.frameworks.detector_base import FrameworkRuleDetectorBase
from mcp_zen_of_languages.models import Location


if TYPE_CHECKING:
    from collections.abc import Callable

    from mcp_zen_of_languages.analyzers.base import AnalysisContext
    from mcp_zen_of_languages.languages.configs import DetectorConfig
    from mcp_zen_of_languages.models import Violation


def _mask_comments(code: str) -> str:
    """Replace comment spans with spaces while preserving offsets."""
    lines = code.splitlines(keepends=True)
    try:
        tokens = tokenize.generate_tokens(io.StringIO(code).readline)
        for token in tokens:
            if token.type != tokenize.COMMENT:
                continue
            start_line, start_column = token.start
            end_line, end_column = token.end
            if start_line != end_line:
                continue
            line = lines[start_line - 1]
            lines[start_line - 1] = (
                line[:start_column]
                + (" " * (end_column - start_column))
                + line[end_column:]
            )
    except tokenize.TokenError:
        return code
    return "".join(lines)


def _location_for_offset(code: str, offset: int) -> Location:
    """Convert an absolute character offset into a source location."""
    line = code.count("\n", 0, offset) + 1
    last_newline = code.rfind("\n", 0, offset)
    column = offset + 1 if last_newline == -1 else offset - last_newline
    return Location(line=line, column=column)


class PydanticRuleDetector(FrameworkRuleDetectorBase):
    """Framework-specific detector with Pydantic-aware heuristics."""

    def _rule_handlers(
        self,
    ) -> dict[str, Callable[[AnalysisContext, DetectorConfig], list[Violation]]]:
        return {
            "pydantic-001": self._detect_v1_serialization,
            "pydantic-002": self._detect_v1_validation,
            "pydantic-003": self._detect_mutable_defaults,
            "pydantic-004": self._detect_nested_config,
            "pydantic-005": self._detect_legacy_validator,
            "pydantic-006": self._detect_legacy_fields_attribute,
            "pydantic-007": self._detect_optional_annotations,
            "pydantic-008": self._detect_orm_mode,
        }

    def _match_pattern(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
        pattern: str,
        *,
        contains: str,
    ) -> list[Violation]:
        code = _mask_comments(context.code)
        return [
            self.build_violation(
                config,
                contains=contains,
                location=_location_for_offset(code, match.start()),
                suggestion=config.recommended_alternative,
            )
            for match in re.finditer(pattern, code, re.MULTILINE | re.DOTALL)
        ]

    def _detect_v1_serialization(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r"\.(?:dict|json)\(",
            contains=".dict(",
        )

    def _detect_v1_validation(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r"\b(?:parse_obj|parse_raw|from_orm)\(",
            contains="parse_obj",
        )

    def _detect_mutable_defaults(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r":\s*(?:list|dict|set)\b[^\n=]*=\s*(?:\[\]|\{\}|set\(\))",
            contains="default_factory",
        )

    def _detect_nested_config(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r"^\s+class\s+Config\s*:",
            contains="class Config",
        )

    def _detect_legacy_validator(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r"@validator\b",
            contains="@validator",
        )

    def _detect_legacy_fields_attribute(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r"\.__fields__\b",
            contains="__fields__",
        )

    def _detect_optional_annotations(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r"\bOptional\[",
            contains="Optional[",
        )

    def _detect_orm_mode(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r"\borm_mode\s*=\s*True\b",
            contains="orm_mode",
        )


class _BoundPydanticDetector(PydanticRuleDetector):
    """Base class for rule-bound pydantic detectors."""

    _handler_name: str

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        """Run the bound pydantic detector handler."""
        handler = getattr(self, self._handler_name)
        return handler(context, config)


class PydanticDefaultFactoryDetector(_BoundPydanticDetector):
    """Concrete detector binding for PydanticDefaultFactoryDetector."""

    _handler_name = "_detect_mutable_defaults"


class PydanticFieldValidatorDetector(_BoundPydanticDetector):
    """Concrete detector binding for PydanticFieldValidatorDetector."""

    _handler_name = "_detect_legacy_validator"


class PydanticFromAttributesDetector(_BoundPydanticDetector):
    """Concrete detector binding for PydanticFromAttributesDetector."""

    _handler_name = "_detect_orm_mode"


class PydanticModelConfigDetector(_BoundPydanticDetector):
    """Concrete detector binding for PydanticModelConfigDetector."""

    _handler_name = "_detect_nested_config"


class PydanticModelDumpDetector(_BoundPydanticDetector):
    """Concrete detector binding for PydanticModelDumpDetector."""

    _handler_name = "_detect_v1_serialization"


class PydanticModelFieldsDetector(_BoundPydanticDetector):
    """Concrete detector binding for PydanticModelFieldsDetector."""

    _handler_name = "_detect_legacy_fields_attribute"


class PydanticModelValidateDetector(_BoundPydanticDetector):
    """Concrete detector binding for PydanticModelValidateDetector."""

    _handler_name = "_detect_v1_validation"


class PydanticModernTypingDetector(_BoundPydanticDetector):
    """Concrete detector binding for PydanticModernTypingDetector."""

    _handler_name = "_detect_optional_annotations"


__all__ = [
    "PydanticDefaultFactoryDetector",
    "PydanticFieldValidatorDetector",
    "PydanticFromAttributesDetector",
    "PydanticModelConfigDetector",
    "PydanticModelDumpDetector",
    "PydanticModelFieldsDetector",
    "PydanticModelValidateDetector",
    "PydanticModernTypingDetector",
]
