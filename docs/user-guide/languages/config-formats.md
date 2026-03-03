---
title: Config Formats
description: "Zen principles across JSON, TOML, XML, and YAML enforced by dedicated detectors for data format consistency and correctness."
icon: material/code-json
tags:
  - JSON
  - TOML
  - XML
  - YAML
---

# Configuration Formats

Configuration files are code too — they're read by humans, versioned in git, and debugged at 2am during outages. MCP Zen of Languages analyzes four data formats with dedicated detectors for each.

## JSON — 9 Principles, 9 Detectors

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `json-001` | Choose strictness intentionally | Correctness | 7 | `ZEN-EXPLICIT-INTENT` |
| `json-002` | Keep object depth understandable | Structure | 6 | `ZEN-RETURN-EARLY` |
| `json-003` | Keys must be unique | Correctness | 8 | `ZEN-EXPLICIT-INTENT` |
| `json-004` | Avoid magic string repetition | Clarity | 5 | `ZEN-EXPLICIT-INTENT` |
| `json-005` | Keys are case-sensitive identifiers | Naming | 5 | `ZEN-UNAMBIGUOUS-NAME` |
| `json-006` | Keep inline arrays bounded | Structure | 4 | `ZEN-RETURN-EARLY` |
| `json-007` | Prefer omission over null sprawl | Correctness | 5 | `ZEN-EXPLICIT-INTENT` |
| `json-008` | Dates must follow ISO 8601 | Correctness | 6 | `ZEN-EXPLICIT-INTENT` |
| `json-009` | Prefer key omission over explicit null | Clarity | 5 | `ZEN-EXPLICIT-INTENT` |

??? info "`json-001` — Choose strictness intentionally"
    **Trailing commas should be rejected for JSON unless JSON5 is explicitly targeted.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Trailing commas in strict JSON mode

    **Detectable Patterns:**

    - `,\]`
    - `,\}`

??? info "`json-002` — Keep object depth understandable"
    **Deeply nested objects/arrays are hard to reason about and validate.**

    **Universal Dogmas:** `ZEN-RETURN-EARLY`

    **Common Violations:**

    - Nesting depth exceeds configured threshold

??? info "`json-003` — Keys must be unique"
    **Duplicate object keys silently override values in many parsers.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Duplicate keys in an object

??? info "`json-004` — Avoid magic string repetition"
    **Repeated string literals should be extracted or referenced consistently.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Repeated magic string values

