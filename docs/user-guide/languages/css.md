---
title: CSS
description: "8 zen principles enforced by 8 detectors: Maintainable stylesheets through consistency and design tokens.."
icon: material/language-css3
tags:
  - CSS
---

# CSS

Stylesheets can accumulate hidden complexity quickly — deeply nested selectors, hardcoded values, and oversized files that become difficult to maintain. These **8 principles** focus on keeping CSS, SCSS, and Less modular, token-driven, and consistent with frontend design-system practices.

## Optional External Tool Augmentation

!!! info "Consent-first external tooling"
    External tool execution is optional and disabled by default. Use
    `--enable-external-tools` (CLI) or `enable_external_tools=true` (MCP)
    to opt in. Missing tools should return recommendations; no automatic
    installs occur during analysis.

| Tool | Default invocation | Output |
|------|---------------------|--------|
| `biome` | `biome lint --stdin-file-path stdin.css --reporter json` | JSON |
| `prettier` | `prettier --check --stdin-filepath stdin.css` | Text / structured stderr |
| `stylelint` | `stylelint --stdin-filename stdin.css` | Text / structured stderr |

!!! tip "Temporary runner fallback"
    For temporary execution via package runners, use
    `--allow-temporary-runners` (CLI) or `allow_temporary_runners=true` (MCP).


## Zen Principles

