"""Conventional commits branch helper.

Usage::

    uv run python scripts/branch.py new feat "add multi-language support"
    # → branch:  feat/add-multi-language-support
    # → title:   feat: add multi-language support

    uv run python scripts/branch.py new fix "null pointer in parser" --scope python
    # → branch:  fix/python-null-pointer-in-parser
    # → title:   fix(python): null pointer in parser

    uv run python scripts/branch.py new feat "my feature" --dry-run

    uv run python scripts/branch.py rescue feat "add multi-language support"
    # 1. Detects commits on current branch ahead of origin/<branch>
    # 2. Creates feat/add-multi-language-support at current HEAD
    # 3. Resets the original branch back to origin/<branch>
    # 4. Switches to the new rescue branch

    uv run python scripts/branch.py rescue fix "urgent crash fix" --since abc1234
    # Rescue commits from abc1234..HEAD regardless of remote state

Supported types: feat, fix, chore, docs, refactor, test, ci, perf, style, build
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CONVENTIONAL_TYPES = (
    "feat",
    "fix",
    "chore",
    "docs",
    "refactor",
    "test",
    "ci",
    "perf",
    "style",
    "build",
)

# Max length for the slug portion after "type/" (branch name limit safety)
_SLUG_MAX = 60


# ---------------------------------------------------------------------------
# Naming helpers
# ---------------------------------------------------------------------------


@dataclass
class BranchName:
    """Builds a conventional-commits-aligned git branch name."""

    type: str
    description: str
    scope: str | None = None

    def slug(self) -> str:
        """Return the full branch name, e.g. ``feat/python-add-inference``."""
        raw = f"{self.scope}-{self.description}" if self.scope else self.description
        slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
        slug = slug[:_SLUG_MAX].rstrip("-")
        return f"{self.type}/{slug}"

    def commit_title(self) -> str:
        """Return a conventional commit title, e.g. ``feat(python): add inference``."""
        scope_part = f"({self.scope})" if self.scope else ""
        return f"{self.type}{scope_part}: {self.description}"


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _run(cmd: list[str], dry_run: bool, label: str) -> str:
    pretty = " ".join(cmd)
    if dry_run:
        print(f"  [dry-run] Would run: {pretty}")
        return ""
    print(f"  $ {pretty}")
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        msg = f"{label} failed (exit {result.returncode})"
        raise RuntimeError(msg)
    if result.stdout.strip():
        print(result.stdout.strip())
    return result.stdout.strip()


def _capture(cmd: list[str]) -> str:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True).stdout.strip()


def _branch_exists(branch: str) -> bool:
    return bool(_capture(["git", "branch", "--list", branch]))


def _current_branch() -> str:
    return _capture(["git", "branch", "--show-current"])


def _working_tree_clean() -> bool:
    return _capture(["git", "status", "--porcelain"]) == ""


def _commits_ahead(base_ref: str) -> list[str]:
    """Return short log lines for commits on HEAD not in *base_ref*."""
    out = _capture(["git", "log", f"{base_ref}..HEAD", "--pretty=format:%h %s"])
    return [line for line in out.splitlines() if line]


# ---------------------------------------------------------------------------
# `new` subcommand
# ---------------------------------------------------------------------------


def cmd_new(args: argparse.Namespace) -> None:
    branch = BranchName(type=args.type, description=args.description, scope=args.scope)
    branch_name = branch.slug()
    commit_title = branch.commit_title()

    base = _current_branch() if not args.dry_run else "<current>"
    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}New branch from '{base}'")
    print(f"  Branch : {branch_name}")
    print(f"  Title  : {commit_title}\n")

    if not args.dry_run:
        if not _working_tree_clean():
            print(
                "⚠  Working tree has uncommitted changes.\n"
                "   Commit or stash them first, or use --dry-run to preview.",
                file=sys.stderr,
            )
            sys.exit(1)
        if _branch_exists(branch_name):
            print(
                f"⚠  Branch '{branch_name}' already exists.\n"
                "   Delete it first or choose a different description.",
                file=sys.stderr,
            )
            sys.exit(1)

    print("── Creating branch ───────────────────────────────────────────────")
    _run(
        ["git", "checkout", "-b", branch_name],
        dry_run=args.dry_run,
        label="git checkout -b",
    )

    print(f"\n✅ Done!  Suggested commit title:\n\n    {commit_title}\n")
    if args.dry_run:
        print("[dry-run complete — no changes made]")


# ---------------------------------------------------------------------------
# `rescue` subcommand
# ---------------------------------------------------------------------------


def cmd_rescue(args: argparse.Namespace) -> None:
    branch = BranchName(type=args.type, description=args.description, scope=args.scope)
    branch_name = branch.slug()
    commit_title = branch.commit_title()

    origin_branch = _current_branch() if not args.dry_run else "main"

    print(
        f"\n{'[DRY RUN] ' if args.dry_run else ''}"
        f"Rescue commits from '{origin_branch}' → '{branch_name}'\n"
    )

    # Determine commits to rescue and the reset target
    if args.since:
        log_lines = _commits_ahead(args.since)
        reset_target = args.since
    else:
        remote_ref = f"origin/{origin_branch}"
        log_lines = _commits_ahead(remote_ref)
        reset_target = remote_ref

    if not log_lines and not args.dry_run:
        ref_label = args.since or f"origin/{origin_branch}"
        print(
            f"⚠  No commits found ahead of '{ref_label}'.\n"
            "   Nothing to rescue. Use --since <sha> to specify a starting point.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("── Commits to rescue ─────────────────────────────────────────────")
    if log_lines:
        for line in log_lines:
            print(f"  {line}")
    else:
        print(f"  [dry-run] Would detect commits ahead of origin/{origin_branch}")

    if not args.dry_run and _branch_exists(branch_name):
        print(
            f"⚠  Branch '{branch_name}' already exists.\n"
            "   Delete it first or choose a different description.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 1. Create new branch at current HEAD (all rescued commits included)
    print("\n── Creating rescue branch ────────────────────────────────────────")
    _run(
        ["git", "checkout", "-b", branch_name],
        dry_run=args.dry_run,
        label="git checkout -b rescue",
    )

    # 2. Go back to origin branch and reset it to remote state
    print("\n── Resetting origin branch ───────────────────────────────────────")
    _run(
        ["git", "checkout", origin_branch],
        dry_run=args.dry_run,
        label=f"git checkout {origin_branch}",
    )
    _run(
        ["git", "reset", "--hard", reset_target],
        dry_run=args.dry_run,
        label="git reset --hard",
    )

    # 3. Switch back to the rescue branch
    print("\n── Switching to rescue branch ────────────────────────────────────")
    _run(
        ["git", "checkout", branch_name],
        dry_run=args.dry_run,
        label="git checkout rescue",
    )

    n = len(log_lines)
    print(
        f"\n✅ Done!  {n} commit(s) rescued into '{branch_name}'.\n"
        f"   '{origin_branch}' has been reset to '{reset_target}'.\n"
        f"   Suggested commit title (for future work):\n\n    {commit_title}\n"
    )
    if args.dry_run:
        print("[dry-run complete — no changes made]")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Conventional commits branch helper.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ---- new ----------------------------------------------------------------
    new_p = sub.add_parser(
        "new",
        help="Create a new conventionally-named branch from the current HEAD.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    new_p.add_argument(
        "type",
        choices=CONVENTIONAL_TYPES,
        help="Conventional commit type (feat, fix, chore, …).",
    )
    new_p.add_argument(
        "description",
        help="Short description — becomes the branch slug.",
    )
    new_p.add_argument(
        "--scope",
        metavar="SCOPE",
        default=None,
        help="Optional scope, e.g. --scope python → fix(python)/…",
    )
    new_p.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview branch name and commit title without touching git.",
    )
    new_p.set_defaults(func=cmd_new)

    # ---- rescue -------------------------------------------------------------
    rescue_p = sub.add_parser(
        "rescue",
        help="Move commits from the current branch to a new one and reset the origin branch.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    rescue_p.add_argument(
        "type",
        choices=CONVENTIONAL_TYPES,
        help="Conventional commit type for the rescue branch.",
    )
    rescue_p.add_argument(
        "description",
        help="Short description for the rescue branch.",
    )
    rescue_p.add_argument(
        "--scope",
        metavar="SCOPE",
        default=None,
        help="Optional scope.",
    )
    rescue_p.add_argument(
        "--since",
        metavar="SHA",
        default=None,
        help="Rescue commits since this SHA (default: commits ahead of origin/<branch>).",
    )
    rescue_p.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview all steps without touching git.",
    )
    rescue_p.set_defaults(func=cmd_rescue)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
