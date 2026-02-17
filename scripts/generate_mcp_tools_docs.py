"""Generate docs/user-guide/mcp-tools-reference.md from the live MCP server.

Run::

    uv run python scripts/generate_mcp_tools_docs.py          # write file
    uv run python scripts/generate_mcp_tools_docs.py --check   # CI dry-run

The script imports the FastMCP server instance from ``server.py``, inspects
every registered tool, resource, and prompt, and renders a comprehensive
reference page at ``docs/user-guide/mcp-tools-reference.md``.

This ensures documentation never drifts from the actual server surface.
"""

from __future__ import annotations

import argparse
import inspect
import sys
import textwrap
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs" / "user-guide"
OUTPUT_FILE = DOCS_DIR / "mcp-tools-reference.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_first_paragraph(docstring: str | None) -> str:
    """Extract the first paragraph from a docstring."""
    if not docstring:
        return ""
    lines: list[str] = []
    for line in textwrap.dedent(docstring).strip().splitlines():
        stripped = line.strip()
        if not stripped and lines:
            break
        if stripped:
            lines.append(stripped)
    return " ".join(lines)


def _extract_args_section(docstring: str | None) -> list[tuple[str, str]]:
    """Extract (param_name, description) pairs from the Args section."""
    if not docstring:
        return []
    in_args = False
    params: list[tuple[str, str]] = []
    current_name = ""
    current_desc_lines: list[str] = []

    for line in textwrap.dedent(docstring).strip().splitlines():
        stripped = line.strip()
        if stripped.startswith("Args:"):
            in_args = True
            continue
        if in_args:
            # New section header (Returns:, Raises:, etc.)
            if (
                stripped
                and not stripped.startswith("-")
                and stripped.endswith(":")
                and "(" not in stripped
            ):
                # Flush last param
                if current_name:
                    params.append((current_name, " ".join(current_desc_lines).strip()))
                break
            # Param line: "name (type): description"
            if "(" in stripped and "):" in stripped:
                # Flush previous
                if current_name:
                    params.append((current_name, " ".join(current_desc_lines).strip()))
                paren_idx = stripped.index("(")
                current_name = stripped[:paren_idx].strip()
                colon_idx = stripped.index("):")
                current_desc_lines = [stripped[colon_idx + 2 :].strip()]
            elif stripped and current_name:
                # Continuation line
                current_desc_lines.append(stripped)
    # Flush last
    if current_name:
        params.append((current_name, " ".join(current_desc_lines).strip()))
    # Deduplicate by param name (keep first occurrence)
    seen: set[str] = set()
    deduped: list[tuple[str, str]] = []
    for name, desc in params:
        if name not in seen:
            seen.add(name)
            deduped.append((name, desc))
    return deduped


def _extract_returns_section(docstring: str | None) -> str:
    """Extract the Returns section text."""
    if not docstring:
        return ""
    in_returns = False
    lines: list[str] = []
    for line in textwrap.dedent(docstring).strip().splitlines():
        stripped = line.strip()
        if stripped.startswith("Returns:"):
            in_returns = True
            continue
        if in_returns:
            if (
                stripped
                and not stripped.startswith("-")
                and stripped.endswith(":")
                and "(" not in stripped
            ):
                break
            if stripped:
                lines.append(stripped)
    return " ".join(lines).strip()


def _tag_badges(tags: set[str] | None) -> str:
    """Render tags as inline badges."""
    if not tags:
        return ""
    return " ".join(f'<span class="md-tag">{t}</span>' for t in sorted(tags))


def _annotation_label(annotations: object | None) -> str:
    """Return a human label from ToolAnnotations."""
    if annotations is None:
        return ""
    read_only = getattr(annotations, "readOnlyHint", None)
    destructive = getattr(annotations, "destructiveHint", None)
    if read_only:
        return ':material-eye-outline:{ title="Read-only" } Read-only'
    if destructive:
        return ':material-pencil-outline:{ title="Mutating" } Mutating'
    return ""


# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------


