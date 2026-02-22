"""Shared utilities that support the analysis pipeline without owning domain logic.

Includes language detection by file extension and content heuristics, Markdown
normalization for report output, metric scoring helpers, and parser front-ends
that select between tree-sitter and the built-in ``ast`` module.

See Also:
    ``utils.language_detection``: Maps file extensions and code patterns to language names.
    ``utils.markdown_quality``: Structural lint checks for generated Markdown reports.
    ``utils.metric``: Quality-score arithmetic consumed by result models.
    ``utils.parsers``: AST construction with tree-sitter / ``ast`` fallback.
    ``utils.subprocess_runner``: Secure subprocess invocation for external linters/tools.
"""
