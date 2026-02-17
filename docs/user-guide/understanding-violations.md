---
title: Understanding Violations
description: Violations are emitted with a severity score (1-10). Higher scores indicate more critical issues.
icon: material/book-open-page-variant
tags:
  - CLI
  - Configuration
---

# Understanding Violations

When zen analyzes your code, it produces **violations** — each one tied to a specific zen principle, with a severity score and enough context to understand what went wrong and why it matters.

## Anatomy of a violation

```text
Violation(
  rule_id="py-001",
  message="Function 'process_order' has cyclomatic complexity 18 (max 10)",
  severity=7,
  location=src/orders.py:42,
  principle="Flat is better than nested"
)
```

Each violation includes:

| Field | What it tells you |
|-------|------------------|
| **rule_id** | Which zen principle was violated (e.g., `py-001`, `ts-003`) |
| **message** | Human-readable description of the specific issue |
| **severity** | How critical it is (1–10 scale) |
| **location** | File and line where the violation was detected |
| **principle** | The zen principle being enforced |

## Severity scale

Severity determines **what to fix first** and whether violations block CI.

| Range | Level | What it means | Action |
|:-----:|-------|---------------|--------|
| 8–10 | 🔴 Critical | Structural risk — god classes, circular dependencies, unsafe blocks | Fix before merging |
| 6–7 | 🟠 High | Maintainability risk — high complexity, deep nesting, long functions | Fix in current sprint |
| 4–5 | 🔵 Medium | Clarity risk — implicit types, missing error handling, style drift | Track and improve |
| 1–3 | ⚪ Low | Informational — minor naming issues, documentation gaps | Address when nearby |

## Worked examples

### High severity: Cyclomatic complexity (Python)

```python
# severity 7 — py-001: "Flat is better than nested"
def process_order(order):
    if order.is_valid():
        if order.has_payment():
            if order.payment.verified:
                if not order.is_duplicate():
                    # ... deeply nested logic
```

**Why it matters**: Each `if` branch multiplies the paths through this function. At complexity 18, testing all paths is impractical, and bugs hide in untested branches.

**Remediation**: Extract guard clauses, use early returns, or split into smaller functions.

### High severity: Bare unwrap (Rust)

```rust
// severity 7 — rs-003: "Handle the None, handle the error"
let config = load_config().unwrap();  // panics on error
```

**Why it matters**: `unwrap()` converts a recoverable error into a panic. In production, this crashes instead of handling the failure gracefully.

**Remediation**: Use `?` for propagation, `unwrap_or_default()` for fallbacks, or pattern match on the `Result`.

### Medium severity: Implicit any (TypeScript)

```typescript
// severity 5 — ts-001: "If it can be typed, type it"
function transform(data) {  // implicit 'any' parameter
  return data.map(item => item.value);
}
```

**Why it matters**: Without a type annotation, TypeScript can't catch type errors at compile time. The function accepts anything and will fail silently at runtime.

**Remediation**: Add explicit type annotations: `function transform(data: DataItem[])`.

## Severity glyphs in reports

Reports use emoji badges for quick scanning:

| Severity | Rich terminal | Plain text fallback |
|----------|:------------:|:-------------------:|
| Critical | 🔴 CRIT | ● CRIT |
| High | 🟠 HIGH | ▲ HIGH |
| Medium | 🔵 MED | ◆ MED |
| Low | ⚪ LOW | ○ LOW |

## What to do with violations

1. **Sort by severity** — fix 🔴 and 🟠 first
2. **Check the principle** — understand *why* this is flagged, not just *what*
3. **Use remediation prompts** — run `zen prompts .` to generate AI-ready fix instructions
4. **Tune thresholds** — if a rule is too noisy for your codebase, adjust in [configuration](configuration.md)
5. **Set CI thresholds** — use `severity_threshold` to block PRs only on high-severity issues

## See Also

- [Configuration](configuration.md) — How to tune severity thresholds
- [Prompt Generation](prompt-generation.md) — Generate AI remediation from violations
- [Languages](languages/index.md) — See every principle and detector per language
