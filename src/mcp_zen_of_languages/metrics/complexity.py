"""Radon-backed complexity metrics that power zen principle threshold checks.

Cyclomatic complexity is computed per-function via ``radon.complexity.cc_visit``
and aggregated into a ``CyclomaticSummary``. The maintainability index uses
``radon.metrics.mi_visit``, which blends Halstead volume, cyclomatic complexity,
and lines of code into a single 0–100 score following the Microsoft Visual
Studio formula.
"""

from radon.complexity import cc_visit
from radon.metrics import mi_visit

from mcp_zen_of_languages.models import CyclomaticBlock, CyclomaticSummary


def compute_cyclomatic_complexity(code: str) -> CyclomaticSummary:
    """Walk every function and class in *code* with radon's ``cc_visit`` and return structured results.

    Each callable block receives an independent complexity score counting
    the number of linearly independent paths through its control flow.
    The per-block scores are averaged into a single file-level summary
    that detectors compare against ``max_cyclomatic_complexity``.

    Args:
        code: Python source text to analyse.

    Returns:
        A ``CyclomaticSummary`` containing individual ``CyclomaticBlock``
        entries and the arithmetic mean complexity across all blocks.
        Returns an empty summary with ``average=0.0`` when radon cannot
        parse the input.
    """
    try:
        blocks = cc_visit(code)
        results = [
            CyclomaticBlock(name=b.name, complexity=b.complexity, lineno=b.lineno)
            for b in blocks
        ]
        avg = sum(b.complexity for b in blocks) / len(blocks) if blocks else 0.0
        return CyclomaticSummary(blocks=results, average=avg)
    except Exception:
        return CyclomaticSummary(blocks=[], average=0.0)


def compute_maintainability_index(code: str, *, multi: bool = False) -> float:
    """Compute a 0–100 maintainability index using radon's ``mi_visit``.

    The score combines Halstead volume, cyclomatic complexity, and source
    lines of code. Higher values indicate easier-to-maintain code; the
    zen principle ``min_maintainability_index`` sets the passing threshold.

    Args:
        code: Python source text to evaluate.
        multi: When ``True``, radon counts multi-line strings as comments,
            which can raise the score for heavily documented modules.

    Returns:
        A float between 0 and 100 representing the maintainability index.
        Returns ``0.0`` when radon cannot parse the input.
    """
    try:
        mi = mi_visit(code=code, multi=multi)
        return float(mi)
    except Exception:
        return 0.0
