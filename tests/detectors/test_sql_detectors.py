from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import SqlAliasClarityConfig
from mcp_zen_of_languages.languages.configs import SqlAnsi89JoinConfig
from mcp_zen_of_languages.languages.configs import SqlDynamicSqlConfig
from mcp_zen_of_languages.languages.configs import SqlImplicitJoinCoercionConfig
from mcp_zen_of_languages.languages.configs import SqlInsertColumnListConfig
from mcp_zen_of_languages.languages.configs import SqlNolockConfig
from mcp_zen_of_languages.languages.configs import SqlSelectStarConfig
from mcp_zen_of_languages.languages.configs import SqlTransactionBoundaryConfig
from mcp_zen_of_languages.languages.configs import SqlUnboundedQueryConfig
from mcp_zen_of_languages.languages.sql.detectors import SqlAliasClarityDetector
from mcp_zen_of_languages.languages.sql.detectors import SqlAnsi89JoinDetector
from mcp_zen_of_languages.languages.sql.detectors import SqlDynamicSqlDetector
from mcp_zen_of_languages.languages.sql.detectors import SqlImplicitJoinCoercionDetector
from mcp_zen_of_languages.languages.sql.detectors import SqlInsertColumnListDetector
from mcp_zen_of_languages.languages.sql.detectors import SqlNolockDetector
from mcp_zen_of_languages.languages.sql.detectors import SqlSelectStarDetector
from mcp_zen_of_languages.languages.sql.detectors import SqlTransactionBoundaryDetector
from mcp_zen_of_languages.languages.sql.detectors import SqlUnboundedQueryDetector


def test_sql_select_star_detector_flags_violation():
    detector = SqlSelectStarDetector()
    context = AnalysisContext(code="SELECT * FROM users;", language="sql")

    violations = detector.detect(context, SqlSelectStarConfig())

    assert len(violations) == 1
    assert violations[0].location is not None
    assert violations[0].location.line == 1
    assert violations[0].location.column == 1


def test_sql_select_star_detector_ignores_count_star():
    detector = SqlSelectStarDetector()
    context = AnalysisContext(code="SELECT COUNT(*) FROM users;", language="sql")

    violations = detector.detect(context, SqlSelectStarConfig())

    assert violations == []


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
        code="SELECT id FROM users WITH (nolock);",
        language="sql",
    )

    violations = detector.detect(context, SqlNolockConfig())

    assert len(violations) == 1
    assert violations[0].location is not None
    assert violations[0].location.column > 1


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
    context = AnalysisContext(code="select id, email from users;", language="sql")

    violations = detector.detect(context, SqlUnboundedQueryConfig())

    assert len(violations) == 1
    assert violations[0].location is not None
    assert violations[0].location.column == 1


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
        code="begin transaction; INSERT INTO users(id) VALUES (1);",
        language="sql",
    )

    violations = detector.detect(context, SqlTransactionBoundaryConfig())

    assert len(violations) == 1
    assert violations[0].location is not None
    assert violations[0].location.column == 1


def test_sql_ansi89_join_detector_flags_comma_join():
    detector = SqlAnsi89JoinDetector()
    context = AnalysisContext(
        code=("SELECT a.id, b.name FROM orders a, users b WHERE a.user_id = b.id;"),
        language="sql",
    )

    violations = detector.detect(context, SqlAnsi89JoinConfig())

    assert len(violations) == 1
