---
title: Docker Compose
description: "4 zen principles enforced by 4 detectors: Docker Compose service configuration hardening best practices."
icon: material/docker
tags:
  - Docker Compose
---

# Docker Compose



## Zen Principles

4 principles across 2 categories, drawn from [Compose Specification](https://compose-spec.io/).

<div class="grid" markdown>

:material-tag-outline: **Robustness** · 1 principle
:material-tag-outline: **Security** · 3 principles

</div>

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `docker-compose-001` | Avoid latest tags in image definitions | Security | 8 |
| `docker-compose-002` | Run services as non-root user | Security | 9 |
| `docker-compose-003` | Declare service healthchecks | Robustness | 7 |
| `docker-compose-004` | Keep secrets out of environment literals | Security | 9 |

??? info "`docker-compose-001` — Avoid latest tags in image definitions"
    **Pin service image versions to avoid unplanned upgrades.**

    **Common Violations:**

    - image uses latest tag

    **Detectable Patterns:**

    - `:latest`

    !!! tip "Recommended Fix"
        Use explicit image tags for every service.

??? info "`docker-compose-002` — Run services as non-root user"
    **Service user should not be root unless explicitly justified.**

    **Common Violations:**

    - user is root or uid 0

    **Detectable Patterns:**

    - `user: root`

??? info "`docker-compose-003` — Declare service healthchecks"
    **Services should define healthcheck probes for reliability.**

    **Common Violations:**

    - missing healthcheck key

    **Detectable Patterns:**

    - `!healthcheck:`

??? info "`docker-compose-004` — Keep secrets out of environment literals"
    **Secret-like keys should not be embedded directly in environment values.**

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
    graph LR
    docker_compose_001["docker-compose-001<br/>Avoid latest tags in image definitions"]
    docker_compose_002["docker-compose-002<br/>Run services as non-root user"]
    docker_compose_003["docker-compose-003<br/>Declare service healthchecks"]
    docker_compose_004["docker-compose-004<br/>Keep secrets out of environment literals"]
    det_DockerComposeHealthcheckDetector["DockerComposeHealthcheckDetector"]
    docker_compose_003 --> det_DockerComposeHealthcheckDetector
    det_DockerComposeLatestTagDetector["DockerComposeLatestTagDetector"]
    docker_compose_001 --> det_DockerComposeLatestTagDetector
    det_DockerComposeNonRootUserDetector["DockerComposeNonRootUserDetector"]
    docker_compose_002 --> det_DockerComposeNonRootUserDetector
    det_DockerComposeSecretHygieneDetector["DockerComposeSecretHygieneDetector"]
    docker_compose_004 --> det_DockerComposeSecretHygieneDetector
    classDef principle fill:#4051b5,color:#fff,stroke:none
    classDef detector fill:#26a269,color:#fff,stroke:none
    class docker_compose_001 principle
    class docker_compose_002 principle
    class docker_compose_003 principle
    class docker_compose_004 principle
    class det_DockerComposeHealthcheckDetector detector
    class det_DockerComposeLatestTagDetector detector
    class det_DockerComposeNonRootUserDetector detector
    class det_DockerComposeSecretHygieneDetector detector
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
