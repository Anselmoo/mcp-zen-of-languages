from __future__ import annotations

import sys
import types

from mcp_zen_of_languages.utils import parsers
from mcp_zen_of_languages.utils.parsers import parse_python


def test_parse_python_success():
    tree = parse_python("def foo():\n    pass\n")
    assert tree


def test_parse_python_failure():
    tree = parse_python("def foo(")
    assert tree is None


def test_parse_python_prefers_treesitter(monkeypatch):
    monkeypatch.setattr(parsers, "parse_python_with_treesitter", lambda _: object())
    tree = parse_python("def foo():\n    pass\n")
    assert tree
    assert tree.type == "tree-sitter"


def test_parse_python_with_treesitter_success(monkeypatch):
    class FakeParser:
        def set_language(self, _):
            return None

        def parse(self, _):
            return "tree"

    fake_tree_sitter = types.SimpleNamespace(Parser=FakeParser)
    fake_build = types.SimpleNamespace(PY_LANGUAGE=object())
    monkeypatch.setitem(sys.modules, "tree_sitter", fake_tree_sitter)
    monkeypatch.setitem(sys.modules, "build", types.ModuleType("build"))
    monkeypatch.setitem(sys.modules, "build.my_languages", fake_build)
    tree = parsers.parse_python_with_treesitter("def foo():\n    pass\n")
    assert tree == "tree"


def test_parse_python_with_treesitter_without_set_language(monkeypatch):
    class FakeParser:
        def parse(self, _):
            return "tree"

    fake_tree_sitter = types.SimpleNamespace(Parser=FakeParser)
    fake_build = types.SimpleNamespace(PY_LANGUAGE=object())
    monkeypatch.setitem(sys.modules, "tree_sitter", fake_tree_sitter)
    monkeypatch.setitem(sys.modules, "build", types.ModuleType("build"))
    monkeypatch.setitem(sys.modules, "build.my_languages", fake_build)

    tree = parsers.parse_python_with_treesitter("def foo():\n    pass\n")
    assert tree is None
