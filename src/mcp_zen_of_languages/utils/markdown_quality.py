"""Structural linting for Markdown reports emitted by the analysis pipeline.

Before a zen analysis result is rendered to the user, the Markdown output
passes through normalization (trailing-whitespace removal, final-newline
guarantee) and a suite of quality checks covering heading hierarchy, bullet
consistency, fenced-code language tags, and table alignment.
"""

from __future__ import annotations

import re

from pydantic import BaseModel


class MarkdownQuality(BaseModel):
    """Aggregate pass/fail result for each Markdown structural rule.

    Attributes:
        consistent_heading_levels: ``True`` when heading levels never skip
            (e.g. ``##`` directly under ``#`` is fine, ``###`` under ``#`` is not).
        consistent_bullet_markers: ``True`` when all unordered list items use
            the same marker character (``-`` or ``*``, but not both).
        code_blocks_have_language: ``True`` when every fenced code block
            specifies a language tag after the opening triple-backtick.
        no_trailing_whitespace: ``True`` when no line ends with extra spaces.
        tables_aligned: ``True`` when every row in each table block contains
            the same number of pipe delimiters.
    """

    consistent_heading_levels: bool
    consistent_bullet_markers: bool
    code_blocks_have_language: bool
    no_trailing_whitespace: bool
    tables_aligned: bool


_HEADING_RE = re.compile(r"^(#+)\s+")
_BULLET_RE = re.compile(r"^\s*([-*])\s+")
_FENCE_RE = re.compile(r"^```(\S*)\s*$")


def normalize_markdown(text: str) -> str:
    """Strip trailing whitespace from every line and guarantee a final newline.

    Applied to Markdown report content before quality validation so that
    whitespace-only differences do not trigger false negatives in the
    ``no_trailing_whitespace`` check.

    Args:
        text: Raw Markdown string, possibly with inconsistent line endings.

    Returns:
        Cleaned Markdown string with each line right-stripped and a single
        trailing newline appended.
    """

    cleaned_lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(cleaned_lines).strip() + "\n"


def _has_consistent_headings(lines: list[str]) -> bool:
    """Check that heading levels increment by at most one (no skipped levels).

    Walks lines matching ``_HEADING_RE`` and tracks the previous heading
    depth. A jump from ``#`` straight to ``###`` is flagged as inconsistent
    because readers lose the intermediate structural context.

    Args:
        lines: Pre-split Markdown lines to inspect.

    Returns:
        ``True`` when every heading is at most one level deeper than its
        predecessor, ``False`` on the first violation.
    """

    previous_level = 0
    for line in lines:
        match = _HEADING_RE.match(line)
        if not match:
            continue
        level = len(match.group(1))
        if previous_level and level > previous_level + 1:
            return False
        previous_level = level
    return True


def _has_consistent_bullets(lines: list[str]) -> bool:
    """Verify that all unordered list items use the same bullet character.

    Collects the set of distinct markers (``-`` or ``*``) across all lines
    matching ``_BULLET_RE``. Mixed markers hurt visual consistency in
    rendered reports.

    Args:
        lines: Pre-split Markdown lines to inspect.

    Returns:
        ``True`` when zero or one distinct marker character is used,
        ``False`` when both ``-`` and ``*`` appear.
    """

    markers = {match.group(1) for line in lines if (match := _BULLET_RE.match(line))}
    return len(markers) <= 1


def _code_blocks_have_language(lines: list[str]) -> bool:
    """Ensure every opening triple-backtick fence declares a language identifier.

    Tracks open/close state via ``_FENCE_RE`` and checks the capture group
    on each opening fence. Missing language tags prevent syntax highlighting
    in rendered output and reduce report readability.

    Args:
        lines: Pre-split Markdown lines to inspect.

    Returns:
        ``True`` when all fenced blocks include a language tag,
        ``False`` on the first bare opening fence.
    """

    in_code = False
    for line in lines:
        match = _FENCE_RE.match(line.strip())
        if not match:
            continue
        if in_code:
            in_code = False
            continue
        in_code = True
        if not match.group(1):
            return False
    return True


def _tables_aligned(lines: list[str]) -> bool:
    """Confirm that every row within a Markdown table has the same number of columns.

    Identifies table rows as lines starting and ending with ``|``, then
    counts pipe characters per row. A column-count mismatch within a
    contiguous table block indicates a formatting error.

    Args:
        lines: Pre-split Markdown lines to inspect.

    Returns:
        ``True`` when all rows in every table block share the same pipe
        count, ``False`` on the first mismatch.
    """

    expected_columns: int | None = None
    for line in lines:
        stripped = line.strip()
        if "|" not in stripped:
            expected_columns = None
            continue
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        columns = stripped.count("|")
        if expected_columns is None:
            expected_columns = columns
            continue
        if columns != expected_columns:
            return False
    return True


def validate_markdown(text: str) -> MarkdownQuality:
    """Run the full suite of structural quality checks against Markdown content.

    Splits *text* into lines once and feeds them to each individual check
    function. The combined result tells report generators whether the
    output meets the project's Markdown style expectations.

    Args:
        text: Complete Markdown string to validate.

    Returns:
        A ``MarkdownQuality`` model with a boolean field for each rule,
        suitable for programmatic inspection or rendering in diagnostics.
    """

    lines = text.splitlines()
    return MarkdownQuality(
        consistent_heading_levels=_has_consistent_headings(lines),
        consistent_bullet_markers=_has_consistent_bullets(lines),
        code_blocks_have_language=_code_blocks_have_language(lines),
        no_trailing_whitespace=all(line == line.rstrip() for line in lines),
        tables_aligned=_tables_aligned(lines),
    )
