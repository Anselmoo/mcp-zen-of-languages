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

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `cpp-001` | Use RAII for resource management | Resource Management | 9 | `ZEN-STRICT-FENCES` |
| `cpp-002` | Prefer smart pointers over raw pointers | Memory Management | 9 | `ZEN-VISIBLE-STATE` |
| `cpp-003` | Use auto for type deduction | Idioms | 6 | `ZEN-RIGHT-ABSTRACTION` |
| `cpp-004` | Prefer nullptr over NULL or 0 | Correctness | 7 | `ZEN-EXPLICIT-INTENT` |
| `cpp-005` | Use range-based for loops | Idioms | 6 | `ZEN-RIGHT-ABSTRACTION` |
| `cpp-006` | Avoid manual memory allocation | Memory Management | 9 | `ZEN-VISIBLE-STATE` |
| `cpp-007` | Use const correctness | Correctness | 8 | `ZEN-EXPLICIT-INTENT` |
| `cpp-008` | Avoid C-style casts | Type Safety | 7 | `ZEN-EXPLICIT-INTENT` |
| `cpp-009` | Follow Rule of Zero/Three/Five | Design | 8 | `ZEN-RIGHT-ABSTRACTION` |
| `cpp-010` | Use std::move for rvalue references | Performance | 7 | `ZEN-PROPORTIONATE-COMPLEXITY` |
| `cpp-011` | Avoid global variables | Design | 8 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE` |
| `cpp-012` | Use override and final keywords | Correctness | 7 | `ZEN-EXPLICIT-INTENT` |
| `cpp-013` | Prefer std::optional over null pointers | Design | 6 | `ZEN-RIGHT-ABSTRACTION` |

??? info "`cpp-001` — Use RAII for resource management"
    **Resources should be tied to object lifetime**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`
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

    **Universal Dogmas:** `ZEN-VISIBLE-STATE`
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

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Verbose type declarations when auto works
    - Iterator types spelled out
    - Not using auto in range-based for

    **Detectable Patterns:**

    - `!auto `

??? info "`cpp-004` — Prefer nullptr over NULL or 0"
    **Use nullptr for pointer initialization**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
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

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Index-based iteration
    - Iterator-based loops when range-for works
    - Manual iteration with .begin()/.end()

    **Detectable Patterns:**

    - `.begin()`
    - `.end()`

??? info "`cpp-006` — Avoid manual memory allocation"
    **Use containers and smart pointers**

    **Universal Dogmas:** `ZEN-VISIBLE-STATE`
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

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Non-const member functions that don't modify
    - Missing const references in parameters
    - Mutable data without justification
    - Not using constexpr when possible

    **Detectable Patterns:**

    - `!const `

??? info "`cpp-008` — Avoid C-style casts"
    **Use static_cast, dynamic_cast, const_cast**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - C-style casts: (Type)value
    - Implicit dangerous conversions
    - Not using explicit casts

    **Detectable Patterns:**

    - `(Type)`
    - `C-style cast`

??? info "`cpp-009` — Follow Rule of Zero/Three/Five"
    **Properly manage special member functions**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
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

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - Copying when moving would work
    - Not implementing move constructors
    - Not using std::forward in templates

    **Detectable Patterns:**

    - `!std::move`

??? info "`cpp-011` — Avoid global variables"
    **Minimize mutable global state**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Mutable global variables
    - Singleton abuse
    - Static member variables as globals

    **Detectable Patterns:**

    - `static `
    - `extern `

??? info "`cpp-012` — Use override and final keywords"
    **Explicitly mark virtual function overrides**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Virtual functions without override
    - Not using final for non-overridable functions
    - Missing virtual in base class

    **Detectable Patterns:**

    - `virtual function without override keyword`

