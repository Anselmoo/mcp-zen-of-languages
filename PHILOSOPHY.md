# Philosophy: The 10 Dogmas of Zen for MCP Vibe Coding

`mcp-zen-of-languages` treats static analysis as **architectural coaching**, not just linting.
In AI-assisted vibe coding, fast iteration increases the risk of hidden complexity.
These dogmas are guardrails that MCP tools can return as structured, teachable feedback.

## The 10 Dogmas

1. **Dogma of Purpose** (`ZEN-UTILIZE-ARGUMENTS`) — every argument must be used or removed.
2. **Dogma of Explicit Intent** (`ZEN-EXPLICIT-INTENT`) — avoid magic behavior and hidden assumptions.
3. **Dogma of Flat Traversal** (`ZEN-RETURN-EARLY`) — prefer guard clauses over deep nesting.
4. **Dogma of Loud Failures** (`ZEN-FAIL-FAST`) — never silently swallow errors.
5. **Dogma of Meaningful Abstraction** (`ZEN-RIGHT-ABSTRACTION`) — avoid flag-heavy abstractions.
6. **Dogma of Unambiguous Naming** (`ZEN-UNAMBIGUOUS-NAME`) — clarity over clever shorthand.
7. **Dogma of Visible State** (`ZEN-VISIBLE-STATE`) — make mutation explicit and predictable.
8. **Dogma of Strict Fences** (`ZEN-STRICT-FENCES`) — preserve encapsulation boundaries.
9. **Dogma of Ruthless Deletion** (`ZEN-RUTHLESS-DELETION`) — remove dead and unreachable code.
10. **Dogma of Proportionate Complexity** (`ZEN-PROPORTIONATE-COMPLEXITY`) — choose the simplest design that works.

## MCP-Centric Framing

- **Universal layer**: dogmas are language-agnostic intent.
- **Adapter layer**: language analyzers map syntax/AST details into those dogmas.
- **Transport layer**: CLI and MCP reporters expose findings for humans and AI agents.

This lets assistants move from "style warnings" to principled guidance:
what is wrong, why it increases cognitive load, and how to refactor with intent.

## Identifier Mapping Reference

Universal dogma constants in code use enum-style names in
`UniversalDogmaID` and map directly to the canonical IDs documented above:

- `UTILIZE_ARGUMENTS` → `ZEN-UTILIZE-ARGUMENTS` (Dogma of Purpose)
- `EXPLICIT_INTENT` → `ZEN-EXPLICIT-INTENT` (Dogma of Explicit Intent)
- `RETURN_EARLY` → `ZEN-RETURN-EARLY` (Dogma of Flat Traversal)
- `FAIL_FAST` → `ZEN-FAIL-FAST` (Dogma of Loud Failures)
- `RIGHT_ABSTRACTION` → `ZEN-RIGHT-ABSTRACTION` (Dogma of Meaningful Abstraction)
- `UNAMBIGUOUS_NAME` → `ZEN-UNAMBIGUOUS-NAME` (Dogma of Unambiguous Naming)
- `VISIBLE_STATE` → `ZEN-VISIBLE-STATE` (Dogma of Visible State)
- `STRICT_FENCES` → `ZEN-STRICT-FENCES` (Dogma of Strict Fences)
- `RUTHLESS_DELETION` → `ZEN-RUTHLESS-DELETION` (Dogma of Ruthless Deletion)
- `PROPORTIONATE_COMPLEXITY` → `ZEN-PROPORTIONATE-COMPLEXITY` (Dogma of Proportionate Complexity)
