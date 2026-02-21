import pytest

from mcp_zen_of_languages import server


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("language", "code"),
    [
        ("python", "def foo():\n    return 1\n"),
        ("typescript", "const x: number = 1;"),
        ("javascript", "const x = 1;"),
        ("go", "package main\nfunc main() {}"),
        ("rust", "fn main() {}"),
        ("bash", "echo hello"),
        ("powershell", "Write-Output 'hello'"),
        ("ruby", "puts 'hello'"),
        ("cpp", "#include <iostream>\nint main() { return 0; }"),
        ("csharp", "class Program { static void Main() {} }"),
        ("css", ".btn { color: var(--text); }"),
        ("yaml", "name: value"),
        (
            "github-actions",
            "name: CI\non: push\njobs:\n  build:\n    runs-on: ubuntu-latest\n    timeout-minutes: 10\n    steps:\n      - run: echo hi\n        shell: bash",
        ),
        ("toml", "name = 'value'"),
        ("xml", "<root><item /></root>"),
        ("json", '{"name": "value"}'),
        ("sql", "SELECT * FROM users;"),
        ("markdown", "# Title\n\nSome text.\n"),
        ("latex", "\\documentclass{article}\n\\begin{document}Hello\\end{document}"),
        ("docker_compose", "services:\n  web:\n    image: nginx:latest\n"),
        ("dockerfile", "FROM ubuntu:latest\nUSER root\n"),
    ],
)
async def test_analyze_zen_violations_supported_languages(language: str, code: str):
    result = await server.analyze_zen_violations.fn(code, language)
    assert result.language == language
    assert result.metrics.lines_of_code >= 0
