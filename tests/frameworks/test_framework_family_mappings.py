from __future__ import annotations

from mcp_zen_of_languages.analyzers.registry import DetectorRegistry
from mcp_zen_of_languages.frameworks.django.mapping import DETECTOR_MAP as DJANGO_MAP
from mcp_zen_of_languages.frameworks.fastapi.mapping import DETECTOR_MAP as FASTAPI_MAP
from mcp_zen_of_languages.frameworks.pydantic.mapping import (
    DETECTOR_MAP as PYDANTIC_MAP,
)
from mcp_zen_of_languages.frameworks.react.mapping import DETECTOR_MAP as REACT_MAP


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


def test_framework_family_indexes_preserve_authored_verified_subsets() -> None:
    registry = _build_registry(REACT_MAP, DJANGO_MAP, PYDANTIC_MAP, FASTAPI_MAP)

    assert registry.testing_ids_for("react-004", "react", "react-004") == ["jest"]
    assert registry.verified_projection_ids_for("react-002", "react", "react-002") == []

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
