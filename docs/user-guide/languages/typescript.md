---
title: TypeScript
description: "18 zen principles enforced by 25 detectors: Type Safety and Maintainability."
icon: material/language-typescript
tags:
  - TypeScript
---

# TypeScript

TypeScript's power lies in its type system — but that power is easily undermined by `any` casts, missing return types, and non-null assertions. MCP Zen of Languages encodes **10 type-safety principles** that catch the patterns where TypeScript's guarantees quietly erode.

## Optional External Tool Augmentation

!!! info "Consent-first external tooling"
    External tool execution is optional and disabled by default. Use
    `--enable-external-tools` (CLI) or `enable_external_tools=true` (MCP)
    to opt in. Missing tools should return recommendations; no automatic
    installs occur during analysis.

| Tool | Default invocation | Output |
|------|---------------------|--------|
| `biome` | `biome lint --stdin-file-path stdin.ts --reporter json` | JSON |
| `eslint` | `eslint --stdin --format json` | JSON |
| `prettier` | `prettier --check --stdin-filepath stdin.ts` | Text / structured stderr |

!!! tip "Temporary runner fallback"
    For temporary execution via package runners, use
    `--allow-temporary-runners` (CLI) or `allow_temporary_runners=true` (MCP).


## Zen Principles

18 principles across 8 categories, drawn from [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html).

<div class="grid" markdown>

:material-tag-outline: **Async** · 1 principle
:material-tag-outline: **Clarity** · 1 principle
:material-tag-outline: **Configuration** · 1 principle
:material-tag-outline: **Idioms** · 6 principles
:material-tag-outline: **Immutability** · 1 principle
:material-tag-outline: **Organization** · 1 principle
:material-tag-outline: **Readability** · 1 principle
:material-tag-outline: **Type Safety** · 6 principles

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `ts-001` | Avoid 'any' type | Type Safety | 9 | `ZEN-EXPLICIT-INTENT` |
| `ts-002` | Use strict mode | Configuration | 9 | `ZEN-EXPLICIT-INTENT` |
| `ts-003` | Prefer interfaces over type aliases for objects | Idioms | 5 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-UNAMBIGUOUS-NAME`, `ZEN-PROPORTIONATE-COMPLEXITY` |
| `ts-004` | Always specify return types | Type Safety | 7 | `ZEN-EXPLICIT-INTENT`, `ZEN-FAIL-FAST` |
| `ts-005` | Use readonly when appropriate | Immutability | 6 | `ZEN-VISIBLE-STATE` |
| `ts-006` | Leverage type guards | Type Safety | 7 | `ZEN-EXPLICIT-INTENT` |
| `ts-007` | Use utility types | Idioms | 6 | `ZEN-RIGHT-ABSTRACTION` |
| `ts-008` | Avoid non-null assertions | Type Safety | 8 | `ZEN-EXPLICIT-INTENT` |
| `ts-009` | Use enums or const assertions appropriately | Idioms | 6 | `ZEN-RIGHT-ABSTRACTION` |
| `ts-010` | Prefer unknown over any for uncertain types | Type Safety | 7 | `ZEN-EXPLICIT-INTENT`, `ZEN-FAIL-FAST` |
| `ts-011` | Use optional chaining instead of manual null checks | Idioms | 5 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-RETURN-EARLY` |
| `ts-012` | Prefer for-of and array methods over index loops | Idioms | 4 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-FAIL-FAST` |
| `ts-013` | Prefer async/await over raw promise chains | Async | 6 | `ZEN-FAIL-FAST`, `ZEN-RETURN-EARLY` |
| `ts-014` | Prefer named exports over default exports | Organization | 4 | `ZEN-STRICT-FENCES`, `ZEN-UNAMBIGUOUS-NAME` |
| `ts-015` | Avoid catch-all types like Object or {} | Type Safety | 6 | `ZEN-EXPLICIT-INTENT` |
| `ts-016` | Avoid console usage in production code | Clarity | 4 | `ZEN-EXPLICIT-INTENT`, `ZEN-FAIL-FAST` |
| `ts-017` | Use ES module imports instead of require() | Idioms | 5 | `ZEN-RIGHT-ABSTRACTION` |
| `ts-018` | Use template literals instead of string concatenation | Readability | 3 | `ZEN-UNAMBIGUOUS-NAME`, `ZEN-FAIL-FAST` |

??? info "`ts-001` — Avoid 'any' type"
    **Use proper types instead of any to maintain type safety**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Explicit any annotations
    - Implicit any from missing types
    - Type assertions to any
    - any[] arrays

    **Detectable Patterns:**

    - `: any`
    - `as any`

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_any_usages` | `0` |
    | `detect_explicit_any` | `True` |
    | `detect_assertions_any` | `True` |
    | `detect_any_arrays` | `True` |

    !!! tip "Recommended Fix"
        unknown, specific types, or generics

