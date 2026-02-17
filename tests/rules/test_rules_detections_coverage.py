from __future__ import annotations

from mcp_zen_of_languages.rules.tools.detections import (
    detect_deep_nesting,
    detect_long_functions,
    detect_magic_methods_overuse,
    detect_multiple_implementations,
    detect_sparse_code,
)


def test_rules_detection_helpers():
    assert detect_deep_nesting("if True:\n    if True:\n        pass\n", max_depth=0)[0]
    assert detect_long_functions("def foo():\n    pass\n", max_lines=0)
    assert detect_magic_methods_overuse("def __str__(self):\n    pass\n")
    assert detect_multiple_implementations(
        {"a.py": "def foo():\n    pass\n", "b.py": "def foo():\n    pass\n"}
    )
    assert detect_sparse_code("x = 1; y = 2", max_statements_per_line=1)
