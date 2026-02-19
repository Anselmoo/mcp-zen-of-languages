"""One-time bootstrap that populates the detector registry at import time.

When this module is first imported (triggered lazily by
[`adapter`][mcp_zen_of_languages.analyzers.registry.DetectorRegistry.adapter]),
it performs two passes:

1. **Mapping scan** — calls
   ``bootstrap_from_mappings``
   to discover hand-written detector bindings from ``languages/*/mapping.py``.
2. **Gap fill** — iterates every language's zen principles and registers a
   generic [`RulePatternDetector`][mcp_zen_of_languages.languages.rule_pattern.RulePatternDetector]
   for any rule that lacks a dedicated detector, dynamically generating a
   Pydantic config model via [`pydantic.create_model`][pydantic.create_model].

After this module finishes execution, the
:data:`~mcp_zen_of_languages.analyzers.registry.REGISTRY` is fully
populated and ready for projection and pipeline construction.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import create_model

from mcp_zen_of_languages.analyzers.registry import REGISTRY, DetectorMetadata
from mcp_zen_of_languages.languages.configs import RULE_CONFIGS, DetectorConfig
from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector
from mcp_zen_of_languages.rules import get_all_languages, get_language_zen

_RULE_CONFIG_FIELDS: dict[str, list[str]] = {
    "bash-006": ["max_script_length_without_functions"],
    "bash-011": ["min_variable_name_length"],
    "js-009": ["max_inheritance_depth"],
    "js-011": ["min_identifier_length"],
    "cs-008": ["public_naming", "private_naming"],
}

_RULE_FIELD_DEFAULTS: dict[str, tuple[object, object]] = {
    "max_script_length_without_functions": (int | None, None),
    "min_variable_name_length": (int | None, None),
    "max_inheritance_depth": (int | None, None),
    "min_identifier_length": (int | None, None),
    "public_naming": (str | None, None),
    "private_naming": (str | None, None),
}


def _rule_class_name(rule_id: str) -> str:
    """Derive a PascalCase config class name from a hyphenated rule ID.

    Args:
        rule_id: Hyphenated rule identifier (e.g. ``"bash-006"``).

    Returns:
        PascalCase name suffixed with ``Config`` (e.g. ``"Bash006Config"``).

    Examples:
        >>> _rule_class_name("js-009")
        'Js009Config'
    """
    parts = rule_id.replace("-", "_").split("_")
    return "".join(part.capitalize() for part in parts) + "Config"


def _rule_literal(rule_id: str) -> object:
    """Create a ``Literal["<rule_id>"]`` type for use as a Pydantic discriminator.

    The returned type is assigned to the ``type`` field of dynamically
    generated config models so Pydantic's discriminated union can route
    raw dicts to the correct model class.

    Args:
        rule_id: Rule identifier to embed as a literal value.

    Returns:
        A ``Literal`` type containing exactly *rule_id*.
    """
    return Literal[rule_id]


def _build_rule_configs(rule_ids: list[str]) -> dict[str, type[DetectorConfig]]:
    """Generate or look up Pydantic config models for rules without hand-written detectors.

    For each rule ID, the function first checks :data:`RULE_CONFIGS` for a
    pre-existing config class.  If none is found, it dynamically creates one
    via [`pydantic.create_model`][pydantic.create_model], adding any rule-specific fields
    declared in :data:`_RULE_CONFIG_FIELDS` and defaulting to the types in
    :data:`_RULE_FIELD_DEFAULTS`.

    Args:
        rule_ids: Rules that need config models — typically those
            identified as having no registered detector after the
            mapping scan.

    Returns:
        Mapping from rule ID to its config model class, ready for
        [`register`][mcp_zen_of_languages.analyzers.registry.DetectorRegistry.register].
    """
    configs: dict[str, type[DetectorConfig]] = {}
    for rule_id in rule_ids:
        if rule_id in RULE_CONFIGS:
            configs[rule_id] = RULE_CONFIGS[rule_id]
            continue
        field_names = _RULE_CONFIG_FIELDS.get(rule_id, [])
        fields: dict[str, tuple[object, object]] = {
            name: _RULE_FIELD_DEFAULTS[name] for name in field_names
        }
        field_definitions: dict[str, Any] = {
            "type": (_rule_literal(rule_id), rule_id),
            **fields,
        }
        configs[rule_id] = create_model(
            _rule_class_name(rule_id),
            __base__=DetectorConfig,
            **field_definitions,
        )  # type: ignore[no-matching-overload]
    return configs


if not REGISTRY.items():
    REGISTRY.bootstrap_from_mappings()

    rules_to_register: dict[str, list[str]] = {}
    for language in get_all_languages():
        lang_zen = get_language_zen(language)
        if not lang_zen:
            continue
        if missing := [
            principle.id
            for principle in lang_zen.principles
            if not REGISTRY.detectors_for_rule(principle.id, language)
        ]:
            rules_to_register[language] = missing

    rule_configs = _build_rule_configs(
        [rule_id for ids in rules_to_register.values() for rule_id in ids],
    )
    for language, rule_ids in rules_to_register.items():
        for rule_id in rule_ids:
            REGISTRY.register(
                DetectorMetadata(
                    detector_id=rule_id,
                    detector_class=RulePatternDetector,
                    config_model=rule_configs[rule_id],
                    language=language,
                    rule_ids=[rule_id],
                    default_order=900,
                ),
            )
