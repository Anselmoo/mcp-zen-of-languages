from __future__ import annotations

from mcp_zen_of_languages.languages.javascript.analyzer import JavaScriptAnalyzer
from mcp_zen_of_languages.languages.powershell.analyzer import PowerShellAnalyzer
from mcp_zen_of_languages.languages.ruby.analyzer import RubyAnalyzer


def _pipeline_stub():
    class _Pipeline:
        def run(self, context, config):
            return []

        @property
        def detectors(self):
            return []

    return _Pipeline()


def test_javascript_analyzer_parse_code():
    class StubJavaScriptAnalyzer(JavaScriptAnalyzer):
        def build_pipeline(self):
            return _pipeline_stub()

    analyzer = StubJavaScriptAnalyzer()
    assert analyzer.parse_code("function foo() {}") is None


def test_powershell_analyzer_parse_code():
    class StubPowerShellAnalyzer(PowerShellAnalyzer):
        def build_pipeline(self):
            return _pipeline_stub()

    analyzer = StubPowerShellAnalyzer()
    assert analyzer.parse_code("function Get-Test {}") is None


def test_ruby_analyzer_parse_code():
    class StubRubyAnalyzer(RubyAnalyzer):
        def build_pipeline(self):
            return _pipeline_stub()

    analyzer = StubRubyAnalyzer()
    assert analyzer.parse_code("def foo\nend") is None
