"""Architectural pattern detection for the zen-of-languages MCP server.

This package provides lightweight, text-based detectors that identify common
architectural and design patterns in source code snippets.  Each detector
operates on raw source text via regular expressions so it works across every
language supported by the server without requiring a full parse tree.

Public API::

    from mcp_zen_of_languages.patterns import detect_patterns

    findings = detect_patterns(code, language="python")
    # → list[PatternFinding]
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_zen_of_languages.patterns.detectors import ALL_DETECTORS


if TYPE_CHECKING:
    from mcp_zen_of_languages.models import PatternFinding


def detect_patterns(code: str, language: str) -> list[PatternFinding]:
    """Run all registered pattern detectors against *code*.

    Args:
        code: Source fragment to inspect.
        language: Canonical language key (e.g. ``"python"``, ``"go"``).

    Returns:
        Flat list of every ``PatternFinding`` emitted by all detectors.
        Returns an empty list when no patterns are recognised.
    """
    findings: list[PatternFinding] = []
    for detector in ALL_DETECTORS:
        findings.extend(detector.detect(code, language))
    return findings


__all__ = ["ALL_DETECTORS", "detect_patterns"]
