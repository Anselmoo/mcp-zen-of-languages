from __future__ import annotations

import re
import tomllib

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

# Import name differs from the distribution name for these packages.
IMPORT_ALIASES = {
    "tree-sitter": "tree_sitter",
}


def _declared_runtime_packages() -> set[str]:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    names = set()
    for spec in data["project"]["dependencies"]:
        name = re.split(r"[<>=!\[ ]", spec, maxsplit=1)[0].strip()
        names.add(name.lower())
    return names


def _imported_modules() -> set[str]:
    pattern = re.compile(
        r"^\s*(?:from|import)\s+([A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE
    )
    modules = set()
    for path in SRC.rglob("*.py"):
        modules.update(pattern.findall(path.read_text(encoding="utf-8")))
    return modules


def test_every_declared_runtime_dependency_is_imported():
    imported = _imported_modules()
    unused = sorted(
        name
        for name in _declared_runtime_packages()
        if IMPORT_ALIASES.get(name, name.replace("-", "_")) not in imported
    )
    assert not unused, f"declared but never imported by src/: {unused}"
