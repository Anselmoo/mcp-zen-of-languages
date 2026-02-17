from __future__ import annotations

from mcp_zen_of_languages.analyzers import registry_bootstrap


def test_bootstrap_registry_idempotent():
    registry_bootstrap.REGISTRY.items()
    registry_bootstrap.REGISTRY.items()


def test_build_rule_configs_handles_known_and_dynamic_rules():
    configs = registry_bootstrap._build_rule_configs(["bash-006", "custom-001"])
    assert configs["bash-006"]().type == "bash-006"
    assert configs["custom-001"]().type == "custom-001"
