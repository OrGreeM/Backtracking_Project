"""
Provides a backtracking-based algorithm for graph coloring using k colors.

Includes utilities to generate a graph and attempt to assign colors
to its vertices such that no adjacent vertices share the same color.
"""

from generate_graph import generate_graph
from graph import Graph, Vertex

def main(n:int, p:int|float, k:int, graph:Graph=None):
    """
    Generates a graph (if not provided) and attempts to color it with k colors.

    Args:
        n (int): Number of vertices.
        p (int | float): Probability of edge creation (for random graph).
        k (int): Number of available colors.
        graph (Graph, optional): Predefined graph.

    Returns:
        tuple: (Graph instance, coloring dict or None if no valid coloring exists)
    """

    if graph is None:
        graph = generate_graph(n, p)

    else:
        #TODO: Реалізувати функціонал, коли користувач передає свій граф
        pass

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

def color_graph(k:int, graph:Graph):
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

    def solve(index):
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

if __name__ == '__main__':
    print('Choose parameters for graph generation and coloring:')
    v_num = int(input('Number of vertices: '))
    chance = float(input('Chance of edge generation: '))
    c_num = int(input('Number of colors: '))

    g, colored_graph = main(v_num, chance, c_num)
    print(g)
    print(colored_graph)
