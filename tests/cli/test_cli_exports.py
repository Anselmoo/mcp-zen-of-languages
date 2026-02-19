from __future__ import annotations

import json

from mcp_zen_of_languages import cli


def _write_sample(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    return sample


def test_report_export_json_creates_file(tmp_path):
    sample = _write_sample(tmp_path)
    export_path = tmp_path / "report.json"
    exit_code = cli.main(["report", str(sample), "--export-json", str(export_path)])
    assert exit_code == 0
    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert payload["target"].endswith("sample.py")


def test_report_export_markdown_creates_file(tmp_path):
    sample = _write_sample(tmp_path)
    export_path = tmp_path / "report.md"
    exit_code = cli.main(["report", str(sample), "--export-markdown", str(export_path)])
    assert exit_code == 0
    contents = export_path.read_text(encoding="utf-8")
    assert contents.startswith("# Zen of Languages Report")
    assert "| Metric | Value |" in contents
    assert "| Severity |" in contents


def test_report_export_log_creates_file(tmp_path):
    sample = _write_sample(tmp_path)
    export_path = tmp_path / "report.log"
    exit_code = cli.main(["report", str(sample), "--export-log", str(export_path)])
    assert exit_code == 0
    contents = export_path.read_text(encoding="utf-8")
    assert "target:" in contents
    assert "total_violations:" in contents


def test_report_export_all_three(tmp_path):
    sample = _write_sample(tmp_path)
    export_json = tmp_path / "report.json"
    export_md = tmp_path / "report.md"
    export_log = tmp_path / "report.log"
    exit_code = cli.main(
        [
            "report",
            str(sample),
            "--export-json",
            str(export_json),
            "--export-markdown",
            str(export_md),
            "--export-log",
            str(export_log),
        ],
    )
    assert exit_code == 0
    assert export_json.exists()
    assert export_md.exists()
    assert export_log.exists()


def test_report_export_with_out_flag(tmp_path):
    sample = _write_sample(tmp_path)
    output = tmp_path / "report.out"
    export_json = tmp_path / "report.json"
    exit_code = cli.main(
        [
            "report",
            str(sample),
            "--out",
            str(output),
            "--export-json",
            str(export_json),
        ],
    )
    assert exit_code == 0
    assert output.exists()
    assert export_json.exists()


def test_report_export_json_content(tmp_path):
    sample = _write_sample(tmp_path)
    export_path = tmp_path / "report.json"
    exit_code = cli.main(["report", str(sample), "--export-json", str(export_path)])
    assert exit_code == 0
    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert {"target", "languages", "summary", "analysis", "gaps"} <= payload.keys()


def test_report_export_log_severity_counts(tmp_path):
    sample = _write_sample(tmp_path)
    export_path = tmp_path / "report.log"
    exit_code = cli.main(["report", str(sample), "--export-log", str(export_path)])
    assert exit_code == 0
    contents = export_path.read_text(encoding="utf-8")
    assert "critical:" in contents
    assert "high:" in contents
    assert "medium:" in contents
    assert "low:" in contents
