"""Terraform zen principles as Pydantic models."""

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
from mcp_zen_of_languages.rules.base_models import PrincipleCategory
from mcp_zen_of_languages.rules.base_models import ZenPrinciple


TERRAFORM_ZEN = LanguageZenPrinciples(
    language="terraform",
    name="Terraform",
    philosophy="Terraform Language Documentation",
    source_text="Terraform language and module best-practice documentation",
    source_url=HttpUrl("https://developer.hashicorp.com/terraform/language"),
    principles=[
        ZenPrinciple(
            id="tf-001",
            principle="Pin provider versions",
            category=PrincipleCategory.CONFIGURATION,
            severity=8,
            description="Providers should use explicit version constraints.",
            violations=["Provider block missing explicit version pinning"],
        ),
        ZenPrinciple(
            id="tf-002",
            principle="Pin module versions",
            category=PrincipleCategory.CONFIGURATION,
            severity=8,
            description="External module sources should be pinned to versions or commit refs.",
            violations=["Module source without version pinning"],
        ),
        ZenPrinciple(
            id="tf-003",
            principle="Describe variables and outputs",
            category=PrincipleCategory.DOCUMENTATION,
            severity=5,
            description="Variable and output blocks should include descriptions.",
            violations=["Variable or output missing description"],
        ),
        ZenPrinciple(
            id="tf-004",
            principle="Avoid hardcoded resource IDs",
            category=PrincipleCategory.CONFIGURATION,
            severity=7,
            description="Hardcoded ARNs/IDs reduce portability across environments.",
            violations=["Hardcoded ARN or cloud resource identifier"],
        ),
        ZenPrinciple(
            id="tf-005",
            principle="Avoid hardcoded secrets",
            category=PrincipleCategory.SECURITY,
            severity=9,
            description="Credentials and secrets should not be embedded in Terraform source.",
            violations=["Potential hardcoded secret in Terraform block"],
        ),
        ZenPrinciple(
            id="tf-006",
            principle="Configure remote state backend",
            category=PrincipleCategory.ROBUSTNESS,
            severity=7,
            description="Shared environments should configure an explicit remote backend.",
            violations=["Terraform backend block missing"],
        ),
        ZenPrinciple(
            id="tf-007",
            principle="Use consistent snake_case naming",
            category=PrincipleCategory.NAMING,
            severity=5,
            description="Resource and variable names should follow snake_case convention.",
            violations=["Resource or variable name not in snake_case"],
        ),
    ],
)
