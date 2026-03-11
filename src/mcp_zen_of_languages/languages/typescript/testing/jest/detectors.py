"""Jest/Vitest violation detectors — regex-based, no AST required."""

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.models import Location
from mcp_zen_of_languages.models import Violation


_COMMENT_RE = re.compile(r"^\s*//")
_TEST_BLOCK_RE = re.compile(r"^\s*(test|it)\s*\(")
_EXPECT_RE = re.compile(r"\bexpect\s*\(")
_DESCRIBE_RE = re.compile(r"^\s*describe\s*\(")
_DESCRIBE_EMPTY_RE = re.compile(
    r"^\s*describe\s*\([^)]+,\s*\(\s*\)\s*=>\s*\{\s*\}\s*\)"
)
_ASYNC_TEST_RE = re.compile(r"\b(test|it)\s*\([^,]+,\s*async\s*\(")
_SYNC_PROMISE_RE = re.compile(r"\b(test|it)\s*\([^,]+,\s*\(\s*\)\s*=>\s*\{")
_UNAWAITED_FETCH_RE = re.compile(r"(?<!await\s)\bfetch\s*\(|(?<!await\s)\baxios\.")
_FAKE_TIMER_RE = re.compile(r"\bjest\.useFakeTimers\(\)|vi\.useFakeTimers\(\)")
_SETTIMEOUT_RE = re.compile(r"\bsetTimeout\s*\(|\bsetInterval\s*\(")
_ASSERTIONS_ZERO_RE = re.compile(r"\bexpect\.assertions\s*\(\s*0\s*\)")
_VAGUE_TITLE_RE = re.compile(r"""['"](test\s*\d+|it\s+works|works|it|test)['"]\s*,""")
_RESTORE_MOCKS_RE = re.compile(
    r"\bjest\.(restoreAllMocks|resetAllMocks|clearAllMocks)\s*\(\)"
)
_SPY_ON_RE = re.compile(r"\bjest\.spyOn\s*\(")
_DEEP_DESCRIBE_RE = re.compile(r"^\s*describe\s*\(")
_MAX_DESCRIBE_DEPTH = 2


class NoExpectDetector(ViolationDetector[AnalyzerConfig]):
    """jest-001: Every test()/it() must contain at least one expect()."""

    @property
    def name(self) -> str:
        """Return "jest-no-expect"."""
        return "jest-no-expect"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        lines = context.code.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            if _COMMENT_RE.match(line):
                i += 1
                continue
            if _TEST_BLOCK_RE.match(line):
                test_start = i
                brace_depth = 0
                has_expect = False
                for j in range(i, min(i + 80, len(lines))):
                    brace_depth += lines[j].count("{") - lines[j].count("}")
                    if _EXPECT_RE.search(lines[j]):
                        has_expect = True
                    if j > test_start and brace_depth <= 0:
                        i = j
                        break
                if not has_expect:
                    violations.append(
                        Violation(
                            principle="Every test()/it() must contain at least one expect()",
                            severity=9,
                            message="Test block has no expect() call — it always passes.",
                            suggestion="Add expect(result).toBe(expectedValue)",
                            location=Location(line=test_start + 1, column=1),
                        )
                    )
            i += 1
        return violations


