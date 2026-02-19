from __future__ import annotations

from mcp_zen_of_languages.metrics import complexity
from mcp_zen_of_languages.metrics.collector import MetricsCollector
from mcp_zen_of_languages.metrics.dependency_graph import build_import_graph


def test_metrics_collector_collects():
    cyclomatic, _mi, loc = MetricsCollector.collect("def foo():\n    return 1\n")
    assert loc > 0
    assert cyclomatic


def test_dependency_graph_builds_cycles():
    imports = {"a.py": ["b.py"], "b.py": ["a.py"]}
    graph = build_import_graph(imports)
    assert graph.cycles


def test_compute_cyclomatic_complexity_handles_error(monkeypatch):
    monkeypatch.setattr(
        complexity,
        "cc_visit",
        lambda _: iter(()).throw(RuntimeError("boom")),
    )
    summary = complexity.compute_cyclomatic_complexity("def foo():\n    pass\n")
    assert summary.average == 0.0


def test_compute_maintainability_index_handles_error(monkeypatch):
    monkeypatch.setattr(
        complexity,
        "mi_visit",
        lambda **_: iter(()).throw(RuntimeError("boom")),
    )
    assert complexity.compute_maintainability_index("def foo():\n    pass\n") == 0.0
