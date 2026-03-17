from __future__ import annotations

import tomllib

from pathlib import Path


def _project_scripts() -> dict[str, str]:
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    pyproject_data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    return pyproject_data["project"]["scripts"]


def test_cli_and_server_script_aliases_are_exposed() -> None:
    scripts = _project_scripts()

    assert scripts == {
        "mcp-zen-of-languages": "mcp_zen_of_languages.__main__:main",
        "mcp-zen-of-languages-cli": "mcp_zen_of_languages.cli:main",
        "mcp-zen-of-languages-server": "mcp_zen_of_languages.server:main",
        "zen": "mcp_zen_of_languages.cli:main",
        "zen-mcp-server": "mcp_zen_of_languages.__main__:main",
    }


def test_mcp_server_script_uses_server_entrypoint() -> None:
    scripts = _project_scripts()
    assert scripts["zen-mcp-server"] == "mcp_zen_of_languages.__main__:main"
    assert scripts["mcp-zen-of-languages"] == "mcp_zen_of_languages.__main__:main"
    assert scripts["mcp-zen-of-languages-server"] == "mcp_zen_of_languages.server:main"
    assert scripts["zen-mcp-server"] != scripts["zen"]
    assert scripts["mcp-zen-of-languages-cli"] == scripts["zen"]


def test_deprecated_cli_aliases_are_not_exposed() -> None:
    scripts = _project_scripts()
    assert "zen-of-languages" not in scripts
    assert "zen-cli" not in scripts
