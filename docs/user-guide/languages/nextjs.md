---
title: Next.js
description: "5 zen principles enforced by 1 detectors: Server-first React with framework-level performance, routing, and deployment conventions.."
icon: material/web
tags:
  - Next.js
---

# Next.js




## Zen Principles

5 principles across 4 categories, drawn from [Next.js documentation](https://nextjs.org/docs).

<div class="grid" markdown>

:material-tag-outline: **Correctness** · 1 principle
:material-tag-outline: **Idioms** · 1 principle
:material-tag-outline: **Performance** · 2 principles
:material-tag-outline: **Security** · 1 principle

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `nextjs-001` | Internal navigation should use next/link instead of raw anchors | Idioms | 6 | `ZEN-RIGHT-ABSTRACTION` |
| `nextjs-002` | Images should use next/image when optimization matters | Performance | 7 | `ZEN-PROPORTIONATE-COMPLEXITY` |
| `nextjs-003` | App Router files should not rely on getServerSideProps | Correctness | 8 | `ZEN-EXPLICIT-INTENT` |
| `nextjs-004` | Route handlers should not serialize raw error objects | Security | 9 | `ZEN-STRICT-FENCES`, `ZEN-FAIL-FAST` |
| `nextjs-005` | Client-side fetching inside effects should be reviewed against server-first defaults | Performance | 6 | `ZEN-PROPORTIONATE-COMPLEXITY` |

??? info "`nextjs-001` — Internal navigation should use next/link instead of raw anchors"
    **next/link preserves client-side navigation behavior and framework optimizations.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Internal navigation should use next/link instead of raw anchors

    **Detectable Patterns:**

    - `re:<a\s+href=[\"\']\/`

    !!! tip "Recommended Fix"
        Replace raw internal anchors with the Link component from next/link.

??? info "`nextjs-002` — Images should use next/image when optimization matters"
    **next/image enables responsive delivery, lazy loading, and optimization defaults.**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - Images should use next/image when optimization matters

    **Detectable Patterns:**

    - `re:<img\s+`

    !!! tip "Recommended Fix"
        Use the Image component from next/image for managed images.

??? info "`nextjs-003` — App Router files should not rely on getServerSideProps"
    **getServerSideProps belongs to the Pages Router and is not the idiomatic App Router data-loading model.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - App Router files should not rely on getServerSideProps

    **Detectable Patterns:**

    - `re:\bgetServerSideProps\b`

    !!! tip "Recommended Fix"
        Move data loading into Server Components, route handlers, or fetch in the App Router model.

??? info "`nextjs-004` — Route handlers should not serialize raw error objects"
    **Returning raw error objects can leak implementation details to clients.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`, `ZEN-FAIL-FAST`
    **Common Violations:**

    - Route handlers should not serialize raw error objects

    **Detectable Patterns:**

    - `re:return\s+(?:NextResponse|Response)\.json\(\s*error\b`

    !!! tip "Recommended Fix"
        Return a sanitized error payload and log internal details separately.

??? info "`nextjs-005` — Client-side fetching inside effects should be reviewed against server-first defaults"
    **Fetching inside useEffect often ships extra client JavaScript when Server Components could do the work earlier.**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - Client-side fetching inside effects should be reviewed against server-first defaults

    **Detectable Patterns:**

    - `re:useEffect\([\s\S]*?\bfetch\(`

    !!! tip "Recommended Fix"
        Prefer server-side data fetching and keep client effects for truly client-only work.


## Detector Catalog

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **NextjsRuleDetector** | Framework-specific rule-pattern detector for nextjs rule coverage | `nextjs-001` |


??? example "Principle → Detector Wiring"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    nextjs_001["nextjs-001<br/>Internal navigation shoul..."]
    nextjs_002["nextjs-002<br/>Images should use next/im..."]
    nextjs_003["nextjs-003<br/>App Router files should n..."]
    nextjs_004["nextjs-004<br/>Route handlers should not..."]
    nextjs_005["nextjs-005<br/>Client-side fetching insi..."]
    det_NextjsRuleDetector["Nextjs Rule"]
    nextjs_001 --> det_NextjsRuleDetector
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
        class det_01["Nextjs Rule"]
        ViolationDetector <|-- det_01
    ```

??? example "Analysis Pipeline"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 50, "rankSpacing": 70}}}%%
    flowchart TD
    Source(["Source Code"]) --> Parse["Parse & Tokenize"]
    Parse --> Metrics["Compute Metrics"]
    Metrics --> Pipeline{"1 Detectors"}
    Pipeline --> Collect["Aggregate Violations"]
    Collect --> Result(["AnalysisResult<br/>5 principles"])
    ```

??? example "Analysis States"
    ```mermaid
    %%{init: {"theme": "base"}}%%
    stateDiagram-v2
        [*] --> Ready
        Ready --> Parsing : analyze(code)
        Parsing --> Computing : AST ready
        Computing --> Detecting : metrics ready
        Detecting --> Reporting : 1 detectors run
        Reporting --> [*] : AnalysisResult
        Parsing --> Reporting : parse error (best-effort)
    ```

## Configuration

```yaml
languages:
  nextjs:
    enabled: true
    pipeline:
```


## See Also

- [React](react.md) — Shared component and hook patterns beneath Next.js
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
