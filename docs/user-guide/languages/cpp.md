---
title: C++
description: "13 zen principles enforced by 13 detectors: Modern C++ Best Practices (C++11/14/17/20)."
icon: material/language-cpp
tags:
  - C++
---

# C++

Modern C++ (C++11 through C++20) is a fundamentally different language from the C-with-classes of the 1990s. These **13 principles** encode the [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/) philosophy: resource safety through RAII, type safety through smart pointers, and clarity through `auto`, `const`, and `override`.

## Optional External Tool Augmentation

!!! info "Consent-first external tooling"
    External tool execution is optional and disabled by default. Use
    `--enable-external-tools` (CLI) or `enable_external_tools=true` (MCP)
    to opt in. Missing tools should return recommendations; no automatic
    installs occur during analysis.

| Tool | Default invocation | Output |
|------|---------------------|--------|
| `cppcheck` | `cppcheck --language=c++ -` | Text / structured stderr |



## Zen Principles

13 principles across 7 categories, drawn from [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines).

<div class="grid" markdown>

:material-tag-outline: **Correctness** · 3 principles
:material-tag-outline: **Design** · 3 principles
:material-tag-outline: **Idioms** · 2 principles
:material-tag-outline: **Memory Management** · 2 principles
:material-tag-outline: **Performance** · 1 principle
:material-tag-outline: **Resource Management** · 1 principle
:material-tag-outline: **Type Safety** · 1 principle

</div>

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `cpp-001` | Use RAII for resource management | Resource Management | 9 |
| `cpp-002` | Prefer smart pointers over raw pointers | Memory Management | 9 |
| `cpp-003` | Use auto for type deduction | Idioms | 6 |
| `cpp-004` | Prefer nullptr over NULL or 0 | Correctness | 7 |
| `cpp-005` | Use range-based for loops | Idioms | 6 |
| `cpp-006` | Avoid manual memory allocation | Memory Management | 9 |
| `cpp-007` | Use const correctness | Correctness | 8 |
| `cpp-008` | Avoid C-style casts | Type Safety | 7 |
| `cpp-009` | Follow Rule of Zero/Three/Five | Design | 8 |
| `cpp-010` | Use std::move for rvalue references | Performance | 7 |
| `cpp-011` | Avoid global variables | Design | 8 |
| `cpp-012` | Use override and final keywords | Correctness | 7 |
| `cpp-013` | Prefer std::optional over null pointers | Design | 6 |

??? info "`cpp-001` — Use RAII for resource management"
    **Resources should be tied to object lifetime**

    **Common Violations:**

    - Manual new/delete
    - Naked pointers for ownership
    - Not using smart pointers
    - Missing destructors for resource cleanup

    **Detectable Patterns:**

    - `new `
    - `delete `
    - `malloc(`
    - `free(`

    !!! tip "Recommended Fix"
        unique_ptr, shared_ptr, RAII wrappers

??? info "`cpp-002` — Prefer smart pointers over raw pointers"
    **Use unique_ptr, shared_ptr for ownership**

    **Common Violations:**

    - new/delete in modern code
    - Raw pointers for ownership
    - Manual memory management
    - Not using make_unique/make_shared

    **Detectable Patterns:**

    - `new Type`
    - `delete ptr`

??? info "`cpp-003` — Use auto for type deduction"
    **Let the compiler deduce obvious types**

    **Common Violations:**

    - Verbose type declarations when auto works
    - Iterator types spelled out
    - Not using auto in range-based for

    **Detectable Patterns:**

    - `!auto `

??? info "`cpp-004` — Prefer nullptr over NULL or 0"
    **Use nullptr for pointer initialization**

    **Common Violations:**

    - Using NULL macro
    - Using 0 for null pointers
    - Not using nullptr

    **Detectable Patterns:**

    - `= NULL`
    - `== NULL`
    - `ptr = 0`

??? info "`cpp-005` — Use range-based for loops"
    **Prefer for(auto& item : container)**

    **Common Violations:**

    - Index-based iteration
    - Iterator-based loops when range-for works
    - Manual iteration with .begin()/.end()

    **Detectable Patterns:**

    - `.begin()`
    - `.end()`

