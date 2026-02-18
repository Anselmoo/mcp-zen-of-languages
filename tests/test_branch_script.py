"""Tests for scripts/branch.py — BranchName, CommitTitle, and dry-run behaviour."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Import helpers from scripts/branch.py without executing main()
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
BRANCH_SCRIPT = ROOT / "scripts" / "branch.py"


def _import_branch():
    import importlib.util

    spec = importlib.util.spec_from_file_location("branch", BRANCH_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["branch"] = mod
    spec.loader.exec_module(mod)
    return mod


branch = _import_branch()
BranchName = branch.BranchName


# ---------------------------------------------------------------------------
# BranchName.slug()
# ---------------------------------------------------------------------------


class TestBranchNameSlug:
    def test_basic_feat(self):
        assert BranchName("feat", "add multi-language support").slug() == (
            "feat/add-multi-language-support"
        )

    def test_with_scope(self):
        assert BranchName("fix", "null pointer in parser", scope="python").slug() == (
            "fix/python-null-pointer-in-parser"
        )

    def test_lowercase(self):
        assert BranchName("docs", "Update README").slug() == "docs/update-readme"

    def test_special_chars_become_dashes(self):
        slug = BranchName("chore", "bump deps & update lock!").slug()
        assert "/" in slug
        assert "&" not in slug
        assert "!" not in slug

    def test_consecutive_specials_collapsed(self):
        slug = BranchName("feat", "a   b---c").slug()
        # multiple spaces/dashes should not produce double-dashes in output
        assert "--" not in slug

    def test_max_length(self):
        long_desc = "x" * 200
        slug_part = BranchName("feat", long_desc).slug().split("/", 1)[1]
        assert len(slug_part) <= 60

    def test_no_trailing_dash(self):
        # description that ends with a special char after truncation
        slug = BranchName("fix", "a" * 58 + "!!").slug()
        assert not slug.endswith("-")

    def test_all_types_produce_correct_prefix(self):
        for t in branch.CONVENTIONAL_TYPES:
            result = BranchName(t, "some thing").slug()
            assert result.startswith(f"{t}/"), f"Expected prefix {t}/ for type {t}"


# ---------------------------------------------------------------------------
# BranchName.commit_title()
# ---------------------------------------------------------------------------


class TestCommitTitle:
    def test_no_scope(self):
        assert BranchName("feat", "add cache").commit_title() == "feat: add cache"

    def test_with_scope(self):
        assert (
            BranchName("fix", "memory leak", scope="rust").commit_title()
            == "fix(rust): memory leak"
        )

    def test_docs_no_scope(self):
        assert BranchName("docs", "update API ref").commit_title() == "docs: update API ref"


# ---------------------------------------------------------------------------
# CLI smoke tests (dry-run, no git side-effects)
# ---------------------------------------------------------------------------


def _run_branch(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BRANCH_SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )


class TestNewCommandDryRun:
    def test_dry_run_exits_zero(self):
        result = _run_branch("new", "feat", "add something", "--dry-run")
        assert result.returncode == 0

    def test_dry_run_prints_branch_name(self):
        result = _run_branch("new", "feat", "add something", "--dry-run")
        assert "feat/add-something" in result.stdout

    def test_dry_run_prints_commit_title(self):
        result = _run_branch("new", "feat", "add something", "--dry-run")
        assert "feat: add something" in result.stdout

    def test_dry_run_with_scope(self):
        result = _run_branch("new", "fix", "crash on empty input", "--scope", "python", "--dry-run")
        assert "fix/python-crash-on-empty-input" in result.stdout
        assert "fix(python): crash on empty input" in result.stdout

    def test_dry_run_no_git_calls(self):
        result = _run_branch("new", "chore", "update deps", "--dry-run")
        assert "dry-run complete" in result.stdout

    def test_invalid_type_rejected(self):
        result = _run_branch("new", "invalid_type", "something", "--dry-run")
        assert result.returncode != 0


class TestRescueCommandDryRun:
    def test_dry_run_exits_zero(self):
        result = _run_branch("rescue", "feat", "oops committed to main", "--dry-run")
        assert result.returncode == 0

    def test_dry_run_prints_branch_name(self):
        result = _run_branch("rescue", "feat", "oops committed to main", "--dry-run")
        assert "feat/oops-committed-to-main" in result.stdout

    def test_dry_run_prints_reset_steps(self):
        result = _run_branch("rescue", "feat", "oops committed to main", "--dry-run")
        output = result.stdout
        assert "reset" in output.lower() or "dry-run" in output.lower()

    def test_dry_run_complete_marker(self):
        result = _run_branch("rescue", "feat", "my feature", "--dry-run")
        assert "dry-run complete" in result.stdout


class TestHelpText:
    def test_top_level_help(self):
        result = _run_branch("--help")
        assert result.returncode == 0
        assert "new" in result.stdout
        assert "rescue" in result.stdout

    def test_new_help(self):
        result = _run_branch("new", "--help")
        assert result.returncode == 0
        assert "--scope" in result.stdout
        assert "--dry-run" in result.stdout

    def test_rescue_help(self):
        result = _run_branch("rescue", "--help")
        assert result.returncode == 0
        assert "--since" in result.stdout
        assert "--dry-run" in result.stdout
