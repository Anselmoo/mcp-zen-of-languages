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
        ],
    )
    assert exit_code == 0
    contents = (tmp_path / "zen-config.yaml").read_text(encoding="utf-8")
    assert "  - python" in contents
    assert "  - go" in contents
    assert "severity_threshold: 7" in contents
    assert "#   VS Code: .vscode/mcp.json" in contents
    assert "#   Codex: ~/.codex/config.toml" in contents
    assert "#   Copilot (repo): .github/mcp.json" in contents
    assert "#   Copilot (global): ~/.copilot/mcp-config.json" in contents
    ignore_contents = (tmp_path / ".zen-of-languages.ignore").read_text(
        encoding="utf-8"
    )
    assert ".venv/" in ignore_contents
    assert "node_modules/" in ignore_contents
    assert "dist/" in ignore_contents
    assert "build/" in ignore_contents


def test_init_yes_writes_requested_mcp_targets(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli.Path, "home", lambda: home)

    exit_code = cli.main(
        [
            "init",
            "--yes",
            "--languages",
            "python",
            "--mcp-target",
            "vscode",
            "--mcp-target",
            "codex",
            "--mcp-target",
            "copilot-local",
            "--mcp-target",
            "copilot-global",
        ],
    )

    assert exit_code == 0

    vscode_payload = json.loads(
        (tmp_path / ".vscode" / "mcp.json").read_text(encoding="utf-8")
    )
    assert vscode_payload["servers"]["zen-of-languages"]["args"] == [
        "--from",
        "mcp-zen-of-languages",
        "mcp-zen-of-languages-server",
    ]

    copilot_local = json.loads(
        (tmp_path / ".github" / "mcp.json").read_text(encoding="utf-8")
    )
    assert "zen-of-languages" in copilot_local["mcpServers"]

    copilot_global = json.loads(
        (home / ".copilot" / "mcp-config.json").read_text(encoding="utf-8")
    )
    assert "zen-of-languages" in copilot_global["mcpServers"]

    codex_config = (home / ".codex" / "config.toml").read_text(encoding="utf-8")
    assert '[mcp_servers."zen-of-languages"]' in codex_config
    assert 'command = "uvx"' in codex_config
    assert "mcp-zen-of-languages-server" in codex_config


def test_init_interactive_writes_vscode_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "sample.py").write_text("def foo():\n    pass\n", encoding="utf-8")

    class DummyStdin:
        def isatty(self):
            return True

    monkeypatch.setattr(sys, "stdin", DummyStdin())
    confirmations = iter([True, True])
    monkeypatch.setattr(
        rich.prompt.Confirm,
        "ask",
        lambda *args, **kwargs: next(confirmations),
    )
    responses = iter(["strict", "vscode"])
    monkeypatch.setattr(
        rich.prompt.Prompt,
        "ask",
        lambda *args, **kwargs: next(responses),
    )
    exit_code = cli.main(["init"])
    assert exit_code == 0
    contents = (tmp_path / "zen-config.yaml").read_text(encoding="utf-8")
    assert "  - python" in contents
    assert "severity_threshold: 7" in contents
    assert (
        "# See docs/getting-started/mcp-integration.md for setup examples." in contents
    )
    assert (tmp_path / ".zen-of-languages.ignore").exists()
    payload = json.loads(
        (tmp_path / ".vscode" / "mcp.json").read_text(encoding="utf-8"),
    )
    assert "zen-of-languages" in payload["servers"]
    server = payload["servers"]["zen-of-languages"]
    assert server["command"] == "uvx"
    assert server["args"] == [
        "--from",
        "mcp-zen-of-languages",
        "mcp-zen-of-languages-server",
    ]


def test_init_interactive_can_write_codex_and_local_copilot_configs(
    tmp_path,
    monkeypatch,
):
    home = tmp_path / "home"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli.Path, "home", lambda: home)
    (tmp_path / "sample.py").write_text("def foo():\n    pass\n", encoding="utf-8")

    class DummyStdin:
        def isatty(self):
            return True

    monkeypatch.setattr(sys, "stdin", DummyStdin())
    confirmations = iter([True, True])
    monkeypatch.setattr(
        rich.prompt.Confirm,
        "ask",
        lambda *args, **kwargs: next(confirmations),
    )
    responses = iter(["moderate", "codex, copilot"])
    monkeypatch.setattr(
        rich.prompt.Prompt,
        "ask",
        lambda *args, **kwargs: next(responses),
    )

    exit_code = cli.main(["init"])

    assert exit_code == 0
    assert (tmp_path / ".github" / "mcp.json").exists()
    codex_config = (home / ".codex" / "config.toml").read_text(encoding="utf-8")
    assert '[mcp_servers."zen-of-languages"]' in codex_config


def test_init_yes_appends_codex_config_without_clobbering_existing_sections(
    tmp_path,
    monkeypatch,
):
    home = tmp_path / "home"
    codex_dir = home / ".codex"
    codex_dir.mkdir(parents=True)
    (codex_dir / "config.toml").write_text(
        'model = "gpt-5.4"\n\n[mcp_servers.context7]\nurl = "https://example.com"\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli.Path, "home", lambda: home)

    exit_code = cli.main(["init", "--yes", "--mcp-target", "codex"])

    assert exit_code == 0
    codex_config = (codex_dir / "config.toml").read_text(encoding="utf-8")
    assert 'model = "gpt-5.4"' in codex_config
    assert "[mcp_servers.context7]" in codex_config
    assert codex_config.count("mcp-zen-of-languages-server") == 1


def test_init_yes_merges_existing_copilot_global_config(tmp_path, monkeypatch):
    home = tmp_path / "home"
    copilot_dir = home / ".copilot"
    copilot_dir.mkdir(parents=True)
    (copilot_dir / "mcp-config.json").write_text(
        json.dumps(
            {
                "mcpServers": {
                    "context7": {
                        "command": "npx",
                        "args": ["-y", "@upstash/context7-mcp"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli.Path, "home", lambda: home)

    exit_code = cli.main(["init", "--yes", "--mcp-target", "copilot-global"])

    assert exit_code == 0
    payload = json.loads((copilot_dir / "mcp-config.json").read_text(encoding="utf-8"))
    assert "context7" in payload["mcpServers"]
    assert "zen-of-languages" in payload["mcpServers"]