??? info "`json-005` — Keys are case-sensitive identifiers"
    **Avoid mixing camelCase, snake_case, and PascalCase at the same object level.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`

    **Common Violations:**

    - Mixed key casing at same object level

??? info "`json-006` — Keep inline arrays bounded"
    **Very large inline arrays are hard to review and often belong in separate data files.**

    **Universal Dogmas:** `ZEN-RETURN-EARLY`

    **Common Violations:**

    - Oversized inline arrays

??? info "`json-007` — Prefer omission over null sprawl"
    **Excessive null usage usually indicates optional keys that can be omitted.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Excessive null values across the document

??? info "`json-008` — Dates must follow ISO 8601"
    **Date strings should use ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ) for unambiguous, sortable representation. Locale-dependent formats such as MM/DD/YYYY create parsing ambiguity.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Non-ISO 8601 date string detected

    **Detectable Patterns:**

    - `\d{1,2}/\d{1,2}/\d{2,4}`
    - `\d{1,2}\.\d{1,2}\.\d{4}`

??? info "`json-009` — Prefer key omission over explicit null"
    **Top-level object keys whose value is explicitly null should be omitted entirely. Explicit null at the top level signals optional absence, which is better expressed by omitting the key.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Top-level key set to explicit null

| Detector | What It Catches |
|----------|-----------------|
| **JsonStrictnessDetector** | Flag trailing commas when strict JSON output is expected |
| **JsonSchemaConsistencyDetector** | Detect excessive JSON nesting depth |
| **JsonDuplicateKeyDetector** | Detect duplicate keys in JSON objects |
| **JsonMagicStringDetector** | Detect repeated magic-string values |
| **JsonKeyCasingDetector** | Detect mixed key casing at the same object level |
| **JsonArrayOrderDetector** | Detect oversized inline arrays |
| **JsonNullSprawlDetector** | Detect excessive null values across JSON objects/arrays |
| **JsonDateFormatDetector** | Identify date strings that deviate from ISO 8601 formatting |
| **JsonNullHandlingDetector** | Report top-level object keys whose values are explicitly ``null`` |

---


## SVG — 15 Principles, 15 Detectors

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `svg-001` | Include a root title element for accessibility | Usability | 8 | `ZEN-UNAMBIGUOUS-NAME` |
| `svg-002` | Use role=img with aria-labelledby for inline SVG | Usability | 8 | `ZEN-UNAMBIGUOUS-NAME` |
| `svg-003` | Give image nodes alternative text | Usability | 7 | `ZEN-UNAMBIGUOUS-NAME` |
| `svg-004` | Provide a long description for complex graphics | Documentation | 6 | `ZEN-UNAMBIGUOUS-NAME` |
| `svg-005` | Prefer presentation attributes over inline styles | Consistency | 5 | `ZEN-EXPLICIT-INTENT` |
| `svg-006` | Use viewBox with fixed dimensions | Structure | 6 | `ZEN-RETURN-EARLY` |
| `svg-007` | Remove unused defs entries | Organization | 5 | `ZEN-STRICT-FENCES`, `ZEN-PROPORTIONATE-COMPLEXITY` |
| `svg-008` | Avoid excessive nested group depth | Complexity | 5 | `ZEN-PROPORTIONATE-COMPLEXITY`, `ZEN-RETURN-EARLY` |
| `svg-009` | Keep id attributes unique | Correctness | 8 | `ZEN-EXPLICIT-INTENT` |
| `svg-010` | Prefer relative path commands when practical | Idioms | 4 | `ZEN-RIGHT-ABSTRACTION` |
| `svg-011` | Avoid embedded base64 raster payloads | Performance | 7 | `ZEN-PROPORTIONATE-COMPLEXITY` |
| `svg-012` | Declare the SVG XML namespace | Correctness | 7 | `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME`, `ZEN-STRICT-FENCES` |
| `svg-013` | Use href instead of deprecated xlink:href | Idioms | 4 | `ZEN-RIGHT-ABSTRACTION` |
| `svg-014` | Keep node count within maintainable limits | Performance | 6 | `ZEN-PROPORTIONATE-COMPLEXITY` |
| `svg-015` | Remove production-bloat metadata and comments | Performance | 4 | `ZEN-PROPORTIONATE-COMPLEXITY`, `ZEN-UNAMBIGUOUS-NAME`, `ZEN-STRICT-FENCES` |

??? info "`svg-001` — Include a root title element for accessibility"
    **SVGs without a <title> child on the root are not announced well by screen readers.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`

    **Common Violations:**

    - Missing <title> child on root <svg>

??? info "`svg-002` — Use role=img with aria-labelledby for inline SVG"
    **Inline SVGs should be exposed as images and linked to accessible labels.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`

    **Common Violations:**

    - Missing role="img" and/or aria-labelledby on root <svg>

??? info "`svg-003` — Give image nodes alternative text"
    **Embedded raster images should carry alternative text for assistive technologies.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`

    **Common Violations:**

    - <image> element missing alt/title/aria-label text

??? info "`svg-004` — Provide a long description for complex graphics"
    **Charts or diagrams should provide a <desc> element to explain non-trivial content.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`

    **Common Violations:**

    - Complex SVG missing <desc> element

??? info "`svg-005` — Prefer presentation attributes over inline styles"
    **Inline style attributes reduce maintainability and hinder targeted optimization.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Inline style attribute found in SVG element

??? info "`svg-006` — Use viewBox with fixed dimensions"
    **Hardcoded width/height without viewBox reduces responsive scalability.**

    **Universal Dogmas:** `ZEN-RETURN-EARLY`

    **Common Violations:**

    - Root SVG has width/height but no viewBox

??? info "`svg-007` — Remove unused defs entries"
    **Unused gradients, symbols, or patterns in <defs> increase file complexity.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`, `ZEN-PROPORTIONATE-COMPLEXITY`

    **Common Violations:**

    - Unused ID defined under <defs>

