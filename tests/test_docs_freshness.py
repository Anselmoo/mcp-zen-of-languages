"""Verify generated language docs are not stale.

Runs the generator in ``--check`` mode and asserts that every
``docs/user-guide/languages/*.md`` page matches the output produced
from the current ``rules.py`` and ``DETECTOR_MAP`` data.
"""

from __future__ import annotations

import subprocess
import sys


def test_language_docs_freshness() -> None:
    """Fail if any language doc page is stale relative to rules.py data."""
    result = subprocess.run(
        [sys.executable, "scripts/generate_language_docs.py", "--check"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stale = [
            line for line in result.stdout.splitlines() if line.startswith("STALE:")
        ]
        stale_list = "\n  ".join(stale) if stale else result.stdout
        msg = (
            f"Language docs are stale. Run:\n"
            f"  uv run python scripts/generate_language_docs.py\n\n"
            f"Stale files:\n  {stale_list}"
        )
        raise AssertionError(msg)
