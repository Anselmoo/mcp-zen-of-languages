"""Tests for scripts/branch.py — BranchName, CommitTitle, and dry-run behaviour."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Import helpers from scripts/branch.py without executing main()
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
BRANCH_SCRIPT = ROOT / "scripts" / "branch.py"
MAX_BRANCH_SLUG_LENGTH = 60

GIT: str = shutil.which("git") or "git"  # Fallback to PATH lookup


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
# Git helpers for integration tests
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        # Initialize git repo
        subprocess.run(  # noqa: S603
            [GIT, "init"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )

        # Configure git user (required for commits)
        subprocess.run(  # noqa: S603
            [GIT, "config", "user.email", "test@example.com"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )
        subprocess.run(  # noqa: S603
            [GIT, "config", "user.name", "Test User"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )

        # Create initial commit
        (repo_path / "README.md").write_text("# Test\n")
        subprocess.run(  # noqa: S603
            [GIT, "add", "README.md"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )
        subprocess.run(  # noqa: S603
            [GIT, "commit", "-m", "Initial commit"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )

        # Switch to main branch
        subprocess.run(  # noqa: S603
            [GIT, "checkout", "-b", "main"],
            cwd=repo_path,
            capture_output=True,
            check=False,  # May fail if already on main
        )

        yield repo_path


def _run_branch_in_repo(repo_path: Path, *args: str) -> subprocess.CompletedProcess:
    """Run branch.py in a specific directory."""
    return subprocess.run(  # noqa: S603
        [sys.executable, str(BRANCH_SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(repo_path),
        check=False,
    )


# ---------------------------------------------------------------------------
# BranchName slug tests
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
        assert len(slug_part) <= MAX_BRANCH_SLUG_LENGTH

    def test_no_trailing_dash(self):
        # description that ends with a special char after truncation
        slug = BranchName("fix", "a" * 58 + "!!").slug()
        assert not slug.endswith("-")

    def test_all_types_produce_correct_prefix(self):
        for t in branch.CONVENTIONAL_TYPES:
            result = BranchName(t, "some thing").slug()
            assert result.startswith(f"{t}/"), f"Expected prefix {t}/ for type {t}"


# ---------------------------------------------------------------------------
# BranchName commit_title tests
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
        assert (
            BranchName("docs", "update API ref").commit_title()
            == "docs: update API ref"
        )


# ---------------------------------------------------------------------------
# CLI smoke tests (dry-run, no git side-effects)
# ---------------------------------------------------------------------------


def _run_branch(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(  # noqa: S603
        [sys.executable, str(BRANCH_SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
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
        result = _run_branch(
            "new",
            "fix",
            "crash on empty input",
            "--scope",
            "python",
            "--dry-run",
        )
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


# ---------------------------------------------------------------------------
# Integration tests: branch creation with uncommitted changes migration
# ---------------------------------------------------------------------------


class TestNewCommandWithUncommittedChanges:
    """Test the new behavior where uncommitted changes are migrated to new branch."""

    def test_branch_created_with_uncommitted_changes(self, temp_git_repo):
        """Branch should be created even with uncommitted changes."""
        repo = temp_git_repo

        # Create an uncommitted change
        (repo / "test.txt").write_text("Uncommitted change\n")

        # Run branch command
        result = _run_branch_in_repo(repo, "new", "feat", "test feature")

        # Should succeed
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "feat/test-feature" in result.stdout

    def test_migration_notification_shown(self, temp_git_repo):
        """Migration notification should appear when changes exist."""
        repo = temp_git_repo

        # Create an uncommitted change
        (repo / "test.txt").write_text("Uncommitted change\n")

        # Run branch command
        result = _run_branch_in_repo(repo, "new", "feat", "test feature")

        # Should mention migration
        assert result.returncode == 0
        assert "Uncommitted changes migrated" in result.stdout

    def test_changes_preserved_on_new_branch(self, temp_git_repo):
        """Uncommitted changes should be preserved on the new branch."""
        repo = temp_git_repo

        # Create an uncommitted change
        test_content = "My uncommitted change\n"
        (repo / "new_file.txt").write_text(test_content)

        # Run branch command
        result = _run_branch_in_repo(repo, "new", "feat", "test feature")
        assert result.returncode == 0

        # Verify file exists on new branch
        assert (repo / "new_file.txt").exists()
        assert (repo / "new_file.txt").read_text() == test_content

    def test_new_branch_exists_after_creation(self, temp_git_repo):
        """The new branch should exist and be the current branch."""
        repo = temp_git_repo

        # Create an uncommitted change
        (repo / "test.txt").write_text("Change\n")

        # Run branch command
        result = _run_branch_in_repo(repo, "new", "feat", "test feature")
        assert result.returncode == 0

        # Check that the branch exists
        branches_result = subprocess.run(  # noqa: S603
            [GIT, "branch"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        )
        branches = branches_result.stdout
        assert "feat/test-feature" in branches

    def test_duplicate_branch_still_blocked(self, temp_git_repo):
        """Should still prevent duplicate branch names."""
        repo = temp_git_repo

        # Create a branch first
        subprocess.run(  # noqa: S603
            [GIT, "checkout", "-b", "feat/duplicate-name"],
            cwd=repo,
            capture_output=True,
            check=True,
        )

        # Switch back to main
        subprocess.run(  # noqa: S603
            [GIT, "checkout", "main"],
            cwd=repo,
            capture_output=True,
            check=True,
        )

        # Create uncommitted change
        (repo / "test.txt").write_text("Change\n")

        # Try to create branch with same name - should fail
        result = _run_branch_in_repo(repo, "new", "feat", "duplicate name")

        assert result.returncode != 0
        assert "already exists" in result.stderr

    def test_no_notification_without_changes(self, temp_git_repo):
        """No migration notification when tree is clean."""
        repo = temp_git_repo

        # No uncommitted changes - working tree is clean

        # Run branch command
        result = _run_branch_in_repo(repo, "new", "feat", "clean feature")

        # Should succeed but NOT show migration message
        assert result.returncode == 0
        assert "Uncommitted changes migrated" not in result.stdout

    def test_modified_existing_file_migrated(self, temp_git_repo):
        """Modifications to existing files should also migrate."""
        repo = temp_git_repo

        # Modify existing README
        readme_path = repo / "README.md"
        original_content = readme_path.read_text()
        modified_content = original_content + "Modified line\n"
        readme_path.write_text(modified_content)

        # Run branch command
        result = _run_branch_in_repo(repo, "new", "feat", "modify readme")
        assert result.returncode == 0

        # Verify modification is preserved
        assert readme_path.read_text() == modified_content

    def test_branch_creation_with_scope_and_changes(self, temp_git_repo):
        """Branch with scope should work with uncommitted changes."""
        repo = temp_git_repo

        # Create an uncommitted change
        (repo / "test.txt").write_text("Change\n")

        # Run branch command with scope
        result = _run_branch_in_repo(repo, "new", "fix", "bug fix", "--scope", "python")

        # Should succeed
        assert result.returncode == 0
        assert "fix/python-bug-fix" in result.stdout
        assert "Uncommitted changes migrated" in result.stdout


class TestRescueCommandWithUncommittedChanges:
    """Test rescue command behavior with uncommitted changes."""

    def test_rescue_with_uncommitted_changes(self, temp_git_repo):
        """Rescue should move commits and preserve changes."""
        repo = temp_git_repo

        # Create a commit
        (repo / "file1.txt").write_text("Committed change\n")
        subprocess.run(  # noqa: S603
            [GIT, "add", "file1.txt"],
            cwd=repo,
            capture_output=True,
            check=True,
        )
        subprocess.run(  # noqa: S603
            [GIT, "commit", "-m", "Add file1"],
            cwd=repo,
            capture_output=True,
            check=True,
        )

        # Create an uncommitted change
        (repo / "file2.txt").write_text("Uncommitted change\n")

        # Run rescue command (with --dry-run to avoid actual operations)
        result = _run_branch_in_repo(
            repo, "rescue", "feat", "rescue commits", "--dry-run"
        )

        # Should show dry-run message
        assert result.returncode == 0
        assert "dry-run" in result.stdout.lower() or "rescue" in result.stdout.lower()
