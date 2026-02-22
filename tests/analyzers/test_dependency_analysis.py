"""Tests for dependency analysis across all activated language analyzers."""

from __future__ import annotations

import pytest

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.bash.analyzer import BashAnalyzer
from mcp_zen_of_languages.languages.cpp.analyzer import CppAnalyzer
from mcp_zen_of_languages.languages.csharp.analyzer import CSharpAnalyzer
from mcp_zen_of_languages.languages.css.analyzer import CssAnalyzer
from mcp_zen_of_languages.languages.dockerfile.analyzer import DockerfileAnalyzer
from mcp_zen_of_languages.languages.go.analyzer import GoAnalyzer
from mcp_zen_of_languages.languages.javascript.analyzer import JavaScriptAnalyzer
from mcp_zen_of_languages.languages.powershell.analyzer import PowerShellAnalyzer
from mcp_zen_of_languages.languages.ruby.analyzer import RubyAnalyzer
from mcp_zen_of_languages.languages.rust.analyzer import RustAnalyzer
from mcp_zen_of_languages.languages.typescript.analyzer import TypeScriptAnalyzer
from mcp_zen_of_languages.models import DependencyAnalysis


def _ctx(code: str, lang: str, path: str = "test_file") -> AnalysisContext:
    return AnalysisContext(code=code, language=lang, path=path)


class TestJavaScriptDependencyAnalysis:
    def test_import_from(self) -> None:
        code = "import React from 'react';\nimport { useState } from 'react';"
        analyzer = JavaScriptAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "javascript"))
        assert isinstance(result, DependencyAnalysis)
        assert "react" in result.nodes

    def test_require(self) -> None:
        code = "const fs = require('fs');\nconst path = require('path');"
        analyzer = JavaScriptAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "javascript"))
        assert isinstance(result, DependencyAnalysis)
        assert "fs" in result.nodes
        assert "path" in result.nodes

    def test_no_imports_returns_none(self) -> None:
        analyzer = JavaScriptAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx("const x = 1;", "javascript"))
        assert result is None


class TestTypeScriptDependencyAnalysis:
    def test_import_type(self) -> None:
        code = "import type { Foo } from './types';\nimport { bar } from 'baz';"
        analyzer = TypeScriptAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "typescript"))
        assert isinstance(result, DependencyAnalysis)
        assert "./types" in result.nodes
        assert "baz" in result.nodes

    def test_no_imports_returns_none(self) -> None:
        analyzer = TypeScriptAnalyzer()
        result = analyzer._build_dependency_analysis(
            _ctx("const x: number = 1;", "typescript")
        )
        assert result is None


class TestGoDependencyAnalysis:
    def test_single_import(self) -> None:
        code = 'import "fmt"\n\nfunc main() {}'
        analyzer = GoAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "go"))
        assert isinstance(result, DependencyAnalysis)
        assert "fmt" in result.nodes

    def test_block_import(self) -> None:
        code = 'import (\n\t"fmt"\n\t"os"\n)\n'
        analyzer = GoAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "go"))
        assert isinstance(result, DependencyAnalysis)
        assert "fmt" in result.nodes
        assert "os" in result.nodes

    def test_no_imports_returns_none(self) -> None:
        analyzer = GoAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx("func main() {}", "go"))
        assert result is None


class TestRustDependencyAnalysis:
    def test_use_statement(self) -> None:
        code = "use std::io::Read;\nuse serde::Deserialize;"
        analyzer = RustAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "rust"))
        assert isinstance(result, DependencyAnalysis)
        assert "std::io::Read" in result.nodes

    def test_mod_statement(self) -> None:
        code = "mod utils;\nmod config;"
        analyzer = RustAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "rust"))
        assert isinstance(result, DependencyAnalysis)
        assert "utils" in result.nodes

    def test_extern_crate(self) -> None:
        code = "extern crate serde;"
        analyzer = RustAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "rust"))
        assert isinstance(result, DependencyAnalysis)
        assert "serde" in result.nodes

    def test_no_deps_returns_none(self) -> None:
        analyzer = RustAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx("fn main() {}", "rust"))
        assert result is None


class TestBashDependencyAnalysis:
    def test_source_directive(self) -> None:
        code = "#!/bin/bash\nsource ./lib.sh\n. /etc/profile"
        analyzer = BashAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "bash"))
        assert isinstance(result, DependencyAnalysis)
        assert "./lib.sh" in result.nodes
        assert "/etc/profile" in result.nodes

    def test_comments_skipped(self) -> None:
        code = "# source fake.sh\necho hello"
        analyzer = BashAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "bash"))
        assert result is None

    def test_no_sources_returns_none(self) -> None:
        analyzer = BashAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx("echo hello", "bash"))
        assert result is None


