from __future__ import annotations

import json
import sys

import rich.prompt

from mcp_zen_of_languages import cli


def test_init_yes_writes_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    exit_code = cli.main(
        [
            "init",
            "--yes",
            "--languages",
            "python",
            "--languages",
            "go",
            "--strictness",
            "strict",
        ]
    )
    assert exit_code == 0
    contents = (tmp_path / "zen-config.yaml").read_text(encoding="utf-8")
    assert "  - python" in contents
    assert "  - go" in contents
    assert "severity_threshold: 7" in contents


def test_init_interactive_writes_vscode_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "sample.py").write_text("def foo():\n    pass\n", encoding="utf-8")

    class DummyStdin:
        def isatty(self):
            return True

    monkeypatch.setattr(sys, "stdin", DummyStdin())
    confirmations = iter([True, True])
    monkeypatch.setattr(
        rich.prompt.Confirm, "ask", lambda *args, **kwargs: next(confirmations)
    )
    monkeypatch.setattr(rich.prompt.Prompt, "ask", lambda *args, **kwargs: "strict")
    exit_code = cli.main(["init"])
    assert exit_code == 0
    contents = (tmp_path / "zen-config.yaml").read_text(encoding="utf-8")
    assert "  - python" in contents
    assert "severity_threshold: 7" in contents
    payload = json.loads(
        (tmp_path / ".vscode" / "mcp.json").read_text(encoding="utf-8")
    )
    assert "mcp-zen-of-languages" in payload["mcp"]["servers"]
