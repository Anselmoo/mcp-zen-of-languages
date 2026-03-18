from __future__ import annotations

from mcp_zen_of_languages.analyzers.registry import DetectorRegistry
from mcp_zen_of_languages.frameworks.angular.mapping import DETECTOR_MAP as ANGULAR_MAP
from mcp_zen_of_languages.frameworks.django.mapping import DETECTOR_MAP as DJANGO_MAP
from mcp_zen_of_languages.frameworks.fastapi.mapping import DETECTOR_MAP as FASTAPI_MAP
from mcp_zen_of_languages.frameworks.nextjs.mapping import DETECTOR_MAP as NEXTJS_MAP
from mcp_zen_of_languages.frameworks.pydantic.mapping import (
    DETECTOR_MAP as PYDANTIC_MAP,
)
from mcp_zen_of_languages.frameworks.react.mapping import DETECTOR_MAP as REACT_MAP
from mcp_zen_of_languages.frameworks.sqlalchemy.mapping import (
    DETECTOR_MAP as SQLALCHEMY_MAP,
)
from mcp_zen_of_languages.frameworks.vue.mapping import DETECTOR_MAP as VUE_MAP


def _binding_map(detector_map) -> dict[str, object]:
    return {binding.detector_id: binding for binding in detector_map.bindings}


def _build_registry(*detector_maps) -> DetectorRegistry:
    registry = DetectorRegistry()
    for detector_map in detector_maps:
        for binding in detector_map.bindings:
            bundle = binding.build_bundle(detector_map.language)
            registry.register(bundle.require_rule_model(), bundle=bundle)
    return registry


def test_react_framework_mapping_authors_jest_and_nextjs_families() -> None:
    binding_map = _binding_map(REACT_MAP)

    assert binding_map["react-004"].rule_testing_map == {"react-004": ["jest"]}
    assert binding_map["react-004"].rule_verified_testing_map == {
        "react-004": ["jest"],
    }
    assert binding_map["react-004"].rule_projection_map == {"react-004": ["nextjs"]}
    assert binding_map["react-004"].rule_verified_projection_map == {
        "react-004": ["nextjs"],
    }

    assert binding_map["react-002"].rule_projection_map == {"react-002": ["nextjs"]}
    assert binding_map["react-002"].rule_verified_projection_map == {"react-002": []}


def test_nextjs_framework_mapping_authors_jest_and_nextjs_families() -> None:
    binding_map = _binding_map(NEXTJS_MAP)

    assert all(
        binding.rule_testing_map == {binding.rule_ids[0]: ["jest"]}
        for binding in NEXTJS_MAP.bindings
    )
    assert all(
        binding.rule_projection_map == {binding.rule_ids[0]: ["nextjs"]}
        for binding in NEXTJS_MAP.bindings
    )
    assert all(
        binding.rule_verified_projection_map == {binding.rule_ids[0]: ["nextjs"]}
        for binding in NEXTJS_MAP.bindings
    )
    assert binding_map["nextjs-001"].rule_verified_testing_map == {
        "nextjs-001": ["jest"],
    }


def test_angular_framework_mapping_authors_jest_and_angular_families() -> None:
    binding_map = _binding_map(ANGULAR_MAP)

    assert all(
        binding.rule_testing_map == {binding.rule_ids[0]: ["jest"]}
        for binding in ANGULAR_MAP.bindings
    )
    assert all(
        binding.rule_projection_map == {binding.rule_ids[0]: ["angular"]}
        for binding in ANGULAR_MAP.bindings
    )
    assert binding_map["angular-003"].rule_verified_testing_map == {
        "angular-003": ["jest"],
    }
    assert binding_map["angular-003"].rule_verified_projection_map == {
        "angular-003": ["angular"],
    }


