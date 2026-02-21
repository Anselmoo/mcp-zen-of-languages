"""Generate docs/user-guide/languages/*.md from rules.py + DETECTOR_MAP.

Run::

    uv run python scripts/generate_language_docs.py          # write files
    uv run python scripts/generate_language_docs.py --check  # CI dry-run

The script imports ``LanguageZenPrinciples`` and ``LanguageDetectorMap``
for every supported language, then renders each documentation page from
the Jinja2 template at ``scripts/templates/language_page.md.j2``.
"""

from __future__ import annotations

import argparse
import importlib
import sys
import textwrap
from collections import Counter
from pathlib import Path

from generate_implementation_counts import (
    sync_implementation_counts,
    validate_documented_languages,
)
from jinja2 import Environment, FileSystemLoader

# Maximum characters shown from a principle description in diagram labels
PRINCIPLE_PREVIEW_LENGTH = 40

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "scripts" / "templates"
INTROS_DIR = TEMPLATES_DIR / "intros"
DOCS_DIR = ROOT / "docs" / "user-guide" / "languages"

# ---------------------------------------------------------------------------
# Language metadata
# ---------------------------------------------------------------------------
# module_key, language_name, mkdocs_icon, docs_filename, config_key
LANGUAGES: list[tuple[str, str, str, str, str]] = [
    ("python", "Python", "fontawesome/brands/python", "python.md", "python"),
    (
        "typescript",
        "TypeScript",
        "material/language-typescript",
        "typescript.md",
        "typescript",
    ),
    ("rust", "Rust", "material/language-rust", "rust.md", "rust"),
    ("go", "Go", "material/language-go", "go.md", "go"),
    (
        "javascript",
        "JavaScript",
        "fontawesome/brands/js",
        "javascript.md",
        "javascript",
    ),
    ("css", "CSS", "material/language-css3", "css.md", "css"),
    ("bash", "Bash", "material/console", "bash.md", "bash"),
    (
        "powershell",
        "PowerShell",
        "material/console-line",
        "powershell.md",
        "powershell",
    ),
    ("ruby", "Ruby", "material/language-ruby", "ruby.md", "ruby"),
    ("sql", "SQL", "material/database", "sql.md", "sql"),
    ("cpp", "C++", "material/language-cpp", "cpp.md", "cpp"),
    ("csharp", "C#", "material/language-csharp", "csharp.md", "csharp"),
    (
        "docker_compose",
        "Docker Compose",
        "material/docker",
        "docker-compose.md",
        "docker_compose",
    ),
    ("dockerfile", "Dockerfile", "material/docker", "dockerfile.md", "dockerfile"),
    ("latex", "LaTeX", "material/math-integral", "latex.md", "latex"),
    (
        "markdown",
        "Markdown / MDX",
        "material/language-markdown",
        "markdown.md",
        "markdown",
    ),
]

WORKFLOW_LANGUAGES: list[tuple[str, str, str]] = [
    ("github_actions", "GitHub Actions", "github-actions.md"),
]

CONFIG_LANGUAGES: list[tuple[str, str]] = [
    ("json", "JSON"),
    ("toml", "TOML"),
    ("xml", "XML"),
    ("yaml", "YAML"),
]

