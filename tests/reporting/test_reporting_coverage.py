from __future__ import annotations

from mcp_zen_of_languages.reporting.report import generate_report


def test_report_with_language_override(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    report = generate_report(str(sample), language="python", include_gaps=True)
    assert "Languages:" in report.markdown
