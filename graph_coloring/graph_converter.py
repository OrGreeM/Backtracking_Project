"""
module helps to convert an adjacency matrix
to self implementation of graph in module graph.py
"""

from graph import Graph

def validate(adjacency_matrix: list[list[int]]) -> None:
    """
    Validates an adjacency matrix for an undirected simple graph.

    Checks performed in a single pass over the upper triangle:
        1. Matrix is square (every row has length == len(matrix)).
        2. Diagonal contains only zeros (no self-loops).
        3. Matrix is symmetric (matrix[i][j] == matrix[j][i]).
        4. All entries are 0 or 1.

    Args:
        adjacency_matrix (list[list[int]]): Adjacency matrix to validate.

    Raises:
        ValueError: If the matrix violates any of the rules above.
    """
    n = len(adjacency_matrix)


    for i, row in enumerate(adjacency_matrix):
        if len(row) != n:
            raise ValueError(f"Matrix must be square: row {i} has length {len(row)}, expected {n}")


    for i in range(n):
        row = adjacency_matrix[i]

        if row[i] != 0:
            raise ValueError(f"Self-loop detected at vertex {i}")

        for j in range(i + 1, n):
            value = row[j]

            if value not in (0, 1):
                raise ValueError(f"Invalid entry at ({i},{j}): {value} (expected 0 or 1)")

            if value != adjacency_matrix[j][i]:
                raise ValueError(f"Asymmetric edge at ({i},{j}): {value} != {adjacency_matrix[j][i]}")

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
    validate(adjacency_matrix)
    graph = Graph()

    list_length = len(adjacency_matrix)
    for key in range(list_length):
        graph.add_vertex(key)

    for i in range(list_length):
        for j in range(i + 1, list_length):
            if adjacency_matrix[i][j] == 1:
                graph.add_edge(i, j)

    return graph
