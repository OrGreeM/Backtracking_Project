"""
Module created for graph generation.
"""
import random
from graph import Graph


def generate_graph(number_of_vertices:int, chance_of_edge_generation:float | int) -> Graph:
    """...."""
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
