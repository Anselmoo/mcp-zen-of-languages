---
title: Testing Dogmas
description: >
  The 20 universal testing dogmas that drive framework-specific analysis in
  zen-of-languages — 10 micro-level tactics (ZEN-TEST-*) and 10 macro-level
  strategy principles (ZEN-MACRO-*).
---

# Testing Dogmas

zen-of-languages extends the [Ten Universal Dogmas](the-ten-dogmas.md) with
**20 testing-specific dogmas** split into two tiers:

| Tier | Prefix | Focus | Count |
|------|--------|-------|-------|
| Micro (tactics) | `ZEN-TEST-*` | Individual test quality — F.I.R.S.T., clean code, Kent Beck | 10 |
| Macro (strategy) | `ZEN-MACRO-*` | Test strategy — pyramid, risk, ownership, visibility | 10 |

Framework analyzers (pytest, Jest, RSpec, Go test) detect violations of the
**micro dogmas** in individual test files. The macro dogmas guide architectural
decisions and are surfaced in dependency and structural analysis.

---

## Micro Dogmas — `ZEN-TEST-*`


### 1. Dogma of Isolated — `ZEN-TEST-ISOLATED`

> Each test stands alone — no shared mutable state, no execution-order dependency.

**Rationale.** Tests that depend on global state or previous tests become fragile and non-deterministic. Isolation guarantees that a single test failure points to a single root cause.

**Anti-patterns:**

- Using module-level mocks that persist across test functions.
- Relying on database rows seeded by a previous test.
- Accessing `self` attributes set in a `setUpClass` without resetting between tests.

---

### 2. Dogma of Deterministic — `ZEN-TEST-DETERMINISTIC`

> Given the same inputs, a test always produces the same result.

**Rationale.** Non-deterministic tests erode trust. Flaky tests that sometimes pass and sometimes fail are worse than no tests — they mask real failures and waste debugging time.

**Anti-patterns:**

- Calling `time.sleep()` or `Date.now()` inside a test assertion.
- Asserting on unordered collections without sorting.
- Using random data without a fixed seed.

---

### 3. Dogma of Single Reason — `ZEN-TEST-SINGLE-REASON`

> One test, one behavior — verify exactly one thing.

**Rationale.** Tests that check multiple behaviors require multiple code paths to fail before the root cause is clear. A test with a single assertion is trivially debuggable.

**Anti-patterns:**

- Asserting both the return value and side-effects in a single `it()` block.
- Looping over multiple scenarios inside a single test function.
- Combining a happy-path and an error-path assertion in one test.

---

### 4. Dogma of Named Behavior — `ZEN-TEST-NAMED-BEHAVIOR`

> Test names document behavior, not implementation.

**Rationale.** A test named `test_1` or `should work` provides no signal on failure. Names should read as specifications: what scenario, what expected outcome.

**Anti-patterns:**

- Test functions named `test_1`, `test_2`, `myTest`, or `works`.
- RSpec `it` blocks with no description string.
- Jest `it('test', ...)` with a generic word as the title.

---

### 5. Dogma of No Logic — `ZEN-TEST-NO-LOGIC`

> Tests must not contain loops, conditionals, or complex logic.

**Rationale.** Logic inside a test means the test itself can be buggy. A test is a specification — it should read like a table of inputs and outputs, not a program.

**Anti-patterns:**

- A `for` loop inside a test body that iterates over multiple cases.
- An `if` guard that skips assertions based on runtime state.
- Try/except blocks wrapping the code under test.

---

### 6. Dogma of Fast — `ZEN-TEST-FAST`

> Tests must not block on I/O, sleep, or real network calls.

**Rationale.** Slow tests discourage frequent runs. The test suite must complete in seconds, not minutes, to support TDD and CI gating.

**Anti-patterns:**

- Calling `time.sleep()` or `Thread.sleep()` in a test.
- Making real HTTP requests without a mock or stub.
- Waiting for a fixed timeout instead of polling a condition.

---

### 7. Dogma of Documented Intent — `ZEN-TEST-DOCUMENTED-INTENT`

> Every non-obvious test decision must be explained in a comment or name.

**Rationale.** Future maintainers should understand why a test exists and what edge case it covers. Inline comments turn tests into living documentation.

**Anti-patterns:**

- A test for an obscure edge case with no comment explaining the scenario.
- Magic literals (e.g. `42`, `'abc'`) with no explanation of significance.
- Pending/skipped tests with no reason for the skip.

---

### 8. Dogma of Trustworthy — `ZEN-TEST-TRUSTWORTHY`

> A passing test must mean the behavior is correct.

**Rationale.** Tests that always pass regardless of the implementation are worse than no tests. Assertions must be meaningful and cover the actual contract.

**Anti-patterns:**

- `expect.assertions(0)` in Jest — asserting nothing happened.
- An `assert True` that can never fail.
- Catching exceptions inside the test body and ignoring them.

---

### 9. Dogma of Clean Code — `ZEN-TEST-CLEAN-CODE`

> Tests follow the same code-quality standards as production code.

**Rationale.** Test code is read and maintained as often as production code. Dead code, magic numbers, and bare excepts are just as harmful in tests.

**Anti-patterns:**

- Bare `except:` blocks inside test helpers.
- Commented-out test cases left in the file.
- Test utilities with God-class symptoms (dozens of helper methods).

---

### 10. Dogma of Proportional — `ZEN-TEST-PROPORTIONAL`

> Test complexity must match the complexity of the code under test.

