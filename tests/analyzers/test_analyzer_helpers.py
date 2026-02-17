from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    BaseAnalyzer,
    LocationHelperMixin,
)
from mcp_zen_of_languages.models import CyclomaticSummary, Location, Violation


class _Analyzer(BaseAnalyzer, LocationHelperMixin):
    def default_config(self):
        from mcp_zen_of_languages.analyzers.base import AnalyzerConfig

        return AnalyzerConfig()

    def language(self) -> str:
        return "python"

    def parse_code(self, code: str):
        return None

    def compute_metrics(self, code: str, ast_tree):
        return CyclomaticSummary(blocks=[], average=0.0), 0.0, len(code.splitlines())

    def build_pipeline(self):
        class _Pipeline:
            def run(self, context, config):
                return []

            @property
            def detectors(self):
                return []

        return _Pipeline()


def test_calculate_overall_score_empty():
    analyzer = _Analyzer()
    assert analyzer._calculate_overall_score([]) == 100.0


def test_location_helper_find_location():
    analyzer = _Analyzer()
    loc = analyzer.find_location_by_substring("def foo():\n    pass\n", "def foo")
    assert loc == Location(line=1, column=1)


def test_location_helper_ast_node_to_location():
    analyzer = _Analyzer()

    class Dummy:
        lineno = 3
        col_offset = 4

    loc = analyzer.ast_node_to_location(None, Dummy())
    assert loc == Location(line=3, column=5)


def test_build_result_scores():
    analyzer = _Analyzer()
    context = AnalysisContext(code="def foo():\n    pass\n", language="python")
    violation = Violation(principle="T", severity=5, message="msg")
    result = analyzer._build_result(context, [violation])
    assert result.overall_score == 90.0


def test_build_result_includes_metrics_defaults():
    analyzer = _Analyzer()
    context = AnalysisContext(code="def foo():\n    pass\n", language="python")
    result = analyzer._build_result(context, [])
    assert result.metrics.maintainability_index == 0.0


def test_build_dependency_analysis_default():
    analyzer = _Analyzer()
    context = AnalysisContext(code="def foo():\n    pass\n", language="python")
    assert analyzer._build_dependency_analysis(context) is None
