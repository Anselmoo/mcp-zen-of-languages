"""Integration tests for scripts/branch.py with uncommitted changes."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import uuid

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
BRANCH_SCRIPT = ROOT / "scripts" / "branch.py"

GIT: str = shutil.which("git") or "git"


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

        # Configure git user
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


class TestBranchCreationWithUncommittedChanges:
    """Test that uncommitted changes are migrated to new branch."""

    def test_branch_creation_succeeds_with_changes(self, temp_git_repo):
        """Branch should be created even with uncommitted changes."""
        repo = temp_git_repo
        unique_id = str(uuid.uuid4())[:8]

        # Create an uncommitted change
        (repo / "test.txt").write_text("Uncommitted change\n")

        # Run branch command with unique name
        result = _run_branch_in_repo(repo, "new", "feat", f"feature-{unique_id}")

        # Should succeed (no longer blocks)
        assert result.returncode == 0, f"stderr: {result.stderr}"

    def test_migration_message_shown_with_changes(self, temp_git_repo):
        """Migration message should appear when changes exist."""
        repo = temp_git_repo
        unique_id = str(uuid.uuid4())[:8]

        # Create an uncommitted change
        (repo / "file.txt").write_text("Change\n")

        # Run branch command
        result = _run_branch_in_repo(repo, "new", "feat", f"branch-{unique_id}")

        # Should show migration notification
        assert "Uncommitted changes migrated" in result.stdout
