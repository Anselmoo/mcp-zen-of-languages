"""Factory function for creating language-specific analyzers.

Centralises the mapping from language identifiers (including common aliases
like ``"py"``, ``"ts"``, ``"rs"``) to their concrete
[`BaseAnalyzer`][mcp_zen_of_languages.analyzers.base.BaseAnalyzer] subclass.
Callers never need to import individual analyzer modules; they go through
``create_analyzer`` and receive a fully configured instance.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_zen_of_languages.languages.bash.analyzer import BashAnalyzer
from mcp_zen_of_languages.languages.cpp.analyzer import CppAnalyzer
from mcp_zen_of_languages.languages.csharp.analyzer import CSharpAnalyzer
from mcp_zen_of_languages.languages.go.analyzer import GoAnalyzer
from mcp_zen_of_languages.languages.javascript.analyzer import JavaScriptAnalyzer
from mcp_zen_of_languages.languages.json.analyzer import JsonAnalyzer
from mcp_zen_of_languages.languages.powershell.analyzer import PowerShellAnalyzer
from mcp_zen_of_languages.languages.python.analyzer import PythonAnalyzer
from mcp_zen_of_languages.languages.ruby.analyzer import RubyAnalyzer
from mcp_zen_of_languages.languages.rust.analyzer import RustAnalyzer
from mcp_zen_of_languages.languages.toml.analyzer import TomlAnalyzer
from mcp_zen_of_languages.languages.typescript.analyzer import TypeScriptAnalyzer
from mcp_zen_of_languages.languages.xml.analyzer import XmlAnalyzer
from mcp_zen_of_languages.languages.yaml.analyzer import YamlAnalyzer

if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.base import AnalyzerConfig, BaseAnalyzer
    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig

    type AnalyzerClass = type[BaseAnalyzer]

SUPPORTED_LANGUAGES: tuple[str, ...] = (
    "python",
    "typescript",
    "javascript",
    "go",
    "rust",
    "bash",
    "powershell",
    "ruby",
    "cpp",
    "csharp",
    "yaml",
    "toml",
    "xml",
    "json",
)

_ANALYZERS_BY_ALIAS: dict[str, AnalyzerClass] = {
    "python": PythonAnalyzer,
    "py": PythonAnalyzer,
    "typescript": TypeScriptAnalyzer,
    "ts": TypeScriptAnalyzer,
    "tsx": TypeScriptAnalyzer,
    "javascript": JavaScriptAnalyzer,
    "js": JavaScriptAnalyzer,
    "jsx": JavaScriptAnalyzer,
    "go": GoAnalyzer,
    "rust": RustAnalyzer,
    "rs": RustAnalyzer,
    "bash": BashAnalyzer,
    "sh": BashAnalyzer,
    "shell": BashAnalyzer,
    "powershell": PowerShellAnalyzer,
    "ps": PowerShellAnalyzer,
    "pwsh": PowerShellAnalyzer,
    "ruby": RubyAnalyzer,
    "rb": RubyAnalyzer,
    "cpp": CppAnalyzer,
    "c++": CppAnalyzer,
    "cc": CppAnalyzer,
    "cxx": CppAnalyzer,
    "csharp": CSharpAnalyzer,
    "cs": CSharpAnalyzer,
    "yaml": YamlAnalyzer,
    "yml": YamlAnalyzer,
    "toml": TomlAnalyzer,
    "xml": XmlAnalyzer,
    "json": JsonAnalyzer,
}


def supported_languages() -> tuple[str, ...]:
    """Return canonical language identifiers accepted by ``create_analyzer``."""
    return SUPPORTED_LANGUAGES


def create_analyzer(
    language: str,
    config: AnalyzerConfig | None = None,
    pipeline_config: PipelineConfig | None = None,
) -> BaseAnalyzer:
    """Create a language-specific analyzer instance.

    Normalises *language* to lowercase and matches it against known
    identifiers and aliases.  The returned analyzer has its detection
    pipeline pre-built from zen rules, optionally overlaid with
    *pipeline_config* overrides from ``zen-config.yaml``.

    Args:
        language: Language name or alias (case-insensitive).  Common
            aliases are accepted — see the table below.
        config: Global analyzer thresholds; passed through to the
            analyzer's ``__init__``.
        pipeline_config: Optional detector-level overrides merged on
            top of the rule-derived pipeline.

    Returns:
        A configured [`BaseAnalyzer`][mcp_zen_of_languages.analyzers.base.BaseAnalyzer]
        subclass ready to call ``analyze``.

    Raises:
        ValueError: If *language* does not match any supported language.

    Note:
        **Supported languages and accepted aliases:**

        =============================== ===================================
        Language                        Accepted identifiers
        =============================== ===================================
        Python                          ``python``, ``py``
        TypeScript                      ``typescript``, ``ts``, ``tsx``
        JavaScript                      ``javascript``, ``js``, ``jsx``
        Go                              ``go``
        Rust                            ``rust``, ``rs``
        Bash                            ``bash``, ``sh``, ``shell``
        PowerShell                      ``powershell``, ``ps``, ``pwsh``
        Ruby                            ``ruby``, ``rb``
        C++                             ``cpp``, ``c++``, ``cc``, ``cxx``
        C#                              ``csharp``, ``cs``
        YAML                            ``yaml``, ``yml``
        TOML                            ``toml``
        XML                             ``xml``
        JSON                            ``json``
        =============================== ===================================
    """
    lang = language.lower()
    analyzer_class = _ANALYZERS_BY_ALIAS.get(lang)
    if analyzer_class is None:
        msg = f"Unsupported language: {language}"
        raise ValueError(msg)
    return analyzer_class(config=config, pipeline_config=pipeline_config)
