---
title: JavaScript
description: "11 zen principles enforced by 11 detectors: Modern JavaScript Best Practices."
icon: fontawesome/brands/js
tags:
  - JavaScript
---

# JavaScript

JavaScript has evolved enormously since ES6, but codebases often carry legacy patterns — `var` declarations, loose equality, callback pyramids. These **11 principles** encode modern JavaScript best practices drawn from the Airbnb Style Guide, Node.js best practices, and the functional programming community.

## Optional External Tool Augmentation

!!! info "Consent-first external tooling"
    External tool execution is optional and disabled by default. Use
    `--enable-external-tools` (CLI) or `enable_external_tools=true` (MCP)
    to opt in. Missing tools should return recommendations; no automatic
    installs occur during analysis.

| Tool | Default invocation | Output |
|------|---------------------|--------|
| `biome` | `biome lint --stdin-file-path stdin.js --reporter json` | JSON |
| `eslint` | `eslint --stdin --format json` | JSON |
| `prettier` | `prettier --check --stdin-filepath stdin.js` | Text / structured stderr |

!!! tip "Temporary runner fallback"
    For temporary execution via package runners, use
    `--allow-temporary-runners` (CLI) or `allow_temporary_runners=true` (MCP).


## Zen Principles

11 principles across 10 categories, drawn from [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript).

<div class="grid" markdown>

:material-tag-outline: **Architecture** · 2 principles
:material-tag-outline: **Async** · 1 principle
:material-tag-outline: **Clarity** · 1 principle
:material-tag-outline: **Correctness** · 1 principle
:material-tag-outline: **Design** · 1 principle
:material-tag-outline: **Error Handling** · 1 principle
:material-tag-outline: **Functional** · 1 principle
:material-tag-outline: **Idioms** · 1 principle
:material-tag-outline: **Immutability** · 1 principle
:material-tag-outline: **Readability** · 1 principle

</div>

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `js-001` | Avoid callback hell | Async | 8 |
| `js-002` | Prefer const over let, never var | Immutability | 7 |
| `js-003` | Use strict equality | Correctness | 8 |
| `js-004` | Avoid global state | Architecture | 9 |
| `js-005` | Functions should do one thing | Design | 7 |
| `js-006` | Use modern ES6+ features | Idioms | 6 |
| `js-007` | Handle errors explicitly | Error Handling | 9 |
| `js-008` | Avoid magic numbers and strings | Clarity | 6 |
| `js-009` | Prefer composition over inheritance | Architecture | 7 |
| `js-010` | Keep functions pure when possible | Functional | 6 |
| `js-011` | Use meaningful names | Readability | 8 |

??? info "`js-001` — Avoid callback hell"
    **Use modern async patterns instead of nested callbacks**

    **Common Violations:**

    - Nested callbacks > 2 levels
    - Pyramid of doom pattern
    - Not using async/await when available

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_callback_nesting` | `2` |

    !!! tip "Recommended Fix"
        async/await or Promises

??? info "`js-002` — Prefer const over let, never var"
    **Use const by default for immutability**

    **Common Violations:**

    - Using var keyword
    - Using let for values that don't change
    - Reassigning const-eligible variables

    **Detectable Patterns:**

    - `var keyword usage`
    - `let without reassignment`

??? info "`js-003` — Use strict equality"
    **Always use === and !== to avoid type coercion bugs**

    **Common Violations:**

    - Using == or !=
    - Relying on truthy/falsy in critical comparisons

    **Detectable Patterns:**

    - `== comparison`
    - `!= comparison`

??? info "`js-004` — Avoid global state"
    **Minimize global variables and shared mutable state**

    **Common Violations:**

    - Global variable declarations
    - Window object pollution
    - Singleton pattern overuse
    - Shared mutable state

    **Detectable Patterns:**

    - `window.`
    - `globalThis.`
    - `global.`

??? info "`js-005` — Functions should do one thing"
    **Single Responsibility Principle for functions**

    **Common Violations:**

    - Functions > 50 lines
    - Functions with multiple side effects
    - Functions that both compute and mutate

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_function_length` | `50` |
    | `max_parameters` | `3` |

??? info "`js-006` — Use modern ES6+ features"
    **Leverage destructuring, arrow functions, template literals**

    **Common Violations:**

    - String concatenation instead of template literals
    - Function expressions instead of arrow functions
    - Manual object property access instead of destructuring
    - Not using spread operator

    **Detectable Patterns:**

    - `function() instead of () =>`
    - `string + variable instead of template literal`

??? info "`js-007` — Handle errors explicitly"
    **Always handle promise rejections and errors**

    **Common Violations:**

    - Promises without .catch()
    - async functions without try-catch
    - Ignoring error callbacks
    - Swallowing errors silently

    **Detectable Patterns:**

    - `Promise without catch`
    - `async without try-catch`

??? info "`js-008` — Avoid magic numbers and strings"
    **Use named constants for literal values**

    **Common Violations:**

    - Hardcoded numbers with unclear meaning
    - String literals repeated multiple times
    - Configuration values inline

    **Detectable Patterns:**

    - ` = 0`
    - ` = 1`