??? info "`svg-008` — Avoid excessive nested group depth"
    **Deeply nested <g> structures increase DOM complexity without semantic gain.**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`, `ZEN-RETURN-EARLY`

    **Common Violations:**

    - Nested <g> depth exceeds recommended threshold

??? info "`svg-009` — Keep id attributes unique"
    **Duplicate IDs break references like <use>, url(#id), and ARIA links.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Duplicate id attribute value in SVG

??? info "`svg-010` — Prefer relative path commands when practical"
    **Paths composed only of absolute commands are often larger and less portable.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`

    **Common Violations:**

    - Path uses only absolute commands

??? info "`svg-011` — Avoid embedded base64 raster payloads"
    **Base64 raster data inflates file size and should usually be externalized.**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`

    **Common Violations:**

    - <image> uses data:image/*;base64 payload

??? info "`svg-012` — Declare the SVG XML namespace"
    **Missing xmlns="http://www.w3.org/2000/svg" breaks parsing in non-browser contexts.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME`, `ZEN-STRICT-FENCES`

    **Common Violations:**

    - Missing SVG namespace declaration

??? info "`svg-013` — Use href instead of deprecated xlink:href"
    **xlink:href is deprecated in SVG 2 and should be replaced with href.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`

    **Common Violations:**

    - Deprecated xlink:href attribute detected

??? info "`svg-014` — Keep node count within maintainable limits"
    **Very large SVG DOM trees should be simplified or delivered as sprites.**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`

    **Common Violations:**

    - SVG element count exceeds configured threshold

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_node_count` | `500` |

??? info "`svg-015` — Remove production-bloat metadata and comments"
    **Editor metadata, vendor namespaces, and XML comments add unnecessary payload.**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`, `ZEN-UNAMBIGUOUS-NAME`, `ZEN-STRICT-FENCES`

    **Common Violations:**

    - Metadata/comments/editor namespaces found in production SVG

| Detector | What It Catches |
|----------|-----------------|
| **SvgMissingTitleDetector** | Detects root SVG elements that omit an accessible title child |
| **SvgAriaRoleDetector** | Detects root SVG elements missing image role and labeling attributes |
| **SvgImageAltDetector** | Detects embedded image elements lacking alternative text metadata |
| **SvgDescForComplexGraphicsDetector** | Detects complex SVG documents that lack a descriptive <desc> element |
| **SvgInlineStyleDetector** | Detects inline style usage inside SVG markup |
| **SvgViewBoxDetector** | Detects fixed dimensions used without a responsive viewBox |
| **SvgUnusedDefsDetector** | Detects IDs declared under defs that are never referenced |
| **SvgNestedGroupsDetector** | Detects excessive nesting depth of SVG group elements |
| **SvgDuplicateIdDetector** | Detects duplicate ID values across SVG elements |
| **SvgAbsolutePathOnlyDetector** | Detects paths composed only of absolute command letters |
| **SvgBase64ImageDetector** | Detects base64-embedded raster images in SVG content |
| **SvgXmlnsDetector** | Detects missing core SVG XML namespace declarations |
| **SvgDeprecatedXlinkHrefDetector** | Detects deprecated xlink:href attributes in SVG markup |
| **SvgNodeCountDetector** | Detects SVG documents exceeding a configurable node-count threshold |
| **SvgProductionBloatDetector** | Detects metadata/comments and editor namespace bloat in production SVG |

---


## TOML — 8 Principles, 8 Detectors

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `toml-001` | Avoid inline tables | Readability | 6 | `ZEN-UNAMBIGUOUS-NAME` |
| `toml-002` | Avoid duplicate keys | Correctness | 8 | `ZEN-EXPLICIT-INTENT` |
| `toml-003` | Use lowercase keys | Consistency | 5 | `ZEN-EXPLICIT-INTENT` |
| `toml-004` | Avoid trailing commas | Readability | 5 | `ZEN-UNAMBIGUOUS-NAME` |
| `toml-005` | Clarity is paramount | Clarity | 5 | `ZEN-EXPLICIT-INTENT` |
| `toml-006` | Order implies importance | Organization | 4 | `ZEN-STRICT-FENCES` |
| `toml-007` | Time is specific | Correctness | 6 | `ZEN-EXPLICIT-INTENT` |
| `toml-008` | Floats are not integers | Correctness | 6 | `ZEN-EXPLICIT-INTENT` |

