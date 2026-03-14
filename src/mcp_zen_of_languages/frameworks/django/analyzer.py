"""Django analyzer wrapper."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalyzerCapabilities
from mcp_zen_of_languages.frameworks.base import FrameworkAnalyzerMixin
from mcp_zen_of_languages.languages.python.analyzer import PythonAnalyzer


class DjangoAnalyzer(FrameworkAnalyzerMixin, PythonAnalyzer):
    """Framework-specific analyzer that reuses the parent language pipeline mechanics."""

    framework_key = "django"
    parent_language_key = "python"

    def capabilities(self) -> AnalyzerCapabilities:
        """Report placeholder-style capabilities until framework-specific AST support exists."""
        return AnalyzerCapabilities()
