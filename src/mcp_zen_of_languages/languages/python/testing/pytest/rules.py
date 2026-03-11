"""Pytest zen principles as Pydantic models."""

from __future__ import annotations

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
from mcp_zen_of_languages.rules.base_models import PrincipleCategory
from mcp_zen_of_languages.rules.base_models import ZenPrinciple


PYTEST_ZEN = LanguageZenPrinciples(
    language="pytest",
    name="pytest",
    philosophy="pytest Zen — idiomatic, trustworthy, and maintainable Python tests",
    source_text="pytest documentation and testing best practices",
    source_url=HttpUrl("https://docs.pytest.org/en/stable/"),
    principles=[
        ZenPrinciple(
            id="pytest-001",
            principle="Use assert directly — never assertEqual-style",
            category=PrincipleCategory.IDIOMS,
            severity=6,
            description=(
                "pytest rewrites assert statements to produce rich diffs. "
                "Using unittest-style assertion methods bypasses this mechanism "
                "and produces worse error messages."
            ),
            violations=[
                "assertEqual(a, b) instead of assert a == b",
                "assertTrue(x) instead of assert x",
                "assertFalse(x) instead of assert not x",
            ],
            recommended_alternative="assert a == b",
        ),
        ZenPrinciple(
            id="pytest-002",
            principle="Fixtures must have narrowest possible scope",
            category=PrincipleCategory.ARCHITECTURE,
            severity=7,
            description=(
                "Fixtures with overly broad scope (module, session) risk leaking "
                "state between tests, causing test-order dependency and flakiness."
            ),
            violations=[
                "@pytest.fixture without explicit scope for shared resources",
                "Module or session-scoped fixtures that mutate state",
            ],
            recommended_alternative='@pytest.fixture(scope="function")',
        ),
        ZenPrinciple(
            id="pytest-003",
            principle="Tests must not call time.sleep()",
            category=PrincipleCategory.CORRECTNESS,
            severity=8,
            description=(
                "Real sleeps make the test suite slow and timing-sensitive. "
                "Use freezegun, pytest-mock time mocking, or asyncio.sleep with "
                "fake clocks instead."
            ),
            violations=[
                "time.sleep() inside test functions",
                "asyncio.sleep() with real delays in tests",
            ],
            recommended_alternative="Use freezegun or pytest-mock to freeze/advance time",
        ),
        ZenPrinciple(
            id="pytest-004",
            principle="Parametrize instead of looping in test body",
            category=PrincipleCategory.CORRECTNESS,
            severity=7,
            description=(
                "Loops inside test bodies run all cases in one test, so a single "
                "failure hides all subsequent cases. @pytest.mark.parametrize runs "
                "each case as a separate test item."
            ),
            violations=[
                "for item in cases: assert ...",
                "for value in values: do_assertion(value)",
            ],
            recommended_alternative="@pytest.mark.parametrize('case', cases)",
        ),
        ZenPrinciple(
            id="pytest-005",
            principle="Each test must contain at least one assert",
            category=PrincipleCategory.CORRECTNESS,
            severity=9,
            description=(
                "A test with no assertions always passes and provides false confidence. "
                "Every test function must verify at least one postcondition."
            ),
            violations=[
                "def test_foo(): call_something()  # no assert",
            ],
            recommended_alternative="Add assert <condition> to verify the expected outcome",
        ),
        ZenPrinciple(
            id="pytest-006",
            principle="Test function names must describe behavior",
            category=PrincipleCategory.NAMING,
            severity=5,
            description=(
                "Test names like test_1 or test_it give no information about the "
                "scenario under test. Names should read as sentences describing the "
                "expected behavior."
            ),
            violations=[
                "def test_1(): ...",
                "def test_it(): ...",
                "def test_thing123(): ...",
            ],
            recommended_alternative="def test_login_fails_with_wrong_password(): ...",
        ),
        ZenPrinciple(
            id="pytest-007",
            principle="Avoid bare except in test body",
            category=PrincipleCategory.ERROR_HANDLING,
            severity=8,
            description=(
                "A bare except or overly broad except Exception catches test framework "
                "exceptions (including pytest.fail), silencing test failures and "
                "producing false positives."
            ),
            violations=[
                "except: pass  # swallows all exceptions",
                "except Exception: pass  # too broad",
            ],
            recommended_alternative="Use pytest.raises(SpecificError) for expected exceptions",
        ),
        ZenPrinciple(
            id="pytest-008",
            principle="conftest.py fixtures must not contain business logic",
            category=PrincipleCategory.ARCHITECTURE,
            severity=6,
            description=(
                "conftest.py is for fixture definitions and hooks. Embedding domain "
                "logic there couples test infrastructure to production code and makes "
                "fixtures hard to reason about in isolation."
            ),
            violations=[
                "Helper functions with domain logic inside conftest.py",
                "Data-transformation code in conftest.py fixtures",
            ],
            recommended_alternative="Move domain helpers to a dedicated test_helpers.py module",
        ),
        ZenPrinciple(
            id="pytest-009",
            principle="Use pytest.raises for expected exceptions",
            category=PrincipleCategory.IDIOMS,
            severity=6,
            description=(
                "try/except blocks used to catch expected exceptions are an anti-pattern: "
                "they don't assert anything if the exception is NOT raised. "
                "pytest.raises is explicit and fails correctly."
            ),
            violations=[
                "try: foo(); except ValueError: pass  # no assertion on exception not raised",
            ],
            recommended_alternative="with pytest.raises(ValueError): foo()",
        ),
        ZenPrinciple(
            id="pytest-010",
            principle="Mocked objects must be scoped to the test that needs them",
            category=PrincipleCategory.ARCHITECTURE,
            severity=7,
            description=(
                "Module-level mock setup bleeds mock state into unrelated tests. "
                "Mocks should be created inside the test function or via function-scoped "
                "fixtures to guarantee isolation."
            ),
            violations=[
                "mock = MagicMock() at module level",
                "Patching at module level without restoring in teardown",
            ],
            recommended_alternative="Use mocker fixture or monkeypatch inside the test function",
        ),
    ],
)
