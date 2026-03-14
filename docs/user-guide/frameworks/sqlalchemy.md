---
title: SQLAlchemy
description: "6 zen principles enforced by 6 detectors: Explicit database access with disciplined session lifecycles and parameterized queries.."
icon: material/database
tags:
  - SQLAlchemy
---

# SQLAlchemy




## Zen Principles

6 principles across 4 categories, drawn from [SQLAlchemy 2.0 documentation](https://docs.sqlalchemy.org/en/20/).

<div class="grid" markdown>

:material-tag-outline: **Correctness** · 1 principle
:material-tag-outline: **Idioms** · 2 principles
:material-tag-outline: **Performance** · 2 principles
:material-tag-outline: **Security** · 1 principle

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `sqlalchemy-001` | text queries must not interpolate values directly | Security | 10 | `ZEN-STRICT-FENCES`, `ZEN-FAIL-FAST` |
| `sqlalchemy-002` | Session lifecycles should be explicit | Correctness | 9 | `ZEN-STRICT-FENCES`, `ZEN-EXPLICIT-INTENT` |
| `sqlalchemy-003` | SQLAlchemy 2.x code should prefer mapped_column over Column in ORM models | Idioms | 6 | `ZEN-RIGHT-ABSTRACTION` |
| `sqlalchemy-004` | DeclarativeBase should replace declarative_base in 2.x-style code | Idioms | 5 | `ZEN-RIGHT-ABSTRACTION` |
| `sqlalchemy-005` | relationship loading should be an explicit choice | Performance | 7 | `ZEN-PROPORTIONATE-COMPLEXITY`, `ZEN-EXPLICIT-INTENT` |
| `sqlalchemy-006` | Bulk inserts should avoid session.add inside loops | Performance | 6 | `ZEN-PROPORTIONATE-COMPLEXITY` |

??? info "`sqlalchemy-001` — text queries must not interpolate values directly"
    **Interpolated SQL text bypasses SQLAlchemy's parameter handling and increases injection risk.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`, `ZEN-FAIL-FAST`
    **Common Violations:**

    - text queries must not interpolate values directly

    **Detectable Patterns:**

    - `re:text\(\s*(?:f[\"\']|[rbuf]*[\"\'][^\"\']*%s?[\"\']\s*%)`

    !!! tip "Recommended Fix"
        Use bind parameters such as :name and pass values separately.

??? info "`sqlalchemy-002` — Session lifecycles should be explicit"
    **Ad-hoc Session() calls often hide connection management and teardown responsibilities.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Session lifecycles should be explicit

    **Detectable Patterns:**

    - `re:\bSession\(\)`

    !!! tip "Recommended Fix"
        Prefer a context manager or a well-scoped session factory pattern.

??? info "`sqlalchemy-003` — SQLAlchemy 2.x code should prefer mapped_column over Column in ORM models"
    **mapped_column is the modern declarative field API in SQLAlchemy 2.x ORM models.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - SQLAlchemy 2.x code should prefer mapped_column over Column in ORM models

    **Detectable Patterns:**

    - `re:\bColumn\(`

    !!! tip "Recommended Fix"
        Use mapped_column() in declarative ORM models when targeting SQLAlchemy 2.x.

??? info "`sqlalchemy-004` — DeclarativeBase should replace declarative_base in 2.x-style code"
    **DeclarativeBase is the clearer modern base-class pattern for SQLAlchemy 2.x.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - DeclarativeBase should replace declarative_base in 2.x-style code

    **Detectable Patterns:**

    - `re:\bdeclarative_base\(`

    !!! tip "Recommended Fix"
        Define a DeclarativeBase subclass instead of calling declarative_base().

??? info "`sqlalchemy-005` — relationship loading should be an explicit choice"
    **Implicit relationship loading defaults can hide N+1 query behavior and make data access unpredictable.**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - relationship loading should be an explicit choice

    **Detectable Patterns:**

    - `re:relationship\((?:(?!lazy=)[\s\S])*?\)`

    !!! tip "Recommended Fix"
        Specify lazy=, selectinload, or another explicit loading strategy.

??? info "`sqlalchemy-006` — Bulk inserts should avoid session.add inside loops"
    **session.add inside large loops is a common throughput bottleneck and often indicates missing bulk primitives.**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - Bulk inserts should avoid session.add inside loops

    **Detectable Patterns:**

    - `re:for\s+.+:\s*[\s\S]*?session\.add\(`

    !!! tip "Recommended Fix"
        Use insert(), bulk APIs, or batched unit-of-work patterns for large writes.


## Detector Catalog

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **SqlalchemySessionScopeDetector** | Concrete detector binding for SqlalchemySessionScopeDetector | `sqlalchemy-002` |

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **SqlalchemyDeclarativeBaseDetector** | Concrete detector binding for SqlalchemyDeclarativeBaseDetector | `sqlalchemy-004` |
| **SqlalchemyMappedColumnDetector** | Concrete detector binding for SqlalchemyMappedColumnDetector | `sqlalchemy-003` |

### Performance

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **SqlalchemyBulkInsertDetector** | Concrete detector binding for SqlalchemyBulkInsertDetector | `sqlalchemy-006` |
| **SqlalchemyRelationshipLoadingDetector** | Concrete detector binding for SqlalchemyRelationshipLoadingDetector | `sqlalchemy-005` |

### Security

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **SqlalchemyParameterizedTextDetector** | Concrete detector binding for SqlalchemyParameterizedTextDetector | `sqlalchemy-001` |


??? example "Principle → Detector Wiring"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    sqlalchemy_001["sqlalchemy-001<br/>text queries must not int..."]
    sqlalchemy_002["sqlalchemy-002<br/>Session lifecycles should..."]
    sqlalchemy_003["sqlalchemy-003<br/>SQLAlchemy 2.x code shoul..."]
    sqlalchemy_004["sqlalchemy-004<br/>DeclarativeBase should re..."]
    sqlalchemy_005["sqlalchemy-005<br/>relationship loading shou..."]
    sqlalchemy_006["sqlalchemy-006<br/>Bulk inserts should avoid..."]
    det_SqlalchemyBulkInsertDetector["Sqlalchemy Bulk<br/>Insert"]
    sqlalchemy_006 --> det_SqlalchemyBulkInsertDetector
    det_SqlalchemyDeclarativeBaseDetector["Sqlalchemy Declarative<br/>Base"]
    sqlalchemy_004 --> det_SqlalchemyDeclarativeBaseDetector
    det_SqlalchemyMappedColumnDetector["Sqlalchemy Mapped<br/>Column"]
    sqlalchemy_003 --> det_SqlalchemyMappedColumnDetector
    det_SqlalchemyParameterizedTextDetector["Sqlalchemy Parameterized<br/>Text"]
    sqlalchemy_001 --> det_SqlalchemyParameterizedTextDetector
    det_SqlalchemyRelationshipLoadingDetector["Sqlalchemy Relationship<br/>Loading"]
    sqlalchemy_005 --> det_SqlalchemyRelationshipLoadingDetector
    det_SqlalchemySessionScopeDetector["Sqlalchemy Session<br/>Scope"]
    sqlalchemy_002 --> det_SqlalchemySessionScopeDetector
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
        class det_01["Sqlalchemy Bulk Insert"]
        ViolationDetector <|-- det_01
        class det_02["Sqlalchemy Declarative Base"]
        ViolationDetector <|-- det_02
        class det_03["Sqlalchemy Mapped Column"]
        ViolationDetector <|-- det_03
        class det_04["Sqlalchemy Parameterized Text"]
        ViolationDetector <|-- det_04
        class det_05["Sqlalchemy Relationship Loading"]
        ViolationDetector <|-- det_05
        class det_06["Sqlalchemy Session Scope"]
        ViolationDetector <|-- det_06
    ```

??? example "Analysis Pipeline"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 50, "rankSpacing": 70}}}%%
    flowchart TD
    Source(["Source Code"]) --> Parse["Parse & Tokenize"]
    Parse --> Metrics["Compute Metrics"]
    Metrics --> Pipeline{"6 Detectors"}
    Pipeline --> Collect["Aggregate Violations"]
    Collect --> Result(["AnalysisResult<br/>6 principles"])
    ```

??? example "Analysis States"
    ```mermaid
    %%{init: {"theme": "base"}}%%
    stateDiagram-v2
        [*] --> Ready
        Ready --> Parsing : analyze(code)
        Parsing --> Computing : AST ready
        Computing --> Detecting : metrics ready
        Detecting --> Reporting : 6 detectors run
        Reporting --> [*] : AnalysisResult
        Parsing --> Reporting : parse error (best-effort)
    ```

## Configuration

```yaml
languages:
  sqlalchemy:
    enabled: true
    pipeline:
```


## See Also

- [Python](python.md) — Parent language analysis and shared Python architecture
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Prompt Generation](../prompt-generation.md) — Generate remediation prompts for database access issues
