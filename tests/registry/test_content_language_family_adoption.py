from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_zen_of_languages.analyzers.registry import DetectorRegistry
from mcp_zen_of_languages.languages.css.mapping import DETECTOR_MAP as CSS_MAP
from mcp_zen_of_languages.languages.json.mapping import DETECTOR_MAP as JSON_MAP
from mcp_zen_of_languages.languages.latex.mapping import DETECTOR_MAP as LATEX_MAP
from mcp_zen_of_languages.languages.markdown.mapping import DETECTOR_MAP as MARKDOWN_MAP
from mcp_zen_of_languages.languages.svg.mapping import DETECTOR_MAP as SVG_MAP
from mcp_zen_of_languages.languages.toml.mapping import DETECTOR_MAP as TOML_MAP
from mcp_zen_of_languages.languages.xml.mapping import DETECTOR_MAP as XML_MAP


if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding


def _binding_map(detector_map) -> dict[str, RuleDetectorBinding]:
    return {binding.detector_id: binding for binding in detector_map.bindings}


def _build_registry(*detector_maps) -> DetectorRegistry:
    registry = DetectorRegistry()
    for detector_map in detector_maps:
        for binding in detector_map.bindings:
            bundle = binding.build_bundle(detector_map.language)
            registry.register(bundle.require_rule_model(), bundle=bundle)
    return registry


def test_content_language_bindings_author_testing_and_projection_families() -> None:
    json_bindings = _binding_map(JSON_MAP)
    xml_bindings = _binding_map(XML_MAP)
    toml_bindings = _binding_map(TOML_MAP)
    markdown_bindings = _binding_map(MARKDOWN_MAP)
    css_bindings = _binding_map(CSS_MAP)
    svg_bindings = _binding_map(SVG_MAP)
    latex_bindings = _binding_map(LATEX_MAP)

    assert json_bindings["json-002"].rule_testing_map == {"json-002": ["jsonschema"]}
    assert json_bindings["json-002"].rule_verified_testing_map == {
        "json-002": ["jsonschema"],
    }
    assert json_bindings["json-002"].rule_projection_map == {
        "json-002": ["jsonschema", "openapi"],
    }
    assert json_bindings["json-002"].rule_verified_projection_map == {
        "json-002": ["jsonschema"],
    }
    assert json_bindings["json-008"].rule_projection_map == {
        "json-008": ["jsonschema", "openapi"],
    }
    assert json_bindings["json-009"].rule_verified_projection_map == {
        "json-009": ["jsonschema"],
    }

    assert xml_bindings["xml-003"].rule_testing_map == {"xml-003": ["xmllint"]}
    assert xml_bindings["xml-003"].rule_verified_testing_map == {
        "xml-003": ["xmllint"],
    }
    assert xml_bindings["xml-003"].rule_projection_map == {"xml-003": ["svg"]}
    assert xml_bindings["xml-004"].rule_verified_projection_map == {
        "xml-004": ["svg"],
    }

    assert toml_bindings["toml-002"].rule_projection_map == {"toml-002": ["python"]}
    assert toml_bindings["toml-002"].rule_verified_projection_map == {
        "toml-002": ["python"],
    }
    assert toml_bindings["toml-007"].rule_projection_map == {"toml-007": ["python"]}
    assert toml_bindings["toml-008"].rule_verified_projection_map == {
        "toml-008": ["python"],
    }

    assert markdown_bindings["md-001"].rule_testing_map == {"md-001": ["markdownlint"]}
    assert markdown_bindings["md-001"].rule_verified_testing_map == {
        "md-001": ["markdownlint"],
    }
    assert markdown_bindings["md-005"].rule_projection_map == {
        "md-005": ["react", "nextjs"],
    }
    assert markdown_bindings["md-005"].rule_verified_projection_map == {
        "md-005": ["nextjs"],
    }
    assert markdown_bindings["md-007"].rule_projection_map == {
        "md-007": ["react", "nextjs"],
    }

    assert css_bindings["css-001"].rule_testing_map == {"css-001": ["stylelint"]}
    assert css_bindings["css-001"].rule_verified_testing_map == {
        "css-001": ["stylelint"],
    }
    assert css_bindings["css-001"].rule_projection_map == {
        "css-001": ["react", "nextjs", "vue"],
    }
    assert css_bindings["css-001"].rule_verified_projection_map == {
        "css-001": ["nextjs"],
    }
    assert css_bindings["css-005"].rule_projection_map == {
        "css-005": ["react", "nextjs", "vue"],
    }

    assert svg_bindings["svg-005"].rule_projection_map == {
        "svg-005": ["react", "nextjs", "vue"],
    }
    assert svg_bindings["svg-005"].rule_verified_projection_map == {
        "svg-005": ["react"],
    }
    assert svg_bindings["svg-012"].rule_testing_map == {"svg-012": ["xmllint"]}
    assert svg_bindings["svg-012"].rule_verified_testing_map == {
        "svg-012": ["xmllint"],
    }
    assert svg_bindings["svg-012"].rule_verified_projection_map == {
        "svg-012": ["react", "nextjs"],
    }

    assert latex_bindings["latex-002"].rule_testing_map == {"latex-002": ["chktex"]}
    assert latex_bindings["latex-002"].rule_verified_testing_map == {
        "latex-002": ["chktex"],
    }
    assert latex_bindings["latex-002"].rule_projection_map == {"latex-002": ["pdf"]}
    assert latex_bindings["latex-004"].rule_verified_projection_map == {
        "latex-004": ["pdf"],
    }
    assert latex_bindings["latex-008"].rule_verified_projection_map == {
        "latex-008": ["pdf"],
    }


