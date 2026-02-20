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

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `json-001` | Choose strictness intentionally | Correctness | 7 |
| `json-002` | Keep object depth understandable | Structure | 6 |
| `json-003` | Keys must be unique | Correctness | 8 |
| `json-004` | Avoid magic string repetition | Clarity | 5 |
| `json-005` | Keys are case-sensitive identifiers | Naming | 5 |
| `json-006` | Keep inline arrays bounded | Structure | 4 |
| `json-007` | Prefer omission over null sprawl | Correctness | 5 |
| `json-008` | Dates must follow ISO 8601 | Correctness | 6 |
| `json-009` | Prefer key omission over explicit null | Clarity | 5 |

??? info "`json-001` — Choose strictness intentionally"
    **Trailing commas should be rejected for JSON unless JSON5 is explicitly targeted.**

    **Common Violations:**

    - Trailing commas in strict JSON mode

    **Detectable Patterns:**

    - `,\]`
    - `,\}`

??? info "`json-002` — Keep object depth understandable"
    **Deeply nested objects/arrays are hard to reason about and validate.**

    **Common Violations:**

    - Nesting depth exceeds configured threshold

??? info "`json-003` — Keys must be unique"
    **Duplicate object keys silently override values in many parsers.**

    **Common Violations:**

    - Duplicate keys in an object

??? info "`json-004` — Avoid magic string repetition"
    **Repeated string literals should be extracted or referenced consistently.**

    **Common Violations:**

    - Repeated magic string values

??? info "`json-005` — Keys are case-sensitive identifiers"
    **Avoid mixing camelCase, snake_case, and PascalCase at the same object level.**

    **Common Violations:**

    - Mixed key casing at same object level

??? info "`json-006` — Keep inline arrays bounded"
    **Very large inline arrays are hard to review and often belong in separate data files.**

    **Common Violations:**

    - Oversized inline arrays

??? info "`json-007` — Prefer omission over null sprawl"
    **Excessive null usage usually indicates optional keys that can be omitted.**

    **Common Violations:**

    - Excessive null values across the document

??? info "`json-008` — Dates must follow ISO 8601"
    **Date strings should use ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ) for unambiguous, sortable representation. Locale-dependent formats such as MM/DD/YYYY create parsing ambiguity.**

    **Common Violations:**

    - Non-ISO 8601 date string detected

    **Detectable Patterns:**

    - `\d{1,2}/\d{1,2}/\d{2,4}`
    - `\d{1,2}\.\d{1,2}\.\d{4}`

??? info "`json-009` — Prefer key omission over explicit null"
    **Top-level object keys whose value is explicitly null should be omitted entirely. Explicit null at the top level signals optional absence, which is better expressed by omitting the key.**

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


## TOML — 8 Principles, 8 Detectors

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `toml-001` | Avoid inline tables | Readability | 6 |
| `toml-002` | Avoid duplicate keys | Correctness | 8 |
| `toml-003` | Use lowercase keys | Consistency | 5 |
| `toml-004` | Avoid trailing commas | Readability | 5 |
| `toml-005` | Clarity is paramount | Clarity | 5 |
| `toml-006` | Order implies importance | Organization | 4 |
| `toml-007` | Time is specific | Correctness | 6 |
| `toml-008` | Floats are not integers | Correctness | 6 |

??? info "`toml-001` — Avoid inline tables"
    **Inline tables are harder to read; use full tables instead.**

    **Common Violations:**

    - Inline table definitions in assignments

??? info "`toml-002` — Avoid duplicate keys"
    **Duplicate keys can overwrite previous values.**

    **Common Violations:**

    - Duplicate key definitions

??? info "`toml-003` — Use lowercase keys"
    **Lowercase keys improve consistency across configurations.**

    **Common Violations:**

    - Uppercase characters in keys

??? info "`toml-004` — Avoid trailing commas"
    **Trailing commas reduce readability in TOML arrays/tables.**

    **Common Violations:**

    - Trailing commas before closing brackets

??? info "`toml-005` — Clarity is paramount"
    **Explain magic values with comments.**

    **Common Violations:**

    - Magic values without comments

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `min_comment_lines` | `1` |

