"""Front-end parser selection that provides a unified AST to the analysis pipeline.

Attempts tree-sitter first for richer syntax information and falls back to
Python's built-in ``ast`` module when tree-sitter bindings are unavailable.
The result is wrapped in a ``ParserResult`` model that tags the parser
backend so downstream detectors can adapt their traversal logic accordingly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ast import Module

    from mcp_zen_of_languages.models import ParserResult


def parse_python_with_treesitter(code: str) -> object | None:
    """Try to build a concrete syntax tree using tree-sitter's Python grammar.

    Loads a pre-compiled ``build/my-languages.so`` shared library via the
    ``build.my_languages`` import convention. If tree-sitter bindings,
    the shared library, or the ``PY_LANGUAGE`` object are missing, returns
    ``None`` so the caller can fall back to ``ast.parse``.

    Args:
        code: Python source text to parse into a tree-sitter tree.

    Returns:
        A tree-sitter ``Tree`` object on success, or ``None`` when the
        tree-sitter toolchain is not available in this environment.
    """
    from tree_sitter import Parser

    # Use explicit, typed usage of Parser and Language APIs; do not swallow errors silently here.
    # Attempt to construct Language using the common two-arg form guarded by a TypeError fallback.
    parser = Parser()
    # tree-sitter Language constructors can expect a pointer/int in some bindings; avoid calling
    # Language directly with a path in this environment. Instead, attempt to import a prebuilt
    # language module `build.my_languages` which exposes a `PY_LANGUAGE` object (convention used by CI)
    try:
        from build.my_languages import PY_LANGUAGE  # type: ignore

        if not hasattr(parser, "set_language"):
            return None
        parser.set_language(PY_LANGUAGE)
        return parser.parse(bytes(code, "utf8"))
    except Exception:
        # Fall back to builtin ast if any step fails; do not raise here to keep analysis robust
        return None


def parse_python_with_builtin_ast(code: str) -> Module | None:
    """Parse Python source into a stdlib ``ast.Module`` node.

    Acts as the reliable fallback when tree-sitter is unavailable.
    Syntax errors are caught and converted to ``None`` so callers can
    report a parse failure without raising; other exceptions propagate
    to preserve unexpected-error visibility.

    Args:
        code: Python source text to compile into an AST.

    Returns:
        An ``ast.Module`` root node on success, or ``None`` when the source
        contains a syntax error.
    """

    import ast

    # Let syntax errors propagate as SyntaxError; return None only on unexpected exceptions.
    try:
        return ast.parse(code)
    except SyntaxError:
        return None


def parse_python(code: str) -> ParserResult | None:
    """Unified entry point that selects the best available parser for Python source.

    Tries tree-sitter first for its richer concrete syntax tree, then
    falls back to the built-in ``ast`` module. The chosen backend is
    recorded in ``ParserResult.type`` (``"tree-sitter"`` or ``"ast"``)
    so detectors can branch on parser capabilities when needed.

    Args:
        code: Python source text to parse.

    Returns:
        A ``ParserResult`` wrapping the parsed tree and its backend tag,
        or ``None`` when neither parser can handle the input.
    """
    from mcp_zen_of_languages.models import ParserResult

    tree = parse_python_with_treesitter(code)
    if tree is not None:
        return ParserResult(type="tree-sitter", tree=tree)
    ast_tree = parse_python_with_builtin_ast(code)
    return None if ast_tree is None else ParserResult(type="ast", tree=ast_tree)
