"""Configuration discovery, YAML loading, and pipeline override merging.

Every zen analysis session begins here. This module owns the lifecycle of
``zen-config.yaml``—from locating the file on disk, through YAML parsing,
to Pydantic-validated ``ConfigModel`` construction with fully resolved
detector pipelines.

Discovery algorithm
    When no explicit path is supplied, the loader walks the filesystem
    upward from the current working directory, inspecting each directory
    for ``zen-config.yaml``. The walk stops at the first directory that
    contains a ``pyproject.toml`` (the project-root marker), even when no
    config file has been found yet. This prevents accidental reads from
    unrelated parent projects.

Merge semantics
    User-supplied YAML keys are shallow-merged over built-in defaults so
    that a minimal config (e.g. just ``severity_threshold: 3``) inherits
    every other default without the author having to repeat them.

Pipeline generation
    If the resolved config contains no ``pipelines`` section, the loader
    auto-generates one pipeline per declared language by projecting
    zen-principle rules through
    ``PipelineConfig.from_rules``.

See Also:
    ``PipelineConfig``: Per-language detector pipeline model.
    ``merge_pipeline_overrides``: Merges user overrides into rule-derived
        base pipelines by detector ``type``.
"""

import os

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig


class ConfigModel(BaseModel):
    """Root Pydantic model that holds every tunable knob for zen analysis.

    ``ConfigModel`` is the single source of truth produced by ``load_config``.
    Analyzers, the MCP server, and the CLI all receive a validated instance of
    this model—never a raw dictionary—so typos in YAML keys surface as
    ``ValidationError`` rather than silent mis-configuration.

    Attributes:
        languages: Ordered list of language identifiers that the analysis
            session will support.  Defaults to ten built-in languages
            (python, ruby, typescript, javascript, go, rust, bash,
            powershell, cpp, csharp).  Adding an entry here causes
            ``load_config`` to auto-generate a pipeline for the language
            when the ``pipelines`` section is absent.
        severity_threshold: Minimum severity score (1–10) a violation must
            reach to be included in analysis results.  Violations below
            this threshold are silently dropped.  Default is ``5``.
        pipelines: Per-language detector pipeline configurations.  Each
            entry pairs a language identifier with a list of
            ``DetectorConfig`` objects that control individual detectors.
            When the YAML file omits this key the loader auto-generates
            pipelines from zen-principle rules.

    Example YAML mapping::

        languages:
          - python
          - typescript
        severity_threshold: 3
        pipelines:
          - language: python
            detectors:
              - type: cyclomatic_complexity
                max_cyclomatic_complexity: 8

    Note:
        ``model_config = ConfigDict(extra="forbid")`` rejects unknown keys,
        turning YAML typos like ``severitythreshold`` into immediate
        validation errors instead of silently ignored fields.

    See Also:
        ``PipelineConfig``: Schema for individual pipeline entries.
        ``load_config``: Factory that discovers, parses, merges, and
            validates YAML into a ``ConfigModel`` instance.
    """

    model_config = ConfigDict(extra="forbid")
    languages: list[str] = Field(
        default_factory=lambda: [
            "python",
            "ruby",
            "typescript",
            "javascript",
            "go",
            "rust",
            "bash",
            "powershell",
            "cpp",
            "csharp",
        ]
    )
    severity_threshold: int = 5
    pipelines: list[PipelineConfig] = Field(default_factory=list)

    @field_validator("pipelines", mode="before")
    @classmethod
    def _validate_pipelines(cls, value: object) -> list[PipelineConfig]:
        """Coerce raw YAML sequences into validated ``PipelineConfig`` instances.

        Pydantic invokes this ``mode="before"`` validator before the field
        is assigned, giving it the untyped output of ``yaml.safe_load``—
        typically a ``list[dict]``.  Each dictionary is fed through
        ``PipelineConfig.model_validate``, which in turn validates nested
        detector entries via the detector registry.  A ``None`` value
        (absent key in YAML) is normalised to an empty list so downstream
        code never has to guard against ``None``.

        Args:
            value: Untyped data from the YAML parser—expected to be a
                ``list[dict]``, ``None`` (key absent), or any other type
                which will raise ``TypeError``.

        Returns:
            Validated list of ``PipelineConfig`` objects ready for
            pipeline resolution.  Returns an empty list when *value* is
            ``None``.

        Raises:
            TypeError: If *value* is neither ``None`` nor a ``list``.
            ValidationError: If any nested detector entry fails
                ``PipelineConfig.model_validate``.
        """

        if value is None:
            return []
        if not isinstance(value, list):
            msg = "pipelines must be a list"
            raise TypeError(msg)
        return [PipelineConfig.model_validate(item) for item in value]

    def pipeline_for(self, language: str) -> PipelineConfig:
        """Resolve the effective detector pipeline for a single language.

        Resolution follows a two-layer strategy:

        1. **Base layer** — ``PipelineConfig.from_rules(language)`` projects
           the language's zen principles into detector configs, producing a
           pipeline whose thresholds mirror the canonical rules.
        2. **Override layer** — if the user's ``pipelines`` list contains an
           entry whose ``language`` field matches, its detectors are merged
           on top of the base layer by detector ``type`` via
           ``merge_pipeline_overrides``.  Detectors present only in the
           base are kept unchanged; detectors present only in the override
           are appended.

        When no matching override exists the base pipeline is returned
        unmodified, ensuring every supported language always gets a
        complete detector configuration even with a minimal YAML file.

        Args:
            language: Case-sensitive language identifier (e.g. ``"python"``,
                ``"typescript"``).

        Returns:
            Fully resolved ``PipelineConfig`` with base detectors and any
            user overrides merged in.

        See Also:
            ``PipelineConfig.from_rules``: Builds the base pipeline from
                zen principles.
            ``merge_pipeline_overrides``: Performs the per-detector-type
                merge of base and override configs.
        """

        from mcp_zen_of_languages.analyzers.pipeline import merge_pipeline_overrides

        base = PipelineConfig.from_rules(language)
        for pipeline in self.pipelines:
            if pipeline.language == language:
                return merge_pipeline_overrides(base, pipeline)
        return base


