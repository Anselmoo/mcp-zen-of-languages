"""Universal analyzer-factory adapter helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer
from mcp_zen_of_languages.analyzers.analyzer_factory import supported_languages


if TYPE_CHECKING:
    from mcp_zen_of_languages.core.detector import LanguageAdapter
    from mcp_zen_of_languages.models import AnalysisResult


class AnalyzerFactoryAdapter:
    """Language adapter that delegates analysis to ``create_analyzer``."""

    def __init__(self, language: str) -> None:
        """Bind this adapter to a language key understood by the factory."""
        self.language = language

    def analyze(self, code: str, path: str | None = None) -> AnalysisResult:
        """Analyze code with the configured language analyzer.

        Args:
            code (str): Source code to analyse.
            path (str | None, optional): File path being analysed. Default to None.
        """
        analyzer = create_analyzer(self.language)
        return analyzer.analyze(code, path=path)


def build_universal_adapters() -> dict[str, LanguageAdapter]:
    """Build adapters for all canonical languages in the analyzer factory."""
    return {
        language: AnalyzerFactoryAdapter(language) for language in supported_languages()
    }
