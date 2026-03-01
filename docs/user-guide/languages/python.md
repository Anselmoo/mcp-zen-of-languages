---
title: Python
description: "19 zen principles enforced by 30 detectors: The Zen of Python (PEP 20)."
icon: fontawesome/brands/python
tags:
  - Python
---

# Python

Python's zen principles come directly from [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/). If you've ever typed `import this` in a Python REPL, you've seen them. MCP Zen of Languages turns these aphorisms into **actionable code analysis** — 12 principles enforced by 23 detectors.

!!! tip "Deepest analysis available"
    Python is the only language with full **AST parsing**, **cyclomatic complexity** measurement, **maintainability index** scoring, and **dependency graph analysis**. Other languages use regex-based detection.

## Optional External Tool Augmentation

!!! info "Consent-first external tooling"
    External tool execution is optional and disabled by default. Use
    `--enable-external-tools` (CLI) or `enable_external_tools=true` (MCP)
    to opt in. Missing tools should return recommendations; no automatic
    installs occur during analysis.

| Tool | Default invocation | Output |
|------|---------------------|--------|
| `ruff` | `ruff check --stdin-filename stdin.py -` | Text / structured stderr |

!!! tip "Temporary runner fallback"
    For temporary execution via package runners, use
    `--allow-temporary-runners` (CLI) or `allow_temporary_runners=true` (MCP).


## Zen Principles

