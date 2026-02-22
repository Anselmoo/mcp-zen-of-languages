"""Universal detector contracts and thin orchestration layer."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from mcp_zen_of_languages.models import AnalysisResult

DOGMA_RULE_IDS: tuple[str, ...] = (
    "ZEN-UTILIZE-ARGUMENTS",
    "ZEN-EXPLICIT-INTENT",
    "ZEN-RETURN-EARLY",
    "ZEN-FAIL-FAST",
    "ZEN-RIGHT-ABSTRACTION",
    "ZEN-UNAMBIGUOUS-NAME",
    "ZEN-VISIBLE-STATE",
    "ZEN-STRICT-FENCES",
    "ZEN-RUTHLESS-DELETION",
    "ZEN-PROPORTIONATE-COMPLEXITY",
)


class LanguageAdapter(Protocol):
    """Language adapter contract for universal detector orchestration."""

    language: str

    def analyze(self, code: str, path: str | None = None) -> AnalysisResult:
        """Return language-specific analysis for a source snippet."""


class ReporterInterface(Protocol):
    """Reporter contract for transport-specific output formatting."""

    def report(self, result: AnalysisResult) -> str | dict[str, object]:
        """Format analysis output for the target transport."""


class UniversalZenDetector:
    """Universal coordinator that delegates parsing+analysis to language adapters."""

    def __init__(self, adapters: dict[str, LanguageAdapter]) -> None:
        """Initialize the detector with language-keyed adapters."""
        self._adapters = {name.lower(): adapter for name, adapter in adapters.items()}

    def analyze(
        self,
        code: str,
        language: str,
        path: str | None = None,
    ) -> AnalysisResult:
        """Analyze code via the adapter registered for ``language``."""
        adapter = self._adapters.get(language.lower())
        if adapter is None:
            msg = f"Unsupported language adapter: {language}"
            raise ValueError(msg)
        return adapter.analyze(code, path=path)
