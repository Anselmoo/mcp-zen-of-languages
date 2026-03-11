"""Smoke tests for the Go testing (gotest) framework analyzer."""

from __future__ import annotations

from mcp_zen_of_languages.languages.go.testing.gotest import GoTestAnalyzer


ANALYZER = GoTestAnalyzer()

BAD_CODE_DESCRIPTION = (
    "Triggers: ParallelTestDetector (no t.Parallel), TimeSleepInTestDetector, "
    "FatalInAssertDetector, OsExitInTestDetector, EmptySubtestNameDetector, "
    "GlobalMutableStateDetector, MissingTHelperDetector"
)
BAD_CODE = """\
package myservice_test

import (
\t"os"
\t"testing"
\t"time"
)

var globalDB *Database

func TestSomething(t *testing.T) {
\ttime.Sleep(100 * time.Millisecond)
\tt.Fatalf("expected 42")
}

func TestOther(t *testing.T) {
\tos.Exit(1)
}

func TestWithEmptySubtest(t *testing.T) {
\tt.Parallel()
\tt.Run("", func(t *testing.T) {
\t\tt.Log("unnamed subtest")
\t})
}

func helperSetup(t *testing.T) {
\tif result := doSomething(); result != 42 {
\t\tt.Error("wrong value")
\t}
}
"""

CLEAN_CODE_DESCRIPTION = "A well-written Go test file with no violations."
CLEAN_CODE = """\
package math_test

import (
\t"testing"
)

func TestAddition(t *testing.T) {
\tt.Parallel()
\tresult := 1 + 1
\tif result != 2 {
\t\tt.Errorf("expected 2, got %d", result)
\t}
}

func TestSubtraction(t *testing.T) {
\tt.Parallel()
\tresult := 5 - 3
\tif result != 2 {
\t\tt.Errorf("expected 2, got %d", result)
\t}
}
"""

HELPER_CODE_DESCRIPTION = "Code with a properly implemented helper that has t.Helper()."
HELPER_CLEAN_CODE = """\
package service_test

import "testing"

func assertEqual(t *testing.T, want, got int) {
\tt.Helper()
\tif want != got {
\t\tt.Errorf("want %d got %d", want, got)
\t}
}

func TestService(t *testing.T) {
\tt.Parallel()
\tassertEqual(t, 42, computeAnswer())
}
"""

COMMENT_CODE_DESCRIPTION = (
    "Code that has a comment containing os.Exit — must NOT trigger the detector."
)
COMMENTED_BAD_CODE = """\
package example_test

import "testing"

// os.Exit(1) is documented here as something NOT to do.
func TestCommented(t *testing.T) {
\tt.Parallel()
\tt.Log("nothing bad here")
}
"""


class TestGoTestAnalyzerFileDetection:
    """is_test_file() correctly identifies Go test files."""

    def test_is_test_file_matches_test_go_suffix(self) -> None:
        assert ANALYZER.is_test_file("foo_test.go") is True

    def test_is_test_file_matches_nested_path(self) -> None:
        assert ANALYZER.is_test_file("pkg/service/user_test.go") is True

    def test_is_test_file_no_match_plain_go(self) -> None:
        assert ANALYZER.is_test_file("main.go") is False

    def test_is_test_file_no_match_other_extension(self) -> None:
        assert ANALYZER.is_test_file("foo_test.py") is False

    def test_is_test_file_no_match_test_go_in_dirname(self) -> None:
        # Directory named *_test, but not a .go file.
        assert ANALYZER.is_test_file("mypackage_test/main.go") is False


class TestGoTestAnalyzerMetadata:
    """Analyzer metadata is correct."""

    def test_language(self) -> None:
        assert ANALYZER.language() == "gotest"

    def test_parent_language(self) -> None:
        assert ANALYZER.parent_language == "go"


