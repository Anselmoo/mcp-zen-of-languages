---
title: Pydantic
description: "8 zen principles enforced by 8 detectors: Declarative data validation driven by explicit type annotations and fail-fast contracts.."
icon: material/shield-check-outline
tags:
  - Pydantic
---

# Pydantic




## Zen Principles

8 principles across 2 categories, drawn from [Pydantic v2 documentation](https://docs.pydantic.dev/latest/).

<div class="grid" markdown>

:material-tag-outline: **Correctness** · 1 principle
:material-tag-outline: **Idioms** · 7 principles

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `pydantic-001` | Use model_dump and model_dump_json instead of v1 serialization APIs | Idioms | 8 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT` |
| `pydantic-002` | Use model_validate instead of parse_obj or parse_raw | Idioms | 8 | `ZEN-RIGHT-ABSTRACTION` |
| `pydantic-003` | Mutable defaults should use Field(default_factory=...) | Correctness | 9 | `ZEN-VISIBLE-STATE`, `ZEN-EXPLICIT-INTENT` |
| `pydantic-004` | Prefer model_config over nested Config classes | Idioms | 7 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT` |
| `pydantic-005` | Use field_validator instead of validator | Idioms | 7 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT` |
| `pydantic-006` | Avoid __fields__; use model_fields in v2 | Idioms | 7 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-UNAMBIGUOUS-NAME` |
| `pydantic-007` | Prefer X | None over Optional[X] in modern Python code | Idioms | 4 | `ZEN-EXPLICIT-INTENT` |
| `pydantic-008` | Use from_attributes instead of orm_mode | Idioms | 7 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT` |

??? info "`pydantic-001` — Use model_dump and model_dump_json instead of v1 serialization APIs"
    **Pydantic v2 renamed serialization APIs to make model boundaries more explicit.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Use model_dump and model_dump_json instead of v1 serialization APIs

    **Detectable Patterns:**

    - `re:\.(?:dict|json)\(`

    !!! tip "Recommended Fix"
        Use model_dump() or model_dump_json() on Pydantic models.

??? info "`pydantic-002` — Use model_validate instead of parse_obj or parse_raw"
    **v2 validation APIs center around model_validate and model_validate_json.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Use model_validate instead of parse_obj or parse_raw

    **Detectable Patterns:**

    - `re:\b(?:parse_obj|parse_raw|from_orm)\(`

    !!! tip "Recommended Fix"
        Use model_validate(), model_validate_json(), or from_attributes-compatible validation.

??? info "`pydantic-003` — Mutable defaults should use Field(default_factory=...)"
    **Plain list, dict, and set defaults are shared between instances and create state leaks.**

    **Universal Dogmas:** `ZEN-VISIBLE-STATE`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Mutable defaults should use Field(default_factory=...)

    **Detectable Patterns:**

    - `re::\s*(?:list|dict|set)\b[^=\n]*=\s*(?:\[\]|\{\}|set\(\))`

    !!! tip "Recommended Fix"
        Use Field(default_factory=list), dict, or set instead of a mutable literal default.

??? info "`pydantic-004` — Prefer model_config over nested Config classes"
    **Pydantic v2 consolidated model configuration into the model_config attribute.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Prefer model_config over nested Config classes

    **Detectable Patterns:**

    - `re:^\s*class\s+Config\s*:`

    !!! tip "Recommended Fix"
        Replace the nested Config class with model_config = ConfigDict(...).

??? info "`pydantic-005` — Use field_validator instead of validator"
    **v2 split validation hooks into explicit decorator families such as field_validator and model_validator.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Use field_validator instead of validator

    **Detectable Patterns:**

    - `re:@validator\b`

    !!! tip "Recommended Fix"
        Use @field_validator or @model_validator in Pydantic v2 code.

??? info "`pydantic-006` — Avoid __fields__; use model_fields in v2"
    **The v2 model introspection surface renamed __fields__ to model_fields.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Avoid __fields__; use model_fields in v2

    **Detectable Patterns:**

    - `re:\.__fields__\b`

    !!! tip "Recommended Fix"
        Use model_fields for field metadata lookups.

??? info "`pydantic-007` — Prefer X | None over Optional[X] in modern Python code"
    **Modern union syntax is the project standard for Python 3.12+ and keeps annotations consistent.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Prefer X | None over Optional[X] in modern Python code

    **Detectable Patterns:**

    - `re:\bOptional\[`

    !!! tip "Recommended Fix"
        Use X | None instead of Optional[X].

??? info "`pydantic-008` — Use from_attributes instead of orm_mode"
    **Pydantic v2 renamed ORM compatibility settings to from_attributes.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Use from_attributes instead of orm_mode

    **Detectable Patterns:**

    - `re:orm_mode\s*=\s*True`

    !!! tip "Recommended Fix"
        Configure from_attributes=True via model_config.


## Detector Catalog

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **PydanticDefaultFactoryDetector** | Concrete detector binding for PydanticDefaultFactoryDetector | `pydantic-003` |

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **PydanticFieldValidatorDetector** | Concrete detector binding for PydanticFieldValidatorDetector | `pydantic-005` |
| **PydanticFromAttributesDetector** | Concrete detector binding for PydanticFromAttributesDetector | `pydantic-008` |
| **PydanticModelConfigDetector** | Concrete detector binding for PydanticModelConfigDetector | `pydantic-004` |
| **PydanticModelDumpDetector** | Concrete detector binding for PydanticModelDumpDetector | `pydantic-001` |
| **PydanticModelFieldsDetector** | Concrete detector binding for PydanticModelFieldsDetector | `pydantic-006` |
| **PydanticModelValidateDetector** | Concrete detector binding for PydanticModelValidateDetector | `pydantic-002` |
| **PydanticModernTypingDetector** | Concrete detector binding for PydanticModernTypingDetector | `pydantic-007` |


??? example "Principle → Detector Wiring"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    pydantic_001["pydantic-001<br/>Use model_dump and model_..."]
    pydantic_002["pydantic-002<br/>Use model_validate instea..."]
    pydantic_003["pydantic-003<br/>Mutable defaults should u..."]
    pydantic_004["pydantic-004<br/>Prefer model_config over ..."]
    pydantic_005["pydantic-005<br/>Use field_validator inste..."]
    pydantic_006["pydantic-006<br/>Avoid __fields__; use mod..."]
    pydantic_007["pydantic-007<br/>Prefer X | None over Opti..."]
    pydantic_008["pydantic-008<br/>Use from_attributes inste..."]
    det_PydanticDefaultFactoryDetector["Pydantic Default<br/>Factory"]
    pydantic_003 --> det_PydanticDefaultFactoryDetector
    det_PydanticFieldValidatorDetector["Pydantic Field<br/>Validator"]
    pydantic_005 --> det_PydanticFieldValidatorDetector
    det_PydanticFromAttributesDetector["Pydantic From<br/>Attributes"]
    pydantic_008 --> det_PydanticFromAttributesDetector
    det_PydanticModelConfigDetector["Pydantic Model<br/>Config"]
    pydantic_004 --> det_PydanticModelConfigDetector
    det_PydanticModelDumpDetector["Pydantic Model<br/>Dump"]
    pydantic_001 --> det_PydanticModelDumpDetector
    det_PydanticModelFieldsDetector["Pydantic Model<br/>Fields"]
    pydantic_006 --> det_PydanticModelFieldsDetector
    det_PydanticModelValidateDetector["Pydantic Model<br/>Validate"]
    pydantic_002 --> det_PydanticModelValidateDetector
    det_PydanticModernTypingDetector["Pydantic Modern<br/>Typing"]
    pydantic_007 --> det_PydanticModernTypingDetector
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
        class det_01["Pydantic Default Factory"]
        ViolationDetector <|-- det_01
        class det_02["Pydantic Field Validator"]
        ViolationDetector <|-- det_02
        class det_03["Pydantic From Attributes"]
        ViolationDetector <|-- det_03
        class det_04["Pydantic Model Config"]
        ViolationDetector <|-- det_04
        class det_05["Pydantic Model Dump"]
        ViolationDetector <|-- det_05
        class det_06["Pydantic Model Fields"]
        ViolationDetector <|-- det_06
        class det_07["Pydantic Model Validate"]
        ViolationDetector <|-- det_07
        class det_08["Pydantic Modern Typing"]
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
  pydantic:
    enabled: true
    pipeline:
```


## See Also

- [Python](python.md) — Parent language analysis and shared Python architecture
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
