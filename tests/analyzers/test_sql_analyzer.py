from mcp_zen_of_languages.languages.sql.analyzer import SqlAnalyzer


def test_sql_analyzer_detects_select_star():
    analyzer = SqlAnalyzer()

    result = analyzer.analyze("SELECT * FROM users;", path="schema.sql")

    assert result.language == "sql"
    assert any("SELECT *" in v.message for v in result.violations)
