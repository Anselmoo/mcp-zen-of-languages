#!/usr/bin/env python3
"""Detect orphan markdown files that exist in docs/ but are not in mkdocs.yml nav."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

DOCS_DIR = Path("docs")
MKDOCS_YML = Path("mkdocs.yml")


# Handle mkdocs-specific YAML tags like !ENV, python/name:*, etc.
class _MkDocsLoader(yaml.SafeLoader):
    pass


def _passthrough_constructor(
    loader: yaml.Loader, tag_suffix: str, node: yaml.Node
) -> str:
    """Return empty string for any unknown tags — we only need the nav."""
    return ""


_MkDocsLoader.add_multi_constructor("", _passthrough_constructor)

# Files/dirs that are legitimately not in nav
ALLOWED_ORPHANS = {
    "docs/overrides",
    "docs/stylesheets",
    "docs/assets",
    "docs/includes",
    "docs/404.md",
}


def _collect_nav_paths(nav: list | dict | str, prefix: str = "") -> set[str]:
    """Recursively extract all .md paths referenced in mkdocs nav."""
    paths: set[str] = set()
    if isinstance(nav, str):
        paths.add(f"docs/{nav}")
    elif isinstance(nav, dict):
        for v in nav.values():
            paths |= _collect_nav_paths(v, prefix)
    elif isinstance(nav, list):
        for item in nav:
            paths |= _collect_nav_paths(item, prefix)
    return paths


def main() -> int:
    if not MKDOCS_YML.exists():
        print(f"ERROR: {MKDOCS_YML} not found")
        return 1

    with open(MKDOCS_YML) as f:
        config = yaml.load(f, Loader=_MkDocsLoader)

    nav = config.get("nav", [])
    nav_paths = _collect_nav_paths(nav)

    # Collect all .md files in docs/
    all_md = set()
    for md_file in DOCS_DIR.rglob("*.md"):
        rel = str(md_file)
        # Skip allowed orphan dirs/files
        if any(rel.startswith(a) for a in ALLOWED_ORPHANS):
            continue
        all_md.add(rel)

    orphans = sorted(all_md - nav_paths)
    if orphans:
        print(f"Found {len(orphans)} orphan doc(s) not in mkdocs.yml nav:")
        for orphan in orphans:
            print(f"  - {orphan}")
        return 1

    print(f"✓ All {len(all_md)} doc files are referenced in nav")
    return 0


if __name__ == "__main__":
    sys.exit(main())
