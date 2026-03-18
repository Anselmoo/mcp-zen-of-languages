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
from typing import Literal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from mcp_zen_of_languages.analyzers.base import AnalyzerConfig  # noqa: TC001
from mcp_zen_of_languages.analyzers.base import ViolationDetector  # noqa: TC001
from mcp_zen_of_languages.analyzers.registry import DetectorMetadata  # noqa: TC001
from mcp_zen_of_languages.languages.configs import DetectorConfig  # noqa: TC001


def _normalize_family_rule_maps(
    family_ids: list[str],
    family_rule_map: dict[str, list[str]],
    family_verified_rule_map: dict[str, list[str]],
) -> tuple[list[str], dict[str, list[str]], dict[str, list[str]]]:
    """Normalize family ids and rule maps while preserving authored order."""
    ordered_family_ids = list(
        dict.fromkeys(
            [
                *family_ids,
                *family_rule_map.keys(),
                *family_verified_rule_map.keys(),
            ],
        ),
    )
    if not ordered_family_ids:
        return [], {}, {}

    normalized_rule_map = {
        family_id: list(dict.fromkeys(family_rule_map.get(family_id, [])))
        for family_id in ordered_family_ids
    }
    normalized_verified_rule_map = {
        family_id: list(dict.fromkeys(family_verified_rule_map.get(family_id, [])))
        for family_id in ordered_family_ids
    }
    return (
        ordered_family_ids,
        normalized_rule_map,
        normalized_verified_rule_map,
    )


def _rule_ids_for_family(
    family_rule_map: dict[str, list[str]],
    family_id: str | None,
) -> list[str]:
    """Return rule ids bound to one authored family id."""
    if family_id and family_id in family_rule_map:
        return list(family_rule_map[family_id])
    if len(family_rule_map) == 1:
        return list(next(iter(family_rule_map.values())))
    return []


def _family_ids_for_rule(
    family_ids: list[str],
    family_rule_map: dict[str, list[str]],
    rule_id: str | None,
) -> list[str]:
    """Return authored family ids bound to one rule id."""
    if rule_id is None:
        return []
    return [
        family_id
        for family_id in family_ids
        if rule_id in family_rule_map.get(family_id, [])
    ]


class DogmaPerspectiveModel(BaseModel):
    """Dogma-perspective metadata authored by one detector binding.

    This model preserves explicit rule-to-dogma assignments separately from the
    rule runtime metadata so future dogma-only pipelines can evolve without
    overloading [`DetectorMetadata`][mcp_zen_of_languages.analyzers.registry.DetectorMetadata].
    """

    detector_id: str
    language: str
    dogma_ids: list[str] = Field(default_factory=list)
    dogma_rule_map: dict[str, list[str]] = Field(default_factory=dict)
    dogma_verified_rule_map: dict[str, list[str]] = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True)

    def model_post_init(self, __context: object, /) -> None:
        """Ensure authored dogma maps and ids remain mutually consistent."""
        ordered_dogma_ids, dogma_rule_map, dogma_verified_rule_map = (
            _normalize_family_rule_maps(
                self.dogma_ids,
                self.dogma_rule_map,
                self.dogma_verified_rule_map,
            )
        )
        if not ordered_dogma_ids:
            return

        object.__setattr__(self, "dogma_ids", ordered_dogma_ids)
        object.__setattr__(self, "dogma_rule_map", dogma_rule_map)
        object.__setattr__(self, "dogma_verified_rule_map", dogma_verified_rule_map)

    def rule_ids_for_dogma(self, dogma_id: str | None) -> list[str]:
        """Return rule ids bound to one dogma."""
        return _rule_ids_for_family(self.dogma_rule_map, dogma_id)

    def verified_rule_ids_for_dogma(self, dogma_id: str | None) -> list[str]:
        """Return verified rule ids bound to one dogma."""
        return _rule_ids_for_family(self.dogma_verified_rule_map, dogma_id)

    def dogma_ids_for_rule(self, rule_id: str | None) -> list[str]:
        """Return explicit dogma ids bound to one rule."""
        return _family_ids_for_rule(self.dogma_ids, self.dogma_rule_map, rule_id)

    def verified_dogma_ids_for_rule(self, rule_id: str | None) -> list[str]:
        """Return explicit verified dogma ids bound to one rule."""
        return _family_ids_for_rule(
            self.dogma_ids,
            self.dogma_verified_rule_map,
            rule_id,
        )