class UnawaitedPromiseDetector(ViolationDetector[AnalyzerConfig]):
    """jest-003: Async tests must await or return promises."""

    @property
    def name(self) -> str:
        """Return "jest-unawaited-promise"."""
        return "jest-unawaited-promise"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        lines = context.code.splitlines()
        for i, line in enumerate(lines, start=1):
            if _COMMENT_RE.match(line):
                continue
            if _UNAWAITED_FETCH_RE.search(line) and "await" not in line:
                violations.append(
                    Violation(
                        principle="Async tests must await or return promises",
                        severity=10,
                        message="Potentially un-awaited network/async call in test.",
                        suggestion="Add 'await' or return the promise so Jest waits for it.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class RealTimerInTestDetector(ViolationDetector[AnalyzerConfig]):
    """jest-005: setTimeout/setInterval must use fake timers in tests."""

    @property
    def name(self) -> str:
        """Return "jest-real-timer"."""
        return "jest-real-timer"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        # Only flag if fake timers are not set up in this file
        code = context.code
        if _FAKE_TIMER_RE.search(code):
            return []
        violations = []
        for i, line in enumerate(code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _SETTIMEOUT_RE.search(line):
                violations.append(
                    Violation(
                        principle="setTimeout/setInterval must use fake timers in tests",
                        severity=7,
                        message="Real timer in test — use jest.useFakeTimers() to control time.",
                        suggestion="Call jest.useFakeTimers() in beforeEach and jest.useRealTimers() in afterEach.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class EmptyDescribeDetector(ViolationDetector[AnalyzerConfig]):
    """jest-006: describe blocks must not be empty."""

    @property
    def name(self) -> str:
        """Return "jest-empty-describe"."""
        return "jest-empty-describe"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _DESCRIBE_EMPTY_RE.search(line):
                violations.append(
                    Violation(
                        principle="describe blocks must not be empty",
                        severity=5,
                        message="Empty describe block adds noise without coverage.",
                        suggestion="Add test cases or remove the describe block.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class AssertionsZeroDetector(ViolationDetector[AnalyzerConfig]):
    """jest-007: Avoid expect.assertions(0)."""

    @property
    def name(self) -> str:
        """Return "jest-assertions-zero"."""
        return "jest-assertions-zero"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _ASSERTIONS_ZERO_RE.search(line):
                violations.append(
                    Violation(
                        principle="Avoid expect.assertions(0)",
                        severity=7,
                        message="expect.assertions(0) asserts nothing was tested.",
                        suggestion="Remove expect.assertions(0) and add real assertions.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class VagueTitleDetector(ViolationDetector[AnalyzerConfig]):
    """jest-008: Test titles must describe expected behavior."""

    @property
    def name(self) -> str:
        """Return "jest-vague-title"."""
        return "jest-vague-title"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _VAGUE_TITLE_RE.search(line):
                violations.append(
                    Violation(
                        principle="Test titles must describe expected behavior",
                        severity=5,
                        message="Vague test title — name should describe the scenario.",
                        suggestion="Use it('returns 403 when user lacks permissions', ...)",
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class DeepDescribeDetector(ViolationDetector[AnalyzerConfig]):
    """jest-009: Avoid nested describe blocks deeper than 2 levels."""

    @property
    def name(self) -> str:
        """Return "jest-deep-describe"."""
        return "jest-deep-describe"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        depth = 0
        lines = context.code.splitlines()
        for i, line in enumerate(lines, start=1):
            if _COMMENT_RE.match(line):
                continue
            if _DEEP_DESCRIBE_RE.match(line):
                depth += 1
                if depth > _MAX_DESCRIBE_DEPTH:
                    violations.append(
                        Violation(
                            principle="Avoid nested describe blocks deeper than 2 levels",
                            severity=6,
                            message=f"describe nesting depth {depth} exceeds maximum of {_MAX_DESCRIBE_DEPTH}.",
                            suggestion="Flatten tests or split into multiple test files.",
                            location=Location(line=i, column=1),
                        )
                    )
            depth -= line.count("}") - line.count("{")
            depth = max(0, depth)
        return violations


class NoRestoreMocksDetector(ViolationDetector[AnalyzerConfig]):
    """jest-010: afterEach must restore all mocks."""

    @property
    def name(self) -> str:
        """Return "jest-no-restore-mocks"."""
        return "jest-no-restore-mocks"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        code = context.code
        if not _SPY_ON_RE.search(code):
            return []
        if _RESTORE_MOCKS_RE.search(code):
            return []
        spy_lines = [
            i + 1
            for i, line in enumerate(code.splitlines())
            if _SPY_ON_RE.search(line) and not _COMMENT_RE.match(line)
        ]
        if not spy_lines:
            return []
        return [
            Violation(
                principle="afterEach must restore all mocks",
                severity=8,
                message="jest.spyOn used without jest.restoreAllMocks() in afterEach.",
                suggestion="Add afterEach(() => jest.restoreAllMocks()) to this test file.",
                location=Location(line=spy_lines[0], column=1),
            )
        ]
