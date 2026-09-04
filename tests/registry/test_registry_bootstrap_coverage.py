from __future__ import annotations

from mcp_zen_of_languages.analyzers import registry_bootstrap


def test_bootstrap_registry_idempotent():
    registry_bootstrap.REGISTRY.items()
    registry_bootstrap.REGISTRY.items()


def test_build_rule_configs_handles_known_and_dynamic_rules():
    configs = registry_bootstrap._build_rule_configs(["bash-006", "custom-001"])
    # Calling with no arguments is the behaviour under test: _build_rule_configs
    # defaults `type` to the rule id. ty reads the pydantic.create_model-generated
    # signature, where `type` is declared required, so it cannot see that default.
    assert configs["bash-006"]().type == "bash-006"  # ty: ignore[missing-argument]
    assert configs["custom-001"]().type == "custom-001"  # ty: ignore[missing-argument]
