from __future__ import annotations

from mcp_zen_of_languages import cli


def test_report_terminal_output_ignores_format(tmp_path, capsys):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    exit_code = cli.main(["report", str(sample), "--format", "json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Zen Report" in captured.out
