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
        linked_dogmas = {
            dogma_id
            for violation in result.violations
            for dogma_id in (
                violation.linked_dogma_ids or violation.universal_dogma_ids
            )
        }
        verified_dogmas = {
            dogma_id
            for violation in result.violations
            for dogma_id in violation.verified_dogma_ids
        }
        linked_domain_count = 0
        verified_domain_count = 0
        if result.dogma_analysis:
            linked_domain_count = sum(
                1
                for domain in result.dogma_analysis.domains
                if linked_dogmas.intersection(domain.dogma_ids)
            )
            verified_domain_count = sum(
                1
                for domain in result.dogma_analysis.domains
                if verified_dogmas.intersection(domain.dogma_ids)
            )
        return (
            f"{target}: language={result.language}, "
            f"violations={len(result.violations)}, "
            f"linked_dogmas={len(linked_dogmas)}, "
            f"verified_dogmas={len(verified_dogmas)}, "
            f"linked_domains={linked_domain_count}, "
            f"verified_domains={verified_domain_count}, "
            f"score={result.overall_score:.2f}"
        )


class McpReporter:
    """Render an MCP-friendly structured dictionary payload."""

    def report(self, result: AnalysisResult) -> dict[str, object]:
        """Return a JSON-serializable payload for MCP transport clients."""
        return result.model_dump(mode="json")
