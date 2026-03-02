---
title: Terraform
description: "7 zen principles enforced by 7 detectors: Terraform Language Documentation."
icon: material/cloud-outline
tags:
  - Terraform
---

# Terraform




## Zen Principles

7 principles across 5 categories, drawn from [Terraform language and module best-practice documentation](https://developer.hashicorp.com/terraform/language).

<div class="grid" markdown>

:material-tag-outline: **Configuration** · 3 principles
:material-tag-outline: **Documentation** · 1 principle
:material-tag-outline: **Naming** · 1 principle
:material-tag-outline: **Robustness** · 1 principle
:material-tag-outline: **Security** · 1 principle

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `tf-001` | Pin provider versions | Configuration | 8 | `ZEN-EXPLICIT-INTENT` |
| `tf-002` | Pin module versions | Configuration | 8 | `ZEN-EXPLICIT-INTENT` |
| `tf-003` | Describe variables and outputs | Documentation | 5 | `ZEN-UNAMBIGUOUS-NAME` |
| `tf-004` | Avoid hardcoded resource IDs | Configuration | 7 | `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME` |
| `tf-005` | Avoid hardcoded secrets | Security | 9 | `ZEN-STRICT-FENCES` |
| `tf-006` | Configure remote state backend | Robustness | 7 | `ZEN-FAIL-FAST`, `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE` |
| `tf-007` | Use consistent snake_case naming | Naming | 5 | `ZEN-UNAMBIGUOUS-NAME` |

??? info "`tf-001` — Pin provider versions"
    **Providers should use explicit version constraints.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Provider block missing explicit version pinning

??? info "`tf-002` — Pin module versions"
    **External module sources should be pinned to versions or commit refs.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - Module source without version pinning

??? info "`tf-003` — Describe variables and outputs"
    **Variable and output blocks should include descriptions.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Variable or output missing description

??? info "`tf-004` — Avoid hardcoded resource IDs"
    **Hardcoded ARNs/IDs reduce portability across environments.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Hardcoded ARN or cloud resource identifier

??? info "`tf-005` — Avoid hardcoded secrets"
    **Credentials and secrets should not be embedded in Terraform source.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`
    **Common Violations:**

    - Potential hardcoded secret in Terraform block

??? info "`tf-006` — Configure remote state backend"
    **Shared environments should configure an explicit remote backend.**

    **Universal Dogmas:** `ZEN-FAIL-FAST`, `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - Terraform backend block missing

??? info "`tf-007` — Use consistent snake_case naming"
    **Resource and variable names should follow snake_case convention.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Resource or variable name not in snake_case


## Detector Catalog

### Configuration

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TerraformProviderVersionPinningDetector** | Detects violations | `tf-001` |
| **TerraformModuleVersionPinningDetector** | Detects violations | `tf-002` |
| **TerraformHardcodedIdDetector** | Detects violations | `tf-004` |

### Documentation

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TerraformVariableOutputDescriptionDetector** | Detects violations | `tf-003` |

### Naming

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TerraformNamingConventionDetector** | Detects violations | `tf-007` |

### Robustness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TerraformBackendConfigDetector** | Detects violations | `tf-006` |

### Security

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TerraformNoHardcodedSecretsDetector** | Detects violations | `tf-005` |


??? example "Principle → Detector Wiring"
    ```mermaid
    graph LR
    tf_001["tf-001<br/>Pin provider versions"]
    tf_002["tf-002<br/>Pin module versions"]
    tf_003["tf-003<br/>Describe variables and outputs"]
    tf_004["tf-004<br/>Avoid hardcoded resource IDs"]
    tf_005["tf-005<br/>Avoid hardcoded secrets"]
    tf_006["tf-006<br/>Configure remote state backend"]
    tf_007["tf-007<br/>Use consistent snake_case naming"]
    det_TerraformBackendConfigDetector["TerraformBackendConfigDetector"]
    tf_006 --> det_TerraformBackendConfigDetector
    det_TerraformHardcodedIdDetector["TerraformHardcodedIdDetector"]
    tf_004 --> det_TerraformHardcodedIdDetector
    det_TerraformModuleVersionPinningDetector["TerraformModuleVersionPinningDetector"]
    tf_002 --> det_TerraformModuleVersionPinningDetector
    det_TerraformNamingConventionDetector["TerraformNamingConventionDetector"]
    tf_007 --> det_TerraformNamingConventionDetector
    det_TerraformNoHardcodedSecretsDetector["TerraformNoHardcodedSecretsDetector"]
    tf_005 --> det_TerraformNoHardcodedSecretsDetector
    det_TerraformProviderVersionPinningDetector["TerraformProviderVersionPinningDetector"]
    tf_001 --> det_TerraformProviderVersionPinningDetector
    det_TerraformVariableOutputDescriptionDetector["TerraformVariableOutputDescriptionDetector"]
    tf_003 --> det_TerraformVariableOutputDescriptionDetector
    classDef principle fill:#4051b5,color:#fff,stroke:none
    classDef detector fill:#26a269,color:#fff,stroke:none
    class tf_001 principle
    class tf_002 principle
    class tf_003 principle
    class tf_004 principle
    class tf_005 principle
    class tf_006 principle
    class tf_007 principle
    class det_TerraformBackendConfigDetector detector
    class det_TerraformHardcodedIdDetector detector
    class det_TerraformModuleVersionPinningDetector detector
    class det_TerraformNamingConventionDetector detector
    class det_TerraformNoHardcodedSecretsDetector detector
    class det_TerraformProviderVersionPinningDetector detector
    class det_TerraformVariableOutputDescriptionDetector detector
    ```

## Configuration

```yaml
languages:
  terraform:
    enabled: true
    pipeline:
```


## See Also

- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
- [Prompt Generation](../prompt-generation.md) — Generate Terraform remediation prompts