??? info "`ts-002` — Use strict mode"
    **Enable strict TypeScript compiler options**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - strict: false in tsconfig
    - Disabled strictNullChecks
    - Disabled noImplicitAny

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `require_strict` | `True` |
    | `require_no_implicit_any` | `True` |
    | `require_strict_null_checks` | `True` |

??? info "`ts-003` — Prefer interfaces over type aliases for objects"
    **Use interfaces for object shapes, types for unions/primitives**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-UNAMBIGUOUS-NAME`, `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - Type aliases for simple object shapes
    - Not using interface extension

    **Detectable Patterns:**

    - `type ObjectShape = { ... }`

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_object_type_aliases` | `0` |

??? info "`ts-004` — Always specify return types"
    **Explicit return types improve readability and catch errors**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-FAIL-FAST`
    **Common Violations:**

    - Public functions without return type
    - Exported functions without return type
    - Callbacks without return type

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `require_return_types` | `True` |

??? info "`ts-005` — Use readonly when appropriate"
    **Mark immutable properties as readonly**

    **Universal Dogmas:** `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Properties that should be readonly
    - Arrays that should be ReadonlyArray
    - Mutable config objects

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `require_readonly_properties` | `True` |
    | `min_readonly_occurrences` | `1` |

??? info "`ts-006` — Leverage type guards"
    **Use type guards for runtime type checking**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Type assertions without validation
    - Not narrowing union types
    - Using 'as' instead of type guards

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_type_assertions` | `0` |

    !!! tip "Recommended Fix"
        User-defined type guards (is predicates)

??? info "`ts-007` — Use utility types"
    **Leverage built-in utility types (Partial, Pick, Omit, etc.)**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Manual type transformations
    - Duplicated type definitions
    - Not using Partial for optional updates

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `min_utility_type_usage` | `1` |
    | `min_object_type_aliases` | `2` |

??? info "`ts-008` — Avoid non-null assertions"
    **Handle null/undefined properly instead of using !**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Excessive use of ! operator
    - Non-null assertions without validation
    - Chained non-null assertions

    **Detectable Patterns:**

    - `variable!`
    - `?.!`

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_non_null_assertions` | `0` |

??? info "`ts-009` — Use enums or const assertions appropriately"
    **Use const enums or const assertions for constant values**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Plain objects for enumerations
    - String literal unions without const assertion
    - Regular enums that should be const

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_plain_enum_objects` | `0` |

??? info "`ts-010` — Prefer unknown over any for uncertain types"
    **Use unknown when type is truly unknown, forces type checking**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-FAIL-FAST`
    **Common Violations:**

    - Using any for API responses
    - Using any for error types
    - any for third-party data

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_any_for_unknown` | `0` |

??? info "`ts-011` — Use optional chaining instead of manual null checks"
    **Optional chaining (?.) simplifies nested property access and avoids verbose guard clauses**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-RETURN-EARLY`
    **Common Violations:**

    - Manual && chains for nested access
    - Verbose null/undefined checks before property access
    - Nested ternaries for safe property access

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_manual_null_checks` | `0` |

??? info "`ts-012` — Prefer for-of and array methods over index loops"
    **Modern iteration is more readable and less error-prone than C-style for loops**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-FAIL-FAST`
    **Common Violations:**

    - Using for(let i=0; ...) when for-of suffices
    - Index-based iteration over arrays
    - Manual length-based loops

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_index_loops` | `0` |

??? info "`ts-013` — Prefer async/await over raw promise chains"
    **async/await produces flatter, more readable asynchronous code than .then() chains**

    **Universal Dogmas:** `ZEN-FAIL-FAST`, `ZEN-RETURN-EARLY`
    **Common Violations:**

    - Using .then() chains instead of await
    - Nested .then() callbacks
    - Mixing .then() and async/await styles

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_promise_chains` | `0` |

??? info "`ts-014` — Prefer named exports over default exports"
    **Named exports improve refactoring support and IDE auto-imports**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`, `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Using export default for modules
    - Default-exporting classes or functions
    - Inconsistent export styles in a project

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_default_exports` | `0` |

