"""
module helps to convert an adjacency matrix
to self implementation of graph in module graph.py
"""

from graph import Graph

def convert(list_of_contiguity: list[list[int]]) -> Graph:
    """
    Converts an adjacency matrix into a Graph instance.

    Assumes an undirected graph represented by a square matrix,
    where 1 indicates an edge between vertices and 0 means no edge.

    Args:
        list_of_contiguity (list[list[int]]): Adjacency matrix.

    Returns:
        Graph: Constructed graph instance.
    """
    graph = Graph()

    list_length= len(list_of_contiguity)
    for key in range(list_length):
        graph.add_vertex(key)

    for i in range(list_length):
        for j in range(i + 1, list_length):
            if list_of_contiguity[i][j] == 1:
                graph.add_edge(i, j)

    return graph


if __name__ == '__main__':
    adjacency_matrix = [[0,0,1,0,1],
              [0,0,0,0,1],
              [1,0,0,1,1],
              [0,0,1,0,1],
              [1,1,1,1,0]
    ]

    g = convert(adjacency_matrix)

    print(adjacency_matrix)
    print(g)