# ---------------------------------------------------------------------------
# See-Also blocks (hand-curated cross-references per language)
# ---------------------------------------------------------------------------
SEE_ALSO: dict[str, str] = {
    "python": (
        "- [Configuration](../configuration.md) — Full config reference and override strategies\n"
        "- [Understanding Violations](../understanding-violations.md) — How to interpret severity scores\n"
        "- [Prompt Generation](../prompt-generation.md) — Generate AI remediation prompts from violations"
    ),
    "typescript": (
        "- [JavaScript](javascript.md) — Related principles for JS codebases\n"
        "- [Configuration](../configuration.md) — Per-language pipeline overrides\n"
        "- [Understanding Violations](../understanding-violations.md) — Severity scale reference"
    ),
    "rust": (
        "- [C++](cpp.md) — Systems programming counterpart with different safety models\n"
        "- [Configuration](../configuration.md) — Per-language pipeline overrides\n"
        "- [Understanding Violations](../understanding-violations.md) — Severity scale reference"
    ),
    "go": (
        "- [Rust](rust.md) — Complementary systems language with ownership model\n"
        "- [Configuration](../configuration.md) — Per-language pipeline overrides\n"
        "- [Understanding Violations](../understanding-violations.md) — Severity scale reference"
    ),
    "javascript": (
        "- [TypeScript](typescript.md) — Type-safe superset with additional principles\n"
        "- [Configuration](../configuration.md) — Per-language pipeline overrides\n"
        "- [Understanding Violations](../understanding-violations.md) — Severity scale reference"
    ),
    "css": (
        "- [JavaScript](javascript.md) — Common frontend codebase counterpart\n"
        "- [TypeScript](typescript.md) — Strongly-typed frontend language companion\n"
        "- [Configuration](../configuration.md) — Per-language pipeline overrides"
    ),
    "bash": (
        "- [PowerShell](powershell.md) — Object-pipeline shell with different idioms\n"
        "- [Configuration](../configuration.md) — Per-language pipeline overrides\n"
        "- [Understanding Violations](../understanding-violations.md) — Severity scale reference"
    ),
    "powershell": (
        "- [Bash](bash.md) — POSIX shell scripting counterpart\n"
        "- [Configuration](../configuration.md) — Per-language pipeline overrides\n"
        "- [Understanding Violations](../understanding-violations.md) — Severity scale reference"
    ),
    "ruby": (
        "- [Python](python.md) — Dynamic language with similar expressiveness goals\n"
        "- [Configuration](../configuration.md) — Per-language pipeline overrides\n"
        "- [Understanding Violations](../understanding-violations.md) — Severity scale reference"
    ),
    "sql": (
        "- [Configuration](../configuration.md) — Per-language pipeline overrides\n"
        "- [Understanding Violations](../understanding-violations.md) — Severity scale reference\n"
        "- [Prompt Generation](../prompt-generation.md) — Generate SQL remediation guidance"
    ),
    "cpp": (
        "- [Rust](rust.md) — Memory-safe systems language with compile-time guarantees\n"
        "- [C#](csharp.md) — Managed C-family language with different safety model\n"
        "- [Configuration](../configuration.md) — Per-language pipeline overrides"
    ),
    "csharp": (
        "- [C++](cpp.md) — Unmanaged C-family counterpart\n"
        "- [TypeScript](typescript.md) — Another strongly-typed language with similar patterns\n"
        "- [Configuration](../configuration.md) — Per-language pipeline overrides"
    ),
    "markdown": (
        "- [Config Formats](config-formats.md) — Principles for JSON, TOML, XML, and YAML\n"
        "- [Configuration](../configuration.md) — Per-language pipeline overrides\n"
        "- [Understanding Violations](../understanding-violations.md) — Severity scale reference"
    ),
    "latex": (
        "- [Configuration](../configuration.md) — Per-language pipeline overrides\n"
        "- [Understanding Violations](../understanding-violations.md) — Severity scale reference\n"
        "- [Prompt Generation](../prompt-generation.md) — Generate AI remediation prompts"
    ),
}

# Config tips per language
CONFIG_TIPS: dict[str, str] = {
    "python": (
        '???+ tip "Start relaxed, tighten over time"\n'
        "    For legacy codebases, start with `max_cyclomatic_complexity: 15` and "
        "`max_function_length: 80`, then lower thresholds as you remediate."
    ),
    "typescript": (
        '???+ tip "Migrating from JavaScript?"\n'
        "    Start with `max_any_count: 10` and lower it sprint by sprint. Use the "
        "`ts-010` detector to find `any` that should be `unknown` first — those are the safest to fix."
    ),
}


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------
def _load_zen(module_key: str):
    """Import LanguageZenPrinciples for a language."""
    mod = importlib.import_module(f"mcp_zen_of_languages.languages.{module_key}.rules")
    # Convention: the module-level constant is *_ZEN (e.g. PYTHON_ZEN)
    for attr in dir(mod):
        obj = getattr(mod, attr)
        if hasattr(obj, "principles") and hasattr(obj, "language"):
            return obj
    msg = f"No LanguageZenPrinciples found in {module_key}.rules"
    raise RuntimeError(msg)


def _load_detector_map(module_key: str):
    """Import DETECTOR_MAP for a language."""
    mod = importlib.import_module(
        f"mcp_zen_of_languages.languages.{module_key}.mapping",
    )
    return mod.DETECTOR_MAP


