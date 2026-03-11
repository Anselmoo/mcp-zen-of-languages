"""Shared detector for cross-language keyword/pattern dogma heuristics."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.base import LocationHelperMixin
from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.languages.configs import DetectorConfig
from mcp_zen_of_languages.models import Location
from mcp_zen_of_languages.models import Violation


class SharedDogmaKeywordDetector(
    ViolationDetector[DetectorConfig], LocationHelperMixin
):
    """Detect configured literal patterns in source text across any language."""

    UNIVERSAL_RULE_IDS = (
        "ZEN-EXPLICIT-INTENT",
        "ZEN-UNAMBIGUOUS-NAME",
    )

    @property
    def name(self) -> str:
        """Return a stable detector name for registry and logging."""
        return "shared_dogma_keyword"

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        """Return one violation per configured pattern found in the source snippet."""
        violations: list[Violation] = []
        patterns = config.detectable_patterns or []
        for pattern in patterns:
            if not pattern:
                continue
            for line_number, line in enumerate(context.code.splitlines(), start=1):
                column = line.find(pattern)
                if column < 0:
                    continue
                violations.append(
                    self.build_violation(
                        config,
                        contains=pattern,
                        location=Location(line=line_number, column=column + 1),
                        suggestion=config.recommended_alternative,
                    ),
                )
                break
        return violations
