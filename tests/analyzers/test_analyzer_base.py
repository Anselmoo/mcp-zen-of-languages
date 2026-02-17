from __future__ import annotations

from pydantic import BaseModel

from mcp_zen_of_languages.analyzers.base import BaseAnalyzer
from mcp_zen_of_languages.models import CyclomaticSummary


class _DummyParseResult(BaseModel):
    type: str = "dummy"


class _DummyAnalyzer(BaseAnalyzer):
    def default_config(self):
        from mcp_zen_of_languages.analyzers.base import AnalyzerConfig

        return AnalyzerConfig()

    def language(self) -> str:
        return "python"

    def parse_code(self, code: str):
        if "bad" in code:
            raise ValueError("parse error")
        return _DummyParseResult()

    def compute_metrics(self, code: str, ast_tree):
        return CyclomaticSummary(blocks=[], average=0.0), 0.0, len(code.splitlines())

    def build_pipeline(self):
        class _Pipeline:
            detectors = []

            def run(self, context, config):
                return []

        return _Pipeline()


class _DummyAnalyzerWithResults(_DummyAnalyzer):
    def build_pipeline(self):
        class _Detector:
            def detect(self, context, config):
                return []

            @property
            def name(self):
                return "dummy"

        class _Pipeline:
            def run(self, context, config):
                return _Detector().detect(context, config)

            @property
            def detectors(self):
                return [_Detector()]

        return _Pipeline()


def test_base_analyzer_analyze_success():
    analyzer = _DummyAnalyzer()
    result = analyzer.analyze("def foo():\n    pass\n")
    assert result.metrics.lines_of_code == 2


def test_base_analyzer_handles_parse_error():
    analyzer = _DummyAnalyzer()
    try:
        analyzer.analyze("bad")
    except ValueError as exc:
        assert "parse error" in str(exc)
    else:
        raise AssertionError("Expected parse error")


def test_base_analyzer_collects_results():
    analyzer = _DummyAnalyzerWithResults()
    result = analyzer.analyze("def foo():\n    pass\n")
    assert result.violations == []
