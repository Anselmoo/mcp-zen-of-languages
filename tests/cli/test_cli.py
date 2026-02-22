from __future__ import annotations

import json
import re
import sys
from importlib import metadata

import pytest

from mcp_zen_of_languages import cli
from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    Location,
    Metrics,
    Violation,
)
from mcp_zen_of_languages.rules import get_all_languages

CONFIG_ALREADY_EXISTS_EXIT_CODE = 2
SARIF_RESULT_LINE = 2


def _assert_max_width(output: str, expected: int = 88) -> None:
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")
    for line in output.splitlines():
        assert len(ansi_re.sub("", line)) <= expected


def test_check_command_runs(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    exit_code = cli.main(["check", str(sample)])
    assert exit_code == 0


def test_check_command_runs_css(tmp_path):
    sample = tmp_path / "styles.css"
    sample.write_text(".btn { color: var(--text); }\n", encoding="utf-8")
    assert cli.main(["check", str(sample)]) == 0


def test_check_command_runs_for_gitlab_ci_file(tmp_path):
    sample = tmp_path / ".gitlab-ci.yml"
    sample.write_text("build:\n  image: python:3.12-slim\n  script:\n    - echo ok\n")
    exit_code = cli.main(["check", str(sample)])
    assert exit_code == 0


def test_check_command_runs_scss(tmp_path):
    sample = tmp_path / "styles.scss"
    sample.write_text(".btn { .label { color: var(--text); } }\n", encoding="utf-8")
    assert cli.main(["check", str(sample)]) == 0


def test_check_command_outputs_terminal_summary(monkeypatch, tmp_path, capsys):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")

    result = AnalysisResult(
        language="python",
        path=str(sample),
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=100.0,
            lines_of_code=1,
        ),
        violations=[
            Violation(
                principle="x",
                severity=8,
                message="default summary should hide this detail",
            ),
        ],
        overall_score=90.0,
    )

    monkeypatch.setattr(
        cli,
        "_collect_targets",
        lambda *_args, **_kwargs: [(sample, "python")],
    )
    monkeypatch.setattr(cli, "_analyze_targets", lambda *_args, **_kwargs: [result])

    assert cli.main(["check", str(sample)]) == 0
    output = capsys.readouterr().out
    assert "Zen Report" in output
    assert "Summary" in output
    assert "Total files" in output
    assert "Total violations" in output
    assert "default summary should hide this detail" not in output


def test_check_command_show_files_outputs_details(monkeypatch, tmp_path, capsys):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")

    result = AnalysisResult(
        language="python",
        path=str(sample),
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=100.0,
            lines_of_code=1,
        ),
        violations=[
            Violation(
                principle="x",
                severity=8,
                message="visible per-file detail",
            ),
        ],
        overall_score=90.0,
    )

    monkeypatch.setattr(
        cli,
        "_collect_targets",
        lambda *_args, **_kwargs: [(sample, "python")],
    )
    monkeypatch.setattr(cli, "_analyze_targets", lambda *_args, **_kwargs: [result])

    assert cli.main(["check", str(sample), "--show-files"]) == 0
    output = capsys.readouterr().out
    assert "Zen Report" in output
    assert "visible per-file detail" in output


def test_check_command_terminal_summary_writes_out_file(monkeypatch, tmp_path, capsys):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    output = tmp_path / "check-summary.txt"

    result = AnalysisResult(
        language="python",
        path=str(sample),
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=100.0,
            lines_of_code=1,
        ),
        violations=[Violation(principle="x", severity=8, message="high")],
        overall_score=90.0,
    )

    monkeypatch.setattr(
        cli,
        "_collect_targets",
        lambda *_args, **_kwargs: [(sample, "python")],
    )
    monkeypatch.setattr(cli, "_analyze_targets", lambda *_args, **_kwargs: [result])

    assert cli.main(["--quiet", "check", str(sample), "--out", str(output)]) == 0
    file_output = output.read_text(encoding="utf-8")
    assert "target:" in file_output
    assert "total_files: 1" in file_output
    assert "total_violations: 1" in file_output
    assert capsys.readouterr().out == ""