class TestingPerspectiveModel(BaseModel):
    """Testing-family metadata authored by one detector binding."""

    __test__ = False

    detector_id: str
    language: str
    testing_ids: list[str] = Field(default_factory=list)
    testing_rule_map: dict[str, list[str]] = Field(default_factory=dict)
    testing_verified_rule_map: dict[str, list[str]] = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True)

    def model_post_init(self, __context: object, /) -> None:
        """Ensure authored testing maps and ids remain mutually consistent."""
        ordered_testing_ids, testing_rule_map, testing_verified_rule_map = (
            _normalize_family_rule_maps(
                self.testing_ids,
                self.testing_rule_map,
                self.testing_verified_rule_map,
            )
        )
        if not ordered_testing_ids:
            return

        object.__setattr__(self, "testing_ids", ordered_testing_ids)
        object.__setattr__(self, "testing_rule_map", testing_rule_map)
        object.__setattr__(
            self,
            "testing_verified_rule_map",
            testing_verified_rule_map,
        )

    def rule_ids_for_testing(self, testing_id: str | None) -> list[str]:
        """Return rule ids bound to one testing family id."""
        return _rule_ids_for_family(self.testing_rule_map, testing_id)

    def verified_rule_ids_for_testing(self, testing_id: str | None) -> list[str]:
        """Return verified rule ids bound to one testing family id."""
        return _rule_ids_for_family(self.testing_verified_rule_map, testing_id)

    def testing_ids_for_rule(self, rule_id: str | None) -> list[str]:
        """Return explicit testing family ids bound to one rule."""
        return _family_ids_for_rule(self.testing_ids, self.testing_rule_map, rule_id)

    def verified_testing_ids_for_rule(self, rule_id: str | None) -> list[str]:
        """Return explicit verified testing family ids bound to one rule."""
        return _family_ids_for_rule(
            self.testing_ids,
            self.testing_verified_rule_map,
            rule_id,
        )


class ProjectionPerspectiveModel(BaseModel):
    """Projection-family metadata authored by one detector binding."""

    __test__ = False

    detector_id: str
    language: str
    projection_ids: list[str] = Field(default_factory=list)
    projection_rule_map: dict[str, list[str]] = Field(default_factory=dict)
    projection_verified_rule_map: dict[str, list[str]] = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True)

    def model_post_init(self, __context: object, /) -> None:
        """Ensure authored projection maps and ids remain mutually consistent."""
        ordered_projection_ids, projection_rule_map, projection_verified_rule_map = (
            _normalize_family_rule_maps(
                self.projection_ids,
                self.projection_rule_map,
                self.projection_verified_rule_map,
            )
        )
        if not ordered_projection_ids:
            return

        object.__setattr__(self, "projection_ids", ordered_projection_ids)
        object.__setattr__(self, "projection_rule_map", projection_rule_map)
        object.__setattr__(
            self,
            "projection_verified_rule_map",
            projection_verified_rule_map,
        )

    def rule_ids_for_projection(self, projection_id: str | None) -> list[str]:
        """Return rule ids bound to one projection family id."""
        return _rule_ids_for_family(self.projection_rule_map, projection_id)

    def verified_rule_ids_for_projection(self, projection_id: str | None) -> list[str]:
        """Return verified rule ids bound to one projection family id."""
        return _rule_ids_for_family(self.projection_verified_rule_map, projection_id)

    def projection_ids_for_rule(self, rule_id: str | None) -> list[str]:
        """Return explicit projection family ids bound to one rule."""
        return _family_ids_for_rule(
            self.projection_ids,
            self.projection_rule_map,
            rule_id,
        )

    def verified_projection_ids_for_rule(self, rule_id: str | None) -> list[str]:
        """Return explicit verified projection family ids bound to one rule."""
        return _family_ids_for_rule(
            self.projection_ids,
            self.projection_verified_rule_map,
            rule_id,
        )