def _load_intro(module_key: str) -> str:
    """Load editorial intro from intros/{lang}.md or generate a fallback."""
    intro_path = INTROS_DIR / f"{module_key}.md"
    return intro_path.read_text().strip() if intro_path.exists() else ""


def _validate_language_inventory() -> None:
    """Ensure docs generator language inventories match canonical registry keys."""
    validate_documented_languages(
        {
            *(module_key for module_key, *_ in LANGUAGES),
            *(module_key for module_key, *_ in WORKFLOW_LANGUAGES),
            *(module_key for module_key, _ in CONFIG_LANGUAGES),
        },
    )


def _detector_first_line(detector_cls: type) -> str:
    """Extract the first meaningful sentence from a detector's docstring."""
    doc = detector_cls.__doc__ or ""
    # Take first non-empty line
    for line in doc.strip().splitlines():
        if line := line.strip():
            # Remove trailing period for table consistency, then re-add
            return line.rstrip(".")
    return "Detects violations"


def _build_category_label(cat: str) -> str:
    """Convert enum value like 'error_handling' to 'Error Handling'."""
    return cat.replace("_", " ").title()


# ---------------------------------------------------------------------------
# Mermaid diagram generation
# ---------------------------------------------------------------------------
def _build_mermaid(principles, detector_map) -> str:
    """Build a mermaid graph LR showing principle→detector wiring."""
    lines = ["    graph LR"]

    # Build rule_id → principle label mapping
    rule_labels: dict[str, str] = {}
    for p in principles:
        safe_id = p.id.replace("-", "_")
        short = p.principle[:PRINCIPLE_PREVIEW_LENGTH] + (
            "..." if len(p.principle) > PRINCIPLE_PREVIEW_LENGTH else ""
        )
        lines.append(f'    {safe_id}["{p.id}<br/>{short}"]')
        rule_labels[p.id] = safe_id

    # Build detector nodes and edges (sorted for deterministic output)
    seen_detectors: list[str] = []
    for binding in sorted(
        detector_map.bindings,
        key=lambda b: b.detector_class.__name__,
    ):
        det_name = binding.detector_class.__name__
        if det_name in seen_detectors:
            continue
        seen_detectors.append(det_name)
        det_id = f"det_{det_name}"
        lines.append(f'    {det_id}["{det_name}"]')
        lines.extend(
            [
                f"    {rule_labels[rid]} --> {det_id}"
                for rid in sorted(binding.rule_ids)
                if rid in rule_labels
            ],
        )

    lines.extend(
        (
            "    classDef principle fill:#4051b5,color:#fff,stroke:none",
            "    classDef detector fill:#26a269,color:#fff,stroke:none",
        ),
    )
    for p in principles:
        safe_id = p.id.replace("-", "_")
        lines.append(f"    class {safe_id} principle")
    lines.extend(f"    class det_{det_name} detector" for det_name in seen_detectors)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Config block generation
# ---------------------------------------------------------------------------
def _build_config_entries(_principles, detector_map) -> list[dict]:
    """Build config YAML entries from metrics and detector bindings."""
    entries: list[dict] = []
    seen_types: set[str] = set()

    for binding in detector_map.bindings:
        det_id = binding.detector_id
        if det_id in seen_types or det_id == "analyzer_defaults":
            continue
        seen_types.add(det_id)

        # Get default values from config model
        config_cls = binding.config_model
        params: dict[str, object] = {}
        comments: dict[str, str] = {}

        for field_name, field_info in config_cls.model_fields.items():
            if field_name in ("type", "enabled"):
                continue
            default = field_info.default
            if default is not None:
                params[field_name] = default
                if desc := field_info.description:
                    comments[field_name] = desc[:60]

        if params:
            # Convert detector_id to kebab-case for YAML
            yaml_type = det_id.replace("_", "-")
            entries.append(
                {
                    "type": yaml_type,
                    "params": params,
                    "comments": comments,
                },
            )

    return entries


