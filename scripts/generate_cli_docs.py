"""Generate docs/user-guide/cli-reference.md from the live Typer CLI.

Run::

    uv run python scripts/generate_cli_docs.py          # write file
    uv run python scripts/generate_cli_docs.py --check   # CI dry-run

The script imports the Typer ``app`` instance from ``cli.py``, inspects every
registered command and its parameters, and renders a comprehensive reference
page at ``docs/user-guide/cli-reference.md``.

This ensures documentation never drifts from the actual CLI surface.
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
OUTPUT_FILE = DOCS_DIR / "cli-reference.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_first_paragraph(docstring: str | None) -> str:
    """Return the first non-empty paragraph from a docstring."""
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


def _extract_args_section(docstring: str | None) -> list[tuple[str, str]]:  # noqa: C901
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
            if (
                stripped
                and not stripped.startswith("-")
                and stripped.endswith(":")
                and "(" not in stripped
            ):
                if current_name:
                    params.append((current_name, " ".join(current_desc_lines).strip()))
                break
            if "(" in stripped and "):" in stripped:
                if current_name:
                    params.append((current_name, " ".join(current_desc_lines).strip()))
                paren_idx = stripped.index("(")
                current_name = stripped[:paren_idx].strip()
                colon_idx = stripped.index("):")
                current_desc_lines = [stripped[colon_idx + 2 :].strip()]
            elif stripped and current_name:
                current_desc_lines.append(stripped)
    if current_name:
        params.append((current_name, " ".join(current_desc_lines).strip()))
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


def _option_signature(param: object) -> str:
    """Build a usage-style option string from a click.Option or click.Argument."""
    import click

    if isinstance(param, click.Argument):
        metavar = (param.metavar or param.name or "ARG").upper()
        return f"<{metavar}>"

    if not isinstance(param, click.Option):
        return ""

    opts = list(param.opts)

    # Check if it's a flag (boolean option without a value)
    if param.is_flag:
        value_part = ""
    elif isinstance(param.type, click.Choice):
        choices = "|".join(str(c) for c in param.type.choices)
        value_part = f" {choices}"
    elif param.type and param.type.name not in ("bool", "flag"):
        value_part = f" <{param.type.name.upper()}>"
    else:
        value_part = ""

    # Show all option names (e.g. --quiet / -q)
    names = " / ".join(opts)
    return f"`{names}{value_part}`"


def _build_usage(name: str, command: object) -> str:
    """Build a bash usage line for a command."""
    import click

    parts = [f"zen {name}"]
    options: list[str] = []

    for param in getattr(command, "params", []):
        if isinstance(param, click.Argument):
            metavar = (param.metavar or param.name or "ARG").upper()
            parts.append(f"<{metavar}>")
        elif isinstance(param, click.Option):
            opts = list(param.opts)
            primary = opts[0] if opts else ""
            # Check if it's a flag (boolean option without a value)
            if param.is_flag:
                options.append(f"[{primary}]")
            elif isinstance(param.type, click.Choice):
                value = "|".join(param.type.choices)
                options.append(f"[{primary} {value}]")
            elif param.type and param.type.name not in ("bool", "flag"):
                options.append(f"[{primary} <{param.type.name.upper()}>]")
            else:
                options.append(f"[{primary}]")

    return " ".join(parts + options)


# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------


PANEL_ICONS = {
    "Analysis": ":material-magnify:",
    "Configuration": ":material-cog-outline:",
    "Other": ":material-dots-horizontal:",
}

EXIT_CODES = [
    ("0", "Success — no violations above the configured threshold"),
    ("1", "Violations found above the severity threshold"),
    ("2", "Invalid configuration or arguments"),
]

GLOBAL_OPTIONS = [
    ("`--quiet`, `-q`", "Suppress banner, Rich panels, and decorative output"),
    ("`--verbose`, `-v`", "Show rich tracebacks with local variable inspection"),
    ("`--help`", "Show help for any command"),
    ("`--version`", "Print version number"),
]


def generate() -> str:  # noqa: C901, PLR0912, PLR0915
    """Generate the full markdown content from the live CLI app."""
    import click
    import typer.main as typer_main

    # Import CLI app
    from mcp_zen_of_languages.cli import app

    # Collect click commands from the Typer app
    click_app: click.Group = typer_main.get_command(app)  # type: ignore[attr-defined]

    sections: list[str] = []

    # Gather commands, skip hidden ones and aliases (hidden=True)
    commands: dict[str, click.BaseCommand] = {}
    for cmd_name, cmd in sorted(click_app.commands.items()):
        if getattr(cmd, "hidden", False):
            continue
        commands[cmd_name] = cmd

    sections.extend(
        (
            textwrap.dedent(
                """\
        ---
        title: CLI Reference
        description: The CLI executable is `zen`.
        icon: material/book-open-page-variant
        tags:
          - CLI
          - Configuration
        ---

        # CLI Reference

        ![CLI workflow illustration](../assets/illustration-cli.svg)

        > **Auto-generated** from [`cli.py`](https://github.com/Anselmoo/mcp-zen-of-languages/blob/main/src/mcp_zen_of_languages/cli.py). Do not edit manually.
        >
        > Regenerate with: `uv run python scripts/generate_cli_docs.py`

        The CLI executable is `zen`. It is the local/CI interface for the same analysis capabilities exposed through MCP tools. All commands support `--quiet` to suppress Rich panels and banners.

        !!! info "MCP-first workflow"
            If you're using an MCP-capable editor or agent, start with [MCP Tools Reference](mcp-tools-reference.md). Use the CLI when you need local checks, export artifacts, or CI automation.

    """,
            ),
            "## Commands at a glance\n\n",
            "| Command | Purpose |\n",
            "|---------|--------|\n",
        ),
    )
    for cmd_name, cmd in commands.items():
        first_line = _extract_first_paragraph(cmd.help or "")
        sections.append(f"| `zen {cmd_name}` | {first_line} |\n")
    sections.append("\n")

    # --- Group by rich_help_panel ---
    panel_groups: dict[str, list[tuple[str, click.BaseCommand]]] = {}
    for cmd_name, cmd in commands.items():
        panel = getattr(cmd, "rich_help_panel", None) or "Other"
        panel_groups.setdefault(panel, []).append((cmd_name, cmd))

    # --- Detailed command sections ---
    for panel in ["Analysis", "Configuration", "Other"]:
        group = panel_groups.get(panel, [])
        if not group:
            continue
        icon = PANEL_ICONS.get(panel, "")
        sections.append(f"## {icon} {panel} Commands\n\n")

        for cmd_name, cmd in group:
            fn = getattr(cmd, "callback", None)
            full_doc = inspect.getdoc(fn) if fn else ""

            sections.append(f"### zen {cmd_name} {{{{ #{cmd_name} }}}}\n\n")

            # Usage
            usage = _build_usage(cmd_name, cmd)
            sections.append(f"```bash\n{usage}\n```\n\n")

            if first_para := _extract_first_paragraph(full_doc):
                sections.append(f"{first_para}\n\n")

            if params := [
                p
                for p in getattr(cmd, "params", [])
                if not isinstance(p, click.Argument)
            ]:
                sections.append("**Options:**\n\n")
                sections.append("| Option | Default | Description |\n")
                sections.append("|--------|---------|-------------|\n")
                for param in params:
                    if not isinstance(param, click.Option):
                        continue
                    sig = _option_signature(param)
                    default = param.default
                    if default is None or default is False:
                        default_str = "—"
                    elif isinstance(default, bool):
                        default_str = str(default).lower()
                    else:
                        default_str = f"`{default}`"
                    help_text = param.help or ""
                    sections.append(f"| {sig} | {default_str} | {help_text} |\n")
                sections.append("\n")

            if returns := _extract_returns_section(full_doc):
                sections.append(f"**Returns:** {returns}\n\n")

            sections.append("---\n\n")

    sections.extend(
        (
            "## Global Options\n\n",
            "| Flag | Description |\n",
            "|------|-------------|\n",
        ),
    )
    for flag, desc in GLOBAL_OPTIONS:
        sections.append(f"| {flag} | {desc} |\n")
    sections.extend(("\n", "## Exit Codes\n\n"))
    sections.extend(("| Code | Meaning |\n", "|------|--------|\n"))
    for code, meaning in EXIT_CODES:
        sections.append(f"| `{code}` | {meaning} |\n")
    sections.append("\n")

    return "".join(sections)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate CLI reference docs from cli.py",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry-run: exit 1 if file would change (for CI).",
    )
    args = parser.parse_args()

    # Ensure the package is importable from the source tree
    src_dir = ROOT / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    content = generate()

    if args.check:
        if OUTPUT_FILE.exists():
            existing = OUTPUT_FILE.read_text(encoding="utf-8")
            if existing == content:
                print(f"✅ {OUTPUT_FILE.relative_to(ROOT)} is up to date.")
                sys.exit(0)
        print(f"❌ {OUTPUT_FILE.relative_to(ROOT)} is out of date. Run:")
        print("   uv run python scripts/generate_cli_docs.py")
        sys.exit(1)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"✅ Wrote {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
