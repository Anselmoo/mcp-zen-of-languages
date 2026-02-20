---
title: JSON / JSON5
description: "9 zen principles enforced by 9 detectors: RFC 8259 JSON + practical JSON5 interoperability."
icon: material/code-json
tags:
  - JSON
  - JSON5
  - Config Formats
---

# JSON / JSON5

JSON is the lingua franca of configuration and data interchange — but its simplicity hides a surprising number of ways to write confusing, brittle, or ambiguous files. MCP Zen of Languages encodes **9 structural and semantic principles** that catch the patterns where JSON clarity quietly breaks down, while also supporting the relaxed syntax of JSON5 where explicitly targeted.

!!! info "JSON5 support"
    Detectors are JSON5‑aware. Set `target_format: json5` in your pipeline config
    to allow trailing commas and other JSON5 relaxations without false positives.

## Zen Principles

9 principles across 4 categories, drawn from [RFC 8259 JSON](https://www.json.org/json-en.html) and practical JSON5 interoperability.

<div class="grid" markdown>

:material-tag-outline: **Clarity** · 2 principles
:material-tag-outline: **Correctness** · 4 principles
:material-tag-outline: **Naming** · 1 principle
:material-tag-outline: **Structure** · 2 principles

</div>

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

    Trailing commas are valid JSON5 but illegal in strict JSON (RFC 8259). Many
    tools silently strip them during parsing, making them an invisible source of
    diff noise and interoperability failures.

    **Common Violations:**

    - Trailing commas in strict JSON mode

    **Detectable Patterns:**

    - `,\]`
    - `,\}`

    **Configuration:**

    | Parameter | Default | Description |
    |-----------|---------|-------------|
    | `target_format` | `json` | Target format: `json` (strict) or `json5` |
    | `allow_trailing_commas` | `False` | Explicitly permit trailing commas |

    **Example — violation:**

    ```json
    {
      "name": "my-package",
      "version": "1.0.0",
    }
    ```

    **Example — compliant (JSON5):**

    ```json5
    // zen-config: target_format=json5
    {
      "name": "my-package",
      "version": "1.0.0",
    }
    ```

??? info "`json-002` — Keep object depth understandable"
    **Deeply nested objects/arrays are hard to reason about and validate.**

    Beyond a few levels of nesting reviewers lose the mental model of which
    object they are editing. Flat schemas or $ref-based splitting improve
    readability and testability.

    **Common Violations:**

    - Nesting depth exceeds configured threshold

    **Configuration:**

    | Parameter | Default | Description |
    |-----------|---------|-------------|
    | `max_depth` | `5` | Maximum allowed nesting depth |

    **Example — violation (depth 7):**

    ```json
    {"a": {"b": {"c": {"d": {"e": {"f": {"g": 1}}}}}}}
    ```

??? info "`json-003` — Keys must be unique"
    **Duplicate object keys silently override values in many parsers.**

    RFC 8259 §4 states that key uniqueness *should* apply, but most parsers
    accept duplicates and retain — or discard — earlier values without warning.
    This leads to latent bugs that are invisible in code review.

    **Common Violations:**

    - Duplicate keys in an object

    **Example — violation:**

    ```json
    {
      "timeout": 30,
      "timeout": 60
    }
    ```

??? info "`json-004` — Avoid magic string repetition"
    **Repeated string literals should be extracted or referenced consistently.**

    When the same string value appears in many places (e.g. a base URL, an
    environment name), a single typo or an update leaves files in an
    inconsistent state. Consider JSON Schema `$ref` anchors or a shared
    constants fragment.

    **Common Violations:**

    - Repeated magic string values

    **Configuration:**

    | Parameter | Default | Description |
    |-----------|---------|-------------|
    | `min_repetition` | `3` | Minimum occurrences to flag |
    | `min_length` | `4` | Minimum string length to consider |

    **Example — violation:**

    ```json
    {
      "dev_url":  "https://api.example.com",
      "test_url": "https://api.example.com",
      "prod_url": "https://api.example.com"
    }
    ```

??? info "`json-005` — Keys are case-sensitive identifiers"
    **Avoid mixing camelCase, snake_case, and PascalCase at the same object level.**

    JSON keys are case-sensitive identifiers. Mixing conventions at the same
    object level creates inconsistency that makes it harder to predict key names
    programmatically.

    **Common Violations:**

    - Mixed key casing at same object level

    **Example — violation:**

    ```json
    {
      "firstName": "Alice",
      "last_name": "Smith",
      "Email": "alice@example.com"
    }
    ```

??? info "`json-006` — Keep inline arrays bounded"
    **Very large inline arrays are hard to review and often belong in separate data files.**

    Arrays with many elements clutter configuration files and obscure intent.
    Move large data sets to separate files and reference them by path.

    **Common Violations:**

    - Oversized inline arrays

    **Configuration:**

    | Parameter | Default | Description |
    |-----------|---------|-------------|
    | `max_inline_array_size` | `20` | Maximum permitted inline array length |

??? info "`json-007` — Prefer omission over null sprawl"
    **Excessive null usage usually indicates optional keys that can be omitted.**

    A document littered with `null` values signals that the schema was designed
    around a relational model where absent values must be declared. JSON schemas
    benefit from key omission — absent means absent.

    **Common Violations:**

    - Excessive null values across the document

    **Configuration:**

    | Parameter | Default | Description |
    |-----------|---------|-------------|
    | `max_null_values` | `3` | Maximum total null values across the document |

??? info "`json-008` — Dates must follow ISO 8601"
    **Date strings should use ISO 8601 format for unambiguous, sortable representation.**

    JSON has no native date type — dates are encoded as strings. Locale-dependent
    formats such as `MM/DD/YYYY` are ambiguous (is `02/03/2024` the 2nd of March
    or the 3rd of February?). `YYYY-MM-DD` and `YYYY-MM-DDTHH:MM:SSZ` sort
    correctly as strings, interoperate across time zones, and are universally
    recognised.

    **Common Violations:**

    - Non-ISO 8601 date string detected

    **Detectable Patterns:**

    - `\d{1,2}/\d{1,2}/\d{2,4}` (MM/DD/YYYY)
    - `\d{1,2}\.\d{1,2}\.\d{4}` (DD.MM.YYYY)

    **Configuration:**

    | Parameter | Default | Description |
    |-----------|---------|-------------|
    | `common_date_keys` | `["date","time","created",…]` | Key name fragments used to identify probable date fields |

    **Example — violation:**

    ```json
    {
      "created_at": "03/15/2024",
      "expires":    "31.12.2025"
    }
    ```

    **Example — compliant:**

    ```json
    {
      "created_at": "2024-03-15",
      "expires":    "2025-12-31T23:59:59Z"
    }
    ```

??? info "`json-009` — Prefer key omission over explicit null"
    **Top-level object keys set explicitly to null should be omitted entirely.**

    Setting a top-level key to `null` communicates intentional absence but adds
    noise to the schema. In most cases the correct action is to omit the key
    altogether, letting consumers default-construct missing values rather than
    handle explicit `null`.

    **Common Violations:**

    - Top-level key set to explicit null

    **Configuration:**

    | Parameter | Default | Description |
    |-----------|---------|-------------|
    | `max_top_level_nulls` | `0` | Maximum top-level keys allowed to be `null` |

    **Example — violation:**

    ```json
    {
      "name": "my-service",
      "database": null,
      "cache": null
    }
    ```

    **Example — compliant:**

    ```json
    {
      "name": "my-service"
    }
    ```

## Detectors

| Detector | Rule | What It Catches |
|----------|------|-----------------|
| **JsonStrictnessDetector** | `json-001` | Trailing commas in strict JSON mode |
| **JsonSchemaConsistencyDetector** | `json-002` | Nesting depth beyond the configured threshold |
| **JsonDuplicateKeyDetector** | `json-003` | Duplicate object keys that silently override values |
| **JsonMagicStringDetector** | `json-004` | Repeated string literals that should be shared constants |
| **JsonKeyCasingDetector** | `json-005` | Mixed key-casing conventions at the same object level |
| **JsonArrayOrderDetector** | `json-006` | Inline arrays exceeding the configured size limit |
| **JsonNullSprawlDetector** | `json-007` | Excessive null count across the entire document |
| **JsonDateFormatDetector** | `json-008` | Date strings that are not ISO 8601 format |
| **JsonNullHandlingDetector** | `json-009` | Top-level keys explicitly set to `null` |

## Configuration

Add a `json` key under `languages` in your `zen-config.yaml` to override
defaults for any detector:

```yaml
languages:
  json:
    pipeline:
      - type: json-001
        target_format: json5       # permit trailing commas in JSON5 files
      - type: json-002
        max_depth: 4               # stricter nesting limit
      - type: json-004
        min_repetition: 2          # flag any repeated string
        min_length: 6
      - type: json-006
        max_inline_array_size: 10
      - type: json-007
        max_null_values: 0         # zero tolerance
      - type: json-008
        common_date_keys:
          - date
          - time
          - created
          - updated
          - expires
      - type: json-009
        max_top_level_nulls: 0
```

## See Also

- [Config Formats Overview](config-formats.md) — JSON alongside TOML, XML, and YAML
- [Configuration Reference](../configuration.md) — Full pipeline override syntax
- [Understanding Violations](../understanding-violations.md) — Severity scale and remediation
