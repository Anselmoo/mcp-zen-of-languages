"""Smoke test: ensure scripts/check_content_quality.py exits 0.

Catches accidental doc edits that would break the pre-commit / Poe quality gate
before contributors hit the failure locally.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_content_quality_check_passes() -> None:
    """scripts/check_content_quality.py must exit 0 against the current docs."""
    result = subprocess.run(
        [sys.executable, "scripts/check_content_quality.py"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )
    if result.returncode != 0:
        msg = (
            "Content quality checks failed.\n"
            "Run: uv run python scripts/check_content_quality.py\n\n"
            f"Output:\n{result.stdout}{result.stderr}"
        )
        raise AssertionError(msg)
