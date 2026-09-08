from __future__ import annotations

import ast
import tokenize

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
    assert violations[0].severity == SEVERITY_SINGLE_LINE


def test_grey_commit_false_positive_guards() -> None:
    """Noqa, type: ignore, and single-word comments are never flagged."""
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


def test_grey_commit_honors_configured_severity() -> None:
    """A configured severity shifts the whole ladder relative to the default."""
    code = (
        "def parse_data(value: str) -> int:\n"
        '    """Parse value."""\n'
        "    # NOTE: keep this fallback because prod wheels vary at runtime\n"
        "    return int(value)\n"
    )
    default_violations = _run(code)
    high_violations = _run(code, GreyCommitConfig(severity=9))
    low_violations = _run(code, GreyCommitConfig(severity=1))

    assert default_violations
    assert high_violations
    assert low_violations
    assert default_violations[0].severity == SEVERITY_MARKER
    assert high_violations[0].severity == 9
    assert low_violations[0].severity == 1
    assert high_violations[0].severity != default_violations[0].severity
    assert low_violations[0].severity != default_violations[0].severity
    assert high_violations[0].severity != low_violations[0].severity


def test_grey_commit_detect_grey_comments_false_disables_detector() -> None:
    """Setting detect_grey_comments=False always yields an empty violation list."""
    code = (
        "def parse_data(value: str) -> int:\n"
        "    # NOTE: keep this fallback because prod wheels vary at runtime\n"
        "    return int(value)\n"
    )
    # Confirm the same code *would* be flagged with the detector enabled.
    assert _run(code) != []
    assert _run(code, GreyCommitConfig(detect_grey_comments=False)) == []


def test_grey_commit_max_inline_comment_length_is_configurable() -> None:
    """Lowering max_inline_comment_length flags a comment the default allows."""
    code = (
        "def parse_data(value: str) -> int:\n"
        '    """Parse value."""\n'
        "    # this comment documents the return value for callers here\n"
        "    return int(value)\n"
    )
    assert _run(code) == []
    assert _run(code, GreyCommitConfig(max_inline_comment_length=20)) != []


def test_grey_commit_unparseable_source_yields_no_violations() -> None:
    """Source that cannot be parsed is skipped instead of raising."""
    assert _run("def parse_data(:\n") == []


def test_grey_commit_ignores_comments_outside_function_bodies() -> None:
    """A module-level comment belongs to no function span and is never flagged."""
    code = (
        "# NOTE: module-level rationale that sits outside every function body\n"
        "def parse_data(value: str) -> int:\n"
        '    """Parse value."""\n'
        "    return int(value)\n"
    )
    assert _run(code) == []


def test_grey_commit_attributes_comment_to_the_enclosing_function() -> None:
    """With several functions in scope only the enclosing one is charged."""
    code = (
        "def first(value: str) -> int:\n"
        '    """Parse value."""\n'
        "    return int(value)\n"
        "def second(value: str) -> int:\n"
        '    """Parse value."""\n'
        "    # NOTE: only the second function carries this rationale comment\n"
        "    return int(value)\n"
    )
    violations = _run(code)
    assert len(violations) == 1
    assert violations[0].location.line == 6


def test_grey_commit_handles_comment_on_the_final_source_line() -> None:
    """A trailing inline comment has no following line to inspect."""
    code = (
        "def parse_data(value: str) -> int:\n"
        '    """Parse value."""\n'
        "    return int(value)  # NOTE: rationale explaining the int conversion\n"
    )
    violations = _run(code)
    assert violations
    assert violations[0].location.line == 3


def test_grey_commit_function_spans_skips_nodes_without_a_body() -> None:
    """A function node carrying no body contributes no span."""
    node = ast.FunctionDef(
        name="empty",
        args=ast.arguments(
            posonlyargs=[],
            args=[],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        ),
        body=[],
        decorator_list=[],
        returns=None,
        type_params=[],
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=0,
    )
    tree = ast.Module(body=[node], type_ignores=[])
    assert GreyCommitCommentDetector()._function_spans(tree) == []


def test_grey_commit_survives_a_token_error_mid_stream(monkeypatch) -> None:
    """A TokenError degrades to best-effort instead of escaping the detector."""
    code = (
        "def parse_data(value: str) -> int:\n"
        "    # NOTE: keep this fallback because prod wheels vary at runtime\n"
        "    return int(value)\n"
    )
    comment = "# NOTE: keep this fallback because prod wheels vary at runtime"

    def _truncated_stream(_readline):
        yield tokenize.TokenInfo(
            type=tokenize.COMMENT,
            string=comment,
            start=(2, 4),
            end=(2, 4 + len(comment)),
            line=code.splitlines(keepends=True)[1],
        )
        msg = "unexpected EOF in multi-line statement"
        raise tokenize.TokenError(msg)

    monkeypatch.setattr(tokenize, "generate_tokens", _truncated_stream)

    violations = _run(code)
    assert violations
    assert max(v.severity for v in violations) >= SEVERITY_MARKER
