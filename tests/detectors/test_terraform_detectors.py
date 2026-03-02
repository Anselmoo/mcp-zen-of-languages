from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import TerraformBackendConfig
from mcp_zen_of_languages.languages.configs import TerraformHardcodedIdConfig
from mcp_zen_of_languages.languages.configs import TerraformModuleVersionPinningConfig
from mcp_zen_of_languages.languages.configs import TerraformNamingConventionConfig
from mcp_zen_of_languages.languages.configs import TerraformNoHardcodedSecretsConfig
from mcp_zen_of_languages.languages.configs import TerraformProviderVersionPinningConfig
from mcp_zen_of_languages.languages.configs import TerraformVariableOutputDescriptionConfig
from mcp_zen_of_languages.languages.terraform.detectors import TerraformBackendConfigDetector
from mcp_zen_of_languages.languages.terraform.detectors import TerraformHardcodedIdDetector
from mcp_zen_of_languages.languages.terraform.detectors import (
    TerraformModuleVersionPinningDetector,
)
from mcp_zen_of_languages.languages.terraform.detectors import (
    TerraformNamingConventionDetector,
)
from mcp_zen_of_languages.languages.terraform.detectors import (
    TerraformNoHardcodedSecretsDetector,
)
from mcp_zen_of_languages.languages.terraform.detectors import (
    TerraformProviderVersionPinningDetector,
)
from mcp_zen_of_languages.languages.terraform.detectors import (
    TerraformVariableOutputDescriptionDetector,
)


def test_terraform_detectors_emit_expected_violations() -> None:
    context = AnalysisContext(
        code=(
            'terraform {\n  required_version = ">= 1.6.0"\n}\n'
            'provider "aws" {\n  region = "eu-central-1"\n}\n'
            'module "vpc" {\n  source = "terraform-aws-modules/vpc/aws"\n}\n'
            'variable "VpcId" {\n  type = string\n}\n'
            'output "PublicSubnet" {\n  value = aws_subnet.public.id\n}\n'
            'resource "aws_instance" "WebServer" {\n'
            '  ami = "ami-123456"\n'
            '  subnet_id = "subnet-123abc"\n'
            '  db_password = "supersecret"\n'
            "}\n"
        ),
        language="terraform",
    )
    assert TerraformProviderVersionPinningDetector().detect(
        context, TerraformProviderVersionPinningConfig()
    )
    assert TerraformModuleVersionPinningDetector().detect(
        context, TerraformModuleVersionPinningConfig()
    )
    assert TerraformVariableOutputDescriptionDetector().detect(
        context, TerraformVariableOutputDescriptionConfig()
    )
    assert TerraformHardcodedIdDetector().detect(context, TerraformHardcodedIdConfig())
    assert TerraformNoHardcodedSecretsDetector().detect(
        context, TerraformNoHardcodedSecretsConfig()
    )
    assert TerraformBackendConfigDetector().detect(context, TerraformBackendConfig())
    assert TerraformNamingConventionDetector().detect(
        context, TerraformNamingConventionConfig()
    )


def test_terraform_detectors_cover_clean_paths() -> None:
    context = AnalysisContext(
        code=(
            'terraform {\n'
            '  required_version = ">= 1.6.0"\n'
            '  backend "s3" {\n'
            '    bucket = "state-bucket"\n'
            '    key    = "env/prod/terraform.tfstate"\n'
            '    region = "eu-central-1"\n'
            "  }\n"
            "}\n"
            'provider "aws" {\n  version = "~> 5.0"\n  region = "eu-central-1"\n}\n'
            'module "vpc" {\n'
            '  source  = "terraform-aws-modules/vpc/aws"\n'
            '  version = "5.0.0"\n'
            "}\n"
            'variable "vpc_id" {\n  description = "VPC ID"\n  type = string\n}\n'
            'output "public_subnet_id" {\n'
            '  description = "Public subnet id"\n'
            "  value       = data.aws_subnet.public.id\n"
            "}\n"
            'resource "aws_instance" "web_server" {\n'
            "  subnet_id    = data.aws_subnet.public.id\n"
            "  db_password  = var.db_password\n"
            "}\n"
        ),
        language="terraform",
    )
    assert TerraformProviderVersionPinningDetector().name == "tf-001"
    assert TerraformModuleVersionPinningDetector().name == "tf-002"
    assert TerraformVariableOutputDescriptionDetector().name == "tf-003"
    assert TerraformHardcodedIdDetector().name == "tf-004"
    assert TerraformNoHardcodedSecretsDetector().name == "tf-005"
    assert TerraformBackendConfigDetector().name == "tf-006"
    assert TerraformNamingConventionDetector().name == "tf-007"
    assert not TerraformProviderVersionPinningDetector().detect(
        context, TerraformProviderVersionPinningConfig()
    )
    assert not TerraformModuleVersionPinningDetector().detect(
        context, TerraformModuleVersionPinningConfig()
    )
    assert not TerraformVariableOutputDescriptionDetector().detect(
        context, TerraformVariableOutputDescriptionConfig()
    )
    assert not TerraformHardcodedIdDetector().detect(context, TerraformHardcodedIdConfig())
    assert not TerraformNoHardcodedSecretsDetector().detect(
        context, TerraformNoHardcodedSecretsConfig()
    )
    assert not TerraformBackendConfigDetector().detect(context, TerraformBackendConfig())
    assert not TerraformNamingConventionDetector().detect(
        context, TerraformNamingConventionConfig()
    )
