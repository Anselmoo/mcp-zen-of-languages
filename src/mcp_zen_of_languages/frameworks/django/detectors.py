"""Rule-aware detectors for Django framework guidance."""

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


class DjangoRuleDetector(FrameworkRuleDetectorBase):
    """Framework-specific detector with Django-aware heuristics."""

    def _rule_handlers(
        self,
    ) -> dict[str, Callable[[AnalysisContext, DetectorConfig], list[Violation]]]:
        return {
            "django-001": self._detect_interpolated_raw_sql,
            "django-002": self._detect_hardcoded_secrets,
            "django-003": self._detect_debug_true,
            "django-004": self._detect_hardcoded_redirects,
            "django-005": self._detect_signals,
            "django-006": self._detect_queryset_loops_without_related_loading,
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

    def _detect_interpolated_raw_sql(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r"cursor\.execute\(\s*(?:f[\"']|[rubf]*[\"'][^\"']*%\w*[\"']\s*%|\w+\s*\+)",
            contains="cursor.execute",
        )

    def _detect_hardcoded_secrets(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r"^\s*(?:SECRET_KEY|DATABASE_URL)\s*=\s*[\"']",
            contains="SECRET_KEY",
        )

    def _detect_debug_true(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r"^\s*DEBUG\s*=\s*True\b",
            contains="DEBUG = True",
        )

    def _detect_hardcoded_redirects(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r"\b(?:redirect|HttpResponseRedirect)\(\s*[\"']/",
            contains="redirect(",
        )

    def _detect_signals(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r"\b(?:post_save|pre_save|post_delete|m2m_changed)\.connect\(",
            contains=".connect(",
        )

    def _detect_queryset_loops_without_related_loading(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        code = _mask_comments(context.code)
        pattern = re.compile(
            r"for\s+\w+\s+in\s+\w+\.objects\.(?!select_related|prefetch_related)"
            r"(?:all|filter)\(",
            re.MULTILINE,
        )
        return [
            self.build_violation(
                config,
                contains="select_related",
                location=_location_for_offset(code, match.start()),
                suggestion=config.recommended_alternative,
            )
            for match in pattern.finditer(code)
        ]


class _BoundDjangoDetector(DjangoRuleDetector):
    """Base class for rule-bound django detectors."""

    _handler_name: str

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        """Run the bound django detector handler."""
        handler = getattr(self, self._handler_name)
        return handler(context, config)


class DjangoDebugConfigDetector(_BoundDjangoDetector):
    """Concrete detector binding for DjangoDebugConfigDetector."""

    _handler_name = "_detect_debug_true"


class DjangoParameterizedSqlDetector(_BoundDjangoDetector):
    """Concrete detector binding for DjangoParameterizedSqlDetector."""

    _handler_name = "_detect_interpolated_raw_sql"


class DjangoQuerysetLoadingDetector(_BoundDjangoDetector):
    """Concrete detector binding for DjangoQuerysetLoadingDetector."""

    _handler_name = "_detect_queryset_loops_without_related_loading"


class DjangoReverseUrlDetector(_BoundDjangoDetector):
    """Concrete detector binding for DjangoReverseUrlDetector."""

    _handler_name = "_detect_hardcoded_redirects"


class DjangoSecretSettingsDetector(_BoundDjangoDetector):
    """Concrete detector binding for DjangoSecretSettingsDetector."""

    _handler_name = "_detect_hardcoded_secrets"


class DjangoSignalHookDetector(_BoundDjangoDetector):
    """Concrete detector binding for DjangoSignalHookDetector."""

    _handler_name = "_detect_signals"


__all__ = [
    "DjangoDebugConfigDetector",
    "DjangoParameterizedSqlDetector",
    "DjangoQuerysetLoadingDetector",
    "DjangoReverseUrlDetector",
    "DjangoSecretSettingsDetector",
    "DjangoSignalHookDetector",
]
