"""Pydantic models that bind zen rules to detector classes and their configs.

These models form the declarative bridge between the canonical rule
definitions in ``languages/*/rules.py`` and the detector implementations.
Each language's ``mapping.py`` module exports a
``LanguageDetectorMap`` containing [`DetectorBinding`][DetectorBinding] entries
that tell the registry:

* *which* ``ViolationDetector`` subclass enforces a set of rules,
* *which* ``DetectorConfig`` model carries its thresholds, and
* *how completely* it covers the rules (via [`DetectorBinding.coverage`][DetectorBinding.coverage]).

See Also:
    ``mcp_zen_of_languages.analyzers.registry`` — consumes these
    bindings during bootstrap.

    [`mcp_zen_of_languages.rules.base_models`][mcp_zen_of_languages.rules.base_models] — defines the
    [`ZenPrinciple`][ZenPrinciple] instances that bindings reference.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from mcp_zen_of_languages.analyzers.base import AnalyzerConfig, ViolationDetector
from mcp_zen_of_languages.languages.configs import DetectorConfig

CoverageLevel = Literal["partial", "full-shallow", "full", "1:1"]


class DetectorBinding(BaseModel):
    """Declares which detector class enforces a set of zen rules and how.

    Each binding is authored in a language's ``mapping.py`` and consumed by
    ``DetectorMetadata.from_binding``
    during registry bootstrap.

    Attributes:
        detector_id: Unique key that doubles as the ``type`` discriminator
            on the detector's config model.
        detector_class: Concrete
            [`ViolationDetector`][mcp_zen_of_languages.analyzers.base.ViolationDetector]
            subclass to instantiate in the pipeline.
        config_model: Pydantic model used to validate threshold values
            projected from zen principle metrics.
        rule_ids: Zen rule identifiers this detector can evaluate.
        rule_map: Per-rule mapping to violation-spec indices; ``["*"]``
            means the detector covers all specs for that rule.
        coverage: Self-reported completeness level — ``"1:1"`` for
            detectors that fully cover every violation spec, down to
            ``"partial"`` for heuristic checks.
        default_order: Pipeline execution order; lower values run first.
        enabled_by_default: If ``False``, the detector is excluded from
            the discriminated-union config adapter unless explicitly
            requested.
    """

    detector_id: str
    detector_class: type[ViolationDetector]
    config_model: type[DetectorConfig] | type[AnalyzerConfig]
    rule_ids: list[str] = Field(default_factory=list)
    rule_map: dict[str, list[str]] = Field(default_factory=dict)
    coverage: CoverageLevel = "partial"
    default_order: int = 0
    enabled_by_default: bool = True

    model_config = ConfigDict(arbitrary_types_allowed=True)


class LanguageDetectorMap(BaseModel):
    """All detector bindings for one language, exported as ``DETECTOR_MAP``.

    Each language's ``mapping.py`` module constructs a single instance of
    this model and assigns it to the module-level ``DETECTOR_MAP`` constant,
    which ``DetectorRegistry.bootstrap_from_mappings``
    reads during startup.

    Attributes:
        language: Language identifier matching
            ``language``.
        bindings: Ordered list of detector bindings for this language.
    """

    language: str
    bindings: list[DetectorBinding] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class FullDetectorMap(BaseModel):
    """Aggregate view of detector bindings across every supported language.

    Primarily useful for tooling and introspection; the registry itself
    iterates individual ``LanguageDetectorMap`` instances during bootstrap.

    Attributes:
        languages: Mapping from language identifier to its
            ``LanguageDetectorMap``.
    """

    languages: dict[str, LanguageDetectorMap] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)
