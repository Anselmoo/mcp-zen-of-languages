"""Reporting package that transforms raw analysis results into actionable output.

The reporting pipeline flows through several stages:

1. **Analysis collection** — ``report.generate_report`` scans a target path,
   runs language-specific analyzers, and collects ``AnalysisResult`` objects.
2. **Gap analysis** — ``gaps.build_gap_analysis`` cross-references detected
   violations against the detector registry to surface missing coverage.
3. **Theme clustering** — ``theme_clustering.build_big_picture_analysis`` groups
   violations into remediation themes ranked by cumulative severity.
4. **Prompt generation** — ``prompts.build_prompt_bundle`` produces per-file and
   generic remediation prompts with before/after code patterns.
5. **Agent task generation** — ``agent_tasks.build_agent_tasks`` converts
   violations into dependency-ordered work items for automated remediation.
6. **Rendering** — ``terminal`` renders Rich panels and tables to the console;
   ``report`` serializes the same data as Markdown for file or MCP output.

Public API:
    ReportOutput: Pydantic model carrying the final Markdown text and raw data dict.
    generate_report: Orchestrator that drives the full pipeline end-to-end.

See Also:
    ``mcp_zen_of_languages.cli``: CLI entry point that invokes ``generate_report``.
    ``mcp_zen_of_languages.server``: MCP tool surface that exposes reports over the wire.
"""

from mcp_zen_of_languages.reporting.models import ReportOutput
from mcp_zen_of_languages.reporting.report import generate_report

__all__ = ["ReportOutput", "generate_report"]
