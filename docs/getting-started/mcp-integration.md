---
title: MCP Integration
description: Connect MCP Zen of Languages to VS Code and other MCP-compatible clients for AI-assisted code analysis.
icon: material/rocket-launch
tags:
  - CLI
  - MCP
---

# MCP Integration

The MCP server exposes zen analysis as tools that AI agents can call — analyze code, generate reports, and produce remediation prompts, all from within your editor.

## Start the server

```bash
zen-mcp-server
```

The server communicates via stdin/stdout using the MCP protocol. It doesn't serve HTTP — MCP clients connect to it as a subprocess.

## VS Code configuration

Use one-click install or add config manually.

[![Install with UVX in VS Code](https://img.shields.io/badge/VS_Code-UVX-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=zen-of-languages&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22mcp-zen-of-languages%22%2C%22zen-mcp-server%22%5D%7D) [![Install with UVX in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-UVX-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=zen-of-languages&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22mcp-zen-of-languages%22%2C%22zen-mcp-server%22%5D%7D&quality=insiders)

The `zen init` wizard can generate `.vscode/mcp.json` for you. Here's the manual workspace equivalent:

=== "Basic Configuration"
`json
    {
      "mcp": {
        "servers": {
          "zen-of-languages": {
            "command": "uvx",
            "args": ["--from", "mcp-zen-of-languages", "zen-mcp-server"],
            "env": {
              "ZEN_CONFIG_PATH": "${workspaceFolder}/zen-config.yaml"
            }
          }
        }
      }
    }
    `

=== "With Prompted Values"
For user-prompted configuration paths:

    ```json
    {
      "mcp": {
        "servers": {
          "zen-of-languages": {
            "command": "uvx",
            "args": ["--from", "mcp-zen-of-languages", "zen-mcp-server"],
            "env": {
              "ZEN_CONFIG_PATH": "${input:zenConfigPath}"
            }
          }
        },
        "inputs": [
          {
            "type": "promptString",
            "id": "zenConfigPath",
            "description": "Path to zen-config.yaml",
            "default": "${workspaceFolder}/zen-config.yaml"
          }
        ]
      }
    }
    ```

Once configured, MCP-compatible clients (VS Code with Copilot, Claude Desktop, etc.) can invoke zen tools directly.

## Claude Desktop configuration

Add to your `claude_desktop_config.json` (usually in `~/Library/Application Support/Claude/` on macOS or `%APPDATA%\Claude\` on Windows):

```json
{
  "mcpServers": {
    "zen-of-languages": {
      "command": "uvx",
      "args": ["--from", "mcp-zen-of-languages", "zen-mcp-server"],
      "env": {
        "ZEN_CONFIG_PATH": "/path/to/your/zen-config.yaml"
      }
    }
  }
}
```

Replace `/path/to/your/zen-config.yaml` with the absolute path to your config file, or omit the `env` section to use default auto-discovery.

## Claude Code integration

Install the server using the Claude Code CLI:

```bash
claude mcp add zen-of-languages -- uvx --from mcp-zen-of-languages zen-mcp-server
```

This automatically adds the server to Claude Code's MCP configuration.

## Cursor/Windsurf integration

For Cursor and Windsurf, add to your MCP configuration file:

=== "Cursor"
Edit `.cursor/mcp.json` in your project root:

    ```json
    {
      "mcpServers": {
        "zen-of-languages": {
          "command": "uvx",
          "args": ["--from", "mcp-zen-of-languages", "zen-mcp-server"],
          "env": {
            "ZEN_CONFIG_PATH": "${workspaceFolder}/zen-config.yaml"
          }
        }
      }
    }
    ```

=== "Windsurf"
Edit `.windsurf/mcp.json` in your project root:

    ```json
    {
      "mcpServers": {
        "zen-of-languages": {
          "command": "uvx",
          "args": ["--from", "mcp-zen-of-languages", "zen-mcp-server"],
          "env": {
            "ZEN_CONFIG_PATH": "${workspaceFolder}/zen-config.yaml"
          }
        }
      }
    }
    ```

## Available MCP tools

The server exposes four primary tools for code analysis:

### `analyze_zen_violations`

Analyze a single file against its language's zen principles.

**Parameters:**

- `code` (string, required): Source code to analyze
- `language` (string, required): Programming language (e.g., "python", "typescript", "rust")
- `file_path` (string, optional): File path for context and error messages

**Returns:**

- List of violations with severity (1-10), location, rule ID, and remediation guidance
- Summary metrics (total violations, average severity)

**Example usage:**

```
Ask your AI agent: "Analyze this Python file for zen violations"
```

### `generate_report`

Scan a directory and produce a grouped violation report.

**Parameters:**

- `path` (string, required): File or directory path to analyze
- `format` (string, optional): Output format — `"markdown"` (default), `"json"`, or `"both"`
- `include_prompts` (boolean, optional): Include AI remediation prompts in the report

**Returns:**

- Formatted report with violations grouped by file and severity
- Optional JSON export for programmatic use

**Example usage:**

```
Ask your AI agent: "Generate a zen report for the src/ directory"
```

### `generate_prompts`

Generate AI-ready remediation prompts from analysis results.

**Parameters:**

- `violations` (array, required): List of violation objects from `analyze_zen_violations`
- `severity_threshold` (number, optional): Only generate prompts for violations above this severity

**Returns:**

- Structured prompts with context, problem description, and suggested fixes
- Prompts are optimized for AI agents (Copilot, GPT, Claude)

**Example usage:**

```
Ask your AI agent: "Generate fix prompts for high-severity violations"
```

### `generate_agent_tasks`

Produce structured task objects that MCP agents can execute to fix violations.

**Parameters:**

- `violations` (array, required): List of violation objects
- `auto_fix` (boolean, optional): Include auto-fix code snippets where available

**Returns:**

- Executable task objects with file paths, line numbers, and fix instructions
- Tasks can be processed sequentially or in parallel

**Example usage:**

```
Ask your AI agent: "Create tasks to fix all cyclomatic complexity violations"
```

## Workflow example

1. Open a Python file in VS Code
2. Ask Copilot: _"Run zen analysis on this file"_
3. The agent calls `analyze_zen_violations` via MCP
4. You get back violations with severity scores and fix suggestions
5. Ask: _"Fix the highest-severity violation"_ — the agent uses the remediation context to apply changes

## Troubleshooting

### Server not showing up in VS Code

1. **Verify uvx is installed:**

   ```bash
   uvx --version
   ```

   If not found, install `uv`: `pip install uv`

2. **Check VS Code MCP extension is enabled:**
   - Open Command Palette (`Cmd/Ctrl+Shift+P`)
   - Search for "MCP: List Servers"
   - Verify "zen-of-languages" appears

3. **Test server manually:**

   ```bash
   uvx --from mcp-zen-of-languages zen-mcp-server
   ```

   You should see JSON output indicating the server is ready.

4. **Check logs:**
   - VS Code: Open "Output" panel → Select "MCP" from dropdown
   - Look for connection errors or startup failures

### Python version conflicts

If you see errors about Python 3.12+ requirement:

```bash
# Check your Python version
python --version

# Use a specific Python version with uvx
uvx --python 3.12 --from mcp-zen-of-languages zen-mcp-server
```

### Config file not discovered

The server looks for `zen-config.yaml` in:

1. Current working directory
2. Nearest parent directory containing `pyproject.toml`

Override with environment variable:

```json
{
  "env": {
    "ZEN_CONFIG_PATH": "/absolute/path/to/zen-config.yaml"
  }
}
```

### Debugging with verbose output

Enable debug logging:

```json
{
  "env": {
    "FASTMCP_DEBUG": "true",
    "FASTMCP_LOG_LEVEL": "DEBUG"
  }
}
```

This logs detailed MCP protocol messages and tool invocations.

### Common issues

| Problem                    | Solution                                                    |
| -------------------------- | ----------------------------------------------------------- |
| `uvx: command not found`   | Install `uv`: `pip install uv`                              |
| `Server exits immediately` | Check Python version is 3.12+                               |
| `No violations found`      | Verify language is enabled in `zen-config.yaml`             |
| `Config file ignored`      | Use `ZEN_CONFIG_PATH` env var with absolute path            |
| `Tool timeouts`            | Large codebases may need increased timeout in client config |

## Next steps

- [CLI Reference](../user-guide/cli-reference.md) — Full CLI command documentation
- [Prompt Generation](../user-guide/prompt-generation.md) — How remediation prompts work
- [Configuration](../user-guide/configuration.md) — Customize which detectors run
