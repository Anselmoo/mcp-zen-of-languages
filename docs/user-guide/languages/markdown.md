---
title: Markdown / MDX
description: "7 zen principles enforced by 7 detectors: Documentation structure, accessibility, and MDX component hygiene."
icon: material/language-markdown
tags:
  - Markdown / MDX
---

# Markdown / MDX



## Optional External Tool Augmentation

!!! info "Consent-first external tooling"
    External tool execution is optional and disabled by default. Use
    `--enable-external-tools` (CLI) or `enable_external_tools=true` (MCP)
    to opt in. Missing tools should return recommendations; no automatic
    installs occur during analysis.

| Tool | Default invocation | Output |
|------|---------------------|--------|
| `markdownlint` | `markdownlint --stdin --json` | JSON |
| `prettier` | `prettier --check --stdin-filepath stdin.md` | Text / structured stderr |

!!! tip "Temporary runner fallback"
    For temporary execution via package runners, use
    `--allow-temporary-runners` (CLI) or `allow_temporary_runners=true` (MCP).


## Zen Principles

7 principles across 7 categories, drawn from [CommonMark + MDX authoring best practices](https://commonmark.org/).

<div class="grid" markdown>

:material-tag-outline: **Clarity** · 1 principle
:material-tag-outline: **Configuration** · 1 principle
:material-tag-outline: **Correctness** · 1 principle
:material-tag-outline: **Documentation** · 1 principle
:material-tag-outline: **Organization** · 1 principle
:material-tag-outline: **Structure** · 1 principle
:material-tag-outline: **Usability** · 1 principle

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `md-001` | Preserve heading hierarchy | Structure | 6 | `ZEN-RETURN-EARLY` |
| `md-002` | Images require meaningful alt text | Usability | 8 | `ZEN-UNAMBIGUOUS-NAME` |
| `md-003` | Avoid bare URLs in prose | Clarity | 5 | `ZEN-EXPLICIT-INTENT` |
| `md-004` | Fence code blocks with explicit language tags | Documentation | 4 | `ZEN-UNAMBIGUOUS-NAME`, `ZEN-EXPLICIT-INTENT` |
| `md-005` | Keep front-matter complete when present | Configuration | 6 | `ZEN-EXPLICIT-INTENT` |
| `md-006` | Use named default exports in MDX | Correctness | 6 | `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME` |
| `md-007` | Keep MDX imports hygienic | Organization | 5 | `ZEN-STRICT-FENCES` |

??? info "`md-001` — Preserve heading hierarchy"
    **Headings should not skip levels (for example H1 directly to H3).**

    **Universal Dogmas:** `ZEN-RETURN-EARLY`
    **Common Violations:**

    - Heading level jump greater than one level

??? info "`md-002` — Images require meaningful alt text"
    **Every Markdown image should include non-empty alternative text.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Image markdown with empty alt text

    **Detectable Patterns:**

    - `!\[\s*\]\(`

??? info "`md-003` — Avoid bare URLs in prose"
    **Raw URLs should be wrapped as Markdown links or angle-bracket autolinks.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Bare URL in prose text

    **Detectable Patterns:**

    - `https?://`

??? info "`md-004` — Fence code blocks with explicit language tags"
    **Fenced code blocks should declare a language for syntax highlighting.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Code fence missing language identifier

    **Detectable Patterns:**

    - `\`\`\``

??? info "`md-005` — Keep front-matter complete when present"
    **If YAML front-matter exists, required metadata keys must be provided.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Front-matter is missing required keys

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `required_frontmatter_keys` | `['title', 'description']` |

??? info "`md-006` — Use named default exports in MDX"
    **Avoid anonymous default exports in MDX modules.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Unnamed default export in MDX

??? info "`md-007` — Keep MDX imports hygienic"
    **Imported MDX components should be used in JSX or module code.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`
    **Common Violations:**

    - Imported MDX component is never used


## Detector Catalog

### Clarity

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **MarkdownBareUrlDetector** | Detect raw HTTP(S) URLs not wrapped in Markdown link syntax | `md-003` |

### Configuration

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **MarkdownFrontMatterDetector** | Detect incomplete YAML front-matter blocks and unsafe/dead relative links | `md-005` |

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **MarkdownMdxNamedDefaultExportDetector** | Detect anonymous default exports in MDX modules | `md-006` |

### Documentation

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **MarkdownCodeFenceLanguageDetector** | Detect fenced code blocks that omit a language identifier | `md-004` |

### Organization

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **MarkdownMdxImportHygieneDetector** | Detect imported MDX identifiers that are never referenced | `md-007` |

### Structure

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **MarkdownHeadingHierarchyDetector** | Detect heading level skips, missing H1, and headings-free documents | `md-001` |

### Usability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **MarkdownAltTextDetector** | Detect Markdown image syntax with empty alt text | `md-002` |


??? example "Principle → Detector Wiring"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    md_001["md-001<br/>Preserve heading hierarch..."]
    md_002["md-002<br/>Images require meaningful..."]
    md_003["md-003<br/>Avoid bare URLs in prose"]
    md_004["md-004<br/>Fence code blocks with ex..."]
    md_005["md-005<br/>Keep front-matter complet..."]
    md_006["md-006<br/>Use named default exports..."]
    md_007["md-007<br/>Keep MDX imports hygienic"]
    det_MarkdownAltTextDetector["Markdown Alt<br/>Text"]
    md_002 --> det_MarkdownAltTextDetector
    det_MarkdownBareUrlDetector["Markdown Bare<br/>Url"]
    md_003 --> det_MarkdownBareUrlDetector
    det_MarkdownCodeFenceLanguageDetector["Markdown Code<br/>Fence Language"]
    md_004 --> det_MarkdownCodeFenceLanguageDetector
    det_MarkdownFrontMatterDetector["Markdown Front<br/>Matter"]
    md_005 --> det_MarkdownFrontMatterDetector
    det_MarkdownHeadingHierarchyDetector["Markdown Heading<br/>Hierarchy"]
    md_001 --> det_MarkdownHeadingHierarchyDetector
    det_MarkdownMdxImportHygieneDetector["Markdown Mdx<br/>Import Hygiene"]
    md_007 --> det_MarkdownMdxImportHygieneDetector
    det_MarkdownMdxNamedDefaultExportDetector["Markdown Mdx<br/>Named Default<br/>Export"]
    md_006 --> det_MarkdownMdxNamedDefaultExportDetector
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
        class det_01["Markdown Alt Text"]
        ViolationDetector <|-- det_01
        class det_02["Markdown Bare Url"]
        ViolationDetector <|-- det_02
        class det_03["Markdown Code Fence Language"]
        ViolationDetector <|-- det_03
        class det_04["Markdown Front Matter"]
        ViolationDetector <|-- det_04
        class det_05["Markdown Heading Hierarchy"]
        ViolationDetector <|-- det_05
        class det_06["Markdown Mdx Import Hygiene"]
        ViolationDetector <|-- det_06
        class det_07["Markdown Mdx Named Default Export"]
        ViolationDetector <|-- det_07
    ```

??? example "Analysis Pipeline"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 50, "rankSpacing": 70}}}%%
    flowchart TD
    Source(["Source Code"]) --> Parse["Parse & Tokenize"]
    Parse --> Metrics["Compute Metrics"]
    Metrics --> Pipeline{"7 Detectors"}
    Pipeline --> Collect["Aggregate Violations"]
    Collect --> Result(["AnalysisResult<br/>7 principles"])
    ```

??? example "Analysis States"
    ```mermaid
    %%{init: {"theme": "base"}}%%
    stateDiagram-v2
        [*] --> Ready
        Ready --> Parsing : analyze(code)
        Parsing --> Computing : AST ready
        Computing --> Detecting : metrics ready
        Detecting --> Reporting : 7 detectors run
        Reporting --> [*] : AnalysisResult
        Parsing --> Reporting : parse error (best-effort)
    ```

## Configuration

```yaml
languages:
  markdown:
    enabled: true
    pipeline:
      - type: md-005
        required_frontmatter_keys: ['title', 'description']
      - type: md-006
        mdx_only: True
      - type: md-007
        mdx_only: True
```


## See Also

- [Config Formats](config-formats.md) — Principles for JSON, TOML, XML, and YAML
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