# ---------------------------------------------------------------------------
# Detector grouping
# ---------------------------------------------------------------------------
def _group_detectors(principles, detector_map) -> list[tuple[str, list[dict]]]:
    """Group detectors by PrincipleCategory."""
    rule_to_category: dict[str, str] = {
        p.id: _build_category_label(p.category) for p in principles
    }
    # Group bindings by their primary category
    groups: dict[str, list[dict]] = {}
    seen: set[str] = set()
    for binding in detector_map.bindings:
        det_name = binding.detector_class.__name__
        if det_name in seen or binding.detector_id == "analyzer_defaults":
            continue
        seen.add(det_name)

        category = next(
            (
                rule_to_category[rid]
                for rid in binding.rule_ids
                if rid in rule_to_category
            ),
            "General",
        )
        desc = _detector_first_line(binding.detector_class)
        entry = {
            "name": det_name,
            "description": desc,
            "rule_ids": binding.rule_ids or [],
        }
        groups.setdefault(category, []).append(entry)

    return sorted(groups.items())


# ---------------------------------------------------------------------------
# Principle data preparation
# ---------------------------------------------------------------------------
def _prepare_principle(p) -> dict:
    """Convert a ZenPrinciple to a template-friendly dict."""
    violations = []
    for v in p.violations:
        if hasattr(v, "description"):
            violations.append(v.description)
        else:
            violations.append(str(v))

    return {
        "id": p.id,
        "principle": p.principle,
        "category": _build_category_label(p.category),
        "severity": p.severity,
        "description": p.description,
        "violations": violations,
        "detectable_patterns": p.detectable_patterns or [],
        "metrics": p.metrics or {},
        "recommended_alternative": p.recommended_alternative,
    }


# ---------------------------------------------------------------------------
# Main rendering
# ---------------------------------------------------------------------------
def render_language_page(
    module_key: str,
    language_name: str,
    icon: str,
    config_key: str,
    env: Environment,
) -> str:
    """Render a single language documentation page."""
    zen = _load_zen(module_key)
    detector_map = _load_detector_map(module_key)

    principles = [_prepare_principle(p) for p in zen.principles]
    detector_groups = _group_detectors(zen.principles, detector_map)
    config_entries = _build_config_entries(zen.principles, detector_map)
    mermaid = _build_mermaid(zen.principles, detector_map)

    # Category summary
    cat_counter: Counter[str] = Counter()
    for p in zen.principles:
        cat_counter[_build_category_label(p.category)] += 1
    category_summary = sorted(cat_counter.items())

    num_detectors = len(
        {
            b.detector_class.__name__
            for b in detector_map.bindings
            if b.detector_id != "analyzer_defaults"
        },
    )

    intro = _load_intro(module_key)
    see_also = SEE_ALSO.get(
        module_key,
        (
            "- [Configuration](../configuration.md) — Per-language pipeline overrides\n"
            "- [Understanding Violations](../understanding-violations.md) — Severity scale reference"
        ),
    )
    config_tip = CONFIG_TIPS.get(module_key, "")

    template = env.get_template("language_page.md.j2")
    return template.render(
        language_name=language_name,
        language_key=config_key,
        icon=icon,
        intro=intro,
        philosophy=zen.philosophy if hasattr(zen, "philosophy") else "",
        source_text=zen.source_text if hasattr(zen, "source_text") else "",
        source_url=str(zen.source_url) if hasattr(zen, "source_url") else "",
        num_principles=len(zen.principles),
        num_detectors=num_detectors,
        num_categories=len(category_summary),
        category_summary=category_summary,
        principles=principles,
        detector_groups=detector_groups,
        config_entries=config_entries,
        config_tip=config_tip,
        mermaid_diagram=mermaid,
        see_also=see_also,
    )


