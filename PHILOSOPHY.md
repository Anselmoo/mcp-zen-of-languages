# Philosophy: The 10 Dogmas of Zen for MCP Vibe Coding

<p align="center">
  <img src="docs/assets/illustration-zen-dogma.svg" alt="The 10 Dogmas of Zen — ten stones in a zen garden representing the core code quality principles" width="720" />
</p>

`mcp-zen-of-languages` treats static analysis as **architectural coaching**, not just linting.
In AI-assisted vibe coding, fast iteration increases the risk of hidden complexity.
These dogmas are guardrails that MCP tools can return as structured, teachable feedback.

---

## The 10 Dogmas

### 1. Dogma of Purpose — `ZEN-UTILIZE-ARGUMENTS`

> Every argument must be used or removed.

**Rationale.** Unused parameters signal dead intent. They mislead readers about a
function's contract and accumulate as noise during refactors. In AI-assisted
workflows, an agent generating a function signature should never leave behind
vestigial parameters.

**Anti-patterns:**

- Accepting a parameter that is never referenced in the body.
- Keeping deprecated arguments "for compatibility" without a migration path.
- Forwarding `**kwargs` solely to suppress linter warnings about unused names.

---

### 2. Dogma of Explicit Intent — `ZEN-EXPLICIT-INTENT`

> Avoid magic behavior and hidden assumptions.

**Rationale.** Implicit behavior — type coercion, default mutations, hidden
global state — creates cognitive load that compounds across a codebase. When an
AI assistant reviews code, explicit intent makes violations unambiguous and fixes
mechanical.

**Anti-patterns:**

- Relying on mutable default arguments (`def f(x=[])`).
- Star-imports that hide the origin of names.
- Magic numbers without named constants.
- Implicit type conversions that silently change semantics.

---

### 3. Dogma of Flat Traversal — `ZEN-RETURN-EARLY`

> Prefer guard clauses over deep nesting.

**Rationale.** Deeply nested code forces readers to maintain a mental stack of
conditions. Guard clauses flatten the control flow and highlight the happy path.
Detectors can measure nesting depth mechanically, making this an ideal candidate
for automated enforcement.

**Anti-patterns:**

- `if`/`else` chains nested three or more levels deep.
- Wrapping entire function bodies in a single top-level `if`.
- Failing to invert negative conditions into early returns.

---

### 4. Dogma of Loud Failures — `ZEN-FAIL-FAST`

> Never silently swallow errors.

**Rationale.** Silent failures turn bugs into mysteries. When errors surface
immediately, root-cause analysis becomes trivial. This is especially critical in
MCP workflows where an agent may not observe side effects that a human would
notice in a debugger.

**Anti-patterns:**

- Bare `except: pass` blocks.
- Catching broad exception types without logging or re-raising.
- Returning `None` as a silent error sentinel instead of raising.
- Using `.unwrap()` (Rust) or force-unwrapping (Swift) without context.

---

### 5. Dogma of Meaningful Abstraction — `ZEN-RIGHT-ABSTRACTION`

> Avoid flag-heavy abstractions.

**Rationale.** A boolean parameter that toggles behavior is two functions wearing
one name. Premature or incorrect abstraction is worse than duplication — it
couples unrelated concerns and makes extension fragile.

**Anti-patterns:**

- Functions with boolean `mode` flags that switch between unrelated behaviors.
- God Classes with dozens of methods spanning multiple responsibilities.
- Deep inheritance hierarchies where base classes know about leaf details.
- Circular dependencies between modules.

---

### 6. Dogma of Unambiguous Naming — `ZEN-UNAMBIGUOUS-NAME`

> Clarity over clever shorthand.

**Rationale.** Names are the primary API for understanding code. Ambiguous or
overly short identifiers force readers to trace definitions. For AI assistants
consuming code via MCP, clear names reduce hallucination risk.

**Anti-patterns:**

- Single-letter variable names outside trivial loop counters.
- Abbreviations that save keystrokes but cost comprehension (`mgr`, `ctx`, `impl`).
- Naming style violations for the language (e.g., `camelCase` in Python).
- Inconsistent naming conventions across a project.

