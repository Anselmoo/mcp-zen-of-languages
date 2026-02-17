from __future__ import annotations

from mcp_zen_of_languages.reporting.gaps import build_gap_analysis
from mcp_zen_of_languages.reporting.report import (
    _build_repository_imports,
    _format_gap_markdown,
    generate_report,
)


def test_build_gap_analysis_unknown_language():
    gaps = build_gap_analysis(["unknownlang"])
    assert gaps.detector_gaps == []


def test_build_repository_imports_reads_imports(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("import os\nfrom sys import path\n", encoding="utf-8")
    results = _build_repository_imports([sample])
    assert results[str(sample)] == ["os", "sys"]


def test_format_gap_markdown_includes_feature_gaps():
    gaps = build_gap_analysis(["python"])
    lines = _format_gap_markdown(gaps)
    assert lines[0] == "## Gap Analysis"
    assert any("Feature" in line for line in lines)


def test_generate_report_with_gaps_only(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    report = generate_report(str(sample), include_analysis=False, include_gaps=True)
    assert "Gap Analysis" in report.markdown
