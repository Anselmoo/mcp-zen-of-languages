---
title: Rules
description: >-
  The universal dogmas and per-language zen principles that drive
  every detector and remediation prompt in mcp-zen-of-languages.
icon: material/gavel
tags:
  - Rules
  - Dogmas
  - Architecture
---

# Rules

`mcp-zen-of-languages` has a two-layer rules system:

<div class="grid cards" markdown>

-   :material-gavel:{ .lg .middle } **The 10 Dogmas of Zen**

    ---

    Ten universal, cross-language contracts — every language rule and
    every detector traces back to one of them.

    [The 10 Dogmas](the-ten-dogmas.md)

-   :material-translate:{ .lg .middle } **Language Principles**

    ---

    Per-language zen principles derived from official style guides and
    community best practices — each one mapping to a universal dogma.

    [Languages](../languages/index.md)

</div>

## How the layers connect

```
Universal Dogma  (cross-language, 10 total)
    └── Language Rule  (per language, e.g. python-003)
            └── Detector  (implementation in detectors.py)
                    └── Violation  (reported in analysis results)
```

Each [language principle](../languages/index.md) carries a `dogma` field that
links it back to one or more of the [10 universal dogmas](the-ten-dogmas.md).
This lets MCP clients and AI agents trace every violation back to a fundamental
quality contract.

## The 10 Dogmas at a Glance

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

## See Also

- [The 10 Dogmas](the-ten-dogmas.md) — full reference with rationale and anti-patterns
- [Languages](../languages/index.md) — per-language principles and detector counts
- [Philosophy](../../getting-started/philosophy.md) — the motivation behind the rules system
- [Architecture](../../contributing/architecture.md) — how dogmas drive detector design
