---
title: Go
description: "20 zen principles enforced by 21 detectors: Simplicity, Clarity, and Pragmatism."
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

20 principles across 12 categories, drawn from [Effective Go & The Zen of Go](https://the-zen-of-go.netlify.app/).

<div class="grid" markdown>

:material-tag-outline: **Architecture** · 1 principle
:material-tag-outline: **Complexity** · 1 principle
:material-tag-outline: **Concurrency** · 3 principles
:material-tag-outline: **Correctness** · 1 principle
:material-tag-outline: **Design** · 5 principles
:material-tag-outline: **Error Handling** · 1 principle
:material-tag-outline: **Idioms** · 1 principle
:material-tag-outline: **Initialization** · 1 principle
:material-tag-outline: **Organization** · 2 principles
:material-tag-outline: **Performance** · 1 principle
:material-tag-outline: **Readability** · 2 principles
:material-tag-outline: **Structure** · 1 principle

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `go-001` | Errors are values | Error Handling | 9 | `ZEN-FAIL-FAST`, `ZEN-EXPLICIT-INTENT` |
| `go-002` | Accept interfaces, return structs | Design | 7 | `ZEN-RIGHT-ABSTRACTION` |
| `go-003` | Make the zero value useful | Design | 6 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT` |
| `go-004` | Use short variable names | Readability | 5 | `ZEN-UNAMBIGUOUS-NAME` |
| `go-005` | Don't use pointer to interface | Design | 8 | `ZEN-RIGHT-ABSTRACTION` |
| `go-006` | Avoid goroutine leaks | Concurrency | 9 | `ZEN-VISIBLE-STATE` |
| `go-007` | Use defer for cleanup | Idioms | 7 | `ZEN-RIGHT-ABSTRACTION` |
| `go-008` | Package names are singular | Organization | 5 | `ZEN-STRICT-FENCES`, `ZEN-UNAMBIGUOUS-NAME` |
| `go-009` | Avoid package-level state | Architecture | 7 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE` |
| `go-010` | Keep interfaces small | Design | 7 | `ZEN-RIGHT-ABSTRACTION` |
| `go-011` | Use context for cancellation | Concurrency | 8 | `ZEN-VISIBLE-STATE` |
| `go-012` | Avoid init() when possible | Initialization | 6 | `ZEN-EXPLICIT-INTENT` |
| `go-013` | Organize by responsibility | Organization | 6 | `ZEN-STRICT-FENCES`, `ZEN-RETURN-EARLY`, `ZEN-UNAMBIGUOUS-NAME` |
| `go-014` | Embed for composition, not inheritance | Structure | 7 | `ZEN-RETURN-EARLY`, `ZEN-UNAMBIGUOUS-NAME` |
| `go-015` | Communicate by sharing memory through channels | Concurrency | 8 | `ZEN-VISIBLE-STATE` |
| `go-016` | Avoid unnecessary complexity | Complexity | 7 | `ZEN-PROPORTIONATE-COMPLEXITY`, `ZEN-RETURN-EARLY` |
| `go-017` | Handle every error path | Correctness | 9 | `ZEN-EXPLICIT-INTENT`, `ZEN-FAIL-FAST` |
| `go-018` | Avoid premature optimization | Performance | 5 | `ZEN-PROPORTIONATE-COMPLEXITY` |
| `go-019` | Design for testability | Design | 7 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE` |
| `go-020` | Write self-documenting code | Readability | 5 | `ZEN-UNAMBIGUOUS-NAME`, `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE` |

??? info "`go-001` — Errors are values"
    **Handle errors explicitly, don't panic**

    **Universal Dogmas:** `ZEN-FAIL-FAST`, `ZEN-EXPLICIT-INTENT`
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

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Returning interfaces from functions
    - Accepting concrete types when interface would work
    - Premature interface abstraction

    **Detectable Patterns:**

    - `interface{`

??? info "`go-003` — Make the zero value useful"
    **Structs should be usable without explicit initialization**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Structs requiring explicit initialization
    - Mandatory constructor functions
    - Unusable zero values

    **Detectable Patterns:**

    - `func New`

??? info "`go-004` — Use short variable names"
    **Prefer short, contextual names in limited scopes**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Long variable names in small scopes
    - unnecessarilyLongVariableNames
    - Unclear abbreviations in large scopes

??? info "`go-005` — Don't use pointer to interface"
    **Interfaces are already pointers, don't add ***

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - *Interface type parameters
    - Pointer to interface return types

    **Detectable Patterns:**

    - `*io.Reader`
    - `*SomeInterface`

??? info "`go-006` — Avoid goroutine leaks"
    **Always ensure goroutines can terminate**

    **Universal Dogmas:** `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Goroutines without cancellation
    - Channels without close
    - Infinite loops in goroutines
    - No context for cancellation

    **Detectable Patterns:**

    - `go func`

??? info "`go-007` — Use defer for cleanup"
    **Defer resource cleanup immediately after acquisition**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Manual cleanup scattered in code
    - Not using defer for file.Close()
    - Not deferring mutex.Unlock()

??? info "`go-008` — Package names are singular"
    **Package names should be lowercase, singular nouns**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`, `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Plural package names (utils → util)
    - CamelCase package names
    - Underscores in package names

    **Detectable Patterns:**

    - `package utils`
    - `package helpers`

??? info "`go-009` — Avoid package-level state"
    **Minimize global variables and package-level mutable state**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Mutable package-level variables
    - Package init() with side effects
    - Global singletons

    **Detectable Patterns:**

    - `var `

??? info "`go-010` — Keep interfaces small"
    **Prefer many small interfaces over large ones**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
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

    **Universal Dogmas:** `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Long-running functions without context
    - HTTP handlers without request context
    - Not propagating context

??? info "`go-012` — Avoid init() when possible"
    **Prefer explicit initialization over init()**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Complex logic in init()
    - Multiple init() functions
    - Side effects in init()

    **Detectable Patterns:**

    - `func init(`

??? info "`go-013` — Organize by responsibility"
    **Group code by domain responsibility, not by technical layer**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`, `ZEN-RETURN-EARLY`, `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Organizing packages by type (models/, controllers/)
    - Deeply nested package hierarchies
    - Circular package dependencies
    - Package names reflecting technical role instead of domain

    **Detectable Patterns:**

    - `package models`
    - `package controllers`

??? info "`go-014` — Embed for composition, not inheritance"
    **Use struct embedding for composing behaviors, not faking OOP inheritance**

    **Universal Dogmas:** `ZEN-RETURN-EARLY`, `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Deep embedding chains exceeding two levels
    - Embedding structs solely to access their fields
    - Name collisions from overlapping embedded methods

    **Detectable Patterns:**

    - `type Foo struct { Bar`

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_embedding_depth` | `2` |

??? info "`go-015` — Communicate by sharing memory through channels"
    **Prefer channels over shared-memory synchronization primitives**

    **Universal Dogmas:** `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Using sync.Mutex where a channel would be clearer
    - Shared mutable state accessed by multiple goroutines
    - Missing synchronization around concurrent map access

    **Detectable Patterns:**

    - `sync.Mutex`
    - `sync.RWMutex`

??? info "`go-016` — Avoid unnecessary complexity"
    **Prefer straightforward solutions; complexity must be justified**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`, `ZEN-RETURN-EARLY`
    **Common Violations:**

    - Deeply nested control flow exceeding three levels
    - Functions longer than 50 lines
    - Cyclomatic complexity above 10 per function

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_nesting_depth` | `3` |
    | `max_function_lines` | `50` |

??? info "`go-017` — Handle every error path"
    **Ensure all error branches are explicitly handled, not just the happy path**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-FAIL-FAST`
    **Common Violations:**

    - Returning early without wrapping or annotating the error
    - Silently swallowing errors inside deferred calls
    - Using log.Fatal in library code instead of returning an error

??? info "`go-018` — Avoid premature optimization"
    **Write clear code first; optimize only after profiling proves a bottleneck**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - Unsafe pointer tricks without benchmark justification
    - Manual memory pooling where sync.Pool is not warranted
    - Replacing readable code with micro-optimizations lacking profiling data

??? info "`go-019` — Design for testability"
    **Structure code so that dependencies can be replaced in tests**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Hard-coded external service calls with no interface seam
    - Global state that prevents parallel test execution
    - Unexported helpers that duplicate test setup across packages

??? info "`go-020` — Write self-documenting code"
    **Let clear naming and structure replace the need for most comments**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`, `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Comments that restate the code instead of explaining intent
    - Exported symbols missing GoDoc-style comments
    - Magic numbers without named constants


## Detector Catalog

### Architecture

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoPackageStateDetector** | Flags mutable package-level variables that introduce hidden global state | `go-009` |

### Complexity

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoSimplicityDetector** | Flags empty interface usage that weakens type safety | `go-016` |

### Concurrency

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoContextUsageDetector** | Flags code that lacks ``context.Context`` for cancellation and deadline propagation | `go-011` |
| **GoGoroutineLeakDetector** | Flags goroutines launched without cancellation support and unclosed channels | `go-006` |
| **GoConcurrencyCallerDetector** | Flags functions that spawn goroutines internally | `go-015` |

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoEarlyReturnDetector** | Flags ``err == nil`` guards that nest the happy path instead of returning early | `go-017` |

### Design

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoInterfaceSizeDetector** | Detects oversized interfaces that violate Go's preference for small, composable contracts | `go-010` |
| **GoInterfaceReturnDetector** | Flags functions that return interface types instead of concrete structs | `go-002` |
| **GoZeroValueDetector** | Flags ``New*`` constructor functions where making the zero value usable would be simpler | `go-003` |
| **GoInterfacePointerDetector** | Detects pointers to interfaces, which are almost always a mistake in Go | `go-005` |
| **GoTestPresenceDetector** | Flags exported functions without accompanying test functions | `go-019` |

### Error Handling

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoErrorHandlingDetector** | Flags ignored errors, unchecked ``err`` variables, and ``panic()`` calls in Go code | `go-001` |

### General

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoModerationDetector** | Flags excessive goroutine spawning within a single file |  |

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
| **GoOrganizeResponsibilityDetector** | Detects catch-all package names like util, common, or helper | `go-013` |

### Performance

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoBenchmarkDetector** | Flags optimisation primitives used without benchmark proof | `go-018` |

### Readability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoNamingConventionDetector** | Flags overly long variable names that violate Go's brevity conventions | `go-004` |
| **GoMaintainabilityDetector** | Flags exported functions missing godoc comments | `go-020` |

### Structure

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GoEmbeddingDepthDetector** | Flags structs with too many anonymously embedded types | `go-014` |


??? example "Principle → Detector Wiring"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    go_001["go-001<br/>Errors are values"]
    go_002["go-002<br/>Accept interfaces, return..."]
    go_003["go-003<br/>Make the zero value usefu..."]
    go_004["go-004<br/>Use short variable names"]
    go_005["go-005<br/>Don&#x27;t use pointer to inte..."]
    go_006["go-006<br/>Avoid goroutine leaks"]
    go_007["go-007<br/>Use defer for cleanup"]
    go_008["go-008<br/>Package names are singula..."]
    go_009["go-009<br/>Avoid package-level state"]
    go_010["go-010<br/>Keep interfaces small"]
    go_011["go-011<br/>Use context for cancellat..."]
    go_012["go-012<br/>Avoid init() when possibl..."]
    go_013["go-013<br/>Organize by responsibilit..."]
    go_014["go-014<br/>Embed for composition, no..."]
    go_015["go-015<br/>Communicate by sharing me..."]
    go_016["go-016<br/>Avoid unnecessary complex..."]
    go_017["go-017<br/>Handle every error path"]
    go_018["go-018<br/>Avoid premature optimizat..."]
    go_019["go-019<br/>Design for testability"]
    go_020["go-020<br/>Write self-documenting co..."]
    det_GoBenchmarkDetector["Go Benchmark"]
    go_018 --> det_GoBenchmarkDetector
    det_GoConcurrencyCallerDetector["Go Concurrency<br/>Caller"]
    go_015 --> det_GoConcurrencyCallerDetector
    det_GoContextUsageDetector["Go Context<br/>Usage"]
    go_011 --> det_GoContextUsageDetector
    det_GoDeferUsageDetector["Go Defer<br/>Usage"]
    go_007 --> det_GoDeferUsageDetector
    det_GoEarlyReturnDetector["Go Early<br/>Return"]
    go_017 --> det_GoEarlyReturnDetector
    det_GoEmbeddingDepthDetector["Go Embedding<br/>Depth"]
    go_014 --> det_GoEmbeddingDepthDetector
    det_GoErrorHandlingDetector["Go Error<br/>Handling"]
    go_001 --> det_GoErrorHandlingDetector
    det_GoGoroutineLeakDetector["Go Goroutine<br/>Leak"]
    go_006 --> det_GoGoroutineLeakDetector
    det_GoInitUsageDetector["Go Init<br/>Usage"]
    go_012 --> det_GoInitUsageDetector
    det_GoInterfacePointerDetector["Go Interface<br/>Pointer"]
    go_005 --> det_GoInterfacePointerDetector
    det_GoInterfaceReturnDetector["Go Interface<br/>Return"]
    go_002 --> det_GoInterfaceReturnDetector
    det_GoInterfaceSizeDetector["Go Interface<br/>Size"]
    go_010 --> det_GoInterfaceSizeDetector
    det_GoMaintainabilityDetector["Go Maintainability"]
    go_020 --> det_GoMaintainabilityDetector
    det_GoModerationDetector["Go Moderation"]
    det_GoNamingConventionDetector["Go Naming<br/>Convention"]
    go_004 --> det_GoNamingConventionDetector
    det_GoOrganizeResponsibilityDetector["Go Organize<br/>Responsibility"]
    go_013 --> det_GoOrganizeResponsibilityDetector
    det_GoPackageNamingDetector["Go Package<br/>Naming"]
    go_008 --> det_GoPackageNamingDetector
    det_GoPackageStateDetector["Go Package<br/>State"]
    go_009 --> det_GoPackageStateDetector
    det_GoSimplicityDetector["Go Simplicity"]
    go_016 --> det_GoSimplicityDetector
    det_GoTestPresenceDetector["Go Test<br/>Presence"]
    go_019 --> det_GoTestPresenceDetector
    det_GoZeroValueDetector["Go Zero<br/>Value"]
    go_003 --> det_GoZeroValueDetector
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
        class det_01["Go Benchmark"]
        ViolationDetector <|-- det_01
        class det_02["Go Concurrency Caller"]
        ViolationDetector <|-- det_02
        class det_03["Go Context Usage"]
        ViolationDetector <|-- det_03
        class det_04["Go Defer Usage"]
        ViolationDetector <|-- det_04
        class det_05["Go Early Return"]
        ViolationDetector <|-- det_05
        class det_06["Go Embedding Depth"]
        ViolationDetector <|-- det_06
        class det_07["Go Error Handling"]
        ViolationDetector <|-- det_07
        class det_08["Go Goroutine Leak"]
        ViolationDetector <|-- det_08
        class det_09["Go Init Usage"]
        ViolationDetector <|-- det_09
        class det_10["Go Interface Pointer"]
        ViolationDetector <|-- det_10
        class det_11["Go Interface Return"]
        ViolationDetector <|-- det_11
        class det_12["Go Interface Size"]
        ViolationDetector <|-- det_12
        class det_13["Go Maintainability"]
        ViolationDetector <|-- det_13
        class det_14["Go Moderation"]
        ViolationDetector <|-- det_14
        class det_15["Go Naming Convention"]
        ViolationDetector <|-- det_15
        class det_16["Go Organize Responsibility"]
        ViolationDetector <|-- det_16
        class det_17["Go Package Naming"]
        ViolationDetector <|-- det_17
        class det_18["Go Package State"]
        ViolationDetector <|-- det_18
        class det_19["Go Simplicity"]
        ViolationDetector <|-- det_19
        class det_20["Go Test Presence"]
        ViolationDetector <|-- det_20
        class det_21["Go Zero Value"]
        ViolationDetector <|-- det_21
    ```

??? example "Analysis Pipeline"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 50, "rankSpacing": 70}}}%%
    flowchart TD
    Source(["Source Code"]) --> Parse["Parse & Tokenize"]
    Parse --> Metrics["Compute Metrics"]
    Metrics --> Pipeline{"21 Detectors"}
    Pipeline --> Collect["Aggregate Violations"]
    Collect --> Result(["AnalysisResult<br/>20 principles"])
    ```

??? example "Analysis States"
    ```mermaid
    %%{init: {"theme": "base"}}%%
    stateDiagram-v2
        [*] --> Ready
        Ready --> Parsing : analyze(code)
        Parsing --> Computing : AST ready
        Computing --> Detecting : metrics ready
        Detecting --> Reporting : 21 detectors run
        Reporting --> [*] : AnalysisResult
        Parsing --> Reporting : parse error (best-effort)
    ```

## Configuration

```yaml
languages:
  go:
    enabled: true
    pipeline:
      - type: go_error_handling
        max_ignored_errors: 0
      - type: go_interface_size
        max_interface_methods: 3
      - type: go_context_usage
        require_context: True
      - type: go_defer_usage
        detect_defer_in_loop: True
        detect_missing_defer: True
      - type: go_naming_convention
        detect_long_names: True
      - type: go_embedding_depth
        max_embedding_depth: 2
      - type: go_simplicity
        max_nesting_depth: 3
        max_function_lines: 50
      - type: go_moderation
        max_goroutine_spawns: 5
```


## See Also

- [Rust](rust.md) — Complementary systems language with ownership model
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