??? info "`ts-015` — Avoid catch-all types like Object or {}"
    **Catch-all types bypass the type system; use precise types or Record instead**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Typing as Object or object
    - Using {} as a type annotation
    - Overly broad type parameters

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_catch_all_types` | `0` |

??? info "`ts-016` — Avoid console usage in production code"
    **Use a structured logging framework instead of console.log for production code**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-FAIL-FAST`
    **Common Violations:**

    - console.log for debugging left in code
    - console.error instead of proper error handling
    - console.warn without structured logging

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_console_usages` | `0` |

??? info "`ts-017` — Use ES module imports instead of require()"
    **ES module syntax enables tree-shaking and static analysis**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Using require() in TypeScript files
    - Mixing require and import styles
    - CommonJS patterns in modern TypeScript

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_require_calls` | `0` |

??? info "`ts-018` — Use template literals instead of string concatenation"
    **Template literals are more readable and less error-prone than + concatenation**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`, `ZEN-FAIL-FAST`
    **Common Violations:**

    - String concatenation with + operator
    - Multi-part string building with +
    - Variable interpolation via concatenation

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_string_concats` | `0` |


## Detector Catalog

### Async

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TsPromiseChainDetector** | Detects raw ``.then()`` promise chains replaceable by async/await | `ts-013` |
| **TsAsyncAwaitDetector** | Detects raw ``.then()`` promise chains encouraging async/await usage | `ts-013` |

### Clarity

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TsConsoleUsageDetector** | Detects ``console.*`` calls in TypeScript production code | `ts-016` |
| **TsNoConsoleDetector** | Detects ``console.*`` calls in production code | `ts-016` |

### Configuration

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TsStrictModeDetector** | Checks whether strict compiler options are enabled in the project | `ts-002` |

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TsInterfacePreferenceDetector** | Flags object-shaped type aliases that should be interfaces instead | `ts-003` |
| **TsUtilityTypesDetector** | Detects missed opportunities to use built-in utility types like ``Partial`` or ``Pick`` | `ts-007` |
| **TsEnumConstDetector** | Detects plain object literals used as constants instead of enums or ``as const`` | `ts-009` |
| **TsOptionalChainingDetector** | Detects manual null-check chains replaceable by optional chaining (``?.``) | `ts-011` |
| **TsIndexLoopDetector** | Detects C-style index-based ``for`` loops replaceable by ``for-of`` or array methods | `ts-012` |
| **TsRequireImportDetector** | Detects ``require()`` calls encouraging ES module imports instead | `ts-017` |
| **TsForOfDetector** | Detects C-style index-based ``for`` loops encouraging ``for...of`` iteration | `ts-012` |
| **TsImportOrderDetector** | Detects CommonJS ``require()`` calls mixed with ES module imports | `ts-017` |

### Immutability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TsReadonlyDetector** | Detects insufficient use of ``readonly`` for immutable properties and arrays | `ts-005` |

### Organization

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TsDefaultExportDetector** | Detects ``export default`` statements encouraging named exports instead | `ts-014` |
| **TsNamedExportDetector** | Detects ``export default`` usages encouraging named exports | `ts-014` |

### Readability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TsStringConcatDetector** | Detects string concatenation patterns encouraging template literals | `ts-018` |
| **TsTemplateLiteralDetector** | Detects string concatenation patterns encouraging template literals | `ts-018` |

### Type Safety

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TsAnyUsageDetector** | Detects excessive use of the ``any`` type that undermines TypeScript's value | `ts-001` |
| **TsReturnTypeDetector** | Flags exported functions that lack explicit return type annotations | `ts-004` |
| **TsTypeGuardDetector** | Flags overuse of type assertions (``as T``) instead of user-defined type guards | `ts-006` |
| **TsNonNullAssertionDetector** | Flags excessive non-null assertion operators (``!``) that silence null safety | `ts-008` |
| **TsUnknownOverAnyDetector** | Flags codebases that use ``any`` without ever using the safer ``unknown`` alternative | `ts-010` |
| **TsCatchAllTypeDetector** | Detects catch-all type annotations (``Object``, ``object``, ``{}``) | `ts-015` |
| **TsObjectTypeDetector** | Detects generic ``Object``/``object``/``{}`` type annotations | `ts-015` |


