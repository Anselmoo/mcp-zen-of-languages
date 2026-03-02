---
title: JavaScript
description: "18 zen principles enforced by 18 detectors: Modern JavaScript Best Practices."
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

18 principles across 11 categories, drawn from [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript).

<div class="grid" markdown>

:material-tag-outline: **Architecture** · 3 principles
:material-tag-outline: **Async** · 1 principle
:material-tag-outline: **Clarity** · 1 principle
:material-tag-outline: **Correctness** · 2 principles
:material-tag-outline: **Design** · 2 principles
:material-tag-outline: **Error Handling** · 1 principle
:material-tag-outline: **Functional** · 1 principle
:material-tag-outline: **Idioms** · 4 principles
:material-tag-outline: **Immutability** · 1 principle
:material-tag-outline: **Readability** · 1 principle
:material-tag-outline: **Security** · 1 principle

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `js-001` | Avoid callback hell | Async | 8 | `ZEN-FAIL-FAST`, `ZEN-RETURN-EARLY` |
| `js-002` | Prefer const over let, never var | Immutability | 7 | `ZEN-VISIBLE-STATE` |
| `js-003` | Use strict equality | Correctness | 8 | `ZEN-EXPLICIT-INTENT` |
| `js-004` | Avoid global state | Architecture | 9 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE` |
| `js-005` | Functions should do one thing | Design | 7 | `ZEN-RIGHT-ABSTRACTION` |
| `js-006` | Use modern ES6+ features | Idioms | 6 | `ZEN-RIGHT-ABSTRACTION` |
| `js-007` | Handle errors explicitly | Error Handling | 9 | `ZEN-FAIL-FAST`, `ZEN-EXPLICIT-INTENT` |
| `js-008` | Avoid magic numbers and strings | Clarity | 6 | `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME` |
| `js-009` | Prefer composition over inheritance | Architecture | 7 | `ZEN-RIGHT-ABSTRACTION` |
| `js-010` | Keep functions pure when possible | Functional | 6 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE` |
| `js-011` | Use meaningful names | Readability | 8 | `ZEN-UNAMBIGUOUS-NAME` |
| `js-012` | Use destructuring for assignment | Idioms | 5 | `ZEN-RIGHT-ABSTRACTION` |
| `js-013` | Use object spread over Object.assign | Idioms | 5 | `ZEN-RIGHT-ABSTRACTION` |
| `js-014` | Avoid with statement | Correctness | 9 | `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE` |
| `js-015` | Limit function parameter count | Design | 7 | `ZEN-RIGHT-ABSTRACTION` |
| `js-016` | No eval() | Security | 9 | `ZEN-STRICT-FENCES` |
| `js-017` | Prefer Array.from/spread over arguments | Idioms | 6 | `ZEN-RIGHT-ABSTRACTION` |
| `js-018` | No prototype mutation on built-in objects | Architecture | 9 | `ZEN-RIGHT-ABSTRACTION` |

??? info "`js-001` — Avoid callback hell"
    **Use modern async patterns instead of nested callbacks**

    **Universal Dogmas:** `ZEN-FAIL-FAST`, `ZEN-RETURN-EARLY`
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

    **Universal Dogmas:** `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Using var keyword
    - Using let for values that don't change
    - Reassigning const-eligible variables

    **Detectable Patterns:**

    - `var keyword usage`
    - `let without reassignment`

??? info "`js-003` — Use strict equality"
    **Always use === and !== to avoid type coercion bugs**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Using == or !=
    - Relying on truthy/falsy in critical comparisons

    **Detectable Patterns:**

    - `== comparison`
    - `!= comparison`

??? info "`js-004` — Avoid global state"
    **Minimize global variables and shared mutable state**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE`
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

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
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

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
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

    **Universal Dogmas:** `ZEN-FAIL-FAST`, `ZEN-EXPLICIT-INTENT`
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

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Hardcoded numbers with unclear meaning
    - String literals repeated multiple times
    - Configuration values inline

    **Detectable Patterns:**

    - ` = 0`
    - ` = 1`

??? info "`js-009` — Prefer composition over inheritance"
    **Use object composition and mixins instead of deep class hierarchies**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
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

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Functions modifying external state
    - Functions with hidden side effects
    - Impure array methods (push, splice) when map/filter would work

    **Detectable Patterns:**

    - `push(`
    - `splice(`

??? info "`js-011` — Use meaningful names"
    **Variable and function names should clearly express intent**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Single letter variables (except loop counters)
    - Abbreviations without context
    - Generic names (data, value, temp)
    - Misleading names

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `min_identifier_length` | `2` |

??? info "`js-012` — Use destructuring for assignment"
    **Prefer destructuring over manually extracting object properties or array elements**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Consecutive property extractions from same object
    - Repetitive array index access (arr[0], arr[1])
    - Repeated parameter property access

??? info "`js-013` — Use object spread over Object.assign"
    **Prefer the spread syntax ({...obj}) over Object.assign for shallow cloning and merging**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Object.assign with empty first argument
    - Object.assign for shallow cloning
    - Object.assign with 3+ arguments when spread is clearer

??? info "`js-014` — Avoid with statement"
    **The with statement is disallowed in strict mode and creates ambiguous scope resolution**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Any usage of with statement

