---
title: LaTeX
description: "9 zen principles enforced by 9 detectors: LaTeX document quality and semantic authoring."
icon: material/math-integral
tags:
  - LaTeX
---

# LaTeX



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

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `latex-001` | Prefer \newcommand over \def | Correctness | 7 |
| `latex-002` | Keep labels and references consistent | Correctness | 8 |
| `latex-003` | Require captions in figures and tables | Documentation | 6 |
| `latex-004` | Maintain bibliography hygiene | Organization | 6 |
| `latex-005` | Avoid hardcoded absolute lengths | Consistency | 5 |
| `latex-006` | Prefer semantic emphasis commands | Clarity | 4 |
| `latex-007` | Prevent circular \input and \include chains | Architecture | 8 |
| `latex-008` | Declare UTF-8 encoding intent | Correctness | 5 |
| `latex-009` | Remove unused packages | Organization | 5 |

??? info "`latex-001` — Prefer \newcommand over \def"
    **Use checked macro definitions to avoid accidental redefinitions.**

    **Common Violations:**

    - Raw \def usage for user macros

??? info "`latex-002` — Keep labels and references consistent"
    **Every label should be referenced and every reference should resolve.**

    **Common Violations:**

    - Unused labels or unresolved \ref/\eqref targets

??? info "`latex-003` — Require captions in figures and tables"
    **Figure and table environments should include captions for context.**

    **Common Violations:**

    - Figure/table without \caption

??? info "`latex-004` — Maintain bibliography hygiene"
    **Prefer citation keys with bibliography files and avoid uncited entries.**

    **Common Violations:**

    - Manual \bibitem blocks or uncited bibliography items

??? info "`latex-005` — Avoid hardcoded absolute lengths"
    **Prefer relative lengths such as \textwidth and \linewidth.**

    **Common Violations:**

    - Absolute units like pt/cm/mm/in in layout-sensitive commands

??? info "`latex-006` — Prefer semantic emphasis commands"
    **Use semantic markup over direct visual styling commands.**

    **Common Violations:**

    - \textit or \textbf used as semantic emphasis

??? info "`latex-007` — Prevent circular \input and \include chains"
    **Included files must not create recursive include loops.**

    **Common Violations:**

    - Circular \input/\include dependency

??? info "`latex-008` — Declare UTF-8 encoding intent"
    **Declare UTF-8 input encoding unless using LuaTeX/XeTeX native flow.**

    **Common Violations:**

    - Missing UTF-8 encoding declaration

??? info "`latex-009` — Remove unused packages"
    **Declared packages should have commands used in the document.**

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
    graph LR
    latex_001["latex-001<br/>Prefer \newcommand over \def"]
    latex_002["latex-002<br/>Keep labels and references consistent"]
    latex_003["latex-003<br/>Require captions in figures and tables"]
    latex_004["latex-004<br/>Maintain bibliography hygiene"]
    latex_005["latex-005<br/>Avoid hardcoded absolute lengths"]
    latex_006["latex-006<br/>Prefer semantic emphasis commands"]
    latex_007["latex-007<br/>Prevent circular \input and \include cha..."]
    latex_008["latex-008<br/>Declare UTF-8 encoding intent"]
    latex_009["latex-009<br/>Remove unused packages"]
    det_LatexBibliographyHygieneDetector["LatexBibliographyHygieneDetector"]
    latex_004 --> det_LatexBibliographyHygieneDetector
    det_LatexCaptionCompletenessDetector["LatexCaptionCompletenessDetector"]
    latex_003 --> det_LatexCaptionCompletenessDetector
    det_LatexEncodingDeclarationDetector["LatexEncodingDeclarationDetector"]
    latex_008 --> det_LatexEncodingDeclarationDetector
    det_LatexIncludeLoopDetector["LatexIncludeLoopDetector"]
    latex_007 --> det_LatexIncludeLoopDetector
    det_LatexLabelRefDisciplineDetector["LatexLabelRefDisciplineDetector"]
    latex_002 --> det_LatexLabelRefDisciplineDetector
    det_LatexMacroDefinitionDetector["LatexMacroDefinitionDetector"]
    latex_001 --> det_LatexMacroDefinitionDetector
    det_LatexSemanticMarkupDetector["LatexSemanticMarkupDetector"]
    latex_006 --> det_LatexSemanticMarkupDetector
    det_LatexUnusedPackagesDetector["LatexUnusedPackagesDetector"]
    latex_009 --> det_LatexUnusedPackagesDetector
    det_LatexWidthAbstractionDetector["LatexWidthAbstractionDetector"]
    latex_005 --> det_LatexWidthAbstractionDetector
    classDef principle fill:#4051b5,color:#fff,stroke:none
    classDef detector fill:#26a269,color:#fff,stroke:none
    class latex_001 principle
    class latex_002 principle
    class latex_003 principle
    class latex_004 principle
    class latex_005 principle
    class latex_006 principle
    class latex_007 principle
    class latex_008 principle
    class latex_009 principle
    class det_LatexBibliographyHygieneDetector detector
    class det_LatexCaptionCompletenessDetector detector
    class det_LatexEncodingDeclarationDetector detector
    class det_LatexIncludeLoopDetector detector
    class det_LatexLabelRefDisciplineDetector detector
    class det_LatexMacroDefinitionDetector detector
    class det_LatexSemanticMarkupDetector detector
    class det_LatexUnusedPackagesDetector detector
    class det_LatexWidthAbstractionDetector detector
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
