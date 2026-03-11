"""Smoke tests for the Jest framework analyzer."""

from __future__ import annotations

from mcp_zen_of_languages.languages.typescript.testing.jest import JestAnalyzer


ANALYZER = JestAnalyzer()

BAD_CODE = """\
describe('UserService', () => {});

test('test 1', () => {
  doSomething();
});

test('works', () => {
  expect.assertions(0);
  const result = fetch('/api/data');
});

function getUser(t) {
  jest.spyOn(db, 'query').mockReturnValue(null);
}
"""

CLEAN_CODE = """\
describe('UserService', () => {
  it('returns 404 when user not found', async () => {
    const result = await getUser(999);
    expect(result).toBeNull();
  });

  afterEach(() => jest.restoreAllMocks());
});
"""


class TestJestAnalyzer:
    def test_is_test_file_matches_spec_ts(self) -> None:
        assert ANALYZER.is_test_file("auth.spec.ts") is True

    def test_is_test_file_matches_test_js(self) -> None:
        assert ANALYZER.is_test_file("auth.test.js") is True

    def test_is_test_file_matches_tests_dir(self) -> None:
        assert ANALYZER.is_test_file("__tests__/auth.ts") is True

    def test_is_test_file_no_match(self) -> None:
        assert ANALYZER.is_test_file("src/auth.ts") is False

    def test_language(self) -> None:
        assert ANALYZER.language() == "jest"

    def test_parent_language(self) -> None:
        assert ANALYZER.parent_language == "typescript"

    def test_bad_code_produces_violations(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="src/__tests__/user.test.ts")
        assert len(result.violations) > 0

    def test_detects_assertions_zero(self) -> None:
        code = "test('foo', () => { expect.assertions(0); });\n"
        result = ANALYZER.analyze(code, path="foo.test.ts")
        principles = [v.principle for v in result.violations]
        assert any("assertions" in p.lower() or "0" in p for p in principles)

    def test_detects_vague_title(self) -> None:
        code = "it('test 1', () => { expect(1).toBe(1); });\n"
        result = ANALYZER.analyze(code, path="foo.test.ts")
        principles = [v.principle for v in result.violations]
        assert any("title" in p.lower() or "behav" in p.lower() for p in principles)

    def test_clean_code_fewer_violations(self) -> None:
        result = ANALYZER.analyze(CLEAN_CODE, path="user.spec.ts")
        # Clean code should have very few violations (may have some false positives)
        assert len(result.violations) < 3