def test_registry_resolves_content_language_family_lookups() -> None:
    registry = _build_registry(
        JSON_MAP,
        XML_MAP,
        TOML_MAP,
        MARKDOWN_MAP,
        CSS_MAP,
        SVG_MAP,
        LATEX_MAP,
    )

    assert registry.testing_ids_for("json-002", "json", "json-002") == ["jsonschema"]
    assert registry.verified_projection_ids_for("json-002", "json", "json-002") == [
        "jsonschema",
    ]
    assert registry.projection_ids_for("json-008", "json", "json-008") == [
        "jsonschema",
        "openapi",
    ]

    assert registry.testing_ids_for("xml-004", "xml", "xml-004") == ["xmllint"]
    assert registry.verified_projection_ids_for("xml-004", "xml", "xml-004") == [
        "svg",
    ]

    assert registry.projection_ids_for("toml-007", "toml", "toml-007") == ["python"]
    assert registry.verified_projection_ids_for("toml-008", "toml", "toml-008") == [
        "python",
    ]

    assert registry.testing_ids_for("md-004", "markdown", "md-004") == ["markdownlint"]
    assert registry.projection_ids_for("md-006", "markdown", "md-006") == [
        "react",
        "nextjs",
    ]
    assert registry.verified_projection_ids_for("md-006", "markdown", "md-006") == [
        "nextjs",
    ]

    assert registry.testing_ids_for("css-005", "css", "css-005") == ["stylelint"]
    assert registry.projection_ids_for("css-001", "css", "css-001") == [
        "react",
        "nextjs",
        "vue",
    ]
    assert registry.verified_projection_ids_for("css-005", "css", "css-005") == [
        "nextjs",
    ]

    assert registry.projection_ids_for("svg-012", "svg", "svg-012") == [
        "react",
        "nextjs",
        "vue",
    ]
    assert registry.verified_projection_ids_for("svg-012", "svg", "svg-012") == [
        "react",
        "nextjs",
    ]
    assert registry.projection_ids_for("svg-005", "svg", "svg-005") == [
        "react",
        "nextjs",
        "vue",
    ]

    assert registry.testing_ids_for("latex-002", "latex", "latex-002") == ["chktex"]
    assert registry.verified_projection_ids_for("latex-008", "latex", "latex-008") == [
        "pdf",
    ]

    assert [
        model.detector_id
        for model in registry.testing_models_for_family("markdownlint", "markdown")
    ] == ["md-001", "md-002", "md-003", "md-004"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_family("nextjs", "markdown")
    ] == ["md-005", "md-006", "md-007"]
    assert [
        model.detector_id
        for model in registry.testing_models_for_family("stylelint", "css")
    ] == ["css-001", "css-005"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_family("python", "toml")
    ] == ["toml-002", "toml-007", "toml-008"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_family("jsonschema", "json")
    ] == ["json-002", "json-008", "json-009"]
