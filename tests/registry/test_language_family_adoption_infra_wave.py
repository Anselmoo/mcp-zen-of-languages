from __future__ import annotations

from mcp_zen_of_languages.analyzers.registry import DetectorRegistry


def test_infra_and_ci_language_mappings_author_testing_and_projection_families() -> (
    None
):
    registry = DetectorRegistry()
    registry.bootstrap_from_mappings()

    assert registry.testing_ids_for("tf-001", "terraform", "tf-001") == [
        "terraform-validate",
    ]
    assert registry.verified_testing_ids_for("tf-001", "terraform", "tf-001") == [
        "terraform-validate",
    ]
    assert registry.projection_ids_for("tf-001", "terraform", "tf-001") == [
        "terraform",
    ]
    assert registry.verified_projection_ids_for("tf-001", "terraform", "tf-001") == [
        "terraform",
    ]

    assert registry.testing_ids_for("ansible-003", "ansible", "ansible-003") == [
        "molecule",
    ]
    assert registry.verified_testing_ids_for(
        "ansible-003",
        "ansible",
        "ansible-003",
    ) == ["molecule"]
    assert registry.projection_ids_for("ansible-005", "ansible", "ansible-005") == [
        "ansible",
    ]
    assert registry.verified_projection_ids_for(
        "ansible-005",
        "ansible",
        "ansible-005",
    ) == ["ansible"]

    assert registry.testing_ids_for("yaml-003", "yaml", "yaml-003") == ["yamllint"]
    assert registry.verified_testing_ids_for("yaml-003", "yaml", "yaml-003") == [
        "yamllint",
    ]
    assert registry.projection_ids_for("yaml-003", "yaml", "yaml-003") == [
        "yaml",
        "ansible",
        "github-actions",
        "gitlab_ci",
    ]
    assert registry.verified_projection_ids_for("yaml-003", "yaml", "yaml-003") == [
        "yaml",
    ]

    assert registry.testing_ids_for("gitlab-ci-008", "gitlab_ci", "gitlab-ci-008") == [
        "gitlab-ci-lint",
    ]
    assert registry.verified_testing_ids_for(
        "gitlab-ci-008",
        "gitlab_ci",
        "gitlab-ci-008",
    ) == ["gitlab-ci-lint"]
    assert registry.projection_ids_for(
        "gitlab-ci-008", "gitlab_ci", "gitlab-ci-008"
    ) == [
        "gitlab_ci",
        "github-actions",
    ]
    assert registry.verified_projection_ids_for(
        "gitlab-ci-008",
        "gitlab_ci",
        "gitlab-ci-008",
    ) == ["gitlab_ci"]

    assert registry.testing_ids_for("gha-workflow", "github-actions", "gha-007") == [
        "actionlint",
    ]
    assert registry.verified_testing_ids_for(
        "gha-workflow",
        "github-actions",
        "gha-007",
    ) == ["actionlint"]
    assert registry.projection_ids_for("gha-workflow", "github-actions", "gha-007") == [
        "github-actions",
        "gitlab_ci",
    ]
    assert registry.verified_projection_ids_for(
        "gha-workflow",
        "github-actions",
        "gha-007",
    ) == ["github-actions"]


def test_infra_and_ci_family_registry_lookups_return_expected_models() -> None:
    registry = DetectorRegistry()
    registry.bootstrap_from_mappings()

    assert [
        model.detector_id
        for model in registry.testing_models_for_family(
            "terraform-validate", "terraform"
        )
    ] == ["tf-001", "tf-002", "tf-006"]
    assert [
        model.detector_id
        for model in registry.testing_models_for_family("molecule", "ansible")
    ] == ["ansible-003", "ansible-005"]
    assert [
        model.detector_id
        for model in registry.testing_models_for_family("yamllint", "yaml")
    ] == ["yaml-001", "yaml-002", "yaml-003"]
    assert [
        model.detector_id
        for model in registry.testing_models_for_family("gitlab-ci-lint", "gitlab_ci")
    ] == ["gitlab-ci-008"]
    assert [
        model.detector_id
        for model in registry.testing_models_for_family("actionlint", "github-actions")
    ] == ["gha-workflow"]

    assert [
        model.detector_id
        for model in registry.projection_models_for_family("terraform", "terraform")
    ] == ["tf-001", "tf-002", "tf-006"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_family("ansible", "yaml")
    ] == ["yaml-001", "yaml-002", "yaml-003"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_family(
            "gitlab_ci", "github-actions"
        )
    ] == ["gha-workflow"]
