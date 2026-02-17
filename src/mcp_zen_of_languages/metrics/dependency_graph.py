"""Directed graph construction and cycle detection over inter-module imports.

Uses networkx ``DiGraph`` to model the import relationships between source
files, then applies Johnson's algorithm (``nx.simple_cycles``) to enumerate
all elementary circuits. Circular dependencies surface as ``DependencyCycle``
objects that the coupling detector evaluates against zen thresholds.
"""

import networkx as nx

from mcp_zen_of_languages.models import DependencyAnalysis, DependencyCycle


def build_import_graph(file_imports: dict[str, list[str]]) -> DependencyAnalysis:
    """Construct a networkx ``DiGraph`` from file-level imports and detect circular dependencies.

    Each key in *file_imports* becomes a graph node, and each imported module
    name becomes a directed edge from the importing file to the target.
    After building the graph, Johnson's cycle-finding algorithm enumerates
    every elementary circuit, which the coupling detector later compares
    against the maximum allowed dependency cycles.

    Args:
        file_imports: Mapping of source file paths to the module names they
            import (e.g. ``{"app.py": ["utils", "models"]}``).

    Returns:
        A ``DependencyAnalysis`` model containing the node list, edge pairs,
        and any detected ``DependencyCycle`` instances.
    """
    g = nx.DiGraph()
    for f, imports in file_imports.items():
        g.add_node(f)
        for imp in imports:
            # Avoid adding empty imports
            if not imp:
                continue
            g.add_edge(f, imp)

    nodes = list(g.nodes())
    edges = [(u, v) for u, v in g.edges()]
    cycles_raw = list(nx.simple_cycles(g))
    cycles = [DependencyCycle(cycle=c) for c in cycles_raw]
    return DependencyAnalysis(nodes=nodes, edges=edges, cycles=cycles)


def find_cycles(g: nx.DiGraph) -> list[DependencyCycle]:
    """Enumerate all elementary circuits in a pre-built dependency graph.

    Applies ``nx.simple_cycles`` (Johnson's algorithm) to the directed
    graph and wraps each raw cycle path in a ``DependencyCycle`` model.
    This is the lower-level primitive that ``build_import_graph`` calls
    internally; callers who already hold a ``DiGraph`` can invoke it
    directly to avoid rebuilding the graph.

    Args:
        g: A networkx ``DiGraph`` whose nodes represent modules and whose
            edges represent import relationships.

    Returns:
        A list of ``DependencyCycle`` models, one per elementary circuit
        found. An empty list means the graph is acyclic.
    """
    cycles_raw = list(nx.simple_cycles(g))
    return [DependencyCycle(cycle=c) for c in cycles_raw]
