"""Orchestration layer that gathers all numeric code-health metrics in a single pass.

The collector delegates to radon for cyclomatic complexity and maintainability
index, then counts source lines independently. Analyzers call
``MetricsCollector.collect`` once and receive a ready-to-use tuple that feeds
directly into the ``AnalysisContext`` consumed by the detection pipeline.
"""

from __future__ import annotations

from mcp_zen_of_languages.models import CyclomaticSummary

from .complexity import compute_cyclomatic_complexity, compute_maintainability_index


class MetricsCollector:
    """Stateless façade that unifies cyclomatic, maintainability, and LOC metrics.

    Language-specific analyzers delegate to this collector inside their
    ``compute_metrics`` hook so that metric computation logic stays
    decoupled from the Template Method flow in ``BaseAnalyzer``.
    """

    @staticmethod
    def collect(code: str) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Compute cyclomatic complexity, maintainability index, and line count.

        Wraps radon's ``cc_visit`` and ``mi_visit`` behind a safety net so
        that a failure in one metric never prevents the analyzer from
        returning partial results.

        Args:
            code: Python source text to measure.

        Returns:
            A three-element tuple of ``(cyclomatic_summary, maintainability_index,
            lines_of_code)``. On radon errors the first two elements are ``None``
            while the line count is always populated.
        """
        try:
            cc = compute_cyclomatic_complexity(code)
            mi = compute_maintainability_index(code)
            loc = len(code.splitlines())
            return cc, mi, loc
        except Exception:
            return None, None, len(code.splitlines())
