from __future__ import annotations

import logging

from mcp_zen_of_languages.analyzers.base import BaseAnalyzer
from mcp_zen_of_languages.models import CyclomaticSummary


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


def test_rules_adapter_failure_does_not_abort_analysis(monkeypatch, caplog):
    """A failing rules/dogma integration must degrade, not take the analysis down.

    Exercises the defensive ``except Exception`` in ``BaseAnalyzer.analyze``.
    ``attach_dogma_analysis`` is imported inside the method, so patching it at its
    source module is what the call actually resolves.
    """
    from mcp_zen_of_languages.dogmas import interface as dogma_interface

    original = dogma_interface.attach_dogma_analysis
    calls = {"n": 0}

    def _boom_on_second_call(result):
        # base.py calls attach_dogma_analysis twice per analyze(): first at the
        # unguarded result-construction site, then inside the defensive try.
        # Only the second call is the branch under test, so let the first through.
        calls["n"] += 1
        if calls["n"] < 2:
            return original(result)
        msg = "dogma analysis exploded"
        raise RuntimeError(msg)

    monkeypatch.setattr(dogma_interface, "attach_dogma_analysis", _boom_on_second_call)

    analyzer = _Analyzer()
    with caplog.at_level(logging.DEBUG, logger="mcp_zen_of_languages.analyzers.base"):
        result = analyzer.analyze("def foo():\n    pass\n")

    assert result is not None
    assert any(
        "RulesAdapter integration failed" in r.message for r in caplog.records
    ), "expected the analysis to log and continue rather than propagate"
