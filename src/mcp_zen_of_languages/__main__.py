"""Entry point for running the MCP Zen of Languages server as a module.

When a developer runs ``python -m mcp_zen_of_languages``, Python executes this
file, which boots the FastMCP server in stdio transport mode. Stdio is the
standard communication channel that MCP clients (editors, CI tools, agent
frameworks) use to exchange JSON-RPC messages with the server process.

An equivalent entry point, ``zen-mcp-server``, is registered as a console
script in ``pyproject.toml`` so the server can also be launched directly
from the shell without the ``python -m`` prefix.
"""

from mcp_zen_of_languages.server import mcp


def main() -> None:
    """Start the FastMCP server with stdio transport.

    Stdio transport is the standard MCP communication channel: the server
    reads JSON-RPC requests from stdin and writes responses to stdout,
    letting any MCP-compatible client drive the interaction. Once running,
    the server exposes tools for code analysis, reporting, and
    configuration management.

    See Also:
        server.mcp: The ``FastMCP`` instance that registers all available
            MCP tools and handles request routing.
    """
    mcp.run()


if __name__ == "__main__":
    main()
