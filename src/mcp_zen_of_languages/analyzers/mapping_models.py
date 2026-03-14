"""Pydantic models that bind zen rules to detector classes and their configs.

These models form the declarative bridge between the canonical rule
definitions in ``languages/*/rules.py`` and the detector implementations.
Each language's ``mapping.py`` module exports a
``LanguageDetectorMap`` containing [`RuleDetectorBinding`][RuleDetectorBinding] entries
that tell the registry:

* *which* ``ViolationDetector`` subclass enforces a set of rules,
* *which* ``DetectorConfig`` model carries its thresholds, and
* *which* explicit rule bounds (violation selectors + dogma ids) belong to that detector.

See Also:
    ``mcp_zen_of_languages.analyzers.registry`` — consumes these
    bindings during bootstrap.

    [`mcp_zen_of_languages.rules.base_models`][mcp_zen_of_languages.rules.base_models] — defines the
    [`ZenPrinciple`][ZenPrinciple] instances that bindings reference.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Literal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from mcp_zen_of_languages.analyzers.base import AnalyzerConfig  # noqa: TC001
from mcp_zen_of_languages.analyzers.base import ViolationDetector  # noqa: TC001
from mcp_zen_of_languages.languages.configs import DetectorConfig  # noqa: TC001


if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.registry import DetectorMetadata


class BaseBinding(BaseModel, ABC):
    """Shared detector binding contract for authored mapping entries.

    Concrete binding families provide the domain-specific metadata needed to
    turn an authored mapping entry into registry metadata.
    """

    detector_id: str
    detector_class: type[ViolationDetector]
    config_model: type[DetectorConfig | AnalyzerConfig]
    default_order: int = 0
    enabled_by_default: bool = True

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def rule_ids(self) -> list[str]:
        """Return the ordered rule ids covered by this binding, if any."""
        return []

    @property
    def rule_map(self) -> dict[str, list[str]]:
        """Return violation-selector coverage grouped by rule id, if any."""
        return {}

    @property
    def rule_dogma_map(self) -> dict[str, list[str]]:
        """Return explicit dogma ids grouped by rule id, if any."""
        return {}

    @abstractmethod
    def to_metadata(self, language: str) -> DetectorMetadata:
        """Project this binding into registry metadata for one language."""


class RuleBinding(BaseModel):
    """Explicit binding between one rule id and its dogma/violation bounds."""

    rule_id: str
    violation_selectors: list[str] = Field(default_factory=lambda: ["*"])
    dogma_ids: list[str] = Field(default_factory=list)

    def model_post_init(self, __context: object, /) -> None:
        """Default empty violation selectors to the wildcard selector."""
        if not self.violation_selectors:
            self.violation_selectors = ["*"]


class RuleDetectorBinding(BaseBinding):
    """Declares which detector class enforces one or more zen rules.

    Each binding is authored in a language's ``mapping.py`` and consumed by
    registry bootstrap during startup.

    Attributes:
        detector_id: Unique key that doubles as the ``type`` discriminator
            on the detector's config model.
        detector_class: Concrete
            [`ViolationDetector`][mcp_zen_of_languages.analyzers.base.ViolationDetector]
            subclass to instantiate in the pipeline.
        config_model: Pydantic model used to validate threshold values
            projected from zen principle metrics.
        rules: Explicit per-rule bounds for this detector. Each bound rule
            carries its own violation selectors and dogma ids.
        default_order: Pipeline execution order; lower values run first.
        enabled_by_default: If ``False``, the detector is excluded from
            the discriminated-union config adapter unless explicitly
            requested.
    """

    binding_kind: Literal["rule"] = "rule"
    rules: list[RuleBinding] = Field(min_length=1)

    @property
    def rule_ids(self) -> list[str]:
        """Return the ordered rule ids covered by this detector."""
        return [rule.rule_id for rule in self.rules]

    @property
    def rule_map(self) -> dict[str, list[str]]:
        """Return violation-selector coverage grouped by rule id."""
        return {rule.rule_id: list(rule.violation_selectors) for rule in self.rules}

    @property
    def rule_dogma_map(self) -> dict[str, list[str]]:
        """Return explicit dogma ids grouped by rule id."""
        return {rule.rule_id: list(rule.dogma_ids) for rule in self.rules}

    def to_metadata(self, language: str) -> DetectorMetadata:
        """Build registry metadata for a rule detector binding."""
        from mcp_zen_of_languages.analyzers.registry import DetectorMetadata

        return DetectorMetadata(
            detector_id=self.detector_id,
            detector_class=self.detector_class,
            config_model=self.config_model,
            language=language,
            rule_ids=list(self.rule_ids),
            rule_map=dict(self.rule_map),
            rule_dogma_map=dict(self.rule_dogma_map),
            default_order=self.default_order,
            enabled_by_default=self.enabled_by_default,
        )


class NonRuleDetectorBinding(BaseBinding):
    """Binding for generic detectors that do not map to explicit rules."""

    binding_kind: Literal["generic"] = "generic"

    def to_metadata(self, language: str) -> DetectorMetadata:
        """Build registry metadata for a non-rule detector binding."""
        from mcp_zen_of_languages.analyzers.registry import DetectorMetadata

        return DetectorMetadata(
            detector_id=self.detector_id,
            detector_class=self.detector_class,
            config_model=self.config_model,
            language=language,
            rule_ids=[],
            rule_map={},
            rule_dogma_map={},
            default_order=self.default_order,
            enabled_by_default=self.enabled_by_default,
        )


class LanguageDetectorMap(BaseModel):
    """All current detector bindings for one language, exported as ``DETECTOR_MAP``.

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
    bindings: list[BaseBinding] = Field(default_factory=list)

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


class DetectorGearbox:
    """Reusable binding interface for building language detector maps.

    Provides a light, chainable API so language mappings can share one
    construction pattern while still controlling exact binding metadata.
    """

    def __init__(self, language: str) -> None:
        """Initialize gearbox state for one language mapping."""
        self.language = language
        self._bindings: list[BaseBinding] = []

    def add(self, binding: BaseBinding) -> DetectorGearbox:
        """Add a pre-built detector binding."""
        self._bindings.append(binding)
        return self

    def extend(self, bindings: list[BaseBinding]) -> DetectorGearbox:
        """Add multiple pre-built detector bindings."""
        self._bindings.extend(bindings)
        return self

    def build_map(self) -> LanguageDetectorMap:
        """Build a language detector map from accumulated bindings."""
        return LanguageDetectorMap(
            language=self.language, bindings=list(self._bindings)
        )
