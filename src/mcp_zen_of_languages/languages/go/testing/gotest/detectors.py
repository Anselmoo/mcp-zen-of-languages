"""Go testing violation detectors — regex-based, no AST required."""

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.models import Location
from mcp_zen_of_languages.models import Violation


_COMMENT_RE = re.compile(r"^\s*//")
_TEST_FUNC_RE = re.compile(r"^func\s+(Test\w+)\s*\(\s*t\s+\*testing\.T\s*\)")
_PARALLEL_RE = re.compile(r"\bt\.Parallel\(\)")
_SUBTEST_RE = re.compile(r"\bt\.Run\s*\(")
_EMPTY_SUBTEST_NAME_RE = re.compile(r'\bt\.Run\s*\(\s*""')
_FATAL_ASSERT_RE = re.compile(r"\bt\.Fatalf?\s*\(")
_T_HELPER_RE = re.compile(r"\bt\.Helper\(\)")
_HELPER_FUNC_RE = re.compile(r"^func\s+\w+\s*\(\s*t\s+\*testing\.T")
_OS_EXIT_RE = re.compile(r"\bos\.Exit\s*\(")
_TIME_SLEEP_RE = re.compile(r"\btime\.Sleep\s*\(")
_TEST_MAIN_RE = re.compile(r"^func\s+TestMain\s*\(")
_GLOBAL_VAR_RE = re.compile(r"^var\s+\w+\s+\*")
_ASSERT_MANUAL_RE = re.compile(
    r"\bif\s+got\s*!=\s*want\b|\bif\s+err\s*!=\s*nil\s*\{.*t\.Error"
)


class ParallelTestDetector(ViolationDetector[AnalyzerConfig]):
    """gotest-001: Test functions must call t.Parallel() unless sharing a resource."""

    @property
    def name(self) -> str:
        """Return "gotest-parallel"."""
        return "gotest-parallel"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        lines = context.code.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            m = _TEST_FUNC_RE.match(line)
            if m:
                test_name = m.group(1)
                test_start = i
                brace_depth = 0
                has_parallel = False
                for j in range(i, min(i + 60, len(lines))):
                    brace_depth += lines[j].count("{") - lines[j].count("}")
                    if _PARALLEL_RE.search(lines[j]):
                        has_parallel = True
                    if j > test_start and brace_depth <= 0:
                        i = j
                        break
                if not has_parallel:
                    violations.append(
                        Violation(
                            principle="Test functions must call t.Parallel() unless sharing a resource",
                            severity=6,
                            message=f"{test_name} does not call t.Parallel().",
                            suggestion="Add t.Parallel() as the first statement if no exclusive resource is used.",
                            location=Location(line=test_start + 1, column=1),
                        )
                    )
            i += 1
        return violations


class FatalInAssertDetector(ViolationDetector[AnalyzerConfig]):
    """gotest-003: Use t.Fatal only when setup failure makes test meaningless."""

    @property
    def name(self) -> str:
        """Return "gotest-fatal-assert"."""
        return "gotest-fatal-assert"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _FATAL_ASSERT_RE.search(line):
                violations.append(
                    Violation(
                        principle="Use t.Fatal only when setup failure makes test meaningless",
                        severity=7,
                        message="t.Fatal() stops the test immediately — subsequent failures are hidden.",
                        suggestion="Use t.Error() for assertions so all failures are visible.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class MissingTHelperDetector(ViolationDetector[AnalyzerConfig]):
    """gotest-004: Helper functions must call t.Helper()."""

    @property
    def name(self) -> str:
        """Return "gotest-missing-t-helper"."""
        return "gotest-missing-t-helper"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        lines = context.code.splitlines()
        for i, line in enumerate(lines, start=1):
            if _COMMENT_RE.match(line):
                continue
            m = _HELPER_FUNC_RE.match(line)
            if m and not _TEST_FUNC_RE.match(line) and not _TEST_MAIN_RE.match(line):
                # Check first few lines for t.Helper()
                has_helper = any(
                    _T_HELPER_RE.search(lines[j])
                    for j in range(i, min(i + 5, len(lines)))
                )
                if not has_helper:
                    violations.append(
                        Violation(
                            principle="Helper functions must call t.Helper()",
                            severity=6,
                            message="Test helper function missing t.Helper() call.",
                            suggestion="Add t.Helper() as the first statement in the helper.",
                            location=Location(line=i, column=1),
                        )
                    )
        return violations


class OsExitInTestDetector(ViolationDetector[AnalyzerConfig]):
    """gotest-005: Never call os.Exit in test code."""

    @property
    def name(self) -> str:
        """Return "gotest-os-exit"."""
        return "gotest-os-exit"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _OS_EXIT_RE.search(line):
                violations.append(
                    Violation(
                        principle="Never call os.Exit in test code",
                        severity=10,
                        message="os.Exit() in test bypasses cleanup and coverage flushing.",
                        suggestion="Use t.Fatal() or t.FailNow() instead.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class TimeSleepInTestDetector(ViolationDetector[AnalyzerConfig]):
    """gotest-006: time.Sleep must not appear in test functions."""

    @property
    def name(self) -> str:
        """Return "gotest-time-sleep"."""
        return "gotest-time-sleep"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _TIME_SLEEP_RE.search(line):
                violations.append(
                    Violation(
                        principle="time.Sleep must not appear in test functions",
                        severity=8,
                        message="time.Sleep in test makes suite slow and timing-sensitive.",
                        suggestion="Use channel synchronization or a fake clock library.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class EmptySubtestNameDetector(ViolationDetector[AnalyzerConfig]):
    """gotest-007: Subtests must use t.Run with descriptive name."""

    @property
    def name(self) -> str:
        """Return "gotest-empty-subtest-name"."""
        return "gotest-empty-subtest-name"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _EMPTY_SUBTEST_NAME_RE.search(line):
                violations.append(
                    Violation(
                        principle="Subtests must use t.Run with descriptive name",
                        severity=5,
                        message="t.Run with empty name produces unreadable test output.",
                        suggestion='t.Run("returns_error_on_invalid_input", func(t *testing.T) {...})',
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class GlobalMutableStateDetector(ViolationDetector[AnalyzerConfig]):
    """gotest-010: Test functions must not use global mutable state."""

    @property
    def name(self) -> str:
        """Return "gotest-global-state"."""
        return "gotest-global-state"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _GLOBAL_VAR_RE.match(line):
                violations.append(
                    Violation(
                        principle="Test functions must not use global mutable state",
                        severity=8,
                        message="Global pointer variable may be mutated by multiple tests.",
                        suggestion="Declare test state inside each test function or use t.Cleanup.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations
