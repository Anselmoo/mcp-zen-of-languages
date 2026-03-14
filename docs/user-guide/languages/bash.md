---
title: Bash
description: "14 zen principles enforced by 14 detectors: Shell Scripting Best Practices."
icon: material/console
tags:
  - Bash
---

# Bash

Shell scripts are the glue of infrastructure — and the source of some of the most insidious production bugs. An unquoted variable, a missing `set -e`, a rogue `eval` — these cause outages. These **14 principles** encode defensive shell scripting practices from the [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) and [ShellCheck](https://www.shellcheck.net/) community.

## Optional External Tool Augmentation

!!! info "Consent-first external tooling"
    External tool execution is optional and disabled by default. Use
    `--enable-external-tools` (CLI) or `enable_external_tools=true` (MCP)
    to opt in. Missing tools should return recommendations; no automatic
    installs occur during analysis.

| Tool | Default invocation | Output |
|------|---------------------|--------|
| `shellcheck` | `shellcheck - -f json` | JSON |



## Zen Principles

14 principles across 10 categories, drawn from [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html).

<div class="grid" markdown>

:material-tag-outline: **Correctness** · 2 principles
:material-tag-outline: **Error Handling** · 2 principles
:material-tag-outline: **Idioms** · 1 principle
:material-tag-outline: **Immutability** · 1 principle
:material-tag-outline: **Organization** · 1 principle
:material-tag-outline: **Readability** · 2 principles
:material-tag-outline: **Robustness** · 2 principles
:material-tag-outline: **Scope** · 1 principle
:material-tag-outline: **Security** · 1 principle
:material-tag-outline: **Usability** · 1 principle

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `bash-001` | Always use set -euo pipefail | Error Handling | 9 | `ZEN-FAIL-FAST` |
| `bash-002` | Quote all variables | Correctness | 8 | `ZEN-EXPLICIT-INTENT` |
| `bash-003` | Use [[ ]] over [ ] | Idioms | 7 | `ZEN-RIGHT-ABSTRACTION` |
| `bash-004` | Use $() over backticks | Readability | 6 | `ZEN-UNAMBIGUOUS-NAME`, `ZEN-RETURN-EARLY` |
| `bash-005` | Check command exit codes | Error Handling | 8 | `ZEN-FAIL-FAST` |
| `bash-006` | Use functions for reusable code | Organization | 6 | `ZEN-STRICT-FENCES` |
| `bash-007` | Use local variables in functions | Scope | 7 | `ZEN-STRICT-FENCES` |
| `bash-008` | Avoid eval | Security | 9 | `ZEN-STRICT-FENCES` |
| `bash-009` | Use readonly for constants | Immutability | 6 | `ZEN-VISIBLE-STATE`, `ZEN-EXPLICIT-INTENT` |
| `bash-010` | Validate input and arguments | Robustness | 8 | `ZEN-FAIL-FAST` |
| `bash-011` | Use meaningful variable names | Readability | 7 | `ZEN-UNAMBIGUOUS-NAME` |
| `bash-012` | Handle signals properly | Robustness | 7 | `ZEN-FAIL-FAST` |
| `bash-013` | Use arrays instead of string splitting | Correctness | 7 | `ZEN-EXPLICIT-INTENT` |
| `bash-014` | Include usage information | Usability | 6 | `ZEN-UNAMBIGUOUS-NAME` |

??? info "`bash-001` — Always use set -euo pipefail"
    **Enable strict error handling at script start**

    **Universal Dogmas:** `ZEN-FAIL-FAST`
    **Common Violations:**

    - Scripts without set -e
    - Not using set -u for undefined variables
    - Not using set -o pipefail
    - Missing error handling

    **Detectable Patterns:**

    - `#!/bin/bash without set -euo pipefail`

    !!! tip "Recommended Fix"
        set -euo pipefail at beginning of script

??? info "`bash-002` — Quote all variables"
    **Always quote variable expansions to prevent word splitting**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Unquoted $variable
    - Unquoted ${variable}
    - Unquoted command substitutions
    - Unquoted array expansions

    **Detectable Patterns:**

    - `$variable without quotes`
    - `$(command) without quotes`

    !!! tip "Recommended Fix"
        "$variable" or "${variable}"

??? info "`bash-003` — Use [[ ]] over [ ]"
    **Prefer [[ ]] for conditional expressions**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Using [ ] for tests
    - Not using [[ ]] for string comparisons
    - Using test command

    **Detectable Patterns:**

    - `[ condition ]`
    - `test condition`

    !!! tip "Recommended Fix"
        [[ condition ]]

??? info "`bash-004` — Use $() over backticks"
    **Prefer $() for command substitution**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`, `ZEN-RETURN-EARLY`
    **Common Violations:**

    - Using backticks `command`
    - Nested backticks
    - Hard to read command substitution

    **Detectable Patterns:**

    - ``command``

    !!! tip "Recommended Fix"
        $(command)

??? info "`bash-005` — Check command exit codes"
    **Always verify command success**

    **Universal Dogmas:** `ZEN-FAIL-FAST`
    **Common Violations:**

    - Not checking $? after commands
    - Ignoring command failures
    - Not using || or && for error handling

    **Detectable Patterns:**

    - `!$?`

    !!! tip "Recommended Fix"
        if ! command; then ... fi or command || handle_error

??? info "`bash-006` — Use functions for reusable code"
    **Extract repeated code into functions**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`
    **Common Violations:**

    - Duplicated code blocks
    - Long scripts without functions
    - No code organization

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_script_length_without_functions` | `50` |

??? info "`bash-007` — Use local variables in functions"
    **Declare function variables as local**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`
    **Common Violations:**

    - Function variables without local
    - Global variable pollution
    - Variable scope leakage

    **Detectable Patterns:**

    - `!local `

??? info "`bash-008` — Avoid eval"
    **Don't use eval except when absolutely necessary**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`
    **Common Violations:**

    - eval usage
    - Constructing code from user input
    - Security vulnerabilities

    **Detectable Patterns:**

    - `eval`

??? info "`bash-009` — Use readonly for constants"
    **Mark constants as readonly**

    **Universal Dogmas:** `ZEN-VISIBLE-STATE`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Constants without readonly
    - Magic values not in constants
    - Mutable configuration values

    **Detectable Patterns:**

    - `!readonly `

??? info "`bash-010` — Validate input and arguments"
    **Check script arguments and user input**

    **Universal Dogmas:** `ZEN-FAIL-FAST`
    **Common Violations:**

    - No argument count validation
    - Not checking for required arguments
    - No input sanitization
    - Missing usage information

    **Detectable Patterns:**

    - `!$#`

??? info "`bash-011` — Use meaningful variable names"
    **Avoid single-letter or cryptic names**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Single letter variables (except i, j in loops)
    - Abbreviations without context
    - Unclear variable names

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `min_variable_name_length` | `3` |

??? info "`bash-012` — Handle signals properly"
    **Use trap for cleanup and signal handling**

    **Universal Dogmas:** `ZEN-FAIL-FAST`
    **Common Violations:**

    - No trap for cleanup
    - Temporary files not cleaned up
    - Missing EXIT trap
    - No interrupt handling

    **Detectable Patterns:**

    - `!trap `

    !!! tip "Recommended Fix"
        trap cleanup EXIT INT TERM

??? info "`bash-013` — Use arrays instead of string splitting"
    **Store lists in arrays, not space-separated strings**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Splitting strings on spaces
    - Not using arrays for lists
    - Improper iteration over items

    **Detectable Patterns:**

    - `IFS=`
    - `for item in $`

    !!! tip "Recommended Fix"
        array=(item1 item2); for item in "${array[@]}"

??? info "`bash-014` — Include usage information"
    **Provide help text and usage examples**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Scripts without usage function
    - No help flag (-h/--help)
    - Missing documentation

    **Detectable Patterns:**

    - `!usage`


## Detector Catalog

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **BashQuoteVariablesDetector** | Detect unquoted variable expansions that cause word-splitting bugs | `bash-002` |
| **BashArrayUsageDetector** | Detect IFS-based string splitting used instead of proper Bash arrays | `bash-013` |

### Error Handling

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **BashStrictModeDetector** | Detect scripts missing the unofficial Bash strict mode header | `bash-001` |
| **BashExitCodeChecksDetector** | Detect external commands whose exit codes are silently ignored | `bash-005` |

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **BashDoubleBracketsDetector** | Detect single-bracket ``[ ]`` test expressions that should use ``[[ ]]`` | `bash-003` |

### Immutability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **BashReadonlyConstantsDetector** | Detect ALL_CAPS assignments that are not declared ``readonly`` | `bash-009` |

### Organization

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **BashFunctionUsageDetector** | Detect long scripts that lack function decomposition | `bash-006` |

### Readability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **BashCommandSubstitutionDetector** | Detect legacy backtick command substitution syntax | `bash-004` |
| **BashMeaningfulNamesDetector** | Detect overly short or cryptic variable names in shell scripts | `bash-011` |

### Robustness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **BashArgumentValidationDetector** | Detect scripts that use positional arguments without validation | `bash-010` |
| **BashSignalHandlingDetector** | Detect scripts that lack ``trap`` handlers for cleanup on exit or signals | `bash-012` |

### Scope

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **BashLocalVariablesDetector** | Detect function-scoped variables missing the ``local`` keyword | `bash-007` |

### Security

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **BashEvalUsageDetector** | Detect usage of ``eval`` which enables code injection attacks | `bash-008` |

### Usability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **BashUsageInfoDetector** | Detect scripts lacking a ``usage`` function or ``--help``/``-h`` flag | `bash-014` |


??? example "Principle → Detector Wiring"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    bash_001["bash-001<br/>Always use set -euo pipef..."]
    bash_002["bash-002<br/>Quote all variables"]
    bash_003["bash-003<br/>Use [[ ]] over [ ]"]
    bash_004["bash-004<br/>Use $() over backticks"]
    bash_005["bash-005<br/>Check command exit codes"]
    bash_006["bash-006<br/>Use functions for reusabl..."]
    bash_007["bash-007<br/>Use local variables in fu..."]
    bash_008["bash-008<br/>Avoid eval"]
    bash_009["bash-009<br/>Use readonly for constant..."]
    bash_010["bash-010<br/>Validate input and argume..."]
    bash_011["bash-011<br/>Use meaningful variable n..."]
    bash_012["bash-012<br/>Handle signals properly"]
    bash_013["bash-013<br/>Use arrays instead of str..."]
    bash_014["bash-014<br/>Include usage information"]
    det_BashArgumentValidationDetector["Bash Argument<br/>Validation"]
    bash_010 --> det_BashArgumentValidationDetector
    det_BashArrayUsageDetector["Bash Array<br/>Usage"]
    bash_013 --> det_BashArrayUsageDetector
    det_BashCommandSubstitutionDetector["Bash Command<br/>Substitution"]
    bash_004 --> det_BashCommandSubstitutionDetector
    det_BashDoubleBracketsDetector["Bash Double<br/>Brackets"]
    bash_003 --> det_BashDoubleBracketsDetector
    det_BashEvalUsageDetector["Bash Eval<br/>Usage"]
    bash_008 --> det_BashEvalUsageDetector
    det_BashExitCodeChecksDetector["Bash Exit<br/>Code Checks"]
    bash_005 --> det_BashExitCodeChecksDetector
    det_BashFunctionUsageDetector["Bash Function<br/>Usage"]
    bash_006 --> det_BashFunctionUsageDetector
    det_BashLocalVariablesDetector["Bash Local<br/>Variables"]
    bash_007 --> det_BashLocalVariablesDetector
    det_BashMeaningfulNamesDetector["Bash Meaningful<br/>Names"]
    bash_011 --> det_BashMeaningfulNamesDetector
    det_BashQuoteVariablesDetector["Bash Quote<br/>Variables"]
    bash_002 --> det_BashQuoteVariablesDetector
    det_BashReadonlyConstantsDetector["Bash Readonly<br/>Constants"]
    bash_009 --> det_BashReadonlyConstantsDetector
    det_BashSignalHandlingDetector["Bash Signal<br/>Handling"]
    bash_012 --> det_BashSignalHandlingDetector
    det_BashStrictModeDetector["Bash Strict<br/>Mode"]
    bash_001 --> det_BashStrictModeDetector
    det_BashUsageInfoDetector["Bash Usage<br/>Info"]
    bash_014 --> det_BashUsageInfoDetector
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
        class det_01["Bash Argument Validation"]
        ViolationDetector <|-- det_01
        class det_02["Bash Array Usage"]
        ViolationDetector <|-- det_02
        class det_03["Bash Command Substitution"]
        ViolationDetector <|-- det_03
        class det_04["Bash Double Brackets"]
        ViolationDetector <|-- det_04
        class det_05["Bash Eval Usage"]
        ViolationDetector <|-- det_05
        class det_06["Bash Exit Code Checks"]
        ViolationDetector <|-- det_06
        class det_07["Bash Function Usage"]
        ViolationDetector <|-- det_07
        class det_08["Bash Local Variables"]
        ViolationDetector <|-- det_08
        class det_09["Bash Meaningful Names"]
        ViolationDetector <|-- det_09
        class det_10["Bash Quote Variables"]
        ViolationDetector <|-- det_10
        class det_11["Bash Readonly Constants"]
        ViolationDetector <|-- det_11
        class det_12["Bash Signal Handling"]
        ViolationDetector <|-- det_12
        class det_13["Bash Strict Mode"]
        ViolationDetector <|-- det_13
        class det_14["Bash Usage Info"]
        ViolationDetector <|-- det_14
    ```

??? example "Analysis Pipeline"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 50, "rankSpacing": 70}}}%%
    flowchart TD
    Source(["Source Code"]) --> Parse["Parse & Tokenize"]
    Parse --> Metrics["Compute Metrics"]
    Metrics --> Pipeline{"14 Detectors"}
    Pipeline --> Collect["Aggregate Violations"]
    Collect --> Result(["AnalysisResult<br/>14 principles"])
    ```

??? example "Analysis States"
    ```mermaid
    %%{init: {"theme": "base"}}%%
    stateDiagram-v2
        [*] --> Ready
        Ready --> Parsing : analyze(code)
        Parsing --> Computing : AST ready
        Computing --> Detecting : metrics ready
        Detecting --> Reporting : 14 detectors run
        Reporting --> [*] : AnalysisResult
        Parsing --> Reporting : parse error (best-effort)
    ```

## Configuration

```yaml
languages:
  bash:
    enabled: true
    pipeline:
```


## See Also

- [PowerShell](powershell.md) — Object-pipeline shell with different idioms
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
