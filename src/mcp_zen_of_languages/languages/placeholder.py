"""Placeholder language implementation used for testing and unsupported-language scaffolding."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    ViolationDetector,
)

if TYPE_CHECKING:
    from mcp_zen_of_languages.models import Violation


class PlaceholderDetector(ViolationDetector):
    """No-op detector used as a stub for zen rules that lack a concrete implementation.

    Always returns an empty violation list, allowing the detection pipeline to
    accept rule-to-detector mappings for every rule without raising import or
    registry errors.
    """

    @property
    def name(self) -> str:
        """Return ``'placeholder_detector'`` identifying this stub.

        Returns:
            str: The ``'placeholder_detector'`` identifier.
        """
        return "placeholder_detector"

    def detect(self, context: AnalysisContext, config: object) -> list[Violation]:
        """Return an empty list — no violations are ever produced.

        Args:
            context: Analysis context (ignored by the stub).
            config: Detector configuration (ignored by the stub).

        Returns:
            list[Violation]: Always an empty list.
        """
        return []