def render_config_formats_page(_env: Environment) -> str:  # noqa: C901
    """Render the config-formats.md page for JSON/TOML/XML/YAML."""
    sections: list[str] = [
        textwrap.dedent(
            """\
        ---
        title: Config Formats
        description: "Zen principles across JSON, TOML, XML, and YAML enforced by dedicated detectors for data format consistency and correctness."
        icon: material/code-json
        tags:
          - JSON
          - TOML
          - XML
          - YAML
        ---

        # Configuration Formats

        Configuration files are code too — they're read by humans, versioned in git, and debugged at 2am during outages. MCP Zen of Languages analyzes four data formats with dedicated detectors for each.
    """,
        ),
    ]

    for module_key, display_name in CONFIG_LANGUAGES:
        zen = _load_zen(module_key)
        detector_map = _load_detector_map(module_key)

        principles = [_prepare_principle(p) for p in zen.principles]
        num_detectors = len(
            {
                b.detector_class.__name__
                for b in detector_map.bindings
                if b.detector_id != "analyzer_defaults"
            },
        )

        section = f"## {display_name} — {len(zen.principles)} Principles, {num_detectors} Detectors\n\n"

        # Principles table
        section += "| Rule ID | Principle | Category | Severity |\n"
        section += "|---------|-----------|----------|:--------:|\n"
        for p in principles:
            section += f"| `{p['id']}` | {p['principle']} | {p['category']} | {p['severity']} |\n"
        section += "\n"

        # Expandable details
        for p in principles:
            section += f'??? info "`{p["id"]}` — {p["principle"]}"\n'
            section += f"    **{p['description']}**\n\n"
            if p["violations"]:
                section += "    **Common Violations:**\n\n"
                for v in p["violations"]:
                    section += f"    - {v}\n"
                section += "\n"
            if p["detectable_patterns"]:
                section += "    **Detectable Patterns:**\n\n"
                for pat in p["detectable_patterns"]:
                    section += f"    - `{pat}`\n"
                section += "\n"
            if p["metrics"]:
                section += "    **Thresholds:**\n\n"
                section += "    | Parameter | Default |\n"
                section += "    |-----------|---------|\n"
                for key, val in p["metrics"].items():
                    section += f"    | `{key}` | `{val}` |\n"
                section += "\n"
            if p["recommended_alternative"]:
                section += '    !!! tip "Recommended Fix"\n'
                section += f"        {p['recommended_alternative']}\n\n"

        # Detector table
        section += "| Detector | What It Catches |\n"
        section += "|----------|-----------------|\n"
        for binding in detector_map.bindings:
            if binding.detector_id == "analyzer_defaults":
                continue
            det_name = binding.detector_class.__name__
            desc = _detector_first_line(binding.detector_class)
            section += f"| **{det_name}** | {desc} |\n"
        section += "\n---\n\n"

        sections.append(section)

    # See Also
    sections.append(
        "## See Also\n\n"
        "- [Configuration](../configuration.md) — Per-language pipeline overrides\n"
        "- [Understanding Violations](../understanding-violations.md) — Severity scale reference\n",
    )

    return "\n".join(sections)


