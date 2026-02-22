"""Python MVP adapter for the universal zen detector."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer

if TYPE_CHECKING:
    from mcp_zen_of_languages.models import AnalysisResult


class PythonMVPAdapter:
    """Minimal Python adapter that delegates to the existing Python analyzer."""

    language = "python"

    def analyze(self, code: str, path: str | None = None) -> AnalysisResult:
        """Analyze Python code using the existing production analyzer pipeline."""
        analyzer = create_analyzer(self.language)
        return analyzer.analyze(code, path=path)