??? info "`cpp-006` — Avoid manual memory allocation"
    **Use containers and smart pointers**

    **Common Violations:**

    - malloc/free in C++ code
    - new[] without corresponding delete[]
    - Manual array management
    - Not using std::vector, std::array

    **Detectable Patterns:**

    - `malloc(`
    - `free(`
    - `new[`
    - `delete[`

??? info "`cpp-007` — Use const correctness"
    **Mark everything const that can be const**

    **Common Violations:**

    - Non-const member functions that don't modify
    - Missing const references in parameters
    - Mutable data without justification
    - Not using constexpr when possible

    **Detectable Patterns:**

    - `!const `

??? info "`cpp-008` — Avoid C-style casts"
    **Use static_cast, dynamic_cast, const_cast**

    **Common Violations:**

    - C-style casts: (Type)value
    - Implicit dangerous conversions
    - Not using explicit casts

    **Detectable Patterns:**

    - `(Type)`
    - `C-style cast`

??? info "`cpp-009` — Follow Rule of Zero/Three/Five"
    **Properly manage special member functions**

    **Common Violations:**

    - Custom destructor without copy/move control
    - Copy constructor without assignment operator
    - Not using =default or =delete
    - Incomplete rule of five

    **Detectable Patterns:**

    - `operator=`
    - ` = delete`
    - ` = default`

??? info "`cpp-010` — Use std::move for rvalue references"
    **Enable move semantics for efficiency**

    **Common Violations:**

    - Copying when moving would work
    - Not implementing move constructors
    - Not using std::forward in templates

    **Detectable Patterns:**

    - `!std::move`

??? info "`cpp-011` — Avoid global variables"
    **Minimize mutable global state**

    **Common Violations:**

    - Mutable global variables
    - Singleton abuse
    - Static member variables as globals

    **Detectable Patterns:**

    - `static `
    - `extern `

??? info "`cpp-012` — Use override and final keywords"
    **Explicitly mark virtual function overrides**

    **Common Violations:**

    - Virtual functions without override
    - Not using final for non-overridable functions
    - Missing virtual in base class

    **Detectable Patterns:**

    - `virtual function without override keyword`

??? info "`cpp-013` — Prefer std::optional over null pointers"
    **Use std::optional for optional values**

    **Common Violations:**

    - Pointers for optional values
    - Special sentinel values (-1, nullptr)
    - Not using std::optional in C++17+

    **Detectable Patterns:**

    - `!std::optional`


## Detector Catalog

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CppNullptrDetector** | Flags legacy ``NULL`` macro usage instead of the type-safe ``nullptr`` literal | `cpp-004` |
| **CppConstCorrectnessDetector** | Flags non-const references where ``const`` qualification is appropriate | `cpp-007` |
| **CppOverrideFinalDetector** | Flags ``virtual`` overrides missing the ``override`` or ``final`` specifier | `cpp-012` |

### Design

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CppRuleOfFiveDetector** | Flags classes with destructors but missing copy/move special members | `cpp-009` |
| **CppAvoidGlobalsDetector** | Detects mutable global and file-scope ``static``/``extern`` variables | `cpp-011` |
| **CppOptionalDetector** | Suggests ``std::optional`` over nullable raw pointers for optional values | `cpp-013` |

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CppAutoDetector** | Suggests ``auto`` type deduction where explicit ``std::`` types add verbosity | `cpp-003` |
| **CppRangeForDetector** | Flags iterator-based ``for`` loops that should use range-based ``for`` | `cpp-005` |

### Memory Management

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CppSmartPointerDetector** | Flags raw ``new``/``delete`` usage where smart pointers should be used | `cpp-002` |
| **CppManualAllocationDetector** | Detects C-style heap allocation (``malloc``/``free``, ``new[]``/``delete[]``) | `cpp-006` |

### Performance

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CppMoveDetector** | Flags rvalue references (``&&``) without corresponding ``std::move`` | `cpp-010` |

### Resource Management

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CppRaiiDetector** | Detects manual resource management that should use RAII wrappers | `cpp-001` |

### Type Safety

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CppCStyleCastDetector** | Detects C-style casts that should use ``static_cast``/``dynamic_cast`` | `cpp-008` |


