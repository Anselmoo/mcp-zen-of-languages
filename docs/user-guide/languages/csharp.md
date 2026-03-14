---
title: C#
description: "13 zen principles enforced by 13 detectors: Modern C# Best Practices (.NET 6+)."
icon: material/language-csharp
tags:
  - C#
---

# C#

Modern C# (C# 10–12) has evolved rapidly — records, pattern matching, nullable reference types, collection expressions. These **13 principles** catch codebases stuck on older patterns and guide them toward the expressive, safe idioms that the .NET team recommends.

## Optional External Tool Augmentation

!!! info "Consent-first external tooling"
    External tool execution is optional and disabled by default. Use
    `--enable-external-tools` (CLI) or `enable_external_tools=true` (MCP)
    to opt in. Missing tools should return recommendations; no automatic
    installs occur during analysis.

| Tool | Default invocation | Output |
|------|---------------------|--------|
| `dotnet` | `dotnet format --verify-no-changes` | Text / structured stderr |



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

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `cs-001` | Use nullable reference types | Type Safety | 8 | `ZEN-EXPLICIT-INTENT` |
| `cs-002` | Use expression-bodied members | Idioms | 5 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE`, `ZEN-PROPORTIONATE-COMPLEXITY` |
| `cs-003` | Prefer var for local variables | Readability | 5 | `ZEN-UNAMBIGUOUS-NAME`, `ZEN-EXPLICIT-INTENT` |
| `cs-004` | Use async/await properly | Async | 9 | `ZEN-FAIL-FAST` |
| `cs-005` | Use pattern matching | Idioms | 6 | `ZEN-RIGHT-ABSTRACTION` |
| `cs-006` | Prefer string interpolation | Readability | 6 | `ZEN-UNAMBIGUOUS-NAME`, `ZEN-PROPORTIONATE-COMPLEXITY` |
| `cs-007` | Use collection expressions | Idioms | 5 | `ZEN-RIGHT-ABSTRACTION` |
| `cs-008` | Follow naming conventions | Readability | 7 | `ZEN-UNAMBIGUOUS-NAME` |
| `cs-009` | Use IDisposable and using statements | Resource Management | 9 | `ZEN-STRICT-FENCES`, `ZEN-VISIBLE-STATE` |
| `cs-010` | Avoid magic numbers | Clarity | 6 | `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME`, `ZEN-VISIBLE-STATE` |
| `cs-011` | Use LINQ appropriately | Idioms | 7 | `ZEN-RIGHT-ABSTRACTION` |
| `cs-012` | Handle exceptions properly | Error Handling | 8 | `ZEN-FAIL-FAST` |
| `cs-013` | Use records for DTOs | Design | 6 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-PROPORTIONATE-COMPLEXITY` |

??? info "`cs-001` — Use nullable reference types"
    **Enable nullable reference types for null safety**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Not enabling nullable in project
    - Ignoring nullable warnings
    - Using ! operator excessively
    - Not annotating nullability

    **Detectable Patterns:**

    - `!#nullable enable`

??? info "`cs-002` — Use expression-bodied members"
    **Use => for simple properties and methods**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE`, `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - Full method bodies for one-line methods
    - Property getters with return statement
    - Not using lambda syntax when appropriate

    **Detectable Patterns:**

    - `!=>`

??? info "`cs-003` — Prefer var for local variables"
    **Use var when type is obvious from right side**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Explicit types when var would be clear
    - Verbose type declarations
    - Not using var with new expressions

    **Detectable Patterns:**

    - `!var `

??? info "`cs-004` — Use async/await properly"
    **Follow async best practices, avoid blocking**

    **Universal Dogmas:** `ZEN-FAIL-FAST`
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

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Type checks with 'is' followed by cast
    - Not using switch expressions
    - Verbose null checking instead of is null
    - Not using property patterns

    **Detectable Patterns:**

    - `!is `

??? info "`cs-006` — Prefer string interpolation"
    **Use $"" instead of string.Format or concatenation**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`, `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - String.Format for simple formatting
    - String concatenation with +
    - Not using string interpolation

    **Detectable Patterns:**

    - `String.Format(`
    - `string + variable`

