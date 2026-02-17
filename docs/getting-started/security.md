---
title: Security Considerations
description: Security best practices and data handling for MCP Zen of Languages
icon: material/shield-check
tags:
  - Security
  - MCP
---

# Security Considerations

MCP Zen of Languages is designed with security and privacy in mind. This page documents how the tool handles data, what it accesses, and best practices for secure usage.

## Data Handling

### Local Analysis Only

**All code analysis happens locally** — your code never leaves your machine:

- ✅ Code is parsed and analyzed on your local system
- ✅ No network calls are made during analysis
- ✅ No telemetry or usage data is collected
- ✅ No code is uploaded to external services

### What Data is Processed

The analyzer processes:

- **Source code files** — read-only access to files you explicitly analyze
- **Configuration files** — `zen-config.yaml` for analyzer settings
- **Project metadata** — file paths, language detection, import graphs

The analyzer **never** modifies your source files unless you explicitly use a fix command (future feature).

### What Data is Sent/Received

When using the MCP server:

- **Input**: Code snippets, file paths, analysis parameters sent by the MCP client
- **Output**: Violation reports, severity scores, remediation prompts sent back to the client

All communication is **local** via stdin/stdout (stdio transport).

## File System Access

### Scope of Access

The tool has read-only access to:

1. **Files you explicitly analyze** — via CLI arguments or MCP tool calls
2. **zen-config.yaml** — configuration file discovery
3. **pyproject.toml** — for configuration path resolution

The tool **does not**:

- ❌ Scan your entire file system
- ❌ Access files outside the project directory
- ❌ Modify files (analysis is read-only)
- ❌ Execute code from analyzed files

### Directory Traversal Protection

When analyzing directories, the tool:

- Only processes files with recognized language extensions
- Skips hidden directories (`.git`, `.venv`, `node_modules`)

## MCP Server Security

### Transport Security

The MCP server uses **stdio transport** (standard input/output) for all communication:

- ✅ **Secure** — Local subprocess, no network exposure
- ✅ **Isolated** — Communication is confined to the parent MCP client process
- ✅ **No authentication needed** — The server only responds to the client that spawned it

### Subprocess Security

When running as an MCP server:

- The server runs as a subprocess of the MCP client
- Inherits the permissions of the parent process
- Cannot access resources outside the client's permissions
- Terminates when the client disconnects

### Configuration Security

**Environment variables** may contain sensitive paths:

```json
{
  "env": {
    "ZEN_CONFIG_PATH": "/home/user/projects/my-app/zen-config.yaml"
  }
}
```

Ensure:
- Paths are absolute and validated
- Config files are in trusted locations
- No secrets are stored in `zen-config.yaml`

## Dependency Security

### Supply Chain

The tool depends on:

- **fastmcp** — MCP protocol implementation (trusted source)
- **pydantic** — Data validation (widely used, well-audited)
- **tree-sitter** — Parser library (memory-safe Rust core)
- **pygments** — Syntax highlighting (mature, stable)
- **radon** — Complexity metrics (focused, maintained)

All dependencies:
- Are pinned to specific versions in `uv.lock`
- Are scanned for known vulnerabilities in CI
- Are updated regularly via Dependabot

### Vulnerability Disclosure

If you discover a security vulnerability:

1. **Do not open a public issue**
2. Email the maintainer at `Anselm.Hahn@gmail.com`
3. Include steps to reproduce and impact assessment
4. Allow 90 days for a patch before public disclosure

## Best Practices

### For End Users

1. **Run with minimal privileges** — don't use `sudo` or admin accounts
2. **Use uvx for isolation** — each run gets a clean virtual environment
3. **Keep dependencies updated** — `pip install --upgrade mcp-zen-of-languages`
4. **Review config files** — ensure `zen-config.yaml` doesn't reference untrusted paths
5. **Use stdio transport** — avoid HTTP transports unless necessary

### For CI/CD Pipelines

1. **Use the CLI** — `zen report` instead of the MCP server
2. **Read-only file system** — mount code as read-only in containers
3. **Restrict network access** — no outbound network required
4. **Run in isolated containers** — use Docker for additional sandboxing
5. **Pin versions** — lock to specific releases for reproducibility

### For MCP Integrations

1. **Trust your MCP client** — the server inherits client permissions
2. **Use workspace-scoped configs** — avoid global configurations
3. **Review tool calls** — understand what code the MCP client sends for analysis
4. **Monitor resource usage** — large codebases may consume significant memory
5. **Set timeout limits** — prevent runaway analysis on malformed input

## Privacy

### No Telemetry

MCP Zen of Languages **does not collect any telemetry or usage data**:

- ❌ No analytics
- ❌ No crash reports
- ❌ No feature usage tracking
- ❌ No IP addresses logged

### Offline Operation

The tool works completely offline:

- ✅ No internet connection required
- ✅ No external API calls
- ✅ No cloud dependencies
- ✅ No license servers

## Compliance

### License

The project is open source under the MIT License:

- ✅ Free for commercial use
- ✅ No usage restrictions
- ✅ Audit-friendly (full source available)

### Data Regulations

Since all analysis is local and no data is collected:

- ✅ GDPR compliant (no personal data processed)
- ✅ CCPA compliant (no data sold or shared)
- ✅ HIPAA/SOC2 compatible (no data transmission)

## Audit Trail

For regulated environments needing audit logs:

```bash
# Generate reports with metadata
zen report . --export-json audit.json --export-log audit.log

# audit.log contains:
# - Timestamp
# - Files analyzed
# - Violations found
# - Config used
```

Store these artifacts for compliance and traceability.

## See Also

- [MCP Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices) — Official MCP security guidance
- [Configuration](../user-guide/configuration.md) — How to configure the analyzer
- [Troubleshooting](mcp-integration.md#troubleshooting) — Common security-related issues

## Summary

✅ **Safe to use** — all analysis is local, no data leaves your machine
✅ **Privacy-first** — no telemetry, no tracking, offline operation
✅ **Transparent** — open source, auditable code
✅ **Sandboxed** — read-only access, no code execution
✅ **Supply chain** — pinned dependencies, vulnerability scanning
