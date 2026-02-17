from __future__ import annotations

from mcp_zen_of_languages.rules import detections


def test_detect_deep_nesting_basic():
    code = "if True:\n    if True:\n        pass\n"
    is_deep, depth = detections.detect_deep_nesting(code, max_depth=0)
    assert is_deep
    assert depth >= 1


def test_detect_magic_methods_overuse():
    code = "def __str__(self):\n    pass\n"
    methods = detections.detect_magic_methods_overuse(code)
    assert methods


def test_detect_multiple_implementations():
    files = {"a.py": "def foo():\n    pass\n", "b.py": "def foo():\n    pass\n"}
    duplicates = detections.detect_multiple_implementations(files)
    assert duplicates