def render_index_page() -> str:
    """Render the index.md 'At a Glance' page from live data."""
    programming_rows: list[tuple[str, str, int, int, str, str, str]] = []
    workflow_rows: list[tuple[str, str, int, int, str, str, str]] = []

    for module_key, lang_name, _icon, filename, _config_key in LANGUAGES:
        zen = _load_zen(module_key)
        detector_map = _load_detector_map(module_key)
        num_detectors = len(
            {
                b.detector_class.__name__
                for b in detector_map.bindings
                if b.detector_id != "analyzer_defaults"
            },
        )
        parser = (
            "AST"
            if module_key == "python"
            else "SQLGlot"
            if module_key == "sql"
            else "Regex"
        )
        philosophy = zen.source_text if hasattr(zen, "source_text") else ""
        source_url = str(zen.source_url) if hasattr(zen, "source_url") else ""
        programming_rows.append(
            (
                lang_name,
                filename,
                len(zen.principles),
                num_detectors,
                parser,
                philosophy,
                source_url,
            ),
        )

    for module_key, workflow_name, filename in WORKFLOW_LANGUAGES:
        zen = _load_zen(module_key)
        workflow_checks = len(zen.principles)
        philosophy = zen.source_text if hasattr(zen, "source_text") else ""
        source_url = str(zen.source_url) if hasattr(zen, "source_url") else ""
        workflow_rows.append(
            (
                workflow_name,
                filename,
                len(zen.principles),
                workflow_checks,
                "YAML",
                philosophy,
                source_url,
            ),
        )

    # Config formats (aggregated)
    config_total_p = 0
    config_total_d = 0
    config_parts: list[str] = []
    for module_key, display_name in CONFIG_LANGUAGES:
        zen = _load_zen(module_key)
        detector_map = _load_detector_map(module_key)
        num_det = len(
            {
                b.detector_class.__name__
                for b in detector_map.bindings
                if b.detector_id != "analyzer_defaults"
            },
        )
        config_total_p += len(zen.principles)
        config_total_d += num_det
        config_parts.append(f"{display_name} ({len(zen.principles)})")

    programming_total_p = sum(r[2] for r in programming_rows)
    programming_total_d = sum(r[3] for r in programming_rows)
    workflow_total_p = sum(r[2] for r in workflow_rows)
    workflow_total_checks = sum(r[3] for r in workflow_rows)

    grand_p = programming_total_p + workflow_total_p + config_total_p
    grand_coverage = programming_total_d + workflow_total_checks + config_total_d

    page = textwrap.dedent("""\
        ---
        title: Languages
        description: Supported languages, maturity tiers, zen principles, and detector coverage across all supported languages.
        icon: material/translate
        tags:
          - CLI
          - Configuration
        ---

        # Languages

        Every language has its own philosophy — its own sense of what "good code" means. MCP Zen of Languages encodes these philosophies as **zen principles**: opinionated, idiomatic best practices drawn from each language's community wisdom. Each principle maps to one or more **detectors** that find violations in your code.

        ## At a Glance

        ### Programming Languages

        | Language | Principles | Detectors | Parser | Philosophy Origin |
        |----------|:----------:|:---------:|--------|-------------------|
    """)

    for (
        lang_name,
        filename,
        num_p,
        num_d,
        parser,
        philosophy,
        source_url,
    ) in programming_rows:
        origin = (
            f"[{philosophy}]({source_url})" if philosophy and source_url else philosophy
        )
        page += (
            f"| [{lang_name}]({filename}) | {num_p} | {num_d} | {parser} | {origin} |\n"
        )
    page += f"| **Programming subtotal** | **{programming_total_p}** | **{programming_total_d}** | | |\n"

    page += "\n### Workflows & Automation\n\n"
    page += "| Language | Principles | Workflow Checks | Parser | Philosophy Origin |\n"
    page += "|----------|:----------:|:---------------:|--------|-------------------|\n"
    for (
        workflow_name,
        filename,
        num_p,
        num_checks,
        parser,
        philosophy,
        source_url,
    ) in workflow_rows:
        origin = (
            f"[{philosophy}]({source_url})" if philosophy and source_url else philosophy
        )
        page += f"| [{workflow_name}]({filename}) | {num_p} | {num_checks} | {parser} | {origin} |\n"
    page += f"| **Workflows subtotal** | **{workflow_total_p}** | **{workflow_total_checks}** | | |\n"

    config_detail = ", ".join(config_parts)
    page += "\n### Config Formats\n\n"
    page += (
        "| Language Family | Principles | Detectors | Parser | Coverage Breakdown |\n"
    )
    page += (
        "|-----------------|:----------:|:---------:|--------|--------------------|\n"
    )
    page += f"| [Config formats](config-formats.md) | {config_total_p} | {config_total_d} | Regex | {config_detail} |\n"
    page += (
        f"| **Config subtotal** | **{config_total_p}** | **{config_total_d}** | | |\n"
    )

    page += (
        "\n### Coverage Totals\n\n"
        f"- **Principles (all categories):** {grand_p}\n"
        f"- **Detectors + workflow checks:** {grand_coverage}\n"
    )

    page += textwrap.dedent("""
        ## Maturity Tiers

        <div class="grid cards" markdown>

        -   :material-check-all:{ .lg .middle } **Full Analysis**

            ---

            AST parsing, cyclomatic complexity, dependency graphs, maintainability index. The deepest analysis available.

            **Python**

        -   :material-shield-check:{ .lg .middle } **Rule-Driven**

            ---

            Dedicated detectors with regex-based pattern matching. Each rule has its own detector class with configurable thresholds.

            **TypeScript · Rust · Go · JavaScript · Bash · PowerShell · Ruby · SQL · C++ · C# · Docker Compose · Dockerfile · LaTeX**

        -   :material-source-branch:{ .lg .middle } **Workflow Automation**

            ---

            CI/CD-specific security and maintainability checks for pipeline files and reusable workflow patterns.

            **GitHub Actions**

        -   :material-file-cog:{ .lg .middle } **Config Validation**

            ---

            Schema and structure-focused detectors for data formats. Checks consistency, naming conventions, and format-specific best practices.

            **JSON · TOML · XML · YAML**

        </div>

        !!! info "All tiers use real detectors"
            Every language listed above has **fully implemented detectors** — there are no stubs or placeholders. The tier difference reflects parser depth (AST vs regex), not implementation completeness.

        ## How Principles Work

        Each zen principle has four key attributes:

        - **Rule ID** — A stable identifier like `python-003` or `rust-008` used in configuration and reports
        - **Category** — Groups related principles (e.g., `ERROR_HANDLING`, `TYPE_SAFETY`, `IDIOMS`)
        - **Severity** — A 1-10 score indicating how critical violations are (9-10 = critical, 1-3 = informational)
        - **Detectors** — One or more detector classes that find violations of this principle in your code

        You can tune severity thresholds and detector parameters per-language in your [`zen-config.yaml`](../configuration.md).

        ## Choosing Your Starting Language

        === "Already using Python?"
            Start with [Python](python.md) — it has the deepest analysis (AST parsing, cyclomatic complexity, dependency graphs) and detectors covering everything from naming style to god classes.

        === "TypeScript or JavaScript project?"
            Start with [TypeScript](typescript.md) for type-safety focus, or [JavaScript](javascript.md) for modern patterns. Both detect common pitfalls in frontend and Node.js codebases.

        === "Systems programming?"
            [Rust](rust.md) focuses on ownership and safety idioms. [C++](cpp.md) enforces modern C++ practices (smart pointers, RAII, const-correctness). [Go](go.md) encodes Effective Go principles.

        === "Scripting and automation?"
            [Bash](bash.md) and [PowerShell](powershell.md) catch the shell-scripting antipatterns that cause outages — unquoted variables, missing error handling, eval injection.

        === "CI automation?"
            [GitHub Actions](github-actions.md) focuses on workflow hardening: pinning actions, permission scoping, secret safety, and pipeline maintainability.

        === "Config files?"
            The [config formats](config-formats.md) page covers JSON, TOML, XML, and YAML — consistency checks, naming conventions, and format-specific best practices.

        ## Programmatic Access

        ::: mcp_zen_of_languages.rules.get_all_languages

        ::: mcp_zen_of_languages.rules.get_language_zen
    """)

    return page


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:  # noqa: C901, PLR0912, PLR0915
    parser = argparse.ArgumentParser(
        description="Generate language documentation pages from rules.py data.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry-run: exit non-zero if any file would change.",
    )
    parser.add_argument(
        "--lang",
        type=str,
        default=None,
        help="Generate for a single language (e.g. 'python').",
    )
    args = parser.parse_args()
    _validate_language_inventory()

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    changed: list[str] = []

    # Determine which languages to process
    langs_to_process = LANGUAGES
    if args.lang:
        langs_to_process = [
            lang_cfg for lang_cfg in LANGUAGES if lang_cfg[0] == args.lang
        ]
        if not langs_to_process and args.lang not in dict(CONFIG_LANGUAGES):
            print(f"Unknown language: {args.lang}")
            return 1

    # Render language pages
    for module_key, lang_name, icon, filename, config_key in langs_to_process:
        output = render_language_page(module_key, lang_name, icon, config_key, env)
        out_path = DOCS_DIR / filename

        if args.check:
            if not out_path.exists() or out_path.read_text() != output:
                changed.append(str(out_path))
                print(f"STALE: {out_path}")
        else:
            out_path.write_text(output)
            print(f"  wrote {out_path}")

    # Render config-formats page
    if not args.lang or args.lang in dict(CONFIG_LANGUAGES):
        output = render_config_formats_page(env)
        out_path = DOCS_DIR / "config-formats.md"
        if args.check:
            if not out_path.exists() or out_path.read_text() != output:
                changed.append(str(out_path))
                print(f"STALE: {out_path}")
        else:
            out_path.write_text(output)
            print(f"  wrote {out_path}")

    # Render index page
    if not args.lang:
        output = render_index_page()
        out_path = DOCS_DIR / "index.md"
        if args.check:
            if not out_path.exists() or out_path.read_text() != output:
                changed.append(str(out_path))
                print(f"STALE: {out_path}")
        else:
            out_path.write_text(output)
            print(f"  wrote {out_path}")

    if args.check:
        if sync_implementation_counts(check=True) != 0:
            changed.append("implementation-count-surfaces")
    else:
        sync_implementation_counts(check=False)

    if args.check and changed:
        print(f"\n{len(changed)} file(s) are stale. Run:")
        print("  uv run python scripts/generate_language_docs.py")
        return 1

    if not args.check:
        total = len(langs_to_process) + (0 if args.lang else 1) + 1
        print(f"\nGenerated {total} documentation pages.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
