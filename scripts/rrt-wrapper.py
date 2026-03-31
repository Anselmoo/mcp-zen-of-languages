#!/usr/bin/env python3
"""Wrapper to run rrt (repo-release-tools) if available, else fall back to uvx rrt.

Usage: scripts/rrt-wrapper.py <args...>
This allows POE tasks to invoke "rrt ..." via the wrapper while supporting
contributors who use uvx without installing the package globally.
"""

from __future__ import annotations

import shutil
import subprocess
import sys


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])

    # Prefer system 'rrt' if available
    cmd = ["rrt", *argv] if shutil.which("rrt") else ["uvx", "rrt", *argv]

    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        print(
            "Neither 'rrt' nor 'uvx' found. Install repo-release-tools (Python 3.12+) or use uvx.",
            file=sys.stderr,
        )
        return 127


if __name__ == "__main__":
    raise SystemExit(main())
