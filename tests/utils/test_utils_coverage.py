from __future__ import annotations

from mcp_zen_of_languages.utils.parsers import (
    parse_python_with_builtin_ast,
    parse_python_with_treesitter,
)


def test_parse_python_with_builtin_ast_invalid():
    assert parse_python_with_builtin_ast("def foo(") is None


def test_parse_python_with_treesitter_returns_none():
    assert parse_python_with_treesitter("def foo():\n    pass\n") is None
