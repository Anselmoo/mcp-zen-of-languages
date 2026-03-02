---
title: Ansible
description: "7 zen principles enforced by 7 detectors: Idempotent, secure, and maintainable infrastructure automation.."
icon: material/console
tags:
  - Ansible
---

# Ansible




## Zen Principles

7 principles across 5 categories, drawn from [Ansible Documentation](https://docs.ansible.com/).

<div class="grid" markdown>

:material-tag-outline: **Consistency** · 2 principles
:material-tag-outline: **Correctness** · 1 principle
:material-tag-outline: **Idioms** · 2 principles
:material-tag-outline: **Readability** · 1 principle
:material-tag-outline: **Security** · 1 principle

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `ansible-001` | Name all tasks and plays | Readability | 6 | `ZEN-UNAMBIGUOUS-NAME` |
| `ansible-002` | Use fully qualified collection names | Consistency | 5 | `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME`, `ZEN-STRICT-FENCES` |
| `ansible-003` | Prefer idempotent modules over command or shell | Idioms | 8 | `ZEN-RIGHT-ABSTRACTION` |
| `ansible-004` | Use become instead of sudo | Idioms | 7 | `ZEN-RIGHT-ABSTRACTION` |
| `ansible-005` | State should be explicit | Correctness | 6 | `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE` |
| `ansible-006` | No cleartext passwords | Security | 9 | `ZEN-STRICT-FENCES` |
| `ansible-007` | Use clean Jinja2 variable spacing | Consistency | 4 | `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME` |

??? info "`ansible-001` — Name all tasks and plays"
    **Every play and task should have a descriptive name for clear logs.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - play or task missing name

??? info "`ansible-002` — Use fully qualified collection names"
    **Prefer explicit module namespaces such as ansible.builtin.command.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME`, `ZEN-STRICT-FENCES`
    **Common Violations:**

    - module called without FQCN

??? info "`ansible-003` — Prefer idempotent modules over command or shell"
    **Avoid shell/command for actions with dedicated idempotent modules.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - shell or command module used

    **Detectable Patterns:**

    - `shell:`
    - `command:`

??? info "`ansible-004` — Use become instead of sudo"
    **The sudo key is deprecated; use become for privilege escalation.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - sudo key used

    **Detectable Patterns:**

    - `sudo:`

??? info "`ansible-005` — State should be explicit"
    **Specify explicit module state instead of relying on defaults.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - task module missing explicit state

??? info "`ansible-006` — No cleartext passwords"
    **Sensitive values should be vaulted or externally sourced.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`
    **Common Violations:**

    - potential cleartext secret in variable assignment

??? info "`ansible-007` — Use clean Jinja2 variable spacing"
    **Prefer {{ var_name }} spacing style for readability and consistency.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Jinja expression missing inner spacing

    **Detectable Patterns:**

    - `{{`
    - `}}`


## Detector Catalog

### Consistency

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AnsibleFqcnDetector** | Detect short module names that should use fully qualified collection names | `ansible-002` |
| **AnsibleJinjaSpacingDetector** | Enforce consistent spacing inside Jinja2 interpolation delimiters | `ansible-007` |

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AnsibleStateExplicitDetector** | Ensure stateful modules specify explicit state values | `ansible-005` |

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AnsibleIdempotencyDetector** | Flag shell/command usage where idempotent modules should be preferred | `ansible-003` |
| **AnsibleBecomeDetector** | Flag deprecated sudo usage in plays or tasks | `ansible-004` |

### Readability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AnsibleNamingDetector** | Ensure Ansible plays and tasks include descriptive names | `ansible-001` |

### Security

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AnsibleNoCleartextPasswordDetector** | Detect likely cleartext secret assignments in YAML variables | `ansible-006` |


??? example "Principle → Detector Wiring"
    ```mermaid
    graph LR
    ansible_001["ansible-001<br/>Name all tasks and plays"]
    ansible_002["ansible-002<br/>Use fully qualified collection names"]
    ansible_003["ansible-003<br/>Prefer idempotent modules over command o..."]
    ansible_004["ansible-004<br/>Use become instead of sudo"]
    ansible_005["ansible-005<br/>State should be explicit"]
    ansible_006["ansible-006<br/>No cleartext passwords"]
    ansible_007["ansible-007<br/>Use clean Jinja2 variable spacing"]
    det_AnsibleBecomeDetector["AnsibleBecomeDetector"]
    ansible_004 --> det_AnsibleBecomeDetector
    det_AnsibleFqcnDetector["AnsibleFqcnDetector"]
    ansible_002 --> det_AnsibleFqcnDetector
    det_AnsibleIdempotencyDetector["AnsibleIdempotencyDetector"]
    ansible_003 --> det_AnsibleIdempotencyDetector
    det_AnsibleJinjaSpacingDetector["AnsibleJinjaSpacingDetector"]
    ansible_007 --> det_AnsibleJinjaSpacingDetector
    det_AnsibleNamingDetector["AnsibleNamingDetector"]
    ansible_001 --> det_AnsibleNamingDetector
    det_AnsibleNoCleartextPasswordDetector["AnsibleNoCleartextPasswordDetector"]
    ansible_006 --> det_AnsibleNoCleartextPasswordDetector
    det_AnsibleStateExplicitDetector["AnsibleStateExplicitDetector"]
    ansible_005 --> det_AnsibleStateExplicitDetector
    classDef principle fill:#4051b5,color:#fff,stroke:none
    classDef detector fill:#26a269,color:#fff,stroke:none
    class ansible_001 principle
    class ansible_002 principle
    class ansible_003 principle
    class ansible_004 principle
    class ansible_005 principle
    class ansible_006 principle
    class ansible_007 principle
    class det_AnsibleBecomeDetector detector
    class det_AnsibleFqcnDetector detector
    class det_AnsibleIdempotencyDetector detector
    class det_AnsibleJinjaSpacingDetector detector
    class det_AnsibleNamingDetector detector
    class det_AnsibleNoCleartextPasswordDetector detector
    class det_AnsibleStateExplicitDetector detector
    ```

## Configuration

```yaml
languages:
  ansible:
    enabled: true
    pipeline:
```


## See Also

- [GitHub Actions](github-actions.md) — Workflow automation counterpart in CI environments
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
