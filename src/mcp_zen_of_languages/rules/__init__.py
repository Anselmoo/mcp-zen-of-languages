"""Zen of Languages — Rules Package.

This package owns the ``ZEN_REGISTRY``, the in-memory mapping from language
keys (e.g. ``"python"``, ``"rust"``) to ``LanguageZenPrinciples`` models.
The registry is **lazy-loaded** on first access via ``_initialize_registry``
to avoid circular imports between rule definitions and analyzer code.

Public API:

* ``get_language_zen(language)`` — retrieve principles for one language.
* ``get_all_languages()`` — list every registered language key.
* ``get_principle_by_id(id)`` — cross-language principle lookup.
* ``get_all_principles_by_category(cat)`` — filter by ``PrincipleCategory``.
* ``get_all_critical_principles()`` — severity ≥ 9 across all languages.
* ``get_registry_stats()`` — ``RegistryStats`` Pydantic model.

Examples::

    from mcp_zen_of_languages.rules import ZEN_REGISTRY, get_language_zen

    python_zen = get_language_zen("python")
    all_languages = get_all_languages()
    critical = python_zen.get_by_severity(min_severity=9)
"""

# typing imports not required at module level
from .base_models import (
    AnalysisResult,
    LanguageSummary,
    LanguageZenPrinciples,
    PrincipleCategory,
    RegistryStats,
    SeverityLevel,
    ViolationReport,
    ZenPrinciple,
    get_missing_detector_rules,
    get_number_of_principles,
    get_number_of_priniciple,
    get_registry_detector_gaps,
    get_registry_rule_id_gaps,
    get_rule_id_coverage,
    get_rule_ids,
    get_total_principles,
)

# Central registry of all language zen principles (lazy-loaded to avoid circular imports)
ZEN_REGISTRY: dict[str, LanguageZenPrinciples] = {}


def _initialize_registry() -> None:
    """Populate ``ZEN_REGISTRY`` by importing each language's canonical rule module.

    Called lazily on the first ``get_*`` access.  Subsequent calls are
    no-ops because the guard ``if ZEN_REGISTRY`` short-circuits.
    """
    if ZEN_REGISTRY:
        return  # Already initialized

    # Language modules are canonical; use languages.* directly.
    from mcp_zen_of_languages.languages.bash.rules import BASH_ZEN
    from mcp_zen_of_languages.languages.cpp.rules import CPP_ZEN
    from mcp_zen_of_languages.languages.csharp.rules import CSHARP_ZEN
    from mcp_zen_of_languages.languages.css.rules import CSS_ZEN
    from mcp_zen_of_languages.languages.go.rules import GO_ZEN
    from mcp_zen_of_languages.languages.javascript.rules import JAVASCRIPT_ZEN
    from mcp_zen_of_languages.languages.json.rules import JSON_ZEN
    from mcp_zen_of_languages.languages.powershell.rules import POWERSHELL_ZEN
    from mcp_zen_of_languages.languages.python.rules import PYTHON_ZEN
    from mcp_zen_of_languages.languages.ruby.rules import RUBY_ZEN
    from mcp_zen_of_languages.languages.rust.rules import RUST_ZEN
    from mcp_zen_of_languages.languages.toml.rules import TOML_ZEN
    from mcp_zen_of_languages.languages.typescript.rules import TYPESCRIPT_ZEN
    from mcp_zen_of_languages.languages.xml.rules import XML_ZEN
    from mcp_zen_of_languages.languages.yaml.rules import YAML_ZEN

    ZEN_REGISTRY.update(
        {
            "python": PYTHON_ZEN,
            "javascript": JAVASCRIPT_ZEN,
            "typescript": TYPESCRIPT_ZEN,
            "ruby": RUBY_ZEN,
            "go": GO_ZEN,
            "json": JSON_ZEN,
            "rust": RUST_ZEN,
            "cpp": CPP_ZEN,
            "csharp": CSHARP_ZEN,
            "css": CSS_ZEN,
            "bash": BASH_ZEN,
            "powershell": POWERSHELL_ZEN,
            "yaml": YAML_ZEN,
            "toml": TOML_ZEN,
            "xml": XML_ZEN,
        },
    )


