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
| **TerraformProviderVersionPinningDetector** | Flag provider blocks that omit explicit version constraints | `tf-001` |
| **TerraformModuleVersionPinningDetector** | Flag module blocks that are not pinned to versions or refs | `tf-002` |
| **TerraformHardcodedIdDetector** | Detect hardcoded cloud resource IDs and ARNs in assignments | `tf-004` |

### Documentation

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TerraformVariableOutputDescriptionDetector** | Require description fields on variable and output blocks | `tf-003` |

### Naming

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TerraformNamingConventionDetector** | Enforce snake_case naming for Terraform variables and resources | `tf-007` |

### Robustness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TerraformBackendConfigDetector** | Ensure terraform blocks declare an explicit backend configuration | `tf-006` |

### Security

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **TerraformNoHardcodedSecretsDetector** | Detect likely hardcoded secret values in Terraform assignments | `tf-005` |


??? example "Principle → Detector Wiring"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    tf_001["tf-001<br/>Pin provider versions"]
    tf_002["tf-002<br/>Pin module versions"]
    tf_003["tf-003<br/>Describe variables and ou..."]
    tf_004["tf-004<br/>Avoid hardcoded resource ..."]
    tf_005["tf-005<br/>Avoid hardcoded secrets"]
    tf_006["tf-006<br/>Configure remote state ba..."]
    tf_007["tf-007<br/>Use consistent snake_case..."]
    det_TerraformBackendConfigDetector["Terraform Backend<br/>Config"]
    tf_006 --> det_TerraformBackendConfigDetector
    det_TerraformHardcodedIdDetector["Terraform Hardcoded<br/>Id"]
    tf_004 --> det_TerraformHardcodedIdDetector
    det_TerraformModuleVersionPinningDetector["Terraform Module<br/>Version Pinning"]
    tf_002 --> det_TerraformModuleVersionPinningDetector
    det_TerraformNamingConventionDetector["Terraform Naming<br/>Convention"]
    tf_007 --> det_TerraformNamingConventionDetector
    det_TerraformNoHardcodedSecretsDetector["Terraform No<br/>Hardcoded Secrets"]
    tf_005 --> det_TerraformNoHardcodedSecretsDetector
    det_TerraformProviderVersionPinningDetector["Terraform Provider<br/>Version Pinning"]
    tf_001 --> det_TerraformProviderVersionPinningDetector
    det_TerraformVariableOutputDescriptionDetector["Terraform Variable<br/>Output Description"]
    tf_003 --> det_TerraformVariableOutputDescriptionDetector
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
        class det_01["Terraform Backend Config"]
        ViolationDetector <|-- det_01
        class det_02["Terraform Hardcoded Id"]
        ViolationDetector <|-- det_02
        class det_03["Terraform Module Version Pinning"]
        ViolationDetector <|-- det_03
        class det_04["Terraform Naming Convention"]
        ViolationDetector <|-- det_04
        class det_05["Terraform No Hardcoded Secrets"]
        ViolationDetector <|-- det_05
        class det_06["Terraform Provider Version Pinning"]
        ViolationDetector <|-- det_06
        class det_07["Terraform Variable Output Description"]
        ViolationDetector <|-- det_07
    ```

??? example "Analysis Pipeline"
    ```mermaid
    %%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 50, "rankSpacing": 70}}}%%
    flowchart TD
    Source(["Source Code"]) --> Parse["Parse & Tokenize"]
    Parse --> Metrics["Compute Metrics"]
    Metrics --> Pipeline{"7 Detectors"}
    Pipeline --> Collect["Aggregate Violations"]
    Collect --> Result(["AnalysisResult<br/>7 principles"])
    ```

??? example "Analysis States"
    ```mermaid
    %%{init: {"theme": "base"}}%%
    stateDiagram-v2
        [*] --> Ready
        Ready --> Parsing : analyze(code)
        Parsing --> Computing : AST ready
        Computing --> Detecting : metrics ready
        Detecting --> Reporting : 7 detectors run
        Reporting --> [*] : AnalysisResult
        Parsing --> Reporting : parse error (best-effort)
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