8 principles across 5 categories, drawn from [CSSWG + common modular CSS practices](https://www.w3.org/TR/CSS/).

<div class="grid" markdown>

:material-tag-outline: **Architecture** · 1 principle
:material-tag-outline: **Consistency** · 4 principles
:material-tag-outline: **Design** · 1 principle
:material-tag-outline: **Organization** · 1 principle
:material-tag-outline: **Performance** · 1 principle

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `css-001` | Avoid specificity creep | Architecture | 7 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-RETURN-EARLY` |
| `css-002` | Avoid magic pixel values | Design | 6 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT` |
| `css-003` | Limit inline color literals | Consistency | 6 | `ZEN-EXPLICIT-INTENT` |
| `css-004` | Keep stylesheets modular | Organization | 5 | `ZEN-STRICT-FENCES` |
| `css-005` | Prefer modern import strategy | Performance | 6 | `ZEN-PROPORTIONATE-COMPLEXITY` |
| `css-006` | Use a z-index scale | Consistency | 6 | `ZEN-EXPLICIT-INTENT` |
| `css-007` | Avoid manual vendor prefixes | Consistency | 5 | `ZEN-EXPLICIT-INTENT` |
| `css-008` | Use a consistent breakpoint scale | Consistency | 5 | `ZEN-EXPLICIT-INTENT` |

??? info "`css-001` — Avoid specificity creep"
    **Deep selector nesting and !important overuse make styles brittle.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-RETURN-EARLY`
    **Common Violations:**

    - Deeply nested selectors
    - Overuse of !important

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_selector_nesting` | `3` |
    | `max_important_usages` | `0` |

??? info "`css-002` — Avoid magic pixel values"
    **Prefer design tokens and CSS variables over raw px values.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Raw pixel values used directly

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_raw_pixel_literals` | `0` |

??? info "`css-003` — Limit inline color literals"
    **Prefer design tokens/variables over hardcoded color literals.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Inline hex/rgb/hsl color literal used

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_color_literals` | `0` |

??? info "`css-004` — Keep stylesheets modular"
    **Very large stylesheet files should be split into modules.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`
    **Common Violations:**

    - Stylesheet exceeds line threshold

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_stylesheet_lines` | `300` |

??? info "`css-005` — Prefer modern import strategy"
    **Avoid @import chains where @use/module composition is better.**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - @import usage detected

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_import_statements` | `0` |

??? info "`css-006` — Use a z-index scale"
    **Arbitrary z-index values should follow a shared scale.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - z-index value outside approved scale

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `allowed_z_index_values` | `[0, 1, 10, 100, 1000]` |

??? info "`css-007` — Avoid manual vendor prefixes"
    **Manual prefixes are typically handled by autoprefixer.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Manual vendor-prefixed property used

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_vendor_prefixed_properties` | `0` |

??? info "`css-008` — Use a consistent breakpoint scale"
    **Media query breakpoints should align to a defined scale.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Media query breakpoint not in approved scale

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `allowed_breakpoint_values` | `[480, 768, 1024, 1280, 1440]` |


## Detector Catalog

### Architecture

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CssSpecificityDetector** | Detect excessive selector nesting and ``!important`` usage | `css-001` |

### Consistency

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CssColorLiteralDetector** | Detect inline color literals | `css-003` |
| **CssZIndexScaleDetector** | Detect z-index values outside allowed scale | `css-006` |
| **CssVendorPrefixDetector** | Detect manual vendor-prefixed properties | `css-007` |
| **CssMediaQueryScaleDetector** | Detect inconsistent media query breakpoints | `css-008` |

### Design

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CssMagicPixelsDetector** | Detect raw pixel literals | `css-002` |

### Organization

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CssGodStylesheetDetector** | Detect oversized stylesheet files | `css-004` |

### Performance

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **CssImportChainDetector** | Detect ``@import`` overuse | `css-005` |


??? example "Principle → Detector Wiring"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    css_001["css-001<br/>Avoid specificity creep"]
    css_002["css-002<br/>Avoid magic pixel values"]
    css_003["css-003<br/>Limit inline color litera..."]
    css_004["css-004<br/>Keep stylesheets modular"]
    css_005["css-005<br/>Prefer modern import stra..."]
    css_006["css-006<br/>Use a z-index scale"]
    css_007["css-007<br/>Avoid manual vendor prefi..."]
    css_008["css-008<br/>Use a consistent breakpoi..."]
    det_CssColorLiteralDetector["Css Color<br/>Literal"]
    css_003 --> det_CssColorLiteralDetector
    det_CssGodStylesheetDetector["Css God<br/>Stylesheet"]
    css_004 --> det_CssGodStylesheetDetector
    det_CssImportChainDetector["Css Import<br/>Chain"]
    css_005 --> det_CssImportChainDetector
    det_CssMagicPixelsDetector["Css Magic<br/>Pixels"]
    css_002 --> det_CssMagicPixelsDetector
    det_CssMediaQueryScaleDetector["Css Media<br/>Query Scale"]
    css_008 --> det_CssMediaQueryScaleDetector
    det_CssSpecificityDetector["Css Specificity"]
    css_001 --> det_CssSpecificityDetector
    det_CssVendorPrefixDetector["Css Vendor<br/>Prefix"]
    css_007 --> det_CssVendorPrefixDetector
    det_CssZIndexScaleDetector["Css Z<br/>Index Scale"]
    css_006 --> det_CssZIndexScaleDetector
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
        class det_01["Css Color Literal"]
        ViolationDetector <|-- det_01
        class det_02["Css God Stylesheet"]
        ViolationDetector <|-- det_02
        class det_03["Css Import Chain"]
        ViolationDetector <|-- det_03
        class det_04["Css Magic Pixels"]
        ViolationDetector <|-- det_04
        class det_05["Css Media Query Scale"]
        ViolationDetector <|-- det_05
        class det_06["Css Specificity"]
        ViolationDetector <|-- det_06
        class det_07["Css Vendor Prefix"]
        ViolationDetector <|-- det_07
        class det_08["Css Z Index Scale"]
        ViolationDetector <|-- det_08
    ```

??? example "Analysis Pipeline"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 50, "rankSpacing": 70}}}%%
    flowchart TD
    Source(["Source Code"]) --> Parse["Parse & Tokenize"]
    Parse --> Metrics["Compute Metrics"]
    Metrics --> Pipeline{"8 Detectors"}
    Pipeline --> Collect["Aggregate Violations"]
    Collect --> Result(["AnalysisResult<br/>8 principles"])
    ```

??? example "Analysis States"
    ```mermaid
    %%{init: {"theme": "base"}}%%
    stateDiagram-v2
        [*] --> Ready
        Ready --> Parsing : analyze(code)
        Parsing --> Computing : AST ready
        Computing --> Detecting : metrics ready
        Detecting --> Reporting : 8 detectors run
        Reporting --> [*] : AnalysisResult
        Parsing --> Reporting : parse error (best-effort)
    ```

## Configuration

```yaml
languages:
  css:
    enabled: true
    pipeline:
      - type: css-001
        max_selector_nesting: 3
        max_important_usages: 0
      - type: css-002
        max_raw_pixel_literals: 0
      - type: css-003
        max_color_literals: 0
      - type: css-004
        max_stylesheet_lines: 300
      - type: css-005
        max_import_statements: 0
      - type: css-006
        allowed_z_index_values: [0, 1, 10, 100, 1000]
      - type: css-007
        max_vendor_prefixed_properties: 0
      - type: css-008
        allowed_breakpoint_values: [480, 768, 1024, 1280, 1440]
```


## See Also

- [JavaScript](javascript.md) — Common frontend codebase counterpart
- [TypeScript](typescript.md) — Strongly-typed frontend language companion
- [Configuration](../configuration.md) — Per-language pipeline overrides
