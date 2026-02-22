from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import GreyCommitConfig
from mcp_zen_of_languages.languages.python.detectors import GreyCommitCommentDetector

SEVERITY_SINGLE_LINE = 3
SEVERITY_MULTI_LINE = 5
SEVERITY_MARKER = 6
SEVERITY_NO_DOCSTRING = 8


def _run(code: str, config: GreyCommitConfig | None = None):
    context = AnalysisContext(code=code, language="python")
    return GreyCommitCommentDetector().detect(context, config or GreyCommitConfig())


def test_grey_commit_detects_multiline_comment_block() -> None:
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
    code = (
        "def parse_data(value: str) -> int:\n"
        "    # noqa: E501\n"
        "    # type: ignore[arg-type]\n"
        "    # TODO\n"
        "    return int(value)\n"
    )
    assert _run(code) == []
