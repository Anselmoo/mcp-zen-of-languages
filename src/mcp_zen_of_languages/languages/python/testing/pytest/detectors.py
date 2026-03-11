"""Pytest violation detectors — regex-based, no AST required."""

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.models import Location
from mcp_zen_of_languages.models import Violation


_UNITTEST_ASSERT_RE = re.compile(
    r"\bself\.(assertEqual|assertTrue|assertFalse|assertIs|assertIn|assertRaises|"
    r"assertNotEqual|assertIsNone|assertIsNotNone|assertIsInstance)\s*\("
)
_SLEEP_RE = re.compile(r"\btime\.sleep\s*\(")
_ASYNCIO_SLEEP_RE = re.compile(r"\bawait\s+asyncio\.sleep\s*\(")
_FOR_ASSERT_RE = re.compile(r"^\s*for\s+.+:$")
_INLINE_ASSERT_RE = re.compile(r"\bassert\b")
_COMMENT_RE = re.compile(r"^\s*#")
_DEF_TEST_RE = re.compile(r"^\s*def\s+(test_\w+)\s*\(")
_BARE_EXCEPT_RE = re.compile(r"^\s*except\s*:")
_BROAD_EXCEPT_RE = re.compile(r"^\s*except\s+Exception\s*:")
_MODULE_MOCK_RE = re.compile(r"^mock\s*=\s*MagicMock\s*\(|^patch\(")
_TRY_FOO_EXCEPT_RE = re.compile(r"^\s*try\s*:")
_TEST_NAME_VAGUE_RE = re.compile(r"^\s*def\s+(test_[0-9]+|test_it|test_thing\d*)\s*\(")


