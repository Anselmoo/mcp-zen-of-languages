---
title: Philosophy
description: >-
  The architectural-coaching approach behind mcp-zen-of-languages
  and why universal dogmas matter in AI-assisted development.
icon: material/lightbulb-on
tags:
  - MCP
  - Architecture
  - Quality
---

# Philosophy

![The 10 Dogmas of Zen — ten stones in a zen garden representing the core code quality principles](../assets/illustration-zen-dogma.svg)

`mcp-zen-of-languages` treats static analysis as **architectural coaching**, not just linting.
In AI-assisted coding, fast iteration increases the risk of hidden complexity.
The 10 Dogmas of Zen are universal guardrails that MCP tools can return as structured,
teachable feedback — the same principles whether you write Python, Rust, Go, or TypeScript.

!!! info "Scope and placement"
    This page covers the motivation and coaching philosophy.
    For the full dogma reference — rationale, anti-patterns, and cross-language rule
    mapping — see [User Guide → Rules → The 10 Dogmas](../user-guide/rules/the-ten-dogmas.md).

---

## Why Dogmas, Not Rules?

Rules are prescriptive and brittle: they break when languages evolve.
Dogmas are intentional contracts about *what code should communicate*, not
*what syntax to use*. A detector finds unused arguments in Python **and** in Rust
because both violate the same universal contract: every argument must carry intent.

This architecture means:

- **AI agents get structured, teachable feedback** — not just "bad code" but
  "this violates ZEN-UTILIZE-ARGUMENTS."
- **Remediation prompts are language-agnostic** at the dogma layer, then
  specialized per language for concrete fixes.
- **New language support inherits the dogma framework** — no new philosophy needed.

---

## The Architectural Coaching Model

```
Analyze  →  violations tagged with dogma IDs
Explain  →  structured feedback grounded in the 10 dogmas
Act      →  language-specific remediation prompts
```

This Analyze → Explain → Act loop is the core MCP workflow.
Every step traces back to the universal dogma layer.

!!! tip "Using dogmas in an MCP workflow"
    The full workflow with examples is covered in
    [Understanding Violations](../user-guide/understanding-violations.md#mcp-workflow).

---

## The Zen Lens in Practice

Consider a function that handles user input. A linter finds a missing type annotation.
A zen coach finds something deeper: the function accepts 6 positional arguments with
no defaults — violating **ZEN-PROPORTIONATE-COMPLEXITY** — and swallows parse errors with
`except: pass` — violating **ZEN-FAIL-FAST**. The annotation is cosmetic; the two dogma
violations signal architectural risk.

This is the difference: linters count syntax; dogmas identify _intent failures_.
An AI agent armed with dogma IDs can generate a targeted remediation prompt that
explains *why* the change matters, not just *what* to change.

!!! abstract "Quick reference — The 10 Dogmas"
    | # | Name | ID | Contract |
    |---|------|----|----------|
    | 1 | Purpose | `ZEN-UTILIZE-ARGUMENTS` | Every argument must be used or removed |
    | 2 | Explicit Intent | `ZEN-EXPLICIT-INTENT` | Avoid magic behavior and hidden assumptions |
    | 3 | Flat Traversal | `ZEN-RETURN-EARLY` | Prefer guard clauses over deep nesting |
    | 4 | Loud Failures | `ZEN-FAIL-FAST` | Never silently swallow errors |
    | 5 | Meaningful Abstraction | `ZEN-RIGHT-ABSTRACTION` | Avoid flag-heavy abstractions |
    | 6 | Unambiguous Naming | `ZEN-UNAMBIGUOUS-NAME` | Clarity over clever shorthand |
    | 7 | Visible State | `ZEN-VISIBLE-STATE` | Make mutation explicit and predictable |
    | 8 | Strict Fences | `ZEN-STRICT-FENCES` | Preserve encapsulation boundaries |
    | 9 | Ruthless Deletion | `ZEN-RUTHLESS-DELETION` | Remove dead and unreachable code |
    | 10 | Proportionate Complexity | `ZEN-PROPORTIONATE-COMPLEXITY` | Choose the simplest design that works |

    Full rationale, anti-patterns, and cross-language mapping: [The 10 Dogmas →](../user-guide/rules/the-ten-dogmas.md)

!!! info "Implementation details"
    How dogmas map to detector stubs, the three-layer architecture, and the
    `UniversalDogmaID` enum reference are in
    [Architecture](../contributing/architecture.md#dogma-to-detector-mapping).

## See Also

- [The 10 Dogmas](../user-guide/rules/the-ten-dogmas.md) — full reference with rationale, anti-patterns, and cross-language mapping
- [Understanding Violations](../user-guide/understanding-violations.md) — severity scores, worked examples, and the MCP workflow
- [Architecture](../contributing/architecture.md) — how dogmas drive detector and pipeline design
- [Languages](../user-guide/languages/index.md) — per-language principles derived from these dogmas
