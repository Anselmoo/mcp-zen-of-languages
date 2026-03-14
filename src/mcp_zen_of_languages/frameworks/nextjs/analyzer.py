"""Next.js analyzer wrapper."""

from __future__ import annotations

from mcp_zen_of_languages.frameworks.react.analyzer import ReactAnalyzer


class NextjsAnalyzer(ReactAnalyzer):
    """Framework-specific analyzer that reuses the parent language pipeline mechanics."""

    framework_key = "nextjs"
    parent_language_key = "react"
