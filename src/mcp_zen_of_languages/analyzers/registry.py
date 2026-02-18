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
scans ``languages/*/mapping.py`` modules and auto-generates config models
for rules that lack hand-written detectors.

See Also:
    [`mcp_zen_of_languages.analyzers.registry_bootstrap`][mcp_zen_of_languages.analyzers.registry_bootstrap] — populates
    this registry on first use.
"""

from __future__ import annotations

import operator
from functools import reduce
from typing import TYPE_CHECKING, Annotated, Any

from pydantic import BaseModel, ConfigDict, Discriminator, Field, TypeAdapter

from mcp_zen_of_languages.analyzers.base import (
    AnalyzerConfig,
    DetectionPipeline,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import DetectorConfig
from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples, ZenPrinciple

if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding


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
        default_order: Sort key controlling detector execution order inside
            a pipeline; lower values run first.
        enabled_by_default: Whether this detector is included when building
            the discriminated-union config adapter.
    """

    detector_id: str
    detector_class: type[ViolationDetector]
    config_model: type[DetectorConfig] | type[AnalyzerConfig]
    language: str
    rule_ids: list[str] = Field(default_factory=list)
    rule_map: dict[str, list[str]] = Field(default_factory=dict)
    default_order: int = 0
    enabled_by_default: bool = True

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_binding(cls, binding: DetectorBinding, language: str) -> DetectorMetadata:
        """Construct metadata from a [`DetectorBinding`][mcp_zen_of_languages.analyzers.mapping_models.DetectorBinding].

        Copies all binding fields into a ``DetectorMetadata`` instance,
        tagging it with the owning *language* so the registry can resolve
        detectors by ``(language, rule_id)`` pair.

        Args:
            binding: A detector binding declared in a language's
                ``mapping.py`` module.
            language: Language that owns this binding (e.g. ``"rust"``).

        Returns:
            Registry-ready metadata for [`DetectorRegistry.register`][DetectorRegistry.register].
        """

        return cls(
            detector_id=binding.detector_id,
            detector_class=binding.detector_class,
            config_model=binding.config_model,
            language=language,
            rule_ids=list(binding.rule_ids),
            rule_map=dict(binding.rule_map),
            default_order=binding.default_order,
            enabled_by_default=binding.enabled_by_default,
        )

    def model_post_init(self, __context: object) -> None:
        """Ensure ``rule_ids`` and ``rule_map`` are mutually consistent.

        If only one of the two was provided at construction time, the other
        is derived automatically: missing ``rule_map`` entries default to
        ``["*"]`` (cover all violation specs), and missing ``rule_ids``
        are extracted from ``rule_map`` keys.

        Args:
            __context: Pydantic internal validation context (unused).
        """

        if not self.rule_map and self.rule_ids:
            self.rule_map = {rule_id: ["*"] for rule_id in self.rule_ids}
        if self.rule_map and not self.rule_ids:
            self.rule_ids = list(self.rule_map.keys())


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
        self._config_union: Any | None = None
        self._config_adapter: TypeAdapter | None = None
        self._rule_index: dict[tuple[str, str], list[DetectorMetadata]] | None = None

    def register(self, metadata: DetectorMetadata) -> None:
        """Add a detector to the registry, invalidating all caches.

        Args:
            metadata: Fully populated metadata for the detector to register.

        Raises:
            ValueError: If a detector with the same ``detector_id`` is
                already registered.
        """

        if metadata.detector_id in self._registry:
            raise ValueError(f"Duplicate detector_id: {metadata.detector_id}")
        self._registry[metadata.detector_id] = metadata
        self._config_union = None
        self._config_adapter = None
        self._rule_index = None

    def bootstrap_from_mappings(self) -> None:
        """Scan ``languages/*/mapping.py`` modules and register their bindings.

        Iterates every non-hidden subdirectory under ``languages/``, imports
        its ``mapping`` module, reads the ``DETECTOR_MAP``
        [`LanguageDetectorMap`][mcp_zen_of_languages.analyzers.mapping_models.LanguageDetectorMap],
        and registers each
        [`DetectorBinding`][mcp_zen_of_languages.analyzers.mapping_models.DetectorBinding]
        as a [`DetectorMetadata`][DetectorMetadata].  Already-populated registries are
        skipped (idempotent guard).

        Raises:
            ValueError: If a discovered ``mapping`` module lacks a
                ``DETECTOR_MAP`` attribute.
        """

        if self._registry:
            return
        import importlib
        from pathlib import Path

        languages_dir = Path(__file__).parent.parent / "languages"
        for subdir in sorted(languages_dir.iterdir()):
            if not subdir.is_dir() or subdir.name.startswith("_"):
                continue
            module_name = f"mcp_zen_of_languages.languages.{subdir.name}.mapping"
            try:
                module = importlib.import_module(module_name)
            except ModuleNotFoundError as exc:
                if exc.name == module_name:
                    continue
                raise
            lang_map = getattr(module, "DETECTOR_MAP", None)
            if lang_map is None:
                raise ValueError(f"Missing DETECTOR_MAP in {module_name}")
            for binding in lang_map.bindings:
                self.register(DetectorMetadata.from_binding(binding, lang_map.language))

    def items(self) -> list[DetectorMetadata]:
        """Return a snapshot of every registered detector's metadata.

        Returns:
            Shallow copy of all metadata entries in registration order.
        """

        return list(self._registry.values())

    def get(self, detector_id: str) -> DetectorMetadata:
        """Look up a single detector by its unique identifier.

        Args:
            detector_id: Registry key matching the ``type`` discriminator
                on the detector's config model.

        Returns:
            The metadata for the requested detector.

        Raises:
            KeyError: If *detector_id* is not registered.
        """

        try:
            return self._registry[detector_id]
        except KeyError as exc:
            raise KeyError(f"Unknown detector_id: {detector_id}") from exc

    def detectors_for_rule(self, rule_id: str, language: str) -> list[DetectorMetadata]:
        """Resolve which detectors enforce a specific zen rule for a language.

        Uses a lazily-built ``(language, rule_id)`` index for O(1) lookups
        after the first call.  The index is invalidated whenever a new
        detector is registered.

        Args:
            rule_id: Zen rule identifier (e.g. ``"py-001"``).
            language: Language scope for the lookup.

        Returns:
            Metadata for every detector covering *rule_id* in *language*,
            or an empty list if none are registered.
        """

        if self._rule_index is None:
            self._rule_index = {}
            for meta in self._registry.values():
                for rid in meta.rule_ids:
                    self._rule_index.setdefault((meta.language, rid), []).append(meta)
        return list(self._rule_index.get((language, rule_id), []))

    def get_config_union(self) -> Any:
        """Build a Pydantic discriminated union covering all registered config models.

        The union uses ``Annotated[... , Discriminator("type")]`` so that
        Pydantic can route a raw dict to the correct config subclass based
        on its ``type`` field.  The result is cached until the registry
        changes.

        Returns:
            An ``Annotated`` union type suitable for
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
            raise ValueError("No detectors registered")

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
            A ``TypeAdapter`` that validates raw dicts into the correct
            ``DetectorConfig`` subclass by discriminator.
        """

        if self._config_adapter is None:
            # Ensure registry is bootstrapped before creating adapter
            from mcp_zen_of_languages.analyzers import registry_bootstrap  # noqa: F401

            self._config_adapter = TypeAdapter(self.get_config_union())
        return self._config_adapter

    def configs_from_rules(
        self, lang_zen: LanguageZenPrinciples
    ) -> list[DetectorConfig]:
        """Project an entire language's zen principles into an ordered config list.

        Each principle's ``metrics`` dict is mapped onto the config fields of
        every detector registered for that rule.  When multiple principles
        map to the same detector type, later values overwrite earlier ones
        (last-write wins per field).  An ``analyzer_defaults`` config is
        always injected at the head of the list to carry global thresholds.

        Args:
            lang_zen: Complete zen principles for a single language.

        Returns:
            Ordered detector configs sorted by [`DetectorMetadata.default_order`][DetectorMetadata.default_order],
            with ``analyzer_defaults`` first.
        """

        from mcp_zen_of_languages.analyzers import registry_bootstrap  # noqa: F401

        configs_by_type: dict[str, DetectorConfig] = {
            "analyzer_defaults": AnalyzerConfig()
        }
        base_fields = set(DetectorConfig.model_fields)

        for principle in lang_zen.principles:
            configs = self._project_principle(principle, lang_zen.language, base_fields)
            for config in configs:
                existing = configs_by_type.get(config.type)
                if existing is None:
                    configs_by_type[config.type] = config
                else:
                    updates = config.model_dump(exclude_unset=True)
                    for key in ("type", "principle_id", "principle", "severity"):
                        updates.pop(key, None)
                    configs_by_type[config.type] = existing.model_copy(update=updates)

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
            base: Rule-derived detector configs to serve as defaults.
            overrides: User or programmatic overrides to layer on top.

        Returns:
            Merged and re-ordered detector config list.
        """

        configs_by_type = {cfg.type: cfg for cfg in base}
        for override in overrides:
            existing = configs_by_type.get(override.type)
            if existing is None:
                configs_by_type[override.type] = override
                continue
            updates = override.model_dump(exclude_unset=True)
            updates.pop("type", None)
            configs_by_type[override.type] = existing.model_copy(update=updates)
        return self._order_configs(configs_by_type)

    def create_pipeline_from_rules(
        self, lang_zen: LanguageZenPrinciples
    ) -> DetectionPipeline:
        """Build a ready-to-run detection pipeline from zen principles.

        Projects *lang_zen* into detector configs via [`configs_from_rules`][configs_from_rules],
        then instantiates each detector's class, attaches its config and
        rule IDs, and wraps the list in a
        [`DetectionPipeline`][mcp_zen_of_languages.analyzers.base.DetectionPipeline].
        The ``analyzer_defaults`` entry is excluded from instantiation
        since it carries global thresholds rather than a detector.

        Args:
            lang_zen: Complete zen principles for the target language.

        Returns:
            Pipeline containing configured detector instances in execution
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
            principle: Zen principle whose ``metrics`` supply threshold
                values.
            language: Language scope used for detector resolution.
            base_fields: Field names defined on the base
                ``DetectorConfig`` that should be excluded from metric
                mapping.

        Returns:
            One typed config per detector registered for this principle,
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
            raise ValueError(
                f"Unknown metric keys for {principle.id}: {sorted(unknown)}"
            )

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
            configs.append(config)
        return configs

    def _order_configs(
        self, configs_by_type: dict[str, DetectorConfig]
    ) -> list[DetectorConfig]:
        """Sort configs by [`DetectorMetadata.default_order`][DetectorMetadata.default_order], ``analyzer_defaults`` first.

        The ``analyzer_defaults`` entry is always placed at index 0 so that
        [`BaseAnalyzer`][mcp_zen_of_languages.analyzers.base.BaseAnalyzer] can
        extract global thresholds before iterating over detector-specific
        configs.

        Args:
            configs_by_type: Configs keyed by detector ``type``.

        Returns:
            Deterministically ordered config list.
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
            )
        )
        return ordered


REGISTRY = DetectorRegistry()