class BindingPerspectiveBundle(BaseModel):
    """Composed runtime models built from one authored binding.

    A binding may eventually contribute to several perspectives (rule, dogma,
    testing, projection). The current rollout still uses only ``rule_model``,
    but the bundle is the seam that prevents future perspectives from being
    forced into one rule-shaped projection path.
    """

    rule_model: DetectorMetadata | None = Field(default=None)
    dogma_model: DogmaPerspectiveModel | None = Field(default=None)
    testing_model: TestingPerspectiveModel | None = Field(default=None)
    projection_model: ProjectionPerspectiveModel | None = Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    def require_rule_model(self) -> DetectorMetadata:
        """Return the built rule model or raise when absent."""
        if self.rule_model is None:
            msg = "BindingPerspectiveBundle does not contain a rule_model"
            raise ValueError(msg)
        return self.rule_model


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
    def build_bundle(self, language: str) -> BindingPerspectiveBundle:
        """Build composed runtime models for one authored binding."""

    def to_metadata(self, language: str) -> DetectorMetadata:
        """Project this binding into rule metadata for the current runtime path."""
        return self.build_bundle(language).require_rule_model()


class RuleBinding(BaseModel):
    """Explicit binding between one rule id and its dogma/violation bounds."""

    rule_id: str
    violation_selectors: list[str] = Field(default_factory=lambda: ["*"])
    dogma_ids: list[str] = Field(default_factory=list)
    verified_dogma_ids: list[str] | None = None
    testing_ids: list[str] = Field(default_factory=list)
    verified_testing_ids: list[str] | None = None
    projection_ids: list[str] = Field(default_factory=list)
    verified_projection_ids: list[str] | None = None

    def model_post_init(self, __context: object, /) -> None:
        """Default empty violation selectors to the wildcard selector."""
        if not self.violation_selectors:
            self.violation_selectors = ["*"]
        if self.verified_dogma_ids is None:
            self.verified_dogma_ids = (
                list(self.dogma_ids) if len(self.dogma_ids) == 1 else []
            )
        if self.verified_testing_ids is None:
            self.verified_testing_ids = (
                list(self.testing_ids) if len(self.testing_ids) == 1 else []
            )
        if self.verified_projection_ids is None:
            self.verified_projection_ids = (
                list(self.projection_ids) if len(self.projection_ids) == 1 else []
            )


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

    @property
    def rule_verified_dogma_map(self) -> dict[str, list[str]]:
        """Return explicitly authored verified dogma ids grouped by rule id."""
        return {
            rule.rule_id: list(rule.verified_dogma_ids or []) for rule in self.rules
        }

    @property
    def rule_testing_map(self) -> dict[str, list[str]]:
        """Return explicit testing family ids grouped by rule id."""
        return {rule.rule_id: list(rule.testing_ids) for rule in self.rules}

    @property
    def rule_verified_testing_map(self) -> dict[str, list[str]]:
        """Return explicitly authored verified testing ids grouped by rule id."""
        return {
            rule.rule_id: list(rule.verified_testing_ids or []) for rule in self.rules
        }

    @property
    def rule_projection_map(self) -> dict[str, list[str]]:
        """Return explicit projection family ids grouped by rule id."""
        return {rule.rule_id: list(rule.projection_ids) for rule in self.rules}

    @property
    def rule_verified_projection_map(self) -> dict[str, list[str]]:
        """Return explicitly authored verified projection ids grouped by rule id."""
        return {
            rule.rule_id: list(rule.verified_projection_ids or [])
            for rule in self.rules
        }

    def build_bundle(self, language: str) -> BindingPerspectiveBundle:
        """Build the rule-perspective bundle for a rule detector binding."""
        from mcp_zen_of_languages.analyzers.registry import DetectorMetadata

        dogma_rule_map: dict[str, list[str]] = {}
        dogma_verified_rule_map: dict[str, list[str]] = {}
        testing_rule_map: dict[str, list[str]] = {}
        testing_verified_rule_map: dict[str, list[str]] = {}
        projection_rule_map: dict[str, list[str]] = {}
        projection_verified_rule_map: dict[str, list[str]] = {}
        for rule_id in self.rule_ids:
            for dogma_id in self.rule_dogma_map.get(rule_id, []):
                dogma_rule_map.setdefault(dogma_id, []).append(rule_id)
            for dogma_id in self.rule_verified_dogma_map.get(rule_id, []):
                dogma_verified_rule_map.setdefault(dogma_id, []).append(rule_id)
            for testing_id in self.rule_testing_map.get(rule_id, []):
                testing_rule_map.setdefault(testing_id, []).append(rule_id)
            for testing_id in self.rule_verified_testing_map.get(rule_id, []):
                testing_verified_rule_map.setdefault(testing_id, []).append(rule_id)
            for projection_id in self.rule_projection_map.get(rule_id, []):
                projection_rule_map.setdefault(projection_id, []).append(rule_id)
            for projection_id in self.rule_verified_projection_map.get(rule_id, []):
                projection_verified_rule_map.setdefault(projection_id, []).append(
                    rule_id
                )

        return BindingPerspectiveBundle(
            rule_model=DetectorMetadata(
                detector_id=self.detector_id,
                detector_class=self.detector_class,
                config_model=self.config_model,
                language=language,
                rule_ids=list(self.rule_ids),
                rule_map=dict(self.rule_map),
                rule_dogma_map=dict(self.rule_dogma_map),
                rule_verified_dogma_map=dict(self.rule_verified_dogma_map),
                default_order=self.default_order,
                enabled_by_default=self.enabled_by_default,
            ),
            dogma_model=DogmaPerspectiveModel(
                detector_id=self.detector_id,
                language=language,
                dogma_ids=list(
                    dict.fromkeys(
                        [*dogma_rule_map.keys(), *dogma_verified_rule_map.keys()]
                    ),
                ),
                dogma_rule_map=dogma_rule_map,
                dogma_verified_rule_map=dogma_verified_rule_map,
            ),
            testing_model=TestingPerspectiveModel(
                detector_id=self.detector_id,
                language=language,
                testing_ids=list(
                    dict.fromkeys(
                        [*testing_rule_map.keys(), *testing_verified_rule_map.keys()],
                    ),
                ),
                testing_rule_map=testing_rule_map,
                testing_verified_rule_map=testing_verified_rule_map,
            ),
            projection_model=ProjectionPerspectiveModel(
                detector_id=self.detector_id,
                language=language,
                projection_ids=list(
                    dict.fromkeys(
                        [
                            *projection_rule_map.keys(),
                            *projection_verified_rule_map.keys(),
                        ],
                    ),
                ),
                projection_rule_map=projection_rule_map,
                projection_verified_rule_map=projection_verified_rule_map,
            ),
        )


class NonRuleDetectorBinding(BaseBinding):
    """Binding for generic detectors that do not map to explicit rules."""

    binding_kind: Literal["generic"] = "generic"

    def build_bundle(self, language: str) -> BindingPerspectiveBundle:
        """Build the rule-perspective bundle for a non-rule detector binding."""
        from mcp_zen_of_languages.analyzers.registry import DetectorMetadata

        return BindingPerspectiveBundle(
            rule_model=DetectorMetadata(
                detector_id=self.detector_id,
                detector_class=self.detector_class,
                config_model=self.config_model,
                language=language,
                rule_ids=[],
                rule_map={},
                rule_dogma_map={},
                rule_verified_dogma_map={},
                default_order=self.default_order,
                enabled_by_default=self.enabled_by_default,
            ),
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
