"""Ansible zen principles as Pydantic models."""

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
from mcp_zen_of_languages.rules.base_models import PrincipleCategory
from mcp_zen_of_languages.rules.base_models import ZenPrinciple


ANSIBLE_ZEN = LanguageZenPrinciples(
    language="ansible",
    name="Ansible",
    philosophy="Idempotent, secure, and maintainable infrastructure automation.",
    source_text="Ansible Documentation",
    source_url=HttpUrl("https://docs.ansible.com/"),
    principles=[
        ZenPrinciple(
            id="ansible-001",
            principle="Name all tasks and plays",
            category=PrincipleCategory.READABILITY,
            severity=6,
            description="Every play and task should have a descriptive name for clear logs.",
            violations=["play or task missing name"],
        ),
        ZenPrinciple(
            id="ansible-002",
            principle="Use fully qualified collection names",
            category=PrincipleCategory.CONSISTENCY,
            severity=5,
            description="Prefer explicit module namespaces such as ansible.builtin.command.",
            violations=["module called without FQCN"],
        ),
        ZenPrinciple(
            id="ansible-003",
            principle="Prefer idempotent modules over command or shell",
            category=PrincipleCategory.IDIOMS,
            severity=8,
            description="Avoid shell/command for actions with dedicated idempotent modules.",
            violations=["shell or command module used"],
            detectable_patterns=["shell:", "command:"],
        ),
        ZenPrinciple(
            id="ansible-004",
            principle="Use become instead of sudo",
            category=PrincipleCategory.IDIOMS,
            severity=7,
            description="The sudo key is deprecated; use become for privilege escalation.",
            violations=["sudo key used"],
            detectable_patterns=["sudo:"],
        ),
        ZenPrinciple(
            id="ansible-005",
            principle="State should be explicit",
            category=PrincipleCategory.CORRECTNESS,
            severity=6,
            description="Specify explicit module state instead of relying on defaults.",
            violations=["task module missing explicit state"],
        ),
        ZenPrinciple(
            id="ansible-006",
            principle="No cleartext passwords",
            category=PrincipleCategory.SECURITY,
            severity=9,
            description="Sensitive values should be vaulted or externally sourced.",
            violations=["potential cleartext secret in variable assignment"],
        ),
        ZenPrinciple(
            id="ansible-007",
            principle="Use clean Jinja2 variable spacing",
            category=PrincipleCategory.CONSISTENCY,
            severity=4,
            description="Prefer {{ var_name }} spacing style for readability and consistency.",
            violations=["Jinja expression missing inner spacing"],
            detectable_patterns=["{{", "}}"],
        ),
    ],
)
