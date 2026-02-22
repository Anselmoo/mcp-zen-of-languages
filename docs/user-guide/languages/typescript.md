---
title: TypeScript
description: "10 zen principles enforced by 10 detectors: Type Safety and Maintainability."
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

10 principles across 4 categories, drawn from [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html).

<div class="grid" markdown>

:material-tag-outline: **Configuration** · 1 principle
:material-tag-outline: **Idioms** · 3 principles
:material-tag-outline: **Immutability** · 1 principle
:material-tag-outline: **Type Safety** · 5 principles

</div>

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `ts-001` | Avoid 'any' type | Type Safety | 9 |
| `ts-002` | Use strict mode | Configuration | 9 |
| `ts-003` | Prefer interfaces over type aliases for objects | Idioms | 5 |
| `ts-004` | Always specify return types | Type Safety | 7 |
| `ts-005` | Use readonly when appropriate | Immutability | 6 |
| `ts-006` | Leverage type guards | Type Safety | 7 |
| `ts-007` | Use utility types | Idioms | 6 |
| `ts-008` | Avoid non-null assertions | Type Safety | 8 |
| `ts-009` | Use enums or const assertions appropriately | Idioms | 6 |
| `ts-010` | Prefer unknown over any for uncertain types | Type Safety | 7 |

??? info "`ts-001` — Avoid 'any' type"
    **Use proper types instead of any to maintain type safety**

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

    **Common Violations:**

    - Using any for API responses
    - Using any for error types
    - any for third-party data

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_any_for_unknown` | `0` |


## Detector Catalog

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

### Immutability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TsReadonlyDetector** | Detects insufficient use of ``readonly`` for immutable properties and arrays | `ts-005` |

### Type Safety

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TsAnyUsageDetector** | Detects excessive use of the ``any`` type that undermines TypeScript's value | `ts-001` |
| **TsReturnTypeDetector** | Flags exported functions that lack explicit return type annotations | `ts-004` |
| **TsTypeGuardDetector** | Flags overuse of type assertions (``as T``) instead of user-defined type guards | `ts-006` |
| **TsNonNullAssertionDetector** | Flags excessive non-null assertion operators (``!``) that silence null safety | `ts-008` |
| **TsUnknownOverAnyDetector** | Flags codebases that use ``any`` without ever using the safer ``unknown`` alternative | `ts-010` |


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
    det_TsAnyUsageDetector["TsAnyUsageDetector"]
    ts_001 --> det_TsAnyUsageDetector
    det_TsEnumConstDetector["TsEnumConstDetector"]
    ts_009 --> det_TsEnumConstDetector
    det_TsInterfacePreferenceDetector["TsInterfacePreferenceDetector"]
    ts_003 --> det_TsInterfacePreferenceDetector
    det_TsNonNullAssertionDetector["TsNonNullAssertionDetector"]
    ts_008 --> det_TsNonNullAssertionDetector
    det_TsReadonlyDetector["TsReadonlyDetector"]
    ts_005 --> det_TsReadonlyDetector
    det_TsReturnTypeDetector["TsReturnTypeDetector"]
    ts_004 --> det_TsReturnTypeDetector
    det_TsStrictModeDetector["TsStrictModeDetector"]
    ts_002 --> det_TsStrictModeDetector
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
    class det_TsAnyUsageDetector detector
    class det_TsEnumConstDetector detector
    class det_TsInterfacePreferenceDetector detector
    class det_TsNonNullAssertionDetector detector
    class det_TsReadonlyDetector detector
    class det_TsReturnTypeDetector detector
    class det_TsStrictModeDetector detector
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
```

???+ tip "Migrating from JavaScript?"
    Start with `max_any_count: 10` and lower it sprint by sprint. Use the `ts-010` detector to find `any` that should be `unknown` first — those are the safest to fix.

## See Also

- [JavaScript](javascript.md) — Related principles for JS codebases
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