def test_check_command_fail_on_severity(monkeypatch, tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")

    result = AnalysisResult(
        language="python",
        path=str(sample),
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=100.0,
            lines_of_code=1,
        ),
        violations=[Violation(principle="x", severity=8, message="high")],
        overall_score=90.0,
    )

    monkeypatch.setattr(
        cli,
        "_collect_targets",
        lambda *_args, **_kwargs: [(sample, "python")],
    )
    monkeypatch.setattr(cli, "_analyze_targets", lambda *_args, **_kwargs: [result])

    assert cli.main(["--quiet", "check", str(sample), "--fail-on-severity", "7"]) == 1
    assert cli.main(["--quiet", "check", str(sample), "--fail-on-severity", "9"]) == 0


def test_check_command_passes_enable_external_tools(monkeypatch, tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    captured: dict[str, bool] = {}

    result = AnalysisResult(
        language="python",
        path=str(sample),
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=100.0,
            lines_of_code=1,
        ),
        violations=[],
        overall_score=100.0,
    )

    monkeypatch.setattr(
        cli,
        "_collect_targets",
        lambda *_args, **_kwargs: [(sample, "python")],
    )

    def _fake_analyze_targets(*_args, **kwargs):
        captured["enable_external_tools"] = kwargs.get("enable_external_tools", False)
        return [result]

    monkeypatch.setattr(cli, "_analyze_targets", _fake_analyze_targets)

    assert cli.main(["--quiet", "check", str(sample), "--enable-external-tools"]) == 0
    assert captured["enable_external_tools"] is True


def test_check_command_passes_allow_temporary_runners(monkeypatch, tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    captured: dict[str, bool] = {}

    result = AnalysisResult(
        language="python",
        path=str(sample),
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=100.0,
            lines_of_code=1,
        ),
        violations=[],
        overall_score=100.0,
    )

    monkeypatch.setattr(
        cli,
        "_collect_targets",
        lambda *_args, **_kwargs: [(sample, "python")],
    )

    def _fake_analyze_targets(*_args, **kwargs):
        captured["allow_temporary_tools"] = kwargs.get("allow_temporary_tools", False)
        return [result]

    monkeypatch.setattr(cli, "_analyze_targets", _fake_analyze_targets)

    assert (
        cli.main(
            [
                "--quiet",
                "check",
                str(sample),
                "--enable-external-tools",
                "--allow-temporary-runners",
            ],
        )
        == 0
    )
    assert captured["allow_temporary_tools"] is True


def test_check_command_sarif_output(monkeypatch, tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    output = tmp_path / "result.sarif"
    result = AnalysisResult(
        language="python",
        path=str(sample),
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=100.0,
            lines_of_code=1,
        ),
        violations=[
            Violation(
                principle="x",
                severity=8,
                message="high",
                location=Location(line=2, column=1),
            ),
        ],
        overall_score=90.0,
    )
    monkeypatch.setattr(
        cli,
        "_collect_targets",
        lambda *_args, **_kwargs: [(sample, "python")],
    )
    monkeypatch.setattr(cli, "_analyze_targets", lambda *_args, **_kwargs: [result])

    assert (
        cli.main(
            [
                "--quiet",
                "check",
                str(sample),
                "--format",
                "sarif",
                "--out",
                str(output),
            ],
        )
        == 0
    )
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["version"] == "2.1.0"
    assert "microsoft/sarif-python-om" in payload["$schema"]
    region = payload["runs"][0]["results"][0]["locations"][0]["physicalLocation"][
        "region"
    ]
    assert region["startLine"] == SARIF_RESULT_LINE
    assert region["startColumn"] == 1


