"""Public API surface for the rendering subsystem.

Re-exports console primitives, widget factories, panel builders, progress
indicators, report composition, table helpers, and theme definitions so that
CLI commands and report writers can ``from mcp_zen_of_languages.rendering import …``
without reaching into submodules.

The rendering pipeline flows as follows:

1. **themes** — defines the ``ZEN_THEME`` colour palette and severity glyphs.
2. **console** — creates the Rich ``Console`` singleton bound to that theme.
3. **layout** — enforces an 88-column width cap for all renderables.
4. **factories** — produces ``Panel`` / ``Table`` widgets that honour the cap.
5. **panels / tables** — compose domain-specific widgets (summaries, violations).
6. **report** — orchestrates the final terminal output from ``ReportOutput``.
7. **progress** — provides transient spinners during long-running analysis.
"""

from __future__ import annotations

from .console import (
    console,
    error_console,
    get_banner_art,
    is_quiet,
    print_banner,
    print_error,
    set_quiet,
)
from .factories import zen_header_panel, zen_panel, zen_summary_table, zen_table
from .panels import build_project_summary_panel, build_worst_offenders_panel
from .progress import analysis_progress
from .report import render_report_terminal
from .tables import build_violation_table
from .themes import (
    ZEN_THEME,
    file_glyph,
    pass_fail_glyph,
    score_glyph,
    severity_badge,
    severity_style,
)

__all__ = [
    "ZEN_THEME",
    "analysis_progress",
    "build_project_summary_panel",
    "build_violation_table",
    "build_worst_offenders_panel",
    "console",
    "error_console",
    "file_glyph",
    "get_banner_art",
    "is_quiet",
    "pass_fail_glyph",
    "print_banner",
    "print_error",
    "render_report_terminal",
    "score_glyph",
    "set_quiet",
    "severity_badge",
    "severity_style",
    "zen_header_panel",
    "zen_panel",
    "zen_summary_table",
    "zen_table",
]