def generate() -> str:
    """Generate the full markdown content from the live server."""
    # Import server to get tool/resource/prompt registrations
    from mcp_zen_of_languages.server import mcp

    sections: list[str] = []

    # --- Frontmatter ---
    sections.append(
        textwrap.dedent("""\
        ---
        title: MCP Tools Reference
        description: Auto-generated reference of all MCP tools, resources, and prompts exposed by the zen server.
        icon: material/api
        tags:
          - MCP
          - API
          - Reference
        ---

        # MCP Tools Reference

        > **Auto-generated** from [`server.py`](https://github.com/Anselmoo/mcp-zen-of-languages/blob/main/src/mcp_zen_of_languages/server.py). Do not edit manually.
        >
        > Regenerate with: `uv run python scripts/generate_mcp_tools_docs.py`

        The MCP server exposes **tools**, **resources**, and **prompts** that AI agents
        and IDE integrations can invoke via the
        [Model Context Protocol](https://modelcontextprotocol.io/).
    """)
    )

    # --- Summary table ---
    tool_manager = mcp._tool_manager
    resource_manager = mcp._resource_manager
    prompt_manager = mcp._prompt_manager

    tools = (
        list(tool_manager._tools.values()) if hasattr(tool_manager, "_tools") else []
    )
    resources = (
        list(resource_manager._resources.values())
        if hasattr(resource_manager, "_resources")
        else []
    )
    # Include resource templates (e.g. zen://rules/{language})
    resource_templates = (
        list(resource_manager._templates.values())
        if hasattr(resource_manager, "_templates")
        else []
    )
    prompts = (
        list(prompt_manager._prompts.values())
        if hasattr(prompt_manager, "_prompts")
        else []
    )

    sections.append(
        textwrap.dedent(f"""\
        ## Surface Summary

        | Capability | Count |
        |------------|:-----:|
        | **Tools**  | {len(tools)} |
        | **Resources** | {len(resources) + len(resource_templates)} |
        | **Prompts** | {len(prompts)} |
    """)
    )

    # --- Categorize tools ---
    TOOL_FAMILIES = {
        "Reporting": {
            "prompts",
            "remediation",
            "reporting",
            "agent",
            "tasks",
            "automation",
        },
        "Analysis": {"analysis", "zen", "snippet", "repository", "patterns"},
        "Configuration": {"config", "settings"},
        "Metadata": {"metadata", "languages", "mapping"},
        "Onboarding": {"onboarding", "setup"},
    }

    def _classify(tool_tags: set[str] | None) -> str:
        if not tool_tags:
            return "Other"
        for family, keywords in TOOL_FAMILIES.items():
            if tool_tags & keywords:
                return family
        return "Other"

    family_tools: dict[str, list] = {}
    for tool in tools:
        tags = getattr(tool, "tags", None) or set()
        family = _classify(tags)
        family_tools.setdefault(family, []).append(tool)

    # --- Quick reference table ---
    sections.append("## Quick Reference\n\n")
    sections.append("| Tool | Family | Description | Access |\n")
    sections.append("|------|--------|-------------|--------|\n")

    for family in [
        "Analysis",
        "Reporting",
        "Configuration",
        "Metadata",
        "Onboarding",
        "Other",
    ]:
        for tool in family_tools.get(family, []):
            name = getattr(tool, "name", "unknown")
            desc = getattr(tool, "description", "")
            annotations = getattr(tool, "annotations", None)
            access = _annotation_label(annotations) if annotations else ""
            sections.append(
                f"| [`{name}`](#{name.replace('_', '-')}) | {family} | {desc} | {access} |\n"
            )

    sections.append("\n")

    # --- Detailed tool sections ---
    FAMILY_ICONS = {
        "Analysis": ":material-magnify:",
        "Reporting": ":material-file-document-outline:",
        "Configuration": ":material-cog-outline:",
        "Metadata": ":material-tag-outline:",
        "Onboarding": ":material-school-outline:",
        "Other": ":material-dots-horizontal:",
    }

    for family in [
        "Analysis",
        "Reporting",
        "Configuration",
        "Metadata",
        "Onboarding",
        "Other",
    ]:
        family_list = family_tools.get(family, [])
        if not family_list:
            continue
        icon = FAMILY_ICONS.get(family, "")
        sections.append(f"## {icon} {family} Tools\n\n")

        for tool in family_list:
            name = getattr(tool, "name", "unknown")
            desc = getattr(tool, "description", "")
            tags = getattr(tool, "tags", None) or set()
            annotations = getattr(tool, "annotations", None)
            fn = getattr(tool, "fn", None)
            docstring = inspect.getdoc(fn) if fn else ""

            sections.append(f"### `{name}` {{ #{name.replace('_', '-')} }}\n\n")

            # Badges
            badge_parts: list[str] = []
            if annotations:
                badge_parts.append(_annotation_label(annotations))
            if tags:
                badge_parts.append(_tag_badges(tags))
            if badge_parts:
                sections.append(" ".join(badge_parts) + "\n\n")

            sections.append(f"{desc}\n\n")

            # Extended description from docstring
            first_para = _extract_first_paragraph(docstring)
            if first_para and first_para != desc:
                sections.append(f"{first_para}\n\n")

            # Parameters
            params = _extract_args_section(docstring)
            if params:
                sections.append("**Parameters:**\n\n")
                sections.append("| Parameter | Description |\n")
                sections.append("|-----------|-------------|\n")
                for pname, pdesc in params:
                    sections.append(f"| `{pname}` | {pdesc} |\n")
                sections.append("\n")

            # Returns
            returns = _extract_returns_section(docstring)
            if returns:
                sections.append(f"**Returns:** {returns}\n\n")

            sections.append("---\n\n")

    # --- Resources ---
    all_resources = list(resources) + list(resource_templates)
    if all_resources:
        sections.append("## :material-database-outline: Resources\n\n")
        sections.append(
            "MCP resources are read-only data endpoints that clients can subscribe to.\n\n"
        )
        sections.append("| URI | Name | Description |\n")
        sections.append("|-----|------|-------------|\n")
        for resource in all_resources:
            uri = getattr(resource, "uri", "") or getattr(resource, "uri_template", "")
            name = getattr(resource, "name", "")
            desc = getattr(resource, "description", "")
            sections.append(f"| `{uri}` | {name} | {desc} |\n")
        sections.append("\n")

        for resource in all_resources:
            uri = getattr(resource, "uri", "") or getattr(resource, "uri_template", "")
            name = getattr(resource, "name", "")
            desc = getattr(resource, "description", "")
            fn = getattr(resource, "fn", None)
            docstring = inspect.getdoc(fn) if fn else ""
            first_para = _extract_first_paragraph(docstring)

            sections.append(f"### `{uri}`\n\n")
            sections.append(f"{desc}\n\n")
            if first_para and first_para != desc:
                sections.append(f"{first_para}\n\n")
            sections.append("---\n\n")

    # --- Prompts ---
    if prompts:
        sections.append("## :material-chat-outline: Prompts\n\n")
        sections.append(
            "MCP prompts are pre-built templates that clients can render for user interaction.\n\n"
        )
        for prompt in prompts:
            name = getattr(prompt, "name", "")
            desc = getattr(prompt, "description", "")
            fn = getattr(prompt, "fn", None)
            docstring = inspect.getdoc(fn) if fn else ""
            first_para = _extract_first_paragraph(docstring)

            sections.append(f"### `{name}`\n\n")
            sections.append(f"{desc}\n\n")
            if first_para and first_para != desc:
                sections.append(f"{first_para}\n\n")

            # Extract params
            params = _extract_args_section(docstring)
            if params:
                sections.append("**Parameters:**\n\n")
                for pname, pdesc in params:
                    sections.append(f"- `{pname}`: {pdesc}\n")
                sections.append("\n")

            sections.append("---\n\n")

    # --- Use-case workflows ---
    sections.append(
        textwrap.dedent("""\
        ## :material-workflow: MCP Use-Case Workflows

        ![Tools reference illustration](../assets/illustration-mcp-tools.svg)

        ### AI Code Review in Editor

        The most common use case: an AI agent inside VS Code, Cursor, or Claude Desktop
        invokes zen tools to review code as you write.

        ```mermaid
        sequenceDiagram
            participant Dev as Developer
            participant IDE as VS Code / Cursor
            participant MCP as Zen MCP Server
            Dev->>IDE: "Review this file for zen violations"
            IDE->>MCP: analyze_zen_violations(code, language)
            MCP-->>IDE: AnalysisResult (violations, metrics, score)
            IDE->>Dev: Shows violations with severity and fix guidance
            Dev->>IDE: "Fix the highest-severity issue"
            IDE->>MCP: generate_prompts(code, language)
            MCP-->>IDE: PromptBundle (file + generic prompts)
            IDE->>Dev: Applies remediation
        ```

        ### Automated Remediation Pipeline

        For CI/CD or batch workflows, the agent tasks tool produces machine-readable
        work items that automation agents can process:

        ```mermaid
        sequenceDiagram
            participant CI as CI Pipeline
            participant MCP as Zen MCP Server
            participant Agent as Remediation Agent
            CI->>MCP: analyze_repository(repo_path, languages)
            MCP-->>CI: list[RepositoryAnalysis]
            CI->>MCP: generate_agent_tasks(repo_path, min_severity=7)
            MCP-->>CI: AgentTaskList (prioritized tasks)
            CI->>Agent: Execute tasks sequentially
            Agent-->>CI: Applied fixes
        ```

        ### Project Onboarding

        New projects can use the onboarding tool to bootstrap configuration:

        ```mermaid
        sequenceDiagram
            participant Dev as Developer
            participant MCP as Zen MCP Server
            Dev->>MCP: onboard_project(path, language, strictness)
            MCP-->>Dev: OnboardingGuide (steps + recommended_config)
            Dev->>MCP: set_config_override(language, thresholds…)
            MCP-->>Dev: ConfigStatus (confirmed)
            Dev->>MCP: analyze_repository(path)
            MCP-->>Dev: Baseline results
        ```

        ### Multi-language Repository Analysis

        Analyze polyglot projects by detecting configured languages, then scanning:

        ```mermaid
        sequenceDiagram
            participant Agent as AI Agent
            participant MCP as Zen MCP Server
            Agent->>MCP: detect_languages(repo_path)
            MCP-->>Agent: LanguagesResult
            Agent->>MCP: analyze_repository(repo_path, languages)
            MCP-->>Agent: Per-file results
            Agent->>MCP: generate_report(repo_path, include_gaps=true)
            MCP-->>Agent: ReportOutput (markdown + data)
        ```

        ### Runtime Configuration Tuning

        Adjust thresholds mid-session without restarting the server:

        ```mermaid
        sequenceDiagram
            participant Agent as AI Agent
            participant MCP as Zen MCP Server
            Agent->>MCP: get_config()
            MCP-->>Agent: ConfigStatus (current settings)
            Agent->>MCP: set_config_override("python", max_complexity=8)
            MCP-->>Agent: ConfigStatus (override applied)
            Agent->>MCP: analyze_zen_violations(code, "python")
            MCP-->>Agent: Results with stricter thresholds
            Agent->>MCP: clear_config_overrides()
            MCP-->>Agent: ConfigStatus (reset to defaults)
        ```

    """)
    )

    return "".join(sections)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate MCP tools reference docs from server.py"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry-run: exit 1 if file would change (for CI).",
    )
    args = parser.parse_args()

    content = generate()

    if args.check:
        if OUTPUT_FILE.exists():
            existing = OUTPUT_FILE.read_text(encoding="utf-8")
            if existing == content:
                print(f"✅ {OUTPUT_FILE.relative_to(ROOT)} is up to date.")
                sys.exit(0)
        print(f"❌ {OUTPUT_FILE.relative_to(ROOT)} is out of date. Run:")
        print("   uv run python scripts/generate_mcp_tools_docs.py")
        sys.exit(1)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"✅ Wrote {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
