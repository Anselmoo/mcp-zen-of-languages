from mcp_zen_of_languages.analyzers.base import AnalysisContext
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
from mcp_zen_of_languages.languages.sql.detectors import (
    SqlAliasClarityDetector,
    SqlAnsi89JoinDetector,
    SqlDynamicSqlDetector,
    SqlImplicitJoinCoercionDetector,
    SqlInsertColumnListDetector,
    SqlNolockDetector,
    SqlSelectStarDetector,
    SqlTransactionBoundaryDetector,
    SqlUnboundedQueryDetector,
)


def test_sql_select_star_detector_flags_violation():
    detector = SqlSelectStarDetector()
    context = AnalysisContext(code="SELECT * FROM users;", language="sql")

    violations = detector.detect(context, SqlSelectStarConfig())

    assert len(violations) == 1


def test_sql_insert_column_list_detector_flags_values_only_insert():
    detector = SqlInsertColumnListDetector()
    context = AnalysisContext(
        code="INSERT INTO users VALUES (1, 'alice');", language="sql"
    )

    violations = detector.detect(context, SqlInsertColumnListConfig())

    assert len(violations) == 1


def test_sql_dynamic_sql_detector_flags_exec_concatenation():
    detector = SqlDynamicSqlDetector()
    context = AnalysisContext(
        code="EXEC('SELECT * FROM users WHERE id=' + @id);",
        language="sql",
    )

    violations = detector.detect(context, SqlDynamicSqlConfig())

    assert len(violations) == 1


def test_sql_nolock_detector_flags_nolock_usage():
    detector = SqlNolockDetector()
    context = AnalysisContext(
        code="SELECT id FROM users WITH (NOLOCK);",
        language="sql",
    )

    violations = detector.detect(context, SqlNolockConfig())

    assert len(violations) == 1


def test_sql_implicit_join_coercion_detector_flags_cast_in_join_on():
    detector = SqlImplicitJoinCoercionDetector()
    context = AnalysisContext(
        code=(
            "SELECT * FROM orders o JOIN users u ON CAST(o.user_id AS VARCHAR) = u.id;"
        ),
        language="sql",
    )

    violations = detector.detect(context, SqlImplicitJoinCoercionConfig())

    assert len(violations) == 1


def test_sql_unbounded_query_detector_flags_unrestricted_select():
    detector = SqlUnboundedQueryDetector()
    context = AnalysisContext(code="SELECT id, email FROM users;", language="sql")

    violations = detector.detect(context, SqlUnboundedQueryConfig())

    assert len(violations) == 1


def test_sql_alias_clarity_detector_flags_short_alias():
    detector = SqlAliasClarityDetector()
    context = AnalysisContext(
        code="SELECT o.id FROM orders o JOIN items i ON o.id = i.order_id;",
        language="sql",
    )

    violations = detector.detect(context, SqlAliasClarityConfig())

    assert len(violations) == 1


def test_sql_transaction_boundary_detector_flags_missing_commit_or_rollback():
    detector = SqlTransactionBoundaryDetector()
    context = AnalysisContext(
        code="BEGIN TRANSACTION; INSERT INTO users(id) VALUES (1);",
        language="sql",
    )

    violations = detector.detect(context, SqlTransactionBoundaryConfig())

    assert len(violations) == 1


def test_sql_ansi89_join_detector_flags_comma_join():
    detector = SqlAnsi89JoinDetector()
    context = AnalysisContext(
        code=("SELECT a.id, b.name FROM orders a, users b WHERE a.user_id = b.id;"),
        language="sql",
    )

    violations = detector.detect(context, SqlAnsi89JoinConfig())

    assert len(violations) == 1