---

### 7. Dogma of Visible State — `ZEN-VISIBLE-STATE`

> Make mutation explicit and predictable.

**Rationale.** Hidden mutation — global state changes, in-place modifications
without clear signals — is the leading cause of "works on my machine" bugs.
Visible state makes data flow traceable and diffs reviewable.

**Anti-patterns:**

- Mutating function arguments in place without documenting it.
- Global mutable singletons accessed from multiple modules.
- Implicit state changes through property setters that trigger side effects.
- Shadowing variables in nested scopes, creating ambiguity about which binding is alive.

---

### 8. Dogma of Strict Fences — `ZEN-STRICT-FENCES`

> Preserve encapsulation boundaries.

**Rationale.** Module and class boundaries exist to manage complexity. Breaking
encapsulation — accessing private members, circular imports, leaking internal
types — turns architecture diagrams into lies.

**Anti-patterns:**

- Accessing private/protected members from outside the owning module.
- Circular import dependencies between packages.
- Exposing internal implementation types in public APIs.
- Namespace pollution through wildcard re-exports.

---

### 9. Dogma of Ruthless Deletion — `ZEN-RUTHLESS-DELETION`

> Remove dead and unreachable code.

**Rationale.** Dead code is technical debt with zero value. It misleads readers,
inflates coverage metrics, and creates phantom dependencies. Version control
preserves history — there is no reason to keep unused code in the working tree.

**Anti-patterns:**

- Commented-out code blocks left "just in case."
- Functions or classes that are defined but never called.
- Feature flags that are permanently off with no cleanup plan.
- Unreachable branches after an unconditional return.

---

### 10. Dogma of Proportionate Complexity — `ZEN-PROPORTIONATE-COMPLEXITY`

> Choose the simplest design that works.

**Rationale.** Complexity must be justified by requirements, not by speculative
generality. High cyclomatic complexity, long functions, and over-engineered
abstractions all increase the cost of every future change.

**Anti-patterns:**

- Functions with cyclomatic complexity exceeding a configured threshold.
- Functions longer than a screen (configurable, default ~50 lines).
- Premature introduction of design patterns without a concrete need.
- Over-parameterized configurations when sensible defaults suffice.

---

## How Dogmas Drive Detector Development

Each dogma maps to one or more **universal detector stubs** in the
`core/detectors/` package. These stubs define the *intent* of what should be
detected while language-specific analyzers provide the *implementation*:

| Detector Domain | Dogmas Covered | Module |
| --- | --- | --- |
| **Signature** | 1 Purpose, 2 Explicit Intent, 5 Meaningful Abstraction | `core/detectors/signature.py` |
| **Control Flow** | 3 Flat Traversal, 4 Loud Failures | `core/detectors/control_flow.py` |
| **State Mutation** | 7 Visible State, 8 Strict Fences | `core/detectors/state_mutation.py` |
| **Clutter** | 6 Unambiguous Naming, 9 Ruthless Deletion, 10 Proportionate Complexity | `core/detectors/clutter.py` |
| **Shared Keyword** | All (pattern-based) | `core/detectors/shared_keyword.py` |

Language-specific detectors (e.g., `NestingDepthDetector`, `GodClassDetector`,
`BareExceptDetector` in `languages/python/detectors.py`) are the concrete
implementations that make these stubs actionable. The `DetectionPipeline`
orchestrates them using the **Strategy** pattern — each detector encapsulates a
single concern and can be tested, reordered, or disabled independently.

The `registry_bootstrap` module bridges the gap: it scans all language zen
principles and registers a `RulePatternDetector` for any rule that lacks a
dedicated detector, ensuring every principle is at least heuristically covered.

---

## MCP Alignment: Why Dogmas Matter for AI-Assisted Coding

### The Problem with "Vibe Coding"

AI-assisted development accelerates iteration, but fast iteration without
guardrails accelerates the accumulation of hidden complexity. Traditional
linters report *what* is wrong; dogmas explain *why* it matters and *how*
to refactor with intent.