def test_vue_framework_mapping_authors_jest_and_vue_families() -> None:
    binding_map = _binding_map(VUE_MAP)

    assert all(
        binding.rule_testing_map == {binding.rule_ids[0]: ["jest"]}
        for binding in VUE_MAP.bindings
    )
    assert all(
        binding.rule_projection_map == {binding.rule_ids[0]: ["vue"]}
        for binding in VUE_MAP.bindings
    )
    assert binding_map["vue-005"].rule_verified_testing_map == {"vue-005": ["jest"]}
    assert binding_map["vue-005"].rule_verified_projection_map == {"vue-005": ["vue"]}


def test_django_framework_mapping_authors_pytest_and_sql_families() -> None:
    binding_map = _binding_map(DJANGO_MAP)

    assert all(
        binding.rule_testing_map == {binding.rule_ids[0]: ["pytest"]}
        for binding in DJANGO_MAP.bindings
    )
    assert binding_map["django-001"].rule_projection_map == {"django-001": ["sql"]}
    assert binding_map["django-001"].rule_verified_projection_map == {
        "django-001": ["sql"],
    }
    assert binding_map["django-006"].rule_projection_map == {"django-006": ["sql"]}
    assert binding_map["django-006"].rule_verified_projection_map == {
        "django-006": [],
    }


def test_pydantic_framework_mapping_authors_pytest_and_schema_families() -> None:
    binding_map = _binding_map(PYDANTIC_MAP)

    assert all(
        binding.rule_testing_map == {binding.rule_ids[0]: ["pytest"]}
        for binding in PYDANTIC_MAP.bindings
    )
    assert binding_map["pydantic-004"].rule_projection_map == {
        "pydantic-004": ["jsonschema", "openapi"],
    }
    assert binding_map["pydantic-004"].rule_verified_projection_map == {
        "pydantic-004": ["jsonschema"],
    }
    assert binding_map["pydantic-007"].rule_projection_map == {
        "pydantic-007": ["jsonschema"],
    }
    assert binding_map["pydantic-007"].rule_verified_projection_map == {
        "pydantic-007": ["jsonschema"],
    }
    assert binding_map["pydantic-001"].rule_verified_projection_map == {
        "pydantic-001": [],
    }


def test_fastapi_framework_mapping_authors_pytest_and_openapi_families() -> None:
    binding_map = _binding_map(FASTAPI_MAP)

    assert all(
        binding.rule_testing_map == {binding.rule_ids[0]: ["pytest"]}
        for binding in FASTAPI_MAP.bindings
    )
    assert binding_map["fastapi-001"].rule_projection_map == {
        "fastapi-001": ["openapi"],
    }
    assert binding_map["fastapi-001"].rule_verified_projection_map == {
        "fastapi-001": ["openapi"],
    }
    assert binding_map["fastapi-003"].rule_projection_map == {
        "fastapi-003": ["openapi"],
    }
    assert binding_map["fastapi-003"].rule_verified_projection_map == {
        "fastapi-003": [],
    }


def test_sqlalchemy_framework_mapping_authors_pytest_and_sql_families() -> None:
    binding_map = _binding_map(SQLALCHEMY_MAP)

    assert all(
        binding.rule_testing_map == {binding.rule_ids[0]: ["pytest"]}
        for binding in SQLALCHEMY_MAP.bindings
    )
    assert binding_map["sqlalchemy-001"].rule_projection_map == {
        "sqlalchemy-001": ["sql"],
    }
    assert binding_map["sqlalchemy-001"].rule_verified_projection_map == {
        "sqlalchemy-001": ["sql"],
    }
    assert binding_map["sqlalchemy-005"].rule_projection_map == {
        "sqlalchemy-005": ["sql"],
    }
    assert binding_map["sqlalchemy-005"].rule_verified_projection_map == {
        "sqlalchemy-005": [],
    }


