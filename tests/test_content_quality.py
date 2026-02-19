"""Verify content quality checks stay passing as docs evolve.

Runs the content quality gate script and asserts it exits cleanly,
ensuring that required headings, snippets, and generated markers remain
intact in high-traffic documentation pages.
"""

from __future__ import annotations

import subprocess
import sys


def test_content_quality_checks() -> None:
    """Fail if content quality gate detects missing headings/snippets/markers."""
    result = subprocess.run(
        [sys.executable, "scripts/check_content_quality.py"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        msg = (
            f"Content quality checks failed. Fix the reported issues:\n\n"
            f"{result.stdout}\n{result.stderr}"
        )
        raise AssertionError(msg)
