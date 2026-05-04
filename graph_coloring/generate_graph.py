"""
Module created for graph generation.
"""
import random
from graph_coloring.graph import Graph


def generate_graph(number_of_vertices:int, chance_of_edge_generation:float | int) -> Graph:
    """
    Generates a random undirected graph.

    Vertices are labeled from 0 to `number_of_vertices` - 1.
    For each pair of distinct vertices, an edge is added
    with probability `chance_of_edge_generation`.

    Args:
        number_of_vertices (int): Number of vertices in the graph.
        chance_of_edge_generation (float | int): Probability of creating an edge
            between two vertices (value between 0 and 1).

    Returns:
        Graph: A randomly generated graph with edges.
    """
    graph = Graph()

    for k in range(number_of_vertices):
        graph.add_vertex(k)

    for i in range(number_of_vertices):
        for j in range(i + 1, number_of_vertices):
            if random.random() < chance_of_edge_generation:
                graph.add_edge(i, j)

    return graph

if __name__ == '__main__':
    g = generate_graph(7, 0.4)
    print(g)
