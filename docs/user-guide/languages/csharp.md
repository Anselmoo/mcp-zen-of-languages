---
title: C#
description: "13 zen principles enforced by 13 detectors: Modern C# Best Practices (.NET 6+)."
icon: material/language-csharp
tags:
  - C#
---

# C#

Modern C# (C# 10–12) has evolved rapidly — records, pattern matching, nullable reference types, collection expressions. These **13 principles** catch codebases stuck on older patterns and guide them toward the expressive, safe idioms that the .NET team recommends.

## Zen Principles

13 principles across 8 categories, drawn from [C# Coding Conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions).

<div class="grid" markdown>

:material-tag-outline: **Async** · 1 principle
:material-tag-outline: **Clarity** · 1 principle
:material-tag-outline: **Design** · 1 principle
:material-tag-outline: **Error Handling** · 1 principle
:material-tag-outline: **Idioms** · 4 principles
:material-tag-outline: **Readability** · 3 principles
:material-tag-outline: **Resource Management** · 1 principle
:material-tag-outline: **Type Safety** · 1 principle

</div>

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `cs-001` | Use nullable reference types | Type Safety | 8 |
| `cs-002` | Use expression-bodied members | Idioms | 5 |
| `cs-003` | Prefer var for local variables | Readability | 5 |
| `cs-004` | Use async/await properly | Async | 9 |
| `cs-005` | Use pattern matching | Idioms | 6 |
| `cs-006` | Prefer string interpolation | Readability | 6 |
| `cs-007` | Use collection expressions | Idioms | 5 |
| `cs-008` | Follow naming conventions | Readability | 7 |
| `cs-009` | Use IDisposable and using statements | Resource Management | 9 |
| `cs-010` | Avoid magic numbers | Clarity | 6 |
| `cs-011` | Use LINQ appropriately | Idioms | 7 |
| `cs-012` | Handle exceptions properly | Error Handling | 8 |
| `cs-013` | Use records for DTOs | Design | 6 |

??? info "`cs-001` — Use nullable reference types"
    **Enable nullable reference types for null safety**

    **Common Violations:**

    - Not enabling nullable in project
    - Ignoring nullable warnings
    - Using ! operator excessively
    - Not annotating nullability

    **Detectable Patterns:**

    - `!#nullable enable`

??? info "`cs-002` — Use expression-bodied members"
    **Use => for simple properties and methods**

    **Common Violations:**

    - Full method bodies for one-line methods
    - Property getters with return statement
    - Not using lambda syntax when appropriate

    **Detectable Patterns:**

    - `!=>`

??? info "`cs-003` — Prefer var for local variables"
    **Use var when type is obvious from right side**

    **Common Violations:**

    - Explicit types when var would be clear
    - Verbose type declarations
    - Not using var with new expressions

    **Detectable Patterns:**

    - `!var `

??? info "`cs-004` — Use async/await properly"
    **Follow async best practices, avoid blocking**

    **Common Violations:**

    - .Result or .Wait() on Tasks
    - Async void methods (except event handlers)
    - Not using ConfigureAwait in libraries
    - Synchronous code in async methods

    **Detectable Patterns:**

    - `.Result`
    - `.Wait()`
    - `async void`

??? info "`cs-005` — Use pattern matching"
    **Leverage modern pattern matching features**

    **Common Violations:**

    - Type checks with 'is' followed by cast
    - Not using switch expressions
    - Verbose null checking instead of is null
    - Not using property patterns

    **Detectable Patterns:**

    - `!is `

??? info "`cs-006` — Prefer string interpolation"
    **Use $"" instead of string.Format or concatenation**

    **Common Violations:**

    - String.Format for simple formatting
    - String concatenation with +
    - Not using string interpolation

    **Detectable Patterns:**

    - `String.Format(`
    - `string + variable`

??? info "`cs-007` — Use collection expressions"
    **Use [] for collection initialization (C# 12+)**

    **Common Violations:**

    - new List<T> { } when [] works
    - Verbose array initialization
    - Not using collection expressions

    **Detectable Patterns:**

    - `new List`
    - `new []`

??? info "`cs-008` — Follow naming conventions"
    **PascalCase for public, camelCase for private**

    **Common Violations:**

    - camelCase for public members
    - snake_case in C# code
    - Hungarian notation
    - Inconsistent naming

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `public_naming` | `PascalCase` |
    | `private_naming` | `camelCase or _camelCase` |

??? info "`cs-009` — Use IDisposable and using statements"
    **Properly dispose resources with using**

    **Common Violations:**

    - Not using 'using' for IDisposable
    - Manual Dispose() calls
    - Resource leaks
    - Not implementing IDisposable when needed

    **Detectable Patterns:**

    - `Dispose()`
    - `IDisposable`

??? info "`cs-010` — Avoid magic numbers"
    **Use named constants or enums**

    **Common Violations:**

    - Hardcoded numbers in logic
    - String literals repeated
    - Not using const or readonly

    **Detectable Patterns:**

    - ` = 42`
    - ` = 100`

??? info "`cs-011` — Use LINQ appropriately"
    **Leverage LINQ for collection operations**

    **Common Violations:**

    - Manual loops instead of LINQ
    - Complex iteration logic
    - Not using Where/Select/Any
    - Inefficient LINQ chains

    **Detectable Patterns:**

    - `!Select(`

??? info "`cs-012` — Handle exceptions properly"
    **Catch specific exceptions, don't swallow errors**

    **Common Violations:**

    - Empty catch blocks
    - Catching Exception instead of specific types
    - Not using throw; for re-throwing
    - Exception as control flow

    **Detectable Patterns:**

    - `catch { }`
    - `catch (Exception)`

??? info "`cs-013` — Use records for DTOs"
    **Use record types for data transfer objects**

    **Common Violations:**

    - Classes for simple DTOs
    - Manual equality implementation
    - Not using with expressions
    - Mutable DTOs

    **Detectable Patterns:**

    - `!record `


## Detector Catalog

### Async

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CSharpAsyncAwaitDetector** | Flags synchronous blocking on tasks via ``.Result`` or ``.Wait()`` | `cs-004` |

### Clarity

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CSharpMagicNumberDetector** | Flags hard-coded numeric literals (magic numbers) in business logic | `cs-010` |

### Design

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CSharpRecordDetector** | Suggests ``record`` types for immutable data-transfer objects (DTOs) | `cs-013` |

### Error Handling

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CSharpExceptionHandlingDetector** | Flags overly broad ``catch (Exception)`` or empty ``catch`` blocks | `cs-012` |

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CSharpExpressionBodiedDetector** | Flags verbose property getters that should use expression-bodied members | `cs-002` |
| **CSharpPatternMatchingDetector** | Suggests pattern matching (``is``/``switch`` expressions) over explicit casts | `cs-005` |
| **CSharpCollectionExpressionDetector** | Flags verbose ``new List`` or ``new T[]`` where collection expressions work | `cs-007` |
| **CSharpLinqDetector** | Suggests LINQ methods (``Select``/``Where``) over manual ``foreach`` loops | `cs-011` |

### Readability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CSharpStringInterpolationDetector** | Flags ``String.Format`` usage where string interpolation is cleaner | `cs-006` |
| **CSharpVarDetector** | Flags explicit primitive type declarations where ``var`` improves readability | `cs-003` |
| **CSharpNamingConventionDetector** | Enforces .NET naming conventions for public and private members | `cs-008` |

### Resource Management

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CSharpDisposableDetector** | Detects ``IDisposable`` resources not wrapped in ``using`` statements | `cs-009` |

### Type Safety

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CSharpNullableDetector** | Detects files missing ``#nullable enable`` for nullable reference types | `cs-001` |


??? example "Principle → Detector Wiring"
    ```mermaid
    graph LR
    cs_001["cs-001<br/>Use nullable reference types"]
    cs_002["cs-002<br/>Use expression-bodied members"]
    cs_003["cs-003<br/>Prefer var for local variables"]
    cs_004["cs-004<br/>Use async/await properly"]
    cs_005["cs-005<br/>Use pattern matching"]
    cs_006["cs-006<br/>Prefer string interpolation"]
    cs_007["cs-007<br/>Use collection expressions"]
    cs_008["cs-008<br/>Follow naming conventions"]
    cs_009["cs-009<br/>Use IDisposable and using statements"]
    cs_010["cs-010<br/>Avoid magic numbers"]
    cs_011["cs-011<br/>Use LINQ appropriately"]
    cs_012["cs-012<br/>Handle exceptions properly"]
    cs_013["cs-013<br/>Use records for DTOs"]
    det_CSharpAsyncAwaitDetector["CSharpAsyncAwaitDetector"]
    cs_004 --> det_CSharpAsyncAwaitDetector
    det_CSharpCollectionExpressionDetector["CSharpCollectionExpressionDetector"]
    cs_007 --> det_CSharpCollectionExpressionDetector
    det_CSharpDisposableDetector["CSharpDisposableDetector"]
    cs_009 --> det_CSharpDisposableDetector
    det_CSharpExceptionHandlingDetector["CSharpExceptionHandlingDetector"]
    cs_012 --> det_CSharpExceptionHandlingDetector
    det_CSharpExpressionBodiedDetector["CSharpExpressionBodiedDetector"]
    cs_002 --> det_CSharpExpressionBodiedDetector
    det_CSharpLinqDetector["CSharpLinqDetector"]
    cs_011 --> det_CSharpLinqDetector
    det_CSharpMagicNumberDetector["CSharpMagicNumberDetector"]
    cs_010 --> det_CSharpMagicNumberDetector
    det_CSharpNamingConventionDetector["CSharpNamingConventionDetector"]
    cs_008 --> det_CSharpNamingConventionDetector
    det_CSharpNullableDetector["CSharpNullableDetector"]
    cs_001 --> det_CSharpNullableDetector
    det_CSharpPatternMatchingDetector["CSharpPatternMatchingDetector"]
    cs_005 --> det_CSharpPatternMatchingDetector
    det_CSharpRecordDetector["CSharpRecordDetector"]
    cs_013 --> det_CSharpRecordDetector
    det_CSharpStringInterpolationDetector["CSharpStringInterpolationDetector"]
    cs_006 --> det_CSharpStringInterpolationDetector
    det_CSharpVarDetector["CSharpVarDetector"]
    cs_003 --> det_CSharpVarDetector
    classDef principle fill:#4051b5,color:#fff,stroke:none
    classDef detector fill:#26a269,color:#fff,stroke:none
    class cs_001 principle
    class cs_002 principle
    class cs_003 principle
    class cs_004 principle
    class cs_005 principle
    class cs_006 principle
    class cs_007 principle
    class cs_008 principle
    class cs_009 principle
    class cs_010 principle
    class cs_011 principle
    class cs_012 principle
    class cs_013 principle
    class det_CSharpAsyncAwaitDetector detector
    class det_CSharpCollectionExpressionDetector detector
    class det_CSharpDisposableDetector detector
    class det_CSharpExceptionHandlingDetector detector
    class det_CSharpExpressionBodiedDetector detector
    class det_CSharpLinqDetector detector
    class det_CSharpMagicNumberDetector detector
    class det_CSharpNamingConventionDetector detector
    class det_CSharpNullableDetector detector
    class det_CSharpPatternMatchingDetector detector
    class det_CSharpRecordDetector detector
    class det_CSharpStringInterpolationDetector detector
    class det_CSharpVarDetector detector
    ```

## Configuration

```yaml
languages:
  csharp:
    enabled: true
    pipeline:
```


## See Also

- [C++](cpp.md) — Unmanaged C-family counterpart
- [TypeScript](typescript.md) — Another strongly-typed language with similar patterns
- [Configuration](../configuration.md) — Per-language pipeline overrides
