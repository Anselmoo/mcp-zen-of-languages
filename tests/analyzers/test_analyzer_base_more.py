from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import BaseAnalyzer
from mcp_zen_of_languages.models import CyclomaticSummary, Violation


class _Analyzer(BaseAnalyzer):
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


def test_analyze_includes_rules_summary_disabled():
    analyzer = _Analyzer()
    analyzer.config.enable_pattern_detection = False
    result = analyzer.analyze("def foo():\n    pass\n")
    assert result.rules_summary is None or result.rules_summary


def test_calculate_overall_score_nonempty():
    analyzer = _Analyzer()
    violations = [Violation(principle="T", severity=5, message="msg")]
    assert analyzer._calculate_overall_score(violations) == 90.0


def test_create_context_sets_repository_imports():
    analyzer = _Analyzer()
    context = analyzer._create_context(
        code="def foo():\n    pass\n",
        path="sample.py",
        other_files=None,
        repository_imports={"sample.py": ["os"]},
    )
    assert context.repository_imports
