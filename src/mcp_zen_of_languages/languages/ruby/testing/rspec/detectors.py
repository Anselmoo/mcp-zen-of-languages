"""RSpec violation detectors — regex-based, no AST required."""

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.models import Location
from mcp_zen_of_languages.models import Violation


_COMMENT_RE = re.compile(r"^\s*#")
_IT_ANON_RE = re.compile(r"^\s*it\s*(?:do\b|\{)")
_INSTANCE_VAR_RE = re.compile(r"@\w+\s*=")
_LET_BANG_RE = re.compile(r"^\s*let!\s*\(")
_BEFORE_ALL_RE = re.compile(r"^\s*before\s*\(\s*:all\s*\)")
_ANY_INSTANCE_RE = re.compile(r"\ballow_any_instance_of\b|\bexpect_any_instance_of\b")
_PENDING_RE = re.compile(r"^\s*pending\b")
_XIT_RE = re.compile(r"^\s*xit\b|^\s*xdescribe\b|^\s*xcontext\b")
_FOCUS_RE = re.compile(r"^\s*fit\b|^\s*fdescribe\b|^\s*fcontext\b")
_SHARED_DUP_RE = re.compile(r"^\s*it\s+['\"]")
_SUBJECT_IMPL_RE = re.compile(r"^\s*subject\s*\{|\s*subject\s*do")


class AnonItDetector(ViolationDetector[AnalyzerConfig]):
    """rspec-001: it blocks must have explicit descriptions."""

    @property
    def name(self) -> str:
        """Return "rspec-anon-it"."""
        return "rspec-anon-it"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _IT_ANON_RE.match(line):
                violations.append(
                    Violation(
                        principle="it blocks must have explicit descriptions",
                        severity=6,
                        message="Anonymous it block — add a description string.",
                        suggestion='it "does something specific" do',
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class InstanceVarInBeforeDetector(ViolationDetector[AnalyzerConfig]):
    """rspec-002: Use let not instance variables in examples."""

    @property
    def name(self) -> str:
        """Return "rspec-instance-var"."""
        return "rspec-instance-var"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        lines = context.code.splitlines()
        in_before = False
        for i, line in enumerate(lines, start=1):
            if _COMMENT_RE.match(line):
                continue
            if re.match(r"^\s*before\s*(?:\(|do)", line):
                in_before = True
            if in_before and _INSTANCE_VAR_RE.search(line):
                violations.append(
                    Violation(
                        principle="Use let not instance variables in examples",
                        severity=7,
                        message="Instance variable in before block — use let instead.",
                        suggestion="let(:name) { value } is lazy and clearly scoped.",
                        location=Location(line=i, column=1),
                    )
                )
            if (
                in_before
                and re.search(r"\bend\b", line)
                and not re.match(r"^\s*before", line)
            ):
                in_before = False
        return violations


class LetBangDetector(ViolationDetector[AnalyzerConfig]):
    """rspec-003: let! only when eager evaluation required."""

    @property
    def name(self) -> str:
        """Return "rspec-let-bang"."""
        return "rspec-let-bang"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _LET_BANG_RE.match(line):
                violations.append(
                    Violation(
                        principle="let! only when eager evaluation required",
                        severity=5,
                        message="let! forces eager evaluation — prefer lazy let unless side effects require it.",
                        suggestion="Replace let! with let unless the fixture must always be created.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class BeforeAllMutationDetector(ViolationDetector[AnalyzerConfig]):
    """rspec-006: before(:all) must not mutate shared state."""

    @property
    def name(self) -> str:
        """Return "rspec-before-all"."""
        return "rspec-before-all"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _BEFORE_ALL_RE.match(line):
                violations.append(
                    Violation(
                        principle="before(:all) must not mutate shared state",
                        severity=9,
                        message="before(:all) shares mutation across all examples — creates inter-test dependency.",
                        suggestion="Use before(:each) or database_cleaner strategies instead.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class AnyInstanceDetector(ViolationDetector[AnalyzerConfig]):
    """rspec-007: Avoid allow_any_instance_of."""

    @property
    def name(self) -> str:
        """Return "rspec-any-instance"."""
        return "rspec-any-instance"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _ANY_INSTANCE_RE.search(line):
                violations.append(
                    Violation(
                        principle="Avoid allow_any_instance_of",
                        severity=7,
                        message="allow_any_instance_of stubs all instances — use specific doubles.",
                        suggestion="Inject a specific instance double and stub that instead.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class PendingExampleDetector(ViolationDetector[AnalyzerConfig]):
    """rspec-008: Pending examples must not grow indefinitely."""

    @property
    def name(self) -> str:
        """Return "rspec-pending-example"."""
        return "rspec-pending-example"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _PENDING_RE.match(line) or _XIT_RE.match(line):
                violations.append(
                    Violation(
                        principle="Pending examples must not grow indefinitely",
                        severity=5,
                        message="Pending/skipped example — implement or delete at next sprint boundary.",
                        suggestion="Either implement the example or track it as a tech-debt issue.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations


class FocusMarkerDetector(ViolationDetector[AnalyzerConfig]):
    """rspec-010: Avoid focus markers in committed code."""

    @property
    def name(self) -> str:
        """Return "rspec-focus-marker"."""
        return "rspec-focus-marker"

    def detect(
        self, context: AnalysisContext, _config: AnalyzerConfig
    ) -> list[Violation]:
        """Detect violations and return them."""
        violations = []
        for i, line in enumerate(context.code.splitlines(), start=1):
            if _COMMENT_RE.match(line):
                continue
            if _FOCUS_RE.match(line):
                violations.append(
                    Violation(
                        principle="Avoid focus markers (fit, fdescribe) in committed code",
                        severity=8,
                        message="Focus marker found — CI runs only focused tests, skipping the rest.",
                        suggestion="Remove fit/fdescribe before committing; use tags for selective runs.",
                        location=Location(line=i, column=1),
                    )
                )
        return violations
