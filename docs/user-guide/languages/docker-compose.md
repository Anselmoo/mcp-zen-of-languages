---
title: Docker Compose
description: "4 zen principles enforced by 4 detectors: Docker Compose service configuration hardening best practices."
icon: material/docker
tags:
  - Docker Compose
---

# Docker Compose



## Optional External Tool Augmentation

!!! info "Consent-first external tooling"
    External tool execution is optional and disabled by default. Use
    `--enable-external-tools` (CLI) or `enable_external_tools=true` (MCP)
    to opt in. Missing tools should return recommendations; no automatic
    installs occur during analysis.

| Tool | Default invocation | Output |
|------|---------------------|--------|
| `docker` | `docker compose -f - config -q` | Text / structured stderr |



## Zen Principles

4 principles across 2 categories, drawn from [Compose Specification](https://compose-spec.io/).

<div class="grid" markdown>

:material-tag-outline: **Robustness** · 1 principle
:material-tag-outline: **Security** · 3 principles

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `docker-compose-001` | Avoid latest tags in image definitions | Security | 8 | `ZEN-STRICT-FENCES` |
| `docker-compose-002` | Run services as non-root user | Security | 9 | `ZEN-STRICT-FENCES`, `ZEN-EXPLICIT-INTENT` |
| `docker-compose-003` | Declare service healthchecks | Robustness | 7 | `ZEN-FAIL-FAST` |
| `docker-compose-004` | Keep secrets out of environment literals | Security | 9 | `ZEN-STRICT-FENCES` |

??? info "`docker-compose-001` — Avoid latest tags in image definitions"
    **Pin service image versions to avoid unplanned upgrades.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`
    **Common Violations:**

    - image uses latest tag

    **Detectable Patterns:**

    - `:latest`

    !!! tip "Recommended Fix"
        Use explicit image tags for every service.

??? info "`docker-compose-002` — Run services as non-root user"
    **Service user should not be root unless explicitly justified.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - user is root or uid 0

    **Detectable Patterns:**

    - `user: root`

??? info "`docker-compose-003` — Declare service healthchecks"
    **Services should define healthcheck probes for reliability.**

    **Universal Dogmas:** `ZEN-FAIL-FAST`
    **Common Violations:**

    - missing healthcheck key

    **Detectable Patterns:**

    - `!healthcheck:`

??? info "`docker-compose-004` — Keep secrets out of environment literals"
    **Secret-like keys should not be embedded directly in environment values.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`
    **Common Violations:**

    - secret-like key in environment block


## Detector Catalog

### Robustness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **DockerComposeHealthcheckDetector** | Flags compose files without any ``healthcheck`` definitions | `docker-compose-003` |

### Security

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **DockerComposeLatestTagDetector** | Flags compose ``image:`` entries using a mutable ``latest`` tag | `docker-compose-001` |
| **DockerComposeNonRootUserDetector** | Flags compose services configured to run as root | `docker-compose-002` |
| **DockerComposeSecretHygieneDetector** | Detects secret-like keys in compose environment blocks | `docker-compose-004` |


??? example "Principle → Detector Wiring"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    docker_compose_001["docker-compose-001<br/>Avoid latest tags in imag..."]
    docker_compose_002["docker-compose-002<br/>Run services as non-root ..."]
    docker_compose_003["docker-compose-003<br/>Declare service healthche..."]
    docker_compose_004["docker-compose-004<br/>Keep secrets out of envir..."]
    det_DockerComposeHealthcheckDetector["Docker Compose<br/>Healthcheck"]
    docker_compose_003 --> det_DockerComposeHealthcheckDetector
    det_DockerComposeLatestTagDetector["Docker Compose<br/>Latest Tag"]
    docker_compose_001 --> det_DockerComposeLatestTagDetector
    det_DockerComposeNonRootUserDetector["Docker Compose<br/>Non Root<br/>User"]
    docker_compose_002 --> det_DockerComposeNonRootUserDetector
    det_DockerComposeSecretHygieneDetector["Docker Compose<br/>Secret Hygiene"]
    docker_compose_004 --> det_DockerComposeSecretHygieneDetector
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
        class det_01["Docker Compose Healthcheck"]
        ViolationDetector <|-- det_01
        class det_02["Docker Compose Latest Tag"]
        ViolationDetector <|-- det_02
        class det_03["Docker Compose Non Root User"]
        ViolationDetector <|-- det_03
        class det_04["Docker Compose Secret Hygiene"]
        ViolationDetector <|-- det_04
    ```

??? example "Analysis Pipeline"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 50, "rankSpacing": 70}}}%%
    flowchart TD
    Source(["Source Code"]) --> Parse["Parse & Tokenize"]
    Parse --> Metrics["Compute Metrics"]
    Metrics --> Pipeline{"4 Detectors"}
    Pipeline --> Collect["Aggregate Violations"]
    Collect --> Result(["AnalysisResult<br/>4 principles"])
    ```

??? example "Analysis States"
    ```mermaid
    %%{init: {"theme": "base"}}%%
    stateDiagram-v2
        [*] --> Ready
        Ready --> Parsing : analyze(code)
        Parsing --> Computing : AST ready
        Computing --> Detecting : metrics ready
        Detecting --> Reporting : 4 detectors run
        Reporting --> [*] : AnalysisResult
        Parsing --> Reporting : parse error (best-effort)
    ```

## Configuration

```yaml
languages:
  docker_compose:
    enabled: true
    pipeline:
```


## See Also

- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
