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

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `css-001` | Avoid specificity creep | Architecture | 7 |
| `css-002` | Avoid magic pixel values | Design | 6 |
| `css-003` | Limit inline color literals | Consistency | 6 |
| `css-004` | Keep stylesheets modular | Organization | 5 |
| `css-005` | Prefer modern import strategy | Performance | 6 |
| `css-006` | Use a z-index scale | Consistency | 6 |
| `css-007` | Avoid manual vendor prefixes | Consistency | 5 |
| `css-008` | Use a consistent breakpoint scale | Consistency | 5 |

??? info "`css-001` — Avoid specificity creep"
    **Deep selector nesting and !important overuse make styles brittle.**

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

    **Common Violations:**

    - Raw pixel values used directly

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_raw_pixel_literals` | `0` |

??? info "`css-003` — Limit inline color literals"
    **Prefer design tokens/variables over hardcoded color literals.**

    **Common Violations:**

    - Inline hex/rgb/hsl color literal used

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_color_literals` | `0` |

??? info "`css-004` — Keep stylesheets modular"
    **Very large stylesheet files should be split into modules.**

    **Common Violations:**

    - Stylesheet exceeds line threshold

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_stylesheet_lines` | `300` |

??? info "`css-005` — Prefer modern import strategy"
    **Avoid @import chains where @use/module composition is better.**

    **Common Violations:**

    - @import usage detected

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_import_statements` | `0` |

??? info "`css-006` — Use a z-index scale"
    **Arbitrary z-index values should follow a shared scale.**

    **Common Violations:**

    - z-index value outside approved scale

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `allowed_z_index_values` | `[0, 1, 10, 100, 1000]` |

??? info "`css-007` — Avoid manual vendor prefixes"
    **Manual prefixes are typically handled by autoprefixer.**

    **Common Violations:**

    - Manual vendor-prefixed property used

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_vendor_prefixed_properties` | `0` |

??? info "`css-008` — Use a consistent breakpoint scale"
    **Media query breakpoints should align to a defined scale.**

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
    graph LR
    css_001["css-001<br/>Avoid specificity creep"]
    css_002["css-002<br/>Avoid magic pixel values"]
    css_003["css-003<br/>Limit inline color literals"]
    css_004["css-004<br/>Keep stylesheets modular"]
    css_005["css-005<br/>Prefer modern import strategy"]
    css_006["css-006<br/>Use a z-index scale"]
    css_007["css-007<br/>Avoid manual vendor prefixes"]
    css_008["css-008<br/>Use a consistent breakpoint scale"]
    det_CssColorLiteralDetector["CssColorLiteralDetector"]
    css_003 --> det_CssColorLiteralDetector
    det_CssGodStylesheetDetector["CssGodStylesheetDetector"]
    css_004 --> det_CssGodStylesheetDetector
    det_CssImportChainDetector["CssImportChainDetector"]
    css_005 --> det_CssImportChainDetector
    det_CssMagicPixelsDetector["CssMagicPixelsDetector"]
    css_002 --> det_CssMagicPixelsDetector
    det_CssMediaQueryScaleDetector["CssMediaQueryScaleDetector"]
    css_008 --> det_CssMediaQueryScaleDetector
    det_CssSpecificityDetector["CssSpecificityDetector"]
    css_001 --> det_CssSpecificityDetector
    det_CssVendorPrefixDetector["CssVendorPrefixDetector"]
    css_007 --> det_CssVendorPrefixDetector
    det_CssZIndexScaleDetector["CssZIndexScaleDetector"]
    css_006 --> det_CssZIndexScaleDetector
    classDef principle fill:#4051b5,color:#fff,stroke:none
    classDef detector fill:#26a269,color:#fff,stroke:none
    class css_001 principle
    class css_002 principle
    class css_003 principle
    class css_004 principle
    class css_005 principle
    class css_006 principle
    class css_007 principle
    class css_008 principle
    class det_CssColorLiteralDetector detector
    class det_CssGodStylesheetDetector detector
    class det_CssImportChainDetector detector
    class det_CssMagicPixelsDetector detector
    class det_CssMediaQueryScaleDetector detector
    class det_CssSpecificityDetector detector
    class det_CssVendorPrefixDetector detector
    class det_CssZIndexScaleDetector detector
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
