"""Assert that tools pinned in more than one place all name the same version.

Several tools in this repository are pinned independently in places CI runs
separately:

* ``.pre-commit-config.yaml`` ``rev:`` — the version the pre-commit hook runs.
* ``uv.lock`` — the version ``uv run <tool>`` resolves.
* ``.github/workflows/*.yml`` ``uses:`` — the version the CI action runs.

When those drift apart, the same check runs twice against the same source with
two different binaries and can disagree. That is exactly how ruff ended up
pinned at ``v0.15.15`` by the hook while ``uv.lock`` resolved ``0.15.18``.

Only *exact* pins are compared. The ``[dependency-groups]`` specifiers in
``pyproject.toml`` are deliberately excluded: those are floors, and the lock is
expected to drift ahead of them.
"""

from __future__ import annotations

import re
import sys
import tomllib

from pathlib import Path
from typing import NamedTuple

import yaml


class Tool(NamedTuple):
    """Where one tool's version is pinned across the repository."""

    pre_commit_repo: str
    lock_package: str
    action_repo: str | None


# Tools pinned in more than one place. A tool pinned once cannot disagree with
# itself, so adding one here is only useful when it has two or more sources.
TOOLS = {
    "ruff": Tool(
        pre_commit_repo="https://github.com/astral-sh/ruff-pre-commit",
        lock_package="ruff",
        action_repo=None,
    ),
    "repo-release-tools": Tool(
        pre_commit_repo="https://github.com/Anselmoo/repo-release-tools",
        lock_package="repo-release-tools",
        action_repo="Anselmoo/repo-release-tools",
    ),
}

PRE_COMMIT_CONFIG = Path(".pre-commit-config.yaml")
UV_LOCK = Path("uv.lock")
WORKFLOWS_DIR = Path(".github/workflows")


def _normalise(version: str) -> str:
    """Strip a leading ``v`` tag prefix so ``v1.2.3`` and ``1.2.3`` compare equal."""
    return version.removeprefix("v")


def _pre_commit_revs(root: Path) -> dict[str, str]:
    """Map each pinned pre-commit repo URL to its ``rev``."""
    data = yaml.safe_load((root / PRE_COMMIT_CONFIG).read_text(encoding="utf-8"))
    return {
        repo["repo"].rstrip("/"): _normalise(str(repo["rev"]))
        for repo in data.get("repos", [])
        if repo.get("repo") != "local" and "rev" in repo
    }


def _lock_versions(root: Path) -> dict[str, str]:
    """Map each locked package name to its resolved version."""
    data = tomllib.loads((root / UV_LOCK).read_text(encoding="utf-8"))
    return {
        package["name"]: _normalise(str(package["version"]))
        for package in data.get("package", [])
        if "name" in package and "version" in package
    }


def _action_refs(root: Path) -> dict[str, str]:
    """Map each ``owner/repo`` used by a workflow to the ref it is pinned at."""
    refs: dict[str, str] = {}
    workflows = root / WORKFLOWS_DIR
    if not workflows.is_dir():
        return refs
    pattern = re.compile(r"uses:\s*([\w.-]+/[\w.-]+)@(\S+)")
    for workflow in sorted(workflows.glob("*.y*ml")):
        for repo, ref in pattern.findall(workflow.read_text(encoding="utf-8")):
            refs.setdefault(repo, _normalise(ref))
    return refs


def collect_versions(root: Path) -> dict[str, dict[str, str]]:
    """Collect every pinned version per tool, keyed by where it was found."""
    revs = _pre_commit_revs(root)
    locked = _lock_versions(root)
    actions = _action_refs(root)

    collected: dict[str, dict[str, str]] = {}
    for name, tool in TOOLS.items():
        sources: dict[str, str] = {}
        if (rev := revs.get(tool.pre_commit_repo.rstrip("/"))) is not None:
            sources["pre-commit rev"] = rev
        if (version := locked.get(tool.lock_package)) is not None:
            sources["uv.lock"] = version
        if tool.action_repo and (ref := actions.get(tool.action_repo)) is not None:
            sources["CI action"] = ref
        if sources:
            collected[name] = sources
    return collected


def _disagreements(
    collected: dict[str, dict[str, str]],
) -> list[tuple[str, dict[str, str]]]:
    """Return the tools whose sources do not all name the same version."""
    return [
        (name, sources)
        for name, sources in sorted(collected.items())
        if len(set(sources.values())) > 1
    ]


def main() -> int:
    """Report any tool pinned at two different versions. Returns an exit code."""
    root = Path(__file__).resolve().parents[1]
    collected = collect_versions(root)

    if not (disagreements := _disagreements(collected)):
        print(f"✓ All {len(collected)} multi-pinned tool(s) agree on a version")
        for name, sources in sorted(collected.items()):
            print(f"  - {name} {next(iter(sources.values()))} ({len(sources)} pins)")
        return 0

    print(f"Found {len(disagreements)} tool(s) pinned at disagreeing versions:")
    for name, sources in disagreements:
        print(f"  - {name}:")
        for source, version in sources.items():
            print(f"      {source:<16} {version}")
    print("\nEvery pin for a tool must name the same version, so the hook, the")
    print("lockfile, and CI all run the same binary. Update whichever is stale.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
