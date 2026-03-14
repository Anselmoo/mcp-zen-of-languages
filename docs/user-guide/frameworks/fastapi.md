---
title: FastAPI
description: "6 zen principles enforced by 6 detectors: Type-driven API design with async-first I/O and explicit request/response contracts.."
icon: material/api
tags:
  - FastAPI
---

# FastAPI




## Zen Principles

6 principles across 4 categories, drawn from [FastAPI documentation](https://fastapi.tiangolo.com/).

<div class="grid" markdown>

:material-tag-outline: **Clarity** · 2 principles
:material-tag-outline: **Correctness** · 2 principles
:material-tag-outline: **Idioms** · 1 principle
:material-tag-outline: **Performance** · 1 principle

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `fastapi-001` | Route decorators should declare response_model explicitly | Clarity | 7 | `ZEN-EXPLICIT-INTENT` |
| `fastapi-002` | POST routes should declare an explicit status_code | Clarity | 5 | `ZEN-EXPLICIT-INTENT` |
| `fastapi-003` | Route handlers should not raise bare Exception | Correctness | 7 | `ZEN-FAIL-FAST`, `ZEN-EXPLICIT-INTENT` |
| `fastapi-004` | Background work should use BackgroundTasks instead of raw threads | Correctness | 7 | `ZEN-RIGHT-ABSTRACTION` |
| `fastapi-005` | Async routes should avoid blocking I/O helpers | Performance | 9 | `ZEN-PROPORTIONATE-COMPLEXITY` |
| `fastapi-006` | Prefer explicit HTTP verb decorators over app.route | Idioms | 6 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT` |

??? info "`fastapi-001` — Route decorators should declare response_model explicitly"
    **Explicit response models keep the OpenAPI contract and response serialization predictable.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Route decorators should declare response_model explicitly

    **Detectable Patterns:**

    - `re:@(?:app|router)\.(?:get|post|put|delete|patch)\((?:(?!response_model=)[^)\n])+\)`

    !!! tip "Recommended Fix"
        Add response_model=... to the route decorator.

??? info "`fastapi-002` — POST routes should declare an explicit status_code"
    **POST handlers commonly create resources and should communicate that with an explicit HTTP status.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - POST routes should declare an explicit status_code

    **Detectable Patterns:**

    - `re:@(?:app|router)\.post\((?:(?!status_code=)[^)\n])+\)`

    !!! tip "Recommended Fix"
        Add status_code=201 or another explicit status that matches the route semantics.

??? info "`fastapi-003` — Route handlers should not raise bare Exception"
    **Bare exceptions bypass FastAPI's explicit HTTP contract and usually leak implementation details.**

    **Universal Dogmas:** `ZEN-FAIL-FAST`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Route handlers should not raise bare Exception

    **Detectable Patterns:**

    - `re:raise\s+Exception\(`

    !!! tip "Recommended Fix"
        Raise HTTPException with a status code and detail payload.

??? info "`fastapi-004` — Background work should use BackgroundTasks instead of raw threads"
    **FastAPI provides BackgroundTasks for request-scoped background work without manual thread management.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Background work should use BackgroundTasks instead of raw threads

    **Detectable Patterns:**

    - `re:\bthreading\.Thread\(`

    !!! tip "Recommended Fix"
        Use BackgroundTasks or a proper task queue instead of spawning threads in handlers.

??? info "`fastapi-005` — Async routes should avoid blocking I/O helpers"
    **Blocking calls inside async handlers reduce concurrency and can stall the event loop.**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - Async routes should avoid blocking I/O helpers

    **Detectable Patterns:**

    - `re:async\s+def[\s\S]*?\b(?:requests\.\w+|time\.sleep\(|subprocess\.run\()`

    !!! tip "Recommended Fix"
        Use async-aware clients and non-blocking primitives inside async route functions.

??? info "`fastapi-006` — Prefer explicit HTTP verb decorators over app.route"
    **Method-specific decorators make API intent clearer than the generic app.route entry point.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Prefer explicit HTTP verb decorators over app.route

    **Detectable Patterns:**

    - `re:@(?:app|router)\.route\(`

    !!! tip "Recommended Fix"
        Use @app.get, @app.post, and related verb-specific decorators.


## Detector Catalog

### Clarity

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **FastapiResponseModelDetector** | Concrete detector binding for FastapiResponseModelDetector | `fastapi-001` |
| **FastapiStatusCodeDetector** | Concrete detector binding for FastapiStatusCodeDetector | `fastapi-002` |

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **FastapiBackgroundTasksDetector** | Concrete detector binding for FastapiBackgroundTasksDetector | `fastapi-004` |
| **FastapiHttpExceptionDetector** | Concrete detector binding for FastapiHttpExceptionDetector | `fastapi-003` |

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **FastapiVerbDecoratorDetector** | Concrete detector binding for FastapiVerbDecoratorDetector | `fastapi-006` |

### Performance

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **FastapiAsyncIoDetector** | Concrete detector binding for FastapiAsyncIoDetector | `fastapi-005` |


??? example "Principle → Detector Wiring"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    fastapi_001["fastapi-001<br/>Route decorators should d..."]
    fastapi_002["fastapi-002<br/>POST routes should declar..."]
    fastapi_003["fastapi-003<br/>Route handlers should not..."]
    fastapi_004["fastapi-004<br/>Background work should us..."]
    fastapi_005["fastapi-005<br/>Async routes should avoid..."]
    fastapi_006["fastapi-006<br/>Prefer explicit HTTP verb..."]
    det_FastapiAsyncIoDetector["Fastapi Async<br/>Io"]
    fastapi_005 --> det_FastapiAsyncIoDetector
    det_FastapiBackgroundTasksDetector["Fastapi Background<br/>Tasks"]
    fastapi_004 --> det_FastapiBackgroundTasksDetector
    det_FastapiHttpExceptionDetector["Fastapi Http<br/>Exception"]
    fastapi_003 --> det_FastapiHttpExceptionDetector
    det_FastapiResponseModelDetector["Fastapi Response<br/>Model"]
    fastapi_001 --> det_FastapiResponseModelDetector
    det_FastapiStatusCodeDetector["Fastapi Status<br/>Code"]
    fastapi_002 --> det_FastapiStatusCodeDetector
    det_FastapiVerbDecoratorDetector["Fastapi Verb<br/>Decorator"]
    fastapi_006 --> det_FastapiVerbDecoratorDetector
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
        class det_01["Fastapi Async Io"]
        ViolationDetector <|-- det_01
        class det_02["Fastapi Background Tasks"]
        ViolationDetector <|-- det_02
        class det_03["Fastapi Http Exception"]
        ViolationDetector <|-- det_03
        class det_04["Fastapi Response Model"]
        ViolationDetector <|-- det_04
        class det_05["Fastapi Status Code"]
        ViolationDetector <|-- det_05
        class det_06["Fastapi Verb Decorator"]
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
  fastapi:
    enabled: true
    pipeline:
```


## See Also

- [Python](python.md) — Parent language analysis and shared Python architecture
- [Pydantic](pydantic.md) — Schema conventions that commonly surface in FastAPI projects
- [Configuration](../configuration.md) — Per-language pipeline overrides
