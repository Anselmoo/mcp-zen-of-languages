---
title: Angular
description: "5 zen principles enforced by 5 detectors: Scalable frontend architecture with strong conventions around DI, templates, and change detection.."
icon: fontawesome/brands/angular
tags:
  - Angular
---

# Angular




## Zen Principles

5 principles across 3 categories, drawn from [Angular Style Guide](https://angular.dev/style-guide).

<div class="grid" markdown>

:material-tag-outline: **Correctness** · 2 principles
:material-tag-outline: **Performance** · 2 principles
:material-tag-outline: **Readability** · 1 principle

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `angular-001` | Components should opt into OnPush change detection | Performance | 7 | `ZEN-PROPORTIONATE-COMPLEXITY` |
| `angular-002` | Type annotations should avoid any | Correctness | 8 | `ZEN-EXPLICIT-INTENT` |
| `angular-003` | Manual subscriptions need an explicit lifecycle strategy | Correctness | 9 | `ZEN-EXPLICIT-INTENT` |
| `angular-004` | Component selectors should follow project naming conventions | Readability | 5 | `ZEN-UNAMBIGUOUS-NAME` |
| `angular-005` | Feature routes should prefer lazy loading over eager component wiring | Performance | 6 | `ZEN-PROPORTIONATE-COMPLEXITY` |

??? info "`angular-001` — Components should opt into OnPush change detection"
    **OnPush keeps Angular component trees predictable and reduces unnecessary change detection work.**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - Components should opt into OnPush change detection

    **Detectable Patterns:**

    - `re:@Component\(\{(?:(?!ChangeDetectionStrategy\.OnPush)[\s\S])*?\}\)`

    !!! tip "Recommended Fix"
        Add changeDetection: ChangeDetectionStrategy.OnPush to the component decorator.

??? info "`angular-002` — Type annotations should avoid any"
    **Using any bypasses Angular's TypeScript guarantees and hides template/data contract issues.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Type annotations should avoid any

    **Detectable Patterns:**

    - `re::\s*any\b`

    !!! tip "Recommended Fix"
        Replace any with a domain interface, union, or unknown plus narrowing.

??? info "`angular-003` — Manual subscriptions need an explicit lifecycle strategy"
    **Bare subscribe() calls often leak when they are not paired with takeUntil, async pipe, or cleanup logic.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Manual subscriptions need an explicit lifecycle strategy

    **Detectable Patterns:**

    - `re:\.subscribe\(`

    !!! tip "Recommended Fix"
        Use the async pipe, takeUntilDestroyed(), or an explicit teardown path.

??? info "`angular-004` — Component selectors should follow project naming conventions"
    **Selector prefixes help keep large Angular workspaces consistent and collision-free.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Component selectors should follow project naming conventions

    **Detectable Patterns:**

    - `re:selector\s*:\s*[\"\'](?!app-|lib-)[^\"\']+[\"\']`

    !!! tip "Recommended Fix"
        Prefix selectors with an application or library namespace such as app- or lib-.

??? info "`angular-005` — Feature routes should prefer lazy loading over eager component wiring"
    **Lazy-loaded route boundaries help keep initial bundles small and feature areas isolated.**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - Feature routes should prefer lazy loading over eager component wiring

    **Detectable Patterns:**

    - `re:path\s*:\s*[\"\'][^\"\']+[\"\']\s*,\s*component\s*:`

    !!! tip "Recommended Fix"
        Use loadChildren or loadComponent for feature routes when appropriate.


## Detector Catalog

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AngularNoAnyDetector** | Concrete detector binding for AngularNoAnyDetector | `angular-002` |
| **AngularSubscriptionLifecycleDetector** | Concrete detector binding for AngularSubscriptionLifecycleDetector | `angular-003` |

### Performance

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AngularLazyRouteDetector** | Concrete detector binding for AngularLazyRouteDetector | `angular-005` |
| **AngularOnPushDetector** | Concrete detector binding for AngularOnPushDetector | `angular-001` |

### Readability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AngularSelectorPrefixDetector** | Concrete detector binding for AngularSelectorPrefixDetector | `angular-004` |


??? example "Principle → Detector Wiring"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    angular_001["angular-001<br/>Components should opt int..."]
    angular_002["angular-002<br/>Type annotations should a..."]
    angular_003["angular-003<br/>Manual subscriptions need..."]
    angular_004["angular-004<br/>Component selectors shoul..."]
    angular_005["angular-005<br/>Feature routes should pre..."]
    det_AngularLazyRouteDetector["Angular Lazy<br/>Route"]
    angular_005 --> det_AngularLazyRouteDetector
    det_AngularNoAnyDetector["Angular No<br/>Any"]
    angular_002 --> det_AngularNoAnyDetector
    det_AngularOnPushDetector["Angular On<br/>Push"]
    angular_001 --> det_AngularOnPushDetector
    det_AngularSelectorPrefixDetector["Angular Selector<br/>Prefix"]
    angular_004 --> det_AngularSelectorPrefixDetector
    det_AngularSubscriptionLifecycleDetector["Angular Subscription<br/>Lifecycle"]
    angular_003 --> det_AngularSubscriptionLifecycleDetector
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
        class det_01["Angular Lazy Route"]
        ViolationDetector <|-- det_01
        class det_02["Angular No Any"]
        ViolationDetector <|-- det_02
        class det_03["Angular On Push"]
        ViolationDetector <|-- det_03
        class det_04["Angular Selector Prefix"]
        ViolationDetector <|-- det_04
        class det_05["Angular Subscription Lifecycle"]
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
  angular:
    enabled: true
    pipeline:
```


## See Also

- [TypeScript](typescript.md) — Shared frontend type-safety foundations
- [React](react.md) — Another component-centric UI framework with different trade-offs
- [Configuration](../configuration.md) — Per-language pipeline overrides
