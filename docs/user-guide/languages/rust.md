---
title: Rust
description: "12 zen principles enforced by 13 detectors: Safety, Concurrency, and Zero-Cost Abstractions."
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

12 principles across 9 categories, drawn from [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/).

<div class="grid" markdown>

:material-tag-outline: **Correctness** · 1 principle
:material-tag-outline: **Debugging** · 1 principle
:material-tag-outline: **Design** · 3 principles
:material-tag-outline: **Error Handling** · 1 principle
:material-tag-outline: **Idioms** · 2 principles
:material-tag-outline: **Ownership** · 1 principle
:material-tag-outline: **Performance** · 1 principle
:material-tag-outline: **Safety** · 1 principle
:material-tag-outline: **Type Safety** · 1 principle

</div>

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `rust-001` | Avoid unwrap() and expect() in production code | Error Handling | 9 |
| `rust-002` | Use the type system to prevent bugs | Type Safety | 8 |
| `rust-003` | Prefer iterators over loops | Idioms | 7 |
| `rust-004` | Clone sparingly | Performance | 7 |
| `rust-005` | Use #[must_use] for important return types | Correctness | 6 |
| `rust-006` | Implement Debug for all public types | Debugging | 6 |
| `rust-007` | Use newtype pattern for type safety | Design | 7 |
| `rust-008` | Avoid unsafe unless necessary | Safety | 9 |
| `rust-009` | Use std traits appropriately | Idioms | 7 |
| `rust-010` | Prefer enums over booleans for state | Design | 7 |
| `rust-011` | Use lifetimes judiciously | Ownership | 6 |
| `rust-012` | Avoid Rc<RefCell<T>> unless necessary | Design | 7 |

??? info "`rust-001` — Avoid unwrap() and expect() in production code"
    **Use proper error handling with Result and Option**

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

    **Common Violations:**

    - Cloning when references work
    - Excessive .clone() calls
    - Not using Cow<T>
    - Cloning in hot paths

??? info "`rust-005` — Use #[must_use] for important return types"
    **Mark Result and critical types as must_use**

    **Common Violations:**

    - Result types without must_use
    - Ignoring function return values
    - Not annotating important builders

    **Detectable Patterns:**

    - `!#[must_use]`

??? info "`rust-006` — Implement Debug for all public types"
    **Derive or implement Debug for better debugging**

    **Common Violations:**

    - Public structs without Debug
    - Complex types without Debug
    - Not using #[derive(Debug)]

    **Detectable Patterns:**

    - `!#[derive(Debug)]`

??? info "`rust-007` — Use newtype pattern for type safety"
    **Wrap primitives in newtypes for semantic clarity**

    **Common Violations:**

    - Using raw integers for IDs
    - String for typed values
    - Not distinguishing similar types (UserId vs ProductId)

    **Detectable Patterns:**

    - `!struct `

??? info "`rust-008` — Avoid unsafe unless necessary"
    **Minimize unsafe code and document invariants**

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

    **Common Violations:**

    - Boolean flags for state
    - Multiple related booleans
    - State represented by Option<()>

    **Detectable Patterns:**

    - `bool`

??? info "`rust-011` — Use lifetimes judiciously"
    **Let the compiler infer when possible, be explicit when needed**

    **Common Violations:**

    - Unnecessary lifetime annotations
    - Overly complex lifetime bounds
    - Fighting the borrow checker instead of redesigning

    **Detectable Patterns:**

    - `<'a>`
    - `<'static>`

??? info "`rust-012` — Avoid Rc<RefCell<T>> unless necessary"
    **Prefer ownership or references over runtime borrowing**

    **Common Violations:**

    - Overuse of Rc<RefCell<T>>
    - Interior mutability when not needed
    - Arc<Mutex<T>> in single-threaded code

    **Detectable Patterns:**

    - `Rc<RefCell`
    - `Arc<Mutex`


## Detector Catalog

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

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RustIteratorPreferenceDetector** | Flags excessive manual loops where iterator adapters would be more idiomatic | `rust-003` |
| **RustStdTraitsDetector** | Detects structs that lack standard trait implementations like ``From`` or ``Display`` | `rust-009` |

### Ownership

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RustLifetimeUsageDetector** | Flags excessive explicit lifetime annotations where elision would suffice | `rust-011` |

### Performance

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RustCloneOverheadDetector** | Detects excessive ``.clone()`` calls that undermine Rust's zero-cost abstraction goal | `rust-004` |

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
    det_RustCloneOverheadDetector["RustCloneOverheadDetector"]
    rust_004 --> det_RustCloneOverheadDetector
    det_RustDebugDeriveDetector["RustDebugDeriveDetector"]
    rust_006 --> det_RustDebugDeriveDetector
    det_RustEnumOverBoolDetector["RustEnumOverBoolDetector"]
    rust_010 --> det_RustEnumOverBoolDetector
    det_RustErrorHandlingDetector["RustErrorHandlingDetector"]
    rust_001 --> det_RustErrorHandlingDetector
    det_RustInteriorMutabilityDetector["RustInteriorMutabilityDetector"]
    rust_012 --> det_RustInteriorMutabilityDetector
    det_RustIteratorPreferenceDetector["RustIteratorPreferenceDetector"]
    rust_003 --> det_RustIteratorPreferenceDetector
    det_RustLifetimeUsageDetector["RustLifetimeUsageDetector"]
    rust_011 --> det_RustLifetimeUsageDetector
    det_RustMustUseDetector["RustMustUseDetector"]
    rust_005 --> det_RustMustUseDetector
    det_RustNewtypePatternDetector["RustNewtypePatternDetector"]
    rust_007 --> det_RustNewtypePatternDetector
    det_RustStdTraitsDetector["RustStdTraitsDetector"]
    rust_009 --> det_RustStdTraitsDetector
    det_RustTypeSafetyDetector["RustTypeSafetyDetector"]
    rust_002 --> det_RustTypeSafetyDetector
    det_RustUnsafeBlocksDetector["RustUnsafeBlocksDetector"]
    rust_008 --> det_RustUnsafeBlocksDetector
    det_RustUnwrapUsageDetector["RustUnwrapUsageDetector"]
    rust_001 --> det_RustUnwrapUsageDetector
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
    class det_RustCloneOverheadDetector detector
    class det_RustDebugDeriveDetector detector
    class det_RustEnumOverBoolDetector detector
    class det_RustErrorHandlingDetector detector
    class det_RustInteriorMutabilityDetector detector
    class det_RustIteratorPreferenceDetector detector
    class det_RustLifetimeUsageDetector detector
    class det_RustMustUseDetector detector
    class det_RustNewtypePatternDetector detector
    class det_RustStdTraitsDetector detector
    class det_RustTypeSafetyDetector detector
    class det_RustUnsafeBlocksDetector detector
    class det_RustUnwrapUsageDetector detector
    ```

## Configuration

```yaml
languages:
  rust:
    enabled: true
    pipeline:
      - type: rust-unwrap-usage
        max_unwraps: 0
      - type: rust-002
        primitive_types: ['String', 'i32', 'u32', 'i64', 'u64', 'bool']
      - type: rust-003
        max_loops: 0
      - type: rust-unsafe-blocks
        detect_unsafe_blocks: True
      - type: rust-clone-overhead
        max_clone_calls: 0
      - type: rust-error-handling
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
