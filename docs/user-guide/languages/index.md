---
title: Languages
description: Supported languages, maturity tiers, zen principles, and detector coverage across all supported languages.
icon: material/translate
tags:
  - CLI
  - Configuration
---

# Languages

Every language has its own philosophy — its own sense of what "good code" means. MCP Zen of Languages encodes these philosophies as **zen principles**: opinionated, idiomatic best practices drawn from each language's community wisdom. Each principle maps to one or more **detectors** that find violations in your code.

## At a Glance

| Language | Principles | Detectors | Parser | Philosophy Origin |
|----------|:----------:|:---------:|--------|-------------------|
| [Python](python.md) | 12 | 23 | AST | [PEP 20 - The Zen of Python](https://peps.python.org/pep-0020/) |
| [TypeScript](typescript.md) | 10 | 10 | Regex | [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html) |
| [Rust](rust.md) | 12 | 13 | Regex | [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/) |
| [Go](go.md) | 12 | 12 | Regex | [Effective Go](https://go.dev/doc/effective_go) |
| [JavaScript](javascript.md) | 11 | 11 | Regex | [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript) |
| [Bash](bash.md) | 14 | 14 | Regex | [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) |
| [PowerShell](powershell.md) | 15 | 15 | Regex | [PoshCode Style Guide](https://github.com/PoshCode/PowerShellPracticeAndStyle) |
| [Ruby](ruby.md) | 11 | 11 | Regex | [Ruby Style Guide](https://rubystyle.guide/) |
| [C++](cpp.md) | 13 | 13 | Regex | [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) |
| [C#](csharp.md) | 13 | 13 | Regex | [C# Coding Conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions) |
| [Config formats](config-formats.md) | 29 | 29 | Regex | JSON (7), TOML (8), XML (6), YAML (8) |
| **Total** | **152** | **164** | | |

## Maturity Tiers

<div class="grid cards" markdown>

-   :material-check-all:{ .lg .middle } **Full Analysis**

    ---

    AST parsing, cyclomatic complexity, dependency graphs, maintainability index. The deepest analysis available.

    **Python**

-   :material-shield-check:{ .lg .middle } **Rule-Driven**

    ---

    Dedicated detectors with regex-based pattern matching. Each rule has its own detector class with configurable thresholds.

    **TypeScript · Rust · Go · JavaScript · Bash · PowerShell · Ruby · C++ · C#**

-   :material-file-cog:{ .lg .middle } **Config Validation**

    ---

    Schema and structure-focused detectors for data formats. Checks consistency, naming conventions, and format-specific best practices.

    **JSON · TOML · XML · YAML**

</div>

!!! info "All tiers use real detectors"
    Every language listed above has **fully implemented detectors** — there are no stubs or placeholders. The tier difference reflects parser depth (AST vs regex), not implementation completeness.

## How Principles Work

Each zen principle has four key attributes:

- **Rule ID** — A stable identifier like `python-003` or `rust-008` used in configuration and reports
- **Category** — Groups related principles (e.g., `ERROR_HANDLING`, `TYPE_SAFETY`, `IDIOMS`)
- **Severity** — A 1-10 score indicating how critical violations are (9-10 = critical, 1-3 = informational)
- **Detectors** — One or more detector classes that find violations of this principle in your code

You can tune severity thresholds and detector parameters per-language in your [`zen-config.yaml`](../configuration.md).

## Choosing Your Starting Language

=== "Already using Python?"
    Start with [Python](python.md) — it has the deepest analysis (AST parsing, cyclomatic complexity, dependency graphs) and detectors covering everything from naming style to god classes.

=== "TypeScript or JavaScript project?"
    Start with [TypeScript](typescript.md) for type-safety focus, or [JavaScript](javascript.md) for modern patterns. Both detect common pitfalls in frontend and Node.js codebases.

=== "Systems programming?"
    [Rust](rust.md) focuses on ownership and safety idioms. [C++](cpp.md) enforces modern C++ practices (smart pointers, RAII, const-correctness). [Go](go.md) encodes Effective Go principles.

=== "Scripting and automation?"
    [Bash](bash.md) and [PowerShell](powershell.md) catch the shell-scripting antipatterns that cause outages — unquoted variables, missing error handling, eval injection.

=== "Config files?"
    The [config formats](config-formats.md) page covers JSON, TOML, XML, and YAML — consistency checks, naming conventions, and format-specific best practices.

## Programmatic Access

::: mcp_zen_of_languages.rules.get_all_languages

::: mcp_zen_of_languages.rules.get_language_zen