def test_list_rules_outputs_principles(capsys):
    exit_code = cli.main(["list-rules", "python"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "python-001" in captured.out


def test_init_requires_force(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    existing = tmp_path / "zen-config.yaml"
    existing.write_text("languages:\n  - python\n", encoding="utf-8")
    exit_code = cli.main(["init"])
    assert exit_code == CONFIG_ALREADY_EXISTS_EXIT_CODE
    exit_code = cli.main(["init", "--force"])
    assert exit_code == 0
    assert (tmp_path / "zen-config.yaml").read_text(encoding="utf-8")


def test_report_command_outputs_markdown(tmp_path, capsys):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    exit_code = cli.main(["report", str(sample)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Zen Report" in captured.out
    assert "Gap Analysis" in captured.out


def test_reports_command_outputs_markdown(tmp_path, capsys):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    exit_code = cli.main(["reports", str(sample)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Zen Report" in captured.out


def test_report_command_outputs_json(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    output = tmp_path / "report.json"
    exit_code = cli.main(
        ["report", str(sample), "--format", "json", "--out", str(output)],
    )
    assert exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["target"].endswith("sample.py")


def test_report_command_writes_out_file(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    output = tmp_path / "report.md"
    exit_code = cli.main(["report", str(sample), "--out", str(output)])
    assert exit_code == 0
    assert output.read_text(encoding="utf-8").startswith("# Zen of Languages Report")


def test_export_mapping_outputs_json(capsys):
    exit_code = cli.main(["export-mapping", "--format", "json"])
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload


def test_export_mapping_default_outputs_terminal(capsys):
    exit_code = cli.main(["export-mapping"])
    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Rule Detector Mapping" in output
    assert "Language Coverage" in output


def test_export_mapping_writes_file(tmp_path):
    output = tmp_path / "mapping.json"
    exit_code = cli.main(["export-mapping", "--out", str(output)])
    assert exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload


def test_main_uses_sys_argv_for_help(monkeypatch, capsys):
    monkeypatch.setenv("COLUMNS", "200")
    monkeypatch.setattr(cli, "get_banner_art", lambda: "ZEN HELP BANNER")
    monkeypatch.setattr(sys, "argv", ["prog", "--help"])
    exit_code = cli.main()
    assert exit_code == 0
    output = capsys.readouterr().out
    assert "ZEN HELP BANNER" in output
    assert "Usage" in output
    assert "Analysis" in output
    assert "Configuration" in output
    assert "reports" in output
    assert "prompts" in output
    assert "full-screen TUI" in output
    assert "[bold" not in output
    assert "check" in output
    assert "Usage:" in output
    assert "mcp-zen-of-languages" not in output
    assert "zen-cli" not in output
    _assert_max_width(output)


def test_report_help_respects_width_cap(monkeypatch, capsys):
    monkeypatch.setenv("COLUMNS", "200")
    monkeypatch.setattr(cli, "get_banner_art", lambda: "ZEN HELP BANNER")
    exit_code = cli.main(["report", "--help"])
    assert exit_code == 0
    output = capsys.readouterr().out
    assert "ZEN HELP BANNER" in output
    assert "Usage" in output
    _assert_max_width(output)


def test_reports_help_respects_width_cap(monkeypatch, capsys):
    monkeypatch.setenv("COLUMNS", "200")
    monkeypatch.setattr(cli, "get_banner_art", lambda: "ZEN HELP BANNER")
    exit_code = cli.main(["reports", "--help"])
    assert exit_code == 0
    output = capsys.readouterr().out
    assert "ZEN HELP BANNER" in output
    assert "Usage" in output
    _assert_max_width(output)


def test_prompts_help_includes_banner(monkeypatch, capsys):
    monkeypatch.setenv("COLUMNS", "200")
    monkeypatch.setattr(cli, "get_banner_art", lambda: "ZEN HELP BANNER")
    exit_code = cli.main(["prompts", "--help"])
    assert exit_code == 0
    output = capsys.readouterr().out
    assert "ZEN HELP BANNER" in output
    assert "Usage" in output
    _assert_max_width(output)


def test_main_without_args_shows_welcome(capsys):
    assert cli.main([]) == 0
    output = capsys.readouterr().out
    assert "Welcome to Zen of Languages." in output
    assert "Quick Commands" in output
    assert "zen reports <path>" in output
    assert "no full-screen TUI" in output


def test_prompt_alias_works(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    exit_code = cli.main(["--quiet", "prompt", str(sample), "--mode", "agent"])
    assert exit_code == 0


def test_prompts_command_passes_enable_external_tools(monkeypatch, tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    captured: dict[str, bool] = {}

    result = AnalysisResult(
        language="python",
        path=str(sample),
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=100.0,
            lines_of_code=1,
        ),
        violations=[],
        overall_score=100.0,
    )

    monkeypatch.setattr(
        cli,
        "_collect_targets",
        lambda *_args, **_kwargs: [(sample, "python")],
    )

    def _fake_analyze_targets(*_args, **kwargs):
        captured["enable_external_tools"] = kwargs.get("enable_external_tools", False)
        return [result]

    monkeypatch.setattr(cli, "_analyze_targets", _fake_analyze_targets)

    assert (
        cli.main(
            [
                "--quiet",
                "prompts",
                str(sample),
                "--mode",
                "agent",
                "--enable-external-tools",
            ],
        )
        == 0
    )
    assert captured["enable_external_tools"] is True


def test_prompts_command_passes_allow_temporary_runners(monkeypatch, tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    captured: dict[str, bool] = {}

    result = AnalysisResult(
        language="python",
        path=str(sample),
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=100.0,
            lines_of_code=1,
        ),
        violations=[],
        overall_score=100.0,
    )

    monkeypatch.setattr(
        cli,
        "_collect_targets",
        lambda *_args, **_kwargs: [(sample, "python")],
    )

    def _fake_analyze_targets(*_args, **kwargs):
        captured["allow_temporary_tools"] = kwargs.get("allow_temporary_tools", False)
        return [result]

    monkeypatch.setattr(cli, "_analyze_targets", _fake_analyze_targets)

    assert (
        cli.main(
            [
                "--quiet",
                "prompts",
                str(sample),
                "--mode",
                "agent",
                "--enable-external-tools",
                "--allow-temporary-runners",
            ],
        )
        == 0
    )
    assert captured["allow_temporary_tools"] is True


def test_list_rules_uses_compact_headers(capsys):
    exit_code = cli.main(["list-rules", "python"])
    assert exit_code == 0
    output = capsys.readouterr().out
    assert "ID" in output
    assert "Sev" in output


def test_configure_app_installs_traceback_when_verbose(monkeypatch):
    installed: list[bool] = []
    monkeypatch.setattr(cli, "_install_rich_traceback", lambda: installed.append(True))
    monkeypatch.setattr(cli, "print_banner", lambda *args, **kwargs: None)
    cli._configure_app(quiet=True, verbose=True)
    assert installed == [True]


def test_zen_alias_entrypoint_present():
    entry_points = metadata.entry_points(group="console_scripts")
    assert any(
        ep.name == "zen" and ep.value == "mcp_zen_of_languages.cli:main"
        for ep in entry_points
    )


def test_deprecated_cli_alias_entrypoints_absent():
    entry_points = metadata.entry_points(group="console_scripts")
    deprecated = {"mcp-zen-of-languages", "zen-of-languages", "zen-cli"}
    assert all(ep.name not in deprecated for ep in entry_points)


SAMPLES = {
    "python": "def foo():\n    pass\n",
    "javascript": "function foo() {}\n",
    "typescript": "interface Foo {}\n",
    "ruby": "def foo\nend\n",
    "go": "package main\nfunc main() {}\n",
    "rust": "fn main() {}\n",
    "bash": "#!/usr/bin/env bash\nset -euo pipefail\n",
    "powershell": "function Get-Foo {}\n",
    "cpp": "int main() { return 0; }\n",
    "csharp": "public class Foo {}\n",
    "css": ".button { color: var(--text); }\n",
    "yaml": "key: value\n",
    "gitlab_ci": "build:\n  image: python\n  script:\n    - echo hello\n",
    "github-actions": "name: CI\non: push\njobs:\n  build:\n    runs-on: ubuntu-latest\n    timeout-minutes: 5\n    steps:\n      - run: echo hi\n        shell: bash\n",
    "toml": 'key = "value"\n',
    "json": '{"key": "value"}\n',
    "sql": "SELECT id FROM users;\n",
    "markdown": "# Title\n\nSee http://example.com\n",
    "xml": "<root></root>\n",
    "latex": "\\documentclass{article}\n\\begin{document}Hello\\end{document}\n",
    "docker_compose": "services:\n  web:\n    image: nginx:latest\n",
    "dockerfile": "FROM ubuntu:latest\nUSER root\n",
}


@pytest.mark.parametrize("language", get_all_languages())
def test_report_smoke_per_language(tmp_path, language):
    sample = tmp_path / f"sample.{language}.txt"
    sample.write_text(SAMPLES[language], encoding="utf-8")
    output = tmp_path / f"report-{language}.json"
    exit_code = cli.main(
        [
            "report",
            str(sample),
            "--language",
            language,
            "--format",
            "json",
            "--out",
            str(output),
        ],
    )
    assert exit_code == 0
    assert output.exists()
