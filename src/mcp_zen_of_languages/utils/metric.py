"""Arithmetic helpers that distil violation lists into single quality scores.

The quality score is the primary rollup metric exposed in analysis results.
It starts at a perfect 100 and decreases proportionally to the cumulative
severity of detected violations, giving reviewers a quick at-a-glance
health indicator for the analysed file.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.models import Violation


def calculate_code_quality_score(violations: list[Violation]) -> float:
    """Derive a 0-100 quality score by penalising each violation proportionally to its severity.

    Starts at 100 and subtracts ``2 x severity`` for every violation.
    The 2x multiplier ensures that even a handful of high-severity
    violations produce a noticeable drop, while minor issues degrade the
    score gently. The floor is clamped to 0 so the score never goes negative.

    Args:
        violations: Violation instances whose ``severity`` fields drive the
            penalty calculation.

    Returns:
        A float between 0.0 (heavily violated) and 100.0 (no violations).
    """
    return max(0.0, 100.0 - (sum(v.severity for v in violations) * 2))
