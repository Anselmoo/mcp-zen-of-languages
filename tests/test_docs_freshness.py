"""Verify generated language docs are not stale.

Runs the generator in ``--check`` mode and asserts that every
``docs/user-guide/languages/*.md`` page matches the output produced
from the current ``rules.py`` and ``DETECTOR_MAP`` data.
"""

from __future__ import annotations

import re
import subprocess
import sys

from pathlib import Path


LANGUAGE_DOCS_DIR = Path("docs/user-guide/languages")
BROKEN_INDENTED_MERMAID_PATTERN = re.compile(r"(?m)^ {4}```mermaid\n(?! {4})")
INLINE_MERMAID_CLASSDEF_PATTERN = re.compile(r"(?m)^ {4}classDef ")
BROKEN_MERMAID_LABEL_QUOTES_PATTERN = re.compile(
    r'(?m)^ {4}[A-Za-z0-9_]+\["[^"\n]*"[^"\n]*"\]$'
)


def test_language_docs_freshness() -> None:
    """Fail if any language doc page is stale relative to rules.py data."""
    result = subprocess.run(  # noqa: S603
        [sys.executable, "scripts/generate_language_docs.py", "--check"],
        capture_output=True,
        text=True,
        check=False,
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


def test_language_docs_indented_mermaid_blocks_are_well_formed() -> None:
    """Fail if an indented Mermaid fence is followed by an unindented body line."""
    malformed_files = [
        path.as_posix()
        for path in sorted(LANGUAGE_DOCS_DIR.glob("*.md"))
        if BROKEN_INDENTED_MERMAID_PATTERN.search(path.read_text(encoding="utf-8"))
    ]

    if malformed_files:
        msg = (
            "Generated language docs contain malformed indented Mermaid blocks. "
            "The first line inside an indented ```mermaid fence must use the same "
            "indentation as the fence.\n\nAffected files:\n  "
            + "\n  ".join(malformed_files)
        )
        raise AssertionError(msg)


def test_language_docs_do_not_inline_mermaid_palette_overrides() -> None:
    """Keep generated Mermaid styling in shared CSS instead of inline classDefs."""
    inline_palette_files = [
        path.as_posix()
        for path in sorted(LANGUAGE_DOCS_DIR.glob("*.md"))
        if INLINE_MERMAID_CLASSDEF_PATTERN.search(path.read_text(encoding="utf-8"))
    ]

    if inline_palette_files:
        msg = (
            "Generated language docs contain inline Mermaid classDef palette overrides. "
            "Language guide diagrams should inherit shared styling from "
            "docs/stylesheets/components/mermaid.css.\n\nAffected files:\n  "
            + "\n  ".join(inline_palette_files)
        )
        raise AssertionError(msg)


def test_language_docs_escape_embedded_mermaid_quotes() -> None:
    """Fail if Mermaid node labels contain raw embedded double quotes."""
    malformed_label_files = [
        path.as_posix()
        for path in sorted(LANGUAGE_DOCS_DIR.glob("*.md"))
        if BROKEN_MERMAID_LABEL_QUOTES_PATTERN.search(path.read_text(encoding="utf-8"))
    ]

    if malformed_label_files:
        msg = (
            "Generated language docs contain Mermaid labels with raw embedded double "
            "quotes, which break browser rendering.\n\nAffected files:\n  "
            + "\n  ".join(malformed_label_files)
        )
        raise AssertionError(msg)