19 principles across 11 categories, drawn from [PEP 20 - The Zen of Python](https://peps.python.org/pep-0020/).

<div class="grid" markdown>

:material-tag-outline: **Architecture** · 1 principle
:material-tag-outline: **Clarity** · 1 principle
:material-tag-outline: **Complexity** · 1 principle
:material-tag-outline: **Consistency** · 1 principle
:material-tag-outline: **Correctness** · 2 principles
:material-tag-outline: **Design** · 2 principles
:material-tag-outline: **Error Handling** · 1 principle
:material-tag-outline: **Idioms** · 2 principles
:material-tag-outline: **Organization** · 1 principle
:material-tag-outline: **Readability** · 5 principles
:material-tag-outline: **Structure** · 2 principles

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `python-001` | Beautiful is better than ugly | Readability | 4 | `ZEN-UNAMBIGUOUS-NAME` |
| `python-002` | Explicit is better than implicit | Clarity | 7 | `ZEN-EXPLICIT-INTENT` |
| `python-003` | Simple is better than complex | Complexity | 8 | `ZEN-PROPORTIONATE-COMPLEXITY`, `ZEN-RETURN-EARLY`, `ZEN-RIGHT-ABSTRACTION` |
| `python-004` | Complex is better than complicated | Architecture | 7 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-PROPORTIONATE-COMPLEXITY` |
| `python-005` | Flat is better than nested | Structure | 8 | `ZEN-RETURN-EARLY` |
| `python-006` | Sparse is better than dense | Readability | 5 | `ZEN-UNAMBIGUOUS-NAME`, `ZEN-VISIBLE-STATE` |
| `python-007` | Readability counts | Readability | 9 | `ZEN-UNAMBIGUOUS-NAME` |
| `python-008` | Special cases aren't special enough to break the rules | Consistency | 6 | `ZEN-EXPLICIT-INTENT`, `ZEN-FAIL-FAST` |
| `python-009` | Errors should never pass silently | Error Handling | 9 | `ZEN-FAIL-FAST`, `ZEN-EXPLICIT-INTENT` |
| `python-010` | In the face of ambiguity, refuse the temptation to guess | Correctness | 7 | `ZEN-EXPLICIT-INTENT` |
| `python-011` | There should be one-- and preferably only one --obvious way to do it | Idioms | 6 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE` |
| `python-012` | Namespaces are one honking great idea | Organization | 7 | `ZEN-STRICT-FENCES`, `ZEN-UNAMBIGUOUS-NAME` |
| `python-013` | Practicality beats purity | Design | 5 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-PROPORTIONATE-COMPLEXITY` |
| `python-014` | Errors should never pass silently | Correctness | 8 | `ZEN-EXPLICIT-INTENT`, `ZEN-FAIL-FAST` |
| `python-015` | Now is better than never | Structure | 4 | `ZEN-RETURN-EARLY` |
| `python-016` | Although never is often better than *right* now | Design | 5 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-FAIL-FAST` |
| `python-017` | If the implementation is hard to explain, it's a bad idea | Readability | 6 | `ZEN-UNAMBIGUOUS-NAME` |
| `python-018` | If the implementation is easy to explain, it may be a good idea | Readability | 3 | `ZEN-UNAMBIGUOUS-NAME`, `ZEN-PROPORTIONATE-COMPLEXITY` |
| `python-019` | There should be one-- and preferably only one --obvious way to do it | Idioms | 5 | `ZEN-RIGHT-ABSTRACTION` |

??? info "`python-001` — Beautiful is better than ugly"
    **Code should be aesthetically pleasing and well-formatted**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Inconsistent indentation
    - Poor naming conventions
    - Lack of whitespace around operators
    - Overly compact code

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_line_length` | `88` |
    | `naming_convention` | `snake_case` |
    | `min_identifier_length` | `2` |

??? info "`python-002` — Explicit is better than implicit"
    **Code behavior should be obvious and unambiguous**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Using global variables without declaration
    - Implicit type conversions
    - Magic numbers without constants
    - Overuse of * imports
    - Hidden side effects in functions

    **Detectable Patterns:**

    - `from module import *`
    - `global keyword abuse`
    - `functions modifying arguments without clear indication`

??? info "`python-003` — Simple is better than complex"
    **Favor straightforward solutions over complicated ones**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`, `ZEN-RETURN-EARLY`, `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - High cyclomatic complexity (>10)
    - Overly nested comprehensions
    - Unnecessary abstraction layers
    - Complex one-liners

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_cyclomatic_complexity` | `10` |

??? info "`python-004` — Complex is better than complicated"
    **When complexity is necessary, keep it organized and understandable**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - Tangled dependencies
    - Unclear module boundaries
    - Mixed concerns in single class

??? info "`python-005` — Flat is better than nested"
    **Avoid deep nesting of control structures**

    **Universal Dogmas:** `ZEN-RETURN-EARLY`
    **Common Violations:**

    - Nesting depth > 3 levels
    - Multiple nested loops
    - Deeply nested if-else chains

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_nesting_depth` | `3` |

??? info "`python-006` — Sparse is better than dense"
    **Code should have appropriate spacing and not be cramped**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Multiple statements on one line
    - Overly compact expressions
    - Lack of blank lines between logical sections

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_statements_per_line` | `1` |
    | `min_blank_lines_between_defs` | `1` |

??? info "`python-007` — Readability counts"
    **Code is read more often than written**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Functions longer than 50 lines
    - Classes longer than 300 lines
    - Unclear variable names (a, b, x)
    - Missing docstrings for public APIs

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_function_length` | `50` |
    | `max_class_length` | `300` |

??? info "`python-008` — Special cases aren't special enough to break the rules"
    **Maintain consistency even for edge cases**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-FAIL-FAST`
    **Common Violations:**

    - Inconsistent error handling patterns
    - Different naming conventions within same module
    - Special-case code paths without justification

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_naming_styles` | `1` |

??? info "`python-009` — Errors should never pass silently"
    **Always handle errors explicitly**

    **Universal Dogmas:** `ZEN-FAIL-FAST`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Bare except clauses
    - Catching Exception without handling
    - Ignoring return codes
    - Empty except blocks

    **Detectable Patterns:**

    - `except: pass`
    - `except Exception: pass`

??? info "`python-010` — In the face of ambiguity, refuse the temptation to guess"
    **Be explicit rather than making assumptions**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Implicit type assumptions
    - Unclear function contracts
    - Missing input validation

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `require_type_hints` | `True` |

??? info "`python-011` — There should be one-- and preferably only one --obvious way to do it"
    **Prefer pythonic idioms over alternatives**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Using range(len()) instead of enumerate
    - Manual iteration instead of list comprehensions
    - Not using context managers for resources
    - Multiple implementations of same logic

    **Detectable Patterns:**

    - `for i in range(len(list))`
    - `file without 'with' statement`

??? info "`python-012` — Namespaces are one honking great idea"
    **Use namespaces to organize code clearly**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`, `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Polluting global namespace
    - Too many items in __all__
    - Deep module nesting without purpose

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_top_level_symbols` | `25` |
    | `max_exports` | `20` |

??? info "`python-013` — Practicality beats purity"
    **Prefer simple, practical solutions over excessive abstraction**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - Over-engineered ABC/Protocol hierarchies
    - Premature abstraction with few implementations

??? info "`python-014` — Errors should never pass silently"
    **Handle errors explicitly; never swallow exceptions**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-FAIL-FAST`
    **Common Violations:**

    - Bare except clauses
    - Silent exception catching with pass

??? info "`python-015` — Now is better than never"
    **Address TODOs and stubs promptly**

    **Universal Dogmas:** `ZEN-RETURN-EARLY`
    **Common Violations:**

    - TODO/FIXME/HACK/XXX comments left unresolved

??? info "`python-016` — Although never is often better than *right* now"
    **Document why functionality is deferred rather than raising bare NotImplementedError**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-FAIL-FAST`
    **Common Violations:**

    - Undocumented NotImplementedError stubs

??? info "`python-017` — If the implementation is hard to explain, it's a bad idea"
    **Complex code must be documented**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Functions without docstrings

??? info "`python-018` — If the implementation is easy to explain, it may be a good idea"
    **Even simple public functions benefit from docstrings**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`, `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - Public functions without docstrings

??? info "`python-019` — There should be one-- and preferably only one --obvious way to do it"
    **Use idiomatic Python constructs**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Using range(len()) instead of enumerate()
    - Comparing with == True/False instead of direct boolean checks


## Detector Catalog

### Architecture

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **GodClassDetector** | Detect God classes — classes with too many methods or lines of code | `python-004` |
| **CircularDependencyDetector** | Detect circular import dependencies across modules | `python-004` |
| **DeepInheritanceDetector** | Detect class hierarchies that exceed a safe inheritance depth | `python-004` |

### Clarity

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **MagicMethodDetector** | Detect classes that overload too many dunder (magic) methods | `python-002` |
| **StarImportDetector** | Detect wildcard ``from X import *`` statements that pollute the module namespace | `python-002` |
| **MagicNumberDetector** | Detect excessive use of unexplained numeric literals (magic numbers) | `python-002` |

### Complexity

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CyclomaticComplexityDetector** | Detect functions whose cyclomatic complexity exceeds the configured threshold | `python-003` |
| **ComplexOneLinersDetector** | Detect overly dense one-liner expressions that sacrifice readability | `python-003` |

### Consistency

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **ConsistencyDetector** | Detect mixed naming conventions within a single module | `python-008` |

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **ExplicitnessDetector** | Detect function parameters missing type annotations | `python-010` |
| **PythonExplicitSilenceDetector** | Detects bare except clauses and silently caught exceptions | `python-014` |

### Design

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **PythonPracticalityDetector** | Flags over-engineered abstractions like ABCs with likely few implementations | `python-013` |
| **PythonPrematureImplDetector** | Detects ``raise NotImplementedError`` stubs without documentation | `python-016` |

### Error Handling

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **BareExceptDetector** | Detect bare ``except:`` clauses and silently swallowed exceptions | `python-009` |

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **FeatureEnvyDetector** | Detect methods that access another object's data more than their own | `python-011` |
| **DuplicateImplementationDetector** | Detect identical or near-identical function implementations across files | `python-011` |
| **ContextManagerDetector** | Detect ``open()`` calls not wrapped in a ``with`` context manager | `python-011` |
| **PythonIdiomDetector** | Detects non-idiomatic Python patterns like ``range(len(...))`` and ``== True`` | `python-019` |

### Organization

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **NamespaceUsageDetector** | Detect modules with too many top-level symbols or ``__all__`` exports | `python-012` |

### Readability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **NameStyleDetector** | Detect function and variable names that violate Python's ``snake_case`` convention | `python-001` |
| **LongFunctionDetector** | Detect functions whose line count exceeds the configured maximum | `python-007` |
| **ShortVariableNamesDetector** | Detect variables and loop targets with names shorter than the configured minimum | `python-007` |
| **ClassSizeDetector** | Detect classes whose line count exceeds the configured maximum | `python-007` |
| **LineLengthDetector** | Detect source lines that exceed a configured character limit | `python-001` |
| **SparseCodeDetector** | Detect lines packing multiple statements separated by semicolons | `python-006` |
| **DocstringDetector** | Detect top-level functions and classes missing a docstring | `python-007` |
| **PythonComplexUndocumentedDetector** | Detects functions missing docstrings | `python-017` |
| **PythonSimpleDocumentedDetector** | Detects public functions (not starting with ``_``) missing docstrings | `python-018` |

### Structure

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **NestingDepthDetector** | Detect code blocks with excessive indentation depth and nested loops | `python-005` |
| **PythonTodoStubDetector** | Detects TODO, FIXME, HACK, and XXX comments left in source code | `python-015` |


??? example "Principle → Detector Wiring"
    ```mermaid
    graph LR
    python_001["python-001<br/>Beautiful is better than ugly"]
    python_002["python-002<br/>Explicit is better than implicit"]
    python_003["python-003<br/>Simple is better than complex"]
    python_004["python-004<br/>Complex is better than complicated"]
    python_005["python-005<br/>Flat is better than nested"]
    python_006["python-006<br/>Sparse is better than dense"]
    python_007["python-007<br/>Readability counts"]
    python_008["python-008<br/>Special cases aren't special enough to b..."]
    python_009["python-009<br/>Errors should never pass silently"]
    python_010["python-010<br/>In the face of ambiguity, refuse the tem..."]
    python_011["python-011<br/>There should be one-- and preferably onl..."]
    python_012["python-012<br/>Namespaces are one honking great idea"]
    python_013["python-013<br/>Practicality beats purity"]
    python_014["python-014<br/>Errors should never pass silently"]
    python_015["python-015<br/>Now is better than never"]
    python_016["python-016<br/>Although never is often better than *rig..."]
    python_017["python-017<br/>If the implementation is hard to explain..."]
    python_018["python-018<br/>If the implementation is easy to explain..."]
    python_019["python-019<br/>There should be one-- and preferably onl..."]
    det_BareExceptDetector["BareExceptDetector"]
    python_009 --> det_BareExceptDetector
    det_CircularDependencyDetector["CircularDependencyDetector"]
    python_004 --> det_CircularDependencyDetector
    det_ClassSizeDetector["ClassSizeDetector"]
    python_007 --> det_ClassSizeDetector
    det_ComplexOneLinersDetector["ComplexOneLinersDetector"]
    python_003 --> det_ComplexOneLinersDetector
    det_ConsistencyDetector["ConsistencyDetector"]
    python_008 --> det_ConsistencyDetector
    det_ContextManagerDetector["ContextManagerDetector"]
    python_011 --> det_ContextManagerDetector
    det_CyclomaticComplexityDetector["CyclomaticComplexityDetector"]
    python_003 --> det_CyclomaticComplexityDetector
    det_DeepInheritanceDetector["DeepInheritanceDetector"]
    python_004 --> det_DeepInheritanceDetector
    det_DocstringDetector["DocstringDetector"]
    python_007 --> det_DocstringDetector
    det_DuplicateImplementationDetector["DuplicateImplementationDetector"]
    python_011 --> det_DuplicateImplementationDetector
    det_ExplicitnessDetector["ExplicitnessDetector"]
    python_010 --> det_ExplicitnessDetector
    det_FeatureEnvyDetector["FeatureEnvyDetector"]
    python_011 --> det_FeatureEnvyDetector
    det_GodClassDetector["GodClassDetector"]
    python_004 --> det_GodClassDetector
    det_LineLengthDetector["LineLengthDetector"]
    python_001 --> det_LineLengthDetector
    det_LongFunctionDetector["LongFunctionDetector"]
    python_007 --> det_LongFunctionDetector
    det_MagicMethodDetector["MagicMethodDetector"]
    python_002 --> det_MagicMethodDetector
    det_MagicNumberDetector["MagicNumberDetector"]
    python_002 --> det_MagicNumberDetector
    det_NameStyleDetector["NameStyleDetector"]
    det_NamespaceUsageDetector["NamespaceUsageDetector"]
    python_012 --> det_NamespaceUsageDetector
    det_NestingDepthDetector["NestingDepthDetector"]
    python_005 --> det_NestingDepthDetector
    det_PythonComplexUndocumentedDetector["PythonComplexUndocumentedDetector"]
    python_017 --> det_PythonComplexUndocumentedDetector
    det_PythonExplicitSilenceDetector["PythonExplicitSilenceDetector"]
    python_014 --> det_PythonExplicitSilenceDetector
    det_PythonIdiomDetector["PythonIdiomDetector"]
    python_019 --> det_PythonIdiomDetector
    det_PythonPracticalityDetector["PythonPracticalityDetector"]
    python_013 --> det_PythonPracticalityDetector
    det_PythonPrematureImplDetector["PythonPrematureImplDetector"]
    python_016 --> det_PythonPrematureImplDetector
    det_PythonSimpleDocumentedDetector["PythonSimpleDocumentedDetector"]
    python_018 --> det_PythonSimpleDocumentedDetector
    det_PythonTodoStubDetector["PythonTodoStubDetector"]
    python_015 --> det_PythonTodoStubDetector
    det_ShortVariableNamesDetector["ShortVariableNamesDetector"]
    python_007 --> det_ShortVariableNamesDetector
    det_SparseCodeDetector["SparseCodeDetector"]
    python_006 --> det_SparseCodeDetector
    det_StarImportDetector["StarImportDetector"]
    python_002 --> det_StarImportDetector
    classDef principle fill:#4051b5,color:#fff,stroke:none
    classDef detector fill:#26a269,color:#fff,stroke:none
    class python_001 principle
    class python_002 principle
    class python_003 principle
    class python_004 principle
    class python_005 principle
    class python_006 principle
    class python_007 principle
    class python_008 principle
    class python_009 principle
    class python_010 principle
    class python_011 principle
    class python_012 principle
    class python_013 principle
    class python_014 principle
    class python_015 principle
    class python_016 principle
    class python_017 principle
    class python_018 principle
    class python_019 principle
    class det_BareExceptDetector detector
    class det_CircularDependencyDetector detector
    class det_ClassSizeDetector detector
    class det_ComplexOneLinersDetector detector
    class det_ConsistencyDetector detector
    class det_ContextManagerDetector detector
    class det_CyclomaticComplexityDetector detector
    class det_DeepInheritanceDetector detector
    class det_DocstringDetector detector
    class det_DuplicateImplementationDetector detector
    class det_ExplicitnessDetector detector
    class det_FeatureEnvyDetector detector
    class det_GodClassDetector detector
    class det_LineLengthDetector detector
    class det_LongFunctionDetector detector
    class det_MagicMethodDetector detector
    class det_MagicNumberDetector detector
    class det_NameStyleDetector detector
    class det_NamespaceUsageDetector detector
    class det_NestingDepthDetector detector
    class det_PythonComplexUndocumentedDetector detector
    class det_PythonExplicitSilenceDetector detector
    class det_PythonIdiomDetector detector
    class det_PythonPracticalityDetector detector
    class det_PythonPrematureImplDetector detector
    class det_PythonSimpleDocumentedDetector detector
    class det_PythonTodoStubDetector detector
    class det_ShortVariableNamesDetector detector
    class det_SparseCodeDetector detector
    class det_StarImportDetector detector
    ```

## Configuration

```yaml
languages:
  python:
    enabled: true
    pipeline:
      - type: cyclomatic-complexity
        max_cyclomatic_complexity: 10
      - type: complex-one-liners
        max_for_clauses: 1
        max_line_length: 120
      - type: nesting-depth
        max_nesting_depth: 3
      - type: long-functions
        max_function_length: 50
      - type: short-variable-names
        min_identifier_length: 3
        allowed_loop_names: PydanticUndefined
      - type: god-classes
        max_methods: 10
        max_class_length: 300
      - type: magic-methods
        max_magic_methods: 3
      - type: deep-inheritance
        max_depth: 3
      - type: feature-envy
        min_occurrences: 3
      - type: class-size
        max_class_length: 300
      - type: magic-number
        max_magic_numbers: 0
      - type: line-length
        max_line_length: 88
      - type: sparse-code
        max_statements_per_line: 1
        min_blank_lines_between_defs: 1
      - type: consistency
        max_naming_styles: 1
      - type: explicitness
        require_type_hints: True
      - type: namespace-usage
        max_top_level_symbols: 25
        max_exports: 20
```

???+ tip "Start relaxed, tighten over time"
    For legacy codebases, start with `max_cyclomatic_complexity: 15` and `max_function_length: 80`, then lower thresholds as you remediate.

## See Also

- [Configuration](../configuration.md) — Full config reference and override strategies
- [Understanding Violations](../understanding-violations.md) — How to interpret severity scores
- [Prompt Generation](../prompt-generation.md) — Generate AI remediation prompts from violations
