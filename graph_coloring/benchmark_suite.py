"""
A small, fixed set of benchmark graphs for comparing
graph coloring algorithms.

Structured graphs (cycles, bipartite, complete, tree)
are defined as adjacency matrices. Larger and denser
random graphs are built via `generate_graph`.

Each entry is a tuple (name, graph, k, expected_chromatic).
`expected_chromatic` is None when the chromatic number
is not known up front.
"""

from generate_graph import generate_graph
from graph_converter import convert



K5 = [
    [0, 1, 1, 1, 1],
    [1, 0, 1, 1, 1],
    [1, 1, 0, 1, 1],
    [1, 1, 1, 0, 1],
    [1, 1, 1, 1, 0],
]

C7 = [
    [0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0],
]

C8 = [
    [0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0],
]

K33 = [
    [0, 0, 0, 1, 1, 1],
    [0, 0, 0, 1, 1, 1],
    [0, 0, 0, 1, 1, 1],
    [1, 1, 1, 0, 0, 0],
    [1, 1, 1, 0, 0, 0],
    [1, 1, 1, 0, 0, 0],
]

TREE7 = [
    [0, 1, 1, 0, 0, 0, 0],
    [1, 0, 0, 1, 1, 0, 0],
    [1, 0, 0, 0, 0, 1, 1],
    [0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0],
]


# Each entry: (name, graph, count of colors to try: k, expected chromatic or None)
BENCHMARK_CASES = [
    ('K5',                    convert(K5),                            5,  5),
    ('C7_odd_cycle',          convert(C7),                            3,  3),
    ('C8_even_cycle',         convert(C8),                            2,  2),
    ('K3,3_bipartite',        convert(K33),                           2,  2),
    ('tree_7',                convert(TREE7),                         2,  2),
    ('random_small_sparse',   generate_graph(20, 0.3, seed=1),        6,  None),
    ('random_medium',         generate_graph(50, 0.3, seed=2),       10,  None),
    ('random_large',          generate_graph(100, 0.3, seed=3),      15,  None),
    ('random_large',         generate_graph(200, 0.3, seed=5),      25,  None),
    ('random_medium_dense',   generate_graph(50, 0.7, seed=4),       25,  None),
    ('random_large_dense',   generate_graph(300, 0.7, seed=6),      60,  None),
    ('random_huge',           generate_graph(500, 0.3, seed=7),      30,  None),
    ('random_huge_dense',     generate_graph(500, 0.5, seed=8),      80,  None),
]


if __name__ == '__main__':
    print(f"{'name':<25} {'n':>5} {'expected χ':>12}")
    print('─' * 45)
    for name, graph, k, chi in BENCHMARK_CASES:
        n = len(list(graph.get_vertices()))
        chi_str = str(chi) if chi is not None else '?'
        print(f"{name:<25} {n:>5} {chi_str:>12}")
