"""
module helps to convert an adjacency matrix
to self implementation of graph in module graph.py
"""

from graph import Graph

def convert(adjacency_matrix: list[list[int]]) -> Graph:
    """
    Converts an adjacency matrix into a Graph instance.

    Assumes an undirected graph represented by a square matrix,
    where 1 indicates an edge between vertices and 0 means no edge.

    Args:
        adjacency_matrix (list[list[int]]): Adjacency matrix.

    Returns:
        Graph: Constructed graph instance.
    """
    graph = Graph()

    list_length = len(adjacency_matrix)
    for key in range(list_length):
        graph.add_vertex(key)

    for i in range(list_length):
        for j in range(i + 1, list_length):
            if adjacency_matrix[i][j] == 1:
                graph.add_edge(i, j)

    return graph
