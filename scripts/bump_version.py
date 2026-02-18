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
    5. Update CHANGELOG.md  (git log since last tag, grouped by type)
    6. Run ``uv lock`` to refresh uv.lock
    7. ``git checkout -b release/v{new}``
    8. ``git add pyproject.toml uv.lock src/…/__init__.py CHANGELOG.md``
    9. ``git commit -m "chore: bump version to v{new}"``

Pass ``--no-commit``          to skip steps 8-9 (stage only).
Pass ``--dry-run``            to preview all changes without touching the filesystem or git.
Pass ``--no-changelog``       to skip step 5.
Pass ``--include-maintenance`` to include chore/ci/build/test entries in the changelog.
"""

from __future__ import annotations

import argparse
import datetime
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
CHANGELOG = ROOT / "CHANGELOG.md"

VERSION_RE = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)
INIT_VERSION_RE = re.compile(r'^(__version__\s*=\s*)"([^"]+)"', re.MULTILINE)

# Matches: feat(scope)!: description  OR  feat: description
_CONV_RE = re.compile(
    r"^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|deps)"
    r"(?:\((?P<scope>[^)]+)\))?"
    r"(?P<breaking>!)?"
    r"\s*:\s*(?P<desc>.+)$",
    re.IGNORECASE,
)

# Keep-a-Changelog section names per commit type
_SECTION_MAP: dict[str, str] = {
    "feat": "Added",
    "fix": "Fixed",
    "refactor": "Changed",
    "perf": "Changed",
    "style": "Changed",
    "docs": "Documentation",
    "chore": "Maintenance",
    "ci": "Maintenance",
    "build": "Maintenance",
    "test": "Maintenance",
    "deps": "Maintenance",
}

# Ordered display sections (Breaking Changes always first)
_SECTION_ORDER = [
    "Breaking Changes",
    "Added",
    "Fixed",
    "Changed",
    "Documentation",
    "Maintenance",
]


# ---------------------------------------------------------------------------
# Version helpers
# ---------------------------------------------------------------------------


@dataclass
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, s: str) -> Version:
        parts = s.strip().split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            msg = f"Invalid semver: {s!r}"
            raise ValueError(msg)
        return cls(int(parts[0]), int(parts[1]), int(parts[2]))

    def bump(self, kind: str) -> Version:
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
    if m := VERSION_RE.search(text):
        return Version.parse(m.group(1))
    msg = "Could not find version = '...' in pyproject.toml"
    raise RuntimeError(msg)


# ---------------------------------------------------------------------------
# File update helpers
# ---------------------------------------------------------------------------


def _update_pyproject(new: Version, *, dry_run: bool) -> None:
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


def _update_init(new: Version, *, dry_run: bool) -> None:
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
# Changelog helpers
# ---------------------------------------------------------------------------


@dataclass
class _ParsedCommit:
    sha: str
    type: str
    scope: str | None
    description: str
    breaking: bool = False


def _git_log_since_tag() -> list[tuple[str, str]]:
    """Return ``[(sha, subject), …]`` for commits since the most recent semver tag.

    Falls back to the full history when no tags exist.
    """
    # Find latest semver tag
    tag_result = subprocess.run(
        ["git", "tag", "--sort=-v:refname"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tags = [t.strip() for t in tag_result.stdout.splitlines() if t.strip()]
    ref = f"{tags[0]}..HEAD" if tags else "HEAD"

    log_result = subprocess.run(
        ["git", "log", ref, "--pretty=format:%H\t%s"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    pairs: list[tuple[str, str]] = []
    for line in log_result.stdout.splitlines():
        if "\t" in line:
            sha, subject = line.split("\t", 1)
            pairs.append((sha.strip(), subject.strip()))
    return pairs


def _parse_conventional_commit(sha: str, subject: str) -> _ParsedCommit | None:
    """Parse a conventional commit subject.  Returns *None* for skipped lines."""
    # Skip merge commits and release markers
    if subject.startswith("Merge ") or subject.lower().startswith("release:"):
        return None

    if m := _CONV_RE.match(subject):
        return _ParsedCommit(
            sha=sha,
            type=m.group("type").lower(),
            scope=m.group("scope"),
            description=m.group("desc").strip(),
            breaking=bool(m.group("breaking")),
        )
    return None


def _build_changelog_section(
    version: Version,
    commits: list[tuple[str, str]],
    *,
    include_maintenance: bool,
) -> str:
    """Render a Keep-a-Changelog ``## [version]`` block."""
    sections: dict[str, list[str]] = {s: [] for s in _SECTION_ORDER}

    for sha, subject in commits:
        parsed = _parse_conventional_commit(sha, subject)
        if parsed is None:
            continue
        section = (
            "Breaking Changes" if parsed.breaking else _SECTION_MAP.get(parsed.type)
        )
        if section is None:
            continue
        scope_part = f"**{parsed.scope}**: " if parsed.scope else ""
        entry = f"- {scope_part}{parsed.description}"
        sections[section].append(entry)

    today = datetime.datetime.now(datetime.UTC).date().isoformat()
    lines = [f"## [{version}] \u2013 {today}", ""]

    rendered_any = False
    for section_name in _SECTION_ORDER:
        entries = sections[section_name]
        if not entries:
            continue
        if section_name == "Maintenance" and not include_maintenance:
            continue
        lines.append(f"### {section_name}")
        lines.extend(entries)
        lines.append("")
        rendered_any = True

    if not rendered_any:
        lines.extend(("_No notable changes recorded._", ""))
    return "\n".join(lines)


