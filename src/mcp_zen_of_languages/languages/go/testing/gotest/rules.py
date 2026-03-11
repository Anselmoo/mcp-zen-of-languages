"""Go testing zen principles as Pydantic models."""

from __future__ import annotations

from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
from mcp_zen_of_languages.rules.base_models import PrincipleCategory
from mcp_zen_of_languages.rules.base_models import ZenPrinciple


GOTEST_ZEN = LanguageZenPrinciples(
    language="gotest",
    name="Go testing",
    philosophy="Go testing Zen — fast, parallel, table-driven, and idiomatic Go tests",
    source_text="Go testing documentation and community best practices",
    principles=[
        ZenPrinciple(
            id="gotest-001",
            principle="Test functions must call t.Parallel() unless sharing a resource",
            category=PrincipleCategory.CORRECTNESS,
            severity=6,
            description=(
                "Parallel test execution significantly speeds up the test suite. "
                "Tests that do not share exclusive resources should declare themselves "
                "parallel with t.Parallel()."
            ),
            violations=[
                "func TestFoo(t *testing.T) { /* no t.Parallel() */ }",
            ],
            recommended_alternative="t.Parallel() as the first statement in test functions",
        ),
        ZenPrinciple(
            id="gotest-002",
            principle="Use table-driven tests for multiple input/output cases",
            category=PrincipleCategory.CORRECTNESS,
            severity=7,
            description=(
                "Go idiomatic testing uses a slice of struct test cases iterated in a "
                "loop with t.Run(). This pattern produces clear sub-test names and "
                "keeps related cases together."
            ),
            violations=[
                "Multiple near-identical test functions for the same function under test",
            ],
            recommended_alternative="tests := []struct{ in, want string }{{ ... }}\nfor _, tc := range tests { t.Run(tc.name, ...) }",
        ),
        ZenPrinciple(
            id="gotest-003",
            principle="Use t.Fatal only when setup failure makes test meaningless",
            category=PrincipleCategory.CORRECTNESS,
            severity=7,
            description=(
                "t.Fatal() stops the test immediately. Using it for assertion failures "
                "hides all remaining assertion results. Use t.Error() for assertions "
                "so all failures are visible in one run."
            ),
            violations=[
                "t.Fatal('expected X but got Y')  // stops at first failure",
            ],
            recommended_alternative="t.Error() for assertions; t.Fatal() only when setup fails",
        ),
        ZenPrinciple(
            id="gotest-004",
            principle="Helper functions must call t.Helper()",
            category=PrincipleCategory.READABILITY,
            severity=6,
            description=(
                "Without t.Helper(), error locations point to the helper function "
                "rather than the call site in the test, making failures hard to locate."
            ),
            violations=[
                "func assertEq(t *testing.T, ...) { /* missing t.Helper() */ }",
            ],
            recommended_alternative="t.Helper() as the first statement in test helper functions",
        ),
        ZenPrinciple(
            id="gotest-005",
            principle="Never call os.Exit in test code",
            category=PrincipleCategory.CORRECTNESS,
            severity=10,
            description=(
                "os.Exit() bypasses test cleanup (t.Cleanup, defer), prevents coverage "
                "flushing, and can leave the test binary in an inconsistent state. "
                "Use t.Fatal() or t.FailNow() instead."
            ),
            violations=[
                "os.Exit(1)  // in test or TestMain without proper cleanup",
            ],
            recommended_alternative="t.Fatal('setup failed') or t.FailNow()",
        ),
        ZenPrinciple(
            id="gotest-006",
            principle="time.Sleep must not appear in test functions",
            category=PrincipleCategory.CORRECTNESS,
            severity=8,
            description=(
                "time.Sleep introduces real delays, making tests slow and "
                "timing-sensitive. Use channel signals, polling with eventually "
                "helpers, or fake clock implementations."
            ),
            violations=[
                "time.Sleep(100 * time.Millisecond)  // real delay in test",
            ],
            recommended_alternative="Use channel synchronization or testclock library",
        ),
        ZenPrinciple(
            id="gotest-007",
            principle="Subtests must use t.Run with descriptive name",
            category=PrincipleCategory.READABILITY,
            severity=5,
            description=(
                "Unnamed or cryptically named subtests produce unreadable test output. "
                "t.Run names should clearly identify the scenario being tested."
            ),
            violations=[
                't.Run("", func(t *testing.T) { ... })  // empty name',
            ],
            recommended_alternative='t.Run("returns_error_on_invalid_input", func(t *testing.T) {...})',
        ),
        ZenPrinciple(
            id="gotest-008",
            principle="Use testify assert instead of manual if-statements",
            category=PrincipleCategory.IDIOMS,
            severity=5,
            description=(
                "Manual if err != nil checks in tests are verbose and produce poor "
                "failure messages. testify's assert package gives concise, "
                "human-readable output."
            ),
            violations=[
                "if got != want { t.Errorf(...) }",
            ],
            recommended_alternative="assert.Equal(t, want, got)",
        ),
        ZenPrinciple(
            id="gotest-009",
            principle="Avoid TestMain unless absolutely necessary",
            category=PrincipleCategory.ARCHITECTURE,
            severity=6,
            description=(
                "TestMain takes over the entire test lifecycle and is easy to "
                "misuse. It should only be used for package-level setup that cannot "
                "be expressed with t.Cleanup or sync.Once."
            ),
            violations=[
                "func TestMain(m *testing.M) { /* unnecessary global setup */ }",
            ],
            recommended_alternative="Use t.Cleanup() or package-level TestSetup helpers",
        ),
        ZenPrinciple(
            id="gotest-010",
            principle="Test functions must not use global mutable state",
            category=PrincipleCategory.ARCHITECTURE,
            severity=8,
            description=(
                "Global variables modified by tests create order-dependent behavior "
                "and break parallel test execution. Declare all test state inside "
                "the test function or in per-test fixtures."
            ),
            violations=[
                "var globalDB *DB  // modified by multiple tests",
            ],
            recommended_alternative="db := setupDB(t) inside each test function",
        ),
    ],
)