def get_language_zen(language: str) -> "LanguageZenPrinciples | None":
    """Retrieve the ``LanguageZenPrinciples`` for *language*, or ``None`` if unsupported.

    Args:
        language: Case-insensitive language key (e.g. ``"Python"`` → ``"python"``).

    Returns:
        The matching ``LanguageZenPrinciples``, or ``None``.
    """
    _initialize_registry()
    return ZEN_REGISTRY.get(language.lower())


def get_all_languages() -> list[str]:
    """Return every language key registered in ``ZEN_REGISTRY``.

    Returns:
        Sorted insertion-order list of language keys.
    """
    _initialize_registry()
    return list(ZEN_REGISTRY.keys())


def get_principle_by_id(principle_id: str) -> "ZenPrinciple | None":
    """Search all languages for a principle matching *principle_id*.

    Args:
        principle_id: Globally unique ID (e.g. ``"python-003"``).

    Returns:
        The matching ``ZenPrinciple``, or ``None`` if no language defines it.
    """
    _initialize_registry()
    for lang_zen in ZEN_REGISTRY.values():
        if principle := lang_zen.get_by_id(principle_id):
            return principle
    return None


def get_all_principles_by_category(
    category: PrincipleCategory,
) -> dict[str, list[ZenPrinciple]]:
    """Collect principles matching *category* across every registered language.

    Args:
        category: The ``PrincipleCategory`` to filter by.

    Returns:
        ``{language_key: [ZenPrinciple, …]}`` — languages with no matches
        are omitted.
    """
    _initialize_registry()
    result = {}
    for lang, lang_zen in ZEN_REGISTRY.items():
        if principles := lang_zen.get_by_category(category):
            result[lang] = principles
    return result


def get_all_critical_principles() -> dict[str, list[ZenPrinciple]]:
    """Collect principles with severity ≥ 9 across all languages.

    Returns:
        ``{language_key: [ZenPrinciple, …]}`` — languages with no critical
        principles are omitted.
    """
    _initialize_registry()
    result = {}
    for lang, lang_zen in ZEN_REGISTRY.items():
        if critical := lang_zen.get_by_severity(min_severity=9):
            result[lang] = critical
    return result


def get_registry_stats() -> "RegistryStats":
    """Snapshot the registry into a ``RegistryStats`` Pydantic model.

    Returns:
        Aggregated language counts, principle totals, and per-language
        summaries.
    """
    # Prefer returning a structured Pydantic model for better typing and
    # downstream validation/serialization benefits.
    _initialize_registry()
    return RegistryStats.from_registry(ZEN_REGISTRY)


from .coverage import (  # noqa: E402
    RuleConfigCoverageMap,
    RuleCoverageMap,
    build_all_explicit_rule_config_coverage,
    build_all_explicit_rule_coverage,
    build_all_rule_config_coverage,
    build_all_rule_coverage,
    build_explicit_rule_config_coverage,
    build_explicit_rule_coverage,
    build_rule_config_coverage,
    build_rule_coverage,
)

# Export all public symbols
__all__ = [
    # Registry
    "ZEN_REGISTRY",
    "AnalysisResult",
    "LanguageSummary",
    # Base models
    "LanguageZenPrinciples",
    "PrincipleCategory",
    "RegistryStats",
    "RuleConfigCoverageMap",
    "RuleCoverageMap",
    "SeverityLevel",
    "ViolationReport",
    "ZenPrinciple",
    "build_all_explicit_rule_config_coverage",
    "build_all_explicit_rule_coverage",
    "build_all_rule_config_coverage",
    "build_all_rule_coverage",
    "build_explicit_rule_config_coverage",
    "build_explicit_rule_coverage",
    "build_rule_config_coverage",
    "build_rule_coverage",
    "get_all_critical_principles",
    "get_all_languages",
    "get_all_principles_by_category",
    # Functions
    "get_language_zen",
    "get_missing_detector_rules",
    "get_number_of_principles",
    "get_number_of_priniciple",
    "get_principle_by_id",
    "get_registry_detector_gaps",
    "get_registry_rule_id_gaps",
    "get_registry_stats",
    "get_rule_id_coverage",
    "get_rule_ids",
    "get_total_principles",
]
