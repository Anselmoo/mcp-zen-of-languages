"""Rule-to-config projection and pipeline override merging.

Zen principles defined in ``languages/*/rules.py`` carry metric thresholds
(e.g. ``max_cyclomatic_complexity: 10``) but detectors need typed
[`DetectorConfig`][mcp_zen_of_languages.languages.configs.DetectorConfig] instances.
This module bridges the gap with two operations:

1. **Projection** — each principle's ``metrics`` dict is mapped onto the
   config fields of every detector registered for that rule, producing a
   typed config per detector.
2. **Override merging** — user-supplied ``zen-config.yaml`` pipeline
   entries are merged *over* the rule-derived defaults by matching on
   ``DetectorConfig.type``, so users can tighten or relax thresholds
   without modifying the canonical rule definitions.

See Also:
    ``mcp_zen_of_languages.analyzers.registry`` — performs the actual
    projection and merge logic that this module delegates to.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from pydantic import BaseModel, field_validator

from mcp_zen_of_languages.languages.configs import DetectorConfig  # noqa: TC001
from mcp_zen_of_languages.rules import get_language_zen

if TYPE_CHECKING:
    from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples

logger = logging.getLogger(__name__)
logger.setLevel(
    getattr(
        logging,
        os.environ.get("ZEN_LOG_LEVEL", "WARNING").upper(),
        logging.WARNING,
    ),
)


class PipelineConfig(BaseModel):
    """Typed container for the detector configs that drive a language pipeline.

    A ``PipelineConfig`` holds an ordered list of
    [`DetectorConfig`][mcp_zen_of_languages.languages.configs.DetectorConfig] instances
    ready for execution by
    [`DetectionPipeline`][mcp_zen_of_languages.analyzers.base.DetectionPipeline].
    Configs are either projected from zen principles via ``from_rules``
    or loaded from ``zen-config.yaml`` and validated through the registry's
    discriminated-union :pyclass:`TypeAdapter`.

    Attributes:
        language: ISO-style language identifier (e.g. ``"python"``,
            ``"typescript"``).
        detectors: Ordered detector configs; validated on assignment via
            ``_validate_detectors``.
    """

    language: str
    detectors: list[DetectorConfig]

    @field_validator("detectors", mode="before")
    @classmethod
    def _validate_detectors(cls, value: object) -> list[DetectorConfig]:
        """Coerce raw dicts into typed ``DetectorConfig`` subclasses.

        Each element is validated through the registry's discriminated-union
        [`TypeAdapter`][pydantic.TypeAdapter], which selects the concrete config
        model by inspecting the ``type`` discriminator field.

        Args:
            value: Raw list of dicts or config instances from YAML or
                programmatic construction.

        Returns:
            Typed detector config instances ready for pipeline execution.

        Raises:
            TypeError: If *value* is not a list.
        """
        if isinstance(value, list):
            from mcp_zen_of_languages.analyzers.registry import REGISTRY

            adapter = REGISTRY.adapter()
            return [adapter.validate_python(item) for item in value]
        msg = "detectors must be a list"
        raise TypeError(msg)

    @classmethod
    def from_rules(cls, language: str) -> PipelineConfig:
        """Build a complete pipeline by projecting a language's zen principles.

        Loads the [`LanguageZenPrinciples`][mcp_zen_of_languages.rules.base_models.LanguageZenPrinciples]
        for *language*, then delegates to
        ``configs_from_rules``
        to project each principle's metrics onto the matching detector configs.

        Args:
            language: Language key recognised by [`get_language_zen`][mcp_zen_of_languages.rules.get_language_zen]
                (e.g. ``"python"``).

        Returns:
            A fully populated ``PipelineConfig`` whose detector list reflects
            all zen principles defined for the language.

        Raises:
            ValueError: If no zen rules exist for *language*.

        Examples:
            >>> cfg = PipelineConfig.from_rules("python")
            >>> cfg.language
            'python'
        """
        lang_zen = get_language_zen(language)
        if not lang_zen:
            msg = f"No zen rules for language: {language}"
            raise ValueError(msg)
        from mcp_zen_of_languages.analyzers.registry import REGISTRY

        detectors = REGISTRY.configs_from_rules(lang_zen)
        return cls(language=language, detectors=detectors)


def project_rules_to_configs(lang_zen: LanguageZenPrinciples) -> list[DetectorConfig]:
    """Convert zen principle metric thresholds into typed detector configs.

    For every [`ZenPrinciple`][mcp_zen_of_languages.rules.base_models.ZenPrinciple]
    in *lang_zen*, the function resolves which detectors are registered for
    that rule and maps the principle's ``metrics`` dict onto each detector's
    config fields.  Keys that don't match any registered config field raise
    immediately so typos in rule definitions are caught at startup.

    Args:
        lang_zen: The complete set of zen principles for a single language,
            including metric thresholds and violation specs.

    Returns:
        Ordered detector configs with thresholds populated from the rules.

    See Also:
        ``DetectorRegistry.configs_from_rules``
        — the registry method this function delegates to.
    """
    from mcp_zen_of_languages.analyzers.registry import REGISTRY

    return REGISTRY.configs_from_rules(lang_zen)


def merge_pipeline_overrides(
    base: PipelineConfig,
    overrides: PipelineConfig | None,
) -> PipelineConfig:
    """Layer user overrides from ``zen-config.yaml`` onto rule-derived defaults.

    Override entries are matched to base entries by ``DetectorConfig.type``.
    When a match is found, only the fields explicitly set in the override are
    applied (via ``model_dump(exclude_unset=True)``), preserving every
    rule-derived default that the user didn't touch.  Overrides whose type
    doesn't appear in the base are appended as new detector entries.

    Args:
        base: Pipeline produced by ``PipelineConfig.from_rules`` with
            thresholds derived from canonical zen principles.
        overrides: Pipeline section from ``zen-config.yaml``, or ``None``
            to skip merging entirely.

    Returns:
        A new ``PipelineConfig`` containing the merged detector list.

    Raises:
        ValueError: If *overrides.language* doesn't match *base.language*.
    """
    if overrides is None:
        return base
    if overrides.language != base.language:
        msg = "Override pipeline language mismatch"
        raise ValueError(msg)
    from mcp_zen_of_languages.analyzers.registry import REGISTRY

    merged = REGISTRY.merge_configs(base.detectors, overrides.detectors)
    return PipelineConfig(language=base.language, detectors=merged)
