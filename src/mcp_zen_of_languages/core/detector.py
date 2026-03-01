"""Universal detector contracts and thin orchestration layer."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Protocol

from mcp_zen_of_languages.core.universal_dogmas import (
    DOGMA_RULE_IDS as UNIVERSAL_DOGMA_RULE_IDS,
)


if TYPE_CHECKING:
    from mcp_zen_of_languages.models import AnalysisResult

DOGMA_RULE_IDS: tuple[str, ...] = UNIVERSAL_DOGMA_RULE_IDS


class LanguageAdapter(Protocol):
    """Language adapter contract for universal detector orchestration."""

    language: str

    def analyze(self, code: str, path: str | None = None) -> AnalysisResult:
        """Return language-specific analysis for a source snippet.

        Note:
            The Programming language identifier is defined as a class attribute
            and not an argument to this method because the adapter instance is registered under a specific language in the UniversalZenDetector.
            The analyze method is then called with code and path, and the adapter implementation can assume the language context based on its registration.

        Args:
            code (str): Source code to analyse.
            path (str | None, optional): File path being analysed. Default to None.
        """


class ReporterInterface(Protocol):
    """Reporter contract for transport-specific output formatting."""

    def report(self, result: AnalysisResult) -> str | dict[str, object]:
        """Format analysis output for the target transport.

        result (AnalysisResult): The analysis result for every language analyser.
        """


class UniversalZenDetector:
    """Universal coordinator that delegates parsing+analysis to language adapters."""

    def __init__(self, adapters: dict[str, LanguageAdapter] | None = None) -> None:
        """Initialize the detector with explicit adapters or all supported languages.

        Args:
            adapters (dict[str, LanguageAdapter] | None, optional): Language-specific adapters. Default to None.
        """
        if adapters is None:
            from mcp_zen_of_languages.adapters.universal import build_universal_adapters

            adapters = build_universal_adapters()
        self._adapters = {name.lower(): adapter for name, adapter in adapters.items()}

    def analyze(
        self,
        code: str,
        language: str,
        path: str | None = None,
    ) -> AnalysisResult:
        """Analyze code via the adapter registered for ``language``.

        Args:
            code (str): Source code to analyse.
            language (str): Programming language identifier.
            path (str | None, optional): Path. Default to None.
        """
        adapter = self._adapters.get(language.lower())
        if adapter is None:
            msg = f"Unsupported language adapter: {language}"
            raise ValueError(msg)
        return adapter.analyze(code, path=path)
