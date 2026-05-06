"""
Provides a backtracking-based algorithm for graph coloring using k colors.

Uses MRV (Minimum Remaining Values) heuristic with degree tie-breaking
and Forward Checking for constraint propagation.
"""

from graph_coloring.generate_graph import generate_graph
from graph_coloring.graph import Graph
from graph_coloring.graph_converter import convert

def main(n:int, p:int|float, k:int, graph:Graph|list[list[int]]=None):
    """
    Generates a random graph or uses a provided one, then attempts
    to color it with k colors.

    If a graph is provided as an adjacency matrix, it will be converted
    into a Graph instance.

    Args:
        n (int): Number of vertices (used only if graph is not provided).
        p (int | float): Probability of edge creation (used only if graph is not provided).
        k (int): Number of available colors.
        graph (Graph | list[list[int]], optional): Predefined graph or adjacency matrix.

    Returns:
        tuple: (Graph instance, coloring dict or None if no valid coloring exists)
    """
    if graph is None:
        graph = generate_graph(n, p)

    else:
        graph = convert(graph)

    return graph, color_graph(k, graph)


def color_graph(k:int, graph:Graph) -> dict[int | str, int] | None:
    """
    Attempts to color the graph using at most k colors via backtracking
    with MRV heuristic (with degree tie-breaking) and Forward Checking.

    Args:
        k (int): Number of colors.
        graph (Graph): Graph to color.

    Returns:
        dict or None: Mapping of vertex key to color, or None if impossible.
    """
    colors: dict[int | str, int] = {}
    domains: dict[int | str, set[int]] = {
        vertex: set(range(k)) for vertex in graph.get_vertices()
    }

    def _uncolored_neighbors_count(vertex_key) -> int:
        """Number of still-uncolored neighbors (used for MRV tie-breaking)."""
        return sum(
            1 for nb in graph.get_vertex(vertex_key).get_neighbors()
            if nb in domains
        )

    def _choose_vertex() -> int | str:
        """
        MRV: pick the uncolored vertex with the smallest domain.
        Tie-break by degree: prefer the vertex with more uncolored neighbors
        (more constraining → fail faster on bad branches).
        """
        return min(
            domains,
            key=lambda v: (len(domains[v]), -_uncolored_neighbors_count(v)),
        )

    def _forward_check(color:int, vertex_key) -> tuple[list[int | str], bool]:
        """
        After assigning `color` to `vertex_key`, remove it from every
        uncolored neighbor's domain.

        Returns (pruned, ok):
            pruned — list of neighbor keys whose domains were shrunk
            ok     — False if some domain became empty (wipeout), else True

        Does NOT roll back on wipeout — caller is always responsible for undo.
        """
        pruned = []
        for neighbor_key in graph.get_vertex(vertex_key).get_neighbors():
            if neighbor_key not in domains:
                continue
            if color in domains[neighbor_key]:
                domains[neighbor_key].remove(color)
                pruned.append(neighbor_key)
                if not domains[neighbor_key]:
                    return pruned, False
        return pruned, True

    def _undo_forward_check(color:int, pruned:list[int | str]) -> None:
        """Restore the color removed from neighbors' domains during FC."""
        for neighbor_key in pruned:
            domains[neighbor_key].add(color)

    def _color_vertex(color:int, vertex_key) -> set[int]:
        """Assign color and remove vertex from domains. Return saved domain for undo."""
        saved_domain = domains.pop(vertex_key)
        colors[vertex_key] = color
        return saved_domain

    def _uncolor_vertex(vertex_key, saved_domain:set[int]) -> None:
        """Restore vertex into domains and remove from colors."""
        domains[vertex_key] = saved_domain
        del colors[vertex_key]

    def solve() -> bool:
        if not domains:
            return True

        vertex_key = _choose_vertex()

        for color in list(domains[vertex_key]):
            saved_domain = _color_vertex(color, vertex_key)

            pruned, ok = _forward_check(color, vertex_key)

            if ok and solve():
                return True

            _undo_forward_check(color, pruned)
            _uncolor_vertex(vertex_key, saved_domain)

        return False

    if solve():
        return colors

    return None
