---
title: PowerShell
description: "15 zen principles enforced by 15 detectors: PowerShell Best Practices and Style Guide."
icon: material/console-line
tags:
  - PowerShell
---

# PowerShell

PowerShell is a shell built around objects, pipelines, and cmdlet conventions. Code that ignores these conventions — using aliases in scripts, returning formatted strings, skipping `-WhatIf` support — breaks the pipeline and frustrates users. These **15 principles** come from the [PowerShell Best Practices](https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/cmdlet-development-guidelines) and the community's hard-won experience.

## Optional External Tool Augmentation

!!! info "Consent-first external tooling"
    External tool execution is optional and disabled by default. Use
    `--enable-external-tools` (CLI) or `enable_external_tools=true` (MCP)
    to opt in. Missing tools should return recommendations; no automatic
    installs occur during analysis.

| Tool | Default invocation | Output |
|------|---------------------|--------|
| `pwsh` | `pwsh -Command Invoke-ScriptAnalyzer -ScriptDefinition $input` | Text / structured stderr |



## Zen Principles

15 principles across 12 categories, drawn from [PoshCode Style Guide](https://github.com/PoshCode/PowerShellPracticeAndStyle).

<div class="grid" markdown>

:material-tag-outline: **Clarity** · 1 principle
:material-tag-outline: **Correctness** · 1 principle
:material-tag-outline: **Debugging** · 1 principle
:material-tag-outline: **Design** · 2 principles
:material-tag-outline: **Documentation** · 1 principle
:material-tag-outline: **Error Handling** · 1 principle
:material-tag-outline: **Idioms** · 1 principle
:material-tag-outline: **Naming** · 2 principles
:material-tag-outline: **Readability** · 2 principles
:material-tag-outline: **Robustness** · 1 principle
:material-tag-outline: **Safety** · 1 principle
:material-tag-outline: **Scope** · 1 principle

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `ps-001` | Use approved verbs | Naming | 7 | `ZEN-UNAMBIGUOUS-NAME` |
| `ps-002` | Use proper error handling | Error Handling | 9 | `ZEN-FAIL-FAST` |
| `ps-003` | Use cmdlet binding and parameters | Design | 8 | `ZEN-RIGHT-ABSTRACTION` |
| `ps-004` | Use PascalCase for function names | Naming | 7 | `ZEN-UNAMBIGUOUS-NAME` |
| `ps-005` | Use Write-Verbose and Write-Debug | Debugging | 6 | `ZEN-EXPLICIT-INTENT` |
| `ps-006` | Avoid positional parameters | Readability | 7 | `ZEN-UNAMBIGUOUS-NAME` |
| `ps-007` | Use pipeline properly | Idioms | 7 | `ZEN-RIGHT-ABSTRACTION` |
| `ps-008` | Use -WhatIf and -Confirm support | Safety | 8 | `ZEN-FAIL-FAST` |
| `ps-009` | Use splatting for readability | Readability | 6 | `ZEN-UNAMBIGUOUS-NAME` |
| `ps-010` | Validate parameters properly | Robustness | 8 | `ZEN-FAIL-FAST` |
| `ps-011` | Use comment-based help | Documentation | 7 | `ZEN-UNAMBIGUOUS-NAME` |
| `ps-012` | Avoid aliases in scripts | Clarity | 6 | `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME` |
| `ps-013` | Return objects, not formatted text | Design | 8 | `ZEN-RIGHT-ABSTRACTION` |
| `ps-014` | Use script scope carefully | Scope | 7 | `ZEN-STRICT-FENCES`, `ZEN-EXPLICIT-INTENT` |
| `ps-015` | Handle null values explicitly | Correctness | 7 | `ZEN-EXPLICIT-INTENT`, `ZEN-FAIL-FAST` |

??? info "`ps-001` — Use approved verbs"
    **Function names should use approved PowerShell verbs**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Non-standard verbs in function names
    - Custom verbs without approval
    - Unclear function naming

    **Detectable Patterns:**

    - `function CustomVerb-Noun`

    !!! tip "Recommended Fix"
        Get-Verb to see approved verbs, use Verb-Noun pattern

??? info "`ps-002` — Use proper error handling"
    **Use try/catch/finally and -ErrorAction**

    **Universal Dogmas:** `ZEN-FAIL-FAST`
    **Common Violations:**

    - Commands without error handling
    - Not using try/catch
    - Ignoring $Error variable
    - Silent failures

    **Detectable Patterns:**

    - `command without try/catch`
    - `-ErrorAction SilentlyContinue abuse`

??? info "`ps-003` — Use cmdlet binding and parameters"
    **Functions should use [CmdletBinding()] and proper parameters**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Functions without [CmdletBinding()]
    - Using $args instead of parameters
    - Missing parameter validation
    - No parameter attributes

    **Detectable Patterns:**

    - `!CmdletBinding`

    !!! tip "Recommended Fix"
        [CmdletBinding()] with [Parameter()] attributes

??? info "`ps-004` — Use PascalCase for function names"
    **Follow PowerShell naming conventions**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - camelCase function names
    - snake_case in PowerShell
    - All lowercase names
    - Inconsistent casing

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `naming_convention` | `PascalCase for functions, camelCase for variables` |

??? info "`ps-005` — Use Write-Verbose and Write-Debug"
    **Use proper output streams for logging**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Using Write-Host for logging
    - Not using Write-Verbose
    - No debug output
    - Mixing output streams

    **Detectable Patterns:**

    - `Write-Host for logging`

    !!! tip "Recommended Fix"
        Write-Verbose, Write-Debug, Write-Information

??? info "`ps-006` — Avoid positional parameters"
    **Always use named parameters in scripts**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Positional parameter usage
    - Unclear command calls
    - Not using -ParameterName syntax

    **Detectable Patterns:**

    - `$args`

    !!! tip "Recommended Fix"
        Get-ChildItem -Path $path -Filter $filter

??? info "`ps-007` — Use pipeline properly"
    **Leverage PowerShell pipeline for object processing**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - ForEach-Object loops instead of pipeline
    - Not using pipeline when appropriate
    - Breaking pipeline chain unnecessarily

    **Detectable Patterns:**

    - `!|`

    !!! tip "Recommended Fix"
        Get-Process | Where-Object { $_.CPU -gt 10 }

??? info "`ps-008` — Use -WhatIf and -Confirm support"
    **Implement ShouldProcess for destructive operations**

    **Universal Dogmas:** `ZEN-FAIL-FAST`
    **Common Violations:**

    - Destructive commands without -WhatIf
    - Not using ShouldProcess
    - No user confirmation for dangerous operations

    **Detectable Patterns:**

    - `!WhatIf`

    !!! tip "Recommended Fix"
        [CmdletBinding(SupportsShouldProcess)]

??? info "`ps-009` — Use splatting for readability"
    **Use splatting for multiple parameters**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Long parameter lists inline
    - Not using @splat syntax
    - Unreadable command calls

    **Detectable Patterns:**

    - `!@{`

    !!! tip "Recommended Fix"
        $params = @{...}; Command @params

??? info "`ps-010` — Validate parameters properly"
    **Use parameter validation attributes**

    **Universal Dogmas:** `ZEN-FAIL-FAST`
    **Common Violations:**

    - No [ValidateNotNull()]
    - No [ValidateSet()]
    - Missing [ValidateRange()]
    - No input validation

    **Detectable Patterns:**

    - `![Validate`

    !!! tip "Recommended Fix"
        [ValidateNotNullOrEmpty()], [ValidateSet('value1','value2')]

??? info "`ps-011` — Use comment-based help"
    **Include .SYNOPSIS, .DESCRIPTION, .EXAMPLE**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Functions without help comments
    - Missing .SYNOPSIS
    - No usage examples
    - Incomplete documentation

    **Detectable Patterns:**

    - `!.SYNOPSIS`

??? info "`ps-012` — Avoid aliases in scripts"
    **Use full cmdlet names, not aliases**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Using aliases like 'gci' instead of Get-ChildItem
    - Using '%' instead of ForEach-Object
    - Using '?' instead of Where-Object
    - Unclear abbreviated commands

    **Detectable Patterns:**

    - `gci, ls, dir, cat, etc.`

    !!! tip "Recommended Fix"
        Full cmdlet names

??? info "`ps-013` — Return objects, not formatted text"
    **Return structured objects for pipeline compatibility**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Returning formatted strings
    - Using Format-Table in functions
    - Breaking pipeline with text output
    - Not using PSCustomObject

    **Detectable Patterns:**

    - `Format-Table`
    - `Out-String`

    !!! tip "Recommended Fix"
        [PSCustomObject]@{Property='Value'}

??? info "`ps-014` — Use script scope carefully"
    **Be explicit about variable scope**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Unintended global variables
    - Not using $script: or $global:
    - Scope pollution
    - Variable leakage

    **Detectable Patterns:**

    - `$global:`
    - `$script:`

??? info "`ps-015` — Handle null values explicitly"
    **Check for null before operations**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-FAIL-FAST`
    **Common Violations:**

    - Not checking for $null
    - NullReferenceException in scripts
    - Assuming objects exist
    - No null coalescing

    **Detectable Patterns:**

    - `!$null`

    !!! tip "Recommended Fix"
        if ($null -ne $variable) or $variable ?? 'default'


## Detector Catalog

### Clarity

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **PowerShellAliasUsageDetector** | Detect built-in aliases (``gci``, ``ls``, ``%``, ``?``) used in scripts | `ps-012` |

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **PowerShellNullHandlingDetector** | Detect functions and param blocks that never check for ``$null`` | `ps-015` |

### Debugging

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **PowerShellVerboseDebugDetector** | Detect ``Write-Host`` calls that should use ``Write-Verbose`` or ``Write-Debug`` | `ps-005` |

### Design

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **PowerShellCmdletBindingDetector** | Detect advanced functions missing ``[CmdletBinding()]`` and ``param()`` | `ps-003` |
| **PowerShellReturnObjectsDetector** | Detect functions that return formatted text instead of objects | `ps-013` |

### Documentation

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **PowerShellCommentHelpDetector** | Detect functions missing comment-based help with ``.SYNOPSIS`` | `ps-011` |

### Error Handling

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **PowerShellErrorHandlingDetector** | Detect scripts that lack any form of error handling | `ps-002` |

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **PowerShellPipelineUsageDetector** | Detect ``ForEach-Object`` or ``foreach`` loops that should use pipelines | `ps-007` |

### Naming

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **PowerShellApprovedVerbDetector** | Detect function names that use unapproved PowerShell verbs | `ps-001` |
| **PowerShellPascalCaseDetector** | Detect function names that violate PascalCase naming conventions | `ps-004` |

### Readability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **PowerShellPositionalParamsDetector** | Detect reliance on ``$args`` for positional parameter access | `ps-006` |
| **PowerShellSplattingDetector** | Detect cmdlet calls with many inline parameters that should use splatting | `ps-009` |

### Robustness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **PowerShellParameterValidationDetector** | Detect ``param()`` blocks that lack ``[Validate*]`` attributes | `ps-010` |

### Safety

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **PowerShellShouldProcessDetector** | Detect destructive cmdlet verbs missing ``SupportsShouldProcess`` | `ps-008` |

### Scope

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **PowerShellScopeUsageDetector** | Detect explicit ``$global:`` and ``$script:`` scope modifiers | `ps-014` |


??? example "Principle → Detector Wiring"
    ```mermaid
%%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    ps_001["ps-001<br/>Use approved verbs"]
    ps_002["ps-002<br/>Use proper error handling"]
    ps_003["ps-003<br/>Use cmdlet binding and pa..."]
    ps_004["ps-004<br/>Use PascalCase for functi..."]
    ps_005["ps-005<br/>Use Write-Verbose and Wri..."]
    ps_006["ps-006<br/>Avoid positional paramete..."]
    ps_007["ps-007<br/>Use pipeline properly"]
    ps_008["ps-008<br/>Use -WhatIf and -Confirm ..."]
    ps_009["ps-009<br/>Use splatting for readabi..."]
    ps_010["ps-010<br/>Validate parameters prope..."]
    ps_011["ps-011<br/>Use comment-based help"]
    ps_012["ps-012<br/>Avoid aliases in scripts"]
    ps_013["ps-013<br/>Return objects, not forma..."]
    ps_014["ps-014<br/>Use script scope carefull..."]
    ps_015["ps-015<br/>Handle null values explic..."]
    det_PowerShellAliasUsageDetector["PowerShellAliasUsageDetector"]
    ps_012 --> det_PowerShellAliasUsageDetector
    det_PowerShellApprovedVerbDetector["PowerShellApprovedVerbDetector"]
    ps_001 --> det_PowerShellApprovedVerbDetector
    det_PowerShellCmdletBindingDetector["PowerShellCmdletBindingDetector"]
    ps_003 --> det_PowerShellCmdletBindingDetector
    det_PowerShellCommentHelpDetector["PowerShellCommentHelpDetector"]
    ps_011 --> det_PowerShellCommentHelpDetector
    det_PowerShellErrorHandlingDetector["PowerShellErrorHandlingDetector"]
    ps_002 --> det_PowerShellErrorHandlingDetector
    det_PowerShellNullHandlingDetector["PowerShellNullHandlingDetector"]
    ps_015 --> det_PowerShellNullHandlingDetector
    det_PowerShellParameterValidationDetector["PowerShellParameterValidationDetector"]
    ps_010 --> det_PowerShellParameterValidationDetector
    det_PowerShellPascalCaseDetector["PowerShellPascalCaseDetector"]
    ps_004 --> det_PowerShellPascalCaseDetector
    det_PowerShellPipelineUsageDetector["PowerShellPipelineUsageDetector"]
    ps_007 --> det_PowerShellPipelineUsageDetector
    det_PowerShellPositionalParamsDetector["PowerShellPositionalParamsDetector"]
    ps_006 --> det_PowerShellPositionalParamsDetector
    det_PowerShellReturnObjectsDetector["PowerShellReturnObjectsDetector"]
    ps_013 --> det_PowerShellReturnObjectsDetector
    det_PowerShellScopeUsageDetector["PowerShellScopeUsageDetector"]
    ps_014 --> det_PowerShellScopeUsageDetector
    det_PowerShellShouldProcessDetector["PowerShellShouldProcessDetector"]
    ps_008 --> det_PowerShellShouldProcessDetector
    det_PowerShellSplattingDetector["PowerShellSplattingDetector"]
    ps_009 --> det_PowerShellSplattingDetector
    det_PowerShellVerboseDebugDetector["PowerShellVerboseDebugDetector"]
    ps_005 --> det_PowerShellVerboseDebugDetector
    classDef principle fill:#4051b5,color:#ffffff,stroke:#4051b5,stroke-width:2px
    classDef detector fill:#26a269,color:#ffffff,stroke:#26a269,stroke-width:2px
    class ps_001 principle
    class ps_002 principle
    class ps_003 principle
    class ps_004 principle
    class ps_005 principle
    class ps_006 principle
    class ps_007 principle
    class ps_008 principle
    class ps_009 principle
    class ps_010 principle
    class ps_011 principle
    class ps_012 principle
    class ps_013 principle
    class ps_014 principle
    class ps_015 principle
    class det_PowerShellAliasUsageDetector detector
    class det_PowerShellApprovedVerbDetector detector
    class det_PowerShellCmdletBindingDetector detector
    class det_PowerShellCommentHelpDetector detector
    class det_PowerShellErrorHandlingDetector detector
    class det_PowerShellNullHandlingDetector detector
    class det_PowerShellParameterValidationDetector detector
    class det_PowerShellPascalCaseDetector detector
    class det_PowerShellPipelineUsageDetector detector
    class det_PowerShellPositionalParamsDetector detector
    class det_PowerShellReturnObjectsDetector detector
    class det_PowerShellScopeUsageDetector detector
    class det_PowerShellShouldProcessDetector detector
    class det_PowerShellSplattingDetector detector
    class det_PowerShellVerboseDebugDetector detector
    ```

??? example "Detector Class Hierarchy"
    ```mermaid
%%{init: {"theme": "base"}}%%
    classDiagram
        direction TB
        class ViolationDetector {
            <<abstract>>
            +detect(context, config) list~Violation~
        }
        class PowerShellAliasUsageDetector {
            +rules "ps-012"
        }
        ViolationDetector <|-- PowerShellAliasUsageDetector
        class PowerShellApprovedVerbDetector {
            +rules "ps-001"
        }
        ViolationDetector <|-- PowerShellApprovedVerbDetector
        class PowerShellCmdletBindingDetector {
            +rules "ps-003"
        }
        ViolationDetector <|-- PowerShellCmdletBindingDetector
        class PowerShellCommentHelpDetector {
            +rules "ps-011"
        }
        ViolationDetector <|-- PowerShellCommentHelpDetector
        class PowerShellErrorHandlingDetector {
            +rules "ps-002"
        }
        ViolationDetector <|-- PowerShellErrorHandlingDetector
        class PowerShellNullHandlingDetector {
            +rules "ps-015"
        }
        ViolationDetector <|-- PowerShellNullHandlingDetector
        class PowerShellParameterValidationDetector {
            +rules "ps-010"
        }
        ViolationDetector <|-- PowerShellParameterValidationDetector
        class PowerShellPascalCaseDetector {
            +rules "ps-004"
        }
        ViolationDetector <|-- PowerShellPascalCaseDetector
        class PowerShellPipelineUsageDetector {
            +rules "ps-007"
        }
        ViolationDetector <|-- PowerShellPipelineUsageDetector
        class PowerShellPositionalParamsDetector {
            +rules "ps-006"
        }
        ViolationDetector <|-- PowerShellPositionalParamsDetector
        class PowerShellReturnObjectsDetector {
            +rules "ps-013"
        }
        ViolationDetector <|-- PowerShellReturnObjectsDetector
        class PowerShellScopeUsageDetector {
            +rules "ps-014"
        }
        ViolationDetector <|-- PowerShellScopeUsageDetector
        class PowerShellShouldProcessDetector {
            +rules "ps-008"
        }
        ViolationDetector <|-- PowerShellShouldProcessDetector
        class PowerShellSplattingDetector {
            +rules "ps-009"
        }
        ViolationDetector <|-- PowerShellSplattingDetector
        class PowerShellVerboseDebugDetector {
            +rules "ps-005"
        }
        ViolationDetector <|-- PowerShellVerboseDebugDetector
        classDef abstract fill:#4051b5,color:#ffffff,stroke:#4051b5,stroke-width:2px
        classDef detector fill:#26a269,color:#ffffff,stroke:#26a269,stroke-width:2px
        class ViolationDetector abstract
        class PowerShellAliasUsageDetector,PowerShellApprovedVerbDetector,PowerShellCmdletBindingDetector,PowerShellCommentHelpDetector,PowerShellErrorHandlingDetector,PowerShellNullHandlingDetector,PowerShellParameterValidationDetector,PowerShellPascalCaseDetector,PowerShellPipelineUsageDetector,PowerShellPositionalParamsDetector,PowerShellReturnObjectsDetector,PowerShellScopeUsageDetector,PowerShellShouldProcessDetector,PowerShellSplattingDetector,PowerShellVerboseDebugDetector detector
    ```

??? example "Analysis Pipeline"
    ```mermaid
%%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 50, "rankSpacing": 70}}}%%
    flowchart TD
    Source(["📄 Source Code"]) --> Parse["Parse & Tokenize"]
    Parse --> Metrics["Compute Metrics"]
    Metrics --> Pipeline{"15 Detectors"}
    Pipeline --> Collect["Aggregate Violations"]
    Collect --> Result(["✅ AnalysisResult · 15 principles"])

    classDef io fill:#4051b5,color:#ffffff,stroke:#4051b5,stroke-width:2px
    classDef process fill:#26a269,color:#ffffff,stroke:#26a269,stroke-width:2px
    classDef decision fill:#b55400,color:#ffffff,stroke:#b55400,stroke-width:2px
    class Source,Result io
    class Parse,Metrics,Collect process
    class Pipeline decision
    ```

??? example "Analysis States"
    ```mermaid
%%{init: {"theme": "base"}}%%
    stateDiagram-v2
        [*] --> Ready
        Ready --> Parsing : analyze(code)
        Parsing --> Computing : AST ready
        Computing --> Detecting : metrics ready
        Detecting --> Reporting : 15 detectors run
        Reporting --> [*] : AnalysisResult
        Parsing --> Reporting : parse error (best-effort)
    ```

## Configuration

```yaml
languages:
  powershell:
    enabled: true
    pipeline:
      - type: powershell_approved_verbs
        approved_verbs: ['get', 'set', 'new', 'remove', 'add', 'clear', 'start', 'stop']
```


## See Also

- [Bash](bash.md) — POSIX shell scripting counterpart
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
