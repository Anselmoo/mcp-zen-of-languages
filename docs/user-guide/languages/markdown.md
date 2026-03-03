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
    graph LR
    md_001["md-001<br/>Preserve heading hierarchy"]
    md_002["md-002<br/>Images require meaningful alt text"]
    md_003["md-003<br/>Avoid bare URLs in prose"]
    md_004["md-004<br/>Fence code blocks with explicit language..."]
    md_005["md-005<br/>Keep front-matter complete when present"]
    md_006["md-006<br/>Use named default exports in MDX"]
    md_007["md-007<br/>Keep MDX imports hygienic"]
    det_MarkdownAltTextDetector["MarkdownAltTextDetector"]
    md_002 --> det_MarkdownAltTextDetector
    det_MarkdownBareUrlDetector["MarkdownBareUrlDetector"]
    md_003 --> det_MarkdownBareUrlDetector
    det_MarkdownCodeFenceLanguageDetector["MarkdownCodeFenceLanguageDetector"]
    md_004 --> det_MarkdownCodeFenceLanguageDetector
    det_MarkdownFrontMatterDetector["MarkdownFrontMatterDetector"]
    md_005 --> det_MarkdownFrontMatterDetector
    det_MarkdownHeadingHierarchyDetector["MarkdownHeadingHierarchyDetector"]
    md_001 --> det_MarkdownHeadingHierarchyDetector
    det_MarkdownMdxImportHygieneDetector["MarkdownMdxImportHygieneDetector"]
    md_007 --> det_MarkdownMdxImportHygieneDetector
    det_MarkdownMdxNamedDefaultExportDetector["MarkdownMdxNamedDefaultExportDetector"]
    md_006 --> det_MarkdownMdxNamedDefaultExportDetector
    classDef principle fill:#4051b5,color:#fff,stroke:none
    classDef detector fill:#26a269,color:#fff,stroke:none
    class md_001 principle
    class md_002 principle
    class md_003 principle
    class md_004 principle
    class md_005 principle
    class md_006 principle
    class md_007 principle
    class det_MarkdownAltTextDetector detector
    class det_MarkdownBareUrlDetector detector
    class det_MarkdownCodeFenceLanguageDetector detector
    class det_MarkdownFrontMatterDetector detector
    class det_MarkdownHeadingHierarchyDetector detector
    class det_MarkdownMdxImportHygieneDetector detector
    class det_MarkdownMdxNamedDefaultExportDetector detector
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
