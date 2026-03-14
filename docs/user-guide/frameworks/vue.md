---
title: Vue
description: "5 zen principles enforced by 5 detectors: Progressive UI architecture with explicit reactivity and readable templates.."
icon: fontawesome/brands/vuejs
tags:
  - Vue
---

# Vue




## Zen Principles

5 principles across 2 categories, drawn from [Vue Style Guide](https://vuejs.org/style-guide/).

<div class="grid" markdown>

:material-tag-outline: **Correctness** · 4 principles
:material-tag-outline: **Readability** · 1 principle

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `vue-001` | Components should use multi-word names | Readability | 7 | `ZEN-UNAMBIGUOUS-NAME` |
| `vue-002` | Props should declare explicit types | Correctness | 8 | `ZEN-EXPLICIT-INTENT` |
| `vue-003` | v-for directives need a :key binding on the same element | Correctness | 9 | `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE` |
| `vue-004` | Avoid using v-if and v-for on the same element | Correctness | 9 | `ZEN-EXPLICIT-INTENT` |
| `vue-005` | Props should not be mutated directly | Correctness | 10 | `ZEN-VISIBLE-STATE`, `ZEN-EXPLICIT-INTENT` |

??? info "`vue-001` — Components should use multi-word names"
    **Multi-word component names reduce collisions with native HTML elements and improve readability.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Components should use multi-word names

    **Detectable Patterns:**

    - `re:\bname\s*:\s*[\"\'][A-Z][a-zA-Z0-9]*[\"\']`

    !!! tip "Recommended Fix"
        Rename the component to a multi-word name such as UserCard or TodoList.

??? info "`vue-002` — Props should declare explicit types"
    **Untyped props weaken runtime validation and make component contracts harder to understand.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Props should declare explicit types

    **Detectable Patterns:**

    - `re:(?:defineProps\(\s*\[[^\]]+\]\s*\)|props\s*:\s*\[[^\]]+\])`

    !!! tip "Recommended Fix"
        Declare props with defineProps<T>() or a typed props object.

??? info "`vue-003` — v-for directives need a :key binding on the same element"
    **Stable keys are required for predictable diffing and component state preservation.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - v-for directives need a :key binding on the same element

    **Detectable Patterns:**

    - `re:<[^>]+\bv-for\s*=\s*[\"\'][^\"\']+[\"\'](?:(?!:key=)[^>])*>`

    !!! tip "Recommended Fix"
        Add a :key binding derived from stable item identity.

??? info "`vue-004` — Avoid using v-if and v-for on the same element"
    **Combining v-if and v-for on the same node makes rendering intent harder to reason about.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Avoid using v-if and v-for on the same element

    **Detectable Patterns:**

    - `re:<[^>]+\bv-if\s*=.*\bv-for\s*=|<[^>]+\bv-for\s*=.*\bv-if\s*=`

    !!! tip "Recommended Fix"
        Split the conditional wrapper from the looped element or filter the data first.

??? info "`vue-005` — Props should not be mutated directly"
    **Direct prop mutation breaks one-way data flow and can desynchronize parent and child state.**

    **Universal Dogmas:** `ZEN-VISIBLE-STATE`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Props should not be mutated directly

    **Detectable Patterns:**

    - `re:\bprops\.\w+\s*=`

    !!! tip "Recommended Fix"
        Emit an event or derive local state instead of mutating props.


## Detector Catalog

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **VueConditionalLoopDetector** | Concrete detector binding for VueConditionalLoopDetector | `vue-004` |
| **VueListKeyDetector** | Concrete detector binding for VueListKeyDetector | `vue-003` |
| **VuePropMutationDetector** | Concrete detector binding for VuePropMutationDetector | `vue-005` |
| **VueTypedPropsDetector** | Concrete detector binding for VueTypedPropsDetector | `vue-002` |

### Readability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **VueMultiWordNameDetector** | Concrete detector binding for VueMultiWordNameDetector | `vue-001` |


??? example "Principle → Detector Wiring"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    vue_001["vue-001<br/>Components should use mul..."]
    vue_002["vue-002<br/>Props should declare expl..."]
    vue_003["vue-003<br/>v-for directives need a :..."]
    vue_004["vue-004<br/>Avoid using v-if and v-fo..."]
    vue_005["vue-005<br/>Props should not be mutat..."]
    det_VueConditionalLoopDetector["Vue Conditional<br/>Loop"]
    vue_004 --> det_VueConditionalLoopDetector
    det_VueListKeyDetector["Vue List<br/>Key"]
    vue_003 --> det_VueListKeyDetector
    det_VueMultiWordNameDetector["Vue Multi<br/>Word Name"]
    vue_001 --> det_VueMultiWordNameDetector
    det_VuePropMutationDetector["Vue Prop<br/>Mutation"]
    vue_005 --> det_VuePropMutationDetector
    det_VueTypedPropsDetector["Vue Typed<br/>Props"]
    vue_002 --> det_VueTypedPropsDetector
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
        class det_01["Vue Conditional Loop"]
        ViolationDetector <|-- det_01
        class det_02["Vue List Key"]
        ViolationDetector <|-- det_02
        class det_03["Vue Multi Word Name"]
        ViolationDetector <|-- det_03
        class det_04["Vue Prop Mutation"]
        ViolationDetector <|-- det_04
        class det_05["Vue Typed Props"]
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
  vue:
    enabled: true
    pipeline:
```


## See Also

- [TypeScript](typescript.md) — Shared frontend type-safety foundations
- [React](react.md) — Another component-centric UI model for web applications
- [Configuration](../configuration.md) — Per-language pipeline overrides
