from __future__ import annotations

import importlib

from mcp_zen_of_languages.analyzers.registry import REGISTRY
from mcp_zen_of_languages.languages.bash.rules import BASH_ZEN
from mcp_zen_of_languages.languages.cpp.rules import CPP_ZEN
from mcp_zen_of_languages.languages.csharp.rules import CSHARP_ZEN
from mcp_zen_of_languages.languages.go.rules import GO_ZEN
from mcp_zen_of_languages.languages.javascript.rules import JAVASCRIPT_ZEN
from mcp_zen_of_languages.languages.powershell.rules import POWERSHELL_ZEN
from mcp_zen_of_languages.languages.ruby.rules import RUBY_ZEN
from mcp_zen_of_languages.languages.rust.rules import RUST_ZEN
from mcp_zen_of_languages.languages.typescript.rules import TYPESCRIPT_ZEN


def test_all_rules_have_detectors():
    importlib.import_module("mcp_zen_of_languages.analyzers.registry_bootstrap")

    rules_by_language = {
        "bash": BASH_ZEN,
        "cpp": CPP_ZEN,
        "csharp": CSHARP_ZEN,
        "go": GO_ZEN,
        "javascript": JAVASCRIPT_ZEN,
        "powershell": POWERSHELL_ZEN,
        "ruby": RUBY_ZEN,
        "rust": RUST_ZEN,
        "typescript": TYPESCRIPT_ZEN,
    }
    for language, ruleset in rules_by_language.items():
        for principle in ruleset.principles:
            metas = REGISTRY.detectors_for_rule(principle.id, language)
            assert metas, f"Missing detector for {language} {principle.id}"