??? example "Principle → Detector Wiring"
    ```mermaid
    graph LR
    cpp_001["cpp-001<br/>Use RAII for resource management"]
    cpp_002["cpp-002<br/>Prefer smart pointers over raw pointers"]
    cpp_003["cpp-003<br/>Use auto for type deduction"]
    cpp_004["cpp-004<br/>Prefer nullptr over NULL or 0"]
    cpp_005["cpp-005<br/>Use range-based for loops"]
    cpp_006["cpp-006<br/>Avoid manual memory allocation"]
    cpp_007["cpp-007<br/>Use const correctness"]
    cpp_008["cpp-008<br/>Avoid C-style casts"]
    cpp_009["cpp-009<br/>Follow Rule of Zero/Three/Five"]
    cpp_010["cpp-010<br/>Use std::move for rvalue references"]
    cpp_011["cpp-011<br/>Avoid global variables"]
    cpp_012["cpp-012<br/>Use override and final keywords"]
    cpp_013["cpp-013<br/>Prefer std::optional over null pointers"]
    det_CppAutoDetector["CppAutoDetector"]
    cpp_003 --> det_CppAutoDetector
    det_CppAvoidGlobalsDetector["CppAvoidGlobalsDetector"]
    cpp_011 --> det_CppAvoidGlobalsDetector
    det_CppCStyleCastDetector["CppCStyleCastDetector"]
    cpp_008 --> det_CppCStyleCastDetector
    det_CppConstCorrectnessDetector["CppConstCorrectnessDetector"]
    cpp_007 --> det_CppConstCorrectnessDetector
    det_CppManualAllocationDetector["CppManualAllocationDetector"]
    cpp_006 --> det_CppManualAllocationDetector
    det_CppMoveDetector["CppMoveDetector"]
    cpp_010 --> det_CppMoveDetector
    det_CppNullptrDetector["CppNullptrDetector"]
    cpp_004 --> det_CppNullptrDetector
    det_CppOptionalDetector["CppOptionalDetector"]
    cpp_013 --> det_CppOptionalDetector
    det_CppOverrideFinalDetector["CppOverrideFinalDetector"]
    cpp_012 --> det_CppOverrideFinalDetector
    det_CppRaiiDetector["CppRaiiDetector"]
    cpp_001 --> det_CppRaiiDetector
    det_CppRangeForDetector["CppRangeForDetector"]
    cpp_005 --> det_CppRangeForDetector
    det_CppRuleOfFiveDetector["CppRuleOfFiveDetector"]
    cpp_009 --> det_CppRuleOfFiveDetector
    det_CppSmartPointerDetector["CppSmartPointerDetector"]
    cpp_002 --> det_CppSmartPointerDetector
    classDef principle fill:#4051b5,color:#fff,stroke:none
    classDef detector fill:#26a269,color:#fff,stroke:none
    class cpp_001 principle
    class cpp_002 principle
    class cpp_003 principle
    class cpp_004 principle
    class cpp_005 principle
    class cpp_006 principle
    class cpp_007 principle
    class cpp_008 principle
    class cpp_009 principle
    class cpp_010 principle
    class cpp_011 principle
    class cpp_012 principle
    class cpp_013 principle
    class det_CppAutoDetector detector
    class det_CppAvoidGlobalsDetector detector
    class det_CppCStyleCastDetector detector
    class det_CppConstCorrectnessDetector detector
    class det_CppManualAllocationDetector detector
    class det_CppMoveDetector detector
    class det_CppNullptrDetector detector
    class det_CppOptionalDetector detector
    class det_CppOverrideFinalDetector detector
    class det_CppRaiiDetector detector
    class det_CppRangeForDetector detector
    class det_CppRuleOfFiveDetector detector
    class det_CppSmartPointerDetector detector
    ```

## Configuration

```yaml
languages:
  cpp:
    enabled: true
    pipeline:
```


## See Also

- [Rust](rust.md) — Memory-safe systems language with compile-time guarantees
- [C#](csharp.md) — Managed C-family language with different safety model
- [Configuration](../configuration.md) — Per-language pipeline overrides
