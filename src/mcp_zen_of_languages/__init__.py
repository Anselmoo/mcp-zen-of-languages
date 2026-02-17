"""Multi-language code analysis against zen principles.

This package evaluates source code for adherence to idiomatic best practices
— the "zen" of each supported language. It ships three main entry points:

*  **MCP server** (``__main__.py`` / ``zen-mcp-server``): exposes analysis
   tools over the Model Context Protocol for editor and agent integration.
*  **CLI** (``mcp-zen-of-languages check``): runs analysis locally from
   the terminal and prints a human-readable report.
*  **Programmatic API**: import ``create_analyzer`` or language-specific
   analyzers directly for embedding in custom tooling.

Internally the architecture follows a pipeline design: language-specific
analyzers parse code and compute metrics via the Template Method pattern,
then a ``DetectionPipeline`` runs a chain of Strategy-based violation
detectors to produce an ``AnalysisResult``.

Attributes:
    __version__: Semantic version string for the installed package.
"""

__version__ = "0.1.0"
