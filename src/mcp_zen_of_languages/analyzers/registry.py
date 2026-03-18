"""Global detector registry — the single source of truth for available detectors.

Every detector in the system is represented by a [`DetectorMetadata`][DetectorMetadata]
entry inside the module-level :data:`REGISTRY` singleton.  The registry
provides three core capabilities:

* **Lookup** — resolve a detector by its ``detector_id`` or find all
  detectors mapped to a given ``(language, rule_id)`` pair.
* **Projection** — convert
  [`LanguageZenPrinciples`][mcp_zen_of_languages.rules.base_models.LanguageZenPrinciples]
  into ordered [`DetectorConfig`][mcp_zen_of_languages.languages.configs.DetectorConfig]
  lists by mapping principle ``metrics`` onto detector config fields.
* **Merge** — layer user overrides onto rule-derived configs by matching
  on ``DetectorConfig.type``.

Bootstrap happens lazily: the first call to [`DetectorRegistry.adapter`][DetectorRegistry.adapter]
triggers [`registry_bootstrap`][mcp_zen_of_languages.analyzers.registry_bootstrap], which
scans ``languages/*/mapping.py`` and ``frameworks/*/mapping.py`` modules and auto-generates config models
for rules that lack hand-written detectors.

See Also:
    [`mcp_zen_of_languages.analyzers.registry_bootstrap`][mcp_zen_of_languages.analyzers.registry_bootstrap] — populates
    this registry on first use.
"""

from __future__ import annotations

import importlib
import operator

from functools import reduce
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Annotated
from typing import Any

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Discriminator
from pydantic import Field
from pydantic import TypeAdapter

from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.base import DetectionPipeline
from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.languages.configs import DetectorConfig
from mcp_zen_of_languages.languages.configs import RuleContext


if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.mapping_models import BindingPerspectiveBundle
    from mcp_zen_of_languages.analyzers.mapping_models import DogmaPerspectiveModel
    from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
    from mcp_zen_of_languages.analyzers.mapping_models import ProjectionPerspectiveModel
    from mcp_zen_of_languages.analyzers.mapping_models import TestingPerspectiveModel
    from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
    from mcp_zen_of_languages.rules.base_models import ZenPrinciple


class DetectorMetadata(BaseModel):
    """Everything the registry knows about a single detector.

    Each registered detector carries enough information to instantiate its
    [`ViolationDetector`][mcp_zen_of_languages.analyzers.base.ViolationDetector], validate
    its configuration, and link it back to the zen rules it enforces.

    Attributes:
        detector_id: Unique string key used for registry lookup and as the
            ``type`` discriminator in ``DetectorConfig``.
        detector_class: Concrete ``ViolationDetector`` subclass to
            instantiate when building the detection pipeline.
        config_model: Pydantic model class used to validate and hold
            threshold values for this detector.
        language: Language this detector belongs to (e.g. ``"python"``).
        rule_ids: Zen rule identifiers this detector covers.  Populated
            from [`rule_map`][rule_map] keys when not set explicitly.
        rule_map: Maps each rule ID to the list of violation-spec indices
            the detector can flag; ``["*"]`` means all specs.
        rule_dogma_map: Maps each rule ID to the dogma ids bound to that
            specific rule.
        rule_verified_dogma_map: Maps each rule ID to the dogma ids the
            detector authoritatively verifies itself.
        default_order: Sort key controlling detector execution order inside
            a pipeline; lower values run first.
        enabled_by_default: Whether this detector is included when building
            the discriminated-union config adapter.
    """

    detector_id: str
    detector_class: type[ViolationDetector]
    config_model: type[DetectorConfig | AnalyzerConfig]
    language: str
    rule_ids: list[str] = Field(default_factory=list)
    rule_map: dict[str, list[str]] = Field(default_factory=dict)
    rule_dogma_map: dict[str, list[str]] = Field(default_factory=dict)
    rule_verified_dogma_map: dict[str, list[str]] = Field(default_factory=dict)
    default_order: int = 0
    enabled_by_default: bool = True

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_post_init(self, __context: object, /) -> None:
        """Ensure ``rule_ids`` and ``rule_map`` are mutually consistent.

        Missing ``rule_map`` entries default to ``["*"]`` (cover all
        violation specs). Rule ids are inferred from the union of
        ``rule_ids``, ``rule_map`` keys, and ``rule_dogma_map`` keys.
        """
        ordered_rule_ids = list(
            dict.fromkeys(
                [
                    *self.rule_ids,
                    *self.rule_map.keys(),
                    *self.rule_dogma_map.keys(),
                    *self.rule_verified_dogma_map.keys(),
                ],
            ),
        )
        if not ordered_rule_ids:
            return

        self.rule_ids = ordered_rule_ids
        for rule_id in ordered_rule_ids:
            self.rule_map.setdefault(rule_id, ["*"])
            self.rule_dogma_map.setdefault(rule_id, [])
            self.rule_verified_dogma_map.setdefault(rule_id, [])

    def dogma_ids_for_rule(self, rule_id: str | None) -> list[str]:
        """Return explicit dogma ids bound to one rule."""
        if rule_id and rule_id in self.rule_dogma_map:
            return list(self.rule_dogma_map[rule_id])
        if len(self.rule_dogma_map) == 1:
            return list(next(iter(self.rule_dogma_map.values())))
        return []

    def verified_dogma_ids_for_rule(self, rule_id: str | None) -> list[str]:
        """Return explicitly authored verified dogma ids for one rule."""
        if rule_id and rule_id in self.rule_verified_dogma_map:
            return list(self.rule_verified_dogma_map[rule_id])
        if len(self.rule_verified_dogma_map) == 1:
            return list(next(iter(self.rule_verified_dogma_map.values())))
        return []