class TestRubyDependencyAnalysis:
    def test_require(self) -> None:
        code = "require 'json'\nrequire_relative 'helpers'"
        analyzer = RubyAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "ruby"))
        assert isinstance(result, DependencyAnalysis)
        assert "json" in result.nodes
        assert "helpers" in result.nodes

    def test_no_requires_returns_none(self) -> None:
        analyzer = RubyAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx("puts 'hello'", "ruby"))
        assert result is None


class TestCppDependencyAnalysis:
    def test_include_angle(self) -> None:
        code = "#include <vector>\n#include <string>"
        analyzer = CppAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "cpp"))
        assert isinstance(result, DependencyAnalysis)
        assert "vector" in result.nodes
        assert "string" in result.nodes

    def test_include_quote(self) -> None:
        code = '#include "my_header.h"'
        analyzer = CppAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "cpp"))
        assert isinstance(result, DependencyAnalysis)
        assert "my_header.h" in result.nodes

    def test_no_includes_returns_none(self) -> None:
        analyzer = CppAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx("int main() {}", "cpp"))
        assert result is None


class TestCSharpDependencyAnalysis:
    def test_using_directive(self) -> None:
        code = "using System;\nusing System.Linq;"
        analyzer = CSharpAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "csharp"))
        assert isinstance(result, DependencyAnalysis)
        assert "System" in result.nodes
        assert "System.Linq" in result.nodes

    def test_using_static(self) -> None:
        code = "using static System.Math;"
        analyzer = CSharpAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "csharp"))
        assert isinstance(result, DependencyAnalysis)
        assert "System.Math" in result.nodes

    def test_no_usings_returns_none(self) -> None:
        analyzer = CSharpAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx("class Foo {}", "csharp"))
        assert result is None


class TestCssDependencyAnalysis:
    def test_import(self) -> None:
        code = "@import 'reset.css';\n@import url('fonts.css');"
        analyzer = CssAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "css"))
        assert isinstance(result, DependencyAnalysis)
        assert "reset.css" in result.nodes
        assert "fonts.css" in result.nodes

    def test_no_imports_returns_none(self) -> None:
        analyzer = CssAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx("body { margin: 0; }", "css"))
        assert result is None


class TestDockerfileDependencyAnalysis:
    def test_from(self) -> None:
        code = "FROM python:3.12-slim\nRUN pip install flask"
        analyzer = DockerfileAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "dockerfile"))
        assert isinstance(result, DependencyAnalysis)
        assert "python:3.12-slim" in result.nodes

    def test_copy_from(self) -> None:
        code = "FROM builder AS build\nFROM python:3.12\nCOPY --from=build /app /app"
        analyzer = DockerfileAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "dockerfile"))
        assert isinstance(result, DependencyAnalysis)
        assert "build" in result.nodes

    def test_no_from_returns_none(self) -> None:
        analyzer = DockerfileAnalyzer()
        result = analyzer._build_dependency_analysis(
            _ctx("RUN echo hello", "dockerfile")
        )
        assert result is None


class TestPowerShellDependencyAnalysis:
    def test_import_module(self) -> None:
        code = "Import-Module ActiveDirectory\nImport-Module Az"
        analyzer = PowerShellAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "powershell"))
        assert isinstance(result, DependencyAnalysis)
        assert "ActiveDirectory" in result.nodes
        assert "Az" in result.nodes

    def test_dot_source(self) -> None:
        code = ". ./helpers.ps1"
        analyzer = PowerShellAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "powershell"))
        assert isinstance(result, DependencyAnalysis)
        assert "./helpers.ps1" in result.nodes

    def test_comments_skipped(self) -> None:
        code = "# Import-Module Fake\nWrite-Host 'hello'"
        analyzer = PowerShellAnalyzer()
        result = analyzer._build_dependency_analysis(_ctx(code, "powershell"))
        assert result is None

    def test_no_imports_returns_none(self) -> None:
        analyzer = PowerShellAnalyzer()
        result = analyzer._build_dependency_analysis(
            _ctx("Write-Host 'hello'", "powershell")
        )
        assert result is None


@pytest.mark.parametrize(
    "lang_cls",
    [
        JavaScriptAnalyzer,
        TypeScriptAnalyzer,
        GoAnalyzer,
        RustAnalyzer,
        BashAnalyzer,
        RubyAnalyzer,
        CppAnalyzer,
        CSharpAnalyzer,
        CssAnalyzer,
        DockerfileAnalyzer,
        PowerShellAnalyzer,
    ],
)
def test_all_declare_supports_dependency_analysis(lang_cls: type) -> None:
    analyzer = lang_cls()
    assert analyzer.capabilities().supports_dependency_analysis is True