def _update_changelog(
    new: Version,
    commits: list[tuple[str, str]],
    *,
    include_maintenance: bool,
    dry_run: bool,
) -> None:
    section = _build_changelog_section(new, commits, include_maintenance=include_maintenance)

    # Count visible entries for the summary line
    added = sum(
        bool((p := _parse_conventional_commit("", s)) and p.type == "feat")
        for _, s in commits
    )
    fixed = sum(
        bool((p := _parse_conventional_commit("", s)) and p.type == "fix")
        for _, s in commits
    )

    if dry_run:
        print(f"  [dry-run] Would prepend to {CHANGELOG.name}:")
        for ln in section.splitlines()[:8]:
            print(f"    {ln}")
        if len(section.splitlines()) > 8:
            print("    …")
        return

    existing = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else ""
    CHANGELOG.write_text(section + "\n" + existing, encoding="utf-8")

    summary_parts = []
    if added:
        summary_parts.append(f"Added: {added}")
    if fixed:
        summary_parts.append(f"Fixed: {fixed}")
    summary = ", ".join(summary_parts) if summary_parts else "no feat/fix entries"
    print(f"  ✓ {CHANGELOG.name}  →  ## [{new}]  ({summary})")


# ---------------------------------------------------------------------------
# Git / uv helpers
# ---------------------------------------------------------------------------


def _run(cmd: list[str], *, dry_run: bool, label: str) -> None:
    pretty = " ".join(cmd)
    if dry_run:
        print(f"  [dry-run] Would run: {pretty}")
        return
    print(f"  $ {pretty}")
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
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
        check=False,
    )
    return bool(result.stdout.strip())


def _current_branch() -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def _working_tree_clean() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
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
        "--no-changelog",
        action="store_true",
        help="Skip updating CHANGELOG.md.",
    )
    parser.add_argument(
        "--include-maintenance",
        action="store_true",
        help="Include chore/ci/build/test entries in the changelog.",
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
    _update_pyproject(new, dry_run=args.dry_run)
    _update_init(new, dry_run=args.dry_run)

    # 2a. Update changelog
    if not args.no_changelog:
        print("\n── Updating CHANGELOG.md ──────────────────────────────────────")
        commits = _git_log_since_tag()
        _update_changelog(new, commits, include_maintenance=args.include_maintenance, dry_run=args.dry_run)

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
    if not args.no_changelog and CHANGELOG.exists():
        files_to_stage.append(str(CHANGELOG.relative_to(ROOT)))
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
