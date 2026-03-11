---
title: Ansible
description: "20 zen principles enforced by 20 detectors: Simple, powerful, and human-centered automation."
icon: material/console
tags:
  - Ansible
---

# Ansible




## Zen Principles

20 principles across 10 categories, drawn from [The Zen of Ansible (Red Hat)](https://www.redhat.com/en/blog/the-zen-of-ansible).

<div class="grid" markdown>

:material-tag-outline: **Clarity** · 3 principles
:material-tag-outline: **Complexity** · 2 principles
:material-tag-outline: **Consistency** · 1 principle
:material-tag-outline: **Correctness** · 1 principle
:material-tag-outline: **Design** · 2 principles
:material-tag-outline: **Idioms** · 2 principles
:material-tag-outline: **Organization** · 1 principle
:material-tag-outline: **Readability** · 3 principles
:material-tag-outline: **Robustness** · 1 principle
:material-tag-outline: **Usability** · 4 principles

</div>

| Rule ID | Principle | Category | Severity | Dogma |
|---------|-----------|----------|:--------:|-------|
| `ansible-001` | Ansible is not Python. | Clarity | 7 | `ZEN-EXPLICIT-INTENT` |
| `ansible-002` | YAML sucks for coding. | Readability | 7 | `ZEN-UNAMBIGUOUS-NAME` |
| `ansible-003` | Playbooks are not for programming. | Design | 8 | `ZEN-RIGHT-ABSTRACTION` |
| `ansible-004` | Ansible users are (most likely) not programmers. | Usability | 6 | `ZEN-UNAMBIGUOUS-NAME` |
| `ansible-005` | Clear is better than cluttered. | Clarity | 7 | `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE` |
| `ansible-006` | Concise is better than verbose. | Readability | 5 | `ZEN-UNAMBIGUOUS-NAME` |
| `ansible-007` | Simple is better than complex. | Complexity | 8 | `ZEN-PROPORTIONATE-COMPLEXITY` |
| `ansible-008` | Readability counts. | Readability | 8 | `ZEN-UNAMBIGUOUS-NAME` |
| `ansible-009` | Helping users get things done matters most. | Usability | 7 | `ZEN-UNAMBIGUOUS-NAME`, `ZEN-EXPLICIT-INTENT`, `ZEN-FAIL-FAST` |
| `ansible-010` | User experience beats ideological purity. | Usability | 6 | `ZEN-UNAMBIGUOUS-NAME` |
| `ansible-011` | "Magic" conquers the manual. | Idioms | 6 | `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT` |
| `ansible-012` | When giving users options, use convention over configuration. | Consistency | 6 | `ZEN-EXPLICIT-INTENT` |
| `ansible-013` | Declarative is better than imperative -- most of the time. | Correctness | 8 | `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE` |
| `ansible-014` | Focus avoids complexity. | Organization | 7 | `ZEN-STRICT-FENCES`, `ZEN-PROPORTIONATE-COMPLEXITY` |
| `ansible-015` | Complexity kills productivity. | Complexity | 8 | `ZEN-PROPORTIONATE-COMPLEXITY`, `ZEN-RETURN-EARLY` |
| `ansible-016` | If the implementation is hard to explain, it's a bad idea. | Clarity | 7 | `ZEN-EXPLICIT-INTENT` |
| `ansible-017` | Every shell command and UI interaction is an opportunity to automate. | Idioms | 6 | `ZEN-RIGHT-ABSTRACTION` |
| `ansible-018` | Just because something works, doesn't mean it can't be improved. | Design | 5 | `ZEN-RIGHT-ABSTRACTION` |
| `ansible-019` | Friction should be eliminated whenever possible. | Usability | 7 | `ZEN-UNAMBIGUOUS-NAME` |
| `ansible-020` | Automation is a journey that never ends. | Robustness | 5 | `ZEN-FAIL-FAST` |

??? info "`ansible-001` — Ansible is not Python."
    **Avoid embedding Python-style programming patterns directly in playbooks.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - python command execution embedded in playbook tasks
    - inline python script usage in shell/command tasks

??? info "`ansible-002` — YAML sucks for coding."
    **YAML should describe automation intent, not encode dense program logic.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - complex Jinja control-flow in YAML fields
    - dense inline expressions that reduce readability

??? info "`ansible-003` — Playbooks are not for programming."
    **Prefer declarative module usage over imperative shell/command scripting.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - shell or command used where idempotent module is expected

    **Detectable Patterns:**

    - `shell:`
    - `command:`

??? info "`ansible-004` — Ansible users are (most likely) not programmers."
    **Favor task readability and predictable behavior for operators with varied coding backgrounds.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - deprecated privilege escalation patterns that increase cognitive load

    **Detectable Patterns:**

    - `sudo:`

??? info "`ansible-005` — Clear is better than cluttered."
    **Task intent and desired state should be explicit and unambiguous.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - stateful module used without explicit state

??? info "`ansible-006` — Concise is better than verbose."
    **Keep interpolation and task expressions concise without sacrificing intent.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - Jinja expressions with poor spacing/formatting

    **Detectable Patterns:**

    - `{{`
    - `}}`

??? info "`ansible-007` — Simple is better than complex."
    **Use secure, simple primitives and avoid complex or risky secret handling patterns.**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - cleartext password/token style assignments

??? info "`ansible-008` — Readability counts."
    **Plays and tasks should include descriptive names and readable structure.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - play or task missing a descriptive name

??? info "`ansible-009` — Helping users get things done matters most."
    **Avoid patterns that hide failures or force operators into unclear recovery paths.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`, `ZEN-EXPLICIT-INTENT`, `ZEN-FAIL-FAST`
    **Common Violations:**

    - ignore_errors enabled without explicit rationale

??? info "`ansible-010` — User experience beats ideological purity."
    **Prefer maintainable, user-friendly automation over brittle low-level invocation styles.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - raw command execution used in normal playbook flow

??? info "`ansible-011` — "Magic" conquers the manual."
    **Prefer purpose-built modules over manual package/service shell commands.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`, `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - manual apt/yum/systemctl command invocation via shell/command

??? info "`ansible-012` — When giving users options, use convention over configuration."
    **Use conventional Ansible module naming and invocation styles for predictable playbooks.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - non-FQCN module usage

??? info "`ansible-013` — Declarative is better than imperative -- most of the time."
    **Model desired state declaratively instead of orchestrating imperative command flows.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`, `ZEN-VISIBLE-STATE`
    **Common Violations:**

    - imperative shell/command orchestration in stateful tasks

??? info "`ansible-014` — Focus avoids complexity."
    **Large unfocused plays reduce maintainability and reviewability.**

    **Universal Dogmas:** `ZEN-STRICT-FENCES`, `ZEN-PROPORTIONATE-COMPLEXITY`
    **Common Violations:**

    - single play with excessive task count

??? info "`ansible-015` — Complexity kills productivity."
    **Deep conditional logic and nested control flow increase operational drag.**

    **Universal Dogmas:** `ZEN-PROPORTIONATE-COMPLEXITY`, `ZEN-RETURN-EARLY`
    **Common Violations:**

    - overly complex when conditions

??? info "`ansible-016` — If the implementation is hard to explain, it's a bad idea."
    **Hard-to-explain tasks often present as long opaque command blocks.**

    **Universal Dogmas:** `ZEN-EXPLICIT-INTENT`
    **Common Violations:**

    - overly long inline shell/command expressions

??? info "`ansible-017` — Every shell command and UI interaction is an opportunity to automate."
    **Repeated imperative shell commands indicate automation opportunities.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - repeated shell/command task patterns

??? info "`ansible-018` — Just because something works, doesn't mean it can't be improved."
    **Capture known improvements directly in automation code comments.**

    **Universal Dogmas:** `ZEN-RIGHT-ABSTRACTION`
    **Common Violations:**

    - TODO/FIXME/HACK markers indicating deferred automation improvements

??? info "`ansible-019` — Friction should be eliminated whenever possible."
    **Interactive prompts and pauses introduce avoidable delivery friction.**

    **Universal Dogmas:** `ZEN-UNAMBIGUOUS-NAME`
    **Common Violations:**

    - vars_prompt/pause-driven interactive workflow in automation path

??? info "`ansible-020` — Automation is a journey that never ends."
    **Track and evolve automation by tagging tasks for iterative maintenance.**

    **Universal Dogmas:** `ZEN-FAIL-FAST`
    **Common Violations:**

    - tasks missing maintenance-oriented tags


## Detector Catalog

### Clarity

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AnsibleNamingDetector** | Ensure Ansible plays and tasks include descriptive names | `ansible-001` |
| **AnsibleStateExplicitDetector** | Ensure stateful modules specify explicit state values | `ansible-005` |
| **AnsibleExplainabilityDetector** | Flag command bodies that are difficult to explain at a glance | `ansible-016` |

### Complexity

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AnsibleJinjaSpacingDetector** | Enforce consistent spacing inside Jinja2 interpolation delimiters | `ansible-007` |
| **AnsibleComplexityProductivityDetector** | Detect excessive boolean complexity in task conditions | `ansible-015` |

### Consistency

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AnsibleConventionOverConfigDetector** | Encourage conventional module invocation style (FQCN) | `ansible-012` |

### Correctness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AnsibleDeclarativeBiasDetector** | Bias playbooks toward declarative module usage | `ansible-013` |

### Design

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AnsibleIdempotencyDetector** | Flag shell/command usage where idempotent modules should be preferred | `ansible-003` |
| **AnsibleContinuousImprovementDetector** | Highlight inline debt markers that should become improvement backlog items | `ansible-018` |

### Idioms

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AnsibleMagicAutomationDetector** | Detect manual shell command patterns that should be module-driven | `ansible-011` |
| **AnsibleAutomationOpportunityDetector** | Detect repeated shell commands that indicate module opportunities | `ansible-017` |

### Organization

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AnsibleFocusDetector** | Detect oversized, unfocused plays | `ansible-014` |

### Readability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AnsibleFqcnDetector** | Detect short module names that should use fully qualified collection names | `ansible-002` |
| **AnsibleNoCleartextPasswordDetector** | Detect likely cleartext secret assignments in YAML variables | `ansible-006` |
| **AnsibleReadabilityCountsDetector** | Enforce naming and line readability signals for Ansible content | `ansible-008` |

### Robustness

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AnsibleAutomationJourneyDetector** | Encourage iterative maintenance by requiring task tags | `ansible-020` |

### Usability

| Detector | What It Catches | Rule IDs |
|----------|----------------|----------|
| **AnsibleBecomeDetector** | Flag deprecated sudo usage in plays or tasks | `ansible-004` |
| **AnsibleUserOutcomeDetector** | Flag patterns that hide failure outcomes from users | `ansible-009` |
| **AnsibleUserExperienceDetector** | Prefer maintainable task constructs over raw command execution | `ansible-010` |
| **AnsibleFrictionDetector** | Flag interactive workflow steps that add unnecessary execution friction | `ansible-019` |


??? example "Principle → Detector Wiring"
    ```mermaid
%%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 40, "rankSpacing": 60}}}%%
    graph TD
    ansible_001["ansible-001<br/>Ansible is not Python."]
    ansible_002["ansible-002<br/>YAML sucks for coding."]
    ansible_003["ansible-003<br/>Playbooks are not for pro..."]
    ansible_004["ansible-004<br/>Ansible users are (most l..."]
    ansible_005["ansible-005<br/>Clear is better than clut..."]
    ansible_006["ansible-006<br/>Concise is better than ve..."]
    ansible_007["ansible-007<br/>Simple is better than com..."]
    ansible_008["ansible-008<br/>Readability counts."]
    ansible_009["ansible-009<br/>Helping users get things ..."]
    ansible_010["ansible-010<br/>User experience beats ide..."]
    ansible_011["ansible-011<br/>"Magic" conquers the manu..."]
    ansible_012["ansible-012<br/>When giving users options..."]
    ansible_013["ansible-013<br/>Declarative is better tha..."]
    ansible_014["ansible-014<br/>Focus avoids complexity."]
    ansible_015["ansible-015<br/>Complexity kills producti..."]
    ansible_016["ansible-016<br/>If the implementation is ..."]
    ansible_017["ansible-017<br/>Every shell command and U..."]
    ansible_018["ansible-018<br/>Just because something wo..."]
    ansible_019["ansible-019<br/>Friction should be elimin..."]
    ansible_020["ansible-020<br/>Automation is a journey t..."]
    det_AnsibleAutomationJourneyDetector["AnsibleAutomationJourneyDetector"]
    ansible_020 --> det_AnsibleAutomationJourneyDetector
    det_AnsibleAutomationOpportunityDetector["AnsibleAutomationOpportunityDetector"]
    ansible_017 --> det_AnsibleAutomationOpportunityDetector
    det_AnsibleBecomeDetector["AnsibleBecomeDetector"]
    ansible_004 --> det_AnsibleBecomeDetector
    det_AnsibleComplexityProductivityDetector["AnsibleComplexityProductivityDetector"]
    ansible_015 --> det_AnsibleComplexityProductivityDetector
    det_AnsibleContinuousImprovementDetector["AnsibleContinuousImprovementDetector"]
    ansible_018 --> det_AnsibleContinuousImprovementDetector
    det_AnsibleConventionOverConfigDetector["AnsibleConventionOverConfigDetector"]
    ansible_012 --> det_AnsibleConventionOverConfigDetector
    det_AnsibleDeclarativeBiasDetector["AnsibleDeclarativeBiasDetector"]
    ansible_013 --> det_AnsibleDeclarativeBiasDetector
    det_AnsibleExplainabilityDetector["AnsibleExplainabilityDetector"]
    ansible_016 --> det_AnsibleExplainabilityDetector
    det_AnsibleFocusDetector["AnsibleFocusDetector"]
    ansible_014 --> det_AnsibleFocusDetector
    det_AnsibleFqcnDetector["AnsibleFqcnDetector"]
    ansible_002 --> det_AnsibleFqcnDetector
    det_AnsibleFrictionDetector["AnsibleFrictionDetector"]
    ansible_019 --> det_AnsibleFrictionDetector
    det_AnsibleIdempotencyDetector["AnsibleIdempotencyDetector"]
    ansible_003 --> det_AnsibleIdempotencyDetector
    det_AnsibleJinjaSpacingDetector["AnsibleJinjaSpacingDetector"]
    ansible_007 --> det_AnsibleJinjaSpacingDetector
    det_AnsibleMagicAutomationDetector["AnsibleMagicAutomationDetector"]
    ansible_011 --> det_AnsibleMagicAutomationDetector
    det_AnsibleNamingDetector["AnsibleNamingDetector"]
    ansible_001 --> det_AnsibleNamingDetector
    det_AnsibleNoCleartextPasswordDetector["AnsibleNoCleartextPasswordDetector"]
    ansible_006 --> det_AnsibleNoCleartextPasswordDetector
    det_AnsibleReadabilityCountsDetector["AnsibleReadabilityCountsDetector"]
    ansible_008 --> det_AnsibleReadabilityCountsDetector
    det_AnsibleStateExplicitDetector["AnsibleStateExplicitDetector"]
    ansible_005 --> det_AnsibleStateExplicitDetector
    det_AnsibleUserExperienceDetector["AnsibleUserExperienceDetector"]
    ansible_010 --> det_AnsibleUserExperienceDetector
    det_AnsibleUserOutcomeDetector["AnsibleUserOutcomeDetector"]
    ansible_009 --> det_AnsibleUserOutcomeDetector
    classDef principle fill:#4051b5,color:#ffffff,stroke:#4051b5,stroke-width:2px
    classDef detector fill:#26a269,color:#ffffff,stroke:#26a269,stroke-width:2px
    class ansible_001 principle
    class ansible_002 principle
    class ansible_003 principle
    class ansible_004 principle
    class ansible_005 principle
    class ansible_006 principle
    class ansible_007 principle
    class ansible_008 principle
    class ansible_009 principle
    class ansible_010 principle
    class ansible_011 principle
    class ansible_012 principle
    class ansible_013 principle
    class ansible_014 principle
    class ansible_015 principle
    class ansible_016 principle
    class ansible_017 principle
    class ansible_018 principle
    class ansible_019 principle
    class ansible_020 principle
    class det_AnsibleAutomationJourneyDetector detector
    class det_AnsibleAutomationOpportunityDetector detector
    class det_AnsibleBecomeDetector detector
    class det_AnsibleComplexityProductivityDetector detector
    class det_AnsibleContinuousImprovementDetector detector
    class det_AnsibleConventionOverConfigDetector detector
    class det_AnsibleDeclarativeBiasDetector detector
    class det_AnsibleExplainabilityDetector detector
    class det_AnsibleFocusDetector detector
    class det_AnsibleFqcnDetector detector
    class det_AnsibleFrictionDetector detector
    class det_AnsibleIdempotencyDetector detector
    class det_AnsibleJinjaSpacingDetector detector
    class det_AnsibleMagicAutomationDetector detector
    class det_AnsibleNamingDetector detector
    class det_AnsibleNoCleartextPasswordDetector detector
    class det_AnsibleReadabilityCountsDetector detector
    class det_AnsibleStateExplicitDetector detector
    class det_AnsibleUserExperienceDetector detector
    class det_AnsibleUserOutcomeDetector detector
    ```

??? example "Detector Class Hierarchy"
    ```mermaid
%%{init: {"theme": "base"}}%%
    classDiagram
        direction TB
        class ViolationDetector {
            <<abstract>>
            +detect(context, config) list~Violation~
        }
        class AnsibleAutomationJourneyDetector {
            +rules "ansible-020"
        }
        ViolationDetector <|-- AnsibleAutomationJourneyDetector
        class AnsibleAutomationOpportunityDetector {
            +rules "ansible-017"
        }
        ViolationDetector <|-- AnsibleAutomationOpportunityDetector
        class AnsibleBecomeDetector {
            +rules "ansible-004"
        }
        ViolationDetector <|-- AnsibleBecomeDetector
        class AnsibleComplexityProductivityDetector {
            +rules "ansible-015"
        }
        ViolationDetector <|-- AnsibleComplexityProductivityDetector
        class AnsibleContinuousImprovementDetector {
            +rules "ansible-018"
        }
        ViolationDetector <|-- AnsibleContinuousImprovementDetector
        class AnsibleConventionOverConfigDetector {
            +rules "ansible-012"
        }
        ViolationDetector <|-- AnsibleConventionOverConfigDetector
        class AnsibleDeclarativeBiasDetector {
            +rules "ansible-013"
        }
        ViolationDetector <|-- AnsibleDeclarativeBiasDetector
        class AnsibleExplainabilityDetector {
            +rules "ansible-016"
        }
        ViolationDetector <|-- AnsibleExplainabilityDetector
        class AnsibleFocusDetector {
            +rules "ansible-014"
        }
        ViolationDetector <|-- AnsibleFocusDetector
        class AnsibleFqcnDetector {
            +rules "ansible-002"
        }
        ViolationDetector <|-- AnsibleFqcnDetector
        class AnsibleFrictionDetector {
            +rules "ansible-019"
        }
        ViolationDetector <|-- AnsibleFrictionDetector
        class AnsibleIdempotencyDetector {
            +rules "ansible-003"
        }
        ViolationDetector <|-- AnsibleIdempotencyDetector
        class AnsibleJinjaSpacingDetector {
            +rules "ansible-007"
        }
        ViolationDetector <|-- AnsibleJinjaSpacingDetector
        class AnsibleMagicAutomationDetector {
            +rules "ansible-011"
        }
        ViolationDetector <|-- AnsibleMagicAutomationDetector
        class AnsibleNamingDetector {
            +rules "ansible-001"
        }
        ViolationDetector <|-- AnsibleNamingDetector
        class AnsibleNoCleartextPasswordDetector {
            +rules "ansible-006"
        }
        ViolationDetector <|-- AnsibleNoCleartextPasswordDetector
        class AnsibleReadabilityCountsDetector {
            +rules "ansible-008"
        }
        ViolationDetector <|-- AnsibleReadabilityCountsDetector
        class AnsibleStateExplicitDetector {
            +rules "ansible-005"
        }
        ViolationDetector <|-- AnsibleStateExplicitDetector
        class AnsibleUserExperienceDetector {
            +rules "ansible-010"
        }
        ViolationDetector <|-- AnsibleUserExperienceDetector
        class AnsibleUserOutcomeDetector {
            +rules "ansible-009"
        }
        ViolationDetector <|-- AnsibleUserOutcomeDetector
        classDef abstract fill:#4051b5,color:#ffffff,stroke:#4051b5,stroke-width:2px
        classDef detector fill:#26a269,color:#ffffff,stroke:#26a269,stroke-width:2px
        class ViolationDetector abstract
        class AnsibleAutomationJourneyDetector,AnsibleAutomationOpportunityDetector,AnsibleBecomeDetector,AnsibleComplexityProductivityDetector,AnsibleContinuousImprovementDetector,AnsibleConventionOverConfigDetector,AnsibleDeclarativeBiasDetector,AnsibleExplainabilityDetector,AnsibleFocusDetector,AnsibleFqcnDetector,AnsibleFrictionDetector,AnsibleIdempotencyDetector,AnsibleJinjaSpacingDetector,AnsibleMagicAutomationDetector,AnsibleNamingDetector,AnsibleNoCleartextPasswordDetector,AnsibleReadabilityCountsDetector,AnsibleStateExplicitDetector,AnsibleUserExperienceDetector,AnsibleUserOutcomeDetector detector
    ```

??? example "Analysis Pipeline"
    ```mermaid
%%{init: {"theme": "base", "flowchart": {"useMaxWidth": false, "htmlLabels": true, "nodeSpacing": 50, "rankSpacing": 70}}}%%
    flowchart TD
    Source(["📄 Source Code"]) --> Parse["Parse & Tokenize"]
    Parse --> Metrics["Compute Metrics"]
    Metrics --> Pipeline{"20 Detectors"}
    Pipeline --> Collect["Aggregate Violations"]
    Collect --> Result(["✅ AnalysisResult · 20 principles"])

    classDef io fill:#4051b5,color:#ffffff,stroke:#4051b5,stroke-width:2px
    classDef process fill:#26a269,color:#ffffff,stroke:#26a269,stroke-width:2px
    classDef decision fill:#b55400,color:#ffffff,stroke:#b55400,stroke-width:2px
    class Source,Result io
    class Parse,Metrics,Collect process
    class Pipeline decision
    ```

??? example "Analysis States"
    ```mermaid
%%{init: {"theme": "base"}}%%
    stateDiagram-v2
        [*] --> Ready
        Ready --> Parsing : analyze(code)
        Parsing --> Computing : AST ready
        Computing --> Detecting : metrics ready
        Detecting --> Reporting : 20 detectors run
        Reporting --> [*] : AnalysisResult
        Parsing --> Reporting : parse error (best-effort)
    ```

## Configuration

```yaml
languages:
  ansible:
    enabled: true
    pipeline:
      - type: ansible-014
        max_tasks_per_play: 20
      - type: ansible-015
        max_condition_operators: 3
      - type: ansible-016
        max_inline_command_length: 120
      - type: ansible-017
        min_repeated_shell_commands: 2
```


## See Also

- [GitHub Actions](github-actions.md) — Workflow automation counterpart in CI environments
- [Configuration](../configuration.md) — Per-language pipeline overrides
- [Understanding Violations](../understanding-violations.md) — Severity scale reference
