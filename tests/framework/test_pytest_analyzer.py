"""Smoke tests for the pytest framework analyzer."""

from __future__ import annotations

from mcp_zen_of_languages.languages.python.testing.pytest import PytestAnalyzer


ANALYZER = PytestAnalyzer()

BAD_CODE = """\
import time
from unittest import TestCase


mock = MagicMock()


class MyTests(TestCase):
    def test_1(self):
        self.assertEqual(1, 1)
        time.sleep(0.1)
        for item in [1, 2, 3]:
            assert item > 0

    def test_2(self):
        call_something()
"""

CLEAN_CODE = """\
import pytest


def test_addition_returns_correct_sum():
    result = 1 + 1
    assert result == 2


def test_subtraction():
    assert 5 - 3 == 2
"""


class TestPytestAnalyzer:
    def test_is_test_file_matches_test_prefix(self) -> None:
        assert ANALYZER.is_test_file("tests/test_auth.py") is True

    def test_is_test_file_matches_test_suffix(self) -> None:
        assert ANALYZER.is_test_file("auth_test.py") is True

    def test_is_test_file_matches_conftest(self) -> None:
        assert ANALYZER.is_test_file("conftest.py") is True

    def test_is_test_file_no_match(self) -> None:
        assert ANALYZER.is_test_file("src/auth.py") is False

    def test_language(self) -> None:
        assert ANALYZER.language() == "pytest"

    def test_parent_language(self) -> None:
        assert ANALYZER.parent_language == "python"

    def test_bad_code_produces_violations(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="tests/test_foo.py")
        assert len(result.violations) > 0

    def test_bad_code_detects_unittest_assert(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="tests/test_foo.py")
        principles = [v.principle for v in result.violations]
        assert any("assertEqual" in p or "directly" in p for p in principles)

    def test_bad_code_detects_sleep(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="tests/test_foo.py")
        principles = [v.principle for v in result.violations]
        assert any("sleep" in p.lower() for p in principles)

    def test_bad_code_detects_vague_test_name(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="tests/test_foo.py")
        principles = [v.principle for v in result.violations]
        assert any("name" in p.lower() or "behav" in p.lower() for p in principles)

    def test_clean_code_produces_no_violations(self) -> None:
        result = ANALYZER.analyze(CLEAN_CODE, path="tests/test_clean.py")
        assert len(result.violations) == 0

    def test_no_assert_detected(self) -> None:
        code = "def test_foo():\n    call_something()\n"
        result = ANALYZER.analyze(code, path="tests/test_foo.py")
        principles = [v.principle for v in result.violations]
        assert any("assert" in p.lower() for p in principles)
