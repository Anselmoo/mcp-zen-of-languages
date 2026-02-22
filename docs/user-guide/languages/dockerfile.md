---
title: Dockerfile
description: "8 zen principles enforced by 8 detectors: Docker build and runtime hardening best practices."
icon: material/docker
tags:
  - Dockerfile
---

# Dockerfile



## Optional External Tool Augmentation

!!! info "Consent-first external tooling"
    External tool execution is optional and disabled by default. Use
    `--enable-external-tools` (CLI) or `enable_external_tools=true` (MCP)
    to opt in. Missing tools should return recommendations; no automatic
    installs occur during analysis.

| Tool | Default invocation | Output |
|------|---------------------|--------|
| `hadolint` | `hadolint -f json -` | JSON |



## Zen Principles

8 principles across 5 categories, drawn from [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/).

<div class="grid" markdown>

:material-tag-outline: **Configuration** · 1 principle
:material-tag-outline: **Correctness** · 1 principle
:material-tag-outline: **Performance** · 2 principles
:material-tag-outline: **Robustness** · 1 principle
:material-tag-outline: **Security** · 3 principles

</div>

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `dockerfile-001` | Avoid latest tags in base images | Security | 8 |
| `dockerfile-002` | Run containers as non-root user | Security | 9 |
| `dockerfile-003` | Prefer COPY over ADD unless extra features are needed | Correctness | 6 |
| `dockerfile-004` | Declare HEALTHCHECK for production images | Robustness | 7 |
| `dockerfile-005` | Use multi-stage builds for compiled workloads | Performance | 6 |
| `dockerfile-006` | Keep secrets out of ENV and ARG instructions | Security | 9 |
| `dockerfile-007` | Maintain layer discipline | Performance | 5 |
| `dockerfile-008` | Keep .dockerignore coherent with broad context copies | Configuration | 4 |

??? info "`dockerfile-001` — Avoid latest tags in base images"
    **Pin base image versions to avoid unplanned upgrades.**

    **Common Violations:**

    - FROM image:latest

    **Detectable Patterns:**

    - `:latest`

    !!! tip "Recommended Fix"
        Use explicit version tags like `ubuntu:22.04`.

??? info "`dockerfile-002` — Run containers as non-root user"
    **Final image should set a non-root USER directive.**

    **Common Violations:**

    - Missing USER directive
    - Final USER is root

    **Detectable Patterns:**

    - `USER root`

    !!! tip "Recommended Fix"
        Create and switch to an unprivileged runtime user.

??? info "`dockerfile-003` — Prefer COPY over ADD unless extra features are needed"
    **ADD has surprising behavior for archives and remote URLs.**

    **Common Violations:**

    - Using ADD for plain local copy

    **Detectable Patterns:**

    - `ADD `

    !!! tip "Recommended Fix"
        Use COPY for local files and reserve ADD for tar/URL use cases.

??? info "`dockerfile-004` — Declare HEALTHCHECK for production images"
    **Health checks improve orchestration reliability and recovery.**

    **Common Violations:**

    - Missing HEALTHCHECK instruction

    **Detectable Patterns:**

    - `!HEALTHCHECK`

??? info "`dockerfile-005` — Use multi-stage builds for compiled workloads"
    **Compiled builds should separate build and runtime stages.**

    **Common Violations:**

    - Single-stage Dockerfile for compiled build commands

??? info "`dockerfile-006` — Keep secrets out of ENV and ARG instructions"
    **Credentials in Dockerfile instructions leak into image metadata/layers.**

    **Common Violations:**

    - ENV with secret-like key
    - ARG with credential-like key

??? info "`dockerfile-007` — Maintain layer discipline"
    **Excessive RUN layers increase image size and cache fragmentation.**

    **Common Violations:**

    - Too many RUN instructions

    **Thresholds:**

    | Parameter | Default |
    |-----------|---------|
    | `max_run_instructions` | `5` |

??? info "`dockerfile-008` — Keep .dockerignore coherent with broad context copies"
    **Broad context copies should be paired with .dockerignore hygiene.**

    **Common Violations:**

    - COPY/ADD from build context without .dockerignore

    **Detectable Patterns:**

    - `COPY .`
    - `ADD .`


## Detector Catalog