class DetectorRegistry:
    """Singleton-style registry that maps detector IDs to [`DetectorMetadata`][DetectorMetadata].

    The registry is the central coordination point between zen rules,
    detector implementations, and their typed configurations.  It maintains
    three lazily-built caches:

    * ``_config_union`` — a Pydantic discriminated union of all registered
      config models, enabling ``TypeAdapter`` validation of raw dicts.
    * ``_config_adapter`` — a [`TypeAdapter`][pydantic.TypeAdapter] wrapping the
      union for fast, repeated validation.
    * ``_rule_index`` — a ``(language, rule_id)`` lookup table for
      resolving which detectors cover a given rule.

    All caches are invalidated whenever a new detector is registered.
    """

    def __init__(self) -> None:
        """Create an empty registry with no detectors or caches."""
        self._registry: dict[str, DetectorMetadata] = {}
        self._bundles: dict[tuple[str, str], BindingPerspectiveBundle] = {}
        self._config_union: Any | None = None
        self._config_adapter: TypeAdapter | None = None
        self._rule_index: dict[tuple[str, str], list[DetectorMetadata]] | None = None
        self._bundle_rule_index: (
            dict[tuple[str, str], list[BindingPerspectiveBundle]] | None
        ) = None
        self._dogma_rule_index: (
            dict[tuple[str, str], list[DogmaPerspectiveModel]] | None
        ) = None
        self._dogma_family_index: (
            dict[tuple[str, str], list[DogmaPerspectiveModel]] | None
        ) = None
        self._testing_rule_index: (
            dict[tuple[str, str], list[TestingPerspectiveModel]] | None
        ) = None
        self._projection_rule_index: (
            dict[tuple[str, str], list[ProjectionPerspectiveModel]] | None
        ) = None
        self._testing_family_index: (
            dict[tuple[str, str], list[TestingPerspectiveModel]] | None
        ) = None
        self._projection_family_index: (
            dict[tuple[str, str], list[ProjectionPerspectiveModel]] | None
        ) = None

    def register(
        self,
        metadata: DetectorMetadata,
        *,
        bundle: BindingPerspectiveBundle | None = None,
    ) -> None:
        """Add a detector to the registry, invalidating all caches.

        Args:
            metadata (DetectorMetadata): Fully populated metadata for the detector to register.
            bundle (BindingPerspectiveBundle | None): Optional authored
                bundle to preserve alongside rule metadata. When omitted,
                a synthetic rule-only bundle is stored for compatibility.

        Raises:
            ValueError: If a detector with the same ``detector_id`` is
                already registered.
        """
        from mcp_zen_of_languages.analyzers.mapping_models import (
            BindingPerspectiveBundle,
        )

        if metadata.detector_id in self._registry:
            msg = f"Duplicate detector_id: {metadata.detector_id}"
            raise ValueError(msg)
        if bundle is None:
            bundle = BindingPerspectiveBundle(rule_model=metadata)
        self._registry[metadata.detector_id] = metadata
        self._bundles[(metadata.language, metadata.detector_id)] = bundle
        self._config_union = None
        self._config_adapter = None
        self._rule_index = None
        self._bundle_rule_index = None
        self._dogma_rule_index = None
        self._dogma_family_index = None
        self._testing_rule_index = None
        self._projection_rule_index = None
        self._testing_family_index = None
        self._projection_family_index = None

    @staticmethod
    def _merge_named_rule_maps(
        existing: dict[str, list[str]],
        incoming: dict[str, list[str]],
    ) -> dict[str, list[str]]:
        """Merge authored family→rule maps while preserving first-seen order."""
        ordered_names = list(dict.fromkeys([*existing.keys(), *incoming.keys()]))
        merged: dict[str, list[str]] = {}
        for name in ordered_names:
            merged[name] = list(
                dict.fromkeys([*existing.get(name, []), *incoming.get(name, [])]),
            )
        return merged

    def _merge_testing_models(
        self,
        existing: TestingPerspectiveModel | None,
        incoming: TestingPerspectiveModel | None,
    ) -> TestingPerspectiveModel | None:
        """Merge discovered testing-family metadata onto an existing bundle."""
        if existing is None:
            return incoming
        if incoming is None:
            return existing
        return incoming.model_copy(
            update={
                "testing_ids": list(
                    dict.fromkeys([*existing.testing_ids, *incoming.testing_ids]),
                ),
                "testing_rule_map": self._merge_named_rule_maps(
                    existing.testing_rule_map,
                    incoming.testing_rule_map,
                ),
                "testing_verified_rule_map": self._merge_named_rule_maps(
                    existing.testing_verified_rule_map,
                    incoming.testing_verified_rule_map,
                ),
            },
        )

    def _testing_bundle_for_family(
        self,
        bundle: BindingPerspectiveBundle,
        family: str,
    ) -> BindingPerspectiveBundle:
        """Ensure a discovered testing mapping contributes at least one family id."""
        from mcp_zen_of_languages.analyzers.mapping_models import (
            TestingPerspectiveModel,
        )

        rule_model = bundle.rule_model
        if rule_model is None:
            return bundle
        authored = bundle.testing_model
        synthesized = TestingPerspectiveModel(
            detector_id=rule_model.detector_id,
            language=rule_model.language,
            testing_rule_map={family: list(rule_model.rule_ids)},
            testing_verified_rule_map={family: list(rule_model.rule_ids)},
        )
        merged_testing_model = self._merge_testing_models(authored, synthesized)
        return bundle.model_copy(update={"testing_model": merged_testing_model})

    def _overlay_testing_bundle(
        self,
        metadata: DetectorMetadata,
        bundle: BindingPerspectiveBundle,
    ) -> None:
        """Attach discovered testing metadata to an already-registered parent bundle."""
        key = (metadata.language, metadata.detector_id)
        existing_bundle = self._bundles.get(key)
        if existing_bundle is None:
            msg = (
                "Testing overlay requires an existing parent detector bundle: "
                f"language={metadata.language} detector_id={metadata.detector_id}"
            )
            raise ValueError(msg)
        self._bundles[key] = existing_bundle.model_copy(
            update={
                "testing_model": self._merge_testing_models(
                    existing_bundle.testing_model,
                    bundle.testing_model,
                ),
            },
        )
        self._testing_rule_index = None
        self._testing_family_index = None

    def _import_detector_map(self, module_name: str) -> LanguageDetectorMap | None:
        """Import a mapping module and return its ``DETECTOR_MAP`` when present."""
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            if exc.name == module_name:
                return None
            raise
        detector_map = getattr(module, "DETECTOR_MAP", None)
        if detector_map is None:
            msg = f"Missing DETECTOR_MAP in {module_name}"
            raise ValueError(msg)
        return detector_map

    def _register_package_mappings(
        self,
        *,
        package_name: str,
        package_root: Path,
    ) -> None:
        """Register detector bundles from one package root."""
        if not package_root.exists():
            return
        for subdir in sorted(package_root.iterdir()):
            if not subdir.is_dir() or subdir.name.startswith("_"):
                continue
            module_name = f"mcp_zen_of_languages.{package_name}.{subdir.name}.mapping"
            detector_map = self._import_detector_map(module_name)
            if detector_map is None:
                continue
            for binding in detector_map.bindings:
                bundle = binding.build_bundle(detector_map.language)
                self.register(bundle.require_rule_model(), bundle=bundle)

    def _register_testing_overlays(self, languages_root: Path) -> None:
        """Register discovered testing overlays onto parent-language bundles."""
        if not languages_root.exists():
            return
        for language_dir in sorted(languages_root.iterdir()):
            if not language_dir.is_dir() or language_dir.name.startswith("_"):
                continue
            testing_root = language_dir / "testing"
            if not testing_root.exists():
                continue
            for family_dir in sorted(testing_root.iterdir()):
                if not family_dir.is_dir() or family_dir.name.startswith("_"):
                    continue
                module_name = (
                    "mcp_zen_of_languages.languages."
                    f"{language_dir.name}.testing.{family_dir.name}.mapping"
                )
                testing_map = self._import_detector_map(module_name)
                if testing_map is None:
                    continue
                for binding in testing_map.bindings:
                    bundle = self._testing_bundle_for_family(
                        binding.build_bundle(language_dir.name),
                        family_dir.name,
                    )
                    self._overlay_testing_bundle(bundle.require_rule_model(), bundle)

    def bootstrap_from_mappings(self) -> None:
        """Scan support-module mappings and register their bindings.

        Iterates every non-hidden subdirectory under ``languages/`` and
        ``frameworks/``, imports its ``mapping`` module, reads the ``DETECTOR_MAP``
        [`LanguageDetectorMap`][mcp_zen_of_languages.analyzers.mapping_models.LanguageDetectorMap],
        and registers each
        binding entries
        as a [`DetectorMetadata`][DetectorMetadata].  Already-populated registries are
        skipped (idempotent guard).

        Raises:
            ValueError: If a discovered ``mapping`` module lacks a
                ``DETECTOR_MAP`` attribute.
        """
        if self._registry:
            return
        languages_root = Path(__file__).parent.parent / "languages"
        self._register_package_mappings(
            package_name="languages",
            package_root=languages_root,
        )
        self._register_package_mappings(
            package_name="frameworks",
            package_root=Path(__file__).parent.parent / "frameworks",
        )
        self._register_testing_overlays(languages_root)

    def items(self) -> list[DetectorMetadata]:
        """Return a snapshot of every registered detector's metadata.

        Returns:
            list[DetectorMetadata]: Shallow copy of all metadata entries in registration order.
        """
        return list(self._registry.values())

    def get(self, detector_id: str) -> DetectorMetadata:
        """Look up a single detector by its unique identifier.

        Args:
            detector_id (str): Registry key matching the ``type`` discriminator
                on the detector's config model.

        Returns:
            DetectorMetadata: The metadata for the requested detector.

        Raises:
            KeyError: If *detector_id* is not registered.
        """
        try:
            return self._registry[detector_id]
        except KeyError as exc:
            msg = f"Unknown detector_id: {detector_id}"
            raise KeyError(msg) from exc

    def get_bundle(self, detector_id: str, language: str) -> BindingPerspectiveBundle:
        """Look up the preserved authored bundle for one detector identity."""
        try:
            return self._bundles[(language, detector_id)]
        except KeyError as exc:
            msg = f"Unknown bundle: language={language} detector_id={detector_id}"
            raise KeyError(msg) from exc

    def get_dogma_model(
        self,
        detector_id: str,
        language: str,
    ) -> DogmaPerspectiveModel | None:
        """Return preserved dogma-family metadata for one detector identity."""
        return self.get_bundle(detector_id, language).dogma_model

    def get_testing_model(
        self,
        detector_id: str,
        language: str,
    ) -> TestingPerspectiveModel | None:
        """Return preserved testing-family metadata for one detector identity."""
        return self.get_bundle(detector_id, language).testing_model

    def get_projection_model(
        self,
        detector_id: str,
        language: str,
    ) -> ProjectionPerspectiveModel | None:
        """Return preserved projection-family metadata for one detector identity."""
        return self.get_bundle(detector_id, language).projection_model

    def _ensure_rule_indexes(self) -> None:
        """Build lazy rule indexes for metadata and preserved authored bundles."""
        if self._rule_index is not None and self._bundle_rule_index is not None:
            return

        self._rule_index = {}
        self._bundle_rule_index = {}
        for meta in self._registry.values():
            bundle = self._bundles[(meta.language, meta.detector_id)]
            for rule_id in meta.rule_ids:
                key = (meta.language, rule_id)
                self._rule_index.setdefault(key, []).append(meta)
                self._bundle_rule_index.setdefault(key, []).append(bundle)

    def _index_dogma_model(
        self,
        *,
        language: str,
        model: DogmaPerspectiveModel,
    ) -> None:
        """Index one dogma perspective model by rule id and dogma family id."""
        merged_rule_map = self._merge_named_rule_maps(
            model.dogma_rule_map,
            model.dogma_verified_rule_map,
        )
        for dogma_id, rule_ids in merged_rule_map.items():
            family_key = (language, dogma_id)
            self._dogma_family_index.setdefault(family_key, []).append(model)
            for rule_id in rule_ids:
                rule_key = (language, rule_id)
                self._dogma_rule_index.setdefault(rule_key, []).append(model)

    def _ensure_family_indexes(self) -> None:
        """Build lazy family indexes from preserved bundle metadata only."""
        if (
            self._dogma_rule_index is not None
            and self._dogma_family_index is not None
            and self._testing_rule_index is not None
            and self._projection_rule_index is not None
            and self._testing_family_index is not None
            and self._projection_family_index is not None
        ):
            return

        self._dogma_rule_index = {}
        self._dogma_family_index = {}
        self._testing_rule_index = {}
        self._projection_rule_index = {}
        self._testing_family_index = {}
        self._projection_family_index = {}
        for (language, _detector_id), bundle in self._bundles.items():
            if bundle.dogma_model is not None:
                self._index_dogma_model(language=language, model=bundle.dogma_model)
            if bundle.testing_model is not None:
                for (
                    testing_id,
                    rule_ids,
                ) in bundle.testing_model.testing_rule_map.items():
                    family_key = (language, testing_id)
                    self._testing_family_index.setdefault(family_key, []).append(
                        bundle.testing_model,
                    )
                    for rule_id in rule_ids:
                        rule_key = (language, rule_id)
                        self._testing_rule_index.setdefault(rule_key, []).append(
                            bundle.testing_model,
                        )
            if bundle.projection_model is not None:
                for (
                    projection_id,
                    rule_ids,
                ) in bundle.projection_model.projection_rule_map.items():
                    family_key = (language, projection_id)
                    self._projection_family_index.setdefault(family_key, []).append(
                        bundle.projection_model,
                    )
                    for rule_id in rule_ids:
                        rule_key = (language, rule_id)
                        self._projection_rule_index.setdefault(rule_key, []).append(
                            bundle.projection_model,
                        )

    def linked_dogma_ids_for(
        self,
        detector_id: str,
        language: str,
        rule_id: str | None,
    ) -> list[str]:
        """Resolve linked dogma ids through the preserved bundle seam first."""
        try:
            bundle = self.get_bundle(detector_id, language)
        except KeyError:
            return self.get(detector_id).dogma_ids_for_rule(rule_id)
        if bundle.dogma_model is not None:
            dogma_ids = bundle.dogma_model.dogma_ids_for_rule(rule_id)
            if dogma_ids:
                return dogma_ids
        if bundle.rule_model is not None:
            return bundle.rule_model.dogma_ids_for_rule(rule_id)
        return []

    def verified_dogma_ids_for(
        self,
        detector_id: str,
        language: str,
        rule_id: str | None,
    ) -> list[str]:
        """Resolve verified dogma ids through the preserved bundle seam first."""
        try:
            bundle = self.get_bundle(detector_id, language)
        except KeyError:
            return self.get(detector_id).verified_dogma_ids_for_rule(rule_id)
        if bundle.dogma_model is not None:
            dogma_ids = bundle.dogma_model.verified_dogma_ids_for_rule(rule_id)
            if dogma_ids:
                return dogma_ids
        if bundle.rule_model is not None:
            return bundle.rule_model.verified_dogma_ids_for_rule(rule_id)
        return []

    def testing_ids_for(
        self,
        detector_id: str,
        language: str,
        rule_id: str | None,
    ) -> list[str]:
        """Resolve testing family ids through preserved bundle metadata."""
        try:
            bundle = self.get_bundle(detector_id, language)
        except KeyError:
            return []
        if bundle.testing_model is None:
            return []
        return bundle.testing_model.testing_ids_for_rule(rule_id)

    def verified_testing_ids_for(
        self,
        detector_id: str,
        language: str,
        rule_id: str | None,
    ) -> list[str]:
        """Resolve verified testing family ids through preserved bundle metadata."""
        try:
            bundle = self.get_bundle(detector_id, language)
        except KeyError:
            return []
        if bundle.testing_model is None:
            return []
        return bundle.testing_model.verified_testing_ids_for_rule(rule_id)

    def projection_ids_for(
        self,
        detector_id: str,
        language: str,
        rule_id: str | None,
    ) -> list[str]:
        """Resolve projection family ids through preserved bundle metadata."""
        try:
            bundle = self.get_bundle(detector_id, language)
        except KeyError:
            return []
        if bundle.projection_model is None:
            return []
        return bundle.projection_model.projection_ids_for_rule(rule_id)

    def verified_projection_ids_for(
        self,
        detector_id: str,
        language: str,
        rule_id: str | None,
    ) -> list[str]:
        """Resolve verified projection family ids through preserved bundle metadata."""
        try:
            bundle = self.get_bundle(detector_id, language)
        except KeyError:
            return []
        if bundle.projection_model is None:
            return []
        return bundle.projection_model.verified_projection_ids_for_rule(rule_id)

    def detectors_for_rule(self, rule_id: str, language: str) -> list[DetectorMetadata]:
        """Resolve which detectors enforce a specific zen rule for a language.

        Uses a lazily-built ``(language, rule_id)`` index for O(1) lookups
        after the first call.  The index is invalidated whenever a new
        detector is registered.

        Args:
            rule_id (str): Zen rule identifier (e.g. ``"py-001"``).
            language (str): Language scope for the lookup.

        Returns:
            list[DetectorMetadata]: Metadata for every detector covering *rule_id* in *language*,
            or an empty list if none are registered.
        """
        self._ensure_rule_indexes()
        return list(self._rule_index.get((language, rule_id), []))

    def bundles_for_rule(
        self,
        rule_id: str,
        language: str,
    ) -> list[BindingPerspectiveBundle]:
        """Return preserved authored bundles covering one rule in one language."""
        self._ensure_rule_indexes()
        return list(self._bundle_rule_index.get((language, rule_id), []))

    def dogma_models_for_rule(
        self,
        rule_id: str,
        language: str,
    ) -> list[DogmaPerspectiveModel]:
        """Return preserved dogma-family models for one rule in one language."""
        self._ensure_family_indexes()
        return list(self._dogma_rule_index.get((language, rule_id), []))

    def dogma_models_for_family(
        self,
        dogma_id: str,
        language: str,
    ) -> list[DogmaPerspectiveModel]:
        """Return preserved dogma-family models for one dogma id."""
        self._ensure_family_indexes()
        return list(self._dogma_family_index.get((language, dogma_id), []))

    def testing_models_for_rule(
        self,
        rule_id: str,
        language: str,
    ) -> list[TestingPerspectiveModel]:
        """Return preserved testing-family models for one rule in one language."""
        self._ensure_family_indexes()
        return list(self._testing_rule_index.get((language, rule_id), []))

    def projection_models_for_rule(
        self,
        rule_id: str,
        language: str,
    ) -> list[ProjectionPerspectiveModel]:
        """Return preserved projection-family models for one rule in one language."""
        self._ensure_family_indexes()
        return list(self._projection_rule_index.get((language, rule_id), []))

    def testing_models_for_family(
        self,
        testing_id: str,
        language: str,
    ) -> list[TestingPerspectiveModel]:
        """Return preserved testing-family models for one testing family id."""
        self._ensure_family_indexes()
        return list(self._testing_family_index.get((language, testing_id), []))

    def projection_models_for_family(
        self,
        projection_id: str,
        language: str,
    ) -> list[ProjectionPerspectiveModel]:
        """Return preserved projection-family models for one projection family id."""
        self._ensure_family_indexes()
        return list(self._projection_family_index.get((language, projection_id), []))

    def get_config_union(self) -> object:
        """Build a Pydantic discriminated union covering all registered config models.

        The union uses ``Annotated[... , Discriminator("type")]`` so that
        Pydantic can route a raw dict to the correct config subclass based
        on its ``type`` field.  The result is cached until the registry
        changes.

        Returns:
            object: An ``Annotated`` union type suitable for
            [`TypeAdapter`][pydantic.TypeAdapter] construction.

        Raises:
            ValueError: If no detectors are registered.
        """
        if self._config_union is not None:
            return self._config_union

        config_models = [
            meta.config_model
            for meta in self._registry.values()
            if meta.enabled_by_default or meta.detector_id == "analyzer_defaults"
        ]
        if not config_models:
            msg = "No detectors registered"
            raise ValueError(msg)

        union_type = reduce(operator.or_, config_models)
        union_type = Annotated[union_type, Discriminator("type")]
        self._config_union = union_type
        return union_type

    def adapter(self) -> TypeAdapter:
        """Return a cached [`TypeAdapter`][pydantic.TypeAdapter] for config validation.

        On first call the adapter triggers
        [`registry_bootstrap`][mcp_zen_of_languages.analyzers.registry_bootstrap] to ensure
        all detectors (including auto-generated rule-pattern detectors) are
        registered before the discriminated union is constructed.

        Returns:
            TypeAdapter: A ``TypeAdapter`` that validates raw dicts into the correct
            ``DetectorConfig`` subclass by discriminator.
        """
        if self._config_adapter is None:
            # Ensure registry is bootstrapped before creating adapter
            from mcp_zen_of_languages.analyzers import registry_bootstrap  # noqa: F401

            self._config_adapter = TypeAdapter(self.get_config_union())
        return self._config_adapter

    def configs_from_rules(
        self,
        lang_zen: LanguageZenPrinciples,
    ) -> list[DetectorConfig]:
        """Project an entire language's zen principles into an ordered config list.

        Each principle's ``metrics`` dict is mapped onto the config fields of
        every detector registered for that rule.  When multiple principles
        map to the same detector type, later values overwrite earlier ones
        (last-write wins per field).  An ``analyzer_defaults`` config is
        always injected at the head of the list to carry global thresholds.

        Args:
            lang_zen (LanguageZenPrinciples): Complete zen principles for a single language.

        Returns:
            list[DetectorConfig]: Ordered detector configs sorted by [`DetectorMetadata.default_order`][DetectorMetadata.default_order],
            with ``analyzer_defaults`` first.
        """
        from mcp_zen_of_languages.analyzers import registry_bootstrap  # noqa: F401

        configs_by_type: dict[str, DetectorConfig] = {
            "analyzer_defaults": AnalyzerConfig(),
        }
        base_fields = set(DetectorConfig.model_fields)

        for principle in lang_zen.principles:
            configs = self._project_principle(principle, lang_zen.language, base_fields)
            for config in configs:
                existing = configs_by_type.get(config.type)
                if existing is None:
                    configs_by_type[config.type] = config
                else:
                    configs_by_type[config.type] = self._merge_detector_config(
                        existing,
                        config,
                        drop_fields={"principle_id", "principle", "severity"},
                    )

        return self.merge_configs([], list(configs_by_type.values()))

    def merge_configs(
        self,
        base: list[DetectorConfig],
        overrides: list[DetectorConfig],
    ) -> list[DetectorConfig]:
        """Merge override configs into base configs by ``type`` discriminator.

        For each override, if a base config with the same ``type`` exists,
        only the explicitly-set fields from the override are applied via
        ``model_copy(update=...)``.  Overrides for types not present in
        *base* are appended as new entries.  The final list is sorted by
        [`DetectorMetadata.default_order`][DetectorMetadata.default_order].

        Args:
            base (list[DetectorConfig]): Rule-derived detector configs to serve as defaults.
            overrides (list[DetectorConfig]): User or programmatic overrides to layer on top.

        Returns:
            list[DetectorConfig]: Merged and re-ordered detector config list.
        """
        configs_by_type = {cfg.type: cfg for cfg in base}
        for override in overrides:
            existing = configs_by_type.get(override.type)
            if existing is None:
                configs_by_type[override.type] = override
                continue
            configs_by_type[override.type] = self._merge_detector_config(
                existing,
                override,
            )
        return self._order_configs(configs_by_type)

    def create_pipeline_from_rules(
        self,
        lang_zen: LanguageZenPrinciples,
    ) -> DetectionPipeline:
        """Build a ready-to-run detection pipeline from zen principles.

        Projects *lang_zen* into detector configs via [`configs_from_rules`][configs_from_rules],
        then instantiates each detector's class, attaches its config and
        rule IDs, and wraps the list in a
        [`DetectionPipeline`][mcp_zen_of_languages.analyzers.base.DetectionPipeline].
        The ``analyzer_defaults`` entry is excluded from instantiation
        since it carries global thresholds rather than a detector.

        Args:
            lang_zen (LanguageZenPrinciples): Complete zen principles for the target language.

        Returns:
            DetectionPipeline: Pipeline containing configured detector instances in execution
            order.
        """
        configs = self.configs_from_rules(lang_zen)
        detectors: list[ViolationDetector] = []
        for config in configs:
            if config.type == "analyzer_defaults":
                continue
            meta = self.get(config.type)
            detector = meta.detector_class()
            detector.config = config
            detector.rule_ids = list(meta.rule_ids)
            detectors.append(detector)
        return DetectionPipeline(detectors)

    def _project_principle(
        self,
        principle: ZenPrinciple,
        language: str,
        base_fields: set[str],
    ) -> list[DetectorConfig]:
        """Map a single zen principle's metrics onto its detector configs.

        The principle's ``metrics`` keys are validated against the *union* of
        all config fields across every detector registered for this rule
        (minus ``base_fields`` inherited from ``DetectorConfig``).
        Unknown keys trigger an immediate ``ValueError`` to catch rule
        definition typos at startup.

        Args:
            principle (ZenPrinciple): Zen principle whose ``metrics`` supply threshold
                values.
            language (str): Language scope used for detector resolution.
            base_fields (set[str]): Field names defined on the base
                ``DetectorConfig`` that should be excluded from metric
                mapping.

        Returns:
            list[DetectorConfig]: One typed config per detector registered for this principle,
            each populated with the applicable metric values, severity,
            and violation messages.

        Raises:
            ValueError: If *principle.metrics* contains keys not present
                on any registered detector's config model.
        """
        configs: list[DetectorConfig] = []
        metrics = principle.metrics or {}
        metas = self.detectors_for_rule(principle.id, language)
        if not metas:
            return configs

        allowed_keys: set[str] = set()
        for meta in metas:
            allowed_keys |= set(meta.config_model.model_fields) - base_fields

        if unknown := set(metrics) - allowed_keys:
            msg = f"Unknown metric keys for {principle.id}: {sorted(unknown)}"
            raise ValueError(msg)

        for meta in metas:
            config_fields = set(meta.config_model.model_fields) - base_fields
            payload = {
                key: value for key, value in metrics.items() if key in config_fields
            }
            data: dict[str, object] = {"type": meta.detector_id}
            if payload:
                data |= payload
            config = self.adapter().validate_python(data)
            config.principle_id = principle.id
            config.principle = principle.principle
            config.severity = principle.severity
            config.violation_messages = [
                spec.description for spec in principle.violation_specs
            ]
            config.detectable_patterns = (
                list(principle.detectable_patterns)
                if principle.detectable_patterns
                else None
            )
            config.recommended_alternative = principle.recommended_alternative
            config.rule_contexts[principle.id] = RuleContext(
                principle_id=principle.id,
                principle=principle.principle,
                severity=principle.severity,
                violation_messages=list(config.violation_messages)
                if config.violation_messages
                else None,
                detectable_patterns=list(config.detectable_patterns)
                if config.detectable_patterns
                else None,
                recommended_alternative=config.recommended_alternative,
                linked_dogma_ids=meta.dogma_ids_for_rule(principle.id),
                verified_dogma_ids=meta.verified_dogma_ids_for_rule(principle.id),
                linked_testing_ids=self.testing_ids_for(
                    meta.detector_id,
                    language,
                    principle.id,
                ),
                verified_testing_ids=self.verified_testing_ids_for(
                    meta.detector_id,
                    language,
                    principle.id,
                ),
            )
            configs.append(config)
        return configs

    def _merge_detector_config(
        self,
        existing: DetectorConfig,
        incoming: DetectorConfig,
        *,
        drop_fields: set[str] | None = None,
    ) -> DetectorConfig:
        """Merge detector configs while preserving composite rule contexts."""
        updates = incoming.model_dump(exclude_unset=True)
        updates.pop("type", None)
        for field_name in drop_fields or set():
            updates.pop(field_name, None)
        merged = existing.model_copy(update=updates)
        merged.rule_contexts = {
            **existing.rule_contexts,
            **{
                rule_id: (
                    context
                    if isinstance(context, RuleContext)
                    else RuleContext.model_validate(context)
                )
                for rule_id, context in incoming.rule_contexts.items()
            },
        }
        return merged

    def _order_configs(
        self,
        configs_by_type: dict[str, DetectorConfig],
    ) -> list[DetectorConfig]:
        """Sort configs by [`DetectorMetadata.default_order`][DetectorMetadata.default_order], ``analyzer_defaults`` first.

        The ``analyzer_defaults`` entry is always placed at index 0 so that
        [`BaseAnalyzer`][mcp_zen_of_languages.analyzers.base.BaseAnalyzer] can
        extract global thresholds before iterating over detector-specific
        configs.

        Args:
            configs_by_type (dict[str, DetectorConfig]): Configs keyed by detector ``type``.

        Returns:
            list[DetectorConfig]: Deterministically ordered config list.
        """
        configs_by_type = dict(configs_by_type)
        order_map = {meta.detector_id: meta.default_order for meta in self.items()}
        ordered: list[DetectorConfig] = []
        defaults = configs_by_type.pop("analyzer_defaults", None)
        if defaults is not None:
            ordered.append(defaults)
        ordered.extend(
            sorted(
                configs_by_type.values(),
                key=lambda cfg: (order_map.get(cfg.type, 0), cfg.type),
            ),
        )
        return ordered


REGISTRY = DetectorRegistry()
