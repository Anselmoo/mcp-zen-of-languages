"""Tests for the framework analyzer bridge (FrameworkRegistry, FrameworkAnalyzer)."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import DetectionPipeline
from mcp_zen_of_languages.analyzers.framework_bridge import FrameworkAnalyzer
from mcp_zen_of_languages.analyzers.framework_bridge import FrameworkRegistry


class _DummyAnalyzer(FrameworkAnalyzer):
    test_file_patterns = (r"test_.*\.py$",)
    parent_language = "python"

    def language(self) -> str:
        return "dummy"

    def build_pipeline(self) -> DetectionPipeline:
        return DetectionPipeline(detectors=[])


class _AnotherAnalyzer(FrameworkAnalyzer):
    test_file_patterns = (r".*\.spec\.ts$",)
    parent_language = "typescript"

    def language(self) -> str:
        return "another"

    def build_pipeline(self) -> DetectionPipeline:
        return DetectionPipeline(detectors=[])


class TestFrameworkRegistry:
    def test_register_and_count(self) -> None:
        reg = FrameworkRegistry()
        reg.register(_DummyAnalyzer)
        assert reg.registered_count() == 1

    def test_duplicate_registration_ignored(self) -> None:
        reg = FrameworkRegistry()
        reg.register(_DummyAnalyzer)
        reg.register(_DummyAnalyzer)
        assert reg.registered_count() == 1

    def test_get_frameworks_by_language_and_path(self) -> None:
        reg = FrameworkRegistry()
        reg.register(_DummyAnalyzer)
        reg.register(_AnotherAnalyzer)

        results = reg.get_frameworks("python", "tests/test_auth.py")
        assert len(results) == 1
        assert isinstance(results[0], _DummyAnalyzer)

    def test_get_frameworks_wrong_language(self) -> None:
        reg = FrameworkRegistry()
        reg.register(_DummyAnalyzer)
        results = reg.get_frameworks("ruby", "tests/test_auth.py")
        assert results == []

    def test_get_frameworks_no_match_path(self) -> None:
        reg = FrameworkRegistry()
        reg.register(_DummyAnalyzer)
        results = reg.get_frameworks("python", "src/auth.py")
        assert results == []

    def test_get_frameworks_none_path(self) -> None:
        reg = FrameworkRegistry()
        reg.register(_DummyAnalyzer)
        results = reg.get_frameworks("python", None)
        assert results == []

    def test_iter(self) -> None:
        reg = FrameworkRegistry()
        reg.register(_DummyAnalyzer)
        reg.register(_AnotherAnalyzer)
        classes = list(reg)
        assert _DummyAnalyzer in classes
        assert _AnotherAnalyzer in classes


class TestFrameworkAnalyzer:
    def test_is_test_file_matches(self) -> None:
        analyzer = _DummyAnalyzer()
        assert analyzer.is_test_file("tests/test_auth.py") is True
        assert analyzer.is_test_file("test_utils.py") is True

    def test_is_test_file_no_match(self) -> None:
        analyzer = _DummyAnalyzer()
        assert analyzer.is_test_file("src/auth.py") is False

    def test_is_test_file_none(self) -> None:
        analyzer = _DummyAnalyzer()
        assert analyzer.is_test_file(None) is False

    def test_language(self) -> None:
        analyzer = _DummyAnalyzer()
        assert analyzer.language() == "dummy"

    def test_parse_code_returns_none(self) -> None:
        analyzer = _DummyAnalyzer()
        assert analyzer.parse_code("def foo(): pass") is None

    def test_compute_metrics_returns_line_count(self) -> None:
        analyzer = _DummyAnalyzer()
        _, _, loc = analyzer.compute_metrics("line1\nline2\nline3", None)
        assert loc == 3

    def test_analyze_returns_result(self) -> None:
        analyzer = _DummyAnalyzer()
        result = analyzer.analyze("def test_foo(): pass")
        assert result is not None
