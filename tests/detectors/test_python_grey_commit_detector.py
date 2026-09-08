from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import GreyCommitConfig
from mcp_zen_of_languages.languages.python.detectors import GreyCommitCommentDetector


SEVERITY_SINGLE_LINE = 3
SEVERITY_MULTI_LINE = 5
SEVERITY_MARKER = 6
SEVERITY_NO_DOCSTRING = 8


def _run(code: str, config: GreyCommitConfig | None = None) -> list:
    """Run the grey-commit detector against *code* and return its violations.

    Args:
        code: Python source to analyze.
        config: Optional detector configuration; defaults to
            ``GreyCommitConfig()`` when omitted.

    Returns:
        list: Violations produced by ``GreyCommitCommentDetector``.
    """
    context = AnalysisContext(code=code, language="python")
    return GreyCommitCommentDetector().detect(context, config or GreyCommitConfig())


def test_grey_commit_detects_multiline_comment_block() -> None:
    """A multi-line rationale comment block is flagged at medium severity."""
    code = (
        "def parse_data(value: str) -> int:\n"
        '    """Parse value."""\n'
        "    # avoid calling parser directly in this runtime binding\n"
        "    # instead use the compatibility shim for stable behavior\n"
        "    return int(value)\n"
    )
    violations = _run(code)
    assert violations
    assert violations[0].severity >= SEVERITY_MULTI_LINE


def test_grey_commit_detects_explicit_marker() -> None:
    """A NOTE: marker comment is flagged at marker severity or higher."""
    code = (
        "def parse_data(value: str) -> int:\n"
        '    """Parse value."""\n'
        "    # NOTE: we must keep this fallback because prod wheels vary\n"
        "    return int(value)\n"
    )
    violations = _run(code)
    assert violations
    assert max(v.severity for v in violations) >= SEVERITY_MARKER


def test_grey_commit_uses_high_severity_without_docstring() -> None:
    """A multi-line rationale block in an undocumented function is high severity."""
    code = (
        "def parse_data(value: str) -> int:\n"
        "    # avoid direct import in this environment\n"
        "    # instead use a prebuilt language module from CI\n"
        "    return int(value)\n"
    )
    violations = _run(code)
    assert violations
    assert max(v.severity for v in violations) >= SEVERITY_NO_DOCSTRING


def test_grey_commit_detects_long_single_line_comment() -> None:
    """A single comment line longer than the configured limit is flagged."""
    code = (
        "def parse_data(value: str) -> int:\n"
        '    """Parse value."""\n'
        "    # this explanation is intentionally long because it documents why the "
        "fallback path should remain enabled for compatibility with ci images\n"
        "    return int(value)\n"
    )
    violations = _run(code, GreyCommitConfig(max_inline_comment_length=72))
    assert violations
    assert min(v.severity for v in violations) >= SEVERITY_SINGLE_LINE


def test_grey_commit_false_positive_guards() -> None:
    """Shebang, noqa, type: ignore, and single-word comments are never flagged."""
    code = (
        "def parse_data(value: str) -> int:\n"
        "    # noqa: E501\n"
        "    # type: ignore[arg-type]\n"
        "    # TODO\n"
        "    return int(value)\n"
    )
    assert _run(code) == []


def test_grey_commit_short_comment_with_docstring_yields_no_violations() -> None:
    """A documented function with a short, benign inline comment yields none."""
    code = (
        "def parse_data(value: str) -> int:\n"
        '    """Parse value."""\n'
        "    # noqa\n"
        "    return int(value)\n"
    )
    assert _run(code) == []
