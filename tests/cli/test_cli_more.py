from __future__ import annotations

import json

from mcp_zen_of_languages import cli


def test_render_report_output_both():
    report = type("R", (), {"markdown": "md", "data": {"a": 1}})
    payload = cli._render_report_output(report, "both")
    decoded = json.loads(payload)
    assert decoded["markdown"] == "md"
    assert decoded["data"] == {"a": 1}


def test_report_markdown_includes_tables(tmp_path):
    from mcp_zen_of_languages.reporting.report import generate_report

    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    report = generate_report(str(sample))
    assert "| Metric | Value |" in report.markdown
    assert "| Severity |" in report.markdown
