"""React analyzer wrapper."""

from __future__ import annotations

from mcp_zen_of_languages.frameworks.base import FrameworkAnalyzerMixin
from mcp_zen_of_languages.languages.typescript.analyzer import TypeScriptAnalyzer


class ReactAnalyzer(FrameworkAnalyzerMixin, TypeScriptAnalyzer):
    """Framework-specific analyzer that reuses the parent language pipeline mechanics."""

    framework_key = "react"
    parent_language_key = "typescript"