??? info "`toml-001` — Avoid inline tables"
    **Inline tables are harder to read; use full tables instead.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`

    **Common Violations:**

    - Inline table definitions in assignments

??? info "`toml-002` — Avoid duplicate keys"
    **Duplicate keys can overwrite previous values.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Duplicate key definitions

??? info "`toml-003` — Use lowercase keys"
    **Lowercase keys improve consistency across configurations.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Uppercase characters in keys

??? info "`toml-004` — Avoid trailing commas"
    **Trailing commas reduce readability in TOML arrays/tables.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`

    **Common Violations:**

    - Trailing commas before closing brackets

??? info "`toml-005` — Clarity is paramount"
    **Explain magic values with comments.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Magic values without comments

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `min_comment_lines` | `1` |

??? info "`toml-006` — Order implies importance"
    **Group related keys together before arrays or tables.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`

    **Common Violations:**

    - Repeated table headers spread apart

??? info "`toml-007` — Time is specific"
    **Use ISO 8601 timestamps for dates.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Non-ISO date strings

??? info "`toml-008` — Floats are not integers"
    **Use integer types where appropriate, avoid decimal .0 values.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Floats that represent integers

| Detector | What It Catches |
|----------|-----------------|
| **TomlNoInlineTablesDetector** | Flags inline table syntax (``key = { ... }``) that should use full table sections |
| **TomlDuplicateKeysDetector** | Catches repeated bare keys within the same scope of a TOML file |
| **TomlLowercaseKeysDetector** | Enforces lowercase key names throughout the TOML document |
| **TomlTrailingCommasDetector** | Detects trailing commas inside TOML arrays and inline tables |
| **TomlCommentClarityDetector** | Ensures TOML files with non-trivial configuration include explanatory comments |
| **TomlOrderDetector** | Detects poorly grouped table sections that are separated by excessive whitespace |
| **TomlIsoDatetimeDetector** | Enforces ISO 8601 datetime formatting in quoted TOML string values |
| **TomlFloatIntegerDetector** | Flags float literals ending in ``.0`` that should be plain integers |

---


## XML — 6 Principles, 6 Detectors

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `xml-001` | Mark up meaning, not presentation | Clarity | 5 | `ZEN-EXPLICIT-INTENT` |
| `xml-002` | Attributes for metadata, Elements for data | Structure | 5 | `ZEN-RETURN-EARLY` |
| `xml-003` | Namespaces prevent local collisions | Correctness | 6 | `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME`, `ZEN-STRICT-FENCES` |
| `xml-004` | Validity supersedes well-formedness | Correctness | 6 | `ZEN-EXPLICIT-INTENT` |
| `xml-005` | Hierarchy represents ownership | Structure | 4 | `ZEN-RETURN-EARLY` |
| `xml-006` | Closing tags complete the thought | Correctness | 5 | `ZEN-EXPLICIT-INTENT` |

??? info "`xml-001` — Mark up meaning, not presentation"
    **Prefer semantic tags over presentational markup.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Deprecated presentational tags or style attributes

??? info "`xml-002` — Attributes for metadata, Elements for data"
    **Use attributes for metadata and elements for structured data.**

    **Universal Dogmas:** `ZEN-RETURN-EARLY`

    **Common Violations:**

    - Large text content stored in attributes

??? info "`xml-003` — Namespaces prevent local collisions"
    **Declare namespaces when using prefixed elements.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME`, `ZEN-STRICT-FENCES`

    **Common Violations:**

    - Prefixed elements without xmlns declarations

??? info "`xml-004` — Validity supersedes well-formedness"
    **Provide schema references for validation.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Missing schema declaration

??? info "`xml-005` — Hierarchy represents ownership"
    **Use nested structures to represent ownership.**

    **Universal Dogmas:** `ZEN-RETURN-EARLY`

    **Common Violations:**

    - Flat repeated elements without grouping

??? info "`xml-006` — Closing tags complete the thought"
    **Avoid self-closing tags when content is expected.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Self-closing tags for non-empty elements

