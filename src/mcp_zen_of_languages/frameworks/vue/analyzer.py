"""Vue analyzer wrapper."""

from __future__ import annotations

from mcp_zen_of_languages.frameworks.base import FrameworkAnalyzerMixin
from mcp_zen_of_languages.languages.javascript.analyzer import JavaScriptAnalyzer


class VueAnalyzer(FrameworkAnalyzerMixin, JavaScriptAnalyzer):
    """Framework-specific analyzer that reuses the parent language pipeline mechanics."""

    framework_key = "vue"
    parent_language_key = "javascript"