**Rationale.** Over-testing trivial code and under-testing complex logic are symmetric failures. Proportional coverage focuses effort where bugs are most likely.

**Anti-patterns:**

- Extensive tests for trivial getters with no tests for complex algorithms.
- Integration tests covering every edge case that belongs in unit tests.
- A single smoke test for a function with ten branches.

---

## Macro Dogmas — `ZEN-MACRO-*`

Macro dogmas capture test *strategy* concerns that transcend individual test files. They are used in structural and dependency analysis.

### 1. Dogma of Boundary — `ZEN-MACRO-BOUNDARY`

> Test the edges, not just the happy path.

**Rationale.** Most production bugs live at boundaries: empty inputs, max values, type transitions, null-like sentinels. A strategy that covers only the happy path misses the majority of defect surfaces.

**Anti-patterns:**

- Unit tests only for typical inputs, skipping empty, null, and max-value cases.
- No test for the transition from one state to another.
- Integration tests that only exercise the success path of an API.

---

### 2. Dogma of Traceability — `ZEN-MACRO-TRACEABILITY`

> Every test traces back to a requirement or acceptance criterion.

**Rationale.** Untraceable tests are orphans — they may test the wrong thing or duplicate coverage without anyone knowing. Traceability enables confident deletion when requirements change.

**Anti-patterns:**

- A large test suite with no mapping to user stories or tickets.
- Duplicate tests covering the same acceptance criterion.
- Tests written after the fact that cannot be linked to a specification.

---

### 3. Dogma of Integration — `ZEN-MACRO-INTEGRATION`

> Test interactions between components, not just components in isolation.

**Rationale.** Unit tests validate contracts; integration tests validate that contracts are honored in composition. Both layers are necessary — neither replaces the other.

**Anti-patterns:**

- A codebase with 100% unit coverage and zero integration tests.
- Integration tests that mock every dependency (effectively unit tests).
- Service tests that never cross the database boundary.

---

### 4. Dogma of Risk — `ZEN-MACRO-RISK`

> Allocate testing effort in proportion to risk, not uniformly.

**Rationale.** Not all code is equally critical. Risk-based testing focuses coverage on high-impact, frequently changing, or historically buggy modules.

**Anti-patterns:**

- Equal test depth for a payment processor and a logging utility.
- No tests for authentication or authorization logic.
- Skipping regression tests for recently modified critical paths.

---

### 5. Dogma of Reality Check — `ZEN-MACRO-REALITY-CHECK`

> Tests must reflect production conditions, not idealized lab conditions.

**Rationale.** Tests that only work under perfect conditions miss the bugs users actually encounter. Chaos, concurrency, and resource constraints must be modeled.

**Anti-patterns:**

- Integration tests that never simulate network timeouts or partial failures.
- Load tests run on a developer laptop, not under production-like load.
- Tests that assume UTC timezone when production runs in a mixed-zone environment.

---

### 6. Dogma of Flakiness — `ZEN-MACRO-FLAKINESS`

> Flaky tests must be fixed or deleted — never silently retried.

**Rationale.** A test suite that auto-retries flaky tests hides non-determinism. Every flaky test is a bug report waiting to be written.

**Anti-patterns:**

- CI configured with `--retries 3` to mask flaky failures.
- Tests quarantined in a 'flaky' folder that never gets cleaned up.
- Accepting flakiness as normal for end-to-end tests.

---

### 7. Dogma of Shift Right — `ZEN-MACRO-SHIFT-RIGHT`

> Test in production-like environments as early as possible.

**Rationale.** The later a defect is found, the more expensive it is to fix. Shift-right testing (canary, shadow, production monitoring) catches classes of bugs that pre-production environments cannot.

**Anti-patterns:**

- Deploying directly to production with only unit-test gating.
- No canary or staged rollout for significant changes.
- Monitoring that alerts only on crashes, not on behavioral regressions.

---

### 8. Dogma of Ownership — `ZEN-MACRO-OWNERSHIP`

> Tests are owned by the team that owns the code.

**Rationale.** Shared test suites with no clear owners accumulate technical debt. Ownership means the owning team fixes failures, updates tests for new requirements, and deletes obsolete coverage.

**Anti-patterns:**

- A monolithic end-to-end suite owned by a separate QA team with no developer input.
- Tests that fail intermittently but no one has ownership to fix.
- Shared test helpers modified by multiple teams without coordination.

---

### 9. Dogma of Evolvability — `ZEN-MACRO-EVOLVABILITY`

> Tests must be refactored alongside production code.

**Rationale.** Tests that are never refactored become brittle. When a test suite impedes refactoring because every change breaks dozens of tests, the tests have become an anti-pattern.

**Anti-patterns:**

- Tests that assert on exact private method signatures rather than observable behavior.
- A test suite where every refactor requires updating 50+ test files.
- Snapshot tests that are bulk-updated without review.

---

### 10. Dogma of Visibility — `ZEN-MACRO-VISIBILITY`

> Test results, coverage trends, and flakiness metrics must be visible to all.

**Rationale.** Invisible test quality leads to invisible quality debt. Dashboards, CI badges, and coverage trends make quality a team concern, not an individual one.

**Anti-patterns:**

- Test results only visible in CI logs that developers rarely check.
- No coverage trend tracking over time.
- Flakiness rates not reported or surfaced to the team.

---

## See Also

- [The Ten Dogmas](the-ten-dogmas.md) — the universal cross-language dogmas these extend
- [Understanding Violations](../understanding-violations.md) — severity scores and the MCP workflow
- [Languages](../languages/index.md) — per-language principles
