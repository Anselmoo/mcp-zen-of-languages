"""Shared lightweight YAML helpers for CI analyzers."""

from __future__ import annotations

import re
from dataclasses import dataclass

TOP_LEVEL_KEY_RE = re.compile(r"^([A-Za-z0-9_.-]+):\s*(?:#.*)?$")
KEY_LINE_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*:\s*(.*)$")


@dataclass(slots=True)
class TopLevelBlock:
    """Top-level YAML block."""

    name: str
    start_line: int
    lines: list[str]


def split_top_level_blocks(code: str) -> list[TopLevelBlock]:
    """Split YAML text into top-level key blocks."""
    lines = code.splitlines()
    keys: list[tuple[str, int]] = []
    for idx, line in enumerate(lines, start=1):
        if line.startswith((" ", "\t")):
            continue
        match = TOP_LEVEL_KEY_RE.match(line)
        if match:
            keys.append((match[1], idx))
    blocks: list[TopLevelBlock] = []
    for position, (name, start) in enumerate(keys):
        end = keys[position + 1][1] - 1 if position + 1 < len(keys) else len(lines)
        blocks.append(
            TopLevelBlock(name=name, start_line=start, lines=lines[start - 1 : end])
        )
    return blocks


def has_key(block: TopLevelBlock, key: str) -> bool:
    """Return whether a key exists anywhere in a block."""
    return any(re.match(rf"^\s*{re.escape(key)}\s*:", line) for line in block.lines)


def find_key_line(block: TopLevelBlock, key: str) -> int | None:
    """Find first line number for a key inside a block."""
    for offset, line in enumerate(block.lines):
        if re.match(rf"^\s*{re.escape(key)}\s*:", line):
            return block.start_line + offset
    return None
