---
title: Ruby
description: "11 zen principles enforced by 11 detectors: Principle of Least Surprise (POLS) and Developer Happiness."
icon: material/language-ruby
tags:
  - Ruby
---

# Ruby

Ruby is designed for programmer happiness — expressive, elegant, optimized for reading. But that expressiveness can become a liability when metaprogramming runs wild, method chains grow unreadable, or monkey-patching mutates core classes. These **11 principles** encode the idioms that keep Ruby code joyful to maintain.

## Zen Principles

11 principles across 6 categories, drawn from [Ruby Style Guide](https://rubystyle.guide/).

<div class="grid" markdown>

:material-tag-outline: **Architecture** · 2 principles
:material-tag-outline: **Complexity** · 1 principle
:material-tag-outline: **Error Handling** · 1 principle
:material-tag-outline: **Idioms** · 4 principles
:material-tag-outline: **Readability** · 2 principles
:material-tag-outline: **Structure** · 1 principle

</div>

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `ruby-001` | Convention over configuration | Idioms | 7 |
| `ruby-002` | DRY (Don't Repeat Yourself) | Architecture | 8 |
| `ruby-003` | Prefer blocks over lambdas/procs | Idioms | 6 |
| `ruby-004` | Avoid monkey-patching core classes | Architecture | 9 |
| `ruby-005` | Use meaningful method names with ?/! convention | Readability | 7 |
| `ruby-006` | Keep method chains readable | Readability | 6 |
| `ruby-007` | Prefer symbols over strings for keys | Idioms | 5 |
| `ruby-008` | Use guard clauses | Structure | 6 |
| `ruby-009` | Avoid needless metaprogramming | Complexity | 8 |
| `ruby-010` | Use Ruby's expressive syntax | Idioms | 6 |
| `ruby-011` | Prefer fail over raise for exceptions | Error Handling | 5 |

??? info "`ruby-001` — Convention over configuration"
    **Follow Ruby naming and structural conventions**

    **Common Violations:**

    - camelCase instead of snake_case
    - Non-standard class naming
    - CONSTANTS in lowercase
    - Methods starting with capital letters

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `naming_convention` | `snake_case for methods/variables, PascalCase for classes` |

??? info "`ruby-002` — DRY (Don't Repeat Yourself)"
    **Eliminate code duplication through abstraction**

    **Common Violations:**

    - Duplicated code blocks (>5 lines)
    - Similar methods without extraction
    - Repeated conditional logic
    - Copy-pasted code

    **Detectable Patterns:**

    - `dup(`
    - `clone(`

??? info "`ruby-003` — Prefer blocks over lambdas/procs"
    **Use blocks for most iteration and callbacks**

    **Common Violations:**

    - Lambda where block would be clearer
    - Proc for simple iterations
    - Not using Ruby's block syntax

    **Detectable Patterns:**

    - `lambda { } for simple iterations`
    - `Proc.new instead of block`

??? info "`ruby-004` — Avoid monkey-patching core classes"
    **Don't modify String, Array, or other core classes**

    **Common Violations:**

    - Reopening String class
    - Reopening Array class
    - Modifying Integer, Hash
    - Adding methods to core classes

    **Detectable Patterns:**

    - `class String`
    - `class Array`
    - `class Hash`

??? info "`ruby-005` — Use meaningful method names with ?/! convention"
    **Methods ending in ? return boolean, ! indicate mutation**

    **Common Violations:**

    - Boolean methods without ?
    - Mutating methods without !
    - Inconsistent naming patterns

    **Detectable Patterns:**

    - `def is`
    - `def has`

??? info "`ruby-006` — Keep method chains readable"
    **Limit method chaining to 3-4 calls**

    **Common Violations:**

    - Method chains > 4 calls
    - Complex chaining without intermediate variables
    - Unclear chaining logic

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_method_chain_length` | `4` |

??? info "`ruby-007` — Prefer symbols over strings for keys"
    **Use symbols for hash keys and identifiers**

    **Common Violations:**

    - String keys in hashes
    - Strings for method names in send
    - String identifiers

    **Detectable Patterns:**

    - `=> "`
    - `=> '`

??? info "`ruby-008` — Use guard clauses"
    **Return early to avoid deep nesting**

    **Common Violations:**

    - Deep nested if-else
    - Not using early returns
    - Inverted logic creating nesting

    **Detectable Patterns:**

    - `!return if`

    !!! tip "Recommended Fix"
        return unless, return if

??? info "`ruby-009` — Avoid needless metaprogramming"
    **Use metaprogramming sparingly and only when necessary**

    **Common Violations:**

    - define_method without clear benefit
    - method_missing abuse
    - Overly clever class_eval
    - Unnecessary send/public_send

    **Detectable Patterns:**

    - `define_method`
    - `method_missing`
    - `class_eval`
    - `instance_eval`
    - `send(`

??? info "`ruby-010` — Use Ruby's expressive syntax"
    **Leverage Ruby's readable constructs**

    **Common Violations:**

    - for loops instead of .each
    - unless with negation
    - Not using &: syntax
    - Ternary when if/else is clearer

    **Detectable Patterns:**

    - `for item in collection`
    - `unless !condition`

??? info "`ruby-011` — Prefer fail over raise for exceptions"
    **Use fail to indicate programmer errors**

    **Common Violations:**

    - Using raise for logic errors
    - Not distinguishing error types

    **Detectable Patterns:**

    - `raise `


## Detector Catalog

### Architecture

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RubyDryDetector** | Identifies duplicated code lines that violate Don't Repeat Yourself (DRY) | `ruby-002` |
| **RubyMonkeyPatchDetector** | Detects reopening of core Ruby classes (monkey patching) | `ruby-004` |

### Complexity

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RubyMetaprogrammingDetector** | Flags dangerous metaprogramming constructs like ``method_missing`` and ``eval`` | `ruby-009` |

### Error Handling

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RubyPreferFailDetector** | Flags use of ``raise`` where ``fail`` is the preferred convention for programmer errors | `ruby-011` |

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RubyNamingConventionDetector** | Flags Ruby methods defined with non-snake_case names | `ruby-001` |
| **RubyBlockPreferenceDetector** | Flags use of ``lambda``/``Proc.new`` where idiomatic blocks would suffice | `ruby-003` |
| **RubySymbolKeysDetector** | Flags hash literals using string keys instead of idiomatic symbol keys | `ruby-007` |
| **RubyExpressiveSyntaxDetector** | Flags non-idiomatic control flow like C-style ``for`` loops and ``unless !`` | `ruby-010` |

### Readability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RubyMethodChainDetector** | Detects excessively long method chains that reduce readability | `ruby-006` |
| **RubyMethodNamingDetector** | Flags boolean-style methods that lack the conventional trailing ``?`` | `ruby-005` |

### Structure

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **RubyGuardClauseDetector** | Detects methods that could benefit from guard clauses to reduce nesting | `ruby-008` |


??? example "Principle → Detector Wiring"
    ```mermaid
    graph LR
    ruby_001["ruby-001<br/>Convention over configuration"]
    ruby_002["ruby-002<br/>DRY (Don't Repeat Yourself)"]
    ruby_003["ruby-003<br/>Prefer blocks over lambdas/procs"]
    ruby_004["ruby-004<br/>Avoid monkey-patching core classes"]
    ruby_005["ruby-005<br/>Use meaningful method names with ?/! con..."]
    ruby_006["ruby-006<br/>Keep method chains readable"]
    ruby_007["ruby-007<br/>Prefer symbols over strings for keys"]
    ruby_008["ruby-008<br/>Use guard clauses"]
    ruby_009["ruby-009<br/>Avoid needless metaprogramming"]
    ruby_010["ruby-010<br/>Use Ruby's expressive syntax"]
    ruby_011["ruby-011<br/>Prefer fail over raise for exceptions"]
    det_RubyBlockPreferenceDetector["RubyBlockPreferenceDetector"]
    ruby_003 --> det_RubyBlockPreferenceDetector
    det_RubyDryDetector["RubyDryDetector"]
    ruby_002 --> det_RubyDryDetector
    det_RubyExpressiveSyntaxDetector["RubyExpressiveSyntaxDetector"]
    ruby_010 --> det_RubyExpressiveSyntaxDetector
    det_RubyGuardClauseDetector["RubyGuardClauseDetector"]
    ruby_008 --> det_RubyGuardClauseDetector
    det_RubyMetaprogrammingDetector["RubyMetaprogrammingDetector"]
    ruby_009 --> det_RubyMetaprogrammingDetector
    det_RubyMethodChainDetector["RubyMethodChainDetector"]
    ruby_006 --> det_RubyMethodChainDetector
    det_RubyMethodNamingDetector["RubyMethodNamingDetector"]
    ruby_005 --> det_RubyMethodNamingDetector
    det_RubyMonkeyPatchDetector["RubyMonkeyPatchDetector"]
    ruby_004 --> det_RubyMonkeyPatchDetector
    det_RubyNamingConventionDetector["RubyNamingConventionDetector"]
    ruby_001 --> det_RubyNamingConventionDetector
    det_RubyPreferFailDetector["RubyPreferFailDetector"]
    ruby_011 --> det_RubyPreferFailDetector
    det_RubySymbolKeysDetector["RubySymbolKeysDetector"]
    ruby_007 --> det_RubySymbolKeysDetector
    classDef principle fill:#4051b5,color:#fff,stroke:none
    classDef detector fill:#26a269,color:#fff,stroke:none
    class ruby_001 principle
    class ruby_002 principle
    class ruby_003 principle
    class ruby_004 principle
    class ruby_005 principle
    class ruby_006 principle
    class ruby_007 principle
    class ruby_008 principle
    class ruby_009 principle
    class ruby_010 principle
    class ruby_011 principle
    class det_RubyBlockPreferenceDetector detector
    class det_RubyDryDetector detector
    class det_RubyExpressiveSyntaxDetector detector
    class det_RubyGuardClauseDetector detector
    class det_RubyMetaprogrammingDetector detector
    class det_RubyMethodChainDetector detector
    class det_RubyMethodNamingDetector detector
    class det_RubyMonkeyPatchDetector detector
    class det_RubyNamingConventionDetector detector
    class det_RubyPreferFailDetector detector
    class det_RubySymbolKeysDetector detector
    ```

## Configuration

```yaml
languages:
  ruby:
    enabled: true
    pipeline:
      - type: ruby-method-chain
        max_method_chain_length: 4
```


## See Also

- [Python](python.md) — Dynamic language with similar expressiveness goals
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
