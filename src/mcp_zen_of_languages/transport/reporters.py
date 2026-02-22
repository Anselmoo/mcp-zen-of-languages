"""Reporter implementations for CLI and MCP transport layers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.models import AnalysisResult


class CliReporter:
    """Render a compact human-readable analysis summary for terminal use."""

    def report(self, result: AnalysisResult) -> str:
        """Return a concise terminal-oriented summary string."""
        target = result.path or "<snippet>"
        return (
            f"{target}: language={result.language}, "
            f"violations={len(result.violations)}, score={result.overall_score:.2f}"
        )


class McpReporter:
    """Render an MCP-friendly structured dictionary payload."""

    def report(self, result: AnalysisResult) -> dict[str, object]:
        """Return a JSON-serializable payload for MCP transport clients."""
        return result.model_dump(mode="json")