??? info "`toml-006` — Order implies importance"
    **Group related keys together before arrays or tables.**

    **Common Violations:**

    - Repeated table headers spread apart

??? info "`toml-007` — Time is specific"
    **Use ISO 8601 timestamps for dates.**

    **Common Violations:**

    - Non-ISO date strings

??? info "`toml-008` — Floats are not integers"
    **Use integer types where appropriate, avoid decimal .0 values.**

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

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `xml-001` | Mark up meaning, not presentation | Clarity | 5 |
| `xml-002` | Attributes for metadata, Elements for data | Structure | 5 |
| `xml-003` | Namespaces prevent local collisions | Correctness | 6 |
| `xml-004` | Validity supersedes well-formedness | Correctness | 6 |
| `xml-005` | Hierarchy represents ownership | Structure | 4 |
| `xml-006` | Closing tags complete the thought | Correctness | 5 |

??? info "`xml-001` — Mark up meaning, not presentation"
    **Prefer semantic tags over presentational markup.**

    **Common Violations:**

    - Deprecated presentational tags or style attributes

??? info "`xml-002` — Attributes for metadata, Elements for data"
    **Use attributes for metadata and elements for structured data.**

    **Common Violations:**

    - Large text content stored in attributes

??? info "`xml-003` — Namespaces prevent local collisions"
    **Declare namespaces when using prefixed elements.**

    **Common Violations:**

    - Prefixed elements without xmlns declarations

??? info "`xml-004` — Validity supersedes well-formedness"
    **Provide schema references for validation.**

    **Common Violations:**

    - Missing schema declaration

??? info "`xml-005` — Hierarchy represents ownership"
    **Use nested structures to represent ownership.**

    **Common Violations:**

    - Flat repeated elements without grouping

??? info "`xml-006` — Closing tags complete the thought"
    **Avoid self-closing tags when content is expected.**

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

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `yaml-001` | Use consistent indentation | Readability | 6 |
| `yaml-002` | Avoid tabs in indentation | Readability | 7 |
| `yaml-003` | Avoid duplicate keys | Correctness | 8 |
| `yaml-004` | Use lowercase keys | Consistency | 5 |
| `yaml-005` | Keys should be self-explanatory | Naming | 5 |
| `yaml-006` | Consistency provides comfort | Consistency | 5 |
| `yaml-007` | Comments explain intent | Documentation | 4 |
| `yaml-008` | Strings should look like strings | Clarity | 6 |

??? info "`yaml-001` — Use consistent indentation"
    **Indentation should be consistent to avoid structural mistakes.**

    **Common Violations:**

    - Mixed indentation widths
    - Indentation not aligned to expected spaces

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `indent_size` | `2` |

??? info "`yaml-002` — Avoid tabs in indentation"
    **YAML indentation should use spaces, not tabs.**

    **Common Violations:**

    - Tab characters in indentation

    **Detectable Patterns:**

    - `	`

??? info "`yaml-003` — Avoid duplicate keys"
    **Duplicate keys can cause data loss when parsing.**

    **Common Violations:**

    - Duplicate mapping keys

??? info "`yaml-004` — Use lowercase keys"
    **Lowercase keys improve consistency across configurations.**

    **Common Violations:**

    - Uppercase characters in keys

??? info "`yaml-005` — Keys should be self-explanatory"
    **Prefer descriptive keys over terse abbreviations.**

    **Common Violations:**

    - Single-letter or cryptic keys

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `min_key_length` | `3` |

??? info "`yaml-006` — Consistency provides comfort"
    **Use a consistent list style throughout the file.**

    **Common Violations:**

    - Mixed list markers (- and *)

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `allowed_list_markers` | `['-']` |

??? info "`yaml-007` — Comments explain intent"
    **Document complex sections with comments.**

    **Common Violations:**

    - No comments in a complex configuration

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `min_comment_lines` | `1` |
    | `min_nonempty_lines` | `5` |

??? info "`yaml-008` — Strings should look like strings"
    **Quote strings with spaces or special characters.**

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
