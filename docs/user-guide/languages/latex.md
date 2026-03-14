---
title: LaTeX
description: "9 zen principles enforced by 9 detectors: LaTeX document quality and semantic authoring."
icon: material/math-integral
tags:
  - LaTeX
---

# LaTeX



## Optional External Tool Augmentation

!!! info "Consent-first external tooling"
    External tool execution is optional and disabled by default. Use
    `--enable-external-tools` (CLI) or `enable_external_tools=true` (MCP)
    to opt in. Missing tools should return recommendations; no automatic
    installs occur during analysis.

| Tool | Default invocation | Output |
|------|---------------------|--------|
| `chktex` | `chktex -q -v0 -` | Text / structured stderr |



## Zen Principles

9 principles across 6 categories, drawn from [LaTeX Project](https://www.latex-project.org/).

<div class="grid" markdown>

:material-tag-outline: **Architecture** · 1 principle
:material-tag-outline: **Clarity** · 1 principle
:material-tag-outline: **Consistency** · 1 principle
:material-tag-outline: **Correctness** · 3 principles
:material-tag-outline: **Documentation** · 1 principle
:material-tag-outline: **Organization** · 2 principles

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `latex-001` | Prefer \newcommand over \def | Correctness | 7 | `ZEN-EXPLICIT-INTENT` |
| `latex-002` | Keep labels and references consistent | Correctness | 8 | `ZEN-EXPLICIT-INTENT` |
| `latex-003` | Require captions in figures and tables | Documentation | 6 | `ZEN-UNAMBIGUOUS-NAME` |
| `latex-004` | Maintain bibliography hygiene | Organization | 6 | `ZEN-STRICT-FENCES` |
| `latex-005` | Avoid hardcoded absolute lengths | Consistency | 5 | `ZEN-EXPLICIT-INTENT` |
| `latex-006` | Prefer semantic emphasis commands | Clarity | 4 | `ZEN-EXPLICIT-INTENT` |
| `latex-007` | Prevent circular \input and \include chains | Architecture | 8 | `ZEN-RIGHT-ABSTRACTION` |
| `latex-008` | Declare UTF-8 encoding intent | Correctness | 5 | `ZEN-EXPLICIT-INTENT` |
| `latex-009` | Remove unused packages | Organization | 5 | `ZEN-STRICT-FENCES` |

??? info "`latex-001` — Prefer \newcommand over \def"
    **Use checked macro definitions to avoid accidental redefinitions.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Raw \def usage for user macros

??? info "`latex-002` — Keep labels and references consistent"
    **Every label should be referenced and every reference should resolve.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Unused labels or unresolved \ref/\eqref targets

??? info "`latex-003` — Require captions in figures and tables"
    **Figure and table environments should include captions for context.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Figure/table without \caption

??? info "`latex-004` — Maintain bibliography hygiene"
    **Prefer citation keys with bibliography files and avoid uncited entries.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`
    **Common Violations:**

    - Manual \bibitem blocks or uncited bibliography items

??? info "`latex-005` — Avoid hardcoded absolute lengths"
    **Prefer relative lengths such as \textwidth and \linewidth.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Absolute units like pt/cm/mm/in in layout-sensitive commands

??? info "`latex-006` — Prefer semantic emphasis commands"
    **Use semantic markup over direct visual styling commands.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - \textit or \textbf used as semantic emphasis

??? info "`latex-007` — Prevent circular \input and \include chains"
    **Included files must not create recursive include loops.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Circular \input/\include dependency

??? info "`latex-008` — Declare UTF-8 encoding intent"
    **Declare UTF-8 input encoding unless using LuaTeX/XeTeX native flow.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Missing UTF-8 encoding declaration

??? info "`latex-009` — Remove unused packages"
    **Declared packages should have commands used in the document.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`
    **Common Violations:**

    - \usepackage declarations with no usage


## Detector Catalog

### Architecture

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **LatexIncludeLoopDetector** | Detect circular include/input chains across LaTeX files | `latex-007` |

### Clarity

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **LatexSemanticMarkupDetector** | Flag visual styling commands used where semantic emphasis is preferred | `latex-006` |

### Consistency

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **LatexWidthAbstractionDetector** | Find hardcoded absolute lengths in layout-related commands | `latex-005` |

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **LatexMacroDefinitionDetector** | Detect raw ``\def`` macro declarations | `latex-001` |
| **LatexLabelRefDisciplineDetector** | Validate that labels and references are mutually consistent | `latex-002` |
| **LatexEncodingDeclarationDetector** | Require UTF-8 encoding declaration for non-LuaTeX/XeTeX documents | `latex-008` |

### Documentation

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **LatexCaptionCompletenessDetector** | Check that ``figure`` and ``table`` environments define captions | `latex-003` |

### Organization

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **LatexBibliographyHygieneDetector** | Detect manual bibliography drift and uncited entries | `latex-004` |
| **LatexUnusedPackagesDetector** | Warn about package declarations with no observable command usage | `latex-009` |


??? example "Principle → Detector Wiring"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    latex_001["latex-001<br/>Prefer \newcommand over \..."]
    latex_002["latex-002<br/>Keep labels and reference..."]
    latex_003["latex-003<br/>Require captions in figur..."]
    latex_004["latex-004<br/>Maintain bibliography hyg..."]
    latex_005["latex-005<br/>Avoid hardcoded absolute ..."]
    latex_006["latex-006<br/>Prefer semantic emphasis ..."]
    latex_007["latex-007<br/>Prevent circular \input a..."]
    latex_008["latex-008<br/>Declare UTF-8 encoding in..."]
    latex_009["latex-009<br/>Remove unused packages"]
    det_LatexBibliographyHygieneDetector["Latex Bibliography<br/>Hygiene"]
    latex_004 --> det_LatexBibliographyHygieneDetector
    det_LatexCaptionCompletenessDetector["Latex Caption<br/>Completeness"]
    latex_003 --> det_LatexCaptionCompletenessDetector
    det_LatexEncodingDeclarationDetector["Latex Encoding<br/>Declaration"]
    latex_008 --> det_LatexEncodingDeclarationDetector
    det_LatexIncludeLoopDetector["Latex Include<br/>Loop"]
    latex_007 --> det_LatexIncludeLoopDetector
    det_LatexLabelRefDisciplineDetector["Latex Label<br/>Ref Discipline"]
    latex_002 --> det_LatexLabelRefDisciplineDetector
    det_LatexMacroDefinitionDetector["Latex Macro<br/>Definition"]
    latex_001 --> det_LatexMacroDefinitionDetector
    det_LatexSemanticMarkupDetector["Latex Semantic<br/>Markup"]
    latex_006 --> det_LatexSemanticMarkupDetector
    det_LatexUnusedPackagesDetector["Latex Unused<br/>Packages"]
    latex_009 --> det_LatexUnusedPackagesDetector
    det_LatexWidthAbstractionDetector["Latex Width<br/>Abstraction"]
    latex_005 --> det_LatexWidthAbstractionDetector
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
        class det_01["Latex Bibliography Hygiene"]
        ViolationDetector <|-- det_01
        class det_02["Latex Caption Completeness"]
        ViolationDetector <|-- det_02
        class det_03["Latex Encoding Declaration"]
        ViolationDetector <|-- det_03
        class det_04["Latex Include Loop"]
        ViolationDetector <|-- det_04
        class det_05["Latex Label Ref Discipline"]
        ViolationDetector <|-- det_05
        class det_06["Latex Macro Definition"]
        ViolationDetector <|-- det_06
        class det_07["Latex Semantic Markup"]
        ViolationDetector <|-- det_07
        class det_08["Latex Unused Packages"]
        ViolationDetector <|-- det_08
        class det_09["Latex Width Abstraction"]
        ViolationDetector <|-- det_09
    ```

??? example "Analysis Pipeline"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 50, "rankSpacing": 70}}}%%
    flowchart TD
    Source(["Source Code"]) --> Parse["Parse & Tokenize"]
    Parse --> Metrics["Compute Metrics"]
    Metrics --> Pipeline{"9 Detectors"}
    Pipeline --> Collect["Aggregate Violations"]
    Collect --> Result(["AnalysisResult<br/>9 principles"])
    ```

??? example "Analysis States"
    ```mermaid
    %%{init: {"theme": "base"}}%%
    stateDiagram-v2
        [*] --> Ready
        Ready --> Parsing : analyze(code)
        Parsing --> Computing : AST ready
        Computing --> Detecting : metrics ready
        Detecting --> Reporting : 9 detectors run
        Reporting --> [*] : AnalysisResult
        Parsing --> Reporting : parse error (best-effort)
    ```

## Configuration

```yaml
languages:
  latex:
    enabled: true
    pipeline:
```


## See Also

- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
- [Prompt Generation](../prompt-generation.md) — Generate AI remediation prompts
