from __future__ import annotations

from mcp_zen_of_languages.analyzers.registry import DetectorRegistry


def test_shell_and_container_language_mappings_author_family_ids() -> None:
    registry = DetectorRegistry()
    registry.bootstrap_from_mappings()

    assert registry.testing_ids_for("bash_strict_mode", "bash", "bash-001") == [
        "shellcheck",
    ]
    assert registry.verified_testing_ids_for(
        "bash_strict_mode", "bash", "bash-001"
    ) == [
        "shellcheck",
    ]
    assert registry.projection_ids_for("bash_strict_mode", "bash", "bash-001") == [
        "bash",
        "powershell",
        "python",
    ]
    assert registry.verified_projection_ids_for(
        "bash_strict_mode",
        "bash",
        "bash-001",
    ) == ["bash"]

    assert registry.testing_ids_for(
        "powershell_error_handling",
        "powershell",
        "ps-002",
    ) == ["psscriptanalyzer"]
    assert registry.verified_testing_ids_for(
        "powershell_error_handling",
        "powershell",
        "ps-002",
    ) == ["psscriptanalyzer"]
    assert registry.projection_ids_for(
        "powershell_error_handling",
        "powershell",
        "ps-002",
    ) == ["powershell", "bash", "python"]
    assert registry.verified_projection_ids_for(
        "powershell_error_handling",
        "powershell",
        "ps-002",
    ) == ["powershell"]

    assert registry.testing_ids_for(
        "dockerfile-002", "dockerfile", "dockerfile-002"
    ) == [
        "hadolint",
    ]
    assert registry.verified_testing_ids_for(
        "dockerfile-002",
        "dockerfile",
        "dockerfile-002",
    ) == ["hadolint"]
    assert registry.projection_ids_for(
        "dockerfile-002", "dockerfile", "dockerfile-002"
    ) == [
        "dockerfile",
        "docker_compose",
    ]
    assert registry.verified_projection_ids_for(
        "dockerfile-002",
        "dockerfile",
        "dockerfile-002",
    ) == ["dockerfile"]

    assert registry.testing_ids_for(
        "docker-compose-002",
        "docker_compose",
        "docker-compose-002",
    ) == ["docker-compose-config"]
    assert registry.verified_testing_ids_for(
        "docker-compose-002",
        "docker_compose",
        "docker-compose-002",
    ) == ["docker-compose-config"]
    assert registry.projection_ids_for(
        "docker-compose-002",
        "docker_compose",
        "docker-compose-002",
    ) == ["docker_compose", "dockerfile"]
    assert registry.verified_projection_ids_for(
        "docker-compose-002",
        "docker_compose",
        "docker-compose-002",
    ) == ["docker_compose"]


def test_shell_and_container_family_registry_lookups_return_expected_models() -> None:
    registry = DetectorRegistry()
    registry.bootstrap_from_mappings()

    assert [
        model.detector_id
        for model in registry.testing_models_for_family("shellcheck", "bash")
    ] == ["bash-005", "bash-010", "bash-012", "bash_strict_mode"]
    assert [
        model.detector_id
        for model in registry.testing_models_for_family(
            "psscriptanalyzer",
            "powershell",
        )
    ] == [
        "powershell_error_handling",
        "powershell_null_handling",
        "powershell_parameter_validation",
    ]
    assert [
        model.detector_id
        for model in registry.testing_models_for_family("hadolint", "dockerfile")
    ] == ["dockerfile-001", "dockerfile-002", "dockerfile-004", "dockerfile-006"]
    assert [
        model.detector_id
        for model in registry.testing_models_for_family(
            "docker-compose-config",
            "docker_compose",
        )
    ] == [
        "docker-compose-001",
        "docker-compose-002",
        "docker-compose-003",
        "docker-compose-004",
    ]

    assert [
        model.detector_id
        for model in registry.projection_models_for_family("powershell", "bash")
    ] == ["bash-005", "bash-010", "bash-012", "bash_strict_mode"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_family("bash", "powershell")
    ] == [
        "powershell_error_handling",
        "powershell_parameter_validation",
    ]
    assert [
        model.detector_id
        for model in registry.projection_models_for_family(
            "docker_compose",
            "dockerfile",
        )
    ] == ["dockerfile-001", "dockerfile-002", "dockerfile-004", "dockerfile-006"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_family(
            "dockerfile",
            "docker_compose",
        )
    ] == [
        "docker-compose-001",
        "docker-compose-002",
        "docker-compose-003",
        "docker-compose-004",
    ]
