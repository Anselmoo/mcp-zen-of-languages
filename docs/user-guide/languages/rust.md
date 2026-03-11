---
title: Rust
description: "17 zen principles enforced by 23 detectors: Safety, Concurrency, and Zero-Cost Abstractions."
icon: material/language-rust
tags:
  - Rust
---

# Rust

Rust's zen is the compiler's bargain: fight with the borrow checker at compile time, and your code won't segfault at runtime. These **12 principles** encode the idiomatic patterns that experienced Rustaceans follow — patterns that go beyond "it compiles" into "it's well-designed."

## Optional External Tool Augmentation

!!! info "Consent-first external tooling"
    External tool execution is optional and disabled by default. Use
    `--enable-external-tools` (CLI) or `enable_external_tools=true` (MCP)
    to opt in. Missing tools should return recommendations; no automatic
    installs occur during analysis.

| Tool | Default invocation | Output |
|------|---------------------|--------|
| `cargo` | `cargo clippy --message-format=json` | JSON |



## Zen Principles

17 principles across 11 categories, drawn from [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/).

<div class="grid" markdown>

:material-tag-outline: **Concurrency** · 1 principle
:material-tag-outline: **Correctness** · 1 principle
:material-tag-outline: **Debugging** · 1 principle
:material-tag-outline: **Design** · 3 principles
:material-tag-outline: **Error Handling** · 2 principles
:material-tag-outline: **Idioms** · 4 principles
:material-tag-outline: **Ownership** · 1 principle
:material-tag-outline: **Performance** · 1 principle
:material-tag-outline: **Readability** · 1 principle
:material-tag-outline: **Safety** · 1 principle
:material-tag-outline: **Type Safety** · 1 principle

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `rust-001` | Avoid unwrap() and expect() in production code | Error Handling | 9 | `ZEN-FAIL-FAST` |
| `rust-002` | Use the type system to prevent bugs | Type Safety | 8 | `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE` |
| `rust-003` | Prefer iterators over loops | Idioms | 7 | `ZEN-RIGHT-ABSTRACTION` |
| `rust-004` | Clone sparingly | Performance | 7 | `ZEN-PROPORTIONATE-COMPLEXITY` |
| `rust-005` | Use #[must_use] for important return types | Correctness | 6 | `ZEN-EXPLICIT-INTENT` |
| `rust-006` | Implement Debug for all public types | Debugging | 6 | `ZEN-EXPLICIT-INTENT` |
| `rust-007` | Use newtype pattern for type safety | Design | 7 | `ZEN-RIGHT-ABSTRACTION` |
| `rust-008` | Avoid unsafe unless necessary | Safety | 9 | `ZEN-FAIL-FAST` |
| `rust-009` | Use std traits appropriately | Idioms | 7 | `ZEN-RIGHT-ABSTRACTION` |
| `rust-010` | Prefer enums over booleans for state | Design | 7 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE` |
| `rust-011` | Use lifetimes judiciously | Ownership | 6 | `ZEN-VISIBLE-STATE`, `ZEN-EXPLICIT-INTENT` |
| `rust-012` | Avoid Rc<RefCell<T>> unless necessary | Design | 7 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE` |
| `rust-013` | Send + Sync should be implemented when types allow | Concurrency | 7 | `ZEN-VISIBLE-STATE` |
| `rust-014` | Error types should implement standard error traits | Error Handling | 8 | `ZEN-FAIL-FAST` |
| `rust-015` | Follow Rust naming conventions (RFC 430) | Readability | 6 | `ZEN-UNAMBIGUOUS-NAME` |
| `rust-016` | Implement Default when there is an obvious default value | Idioms | 5 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE` |
| `rust-017` | Use From/Into for type conversions | Idioms | 6 | `ZEN-RIGHT-ABSTRACTION` |

??? info "`rust-001` — Avoid unwrap() and expect() in production code"
    **Use proper error handling with Result and Option**

    **Universal Dogmas:** `ZEN-FAIL-FAST`
    **Common Violations:**

    - unwrap() in library code
    - expect() without clear justification
    - Ignoring Result types
    - Excessive panic usage

    **Detectable Patterns:**

    - `.unwrap()`
    - `.expect(`

    !!! tip "Recommended Fix"
        match, if let, ?, or unwrap_or

??? info "`rust-002` — Use the type system to prevent bugs"
    **Leverage Rust's type system for compile-time guarantees**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Using primitive types when newtype would be safer
    - Stringly-typed APIs
    - Not using enums for state machines
    - Overuse of Option<T> instead of proper types

    **Detectable Patterns:**

    - `String`
    - `i32`
    - `u32`

??? info "`rust-003` — Prefer iterators over loops"
    **Use iterator methods for functional, zero-cost abstractions**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Manual for loops over collections
    - Index-based iteration
    - Mutable accumulator patterns
    - Not using map/filter/fold

    **Detectable Patterns:**

    - `for i in 0..vec.len()`
    - `manual mutation in loops`

??? info "`rust-004` — Clone sparingly"
    **Avoid unnecessary cloning, prefer borrowing**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - Cloning when references work
    - Excessive .clone() calls
    - Not using Cow<T>
    - Cloning in hot paths

??? info "`rust-005` — Use #[must_use] for important return types"
    **Mark Result and critical types as must_use**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Result types without must_use
    - Ignoring function return values
    - Not annotating important builders

    **Detectable Patterns:**

    - `!#[must_use]`

??? info "`rust-006` — Implement Debug for all public types"
    **Derive or implement Debug for better debugging**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Public structs without Debug
    - Complex types without Debug
    - Not using #[derive(Debug)]

    **Detectable Patterns:**

    - `!#[derive(Debug)]`

??? info "`rust-007` — Use newtype pattern for type safety"
    **Wrap primitives in newtypes for semantic clarity**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Using raw integers for IDs
    - String for typed values
    - Not distinguishing similar types (UserId vs ProductId)

    **Detectable Patterns:**

    - `!struct `

??? info "`rust-008` — Avoid unsafe unless necessary"
    **Minimize unsafe code and document invariants**

    **Universal Dogmas:** `ZEN-FAIL-FAST`
    **Common Violations:**

    - Unnecessary unsafe blocks
    - Unsafe without safety comments
    - Large unsafe blocks
    - Unsafe in public APIs without documentation

    **Detectable Patterns:**

    - `unsafe {`
    - `unsafe fn`

??? info "`rust-009` — Use std traits appropriately"
    **Implement standard traits (Display, From, Into, etc.)**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Custom conversion instead of From/Into
    - String formatting without Display
    - Not implementing Default when appropriate
    - Manual iteration instead of IntoIterator

    **Detectable Patterns:**

    - `!impl From`
    - `!impl Default`

??? info "`rust-010` — Prefer enums over booleans for state"
    **Use enums to make state explicit**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Boolean flags for state
    - Multiple related booleans
    - State represented by Option<()>

    **Detectable Patterns:**

    - `bool`

??? info "`rust-011` — Use lifetimes judiciously"
    **Let the compiler infer when possible, be explicit when needed**

    **Universal Dogmas:** `ZEN-VISIBLE-STATE`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Unnecessary lifetime annotations
    - Overly complex lifetime bounds
    - Fighting the borrow checker instead of redesigning

    **Detectable Patterns:**

    - `<'a>`
    - `<'static>`

??? info "`rust-012` — Avoid Rc<RefCell<T>> unless necessary"
    **Prefer ownership or references over runtime borrowing**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Overuse of Rc<RefCell<T>>
    - Interior mutability when not needed
    - Arc<Mutex<T>> in single-threaded code

    **Detectable Patterns:**

    - `Rc<RefCell`
    - `Arc<Mutex`

??? info "`rust-013` — Send + Sync should be implemented when types allow"
    **Public types that can safely be Send/Sync should be, and unsafe impls need SAFETY comments**

    **Universal Dogmas:** `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - unsafe impl Send without SAFETY comment
    - unsafe impl Sync without SAFETY comment
    - Public types missing Send/Sync bounds

    **Detectable Patterns:**

    - `unsafe impl Send`
    - `unsafe impl Sync`

??? info "`rust-014` — Error types should implement standard error traits"
    **Custom error types must implement std::error::Error, Display, and Debug**

    **Universal Dogmas:** `ZEN-FAIL-FAST`
    **Common Violations:**

    - Error type without std::error::Error impl
    - Missing Display for error types
    - Error types without Debug

    **Detectable Patterns:**

    - `struct Error without impl Error`
    - `enum Error without Display`

    !!! tip "Recommended Fix"
        Use thiserror derive macros or manual Display + Error impls

??? info "`rust-015` — Follow Rust naming conventions (RFC 430)"
    **Use snake_case for functions, CamelCase for types, SCREAMING_SNAKE_CASE for constants**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - camelCase function names
    - snake_case type names
    - Lowercase constants
    - Non-standard lifetime names

    **Detectable Patterns:**

    - `fn camelCase`
    - `struct snake_case`
    - `const lowercase`

??? info "`rust-016` — Implement Default when there is an obvious default value"
    **Types with meaningful zero/empty states should derive or implement Default**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Public structs with obvious defaults missing Default
    - Builder patterns without Default
    - Option/Vec fields without derive Default

    **Detectable Patterns:**

    - `pub struct without derive(Default)`

??? info "`rust-017` — Use From/Into for type conversions"
    **Prefer From/Into trait implementations over manual conversion functions**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Manual from_xxx() without From impl
    - Manual to_xxx() without Into impl
    - Clone-into chains suggesting missing From

    **Detectable Patterns:**

    - `fn from_string(`
    - `fn into_vec(`
    - `fn to_string(`

    !!! tip "Recommended Fix"
        impl From<T> for type conversions


## Detector Catalog

### Concurrency

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RustSendSyncDetector** | Flags unsafe Send/Sync implementations without SAFETY comments | `rust-013` |

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RustMustUseDetector** | Detects ``Result``-returning code that omits the ``#[must_use]`` attribute | `rust-005` |

### Debugging

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RustDebugDeriveDetector** | Ensures public structs derive ``Debug`` for ergonomic logging and diagnostics | `rust-006` |

### Design

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RustNewtypePatternDetector** | Flags type aliases to primitives that should be tuple-struct newtypes | `rust-007` |
| **RustEnumOverBoolDetector** | Flags structs with too many boolean fields that should be expressed as enums | `rust-010` |
| **RustInteriorMutabilityDetector** | Detects ``Rc<RefCell<T>>`` and ``Arc<Mutex<T>>`` patterns that signal design issues | `rust-012` |

### Error Handling

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RustUnwrapUsageDetector** | Flags excessive ``unwrap()`` and ``expect()`` calls that bypass Rust's error model | `rust-001` |
| **RustErrorHandlingDetector** | Flags functions that use ``Result`` without propagating errors and detects ``panic!`` abuse | `rust-001` |
| **RustErrorTraitsDetector** | Flags error types that do not implement ``std::error::Error`` | `rust-014` |

### General

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **ClutterDetector** | Stub detector for naming, dead-code, and complexity dogmas |  |
| **ControlFlowDetector** | Stub detector for return-early and fail-fast dogmas |  |
| **StateMutationDetector** | Stub detector for visible-state and strict-fences dogmas |  |
| **SignatureDetector** | Stub detector for argument-use, explicit-intent, and abstraction dogmas |  |
| **SharedDogmaKeywordDetector** | Detect configured literal patterns in source text across any language |  |

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RustIteratorPreferenceDetector** | Flags excessive manual loops where iterator adapters would be more idiomatic | `rust-003` |
| **RustStdTraitsDetector** | Detects structs that lack standard trait implementations like ``From`` or ``Display`` | `rust-009` |
| **RustDefaultImplDetector** | Flags public structs that lack a ``Default`` implementation | `rust-016` |
| **RustFromIntoDetector** | Flags ad-hoc conversion functions that should use ``From``/``Into`` traits | `rust-017` |

### Ownership

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RustLifetimeUsageDetector** | Flags excessive explicit lifetime annotations where elision would suffice | `rust-011` |

### Performance

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RustCloneOverheadDetector** | Detects excessive ``.clone()`` calls that undermine Rust's zero-cost abstraction goal | `rust-004` |

### Readability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RustNamingDetector** | Flags functions using camelCase instead of snake_case | `rust-015` |

### Safety

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RustUnsafeBlocksDetector** | Ensures every ``unsafe`` block is preceded by a ``// SAFETY:`` comment | `rust-008` |

### Type Safety

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RustTypeSafetyDetector** | Flags structs that use raw primitive types instead of domain-specific newtypes | `rust-002` |


??? example "Principle → Detector Wiring"
    ```mermaid
    graph LR
    rust_001["rust-001<br/>Avoid unwrap() and expect() in productio..."]
    rust_002["rust-002<br/>Use the type system to prevent bugs"]
    rust_003["rust-003<br/>Prefer iterators over loops"]
    rust_004["rust-004<br/>Clone sparingly"]
    rust_005["rust-005<br/>Use #[must_use] for important return typ..."]
    rust_006["rust-006<br/>Implement Debug for all public types"]
    rust_007["rust-007<br/>Use newtype pattern for type safety"]
    rust_008["rust-008<br/>Avoid unsafe unless necessary"]
    rust_009["rust-009<br/>Use std traits appropriately"]
    rust_010["rust-010<br/>Prefer enums over booleans for state"]
    rust_011["rust-011<br/>Use lifetimes judiciously"]
    rust_012["rust-012<br/>Avoid Rc<RefCell<T>> unless necessary"]
    rust_013["rust-013<br/>Send + Sync should be implemented when t..."]
    rust_014["rust-014<br/>Error types should implement standard er..."]
    rust_015["rust-015<br/>Follow Rust naming conventions (RFC 430)"]
    rust_016["rust-016<br/>Implement Default when there is an obvio..."]
    rust_017["rust-017<br/>Use From/Into for type conversions"]
    det_ClutterDetector["ClutterDetector"]
    det_ControlFlowDetector["ControlFlowDetector"]
    det_RustCloneOverheadDetector["RustCloneOverheadDetector"]
    rust_004 --> det_RustCloneOverheadDetector
    det_RustDebugDeriveDetector["RustDebugDeriveDetector"]
    rust_006 --> det_RustDebugDeriveDetector
    det_RustDefaultImplDetector["RustDefaultImplDetector"]
    rust_016 --> det_RustDefaultImplDetector
    det_RustEnumOverBoolDetector["RustEnumOverBoolDetector"]
    rust_010 --> det_RustEnumOverBoolDetector
    det_RustErrorHandlingDetector["RustErrorHandlingDetector"]
    rust_001 --> det_RustErrorHandlingDetector
    det_RustErrorTraitsDetector["RustErrorTraitsDetector"]
    rust_014 --> det_RustErrorTraitsDetector
    det_RustFromIntoDetector["RustFromIntoDetector"]
    rust_017 --> det_RustFromIntoDetector
    det_RustInteriorMutabilityDetector["RustInteriorMutabilityDetector"]
    rust_012 --> det_RustInteriorMutabilityDetector
    det_RustIteratorPreferenceDetector["RustIteratorPreferenceDetector"]
    rust_003 --> det_RustIteratorPreferenceDetector
    det_RustLifetimeUsageDetector["RustLifetimeUsageDetector"]
    rust_011 --> det_RustLifetimeUsageDetector
    det_RustMustUseDetector["RustMustUseDetector"]
    rust_005 --> det_RustMustUseDetector
    det_RustNamingDetector["RustNamingDetector"]
    rust_015 --> det_RustNamingDetector
    det_RustNewtypePatternDetector["RustNewtypePatternDetector"]
    rust_007 --> det_RustNewtypePatternDetector
    det_RustSendSyncDetector["RustSendSyncDetector"]
    rust_013 --> det_RustSendSyncDetector
    det_RustStdTraitsDetector["RustStdTraitsDetector"]
    rust_009 --> det_RustStdTraitsDetector
    det_RustTypeSafetyDetector["RustTypeSafetyDetector"]
    rust_002 --> det_RustTypeSafetyDetector
    det_RustUnsafeBlocksDetector["RustUnsafeBlocksDetector"]
    rust_008 --> det_RustUnsafeBlocksDetector
    det_RustUnwrapUsageDetector["RustUnwrapUsageDetector"]
    rust_001 --> det_RustUnwrapUsageDetector
    det_SharedDogmaKeywordDetector["SharedDogmaKeywordDetector"]
    det_SignatureDetector["SignatureDetector"]
    det_StateMutationDetector["StateMutationDetector"]
    classDef principle fill:#4051b5,color:#fff,stroke:none
    classDef detector fill:#26a269,color:#fff,stroke:none
    class rust_001 principle
    class rust_002 principle
    class rust_003 principle
    class rust_004 principle
    class rust_005 principle
    class rust_006 principle
    class rust_007 principle
    class rust_008 principle
    class rust_009 principle
    class rust_010 principle
    class rust_011 principle
    class rust_012 principle
    class rust_013 principle
    class rust_014 principle
    class rust_015 principle
    class rust_016 principle
    class rust_017 principle
    class det_ClutterDetector detector
    class det_ControlFlowDetector detector
    class det_RustCloneOverheadDetector detector
    class det_RustDebugDeriveDetector detector
    class det_RustDefaultImplDetector detector
    class det_RustEnumOverBoolDetector detector
    class det_RustErrorHandlingDetector detector
    class det_RustErrorTraitsDetector detector
    class det_RustFromIntoDetector detector
    class det_RustInteriorMutabilityDetector detector
    class det_RustIteratorPreferenceDetector detector
    class det_RustLifetimeUsageDetector detector
    class det_RustMustUseDetector detector
    class det_RustNamingDetector detector
    class det_RustNewtypePatternDetector detector
    class det_RustSendSyncDetector detector
    class det_RustStdTraitsDetector detector
    class det_RustTypeSafetyDetector detector
    class det_RustUnsafeBlocksDetector detector
    class det_RustUnwrapUsageDetector detector
    class det_SharedDogmaKeywordDetector detector
    class det_SignatureDetector detector
    class det_StateMutationDetector detector
    ```

## Configuration

```yaml
languages:
  rust:
    enabled: true
    pipeline:
      - type: rust_unwrap_usage
        max_unwraps: 0
      - type: rust-002
        primitive_types: ['String', 'i32', 'u32', 'i64', 'u64', 'bool']
      - type: rust-003
        max_loops: 0
      - type: rust_unsafe_blocks
        detect_unsafe_blocks: True
      - type: rust_clone_overhead
        max_clone_calls: 0
      - type: rust_error_handling
        detect_unhandled_results: True
        max_panics: 0
      - type: rust-007
        primitive_types: ['String', 'i32', 'u32', 'i64', 'u64', 'bool']
      - type: rust-010
        max_bool_fields: 0
      - type: rust-011
        max_explicit_lifetimes: 0
```


## See Also

- [C++](cpp.md) — Systems programming counterpart with different safety models
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
