from __future__ import annotations

import json

from mcp_zen_of_languages import cli


def _write_sample(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    return sample


def test_prompts_remediation_outputs_panel(tmp_path, capsys):
    sample = _write_sample(tmp_path)
    exit_code = cli.main(["prompts", str(sample), "--mode", "remediation"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Zen Prompts" in captured.out
    assert "Remediation Roadmap" in captured.out
    assert "File Summary" in captured.out
    assert "### File:" not in captured.out


def test_prompts_agent_outputs_table(tmp_path, capsys):
    sample = _write_sample(tmp_path)
    exit_code = cli.main(["prompts", str(sample), "--mode", "agent"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Agent Tasks" in captured.out


def test_prompts_quiet_suppresses_output(tmp_path, capsys):
    sample = _write_sample(tmp_path)
    exit_code = cli.main(["--quiet", "prompts", str(sample), "--mode", "agent"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert captured.out == ""


def test_prompts_both_exports(tmp_path):
    sample = _write_sample(tmp_path)
    export_md = tmp_path / "rules.agent.md"
    export_json = tmp_path / "rules.agent.json"
    exit_code = cli.main(
        [
            "prompts",
            str(sample),
            "--mode",
            "both",
            "--export-prompts",
            str(export_md),
            "--export-agent",
            str(export_json),
        ],
    )
    assert exit_code == 0
    assert export_md.exists()
    contents = export_md.read_text(encoding="utf-8")
    assert "### File:" in contents
    payload = json.loads(export_json.read_text(encoding="utf-8"))
    assert "tasks" in payload
    assert "clusters" in payload