??? info "`cs-007` — Use collection expressions"
    **Use [] for collection initialization (C# 12+)**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - new List<T> { } when [] works
    - Verbose array initialization
    - Not using collection expressions

    **Detectable Patterns:**

    - `new List`
    - `new []`

??? info "`cs-008` — Follow naming conventions"
    **PascalCase for public, camelCase for private**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
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

    **Universal Dogmas:** `ZEN-STRICT-FENCES`, `ZEN-VISIBLE-STATE`
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

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Hardcoded numbers in logic
    - String literals repeated
    - Not using const or readonly

    **Detectable Patterns:**

    - ` = 42`
    - ` = 100`

??? info "`cs-011` — Use LINQ appropriately"
    **Leverage LINQ for collection operations**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Manual loops instead of LINQ
    - Complex iteration logic
    - Not using Where/Select/Any
    - Inefficient LINQ chains

    **Detectable Patterns:**

    - `!Select(`

??? info "`cs-012` — Handle exceptions properly"
    **Catch specific exceptions, don't swallow errors**

    **Universal Dogmas:** `ZEN-FAIL-FAST`
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

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-PROPORTIONATE-COMPLEXITY`
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
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    cs_001["cs-001<br/>Use nullable reference ty..."]
    cs_002["cs-002<br/>Use expression-bodied mem..."]
    cs_003["cs-003<br/>Prefer var for local vari..."]
    cs_004["cs-004<br/>Use async/await properly"]
    cs_005["cs-005<br/>Use pattern matching"]
    cs_006["cs-006<br/>Prefer string interpolati..."]
    cs_007["cs-007<br/>Use collection expression..."]
    cs_008["cs-008<br/>Follow naming conventions"]
    cs_009["cs-009<br/>Use IDisposable and using..."]
    cs_010["cs-010<br/>Avoid magic numbers"]
    cs_011["cs-011<br/>Use LINQ appropriately"]
    cs_012["cs-012<br/>Handle exceptions properl..."]
    cs_013["cs-013<br/>Use records for DTOs"]
    det_CSharpAsyncAwaitDetector["C Sharp<br/>Async Await"]
    cs_004 --> det_CSharpAsyncAwaitDetector
    det_CSharpCollectionExpressionDetector["C Sharp<br/>Collection Expression"]
    cs_007 --> det_CSharpCollectionExpressionDetector
    det_CSharpDisposableDetector["C Sharp<br/>Disposable"]
    cs_009 --> det_CSharpDisposableDetector
    det_CSharpExceptionHandlingDetector["C Sharp<br/>Exception Handling"]
    cs_012 --> det_CSharpExceptionHandlingDetector
    det_CSharpExpressionBodiedDetector["C Sharp<br/>Expression Bodied"]
    cs_002 --> det_CSharpExpressionBodiedDetector
    det_CSharpLinqDetector["C Sharp<br/>Linq"]
    cs_011 --> det_CSharpLinqDetector
    det_CSharpMagicNumberDetector["C Sharp<br/>Magic Number"]
    cs_010 --> det_CSharpMagicNumberDetector
    det_CSharpNamingConventionDetector["C Sharp<br/>Naming Convention"]
    cs_008 --> det_CSharpNamingConventionDetector
    det_CSharpNullableDetector["C Sharp<br/>Nullable"]
    cs_001 --> det_CSharpNullableDetector
    det_CSharpPatternMatchingDetector["C Sharp<br/>Pattern Matching"]
    cs_005 --> det_CSharpPatternMatchingDetector
    det_CSharpRecordDetector["C Sharp<br/>Record"]
    cs_013 --> det_CSharpRecordDetector
    det_CSharpStringInterpolationDetector["C Sharp<br/>String Interpolation"]
    cs_006 --> det_CSharpStringInterpolationDetector
    det_CSharpVarDetector["C Sharp<br/>Var"]
    cs_003 --> det_CSharpVarDetector
    ```

??? example "Detector Class Hierarchy"
    ```mermaid
    %%{init: {"theme": "base"}}%%
    classDiagram
        direction TB
        class ViolationDetector {
            <<abstract>>
            +detect(context, config)
        }
        class det_01["C Sharp Async Await"]
        ViolationDetector <|-- det_01
        class det_02["C Sharp Collection Expression"]
        ViolationDetector <|-- det_02
        class det_03["C Sharp Disposable"]
        ViolationDetector <|-- det_03
        class det_04["C Sharp Exception Handling"]
        ViolationDetector <|-- det_04
        class det_05["C Sharp Expression Bodied"]
        ViolationDetector <|-- det_05
        class det_06["C Sharp Linq"]
        ViolationDetector <|-- det_06
        class det_07["C Sharp Magic Number"]
        ViolationDetector <|-- det_07
        class det_08["C Sharp Naming Convention"]
        ViolationDetector <|-- det_08
        class det_09["C Sharp Nullable"]
        ViolationDetector <|-- det_09
        class det_10["C Sharp Pattern Matching"]
        ViolationDetector <|-- det_10
        class det_11["C Sharp Record"]
        ViolationDetector <|-- det_11
        class det_12["C Sharp String Interpolation"]
        ViolationDetector <|-- det_12
        class det_13["C Sharp Var"]
        ViolationDetector <|-- det_13
    ```

??? example "Analysis Pipeline"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 50, "rankSpacing": 70}}}%%
    flowchart TD
    Source(["Source Code"]) --> Parse["Parse & Tokenize"]
    Parse --> Metrics["Compute Metrics"]
    Metrics --> Pipeline{"13 Detectors"}
    Pipeline --> Collect["Aggregate Violations"]
    Collect --> Result(["AnalysisResult<br/>13 principles"])
    ```

??? example "Analysis States"
    ```mermaid
    %%{init: {"theme": "base"}}%%
    stateDiagram-v2
        [*] --> Ready
        Ready --> Parsing : analyze(code)
        Parsing --> Computing : AST ready
        Computing --> Detecting : metrics ready
        Detecting --> Reporting : 13 detectors run
        Reporting --> [*] : AnalysisResult
        Parsing --> Reporting : parse error (best-effort)
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