??? example "Principle → Detector Wiring"
    ```mermaid
    graph LR
    ts_001["ts-001<br/>Avoid 'any' type"]
    ts_002["ts-002<br/>Use strict mode"]
    ts_003["ts-003<br/>Prefer interfaces over type aliases for ..."]
    ts_004["ts-004<br/>Always specify return types"]
    ts_005["ts-005<br/>Use readonly when appropriate"]
    ts_006["ts-006<br/>Leverage type guards"]
    ts_007["ts-007<br/>Use utility types"]
    ts_008["ts-008<br/>Avoid non-null assertions"]
    ts_009["ts-009<br/>Use enums or const assertions appropriat..."]
    ts_010["ts-010<br/>Prefer unknown over any for uncertain ty..."]
    ts_011["ts-011<br/>Use optional chaining instead of manual ..."]
    ts_012["ts-012<br/>Prefer for-of and array methods over ind..."]
    ts_013["ts-013<br/>Prefer async/await over raw promise chai..."]
    ts_014["ts-014<br/>Prefer named exports over default export..."]
    ts_015["ts-015<br/>Avoid catch-all types like Object or {}"]
    ts_016["ts-016<br/>Avoid console usage in production code"]
    ts_017["ts-017<br/>Use ES module imports instead of require..."]
    ts_018["ts-018<br/>Use template literals instead of string ..."]
    det_TsAnyUsageDetector["TsAnyUsageDetector"]
    ts_001 --> det_TsAnyUsageDetector
    det_TsAsyncAwaitDetector["TsAsyncAwaitDetector"]
    ts_013 --> det_TsAsyncAwaitDetector
    det_TsCatchAllTypeDetector["TsCatchAllTypeDetector"]
    ts_015 --> det_TsCatchAllTypeDetector
    det_TsConsoleUsageDetector["TsConsoleUsageDetector"]
    ts_016 --> det_TsConsoleUsageDetector
    det_TsDefaultExportDetector["TsDefaultExportDetector"]
    ts_014 --> det_TsDefaultExportDetector
    det_TsEnumConstDetector["TsEnumConstDetector"]
    ts_009 --> det_TsEnumConstDetector
    det_TsForOfDetector["TsForOfDetector"]
    ts_012 --> det_TsForOfDetector
    det_TsImportOrderDetector["TsImportOrderDetector"]
    ts_017 --> det_TsImportOrderDetector
    det_TsIndexLoopDetector["TsIndexLoopDetector"]
    ts_012 --> det_TsIndexLoopDetector
    det_TsInterfacePreferenceDetector["TsInterfacePreferenceDetector"]
    ts_003 --> det_TsInterfacePreferenceDetector
    det_TsNamedExportDetector["TsNamedExportDetector"]
    ts_014 --> det_TsNamedExportDetector
    det_TsNoConsoleDetector["TsNoConsoleDetector"]
    ts_016 --> det_TsNoConsoleDetector
    det_TsNonNullAssertionDetector["TsNonNullAssertionDetector"]
    ts_008 --> det_TsNonNullAssertionDetector
    det_TsObjectTypeDetector["TsObjectTypeDetector"]
    ts_015 --> det_TsObjectTypeDetector
    det_TsOptionalChainingDetector["TsOptionalChainingDetector"]
    ts_011 --> det_TsOptionalChainingDetector
    det_TsPromiseChainDetector["TsPromiseChainDetector"]
    ts_013 --> det_TsPromiseChainDetector
    det_TsReadonlyDetector["TsReadonlyDetector"]
    ts_005 --> det_TsReadonlyDetector
    det_TsRequireImportDetector["TsRequireImportDetector"]
    ts_017 --> det_TsRequireImportDetector
    det_TsReturnTypeDetector["TsReturnTypeDetector"]
    ts_004 --> det_TsReturnTypeDetector
    det_TsStrictModeDetector["TsStrictModeDetector"]
    ts_002 --> det_TsStrictModeDetector
    det_TsStringConcatDetector["TsStringConcatDetector"]
    ts_018 --> det_TsStringConcatDetector
    det_TsTemplateLiteralDetector["TsTemplateLiteralDetector"]
    ts_018 --> det_TsTemplateLiteralDetector
    det_TsTypeGuardDetector["TsTypeGuardDetector"]
    ts_006 --> det_TsTypeGuardDetector
    det_TsUnknownOverAnyDetector["TsUnknownOverAnyDetector"]
    ts_010 --> det_TsUnknownOverAnyDetector
    det_TsUtilityTypesDetector["TsUtilityTypesDetector"]
    ts_007 --> det_TsUtilityTypesDetector
    classDef principle fill:#4051b5,color:#fff,stroke:none
    classDef detector fill:#26a269,color:#fff,stroke:none
    class ts_001 principle
    class ts_002 principle
    class ts_003 principle
    class ts_004 principle
    class ts_005 principle
    class ts_006 principle
    class ts_007 principle
    class ts_008 principle
    class ts_009 principle
    class ts_010 principle
    class ts_011 principle
    class ts_012 principle
    class ts_013 principle
    class ts_014 principle
    class ts_015 principle
    class ts_016 principle
    class ts_017 principle
    class ts_018 principle
    class det_TsAnyUsageDetector detector
    class det_TsAsyncAwaitDetector detector
    class det_TsCatchAllTypeDetector detector
    class det_TsConsoleUsageDetector detector
    class det_TsDefaultExportDetector detector
    class det_TsEnumConstDetector detector
    class det_TsForOfDetector detector
    class det_TsImportOrderDetector detector
    class det_TsIndexLoopDetector detector
    class det_TsInterfacePreferenceDetector detector
    class det_TsNamedExportDetector detector
    class det_TsNoConsoleDetector detector
    class det_TsNonNullAssertionDetector detector
    class det_TsObjectTypeDetector detector
    class det_TsOptionalChainingDetector detector
    class det_TsPromiseChainDetector detector
    class det_TsReadonlyDetector detector
    class det_TsRequireImportDetector detector
    class det_TsReturnTypeDetector detector
    class det_TsStrictModeDetector detector
    class det_TsStringConcatDetector detector
    class det_TsTemplateLiteralDetector detector
    class det_TsTypeGuardDetector detector
    class det_TsUnknownOverAnyDetector detector
    class det_TsUtilityTypesDetector detector
    ```