class TestGoTestBadCodeViolations:
    """BAD Go test code produces the expected violations."""

    def test_bad_code_produces_violations(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="pkg/service_test.go")
        assert len(result.violations) > 0

    def test_detects_missing_parallel(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="pkg/service_test.go")
        principles = [v.principle for v in result.violations]
        assert any("Parallel" in p for p in principles)

    def test_detects_time_sleep(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="pkg/service_test.go")
        principles = [v.principle for v in result.violations]
        assert any("Sleep" in p or "sleep" in p for p in principles)

    def test_detects_fatal_in_assert(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="pkg/service_test.go")
        principles = [v.principle for v in result.violations]
        assert any("Fatal" in p for p in principles)

    def test_detects_os_exit(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="pkg/service_test.go")
        principles = [v.principle for v in result.violations]
        assert any("os.Exit" in p or "Exit" in p for p in principles)

    def test_detects_global_mutable_state(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="pkg/service_test.go")
        principles = [v.principle for v in result.violations]
        assert any("global" in p.lower() or "mutable" in p.lower() for p in principles)

    def test_detects_empty_subtest_name(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="pkg/service_test.go")
        principles = [v.principle for v in result.violations]
        assert any(
            "Subtest" in p or "subtest" in p or "descriptive" in p.lower()
            for p in principles
        )

    def test_detects_missing_t_helper(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="pkg/service_test.go")
        principles = [v.principle for v in result.violations]
        assert any("Helper" in p or "helper" in p.lower() for p in principles)

    def test_violations_have_locations(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="pkg/service_test.go")
        for violation in result.violations:
            assert violation.location is not None
            assert violation.location.line >= 1


class TestGoTestCleanCode:
    """CLEAN Go test code produces no violations."""

    def test_clean_code_produces_no_violations(self) -> None:
        result = ANALYZER.analyze(CLEAN_CODE, path="math/math_test.go")
        assert len(result.violations) == 0

    def test_helper_with_t_helper_no_violation(self) -> None:
        result = ANALYZER.analyze(HELPER_CLEAN_CODE, path="svc/service_test.go")
        assert len(result.violations) == 0

    def test_comment_line_not_flagged(self) -> None:
        """Patterns inside comments must not trigger detectors."""
        result = ANALYZER.analyze(COMMENTED_BAD_CODE, path="pkg/example_test.go")
        assert len(result.violations) == 0


class TestGoTestIndividualDetectors:
    """Targeted tests for each detector in isolation."""

    def test_parallel_only_violation_single_func(self) -> None:
        code = 'func TestFoo(t *testing.T) {\n\tt.Log("no parallel")\n}\n'
        result = ANALYZER.analyze(code, path="foo_test.go")
        principles = [v.principle for v in result.violations]
        assert any("Parallel" in p for p in principles)

    def test_no_parallel_violation_when_present(self) -> None:
        code = 'func TestFoo(t *testing.T) {\n\tt.Parallel()\n\tt.Log("ok")\n}\n'
        result = ANALYZER.analyze(code, path="foo_test.go")
        principles = [v.principle for v in result.violations]
        assert not any("Parallel" in p for p in principles)

    def test_fatalf_triggers_violation(self) -> None:
        code = 'func TestX(t *testing.T) {\n\tt.Fatalf("boom")\n}\n'
        result = ANALYZER.analyze(code, path="x_test.go")
        principles = [v.principle for v in result.violations]
        assert any("Fatal" in p for p in principles)

    def test_os_exit_triggers_violation(self) -> None:
        code = "func TestX(t *testing.T) {\n\tos.Exit(2)\n}\n"
        result = ANALYZER.analyze(code, path="x_test.go")
        principles = [v.principle for v in result.violations]
        assert any("os.Exit" in p or "Exit" in p for p in principles)

    def test_time_sleep_triggers_violation(self) -> None:
        code = "func TestX(t *testing.T) {\n\ttime.Sleep(time.Second)\n}\n"
        result = ANALYZER.analyze(code, path="x_test.go")
        principles = [v.principle for v in result.violations]
        assert any("Sleep" in p or "sleep" in p for p in principles)

    def test_empty_subtest_name_triggers_violation(self) -> None:
        code = (
            "func TestX(t *testing.T) {\n"
            "\tt.Parallel()\n"
            '\tt.Run("", func(t *testing.T) {})\n'
            "}\n"
        )
        result = ANALYZER.analyze(code, path="x_test.go")
        principles = [v.principle for v in result.violations]
        assert any(
            "Subtest" in p or "subtest" in p or "name" in p.lower() for p in principles
        )

    def test_global_pointer_triggers_violation(self) -> None:
        code = "var db *DB\n\nfunc TestX(t *testing.T) {\n\tt.Parallel()\n}\n"
        result = ANALYZER.analyze(code, path="x_test.go")
        principles = [v.principle for v in result.violations]
        assert any("global" in p.lower() or "mutable" in p.lower() for p in principles)

    def test_missing_t_helper_triggers_violation(self) -> None:
        code = (
            "func assertThing(t *testing.T, val int) {\n"
            "\tif val != 42 {\n"
            '\t\tt.Error("wrong")\n'
            "\t}\n"
            "}\n"
        )
        result = ANALYZER.analyze(code, path="helpers_test.go")
        principles = [v.principle for v in result.violations]
        assert any("Helper" in p or "helper" in p.lower() for p in principles)
