"""Pre-commit hook: block Sphinx role markup in Python source docstrings."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SRC_ROOT = Path("src")
ROLE_PATTERN = re.compile(r":(?:class|meth|func|mod|attr):`[^`]+`")


def main() -> int:
    violations: list[str] = []

    for path in sorted(SRC_ROOT.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for match in ROLE_PATTERN.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            snippet = match.group(0)
            violations.append(f"{path}:{line}: {snippet}")

    if violations:
        print("❌ Sphinx role markup detected in src docstrings/comments:")
        for violation in violations:
            print(f"  • {violation}")
        print(
            "Use mkdocstrings markdown cross-references instead, e.g. [`Name`][path.to.Name]."
        )
        return 1

    print("✅ No Sphinx role markup detected in src")
    return 0


if __name__ == "__main__":
    sys.exit(main())