def test_framework_family_indexes_preserve_authored_verified_subsets() -> None:
    registry = _build_registry(
        REACT_MAP,
        NEXTJS_MAP,
        ANGULAR_MAP,
        VUE_MAP,
        DJANGO_MAP,
        PYDANTIC_MAP,
        FASTAPI_MAP,
        SQLALCHEMY_MAP,
    )

    assert registry.testing_ids_for("react-004", "react", "react-004") == ["jest"]
    assert registry.verified_projection_ids_for("react-002", "react", "react-002") == []
    assert registry.testing_ids_for("nextjs-001", "nextjs", "nextjs-001") == ["jest"]
    assert registry.projection_ids_for("nextjs-001", "nextjs", "nextjs-001") == [
        "nextjs",
    ]

    assert registry.testing_ids_for("angular-003", "angular", "angular-003") == [
        "jest",
    ]
    assert registry.verified_projection_ids_for(
        "angular-003",
        "angular",
        "angular-003",
    ) == ["angular"]

    assert registry.testing_ids_for("vue-005", "vue", "vue-005") == ["jest"]
    assert registry.projection_ids_for("vue-005", "vue", "vue-005") == ["vue"]

    assert registry.testing_ids_for("django-001", "django", "django-001") == ["pytest"]
    assert registry.projection_ids_for("django-001", "django", "django-001") == ["sql"]
    assert (
        registry.verified_projection_ids_for("django-006", "django", "django-006") == []
    )

    assert registry.projection_ids_for("pydantic-004", "pydantic", "pydantic-004") == [
        "jsonschema",
        "openapi",
    ]
    assert registry.verified_projection_ids_for(
        "pydantic-004",
        "pydantic",
        "pydantic-004",
    ) == ["jsonschema"]

    assert registry.projection_ids_for("fastapi-001", "fastapi", "fastapi-001") == [
        "openapi",
    ]
    assert (
        registry.verified_projection_ids_for(
            "fastapi-003",
            "fastapi",
            "fastapi-003",
        )
        == []
    )

    assert registry.testing_ids_for(
        "sqlalchemy-001", "sqlalchemy", "sqlalchemy-001"
    ) == [
        "pytest",
    ]
    assert registry.projection_ids_for(
        "sqlalchemy-001", "sqlalchemy", "sqlalchemy-001"
    ) == [
        "sql",
    ]
    assert (
        registry.verified_projection_ids_for(
            "sqlalchemy-005",
            "sqlalchemy",
            "sqlalchemy-005",
        )
        == []
    )
    assert [
        model.detector_id
        for model in registry.testing_models_for_family("pytest", "sqlalchemy")
    ] == [binding.detector_id for binding in SQLALCHEMY_MAP.bindings]
    assert [
        model.detector_id
        for model in registry.projection_models_for_family("sql", "sqlalchemy")
    ] == ["sqlalchemy-001", "sqlalchemy-005"]


def test_framework_family_rule_indexes_cover_authored_models() -> None:
    registry = _build_registry(
        REACT_MAP,
        NEXTJS_MAP,
        ANGULAR_MAP,
        VUE_MAP,
        DJANGO_MAP,
        PYDANTIC_MAP,
        FASTAPI_MAP,
        SQLALCHEMY_MAP,
    )

    assert [
        model.detector_id
        for model in registry.testing_models_for_rule("react-004", "react")
    ] == ["react-004"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_rule("react-004", "react")
    ] == ["react-004"]

    assert [
        model.detector_id
        for model in registry.testing_models_for_rule("nextjs-001", "nextjs")
    ] == ["nextjs-001"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_rule("nextjs-001", "nextjs")
    ] == ["nextjs-001"]

    assert [
        model.detector_id
        for model in registry.testing_models_for_rule("angular-003", "angular")
    ] == ["angular-003"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_rule("angular-003", "angular")
    ] == ["angular-003"]

    assert [
        model.detector_id
        for model in registry.testing_models_for_rule("django-001", "django")
    ] == ["django-001"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_rule("django-001", "django")
    ] == ["django-001"]

    assert [
        model.detector_id
        for model in registry.testing_models_for_rule("fastapi-001", "fastapi")
    ] == ["fastapi-001"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_rule("fastapi-001", "fastapi")
    ] == ["fastapi-001"]

    assert [
        model.detector_id
        for model in registry.testing_models_for_rule("sqlalchemy-001", "sqlalchemy")
    ] == ["sqlalchemy-001"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_rule("sqlalchemy-001", "sqlalchemy")
    ] == ["sqlalchemy-001"]
