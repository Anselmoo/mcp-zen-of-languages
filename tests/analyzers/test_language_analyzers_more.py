from __future__ import annotations

from mcp_zen_of_languages.languages.python.analyzer import PythonAnalyzer

EXPECTED_IMPORT_LINES = 2


def test_python_analyzer_dependency_analysis(tmp_path):
    analyzer = PythonAnalyzer()
    code = "import os\nimport sys\n"
    result = analyzer.analyze(code, path=str(tmp_path / "sample.py"))
    assert result.metrics.lines_of_code == EXPECTED_IMPORT_LINES


def test_python_analyzer_handles_repository_imports(tmp_path):
    analyzer = PythonAnalyzer()
    repo_imports = {str(tmp_path / "sample.py"): ["os"]}
    result = analyzer.analyze(
        "import os\n",
        path=str(tmp_path / "sample.py"),
        repository_imports=repo_imports,
    )
    assert result.metrics.lines_of_code == 1
