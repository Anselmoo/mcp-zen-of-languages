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

## JSON — 6 Principles, 6 Detectors

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `json-001` | Strictness enables interoperability | Correctness | 7 |
| `json-002` | Structure implies Schema | Structure | 6 |
| `json-003` | Dates should be standard | Correctness | 6 |
| `json-004` | Null is a value, missing is unknown | Correctness | 5 |
| `json-005` | Keys are case-sensitive identifiers | Naming | 5 |
| `json-006` | Arrays are ordered, Objects are not | Clarity | 4 |

??? info "`json-001` — Strictness enables interoperability"
    **Avoid comments and trailing commas for strict JSON compliance.**

    **Common Violations:**

    - Comments in JSON
    - Trailing commas in objects/arrays

    **Detectable Patterns:**

    - `//`
    - `/\*`
    - `,\]`
    - `,\}`

??? info "`json-002` — Structure implies Schema"
    **Keep object shapes consistent within arrays.**

    **Common Violations:**

    - Array objects with inconsistent keys

??? info "`json-003` — Dates should be standard"
    **Use ISO 8601 date/time strings.**

    **Common Violations:**

    - Non-ISO date strings

??? info "`json-004` — Null is a value, missing is unknown"
    **Prefer explicit nulls for optional keys when applicable.**

    **Common Violations:**

    - Optional keys missing without nulls

??? info "`json-005` — Keys are case-sensitive identifiers"
    **Use consistent key casing (e.g., lower_snake or lowerCamel).**

    **Common Violations:**

    - Mixed key casing

??? info "`json-006` — Arrays are ordered, Objects are not"
    **Do not rely on object key order; use arrays when ordering matters.**

    **Common Violations:**

    - Object keys imply ordering

| Detector | What It Catches |
|----------|-----------------|
| **JsonStrictnessDetector** | Flags non-standard JSON extensions such as comments and trailing commas |
| **JsonSchemaConsistencyDetector** | Detects inconsistent object shapes inside top-level JSON arrays |
| **JsonDateFormatDetector** | Identifies date strings that deviate from ISO 8601 formatting |
| **JsonNullHandlingDetector** | Reports top-level object keys whose values are explicitly ``null`` |
| **JsonKeyCasingDetector** | Enforces consistent letter casing across all keys in a JSON object |
| **JsonArrayOrderDetector** | Checks for ordered collections and duplicate keys that hint at misused objects |

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
