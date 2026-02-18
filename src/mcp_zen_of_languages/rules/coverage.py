"""Rule-to-detector coverage analysis.

Provides functions and Pydantic models that answer the question: *"Does every
zen principle have at least one detector that can enforce it?"*

Two granularity levels are supported:

* **Rule coverage** (``RuleCoverageMap``) — maps principle IDs to detector IDs.
* **Config coverage** (``RuleConfigCoverageMap``) — maps principle IDs to
  ``DetectorConfig`` classes, useful for verifying that the pipeline can
  build a valid config for every registered detector.

Each function comes in *inclusive* and *explicit* variants.  Inclusive
variants count the generic ``RulePatternDetector`` fallback; explicit
variants require a purpose-built detector and raise ``ValueError`` when
one is missing.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from mcp_zen_of_languages.languages.configs import DetectorConfig
from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector
from mcp_zen_of_languages.rules import get_all_languages, get_language_zen


class RuleCoverageMap(BaseModel):
    """Maps each principle ID to the detector IDs registered for it.

    Attributes:
        language: Lowercase language key (e.g. ``"python"``).
        rules: ``{principle_id: [detector_id, …]}`` — empty lists indicate
            uncovered principles.
    """

    language: str
    rules: dict[str, list[str]] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")

    def detector_counts(self) -> dict[str, int]:
        """Return the number of detectors backing each principle.

        Returns:
            ``{principle_id: count}`` — zero means the rule is uncovered.
        """
        return {rule_id: len(detectors) for rule_id, detectors in self.rules.items()}


class RuleConfigCoverageMap(BaseModel):
    """Maps each principle ID to the ``DetectorConfig`` subclasses that serve it.

    Attributes:
        language: Lowercase language key.
        rules: ``{principle_id: [ConfigClass, …]}`` — used to verify that
            every detector can be instantiated with a valid config model.
    """

    language: str
    rules: dict[str, list[type[DetectorConfig]]] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    def config_counts(self) -> dict[str, int]:
        """Return the number of distinct config classes per principle.

        Returns:
            ``{principle_id: count}`` — zero means no config class is bound.
        """
        return {rule_id: len(configs) for rule_id, configs in self.rules.items()}


def build_rule_coverage(language: str) -> RuleCoverageMap:
    """Build an inclusive rule-to-detector map for *language*.

    Includes ``RulePatternDetector`` fallback registrations alongside
    purpose-built detectors.

    Args:
        language: Lowercase language key (e.g. ``"python"``).

    Returns:
        A ``RuleCoverageMap`` covering every principle defined for *language*.

    Raises:
        ValueError: If *language* is not present in the registry.
    """
    from mcp_zen_of_languages.analyzers import registry_bootstrap  # noqa: F401
    from mcp_zen_of_languages.analyzers.registry import REGISTRY

    lang_zen = get_language_zen(language)
    if lang_zen is None:
        raise ValueError(f"Unknown language: {language}")
    rules: dict[str, list[str]] = {}
    for principle in lang_zen.principles:
        metas = REGISTRY.detectors_for_rule(principle.id, language)
        detector_ids = sorted({meta.detector_id for meta in metas})
        rules[principle.id] = detector_ids
    return RuleCoverageMap(language=language, rules=rules)


def build_explicit_rule_coverage(language: str) -> RuleCoverageMap:
    """Build a strict rule-to-detector map excluding ``RulePatternDetector`` fallbacks.

    Raises ``ValueError`` if any principle lacks a purpose-built detector.

    Args:
        language: Lowercase language key.

    Returns:
        A ``RuleCoverageMap`` containing only explicitly registered detectors.

    Raises:
        ValueError: If *language* is unknown or any principle is uncovered.
    """
    from mcp_zen_of_languages.analyzers import registry_bootstrap  # noqa: F401
    from mcp_zen_of_languages.analyzers.registry import REGISTRY

    lang_zen = get_language_zen(language)
    if lang_zen is None:
        raise ValueError(f"Unknown language: {language}")
    rules: dict[str, list[str]] = {}
    for principle in lang_zen.principles:
        metas = REGISTRY.detectors_for_rule(principle.id, language)
        if detector_ids := sorted(
            {
                meta.detector_id
                for meta in metas
                if meta.detector_class is not RulePatternDetector
            }
        ):
            rules[principle.id] = detector_ids
        else:
            raise ValueError(
                f"Explicit coverage missing for {language} rule {principle.id}"
            )
    return RuleCoverageMap(language=language, rules=rules)


def build_rule_config_coverage(language: str) -> RuleConfigCoverageMap:
    """Build an inclusive rule-to-config-class map for *language*.

    Args:
        language: Lowercase language key.

    Returns:
        A ``RuleConfigCoverageMap`` listing every ``DetectorConfig`` subclass
        serving each principle.

    Raises:
        ValueError: If *language* is not present in the registry.
    """
    from mcp_zen_of_languages.analyzers import registry_bootstrap  # noqa: F401
    from mcp_zen_of_languages.analyzers.registry import REGISTRY

    lang_zen = get_language_zen(language)
    if lang_zen is None:
        raise ValueError(f"Unknown language: {language}")
    rules: dict[str, list[type[DetectorConfig]]] = {}
    for principle in lang_zen.principles:
        metas = REGISTRY.detectors_for_rule(principle.id, language)
        ordered_metas = sorted(metas, key=lambda meta: meta.detector_id)
        configs: list[type[DetectorConfig]] = []
        seen: set[type[DetectorConfig]] = set()
        for meta in ordered_metas:
            config_model = meta.config_model
            if config_model in seen:
                continue
            seen.add(config_model)
            configs.append(config_model)
        rules[principle.id] = configs
    return RuleConfigCoverageMap(language=language, rules=rules)


def build_explicit_rule_config_coverage(language: str) -> RuleConfigCoverageMap:
    """Build a strict rule-to-config-class map excluding ``RulePatternDetector`` fallbacks.

    Raises ``ValueError`` if any principle lacks an explicit config class.

    Args:
        language: Lowercase language key.

    Returns:
        A ``RuleConfigCoverageMap`` containing only explicitly registered configs.

    Raises:
        ValueError: If *language* is unknown or any principle is uncovered.
    """
    from mcp_zen_of_languages.analyzers import registry_bootstrap  # noqa: F401
    from mcp_zen_of_languages.analyzers.registry import REGISTRY

    lang_zen = get_language_zen(language)
    if lang_zen is None:
        raise ValueError(f"Unknown language: {language}")
    rules: dict[str, list[type[DetectorConfig]]] = {}
    for principle in lang_zen.principles:
        metas = REGISTRY.detectors_for_rule(principle.id, language)
        ordered_metas = sorted(
            (meta for meta in metas if meta.detector_class is not RulePatternDetector),
            key=lambda meta: meta.detector_id,
        )
        configs: list[type[DetectorConfig]] = []
        seen: set[type[DetectorConfig]] = set()
        for meta in ordered_metas:
            config_model = meta.config_model
            if config_model in seen:
                continue
            seen.add(config_model)
            configs.append(config_model)
        if not configs:
            raise ValueError(
                f"Explicit config coverage missing for {language} rule {principle.id}"
            )
        rules[principle.id] = configs
    return RuleConfigCoverageMap(language=language, rules=rules)


def build_all_rule_coverage(
    languages: list[str] | None = None,
) -> list[RuleCoverageMap]:
    """Build inclusive rule coverage maps for all (or selected) languages.

    Args:
        languages: Restrict to these language keys.  ``None`` means all
            languages in the registry.

    Returns:
        One ``RuleCoverageMap`` per language.
    """
    langs = languages or get_all_languages()
    return [build_rule_coverage(lang) for lang in langs]


def build_all_explicit_rule_coverage(
    languages: list[str] | None = None,
) -> list[RuleCoverageMap]:
    """Build strict rule coverage maps (no fallback) for all (or selected) languages.

    Args:
        languages: Restrict to these language keys.  ``None`` means all.

    Returns:
        One ``RuleCoverageMap`` per language (raises on gaps).
    """
    langs = languages or get_all_languages()
    return [build_explicit_rule_coverage(lang) for lang in langs]


def build_all_rule_config_coverage(
    languages: list[str] | None = None,
) -> list[RuleConfigCoverageMap]:
    """Build inclusive config coverage maps for all (or selected) languages.

    Args:
        languages: Restrict to these language keys.  ``None`` means all.

    Returns:
        One ``RuleConfigCoverageMap`` per language.
    """
    langs = languages or get_all_languages()
    return [build_rule_config_coverage(lang) for lang in langs]


def build_all_explicit_rule_config_coverage(
    languages: list[str] | None = None,
) -> list[RuleConfigCoverageMap]:
    """Build strict config coverage maps (no fallback) for all (or selected) languages.

    Args:
        languages: Restrict to these language keys.  ``None`` means all.

    Returns:
        One ``RuleConfigCoverageMap`` per language (raises on gaps).
    """
    langs = languages or get_all_languages()
    return [build_explicit_rule_config_coverage(lang) for lang in langs]


__all__ = [
    "RuleConfigCoverageMap",
    "RuleCoverageMap",
    "build_all_explicit_rule_config_coverage",
    "build_all_explicit_rule_coverage",
    "build_all_rule_config_coverage",
    "build_all_rule_coverage",
    "build_explicit_rule_config_coverage",
    "build_explicit_rule_coverage",
    "build_rule_config_coverage",
    "build_rule_coverage",
]