### Three-Layer Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│  UNIVERSAL DOGMAS (language-agnostic intent)                │
│  UniversalDogmaID enum — 10 canonical identifiers           │
├─────────────────────────────────────────────────────────────┤
│  LANGUAGE ADAPTERS (syntax/AST → dogma mapping)             │
│  BaseAnalyzer subclasses + DetectionPipeline                │
├─────────────────────────────────────────────────────────────┤
│  MCP / CLI TRANSPORT (structured output for agents/humans)  │
│  FastMCP server (13 tools) + zen CLI                        │
└─────────────────────────────────────────────────────────────┘
```

- **Universal layer**: dogmas are language-agnostic intent encoded as
  `UniversalDogmaID` values.
- **Adapter layer**: language analyzers map syntax/AST details into those
  dogmas via `infer_dogmas_for_principle()`.
- **Transport layer**: CLI and MCP reporters expose findings for humans
  and AI agents as structured `ViolationReport` objects.

This lets assistants move from "style warnings" to principled guidance:
what is wrong, why it increases cognitive load, and how to refactor with intent.

### MCP Workflow Example

1. **Analyze** — `analyze_zen_violations` returns severity-scored violations
   tagged with dogma identifiers.
2. **Explain** — `generate_prompts` produces remediation instructions grounded
   in the specific dogma that was violated.
3. **Act** — `generate_agent_tasks` creates a prioritised task list that an
   AI agent can execute directly.

---

## Identifier Mapping Reference

Universal dogma constants in code use enum-style names in
`UniversalDogmaID` and map directly to the canonical IDs documented above:

| Enum Member | Canonical ID | Dogma Title |
| --- | --- | --- |
| `UTILIZE_ARGUMENTS` | `ZEN-UTILIZE-ARGUMENTS` | Dogma of Purpose |
| `EXPLICIT_INTENT` | `ZEN-EXPLICIT-INTENT` | Dogma of Explicit Intent |
| `RETURN_EARLY` | `ZEN-RETURN-EARLY` | Dogma of Flat Traversal |
| `FAIL_FAST` | `ZEN-FAIL-FAST` | Dogma of Loud Failures |
| `RIGHT_ABSTRACTION` | `ZEN-RIGHT-ABSTRACTION` | Dogma of Meaningful Abstraction |
| `UNAMBIGUOUS_NAME` | `ZEN-UNAMBIGUOUS-NAME` | Dogma of Unambiguous Naming |
| `VISIBLE_STATE` | `ZEN-VISIBLE-STATE` | Dogma of Visible State |
| `STRICT_FENCES` | `ZEN-STRICT-FENCES` | Dogma of Strict Fences |
| `RUTHLESS_DELETION` | `ZEN-RUTHLESS-DELETION` | Dogma of Ruthless Deletion |
| `PROPORTIONATE_COMPLEXITY` | `ZEN-PROPORTIONATE-COMPLEXITY` | Dogma of Proportionate Complexity |

### Category-to-Dogma Mapping

The `_CATEGORY_TO_DOGMAS` table in `core/universal_dogmas.py` provides a
baseline mapping from `PrincipleCategory` to the most relevant dogma. This
is enriched at inference time by keyword scanning of violation and pattern
descriptions.

| Category | Primary Dogma |
| --- | --- |
| Readability, Usability, Naming, Documentation | Unambiguous Naming |
| Clarity, Consistency, Type Safety, Configuration, Initialization, Debugging, Correctness | Explicit Intent |
| Complexity, Performance | Proportionate Complexity |
| Architecture, Idioms, Design, Functional | Meaningful Abstraction |
| Structure | Flat Traversal |
| Error Handling, Async, Safety, Robustness | Loud Failures |
| Immutability, Concurrency, Ownership, Memory Management | Visible State |
| Organization, Resource Management, Scope, Security | Strict Fences |

---

## References

- **Epic:** [#69 — 10 Dogmas of Zen](https://github.com/Anselmoo/mcp-zen-of-languages/issues/69)
- **Implementation PR:** [#73 — Core universal zen detector contracts](https://github.com/Anselmoo/mcp-zen-of-languages/pull/73)
- **Source code:** `src/mcp_zen_of_languages/core/universal_dogmas.py`
