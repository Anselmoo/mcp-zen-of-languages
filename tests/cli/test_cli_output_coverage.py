from __future__ import annotations

import json

from mcp_zen_of_languages.cli import main


def test_cli_report_text_output(tmp_path, capsys):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    exit_code = main(["report", str(sample)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Zen Report" in captured.out


def test_cli_report_json_output(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    output = tmp_path / "report.json"
    exit_code = main(["report", str(sample), "--format", "json", "--out", str(output)])
    assert exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["target"].endswith("sample.py")