def load_config(path: str | None = None) -> ConfigModel:
    """Discover, load, and validate ``zen-config.yaml`` into a ``ConfigModel``.

    The discovery algorithm searches for ``zen-config.yaml`` using a
    deterministic walk that balances convenience with safety:

    1. **Explicit path** — when *path* is supplied the file is read
       directly; no filesystem walk occurs.
    2. **CWD check** — ``Path.cwd() / "zen-config.yaml"`` is tried first.
    3. **Upward walk** — each parent directory is inspected in order.
       The walk halts as soon as a directory containing
       ``pyproject.toml`` is reached (the project-root marker), even if
       no config was found, preventing accidental reads from unrelated
       ancestor projects.

    Once a file is located the raw YAML is shallow-merged over the
    built-in defaults (``ConfigModel()``), so a minimal file that sets
    only ``severity_threshold: 3`` inherits every other default without
    repetition.

    If the merged config has an empty ``pipelines`` list, a pipeline is
    auto-generated for each language in ``languages`` by calling
    ``PipelineConfig.from_rules``, guaranteeing that every declared
    language ships with a complete detector configuration.

    Args:
        path: Filesystem path to ``zen-config.yaml``.  Pass ``None``
            (the default) to activate auto-discovery.

    Returns:
        Validated ``ConfigModel`` reflecting the merged configuration.
        Returns a default ``ConfigModel`` when no config file is found
        anywhere on the search path.

    Raises:
        yaml.YAMLError: If the file contains invalid YAML syntax.
        ValidationError: If merged values violate ``ConfigModel``
            constraints (e.g. unknown keys due to ``extra="forbid"``).

    Examples:
        Explicit path::

            cfg = load_config("/repo/zen-config.yaml")

        Auto-discovery from CWD::

            cfg = load_config()  # walks CWD → parents → pyproject.toml

    See Also:
        ``ConfigModel``: The Pydantic model returned by this function.
        ``PipelineConfig.from_rules``: Generates pipelines when
            ``pipelines`` is empty.
    """
    from pathlib import Path

    default = ConfigModel()

    # Auto-discover config if no path provided
    if not path:
        cwd_config = Path.cwd() / "zen-config.yaml"
        if cwd_config.exists():
            path = str(cwd_config)
        else:
            # Try to find project root by looking for pyproject.toml
            current = Path.cwd()
            for parent in [current, *current.parents]:
                candidate = parent / "zen-config.yaml"
                if candidate.exists():
                    path = str(candidate)
                    break
                # Stop at project root marker
                if (parent / "pyproject.toml").exists():
                    break

    if not path:
        return default
    try:
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        merged = {**default.model_dump(), **data}
        env_severity_threshold = os.environ.get("ZEN_SEVERITY_THRESHOLD")
        if env_severity_threshold is not None:
            try:
                merged["severity_threshold"] = int(env_severity_threshold)
            except ValueError as exc:
                msg = (
                    "Environment variable ZEN_SEVERITY_THRESHOLD must be an integer "
                    f"between 1 and 10; got {env_severity_threshold!r}"
                )
                raise ValueError(msg) from exc
        cfg = ConfigModel.model_validate(merged)
        if not cfg.pipelines:
            cfg = cfg.model_copy(
                update={
                    "pipelines": [
                        PipelineConfig.from_rules(lang) for lang in cfg.languages
                    ]
                }
            )
    except FileNotFoundError:
        return default
    except Exception:
        raise
    else:
        return cfg