??? info "`cpp-013` — Prefer std::optional over null pointers"
    **Use std::optional for optional values**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
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
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    cpp_001["cpp-001<br/>Use RAII for resource man..."]
    cpp_002["cpp-002<br/>Prefer smart pointers ove..."]
    cpp_003["cpp-003<br/>Use auto for type deducti..."]
    cpp_004["cpp-004<br/>Prefer nullptr over NULL ..."]
    cpp_005["cpp-005<br/>Use range-based for loops"]
    cpp_006["cpp-006<br/>Avoid manual memory alloc..."]
    cpp_007["cpp-007<br/>Use const correctness"]
    cpp_008["cpp-008<br/>Avoid C-style casts"]
    cpp_009["cpp-009<br/>Follow Rule of Zero/Three..."]
    cpp_010["cpp-010<br/>Use std::move for rvalue ..."]
    cpp_011["cpp-011<br/>Avoid global variables"]
    cpp_012["cpp-012<br/>Use override and final ke..."]
    cpp_013["cpp-013<br/>Prefer std::optional over..."]
    det_CppAutoDetector["Cpp Auto"]
    cpp_003 --> det_CppAutoDetector
    det_CppAvoidGlobalsDetector["Cpp Avoid<br/>Globals"]
    cpp_011 --> det_CppAvoidGlobalsDetector
    det_CppCStyleCastDetector["Cpp C<br/>Style Cast"]
    cpp_008 --> det_CppCStyleCastDetector
    det_CppConstCorrectnessDetector["Cpp Const<br/>Correctness"]
    cpp_007 --> det_CppConstCorrectnessDetector
    det_CppManualAllocationDetector["Cpp Manual<br/>Allocation"]
    cpp_006 --> det_CppManualAllocationDetector
    det_CppMoveDetector["Cpp Move"]
    cpp_010 --> det_CppMoveDetector
    det_CppNullptrDetector["Cpp Nullptr"]
    cpp_004 --> det_CppNullptrDetector
    det_CppOptionalDetector["Cpp Optional"]
    cpp_013 --> det_CppOptionalDetector
    det_CppOverrideFinalDetector["Cpp Override<br/>Final"]
    cpp_012 --> det_CppOverrideFinalDetector
    det_CppRaiiDetector["Cpp Raii"]
    cpp_001 --> det_CppRaiiDetector
    det_CppRangeForDetector["Cpp Range<br/>For"]
    cpp_005 --> det_CppRangeForDetector
    det_CppRuleOfFiveDetector["Cpp Rule<br/>Of Five"]
    cpp_009 --> det_CppRuleOfFiveDetector
    det_CppSmartPointerDetector["Cpp Smart<br/>Pointer"]
    cpp_002 --> det_CppSmartPointerDetector
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
        class det_01["Cpp Auto"]
        ViolationDetector <|-- det_01
        class det_02["Cpp Avoid Globals"]
        ViolationDetector <|-- det_02
        class det_03["Cpp C Style Cast"]
        ViolationDetector <|-- det_03
        class det_04["Cpp Const Correctness"]
        ViolationDetector <|-- det_04
        class det_05["Cpp Manual Allocation"]
        ViolationDetector <|-- det_05
        class det_06["Cpp Move"]
        ViolationDetector <|-- det_06
        class det_07["Cpp Nullptr"]
        ViolationDetector <|-- det_07
        class det_08["Cpp Optional"]
        ViolationDetector <|-- det_08
        class det_09["Cpp Override Final"]
        ViolationDetector <|-- det_09
        class det_10["Cpp Raii"]
        ViolationDetector <|-- det_10
        class det_11["Cpp Range For"]
        ViolationDetector <|-- det_11
        class det_12["Cpp Rule Of Five"]
        ViolationDetector <|-- det_12
        class det_13["Cpp Smart Pointer"]
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
  cpp:
    enabled: true
    pipeline:
```


## See Also

- [Rust](rust.md) — Memory-safe systems language with compile-time guarantees
- [C#](csharp.md) — Managed C-family language with different safety model
- [Configuration](../configuration.md) — Per-language pipeline overrides