class UnittestAssertDetector(ViolationDetector[AnalyzerConfig]):
    """pytest-001: Use assert directly instead of unittest-style methods."""

    @property
    def name(self) -> str:
        """Return "pytest-unittest-assert"."""
        return "pytest-unittest-assert"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            m = _UNITTEST_ASSERT_RE.search(line)
            if m:
                violations.append(
                    Violation(
                        principle="Use assert directly — never assertEqual-style",
                        severity=6,
                        message=(
                            f"Unittest-style assertion '{m.group(1)}()' found. "
                            "Use plain assert for pytest-native output."
                        ),
                        suggestion="Replace with assert <expression>",
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class SleepInTestDetector(ViolationDetector[AnalyzerConfig]):
    """pytest-003: Tests must not call time.sleep()."""

    @property
    def name(self) -> str:
        """Return "pytest-sleep-in-test"."""
        return "pytest-sleep-in-test"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _SLEEP_RE.search(line) or _ASYNCIO_SLEEP_RE.search(line):
                violations.append(
                    Violation(
                        principle="Tests must not call time.sleep()",
                        severity=8,
                        message="Real sleep in test code makes the suite slow and timing-sensitive.",
                        suggestion="Use freezegun or pytest-mock time mocking instead.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class LoopInTestDetector(ViolationDetector[AnalyzerConfig]):
    """pytest-004: Parametrize instead of looping in test body."""

    @property
    def name(self) -> str:
        """Return "pytest-loop-in-test"."""
        return "pytest-loop-in-test"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        lines = context.code.splitlines()
        inside_test = False
        test_indent = 0
        for i, line in enumerate(lines, start=1):
            if _COMMENT_RE.match(line):
                continue
            m = _DEF_TEST_RE.match(line)
            if m:
                inside_test = True
                test_indent = len(line) - len(line.lstrip())
                continue
            if inside_test:
                stripped = line.lstrip()
                if stripped and (len(line) - len(stripped)) <= test_indent and i > 1:
                    inside_test = False
                    continue
                m_for = _FOR_ASSERT_RE.match(line)
                if m_for:
                    # Check if the next non-empty line has an assert
                    for j in range(i, min(i + 5, len(lines))):
                        if _INLINE_ASSERT_RE.search(lines[j]):
                            violations.append(
                                Violation(
                                    principle="Parametrize instead of looping in test body",
                                    severity=7,
                                    message=(
                                        "Loop with assertions in test body detected. "
                                        "A single failure hides subsequent cases."
                                    ),
                                    suggestion="Use @pytest.mark.parametrize instead.",
                                    location=Location(line=i, column=1),
                                )
                            )
                            break
        return violations


class NoAssertInTestDetector(ViolationDetector[AnalyzerConfig]):
    """pytest-005: Each test must contain at least one assert."""

    @property
    def name(self) -> str:
        """Return "pytest-no-assert"."""
        return "pytest-no-assert"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        lines = context.code.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            m = _DEF_TEST_RE.match(line)
            if m:
                test_name = m.group(1)
                def_indent = len(line) - len(line.lstrip())
                test_start = i
                has_assert = False
                i += 1
                while i < len(lines):
                    inner = lines[i]
                    stripped = inner.lstrip()
                    if (
                        stripped
                        and (len(inner) - len(stripped)) <= def_indent
                        and i > test_start
                    ):
                        break
                    if _INLINE_ASSERT_RE.search(inner) or re.search(
                        r"\bpytest\.raises\b", inner
                    ):
                        has_assert = True
                        break
                    i += 1
                if not has_assert:
                    violations.append(
                        Violation(
                            principle="Each test must contain at least one assert",
                            severity=9,
                            message=f"Test function '{test_name}' has no assertions.",
                            suggestion="Add assert <condition> to verify the expected outcome.",
                            location=Location(line=test_start + 1, column=1),
                        )
                    )
                continue
            i += 1
        return violations


class VagueTestNameDetector(ViolationDetector[AnalyzerConfig]):
    """pytest-006: Test function names must describe behavior."""

    @property
    def name(self) -> str:
        """Return "pytest-vague-test-name"."""
        return "pytest-vague-test-name"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            m = _TEST_NAME_VAGUE_RE.match(line)
            if m:
                violations.append(
                    Violation(
                        principle="Test function names must describe behavior",
                        severity=5,
                        message=f"Vague test name '{m.group(1)}' — name should read as behavior.",
                        suggestion="Rename to describe the scenario, e.g. test_login_fails_with_wrong_password.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class BareExceptInTestDetector(ViolationDetector[AnalyzerConfig]):
    """pytest-007: Avoid bare except in test body."""

    @property
    def name(self) -> str:
        """Return "pytest-bare-except"."""
        return "pytest-bare-except"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _BARE_EXCEPT_RE.match(line) or _BROAD_EXCEPT_RE.match(line):
                violations.append(
                    Violation(
                        principle="Avoid bare except in test body",
                        severity=8,
                        message="Bare or broad except clause may swallow test framework exceptions.",
                        suggestion="Use pytest.raises(SpecificError) for expected exceptions.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class PytestRaisesDetector(ViolationDetector[AnalyzerConfig]):
    """pytest-009: Use pytest.raises for expected exceptions."""

    @property
    def name(self) -> str:
        """Return "pytest-use-raises"."""
        return "pytest-use-raises"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        lines = context.code.splitlines()
        for i, line in enumerate(lines, start=1):
            if _COMMENT_RE.match(line):
                continue
            if _TRY_FOO_EXCEPT_RE.match(line):
                # Look-ahead: if the except doesn't use pytest.raises, flag it
                for j in range(i, min(i + 10, len(lines))):
                    inner = lines[j]
                    if (
                        re.match(r"^\s*except\s+\w+", inner)
                        and "pytest.raises" not in inner
                    ):
                        violations.append(
                            Violation(
                                principle="Use pytest.raises for expected exceptions",
                                severity=6,
                                message=(
                                    "try/except pattern detected. If this is testing "
                                    "for an expected exception, use pytest.raises() instead."
                                ),
                                suggestion="with pytest.raises(SpecificError): call_code()",
                                location=Location(line=i, column=1),
                            )
                        )
                        break
                    if re.match(r"^\s*except\b", inner):
                        break
        return violations


class ModuleLevelMockDetector(ViolationDetector[AnalyzerConfig]):
    """pytest-010: Mocked objects must be scoped to the test that needs them."""

    @property
    def name(self) -> str:
        """Return "pytest-module-level-mock"."""
        return "pytest-module-level-mock"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        # Only flag module-level mock assignments (indent = 0)
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if (
                _MODULE_MOCK_RE.match(line.strip())
                and not line.startswith(" ")
                and not line.startswith("\t")
            ):
                violations.append(
                    Violation(
                        principle="Mocked objects must be scoped to the test that needs them",
                        severity=7,
                        message="Module-level mock may bleed state between tests.",
                        suggestion="Use mocker fixture or monkeypatch inside the test function.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations
