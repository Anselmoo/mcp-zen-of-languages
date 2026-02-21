"""Detectors for SQL query correctness, security, and maintainability."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import sqlglot
from sqlglot import exp

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import (
    SqlAliasClarityConfig,
    SqlAnsi89JoinConfig,
    SqlDynamicSqlConfig,
    SqlImplicitJoinCoercionConfig,
    SqlInsertColumnListConfig,
    SqlNolockConfig,
    SqlSelectStarConfig,
    SqlTransactionBoundaryConfig,
    SqlUnboundedQueryConfig,
)

if TYPE_CHECKING:
    from mcp_zen_of_languages.models import Violation


def _parse_statements(code: str, dialect: str) -> list[exp.Expression]:
    """Parse SQL statements with a best-effort fallback for invalid SQL."""
    try:
        statements = sqlglot.parse(code, read=dialect)
        return [statement for statement in statements if statement is not None]
    except (sqlglot.errors.ParseError, ValueError):
        return []


class SqlSelectStarDetector(
    ViolationDetector[SqlSelectStarConfig],
    LocationHelperMixin,
):
    """Flag ``SELECT *`` usage."""

    @property
    def name(self) -> str:
        """Return detector identifier."""
        return "sql-001"

    def detect(self, context: AnalysisContext, config: SqlSelectStarConfig) -> list[Violation]:
        """Detect star projections in select statements."""
        statements = _parse_statements(context.code, config.dialect)
        for statement in statements:
            for select in statement.find_all(exp.Select):
                if any(expr.find(exp.Star) for expr in select.expressions):
                    return [
                        self.build_violation(
                            config,
                            location=self.find_location_by_substring(context.code, "SELECT *"),
                            suggestion="List explicit columns instead of using SELECT *.",
                        ),
                    ]
        if re.search(r"(?i)select\s+\*\s+from", context.code):
            return [
                self.build_violation(
                    config,
                    location=self.find_location_by_substring(context.code, "SELECT"),
                    suggestion="List explicit columns instead of using SELECT *.",
                ),
            ]
        return []


class SqlInsertColumnListDetector(
    ViolationDetector[SqlInsertColumnListConfig],
    LocationHelperMixin,
):
    """Flag INSERT statements that omit explicit target columns."""

    @property
    def name(self) -> str:
        """Return detector identifier."""
        return "sql-002"

    def detect(
        self,
        context: AnalysisContext,
        config: SqlInsertColumnListConfig,
    ) -> list[Violation]:
        """Detect ``INSERT INTO table VALUES (...)`` patterns."""
        if match := re.search(
            r"(?i)\binsert\s+into\s+[^\s(]+\s+values\s*\(",
            context.code,
        ):
            return [
                self.build_violation(
                    config,
                    location=self.find_location_by_substring(context.code, match.group(0)),
                    suggestion="Specify INSERT column names explicitly before VALUES.",
                ),
            ]
        return []


class SqlDynamicSqlDetector(
    ViolationDetector[SqlDynamicSqlConfig],
    LocationHelperMixin,
):
    """Flag risky dynamic SQL execution via string concatenation."""

    @property
    def name(self) -> str:
        """Return detector identifier."""
        return "sql-003"

    def detect(self, context: AnalysisContext, config: SqlDynamicSqlConfig) -> list[Violation]:
        """Detect EXEC/EXECUTE patterns that concatenate SQL fragments."""
        pattern = r"(?is)\bexec(?:ute)?\b[^;\n]*(?:\+|\|\||concat\s*\()"
        if match := re.search(pattern, context.code):
            return [
                self.build_violation(
                    config,
                    location=self.find_location_by_substring(context.code, match.group(0)),
                    suggestion="Use bind parameters and prepared statements.",
                ),
            ]
        return []


class SqlNolockDetector(
    ViolationDetector[SqlNolockConfig],
    LocationHelperMixin,
):
    """Flag NOLOCK table-hint usage."""

    @property
    def name(self) -> str:
        """Return detector identifier."""
        return "sql-004"

    def detect(self, context: AnalysisContext, config: SqlNolockConfig) -> list[Violation]:
        """Detect ``WITH (NOLOCK)`` occurrences."""
        if re.search(r"(?i)with\s*\(\s*nolock\s*\)", context.code):
            return [
                self.build_violation(
                    config,
                    location=self.find_location_by_substring(context.code, "NOLOCK"),
                    suggestion="Remove NOLOCK and use an appropriate transaction isolation level.",
                ),
            ]
        return []


class SqlImplicitJoinCoercionDetector(
    ViolationDetector[SqlImplicitJoinCoercionConfig],
    LocationHelperMixin,
):
    """Detect join predicates that cast either side of the comparison."""

    @property
    def name(self) -> str:
        """Return detector identifier."""
        return "sql-005"

    def detect(
        self,
        context: AnalysisContext,
        config: SqlImplicitJoinCoercionConfig,
    ) -> list[Violation]:
        """Detect CAST/CONVERT usage inside JOIN ON clauses."""
        pattern = r"(?is)\bjoin\b[\s\S]*?\bon\b[\s\S]*?(cast\s*\(|convert\s*\()"
        if match := re.search(pattern, context.code):
            return [
                self.build_violation(
                    config,
                    location=self.find_location_by_substring(context.code, match.group(1)),
                    suggestion="Align join key data types and avoid casting in JOIN predicates.",
                ),
            ]
        return []


class SqlUnboundedQueryDetector(
    ViolationDetector[SqlUnboundedQueryConfig],
    LocationHelperMixin,
):
    """Warn on unbounded SELECT queries."""

    @property
    def name(self) -> str:
        """Return detector identifier."""
        return "sql-006"

    def detect(
        self,
        context: AnalysisContext,
        config: SqlUnboundedQueryConfig,
    ) -> list[Violation]:
        """Detect SELECT statements missing WHERE/LIMIT/TOP restrictions."""
        statements = _parse_statements(context.code, config.dialect)
        for statement in statements:
            for select in statement.find_all(exp.Select):
                has_where = select.args.get("where") is not None
                has_limit = select.args.get("limit") is not None
                has_top = select.args.get("limit_options") is not None
                if select.args.get("from") is not None and not (has_where or has_limit or has_top):
                    return [
                        self.build_violation(
                            config,
                            location=self.find_location_by_substring(context.code, "SELECT"),
                            suggestion="Add WHERE, LIMIT, or TOP clauses to bound result size.",
                        ),
                    ]
        pattern = r"(?is)\bselect\b(?![^;]*\b(top\s+\d+)\b)[^;]*\bfrom\b[^;]*(?!(?:[^;]*\b(where|limit)\b))"
        if re.search(pattern, context.code):
            return [
                self.build_violation(
                    config,
                    location=self.find_location_by_substring(context.code, "SELECT"),
                    suggestion="Add WHERE, LIMIT, or TOP clauses to bound result size.",
                ),
            ]
        return []


class SqlAliasClarityDetector(
    ViolationDetector[SqlAliasClarityConfig],
    LocationHelperMixin,
):
    """Flag aliases that are shorter than configured readability threshold."""

    @property
    def name(self) -> str:
        """Return detector identifier."""
        return "sql-007"

    def detect(self, context: AnalysisContext, config: SqlAliasClarityConfig) -> list[Violation]:
        """Detect overly short aliases in FROM/JOIN clauses."""
        pattern = r"(?i)\b(?:from|join)\s+[\w.\[\]\"`]+\s+(?:as\s+)?([a-z][a-z0-9_]*)"
        for match in re.finditer(pattern, context.code):
            alias = match.group(1)
            if len(alias) < config.min_alias_length:
                return [
                    self.build_violation(
                        config,
                        location=self.find_location_by_substring(context.code, alias),
                        suggestion="Use descriptive table aliases (for example, ord, order_items).",
                    ),
                ]
        return []


class SqlTransactionBoundaryDetector(
    ViolationDetector[SqlTransactionBoundaryConfig],
    LocationHelperMixin,
):
    """Ensure explicit transaction blocks are balanced."""

    @property
    def name(self) -> str:
        """Return detector identifier."""
        return "sql-008"

    def detect(
        self,
        context: AnalysisContext,
        config: SqlTransactionBoundaryConfig,
    ) -> list[Violation]:
        """Detect unmatched transaction beginnings."""
        begins = re.findall(r"(?i)\bbegin\s+tran(?:saction)?\b", context.code)
        ends = re.findall(r"(?i)\b(?:commit|rollback)\b", context.code)
        if len(begins) > len(ends):
            return [
                self.build_violation(
                    config,
                    location=self.find_location_by_substring(context.code, "BEGIN"),
                    suggestion="Ensure each BEGIN TRANSACTION has COMMIT or ROLLBACK in the same file.",
                ),
            ]
        return []


class SqlAnsi89JoinDetector(
    ViolationDetector[SqlAnsi89JoinConfig],
    LocationHelperMixin,
):
    """Detect deprecated ANSI-89 comma-join syntax."""

    @property
    def name(self) -> str:
        """Return detector identifier."""
        return "sql-009"

    def detect(self, context: AnalysisContext, config: SqlAnsi89JoinConfig) -> list[Violation]:
        """Detect comma-separated FROM clauses combined with WHERE joins."""
        pattern = r"(?is)\bselect\b[^;]*\bfrom\b[^;]*,[^;]*\bwhere\b"
        if match := re.search(pattern, context.code):
            return [
                self.build_violation(
                    config,
                    location=self.find_location_by_substring(context.code, match.group(0)),
                    suggestion="Use explicit JOIN ... ON syntax instead of comma joins.",
                ),
            ]
        return []


__all__ = [
    "SqlAliasClarityDetector",
    "SqlAnsi89JoinDetector",
    "SqlDynamicSqlDetector",
    "SqlImplicitJoinCoercionDetector",
    "SqlInsertColumnListDetector",
    "SqlNolockDetector",
    "SqlSelectStarDetector",
    "SqlTransactionBoundaryDetector",
    "SqlUnboundedQueryDetector",
]
