from __future__ import annotations

from mcp_zen_of_languages.orchestration import build_repository_imports
from mcp_zen_of_languages.reporting import gaps as gaps_module
from mcp_zen_of_languages.reporting.report import (
    _analyze_targets,
    _collect_targets,
    _format_analysis_markdown,
)


def test_collect_targets_with_language_override(tmp_path):
    py_file = tmp_path / "sample.py"
    py_file.write_text("def foo():\n    pass\n", encoding="utf-8")
    targets = _collect_targets(tmp_path, "python")
    assert targets == [(py_file, "python")]


def test_format_analysis_markdown_no_violations():
    lines = _format_analysis_markdown([])
    assert lines == ["## Analysis"]


def test_collect_targets_filters_unknown(tmp_path):
    unknown = tmp_path / "sample.unknown"
    unknown.write_text("data", encoding="utf-8")
    targets = _collect_targets(tmp_path, None)
    assert targets == []


def test_collect_targets_includes_known_file(tmp_path):
    py_file = tmp_path / "sample.py"
    py_file.write_text("def foo():\n    pass\n", encoding="utf-8")
    targets = _collect_targets(tmp_path, None)
    assert (py_file, "python") in targets


def test_collect_targets_override_filters_mismatch(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    py_file = tmp_path / "sample.py"
    js_file = tmp_path / "sample.js"
    py_file.write_text("def foo():\n    pass\n", encoding="utf-8")
    js_file.write_text("function foo() {}\n", encoding="utf-8")
    targets = _collect_targets(tmp_path, "python")
    assert (py_file, "python") in targets
    assert all(path != js_file for path, _ in targets)


def test_analyze_targets_skips_unknown_language(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("data", encoding="utf-8")
    results = _analyze_targets([(sample, "unknownlang")], None)
    assert results == []


def test_build_repository_imports_non_python_is_empty(tmp_path):
    sample = tmp_path / "sample.ts"
    sample.write_text("import { x } from 'pkg';", encoding="utf-8")
    imports = build_repository_imports([sample], language="typescript")
    assert imports[str(sample)] == []


def test_gap_analysis_includes_missing_detectors(monkeypatch):
    def _no_detectors(rule_id: str, language: str) -> list[object]:
        return []

    monkeypatch.setattr(gaps_module.REGISTRY, "detectors_for_rule", _no_detectors)
    analysis = gaps_module.build_gap_analysis(["python"])
    assert any(
        gap.reason == "No detector registered for rule."
        for gap in analysis.detector_gaps
    )
