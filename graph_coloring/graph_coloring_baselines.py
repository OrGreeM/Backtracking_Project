"""
Provides baseline graph coloring algorithms for comparison
with the backtracking-based approach.

Includes:
    - Greedy coloring (Welsh-Powell): assigns the smallest available
      color to each vertex in order of decreasing degree. Fast but
      may use more colors than the chromatic number.

    - DFS coloring: traverses the graph in depth-first order from
      an arbitrary start vertex and assigns the smallest available
      color to each vertex as it is visited. No backtracking.
"""

from collections import deque
from graph_coloring.generate_graph import generate_graph
from graph_coloring.graph import Graph
from graph_coloring.graph_converter import convert


def main(n:int, p:int|float, k:int, graph:Graph|list[list[int]]=None):
    """
    Generates a random graph or uses a provided one, then runs both
    baseline algorithms (greedy and DFS) on it.

    If a graph is provided as an adjacency matrix, it will be converted
    into a Graph instance.

    Args:
        n (int): Number of vertices (used only if graph is not provided).
        p (int | float): Probability of edge creation (used only if graph is not provided).
        k (int): Maximum number of colors allowed.
        graph (Graph | list[list[int]], optional): Predefined graph or adjacency matrix.

    Returns:
        tuple: (Graph instance, greedy coloring dict, dfs coloring dict)
            Each coloring dict is None if more than k colors were required.
    """
    if graph is None:
        graph = generate_graph(n, p)
    else:
        graph = convert(graph)

    return graph, greedy_color(k, graph), dfs_color(k, graph)


def _smallest_available_color(vertex_key, graph:Graph, colors:dict[int | str, int]) -> int:
    """
    Returns the smallest non-negative color not used by any colored neighbor.

    Args:
        vertex_key: Vertex whose color is being chosen.
        graph (Graph): The graph being colored.
        colors (dict): Current color assignments.

    Returns:
        int: Smallest color index not present among colored neighbors.
    """
    used = {
        colors[neighbor_key]
        for neighbor_key in graph.get_vertex(vertex_key).get_neighbors()
        if neighbor_key in colors
    }

    color = 0
    while color in used:
        color += 1

    return color


def greedy_color(k:int, graph:Graph) -> dict[int | str, int] | None:
    """
    Colors the graph using a greedy Welsh-Powell strategy.

    Vertices are processed in order of decreasing degree. Each vertex
    receives the smallest color not already used by its colored neighbors.
    No backtracking is performed.

    Args:
        k (int): Maximum number of colors allowed.
        graph (Graph): Graph to color.

    Returns:
        dict or None: Mapping of vertex key to color, or None if the
        coloring required more than k colors.
    """
    colors:dict[int | str, int] = {}

    vertices_by_degree = sorted(
        graph.get_vertices(),
        key=lambda v: len(list(graph.get_vertex(v).get_neighbors())),
        reverse=True,
    )

    for vertex_key in vertices_by_degree:
        color = _smallest_available_color(vertex_key, graph, colors)
        if color >= k:
            return None
        colors[vertex_key] = color

    return colors


def dfs_color(k:int, graph:Graph) -> dict[int | str, int] | None:
    """
    Colors the graph by traversing it in depth-first order.

    Starts from the first vertex returned by the graph and visits
    vertices via DFS, assigning the smallest available color upon
    visiting each one. No backtracking is performed.

    For disconnected graphs, DFS is restarted from each unvisited
    vertex.

    Args:
        k (int): Maximum number of colors allowed.
        graph (Graph): Graph to color.

    Returns:
        dict or None: Mapping of vertex key to color, or None if the
        coloring required more than k colors.
    """
    colors:dict[int | str, int] = {}
    vertices = list(graph.get_vertices())

    for start_key in vertices:
        if start_key in colors:
            continue

        stack = deque()
        stack.append(start_key)

        while stack:
            vertex_key = stack.pop()
            if vertex_key in colors:
                continue

            color = _smallest_available_color(vertex_key, graph, colors)
            if color >= k:
                return None
            colors[vertex_key] = color

            for neighbor_key in graph.get_vertex(vertex_key).get_neighbors():
                if neighbor_key not in colors:
                    stack.append(neighbor_key)

    return colors
