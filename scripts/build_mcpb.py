"""Build the .mcpb release bundle for mcp-zen-of-languages.

Creates dist/mcp-zen-of-languages-{version}.mcpb, a ZIP archive containing
a manifest.json conforming to the DXT spec v0.4, plus pyproject.toml as
the uv entry_point.
"""

from __future__ import annotations

import json
import tomllib
import zipfile

from pathlib import Path


def _read_version(root: Path) -> str:
    with (root / "pyproject.toml").open("rb") as fh:
        data = tomllib.load(fh)
    return data["project"]["version"]


def _build_manifest(version: str) -> dict:
    return {
        "manifest_version": "0.4",
        "name": "mcp-zen-of-languages",
        "display_name": "MCP Zen of Languages",
        "version": version,
        "description": (
            "Multi-language architectural and idiomatic code analysis "
            "via the Model Context Protocol."
        ),
        "author": {
            "name": "Anselm Hahn",
            "email": "Anselm.Hahn@gmail.com",
            "url": "https://github.com/Anselmoo/mcp-zen-of-languages",
        },
        "repository": {
            "type": "git",
            "url": "https://github.com/Anselmoo/mcp-zen-of-languages",
        },
        "documentation": (
            "https://anselmoo.github.io/mcp-zen-of-languages/"
            "getting-started/installation/"
        ),
        "license": "MIT",
        "keywords": [
            "mcp",
            "code-analysis",
            "zen",
            "refactoring",
            "architecture",
        ],
        "server": {
            "type": "uv",
            "entry_point": "pyproject.toml",
            "mcp_config": {
                "command": "uvx",
                "args": [
                    "--from",
                    f"mcp-zen-of-languages=={version}",
                    "mcp-zen-of-languages-server",
                ],
            },
        },
        "tools_generated": True,
        "compatibility": {
            "claude_desktop": ">=0.10.0",
            "platforms": ["darwin", "win32", "linux"],
            "runtimes": {"python": ">=3.12"},
        },
    }


def main() -> None:
    root = Path(__file__).parent.parent
    version = _read_version(root)
    manifest = _build_manifest(version)

    dist = root / "dist"
    dist.mkdir(exist_ok=True)

    mcpb_path = dist / f"mcp-zen-of-languages-{version}.mcpb"
    with zipfile.ZipFile(mcpb_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        zf.write(root / "pyproject.toml", "pyproject.toml")

    print(f"Built {mcpb_path}")


if __name__ == "__main__":
    main()
