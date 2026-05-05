"""
Provides a backtracking-based algorithm for graph coloring using k colors.

Includes utilities to generate a graph and attempt to assign colors
to its vertices such that no adjacent vertices share the same color.
"""

from graph_coloring.generate_graph import generate_graph
from graph_coloring.graph import Graph, Vertex
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



def _is_valid(vertex:Vertex, color:int, colors: dict[int | str, int]) -> bool:
    """
    Checks if a given color can be assigned to a vertex without conflicts.

    Args:
        vertex (Vertex): Vertex to validate.
        color (int): Color to assign.
        colors (dict): Current color assignments.

    Returns:
        bool: True if valid, False otherwise.
    """
    for neighbor in vertex.get_neighbors():
        if color == colors.get(neighbor):
            return False

    return True

def color_graph(k:int, graph:Graph) -> dict[int | str, int] | None:
    """
    Attempts to color the graph using at most k colors via backtracking.

    Uses a recursive backtracking strategy to assign
    colors to vertices one by one while ensuring no adjacent vertices share
    the same color.

    Args:
        k (int): Number of colors.
        graph (Graph): Graph to color.

    Returns:
        dict or None: Mapping of vertex to color, or None if impossible.
    """
    colors = {}
    vertices = list(graph.get_vertices())

    def solve(index:int):
        if index == len(vertices):
            return True

        vertex_key = vertices[index]

        vertex = graph.get_vertex(vertex_key)
        for color in range(k):
            if _is_valid(vertex, color, colors):
                colors[vertex_key] = color
                if solve(index + 1):
                    return True

                del colors[vertex_key]

        return False

    if solve(0):
        return colors

    return None
