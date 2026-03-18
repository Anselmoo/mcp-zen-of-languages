"""Rule-aware detectors for SQLAlchemy framework guidance."""

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


class SqlalchemyRuleDetector(FrameworkRuleDetectorBase):
    """Framework-specific detector with SQLAlchemy-aware heuristics."""

    def _rule_handlers(
        self,
    ) -> dict[str, Callable[[AnalysisContext, DetectorConfig], list[Violation]]]:
        return {
            "sqlalchemy-001": self._detect_interpolated_text_queries,
            "sqlalchemy-002": self._detect_ad_hoc_sessions,
            "sqlalchemy-003": self._detect_legacy_column_api,
            "sqlalchemy-004": self._detect_legacy_declarative_base,
            "sqlalchemy-005": self._detect_relationship_without_loading_strategy,
            "sqlalchemy-006": self._detect_session_add_in_loops,
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

    def _detect_interpolated_text_queries(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r"text\(\s*(?:f[\"']|[rubf]*[\"'][^\"']*%\w*[\"']\s*%|[\"'][^\"']*[\"']\s*\+)",
            contains="text(",
        )

    def _detect_ad_hoc_sessions(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        code = _mask_comments(context.code)
        pattern = re.compile(r"^(?!\s*with\b).*?\bSession\(\)", re.MULTILINE)
        return [
            self.build_violation(
                config,
                contains="Session()",
                location=_location_for_offset(code, match.start()),
                suggestion=config.recommended_alternative,
            )
            for match in pattern.finditer(code)
        ]

    def _detect_legacy_column_api(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r"\bColumn\(",
            contains="Column(",
        )

    def _detect_legacy_declarative_base(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r"\bdeclarative_base\(",
            contains="declarative_base(",
        )

    def _detect_relationship_without_loading_strategy(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        code = _mask_comments(context.code)
        pattern = re.compile(r"relationship\((?:(?!lazy=)[\s\S])*?\)", re.MULTILINE)
        return [
            self.build_violation(
                config,
                contains="relationship(",
                location=_location_for_offset(code, match.start()),
                suggestion=config.recommended_alternative,
            )
            for match in pattern.finditer(code)
        ]

    def _detect_session_add_in_loops(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self._match_pattern(
            context,
            config,
            r"for\s+.+:\s*[\s\S]*?session\.add\(",
            contains="session.add(",
        )


class _BoundSqlalchemyDetector(SqlalchemyRuleDetector):
    """Base class for rule-bound sqlalchemy detectors."""

    _handler_name: str

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        """Run the bound sqlalchemy detector handler."""
        handler = getattr(self, self._handler_name)
        return handler(context, config)


class SqlalchemyBulkInsertDetector(_BoundSqlalchemyDetector):
    """Concrete detector binding for SqlalchemyBulkInsertDetector."""

    _handler_name = "_detect_session_add_in_loops"


class SqlalchemyDeclarativeBaseDetector(_BoundSqlalchemyDetector):
    """Concrete detector binding for SqlalchemyDeclarativeBaseDetector."""

    _handler_name = "_detect_legacy_declarative_base"


class SqlalchemyMappedColumnDetector(_BoundSqlalchemyDetector):
    """Concrete detector binding for SqlalchemyMappedColumnDetector."""

    _handler_name = "_detect_legacy_column_api"


class SqlalchemyParameterizedTextDetector(_BoundSqlalchemyDetector):
    """Concrete detector binding for SqlalchemyParameterizedTextDetector."""

    _handler_name = "_detect_interpolated_text_queries"


class SqlalchemyRelationshipLoadingDetector(_BoundSqlalchemyDetector):
    """Concrete detector binding for SqlalchemyRelationshipLoadingDetector."""

    _handler_name = "_detect_relationship_without_loading_strategy"


class SqlalchemySessionScopeDetector(_BoundSqlalchemyDetector):
    """Concrete detector binding for SqlalchemySessionScopeDetector."""

    _handler_name = "_detect_ad_hoc_sessions"


__all__ = [
    "SqlalchemyBulkInsertDetector",
    "SqlalchemyDeclarativeBaseDetector",
    "SqlalchemyMappedColumnDetector",
    "SqlalchemyParameterizedTextDetector",
    "SqlalchemyRelationshipLoadingDetector",
    "SqlalchemySessionScopeDetector",
]
