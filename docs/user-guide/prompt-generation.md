---
title: Prompt Generation
description: Generate AI-ready remediation prompts and agent task lists from zen analysis results.
icon: material/book-open-page-variant
tags:
  - CLI
  - Configuration
status: new
---

# Prompt Generation

Zen analysis finds violations. Prompt generation turns those violations into **actionable fix instructions** — either for a human developer or for an AI agent to execute automatically.

## The concept

Instead of just telling you "function has complexity 15," prompt generation produces remediation guidance:

- **What** the problem is (with code location)
- **Why** it matters (which zen principle is violated)
- **How** to fix it (concrete refactoring steps)
- **Priority** order (highest severity first)

## CLI usage

```bash
zen prompts path/to/project --mode remediation
```

Three modes:

| Mode | Output | Use case |
|------|--------|----------|
| `remediation` | Markdown prompts | Paste into AI chat, share with team |
| `agent` | Structured JSON tasks | Feed to MCP agents for automated fixes |
| `both` | Both formats | CI pipelines — humans read markdown, agents read JSON |

## Terminal output

The terminal renderer shows a compact summary:

- **Remediation Roadmap** — prioritized themes and fix order
- **Big Picture** — health score, systemic patterns, and trajectory notes
- **File Summary** — counts, top themes, and highest severity per file
- **Generic Prompts** — titles only (export for full text)

## Exporting prompts

```bash
zen prompts src --mode both \
  --export-prompts out/prompts.md \
  --export-agent out/prompts.json
```

### Filtering by severity

```bash
zen prompts src --mode remediation --severity 6
```

Only violations with severity ≥ 6 get prompts. Useful for focusing on high-impact issues.

## Prompt structure

Exported markdown prompts use fenced blocks to preserve code formatting:

```markdown
## File: src/orders.py

### Violation: Cyclomatic complexity 18 (max 10)
**Severity**: 7 | **Rule**: py-001 | **Line**: 42

**Problem**: The `process_order` function has 18 decision paths...
**Fix**: Extract guard clauses, split validation from processing...
```

## MCP tools

When running as an MCP server, two tools handle prompt generation:

| Tool | What it returns |
|------|----------------|
| `generate_prompts` | Remediation prompts for a code sample or file |
| `generate_agent_tasks` | Structured task objects that agents can execute |

## See Also

- [Understanding Violations](understanding-violations.md) — How severity scores work
- [MCP Integration](../getting-started/mcp-integration.md) — Connecting agents to the server
- [Examples](examples.md) — End-to-end prompt generation workflows