### Configuration

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **DockerfileDockerignoreDetector** | Warns when broad context copies are used without a ``.dockerignore`` file | `dockerfile-008` |

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **DockerfileAddInstructionDetector** | Discourages broad ``ADD`` usage when ``COPY`` is sufficient | `dockerfile-003` |

### Performance

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **DockerfileMultiStageDetector** | Advises multi-stage builds when compiled build commands are detected | `dockerfile-005` |
| **DockerfileLayerDisciplineDetector** | Limits excessive ``RUN`` layer count in Dockerfiles | `dockerfile-007` |

### Robustness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **DockerfileHealthcheckDetector** | Reports Dockerfiles that do not declare a ``HEALTHCHECK`` instruction | `dockerfile-004` |

### Security

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **DockerfileLatestTagDetector** | Flags ``FROM`` instructions that pin to the mutable ``latest`` tag | `dockerfile-001` |
| **DockerfileNonRootUserDetector** | Ensures the final Docker runtime user is not root | `dockerfile-002` |
| **DockerfileSecretHygieneDetector** | Detects secret-like keys embedded in ``ENV`` and ``ARG`` declarations | `dockerfile-006` |


??? example "Principle → Detector Wiring"
    ```mermaid
    graph LR
    dockerfile_001["dockerfile-001<br/>Avoid latest tags in base images"]
    dockerfile_002["dockerfile-002<br/>Run containers as non-root user"]
    dockerfile_003["dockerfile-003<br/>Prefer COPY over ADD unless extra featur..."]
    dockerfile_004["dockerfile-004<br/>Declare HEALTHCHECK for production image..."]
    dockerfile_005["dockerfile-005<br/>Use multi-stage builds for compiled work..."]
    dockerfile_006["dockerfile-006<br/>Keep secrets out of ENV and ARG instruct..."]
    dockerfile_007["dockerfile-007<br/>Maintain layer discipline"]
    dockerfile_008["dockerfile-008<br/>Keep .dockerignore coherent with broad c..."]
    det_DockerfileAddInstructionDetector["DockerfileAddInstructionDetector"]
    dockerfile_003 --> det_DockerfileAddInstructionDetector
    det_DockerfileDockerignoreDetector["DockerfileDockerignoreDetector"]
    dockerfile_008 --> det_DockerfileDockerignoreDetector
    det_DockerfileHealthcheckDetector["DockerfileHealthcheckDetector"]
    dockerfile_004 --> det_DockerfileHealthcheckDetector
    det_DockerfileLatestTagDetector["DockerfileLatestTagDetector"]
    dockerfile_001 --> det_DockerfileLatestTagDetector
    det_DockerfileLayerDisciplineDetector["DockerfileLayerDisciplineDetector"]
    dockerfile_007 --> det_DockerfileLayerDisciplineDetector
    det_DockerfileMultiStageDetector["DockerfileMultiStageDetector"]
    dockerfile_005 --> det_DockerfileMultiStageDetector
    det_DockerfileNonRootUserDetector["DockerfileNonRootUserDetector"]
    dockerfile_002 --> det_DockerfileNonRootUserDetector
    det_DockerfileSecretHygieneDetector["DockerfileSecretHygieneDetector"]
    dockerfile_006 --> det_DockerfileSecretHygieneDetector
    classDef principle fill:#4051b5,color:#fff,stroke:none
    classDef detector fill:#26a269,color:#fff,stroke:none
    class dockerfile_001 principle
    class dockerfile_002 principle
    class dockerfile_003 principle
    class dockerfile_004 principle
    class dockerfile_005 principle
    class dockerfile_006 principle
    class dockerfile_007 principle
    class dockerfile_008 principle
    class det_DockerfileAddInstructionDetector detector
    class det_DockerfileDockerignoreDetector detector
    class det_DockerfileHealthcheckDetector detector
    class det_DockerfileLatestTagDetector detector
    class det_DockerfileLayerDisciplineDetector detector
    class det_DockerfileMultiStageDetector detector
    class det_DockerfileNonRootUserDetector detector
    class det_DockerfileSecretHygieneDetector detector
    ```

## Configuration

```yaml
languages:
  dockerfile:
    enabled: true
    pipeline:
      - type: dockerfile-007
        max_run_instructions: 5
```


## See Also

- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
