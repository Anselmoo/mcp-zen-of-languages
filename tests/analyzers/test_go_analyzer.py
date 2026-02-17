from mcp_zen_of_languages.languages.go import GoAnalyzer


def test_go_analyzer_detects_error_handling():
    analyzer = GoAnalyzer()
    code = 'package main\n\nfunc main() { panic("boom") }\n'
    result = analyzer.analyze(code)
    assert any("Errors are values" in v.principle for v in result.violations)
