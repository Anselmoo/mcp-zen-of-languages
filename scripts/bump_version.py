"""Bump the project version, update uv.lock, and create a release branch.

Usage::

    uv run python scripts/bump_version.py patch          # 0.1.0 → 0.1.1
    uv run python scripts/bump_version.py minor          # 0.1.0 → 0.2.0
    uv run python scripts/bump_version.py major          # 0.1.0 → 1.0.0
    uv run python scripts/bump_version.py 1.2.3          # explicit version
    uv run python scripts/bump_version.py patch --dry-run  # preview only

Steps performed:
    1. Parse current version from pyproject.toml
    2. Compute new version
    3. Update pyproject.toml  [version = "…"]
    4. Update src/…/__init__.py  [__version__ = "…"]
    5. Run ``uv lock`` to refresh uv.lock
    6. ``git checkout -b release/v{new}``
    7. ``git add pyproject.toml uv.lock src/…/__init__.py``
    8. ``git commit -m "chore: bump version to v{new}"``

Pass ``--no-commit`` to skip steps 7-8 (stage only).
Pass ``--dry-run``  to preview all changes without touching the filesystem or git.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
INIT_FILE = ROOT / "src" / "mcp_zen_of_languages" / "__init__.py"

VERSION_RE = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)
INIT_VERSION_RE = re.compile(r'^(__version__\s*=\s*)"([^"]+)"', re.MULTILINE)


# ---------------------------------------------------------------------------
# Version helpers
# ---------------------------------------------------------------------------


@dataclass
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, s: str) -> "Version":
        parts = s.strip().split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            msg = f"Invalid semver: {s!r}"
            raise ValueError(msg)
        return cls(int(parts[0]), int(parts[1]), int(parts[2]))

    def bump(self, kind: str) -> "Version":
        if kind == "major":
            return Version(self.major + 1, 0, 0)
        if kind == "minor":
            return Version(self.major, self.minor + 1, 0)
        if kind == "patch":
            return Version(self.major, self.minor, self.patch + 1)
        msg = f"Unknown bump kind: {kind!r}"
        raise ValueError(msg)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def _read_current_version() -> Version:
    text = PYPROJECT.read_text(encoding="utf-8")
    m = VERSION_RE.search(text)
    if not m:
        msg = 'Could not find version = "..." in pyproject.toml'
        raise RuntimeError(msg)
    return Version.parse(m.group(1))


# ---------------------------------------------------------------------------
# File update helpers
# ---------------------------------------------------------------------------


def _update_pyproject(new: Version, dry_run: bool) -> None:
    text = PYPROJECT.read_text(encoding="utf-8")
    updated = VERSION_RE.sub(f'version = "{new}"', text, count=1)
    if text == updated:
        msg = "pyproject.toml version replacement had no effect"
        raise RuntimeError(msg)
    if dry_run:
        print(
            f'  [dry-run] Would update {PYPROJECT.relative_to(ROOT)}: version = "{new}"'
        )
    else:
        PYPROJECT.write_text(updated, encoding="utf-8")
        print(f'  ✓ {PYPROJECT.relative_to(ROOT)}  →  version = "{new}"')


def _update_init(new: Version, dry_run: bool) -> None:
    if not INIT_FILE.exists():
        print(f"  ⚠ {INIT_FILE.relative_to(ROOT)} not found — skipping")
        return
    text = INIT_FILE.read_text(encoding="utf-8")
    updated = INIT_VERSION_RE.sub(rf'\g<1>"{new}"', text, count=1)
    if text == updated:
        print(
            f"  ⚠ No __version__ pattern found in {INIT_FILE.relative_to(ROOT)} — skipping"
        )
        return
    if dry_run:
        print(
            f'  [dry-run] Would update {INIT_FILE.relative_to(ROOT)}: __version__ = "{new}"'
        )
    else:
        INIT_FILE.write_text(updated, encoding="utf-8")
        print(f'  ✓ {INIT_FILE.relative_to(ROOT)}  →  __version__ = "{new}"')


# ---------------------------------------------------------------------------
# Git / uv helpers
# ---------------------------------------------------------------------------


def _run(cmd: list[str], dry_run: bool, label: str) -> None:
    pretty = " ".join(cmd)
    if dry_run:
        print(f"  [dry-run] Would run: {pretty}")
        return
    print(f"  $ {pretty}")
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        msg = f"{label} failed (exit {result.returncode})"
        raise RuntimeError(msg)
    if result.stdout.strip():
        print(result.stdout.strip())


def _branch_exists(branch: str) -> bool:
    result = subprocess.run(
        ["git", "branch", "--list", branch],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def _current_branch() -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _working_tree_clean() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() == ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bump version, refresh uv.lock, and create a release branch.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "bump",
        metavar="BUMP",
        help="Bump kind: major | minor | patch, or an explicit semver like 1.2.3",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview all changes without writing files or running git commands.",
    )
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="Stage changed files but skip the git commit.",
    )
    parser.add_argument(
        "--base-branch",
        default=None,
        metavar="BRANCH",
        help="Branch to create the release branch from (default: current branch).",
    )
    args = parser.parse_args()

    # --- Compute versions ---
    current = _read_current_version()
    if args.bump in ("major", "minor", "patch"):
        new = current.bump(args.bump)
    else:
        try:
            new = Version.parse(args.bump)
        except ValueError as exc:
            parser.error(str(exc))

    branch_name = f"release/v{new}"

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Version bump: {current}  →  {new}")
    print(f"Target branch: {branch_name}\n")

    # --- Safety checks ---
    if not args.dry_run:
        if not _working_tree_clean():
            print(
                "⚠  Working tree has uncommitted changes.\n"
                "   Commit or stash them before bumping, or use --dry-run to preview.",
                file=sys.stderr,
            )
            sys.exit(1)
        if _branch_exists(branch_name):
            print(
                f"⚠  Branch '{branch_name}' already exists.\n"
                "   Delete it first or choose a different version.",
                file=sys.stderr,
            )
            sys.exit(1)

    # --- Base branch ---
    base = args.base_branch or _current_branch()
    if not args.dry_run and _current_branch() != base:
        _run(["git", "checkout", base], dry_run=False, label="git checkout base")

    # 1. Update files
    print("── Updating version strings ──────────────────────────────────")
    _update_pyproject(new, args.dry_run)
    _update_init(new, args.dry_run)

    # 2. Refresh lockfile
    print("\n── Refreshing uv.lock ───────────────────────────────────────")
    _run(["uv", "lock"], dry_run=args.dry_run, label="uv lock")

    # 3. Create branch
    print("\n── Git ───────────────────────────────────────────────────────")
    _run(
        ["git", "checkout", "-b", branch_name],
        dry_run=args.dry_run,
        label="git checkout -b",
    )

    # 4. Stage
    files_to_stage = [
        str(PYPROJECT.relative_to(ROOT)),
        "uv.lock",
        str(INIT_FILE.relative_to(ROOT)),
    ]
    _run(["git", "add", *files_to_stage], dry_run=args.dry_run, label="git add")

    # 5. Commit (unless --no-commit)
    if not args.no_commit:
        commit_msg = f"chore: bump version to v{new}"
        _run(
            ["git", "commit", "-m", commit_msg],
            dry_run=args.dry_run,
            label="git commit",
        )
        print(f"\n✅ Done!  Branch '{branch_name}' created with commit: {commit_msg!r}")
    else:
        print(f"\n✅ Done (no commit)!  Branch '{branch_name}' created, files staged.")

    if args.dry_run:
        print("\n[dry-run complete — no files were modified]")


if __name__ == "__main__":
    main()
