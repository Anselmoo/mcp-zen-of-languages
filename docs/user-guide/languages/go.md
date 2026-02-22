---
title: Go
description: "12 zen principles enforced by 12 detectors: Simplicity, Clarity, and Pragmatism."
icon: material/language-go
tags:
  - Go
---

# Go

Go's philosophy is radical simplicity: small interfaces, explicit errors, flat hierarchies. These **12 principles** come from [Effective Go](https://go.dev/doc/effective_go), the [Go Proverbs](https://go-proverbs.github.io/), and the collective wisdom of the Go community. They catch the patterns where Go's simplicity gets undermined.

## Optional External Tool Augmentation

!!! info "Consent-first external tooling"
    External tool execution is optional and disabled by default. Use
    `--enable-external-tools` (CLI) or `enable_external_tools=true` (MCP)
    to opt in. Missing tools should return recommendations; no automatic
    installs occur during analysis.

| Tool | Default invocation | Output |
|------|---------------------|--------|
| `go` | `go vet ./...` | Text / structured stderr |



## Zen Principles

12 principles across 8 categories, drawn from [Effective Go](https://go.dev/doc/effective_go).

<div class="grid" markdown>

:material-tag-outline: **Architecture** · 1 principle
:material-tag-outline: **Concurrency** · 2 principles
:material-tag-outline: **Design** · 4 principles
:material-tag-outline: **Error Handling** · 1 principle
:material-tag-outline: **Idioms** · 1 principle
:material-tag-outline: **Initialization** · 1 principle
:material-tag-outline: **Organization** · 1 principle
:material-tag-outline: **Readability** · 1 principle

</div>

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `go-001` | Errors are values | Error Handling | 9 |
| `go-002` | Accept interfaces, return structs | Design | 7 |
| `go-003` | Make the zero value useful | Design | 6 |
| `go-004` | Use short variable names | Readability | 5 |
| `go-005` | Don't use pointer to interface | Design | 8 |
| `go-006` | Avoid goroutine leaks | Concurrency | 9 |
| `go-007` | Use defer for cleanup | Idioms | 7 |
| `go-008` | Package names are singular | Organization | 5 |
| `go-009` | Avoid package-level state | Architecture | 7 |
| `go-010` | Keep interfaces small | Design | 7 |
| `go-011` | Use context for cancellation | Concurrency | 8 |
| `go-012` | Avoid init() when possible | Initialization | 6 |

??? info "`go-001` — Errors are values"
    **Handle errors explicitly, don't panic**

    **Common Violations:**

    - Ignoring error returns
    - _ assignment for errors
    - Excessive panic usage
    - Not checking error != nil

    **Detectable Patterns:**

    - `_, err := without checking`
    - `panic() in libraries`

??? info "`go-002` — Accept interfaces, return structs"
    **Function parameters should be interfaces, returns concrete types**

    **Common Violations:**

    - Returning interfaces from functions
    - Accepting concrete types when interface would work
    - Premature interface abstraction

    **Detectable Patterns:**

    - `interface{`

??? info "`go-003` — Make the zero value useful"
    **Structs should be usable without explicit initialization**

    **Common Violations:**

    - Structs requiring explicit initialization
    - Mandatory constructor functions
    - Unusable zero values

    **Detectable Patterns:**

    - `func New`

??? info "`go-004` — Use short variable names"
    **Prefer short, contextual names in limited scopes**

    **Common Violations:**

    - Long variable names in small scopes
    - unnecessarilyLongVariableNames
    - Unclear abbreviations in large scopes

??? info "`go-005` — Don't use pointer to interface"
    **Interfaces are already pointers, don't add ***

    **Common Violations:**

    - *Interface type parameters
    - Pointer to interface return types

    **Detectable Patterns:**

    - `*io.Reader`
    - `*SomeInterface`

??? info "`go-006` — Avoid goroutine leaks"
    **Always ensure goroutines can terminate**

    **Common Violations:**

    - Goroutines without cancellation
    - Channels without close
    - Infinite loops in goroutines
    - No context for cancellation

    **Detectable Patterns:**

    - `go func`

??? info "`go-007` — Use defer for cleanup"
    **Defer resource cleanup immediately after acquisition**

    **Common Violations:**

    - Manual cleanup scattered in code
    - Not using defer for file.Close()
    - Not deferring mutex.Unlock()

??? info "`go-008` — Package names are singular"
    **Package names should be lowercase, singular nouns**

    **Common Violations:**

    - Plural package names (utils → util)
    - CamelCase package names
    - Underscores in package names

    **Detectable Patterns:**

    - `package utils`
    - `package helpers`

??? info "`go-009` — Avoid package-level state"
    **Minimize global variables and package-level mutable state**

    **Common Violations:**

    - Mutable package-level variables
    - Package init() with side effects
    - Global singletons

    **Detectable Patterns:**

    - `var `

??? info "`go-010` — Keep interfaces small"
    **Prefer many small interfaces over large ones**

    **Common Violations:**

    - Interfaces with > 3 methods
    - God interfaces
    - Interface segregation violations

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_interface_methods` | `3` |

??? info "`go-011` — Use context for cancellation"
    **Pass context.Context for cancellation and deadlines**

    **Common Violations:**

    - Long-running functions without context
    - HTTP handlers without request context
    - Not propagating context

??? info "`go-012` — Avoid init() when possible"
    **Prefer explicit initialization over init()**

    **Common Violations:**

    - Complex logic in init()
    - Multiple init() functions
    - Side effects in init()

    **Detectable Patterns:**

    - `func init(`


## Detector Catalog

### Architecture

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoPackageStateDetector** | Flags mutable package-level variables that introduce hidden global state | `go-009` |

### Concurrency

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoContextUsageDetector** | Flags code that lacks ``context.Context`` for cancellation and deadline propagation | `go-011` |
| **GoGoroutineLeakDetector** | Flags goroutines launched without cancellation support and unclosed channels | `go-006` |

### Design

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoInterfaceSizeDetector** | Detects oversized interfaces that violate Go's preference for small, composable contracts | `go-010` |
| **GoInterfaceReturnDetector** | Flags functions that return interface types instead of concrete structs | `go-002` |
| **GoZeroValueDetector** | Flags ``New*`` constructor functions where making the zero value usable would be simpler | `go-003` |
| **GoInterfacePointerDetector** | Detects pointers to interfaces, which are almost always a mistake in Go | `go-005` |

### Error Handling

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoErrorHandlingDetector** | Flags ignored errors, unchecked ``err`` variables, and ``panic()`` calls in Go code | `go-001` |

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoDeferUsageDetector** | Detects ``defer`` misuse inside loops and missing ``defer`` for resource cleanup | `go-007` |

### Initialization

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoInitUsageDetector** | Flags ``func init()`` usage that hides initialization logic from callers | `go-012` |

### Organization

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoPackageNamingDetector** | Flags package names that violate Go's singular, lowercase naming convention | `go-008` |

### Readability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoNamingConventionDetector** | Flags overly long variable names that violate Go's brevity conventions | `go-004` |


??? example "Principle → Detector Wiring"
    ```mermaid
    graph LR
    go_001["go-001<br/>Errors are values"]
    go_002["go-002<br/>Accept interfaces, return structs"]
    go_003["go-003<br/>Make the zero value useful"]
    go_004["go-004<br/>Use short variable names"]
    go_005["go-005<br/>Don't use pointer to interface"]
    go_006["go-006<br/>Avoid goroutine leaks"]
    go_007["go-007<br/>Use defer for cleanup"]
    go_008["go-008<br/>Package names are singular"]
    go_009["go-009<br/>Avoid package-level state"]
    go_010["go-010<br/>Keep interfaces small"]
    go_011["go-011<br/>Use context for cancellation"]
    go_012["go-012<br/>Avoid init() when possible"]
    det_GoContextUsageDetector["GoContextUsageDetector"]
    go_011 --> det_GoContextUsageDetector
    det_GoDeferUsageDetector["GoDeferUsageDetector"]
    go_007 --> det_GoDeferUsageDetector
    det_GoErrorHandlingDetector["GoErrorHandlingDetector"]
    go_001 --> det_GoErrorHandlingDetector
    det_GoGoroutineLeakDetector["GoGoroutineLeakDetector"]
    go_006 --> det_GoGoroutineLeakDetector
    det_GoInitUsageDetector["GoInitUsageDetector"]
    go_012 --> det_GoInitUsageDetector
    det_GoInterfacePointerDetector["GoInterfacePointerDetector"]
    go_005 --> det_GoInterfacePointerDetector
    det_GoInterfaceReturnDetector["GoInterfaceReturnDetector"]
    go_002 --> det_GoInterfaceReturnDetector
    det_GoInterfaceSizeDetector["GoInterfaceSizeDetector"]
    go_010 --> det_GoInterfaceSizeDetector
    det_GoNamingConventionDetector["GoNamingConventionDetector"]
    go_004 --> det_GoNamingConventionDetector
    det_GoPackageNamingDetector["GoPackageNamingDetector"]
    go_008 --> det_GoPackageNamingDetector
    det_GoPackageStateDetector["GoPackageStateDetector"]
    go_009 --> det_GoPackageStateDetector
    det_GoZeroValueDetector["GoZeroValueDetector"]
    go_003 --> det_GoZeroValueDetector
    classDef principle fill:#4051b5,color:#fff,stroke:none
    classDef detector fill:#26a269,color:#fff,stroke:none
    class go_001 principle
    class go_002 principle
    class go_003 principle
    class go_004 principle
    class go_005 principle
    class go_006 principle
    class go_007 principle
    class go_008 principle
    class go_009 principle
    class go_010 principle
    class go_011 principle
    class go_012 principle
    class det_GoContextUsageDetector detector
    class det_GoDeferUsageDetector detector
    class det_GoErrorHandlingDetector detector
    class det_GoGoroutineLeakDetector detector
    class det_GoInitUsageDetector detector
    class det_GoInterfacePointerDetector detector
    class det_GoInterfaceReturnDetector detector
    class det_GoInterfaceSizeDetector detector
    class det_GoNamingConventionDetector detector
    class det_GoPackageNamingDetector detector
    class det_GoPackageStateDetector detector
    class det_GoZeroValueDetector detector
    ```

## Configuration

```yaml
languages:
  go:
    enabled: true
    pipeline:
      - type: go-error-handling
        max_ignored_errors: 0
      - type: go-interface-size
        max_interface_methods: 3
      - type: go-context-usage
        require_context: True
      - type: go-defer-usage
        detect_defer_in_loop: True
        detect_missing_defer: True
      - type: go-naming-convention
        detect_long_names: True
```


## See Also

- [Rust](rust.md) — Complementary systems language with ownership model
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
