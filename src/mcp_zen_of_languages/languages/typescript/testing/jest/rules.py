"""Jest/Vitest zen principles as Pydantic models."""

from __future__ import annotations

from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
from mcp_zen_of_languages.rules.base_models import PrincipleCategory
from mcp_zen_of_languages.rules.base_models import ZenPrinciple


JEST_ZEN = LanguageZenPrinciples(
    language="jest",
    name="Jest/Vitest",
    philosophy="Jest/Vitest Zen — reliable, isolated, and readable JavaScript/TypeScript tests",
    source_text="Jest documentation and JavaScript testing best practices",
    principles=[
        ZenPrinciple(
            id="jest-001",
            principle="Every test()/it() must contain at least one expect()",
            category=PrincipleCategory.CORRECTNESS,
            severity=9,
            description=(
                "A test without an expect() always passes regardless of what the "
                "code does, providing false confidence in correctness."
            ),
            violations=[
                "test('foo', () => { doSomething(); });  // no expect",
            ],
            recommended_alternative="expect(result).toBe(expectedValue)",
        ),
        ZenPrinciple(
            id="jest-002",
            principle="beforeAll state mutations must be idempotent",
            category=PrincipleCategory.ARCHITECTURE,
            severity=8,
            description=(
                "beforeAll runs once per describe block and its mutations persist "
                "across all tests in that block. Non-idempotent mutations create "
                "order-dependent failures."
            ),
            violations=[
                "beforeAll(() => { array.push(item); });  // accumulates state",
            ],
            recommended_alternative="Use beforeEach to reset state before every test",
        ),
        ZenPrinciple(
            id="jest-003",
            principle="Async tests must await or return promises",
            category=PrincipleCategory.CORRECTNESS,
            severity=10,
            description=(
                "A test function that fires a promise but neither awaits it nor returns "
                "it will pass immediately — before the promise resolves — hiding real "
                "failures."
            ),
            violations=[
                "test('foo', () => { fetchData(); });  // un-awaited promise",
            ],
            recommended_alternative="test('foo', async () => { await fetchData(); })",
        ),
        ZenPrinciple(
            id="jest-004",
            principle="Mock implementations must be reset between tests",
            category=PrincipleCategory.ARCHITECTURE,
            severity=8,
            description=(
                "Mocks that retain call history or implementation from a previous "
                "test create subtle cross-test contamination. Always call "
                "jest.clearAllMocks() or jest.resetAllMocks() in afterEach."
            ),
            violations=[
                "Mock call counts leaking between tests",
                "Implementation set in one test persisting to next",
            ],
            recommended_alternative="afterEach(() => jest.resetAllMocks())",
        ),
        ZenPrinciple(
            id="jest-005",
            principle="setTimeout/setInterval must use fake timers in tests",
            category=PrincipleCategory.CORRECTNESS,
            severity=7,
            description=(
                "Real timer usage in tests introduces actual delays, making the suite "
                "slow and timing-dependent. jest.useFakeTimers() / vi.useFakeTimers() "
                "let you advance time programmatically."
            ),
            violations=[
                "Real setTimeout() calls in test bodies",
                "setInterval() without fake timer setup",
            ],
            recommended_alternative="jest.useFakeTimers(); jest.advanceTimersByTime(1000);",
        ),
        ZenPrinciple(
            id="jest-006",
            principle="describe blocks must not be empty",
            category=PrincipleCategory.READABILITY,
            severity=5,
            description=(
                "An empty describe block adds noise to the test report without adding "
                "any coverage. Either remove it or add test cases."
            ),
            violations=[
                "describe('UserService', () => {});  // empty block",
            ],
            recommended_alternative="Add test() / it() cases or remove the describe block",
        ),
        ZenPrinciple(
            id="jest-007",
            principle="Avoid expect.assertions(0)",
            category=PrincipleCategory.CORRECTNESS,
            severity=7,
            description=(
                "expect.assertions(0) explicitly asserts that no assertions ran, "
                "which nearly always indicates a missing or wrong test, not a valid "
                "passing test."
            ),
            violations=[
                "expect.assertions(0)  // asserts nothing was tested",
            ],
            recommended_alternative="Remove expect.assertions(0) and add real assertions",
        ),
        ZenPrinciple(
            id="jest-008",
            principle="Test titles must describe expected behavior",
            category=PrincipleCategory.NAMING,
            severity=5,
            description=(
                "Vague test titles like 'test 1' or 'it works' do not explain "
                "the scenario or expected outcome. Test titles should read like "
                "specifications."
            ),
            violations=[
                "it('test 1', ...)",
                "it('works', ...)",
            ],
            recommended_alternative="it('returns 403 when user lacks permissions', ...)",
        ),
        ZenPrinciple(
            id="jest-009",
            principle="Avoid nested describe blocks deeper than 2 levels",
            category=PrincipleCategory.COMPLEXITY,
            severity=6,
            description=(
                "Deeply nested describe blocks make tests hard to read and indicate "
                "that the subject under test is too complex. Flatten or split into "
                "multiple test files."
            ),
            violations=[
                "describe → describe → describe → it  // 3 levels deep",
            ],
            recommended_alternative="Limit nesting to describe → it or describe → describe → it",
        ),
        ZenPrinciple(
            id="jest-010",
            principle="afterEach must restore all mocks",
            category=PrincipleCategory.ARCHITECTURE,
            severity=8,
            description=(
                "Without restoration, spy/mock state bleeds across tests. "
                "afterEach ensures each test starts with a clean mock state."
            ),
            violations=[
                "jest.spyOn(obj, 'method') without restoreAllMocks() in afterEach",
            ],
            recommended_alternative="afterEach(() => jest.restoreAllMocks())",
        ),
    ],
)
