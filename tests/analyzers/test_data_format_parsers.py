"""Tests for data-format parse_code implementations (W1 analyzers)."""

from __future__ import annotations

import pytest

from mcp_zen_of_languages.languages.docker_compose.analyzer import DockerComposeAnalyzer
from mcp_zen_of_languages.languages.gitlab_ci.analyzer import GitLabCIAnalyzer
from mcp_zen_of_languages.languages.json.analyzer import JsonAnalyzer
from mcp_zen_of_languages.languages.toml.analyzer import TomlAnalyzer
from mcp_zen_of_languages.languages.xml.analyzer import XmlAnalyzer
from mcp_zen_of_languages.languages.yaml.analyzer import YamlAnalyzer
from mcp_zen_of_languages.models import ParserResult


class TestYamlParseCode:
    def test_valid_yaml(self) -> None:
        result = YamlAnalyzer().parse_code("key: value\nlist:\n  - a\n  - b")
        assert isinstance(result, ParserResult)
        assert result.type == "yaml"
        assert result.tree == {"key": "value", "list": ["a", "b"]}

    def test_invalid_yaml_returns_none(self) -> None:
        result = YamlAnalyzer().parse_code(":\n  :\n    - [invalid")
        assert result is None

    def test_capabilities(self) -> None:
        assert YamlAnalyzer().capabilities().supports_ast is True


class TestJsonParseCode:
    def test_valid_json(self) -> None:
        result = JsonAnalyzer().parse_code('{"key": "value", "num": 42}')
        assert isinstance(result, ParserResult)
        assert result.type == "json"
        assert result.tree == {"key": "value", "num": 42}

    def test_invalid_json_returns_none(self) -> None:
        result = JsonAnalyzer().parse_code("{not valid json")
        assert result is None

    def test_capabilities(self) -> None:
        assert JsonAnalyzer().capabilities().supports_ast is True


class TestTomlParseCode:
    def test_valid_toml(self) -> None:
        result = TomlAnalyzer().parse_code("[section]\nkey = 'value'")
        assert isinstance(result, ParserResult)
        assert result.type == "toml"
        assert result.tree == {"section": {"key": "value"}}

    def test_invalid_toml_returns_none(self) -> None:
        result = TomlAnalyzer().parse_code("[invalid\nkey = ")
        assert result is None

    def test_capabilities(self) -> None:
        assert TomlAnalyzer().capabilities().supports_ast is True


class TestXmlParseCode:
    def test_valid_xml(self) -> None:
        result = XmlAnalyzer().parse_code("<root><child>text</child></root>")
        assert isinstance(result, ParserResult)
        assert result.type == "xml"
        assert result.tree is not None

    def test_invalid_xml_returns_none(self) -> None:
        result = XmlAnalyzer().parse_code("<unclosed>")
        assert result is None

    def test_capabilities(self) -> None:
        assert XmlAnalyzer().capabilities().supports_ast is True


class TestDockerComposeParseCode:
    def test_valid_compose(self) -> None:
        code = "services:\n  web:\n    image: nginx"
        result = DockerComposeAnalyzer().parse_code(code)
        assert isinstance(result, ParserResult)
        assert result.type == "yaml"
        assert result.tree == {"services": {"web": {"image": "nginx"}}}

    def test_invalid_compose_returns_none(self) -> None:
        result = DockerComposeAnalyzer().parse_code(":\n  :\n    - [invalid")
        assert result is None

    def test_capabilities(self) -> None:
        assert DockerComposeAnalyzer().capabilities().supports_ast is True


class TestGitLabCIParseCode:
    def test_valid_gitlab_ci(self) -> None:
        code = "stages:\n  - build\n  - test"
        result = GitLabCIAnalyzer().parse_code(code)
        assert isinstance(result, ParserResult)
        assert result.type == "yaml"
        assert result.tree == {"stages": ["build", "test"]}

    def test_invalid_gitlab_ci_returns_none(self) -> None:
        result = GitLabCIAnalyzer().parse_code(":\n  :\n    - [invalid")
        assert result is None

    def test_capabilities(self) -> None:
        assert GitLabCIAnalyzer().capabilities().supports_ast is True


@pytest.mark.parametrize(
    ("analyzer_cls", "valid_input", "expected_type"),
    [
        (YamlAnalyzer, "key: value", "yaml"),
        (JsonAnalyzer, '{"k": 1}', "json"),
        (TomlAnalyzer, "k = 1", "toml"),
        (XmlAnalyzer, "<r/>", "xml"),
        (DockerComposeAnalyzer, "services: {}", "yaml"),
        (GitLabCIAnalyzer, "stages: []", "yaml"),
    ],
)
def test_all_data_format_parsers_return_parser_result(
    analyzer_cls: type,
    valid_input: str,
    expected_type: str,
) -> None:
    result = analyzer_cls().parse_code(valid_input)
    assert isinstance(result, ParserResult)
    assert result.type == expected_type