| Detector | What It Catches |
|----------|-----------------|
| **XmlSemanticMarkupDetector** | Flags presentational HTML-era tags and inline style attributes in XML |
| **XmlAttributeUsageDetector** | Identifies oversized attribute values that belong in child elements instead |
| **XmlNamespaceDetector** | Detects prefixed element names that lack a corresponding ``xmlns`` declaration |
| **XmlValidityDetector** | Checks for schema or DTD references that enable structural validation |
| **XmlHierarchyDetector** | Flags repeated sibling elements that lack a grouping parent container |
| **XmlClosingTagsDetector** | Identifies self-closing tags (``<tag />``) where explicit closing tags are preferred |

---


## YAML — 8 Principles, 8 Detectors

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `yaml-001` | Use consistent indentation | Readability | 6 | `ZEN-UNAMBIGUOUS-NAME` |
| `yaml-002` | Avoid tabs in indentation | Readability | 7 | `ZEN-UNAMBIGUOUS-NAME` |
| `yaml-003` | Avoid duplicate keys | Correctness | 8 | `ZEN-EXPLICIT-INTENT` |
| `yaml-004` | Use lowercase keys | Consistency | 5 | `ZEN-EXPLICIT-INTENT` |
| `yaml-005` | Keys should be self-explanatory | Naming | 5 | `ZEN-UNAMBIGUOUS-NAME` |
| `yaml-006` | Consistency provides comfort | Consistency | 5 | `ZEN-EXPLICIT-INTENT` |
| `yaml-007` | Comments explain intent | Documentation | 4 | `ZEN-UNAMBIGUOUS-NAME` |
| `yaml-008` | Strings should look like strings | Clarity | 6 | `ZEN-EXPLICIT-INTENT` |

??? info "`yaml-001` — Use consistent indentation"
    **Indentation should be consistent to avoid structural mistakes.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`

    **Common Violations:**

    - Mixed indentation widths
    - Indentation not aligned to expected spaces

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `indent_size` | `2` |

??? info "`yaml-002` — Avoid tabs in indentation"
    **YAML indentation should use spaces, not tabs.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`

    **Common Violations:**

    - Tab characters in indentation

    **Detectable Patterns:**

    - `	`

??? info "`yaml-003` — Avoid duplicate keys"
    **Duplicate keys can cause data loss when parsing.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Duplicate mapping keys

??? info "`yaml-004` — Use lowercase keys"
    **Lowercase keys improve consistency across configurations.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Uppercase characters in keys

??? info "`yaml-005` — Keys should be self-explanatory"
    **Prefer descriptive keys over terse abbreviations.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`

    **Common Violations:**

    - Single-letter or cryptic keys

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `min_key_length` | `3` |

??? info "`yaml-006` — Consistency provides comfort"
    **Use a consistent list style throughout the file.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Mixed list markers (- and *)

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `allowed_list_markers` | `['-']` |

??? info "`yaml-007` — Comments explain intent"
    **Document complex sections with comments.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`

    **Common Violations:**

    - No comments in a complex configuration

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `min_comment_lines` | `1` |
    | `min_nonempty_lines` | `5` |

??? info "`yaml-008` — Strings should look like strings"
    **Quote strings with spaces or special characters.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`

    **Common Violations:**

    - Unquoted strings with special characters

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `require_quotes_for_specials` | `True` |

| Detector | What It Catches |
|----------|-----------------|
| **YamlIndentationDetector** | Enforces uniform indentation width across all non-blank, non-comment lines |
| **YamlNoTabsDetector** | Detects tab characters anywhere in YAML content |
| **YamlDuplicateKeysDetector** | Catches repeated top-level mapping keys that cause silent data loss |
| **YamlLowercaseKeysDetector** | Enforces lowercase mapping keys throughout the YAML document |
| **YamlKeyClarityDetector** | Flags overly short mapping keys that sacrifice readability for brevity |
| **YamlConsistencyDetector** | Ensures a single, consistent list-marker style is used throughout the document |
| **YamlCommentIntentDetector** | Ensures complex YAML files include explanatory comments |
| **YamlStringStyleDetector** | Flags unquoted string values that contain spaces or special YAML characters |

---


## See Also

- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
