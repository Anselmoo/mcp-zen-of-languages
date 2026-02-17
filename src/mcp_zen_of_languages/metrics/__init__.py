"""Metrics subsystem for quantifying code health through complexity and dependency analysis.

This package combines radon-based cyclomatic complexity scoring with
networkx-powered dependency graph traversal to produce the numeric signals
that downstream detectors compare against zen principle thresholds.

See Also:
    ``metrics.collector``: Single entry point that orchestrates all metric computations.
    ``metrics.complexity``: Radon wrappers for cyclomatic and maintainability scoring.
    ``metrics.dependency_graph``: Directed graph construction and cycle detection.
"""
