from mcp_zen_of_languages.languages.rust import RustAnalyzer


def test_rust_analyzer_detects_unwrap():
    analyzer = RustAnalyzer()
    code = "fn main() { let _ = Some(1).unwrap(); }"
    result = analyzer.analyze(code)
    assert any("unwrap" in v.message for v in result.violations)