??? info "`js-009` — Prefer composition over inheritance"
    **Use object composition and mixins instead of deep class hierarchies**

    **Common Violations:**

    - Inheritance chains > 2 levels
    - Overuse of class inheritance
    - Not using composition patterns

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_inheritance_depth` | `2` |

??? info "`js-010` — Keep functions pure when possible"
    **Minimize side effects and favor pure functions**

    **Common Violations:**

    - Functions modifying external state
    - Functions with hidden side effects
    - Impure array methods (push, splice) when map/filter would work

    **Detectable Patterns:**

    - `push(`
    - `splice(`

??? info "`js-011` — Use meaningful names"
    **Variable and function names should clearly express intent**

    **Common Violations:**

    - Single letter variables (except loop counters)
    - Abbreviations without context
    - Generic names (data, value, temp)
    - Misleading names

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `min_identifier_length` | `2` |


## Detector Catalog

### Architecture

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **JsGlobalStateDetector** | Detect direct access to global mutable state via ``window``, ``globalThis``, or ``global`` | `js-004` |
| **JsInheritanceDepthDetector** | Detect class hierarchies that exceed a maximum inheritance depth | `js-009` |

### Async

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **JsCallbackNestingDetector** | Detect deeply nested callbacks that create "callback hell" | `js-001` |

### Clarity

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **JsMagicNumbersDetector** | Detect unexplained numeric literals (magic numbers) in JavaScript code | `js-008` |

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **JsStrictEqualityDetector** | Detect loose equality operators (``==`` / ``!=``) in JavaScript | `js-003` |

### Design

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **JsFunctionLengthDetector** | Detect JavaScript functions that exceed a configurable line-count limit | `js-005` |

### Error Handling

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **JsAsyncErrorHandlingDetector** | Detect async functions and promise chains with missing error handling | `js-007` |

### Functional

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **JsPureFunctionDetector** | Detect in-place array mutations that break functional programming principles | `js-010` |

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **JsModernFeaturesDetector** | Detect opportunities to adopt modern ES6+ language features | `js-006` |

### Immutability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **JsNoVarDetector** | Detect usage of the legacy ``var`` keyword for variable declarations | `js-002` |

### Readability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **JsMeaningfulNamesDetector** | Detect overly short or cryptic identifiers in JavaScript declarations | `js-011` |


??? example "Principle → Detector Wiring"
    ```mermaid
    graph LR
    js_001["js-001<br/>Avoid callback hell"]
    js_002["js-002<br/>Prefer const over let, never var"]
    js_003["js-003<br/>Use strict equality"]
    js_004["js-004<br/>Avoid global state"]
    js_005["js-005<br/>Functions should do one thing"]
    js_006["js-006<br/>Use modern ES6+ features"]
    js_007["js-007<br/>Handle errors explicitly"]
    js_008["js-008<br/>Avoid magic numbers and strings"]
    js_009["js-009<br/>Prefer composition over inheritance"]
    js_010["js-010<br/>Keep functions pure when possible"]
    js_011["js-011<br/>Use meaningful names"]
    det_JsAsyncErrorHandlingDetector["JsAsyncErrorHandlingDetector"]
    js_007 --> det_JsAsyncErrorHandlingDetector
    det_JsCallbackNestingDetector["JsCallbackNestingDetector"]
    js_001 --> det_JsCallbackNestingDetector
    det_JsFunctionLengthDetector["JsFunctionLengthDetector"]
    js_005 --> det_JsFunctionLengthDetector
    det_JsGlobalStateDetector["JsGlobalStateDetector"]
    js_004 --> det_JsGlobalStateDetector
    det_JsInheritanceDepthDetector["JsInheritanceDepthDetector"]
    js_009 --> det_JsInheritanceDepthDetector
    det_JsMagicNumbersDetector["JsMagicNumbersDetector"]
    js_008 --> det_JsMagicNumbersDetector
    det_JsMeaningfulNamesDetector["JsMeaningfulNamesDetector"]
    js_011 --> det_JsMeaningfulNamesDetector
    det_JsModernFeaturesDetector["JsModernFeaturesDetector"]
    js_006 --> det_JsModernFeaturesDetector
    det_JsNoVarDetector["JsNoVarDetector"]
    js_002 --> det_JsNoVarDetector
    det_JsPureFunctionDetector["JsPureFunctionDetector"]
    js_010 --> det_JsPureFunctionDetector
    det_JsStrictEqualityDetector["JsStrictEqualityDetector"]
    js_003 --> det_JsStrictEqualityDetector
    classDef principle fill:#4051b5,color:#fff,stroke:none
    classDef detector fill:#26a269,color:#fff,stroke:none
    class js_001 principle
    class js_002 principle
    class js_003 principle
    class js_004 principle
    class js_005 principle
    class js_006 principle
    class js_007 principle
    class js_008 principle
    class js_009 principle
    class js_010 principle
    class js_011 principle
    class det_JsAsyncErrorHandlingDetector detector
    class det_JsCallbackNestingDetector detector
    class det_JsFunctionLengthDetector detector
    class det_JsGlobalStateDetector detector
    class det_JsInheritanceDepthDetector detector
    class det_JsMagicNumbersDetector detector
    class det_JsMeaningfulNamesDetector detector
    class det_JsModernFeaturesDetector detector
    class det_JsNoVarDetector detector
    class det_JsPureFunctionDetector detector
    class det_JsStrictEqualityDetector detector
    ```

## Configuration

```yaml
languages:
  javascript:
    enabled: true
    pipeline:
      - type: js-callback-nesting
        max_callback_nesting: 2
      - type: js-no-var
        detect_var_usage: True
      - type: js-function-length
        max_function_length: 50
```


## See Also

- [TypeScript](typescript.md) — Type-safe superset with additional principles
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
