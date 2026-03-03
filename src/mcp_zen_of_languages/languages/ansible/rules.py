"""Ansible zen principles as Pydantic models."""

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
from mcp_zen_of_languages.rules.base_models import PrincipleCategory
from mcp_zen_of_languages.rules.base_models import ZenPrinciple


ANSIBLE_ZEN = LanguageZenPrinciples(
    language="ansible",
    name="Ansible",
    philosophy="Simple, powerful, and human-centered automation",
    source_text="The Zen of Ansible (Red Hat)",
    source_url=HttpUrl("https://www.redhat.com/en/blog/the-zen-of-ansible"),
    principles=[
        ZenPrinciple(
            id="ansible-001",
            principle="Ansible is not Python.",
            category=PrincipleCategory.CLARITY,
            severity=7,
            description=(
                "Avoid embedding Python-style programming patterns directly in playbooks."
            ),
            violations=[
                "python command execution embedded in playbook tasks",
                "inline python script usage in shell/command tasks",
            ],
        ),
        ZenPrinciple(
            id="ansible-002",
            principle="YAML sucks for coding.",
            category=PrincipleCategory.READABILITY,
            severity=7,
            description=(
                "YAML should describe automation intent, not encode dense program logic."
            ),
            violations=[
                "complex Jinja control-flow in YAML fields",
                "dense inline expressions that reduce readability",
            ],
        ),
        ZenPrinciple(
            id="ansible-003",
            principle="Playbooks are not for programming.",
            category=PrincipleCategory.DESIGN,
            severity=8,
            description=(
                "Prefer declarative module usage over imperative shell/command scripting."
            ),
            violations=[
                "shell or command used where idempotent module is expected",
            ],
            detectable_patterns=["shell:", "command:"],
        ),
        ZenPrinciple(
            id="ansible-004",
            principle="Ansible users are (most likely) not programmers.",
            category=PrincipleCategory.USABILITY,
            severity=6,
            description=(
                "Favor task readability and predictable behavior for operators with varied coding backgrounds."
            ),
            violations=[
                "deprecated privilege escalation patterns that increase cognitive load",
            ],
            detectable_patterns=["sudo:"],
        ),
        ZenPrinciple(
            id="ansible-005",
            principle="Clear is better than cluttered.",
            category=PrincipleCategory.CLARITY,
            severity=7,
            description="Task intent and desired state should be explicit and unambiguous.",
            violations=[
                "stateful module used without explicit state",
            ],
        ),
        ZenPrinciple(
            id="ansible-006",
            principle="Concise is better than verbose.",
            category=PrincipleCategory.READABILITY,
            severity=5,
            description="Keep interpolation and task expressions concise without sacrificing intent.",
            violations=[
                "Jinja expressions with poor spacing/formatting",
            ],
            detectable_patterns=["{{", "}}"],
        ),
        ZenPrinciple(
            id="ansible-007",
            principle="Simple is better than complex.",
            category=PrincipleCategory.COMPLEXITY,
            severity=8,
            description=(
                "Use secure, simple primitives and avoid complex or risky secret handling patterns."
            ),
            violations=[
                "cleartext password/token style assignments",
            ],
        ),
        ZenPrinciple(
            id="ansible-008",
            principle="Readability counts.",
            category=PrincipleCategory.READABILITY,
            severity=8,
            description="Plays and tasks should include descriptive names and readable structure.",
            violations=[
                "play or task missing a descriptive name",
            ],
        ),
        ZenPrinciple(
            id="ansible-009",
            principle="Helping users get things done matters most.",
            category=PrincipleCategory.USABILITY,
            severity=7,
            description=(
                "Avoid patterns that hide failures or force operators into unclear recovery paths."
            ),
            violations=[
                "ignore_errors enabled without explicit rationale",
            ],
        ),
        ZenPrinciple(
            id="ansible-010",
            principle="User experience beats ideological purity.",
            category=PrincipleCategory.USABILITY,
            severity=6,
            description=(
                "Prefer maintainable, user-friendly automation over brittle low-level invocation styles."
            ),
            violations=[
                "raw command execution used in normal playbook flow",
            ],
        ),
        ZenPrinciple(
            id="ansible-011",
            principle='"Magic" conquers the manual.',
            category=PrincipleCategory.IDIOMS,
            severity=6,
            description=(
                "Prefer purpose-built modules over manual package/service shell commands."
            ),
            violations=[
                "manual apt/yum/systemctl command invocation via shell/command",
            ],
        ),
        ZenPrinciple(
            id="ansible-012",
            principle="When giving users options, use convention over configuration.",
            category=PrincipleCategory.CONSISTENCY,
            severity=6,
            description=(
                "Use conventional Ansible module naming and invocation styles for predictable playbooks."
            ),
            violations=[
                "non-FQCN module usage",
            ],
        ),
        ZenPrinciple(
            id="ansible-013",
            principle="Declarative is better than imperative -- most of the time.",
            category=PrincipleCategory.CORRECTNESS,
            severity=8,
            description=(
                "Model desired state declaratively instead of orchestrating imperative command flows."
            ),
            violations=[
                "imperative shell/command orchestration in stateful tasks",
            ],
        ),
        ZenPrinciple(
            id="ansible-014",
            principle="Focus avoids complexity.",
            category=PrincipleCategory.ORGANIZATION,
            severity=7,
            description="Large unfocused plays reduce maintainability and reviewability.",
            violations=[
                "single play with excessive task count",
            ],
        ),
        ZenPrinciple(
            id="ansible-015",
            principle="Complexity kills productivity.",
            category=PrincipleCategory.COMPLEXITY,
            severity=8,
            description="Deep conditional logic and nested control flow increase operational drag.",
            violations=[
                "overly complex when conditions",
            ],
        ),
        ZenPrinciple(
            id="ansible-016",
            principle="If the implementation is hard to explain, it's a bad idea.",
            category=PrincipleCategory.CLARITY,
            severity=7,
            description=(
                "Hard-to-explain tasks often present as long opaque command blocks."
            ),
            violations=[
                "overly long inline shell/command expressions",
            ],
        ),
        ZenPrinciple(
            id="ansible-017",
            principle="Every shell command and UI interaction is an opportunity to automate.",
            category=PrincipleCategory.IDIOMS,
            severity=6,
            description=(
                "Repeated imperative shell commands indicate automation opportunities."
            ),
            violations=[
                "repeated shell/command task patterns",
            ],
        ),
        ZenPrinciple(
            id="ansible-018",
            principle="Just because something works, doesn't mean it can't be improved.",
            category=PrincipleCategory.DESIGN,
            severity=5,
            description="Capture known improvements directly in automation code comments.",
            violations=[
                "TODO/FIXME/HACK markers indicating deferred automation improvements",
            ],
        ),
        ZenPrinciple(
            id="ansible-019",
            principle="Friction should be eliminated whenever possible.",
            category=PrincipleCategory.USABILITY,
            severity=7,
            description=(
                "Interactive prompts and pauses introduce avoidable delivery friction."
            ),
            violations=[
                "vars_prompt/pause-driven interactive workflow in automation path",
            ],
        ),
        ZenPrinciple(
            id="ansible-020",
            principle="Automation is a journey that never ends.",
            category=PrincipleCategory.ROBUSTNESS,
            severity=5,
            description=(
                "Track and evolve automation by tagging tasks for iterative maintenance."
            ),
            violations=[
                "tasks missing maintenance-oriented tags",
            ],
        ),
    ],
)
