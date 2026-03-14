"""SQLAlchemy zen principles."""

from __future__ import annotations

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
from mcp_zen_of_languages.rules.base_models import PrincipleCategory
from mcp_zen_of_languages.rules.base_models import ZenPrinciple


def _principle(  # noqa: PLR0913
    rule_id: str,
    principle: str,
    category: PrincipleCategory,
    severity: int,
    description: str,
    patterns: list[str],
    recommendation: str,
) -> ZenPrinciple:
    return ZenPrinciple(
        id=rule_id,
        principle=principle,
        category=category,
        severity=severity,
        description=description,
        violations=[principle],
        detectable_patterns=patterns,
        recommended_alternative=recommendation,
    )


SQLALCHEMY_ZEN = LanguageZenPrinciples(
    language="sqlalchemy",
    name="SQLAlchemy",
    philosophy="Explicit database access with disciplined session lifecycles and parameterized queries.",
    source_text="SQLAlchemy 2.0 documentation",
    source_url=HttpUrl("https://docs.sqlalchemy.org/en/20/"),
    principles=[
        _principle(
            rule_id="sqlalchemy-001",
            principle="text queries must not interpolate values directly",
            category=PrincipleCategory.SECURITY,
            severity=10,
            description="Interpolated SQL text bypasses SQLAlchemy's parameter handling and increases injection risk.",
            patterns=[
                "re:text\\(\\s*(?:f[\\\"\\']|[rbuf]*[\\\"\\'][^\\\"\\']*%s?[\\\"\\']\\s*%)"
            ],
            recommendation="Use bind parameters such as :name and pass values separately.",
        ),
        _principle(
            rule_id="sqlalchemy-002",
            principle="Session lifecycles should be explicit",
            category=PrincipleCategory.CORRECTNESS,
            severity=9,
            description="Ad-hoc Session() calls often hide connection management and teardown responsibilities.",
            patterns=["re:\\bSession\\(\\)"],
            recommendation="Prefer a context manager or a well-scoped session factory pattern.",
        ),
        _principle(
            rule_id="sqlalchemy-003",
            principle="SQLAlchemy 2.x code should prefer mapped_column over Column in ORM models",
            category=PrincipleCategory.IDIOMS,
            severity=6,
            description="mapped_column is the modern declarative field API in SQLAlchemy 2.x ORM models.",
            patterns=["re:\\bColumn\\("],
            recommendation="Use mapped_column() in declarative ORM models when targeting SQLAlchemy 2.x.",
        ),
        _principle(
            rule_id="sqlalchemy-004",
            principle="DeclarativeBase should replace declarative_base in 2.x-style code",
            category=PrincipleCategory.IDIOMS,
            severity=5,
            description="DeclarativeBase is the clearer modern base-class pattern for SQLAlchemy 2.x.",
            patterns=["re:\\bdeclarative_base\\("],
            recommendation="Define a DeclarativeBase subclass instead of calling declarative_base().",
        ),
        _principle(
            rule_id="sqlalchemy-005",
            principle="relationship loading should be an explicit choice",
            category=PrincipleCategory.PERFORMANCE,
            severity=7,
            description="Implicit relationship loading defaults can hide N+1 query behavior and make data access unpredictable.",
            patterns=["re:relationship\\((?:(?!lazy=)[\\s\\S])*?\\)"],
            recommendation="Specify lazy=, selectinload, or another explicit loading strategy.",
        ),
        _principle(
            rule_id="sqlalchemy-006",
            principle="Bulk inserts should avoid session.add inside loops",
            category=PrincipleCategory.PERFORMANCE,
            severity=6,
            description="session.add inside large loops is a common throughput bottleneck and often indicates missing bulk primitives.",
            patterns=["re:for\\s+.+:\\s*[\\s\\S]*?session\\.add\\("],
            recommendation="Use insert(), bulk APIs, or batched unit-of-work patterns for large writes.",
        ),
    ],
)
