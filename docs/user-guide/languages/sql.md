---
title: SQL
description: "9 zen principles enforced by 9 detectors: Pragmatic SQL correctness, security, and performance hygiene."
icon: material/database
tags:
  - SQL
---

# SQL

SQL queries are production code: they shape correctness, latency, and security just as much as application logic. MCP Zen of Languages applies **9 practical SQL principles** that catch fragile query patterns before they become outages, regressions, or data quality incidents.

## Zen Principles

9 principles across 5 categories, drawn from [ANSI SQL + production database best practices](https://www.iso.org/standard/76584.html).

<div class="grid" markdown>

:material-tag-outline: **Clarity** · 1 principle
:material-tag-outline: **Correctness** · 3 principles
:material-tag-outline: **Performance** · 3 principles
:material-tag-outline: **Readability** · 1 principle
:material-tag-outline: **Security** · 1 principle

</div>

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `sql-001` | Never use SELECT * | Performance | 6 |
| `sql-002` | Always include INSERT column lists | Correctness | 7 |
| `sql-003` | Prefer parameterized SQL over dynamic concatenation | Security | 9 |
| `sql-004` | Avoid NOLOCK and dirty reads | Correctness | 8 |
| `sql-005` | Avoid implicit type coercion in JOIN predicates | Performance | 6 |
| `sql-006` | Bound result sets with WHERE/LIMIT/TOP | Performance | 5 |
| `sql-007` | Use descriptive table aliases | Clarity | 4 |
| `sql-008` | Keep transaction boundaries balanced | Correctness | 8 |
| `sql-009` | Prefer explicit JOIN syntax over ANSI-89 comma joins | Readability | 6 |

??? info "`sql-001` — Never use SELECT *"
    **Enumerate explicit columns to avoid fragile, over-fetching queries.**

    **Common Violations:**

    - SELECT * detected

    **Detectable Patterns:**

    - `(?i)select\s+\*\s+from`

??? info "`sql-002` — Always include INSERT column lists"
    **INSERT statements without a column list break on schema changes.**

    **Common Violations:**

    - INSERT INTO table VALUES (...) without explicit columns

    **Detectable Patterns:**

    - `(?i)insert\s+into\s+\w+\s+values\s*\(`

??? info "`sql-003` — Prefer parameterized SQL over dynamic concatenation"
    **Dynamic SQL string concatenation increases SQL injection risk.**

    **Common Violations:**

    - EXEC/EXECUTE with concatenated SQL string

    **Detectable Patterns:**

    - `(?i)exec(?:ute)?\s*\(?.*['\"]\s*(?:\+|\|\|)`

    !!! tip "Recommended Fix"
        Use bind parameters or prepared statements instead of runtime SQL string assembly.

??? info "`sql-004` — Avoid NOLOCK and dirty reads"
    **WITH (NOLOCK) can silently read uncommitted and inconsistent data.**

    **Common Violations:**

    - NOLOCK table hint used

    **Detectable Patterns:**

    - `(?i)with\s*\(\s*nolock\s*\)`

??? info "`sql-005` — Avoid implicit type coercion in JOIN predicates"
    **Type mismatches in JOIN conditions often force index-unfriendly scans.**

    **Common Violations:**

    - JOIN predicate applies CAST/CONVERT in comparison

    **Detectable Patterns:**

    - `(?i)join[\s\S]*?on[\s\S]*?(cast\s*\(|convert\s*\()`

??? info "`sql-006` — Bound result sets with WHERE/LIMIT/TOP"
    **Unbounded selects on large relations are costly and often accidental.**

    **Common Violations:**

    - SELECT query without WHERE, LIMIT, or TOP

??? info "`sql-007` — Use descriptive table aliases"
    **Single-letter or cryptic aliases reduce readability and maintenance speed.**

    **Common Violations:**

    - Single-letter table alias detected

??? info "`sql-008` — Keep transaction boundaries balanced"
    **BEGIN TRANSACTION without COMMIT/ROLLBACK in the same file risks dangling transactions.**

    **Common Violations:**

    - BEGIN TRANSACTION without matching COMMIT or ROLLBACK

    **Detectable Patterns:**

    - `(?i)\bbegin\s+tran(?:saction)?\b`

??? info "`sql-009` — Prefer explicit JOIN syntax over ANSI-89 comma joins"
    **Comma-separated FROM joins are deprecated and less explicit than JOIN ... ON.**

    **Common Violations:**

    - ANSI-89 comma join syntax detected

    **Detectable Patterns:**

    - `(?i)from\s+[^;]*,\s*[^;]*where`

    !!! tip "Recommended Fix"
        Replace comma joins with explicit INNER JOIN/LEFT JOIN and ON predicates.


## Detector Catalog

### Clarity

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **SqlAliasClarityDetector** | Flag aliases that are shorter than configured readability threshold | `sql-007` |

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **SqlInsertColumnListDetector** | Flag INSERT statements that omit explicit target columns | `sql-002` |
| **SqlNolockDetector** | Flag NOLOCK table-hint usage | `sql-004` |
| **SqlTransactionBoundaryDetector** | Ensure explicit transaction blocks are balanced | `sql-008` |

### Performance

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **SqlSelectStarDetector** | Flag ``SELECT *`` usage | `sql-001` |
| **SqlImplicitJoinCoercionDetector** | Detect join predicates that cast either side of the comparison | `sql-005` |
| **SqlUnboundedQueryDetector** | Warn on unbounded SELECT queries | `sql-006` |

### Readability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **SqlAnsi89JoinDetector** | Detect deprecated ANSI-89 comma-join syntax | `sql-009` |

### Security

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **SqlDynamicSqlDetector** | Flag risky dynamic SQL execution via string concatenation | `sql-003` |


??? example "Principle → Detector Wiring"
    ```mermaid
    graph LR
    sql_001["sql-001<br/>Never use SELECT *"]
    sql_002["sql-002<br/>Always include INSERT column lists"]
    sql_003["sql-003<br/>Prefer parameterized SQL over dynamic co..."]
    sql_004["sql-004<br/>Avoid NOLOCK and dirty reads"]
    sql_005["sql-005<br/>Avoid implicit type coercion in JOIN pre..."]
    sql_006["sql-006<br/>Bound result sets with WHERE/LIMIT/TOP"]
    sql_007["sql-007<br/>Use descriptive table aliases"]
    sql_008["sql-008<br/>Keep transaction boundaries balanced"]
    sql_009["sql-009<br/>Prefer explicit JOIN syntax over ANSI-89..."]
    det_SqlAliasClarityDetector["SqlAliasClarityDetector"]
    sql_007 --> det_SqlAliasClarityDetector
    det_SqlAnsi89JoinDetector["SqlAnsi89JoinDetector"]
    sql_009 --> det_SqlAnsi89JoinDetector
    det_SqlDynamicSqlDetector["SqlDynamicSqlDetector"]
    sql_003 --> det_SqlDynamicSqlDetector
    det_SqlImplicitJoinCoercionDetector["SqlImplicitJoinCoercionDetector"]
    sql_005 --> det_SqlImplicitJoinCoercionDetector
    det_SqlInsertColumnListDetector["SqlInsertColumnListDetector"]
    sql_002 --> det_SqlInsertColumnListDetector
    det_SqlNolockDetector["SqlNolockDetector"]
    sql_004 --> det_SqlNolockDetector
    det_SqlSelectStarDetector["SqlSelectStarDetector"]
    sql_001 --> det_SqlSelectStarDetector
    det_SqlTransactionBoundaryDetector["SqlTransactionBoundaryDetector"]
    sql_008 --> det_SqlTransactionBoundaryDetector
    det_SqlUnboundedQueryDetector["SqlUnboundedQueryDetector"]
    sql_006 --> det_SqlUnboundedQueryDetector
    classDef principle fill:#4051b5,color:#fff,stroke:none
    classDef detector fill:#26a269,color:#fff,stroke:none
    class sql_001 principle
    class sql_002 principle
    class sql_003 principle
    class sql_004 principle
    class sql_005 principle
    class sql_006 principle
    class sql_007 principle
    class sql_008 principle
    class sql_009 principle
    class det_SqlAliasClarityDetector detector
    class det_SqlAnsi89JoinDetector detector
    class det_SqlDynamicSqlDetector detector
    class det_SqlImplicitJoinCoercionDetector detector
    class det_SqlInsertColumnListDetector detector
    class det_SqlNolockDetector detector
    class det_SqlSelectStarDetector detector
    class det_SqlTransactionBoundaryDetector detector
    class det_SqlUnboundedQueryDetector detector
    ```

## Configuration

```yaml
languages:
  sql:
    enabled: true
    pipeline:
      - type: sql-001
        dialect: postgres
      - type: sql-002
        dialect: postgres
      - type: sql-003
        dialect: postgres
      - type: sql-004
        dialect: postgres
      - type: sql-005
        dialect: postgres
      - type: sql-006
        dialect: postgres
      - type: sql-007
        min_alias_length: 2
        dialect: postgres
      - type: sql-008
        dialect: postgres
      - type: sql-009
        dialect: postgres
```


## See Also

- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
- [Prompt Generation](../prompt-generation.md) — Generate SQL remediation guidance
