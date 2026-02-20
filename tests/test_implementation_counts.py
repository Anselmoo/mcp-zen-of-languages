"""Verify generated implementation counts stay in sync with docs surfaces."""

from __future__ import annotations

import subprocess
import sys


def test_implementation_counts_checks() -> None:
    """Fail if generated implementation-count artifacts or surfaces are stale."""
    result = subprocess.run(  # noqa: S603
        [sys.executable, "scripts/generate_implementation_counts.py", "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        msg = (
            "Implementation count checks failed. Run:\n"
            "  uv run python scripts/generate_implementation_counts.py\n\n"
            f"{result.stdout}\n{result.stderr}"
        )
        raise AssertionError(msg)
