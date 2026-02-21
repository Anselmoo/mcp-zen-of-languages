from __future__ import annotations

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer


def test_create_analyzer_types():
    python = create_analyzer("python")
    assert python.language() == "python"
    rust = create_analyzer("rust")
    assert rust.language() == "rust"
    json = create_analyzer("json")
    assert json.language() == "json"
    xml = create_analyzer("xml")
    assert xml.language() == "xml"
    gha = create_analyzer("github-actions")
    assert gha.language() == "github-actions"
    css = create_analyzer("css")
    assert css.language() == "css"
    scss = create_analyzer("scss")
    assert scss.language() == "css"
    docker_compose = create_analyzer("docker-compose")
    assert docker_compose.language() == "docker_compose"
    dockerfile = create_analyzer("dockerfile")
    assert dockerfile.language() == "dockerfile"
    sql = create_analyzer("sql")
    assert sql.language() == "sql"
    postgres = create_analyzer("postgresql")
    assert postgres.language() == "sql"
    markdown = create_analyzer("markdown")
    assert markdown.language() == "markdown"
    mdx = create_analyzer("mdx")
    assert mdx.language() == "markdown"
    latex = create_analyzer("latex")
    assert latex.language() == "latex"
    tex = create_analyzer("tex")
    assert tex.language() == "latex"