??? info "`js-015` — Limit function parameter count"
    **Functions with too many positional parameters should accept an options object instead**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Functions with more than 3 positional parameters
    - Constructor functions with more than 4 parameters

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_params` | `3` |

??? info "`js-016` — No eval()"
    **Use of eval() introduces security vulnerabilities and prevents JavaScript engine optimizations**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`
    **Common Violations:**

    - Direct eval() calls
    - new Function() constructor
    - setTimeout or setInterval with string arguments

??? info "`js-017` — Prefer Array.from/spread over arguments"
    **The arguments object is a legacy non-array; use rest parameters (...args) instead**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Direct use of arguments keyword
    - Array.prototype.slice.call(arguments)
    - Array.from(arguments)

    !!! tip "Recommended Fix"
        Rest parameters (...args)

??? info "`js-018` — No prototype mutation on built-in objects"
    **Extending native prototypes creates global side effects and can break third-party code**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Array.prototype modification
    - String.prototype modification
    - Object.prototype modification
    - Function.prototype modification


## Detector Catalog

### Architecture

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **JsGlobalStateDetector** | Detect direct access to global mutable state via ``window``, ``globalThis``, or ``global`` | `js-004` |
| **JsInheritanceDepthDetector** | Detect class hierarchies that exceed a maximum inheritance depth | `js-009` |
| **JsNoPrototypeMutationDetector** | Detect mutations of built-in object prototypes | `js-018` |

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
| **JsNoWithDetector** | Detect usage of the ``with`` statement in JavaScript | `js-014` |

### Design

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **JsFunctionLengthDetector** | Detect JavaScript functions that exceed a configurable line-count limit | `js-005` |
| **JsParamCountDetector** | Detect functions with too many parameters | `js-015` |

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
| **JsDestructuringDetector** | Detect repeated property access on the same object without destructuring | `js-012` |
| **JsObjectSpreadDetector** | Detect usage of ``Object.assign`` where object spread is preferred | `js-013` |
| **JsNoArgumentsDetector** | Detect usage of the legacy ``arguments`` object in JavaScript | `js-017` |

### Immutability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **JsNoVarDetector** | Detect usage of the legacy ``var`` keyword for variable declarations | `js-002` |

### Readability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **JsMeaningfulNamesDetector** | Detect overly short or cryptic identifiers in JavaScript declarations | `js-011` |

### Security

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **JsNoEvalDetector** | Detect usage of ``eval()`` or ``new Function()`` in JavaScript | `js-016` |


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
    js_012["js-012<br/>Use destructuring for assignment"]
    js_013["js-013<br/>Use object spread over Object.assign"]
    js_014["js-014<br/>Avoid with statement"]
    js_015["js-015<br/>Limit function parameter count"]
    js_016["js-016<br/>No eval()"]
    js_017["js-017<br/>Prefer Array.from/spread over arguments"]
    js_018["js-018<br/>No prototype mutation on built-in object..."]
    det_JsAsyncErrorHandlingDetector["JsAsyncErrorHandlingDetector"]
    js_007 --> det_JsAsyncErrorHandlingDetector
    det_JsCallbackNestingDetector["JsCallbackNestingDetector"]
    js_001 --> det_JsCallbackNestingDetector
    det_JsDestructuringDetector["JsDestructuringDetector"]
    js_012 --> det_JsDestructuringDetector
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
    det_JsNoArgumentsDetector["JsNoArgumentsDetector"]
    js_017 --> det_JsNoArgumentsDetector
    det_JsNoEvalDetector["JsNoEvalDetector"]
    js_016 --> det_JsNoEvalDetector
    det_JsNoPrototypeMutationDetector["JsNoPrototypeMutationDetector"]
    js_018 --> det_JsNoPrototypeMutationDetector
    det_JsNoVarDetector["JsNoVarDetector"]
    js_002 --> det_JsNoVarDetector
    det_JsNoWithDetector["JsNoWithDetector"]
    js_014 --> det_JsNoWithDetector
    det_JsObjectSpreadDetector["JsObjectSpreadDetector"]
    js_013 --> det_JsObjectSpreadDetector
    det_JsParamCountDetector["JsParamCountDetector"]
    js_015 --> det_JsParamCountDetector
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
    class js_012 principle
    class js_013 principle
    class js_014 principle
    class js_015 principle
    class js_016 principle
    class js_017 principle
    class js_018 principle
    class det_JsAsyncErrorHandlingDetector detector
    class det_JsCallbackNestingDetector detector
    class det_JsDestructuringDetector detector
    class det_JsFunctionLengthDetector detector
    class det_JsGlobalStateDetector detector
    class det_JsInheritanceDepthDetector detector
    class det_JsMagicNumbersDetector detector
    class det_JsMeaningfulNamesDetector detector
    class det_JsModernFeaturesDetector detector
    class det_JsNoArgumentsDetector detector
    class det_JsNoEvalDetector detector
    class det_JsNoPrototypeMutationDetector detector
    class det_JsNoVarDetector detector
    class det_JsNoWithDetector detector
    class det_JsObjectSpreadDetector detector
    class det_JsParamCountDetector detector
    class det_JsPureFunctionDetector detector
    class det_JsStrictEqualityDetector detector
    ```

## Configuration

```yaml
languages:
  javascript:
    enabled: true
    pipeline:
      - type: js_callback_nesting
        max_callback_nesting: 2
      - type: js_no_var
        detect_var_usage: True
      - type: js_function_length
        max_function_length: 50
      - type: js_param_count
        max_params: 3
```


## See Also

- [TypeScript](typescript.md) — Type-safe superset with additional principles
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
