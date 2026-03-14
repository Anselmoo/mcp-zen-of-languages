---
title: Django
description: "6 zen principles enforced by 6 detectors: Explicit, batteries-included web architecture with strong defaults for security and maintainability.."
icon: material/web-box
tags:
  - Django
---

# Django




## Zen Principles

6 principles across 4 categories, drawn from [Django documentation](https://docs.djangoproject.com/).

<div class="grid" markdown>

:material-tag-outline: **Architecture** · 1 principle
:material-tag-outline: **Organization** · 1 principle
:material-tag-outline: **Performance** · 1 principle
:material-tag-outline: **Security** · 3 principles

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `django-001` | Raw SQL must not interpolate user-controlled strings directly | Security | 10 | `ZEN-STRICT-FENCES`, `ZEN-FAIL-FAST` |
| `django-002` | Settings files should not hardcode secrets | Security | 10 | `ZEN-STRICT-FENCES` |
| `django-003` | Production-facing settings should not leave DEBUG enabled | Security | 9 | `ZEN-STRICT-FENCES`, `ZEN-FAIL-FAST` |
| `django-004` | Redirects and URL construction should avoid hardcoded internal paths | Organization | 7 | `ZEN-STRICT-FENCES`, `ZEN-RIGHT-ABSTRACTION` |
| `django-005` | Signal hookups should be reviewed carefully | Architecture | 6 | `ZEN-RIGHT-ABSTRACTION` |
| `django-006` | Looping over querysets without related loading hints should be reviewed | Performance | 8 | `ZEN-PROPORTIONATE-COMPLEXITY` |

??? info "`django-001` — Raw SQL must not interpolate user-controlled strings directly"
    **String-built SQL in Django bypasses ORM protections and opens injection risk.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`, `ZEN-FAIL-FAST`
    **Common Violations:**

    - Raw SQL must not interpolate user-controlled strings directly

    **Detectable Patterns:**

    - `re:cursor\.execute\(\s*(?:f[\"\']|[rbuf]*[\"\'][^\"\']*%s?[\"\']\s*%)`

    !!! tip "Recommended Fix"
        Use parameterized queries or ORM expressions instead of interpolated SQL.

??? info "`django-002` — Settings files should not hardcode secrets"
    **Hardcoded secrets in settings are difficult to rotate and often leak into logs, repos, or test fixtures.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`
    **Common Violations:**

    - Settings files should not hardcode secrets

    **Detectable Patterns:**

    - `re:^\s*(?:SECRET_KEY|DATABASE_URL)\s*=\s*[\"\']`

    !!! tip "Recommended Fix"
        Load secrets from environment variables or a dedicated secret store.

??? info "`django-003` — Production-facing settings should not leave DEBUG enabled"
    **DEBUG=True exposes verbose internals and unsafe error surfaces outside local development.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`, `ZEN-FAIL-FAST`
    **Common Violations:**

    - Production-facing settings should not leave DEBUG enabled

    **Detectable Patterns:**

    - `re:^\s*DEBUG\s*=\s*True\b`

    !!! tip "Recommended Fix"
        Set DEBUG from the environment and keep production defaults false.

??? info "`django-004` — Redirects and URL construction should avoid hardcoded internal paths"
    **Hardcoded paths drift when route definitions change and bypass Django's URL reversing tools.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`, `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Redirects and URL construction should avoid hardcoded internal paths

    **Detectable Patterns:**

    - `re:\b(?:redirect|HttpResponseRedirect)\(\s*[\"\']\/`

    !!! tip "Recommended Fix"
        Use reverse() or reverse_lazy() instead of embedding internal paths.

??? info "`django-005` — Signal hookups should be reviewed carefully"
    **Django signals create hidden coupling and should remain a deliberate design choice.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Signal hookups should be reviewed carefully

    **Detectable Patterns:**

    - `re:\b(?:post_save|pre_save|post_delete|m2m_changed)\.connect\(`

    !!! tip "Recommended Fix"
        Keep signal usage explicit and consider service-layer orchestration when behavior becomes complex.

??? info "`django-006` — Looping over querysets without related loading hints should be reviewed"
    **Related-field access in queryset loops often leads to N+1 queries when select_related/prefetch_related are missing.**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - Looping over querysets without related loading hints should be reviewed

    **Detectable Patterns:**

    - `re:for\s+\w+\s+in\s+\w+\.objects\.(?:all|filter)\(`

    !!! tip "Recommended Fix"
        Consider select_related() or prefetch_related() before iterating related ORM objects.


## Detector Catalog

### Architecture

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **DjangoSignalHookDetector** | Concrete detector binding for DjangoSignalHookDetector | `django-005` |

### Organization

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **DjangoReverseUrlDetector** | Concrete detector binding for DjangoReverseUrlDetector | `django-004` |

### Performance

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **DjangoQuerysetLoadingDetector** | Concrete detector binding for DjangoQuerysetLoadingDetector | `django-006` |

### Security

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **DjangoDebugConfigDetector** | Concrete detector binding for DjangoDebugConfigDetector | `django-003` |
| **DjangoParameterizedSqlDetector** | Concrete detector binding for DjangoParameterizedSqlDetector | `django-001` |
| **DjangoSecretSettingsDetector** | Concrete detector binding for DjangoSecretSettingsDetector | `django-002` |


??? example "Principle → Detector Wiring"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    django_001["django-001<br/>Raw SQL must not interpol..."]
    django_002["django-002<br/>Settings files should not..."]
    django_003["django-003<br/>Production-facing setting..."]
    django_004["django-004<br/>Redirects and URL constru..."]
    django_005["django-005<br/>Signal hookups should be ..."]
    django_006["django-006<br/>Looping over querysets wi..."]
    det_DjangoDebugConfigDetector["Django Debug<br/>Config"]
    django_003 --> det_DjangoDebugConfigDetector
    det_DjangoParameterizedSqlDetector["Django Parameterized<br/>Sql"]
    django_001 --> det_DjangoParameterizedSqlDetector
    det_DjangoQuerysetLoadingDetector["Django Queryset<br/>Loading"]
    django_006 --> det_DjangoQuerysetLoadingDetector
    det_DjangoReverseUrlDetector["Django Reverse<br/>Url"]
    django_004 --> det_DjangoReverseUrlDetector
    det_DjangoSecretSettingsDetector["Django Secret<br/>Settings"]
    django_002 --> det_DjangoSecretSettingsDetector
    det_DjangoSignalHookDetector["Django Signal<br/>Hook"]
    django_005 --> det_DjangoSignalHookDetector
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
        class det_01["Django Debug Config"]
        ViolationDetector <|-- det_01
        class det_02["Django Parameterized Sql"]
        ViolationDetector <|-- det_02
        class det_03["Django Queryset Loading"]
        ViolationDetector <|-- det_03
        class det_04["Django Reverse Url"]
        ViolationDetector <|-- det_04
        class det_05["Django Secret Settings"]
        ViolationDetector <|-- det_05
        class det_06["Django Signal Hook"]
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
  django:
    enabled: true
    pipeline:
```


## See Also

- [Python](python.md) — Parent language analysis and shared Python architecture
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