## Configuration

```yaml
languages:
  typescript:
    enabled: true
    pipeline:
      - type: ts-any-usage
        max_any_usages: 0
        detect_explicit_any: True
        detect_assertions_any: True
        detect_any_arrays: True
      - type: ts-strict-mode
        require_strict: True
        require_no_implicit_any: True
        require_strict_null_checks: True
      - type: ts-interface-preference
        max_object_type_aliases: 0
      - type: ts-return-types
        require_return_types: True
      - type: ts-readonly
        require_readonly_properties: True
        min_readonly_occurrences: 1
      - type: ts-type-guards
        max_type_assertions: 0
      - type: ts-utility-types
        min_utility_type_usage: 1
        min_object_type_aliases: 2
      - type: ts-non-null-assertions
        max_non_null_assertions: 0
      - type: ts-enum-const
        max_plain_enum_objects: 0
      - type: ts-unknown-over-any
        max_any_for_unknown: 0
      - type: ts-optional-chaining
        max_manual_null_checks: 0
      - type: ts-index-loops
        max_index_loops: 0
      - type: ts-promise-chains
        max_promise_chains: 0
      - type: ts-default-exports
        max_default_exports: 0
      - type: ts-catch-all-types
        max_catch_all_types: 0
      - type: ts-console-usage
        max_console_usages: 0
      - type: ts-require-imports
        max_require_calls: 0
      - type: ts-string-concats
        max_string_concats: 0
      - type: ts-for-of
        max_index_loops: 0
        max_index_based_loops: 0
      - type: ts-async-await
        max_promise_chains: 2
        max_then_chains: 0
      - type: ts-named-export
        max_default_exports: 0
        max_default_export_usages: 0
      - type: ts-object-type
        max_catch_all_types: 0
        max_object_types: 0
      - type: ts-no-console
        max_console_usages: 0
        max_console_statements: 0
      - type: ts-import-order
        max_require_calls: 0
        max_require_usages: 0
      - type: ts-template-literal
        max_string_concats: 3
        max_string_concatenations: 0
```

???+ tip "Migrating from JavaScript?"
    Start with `max_any_count: 10` and lower it sprint by sprint. Use the `ts-010` detector to find `any` that should be `unknown` first — those are the safest to fix.

## See Also

- [JavaScript](javascript.md) — Related principles for JS codebases
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
