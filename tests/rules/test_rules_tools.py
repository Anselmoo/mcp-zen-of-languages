from __future__ import annotations

from mcp_zen_of_languages.rules.tools import detections


def test_detect_long_functions():
    code = "def foo():\n" + "\n".join(["    x = 1"] * 30) + "\n"
    results = detections.detect_long_functions(code, max_lines=10)
    assert results


def test_detect_god_classes():
    methods = [f"    def m{i}(self):\n        pass" for i in range(12)]
    code = "class Foo:\n" + "\n".join(methods)
    results = detections.detect_god_classes(code, max_methods=5, max_lines=10)
    assert results


def test_detect_deep_inheritance():
    code_map = {
        "a.py": "class A: pass\nclass B(A): pass\nclass C(B): pass\nclass D(C): pass",
    }
    results = detections.detect_deep_inheritance(code_map, max_depth=1)
    assert results


def test_detect_deep_inheritance_handles_multiple_parents():
    code_map = {
        "a.py": "class A: pass\nclass B(A): pass\nclass C(A, B): pass",
    }
    results = detections.detect_deep_inheritance(code_map, max_depth=0)
    assert any(result.chain[0] == "B" for result in results)
    assert any(result.chain[0] == "C" for result in results)


def test_detect_inconsistent_naming_styles():
    code = "def foo():\n    pass\n\ndef Bar():\n    pass\n"
    results = detections.detect_inconsistent_naming_styles(code)
    assert results
    assert "PascalCase" in results[0].naming_styles


def test_detect_feature_envy_prefers_other_refs():
    code = """
class Alpha:
    def foo(self):
        other.bar
        other.baz
"""
    results = detections.detect_feature_envy(code)
    assert results
    assert results[0].target_class == "other"


def test_detect_dependency_cycles():
    edges = [("a", "b"), ("b", "c"), ("c", "a")]
    results = detections.detect_dependency_cycles(edges)
    assert results
    assert all(result.cycle for result in results)


def test_detect_sparse_code_ignores_comments():
    code = "# a = 1; b = 2\na = 1; b = 2\n"
    results = detections.detect_sparse_code(code, max_statements_per_line=1)
    assert len(results) == 1
    assert results[0].line == 2


def test_detect_missing_type_hints_handles_syntax_error():
    assert detections.detect_missing_type_hints("def foo(") == []


def test_detect_namespace_usage_handles_parse_error():
    result = detections.detect_namespace_usage("def foo(")
    assert result.top_level_symbols == 0
    assert result.export_count is None
