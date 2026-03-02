from __future__ import annotations

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer


def test_terraform_analyze_end_to_end() -> None:
    result = create_analyzer("terraform").analyze(
        'terraform {\n  required_version = ">= 1.6.0"\n}\n'
        'provider "aws" {\n  region = "eu-central-1"\n}\n'
        'module "vpc" {\n  source = "terraform-aws-modules/vpc/aws"\n}\n'
        'variable "VpcId" {\n  type = string\n}\n'
        'resource "aws_instance" "WebServer" {\n'
        '  subnet_id = "subnet-123abc"\n'
        '  db_password = "hardcoded"\n'
        "}\n",
        path="main.tf",
    )
    assert result.language == "terraform"
    assert result.violations
