---
title: React
description: "5 zen principles enforced by 5 detectors: Composable, predictable UI driven by state and props.."
icon: fontawesome/brands/react
tags:
  - React
---

# React




## Zen Principles

5 principles across 3 categories, drawn from [React documentation and Rules of React](https://react.dev/).

<div class="grid" markdown>

:material-tag-outline: **Architecture** · 1 principle
:material-tag-outline: **Correctness** · 3 principles
:material-tag-outline: **Performance** · 1 principle

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `react-001` | List keys must be stable and not derived from array indexes | Correctness | 9 | `ZEN-EXPLICIT-INTENT` |
| `react-002` | JSX event handlers should avoid inline callbacks in hot paths | Performance | 5 | `ZEN-PROPORTIONATE-COMPLEXITY` |
| `react-003` | Component logic should not manipulate the DOM directly | Architecture | 7 | `ZEN-RIGHT-ABSTRACTION` |
| `react-004` | Hooks must not be called conditionally | Correctness | 10 | `ZEN-EXPLICIT-INTENT` |
| `react-005` | Effects that register timers or listeners need an explicit cleanup review | Correctness | 7 | `ZEN-EXPLICIT-INTENT` |

??? info "`react-001` — List keys must be stable and not derived from array indexes"
    **React list rendering depends on stable keys to preserve component identity across renders.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - List keys must be stable and not derived from array indexes

    **Detectable Patterns:**

    - `re:key=\{(?:index|i|itemIndex)\}`

    !!! tip "Recommended Fix"
        Use an identifier from the data model instead of the array index.

??? info "`react-002` — JSX event handlers should avoid inline callbacks in hot paths"
    **Inline callbacks create new function identities on every render and can trigger avoidable child updates.**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - JSX event handlers should avoid inline callbacks in hot paths

    **Detectable Patterns:**

    - `re:on(?:Click|Change|Submit|Input|KeyDown|KeyUp)=\{\s*(?:\([^)]*\)|[A-Za-z_]\w*)\s*=>`

    !!! tip "Recommended Fix"
        Extract a named callback or memoized handler outside the JSX attribute.

??? info "`react-003` — Component logic should not manipulate the DOM directly"
    **React should remain the source of truth for UI updates instead of ad-hoc DOM queries and mutations.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - Component logic should not manipulate the DOM directly

    **Detectable Patterns:**

    - `re:\bdocument\.(?:getElementById|querySelector|querySelectorAll)\(`

    !!! tip "Recommended Fix"
        Use refs, state, and declarative rendering instead of direct DOM access.

??? info "`react-004` — Hooks must not be called conditionally"
    **Conditional hook calls break React's call ordering guarantees and lead to runtime bugs.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Hooks must not be called conditionally

    **Detectable Patterns:**

    - `re:\bif\s*\([^)]*\)\s*\{[\s\S]*?\buse[A-Z]\w*\(`

    !!! tip "Recommended Fix"
        Move hooks to the top level of the component and branch on derived values instead.

??? info "`react-005` — Effects that register timers or listeners need an explicit cleanup review"
    **Effects that add listeners or timers are a common source of leaks when cleanup is omitted.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Effects that register timers or listeners need an explicit cleanup review

    **Detectable Patterns:**

    - `re:useEffect\([\s\S]*?(?:setInterval|addEventListener)\(`

    !!! tip "Recommended Fix"
        Return a cleanup function from useEffect that tears down timers or listeners.


## Detector Catalog

### Architecture

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **ReactDirectDomAccessDetector** | Concrete detector binding for ReactDirectDomAccessDetector | `react-003` |

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **ReactConditionalHookDetector** | Concrete detector binding for ReactConditionalHookDetector | `react-004` |
| **ReactEffectCleanupDetector** | Concrete detector binding for ReactEffectCleanupDetector | `react-005` |
| **ReactStableKeyDetector** | Concrete detector binding for ReactStableKeyDetector | `react-001` |

### Performance

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **ReactInlineHandlerDetector** | Concrete detector binding for ReactInlineHandlerDetector | `react-002` |


??? example "Principle → Detector Wiring"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    react_001["react-001<br/>List keys must be stable ..."]
    react_002["react-002<br/>JSX event handlers should..."]
    react_003["react-003<br/>Component logic should no..."]
    react_004["react-004<br/>Hooks must not be called ..."]
    react_005["react-005<br/>Effects that register tim..."]
    det_ReactConditionalHookDetector["React Conditional<br/>Hook"]
    react_004 --> det_ReactConditionalHookDetector
    det_ReactDirectDomAccessDetector["React Direct<br/>Dom Access"]
    react_003 --> det_ReactDirectDomAccessDetector
    det_ReactEffectCleanupDetector["React Effect<br/>Cleanup"]
    react_005 --> det_ReactEffectCleanupDetector
    det_ReactInlineHandlerDetector["React Inline<br/>Handler"]
    react_002 --> det_ReactInlineHandlerDetector
    det_ReactStableKeyDetector["React Stable<br/>Key"]
    react_001 --> det_ReactStableKeyDetector
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
        class det_01["React Conditional Hook"]
        ViolationDetector <|-- det_01
        class det_02["React Direct Dom Access"]
        ViolationDetector <|-- det_02
        class det_03["React Effect Cleanup"]
        ViolationDetector <|-- det_03
        class det_04["React Inline Handler"]
        ViolationDetector <|-- det_04
        class det_05["React Stable Key"]
        ViolationDetector <|-- det_05
    ```

??? example "Analysis Pipeline"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 50, "rankSpacing": 70}}}%%
    flowchart TD
    Source(["Source Code"]) --> Parse["Parse & Tokenize"]
    Parse --> Metrics["Compute Metrics"]
    Metrics --> Pipeline{"5 Detectors"}
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
        Detecting --> Reporting : 5 detectors run
        Reporting --> [*] : AnalysisResult
        Parsing --> Reporting : parse error (best-effort)
    ```

## Configuration

```yaml
languages:
  react:
    enabled: true
    pipeline:
```


## See Also

- [TypeScript](typescript.md) — Shared frontend type-safety foundations
- [JavaScript](javascript.md) — Runtime patterns and browser-side idioms
- [Configuration](../configuration.md) — Per-language pipeline overrides
