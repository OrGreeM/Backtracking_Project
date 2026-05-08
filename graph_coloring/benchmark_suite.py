"""
A fixed set of benchmark graphs for comparing graph coloring algorithms.

Includes:
    - Large structured graphs with known chromatic number
      (Kn, complete bipartite, cycles, trees) — built programmatically.
    - Random Erdős–Rényi graphs at the phase transition (k = χ or
      k = χ - 1) — this is where MRV+FC outperforms Simple Backtracking
      by orders of magnitude.

Each entry is a tuple (name, graph, k, expected_chromatic).
`expected_chromatic` is None when the chromatic number is unknown.
"""

from generate_graph import generate_graph
from graph import Graph


def build_complete(n:int) -> Graph:
    """Complete graph Kn. χ = n."""
    g = Graph()
    for i in range(n):
        g.add_vertex(i)
    for i in range(n):
        for j in range(i + 1, n):
            g.add_edge(i, j)
    return g


def build_cycle(n:int) -> Graph:
    """Cycle Cn. χ = 2 if n even, 3 if n odd."""
    g = Graph()
    for i in range(n):
        g.add_vertex(i)
    for i in range(n):
        g.add_edge(i, (i + 1) % n)
    return g


def build_complete_bipartite(left:int, right:int) -> Graph:
    """Complete bipartite K_{left,right}. χ = 2."""
    g = Graph()
    for i in range(left + right):
        g.add_vertex(i)
    for i in range(left):
        for j in range(left, left + right):
            g.add_edge(i, j)
    return g


def build_path_tree(n:int) -> Graph:
    """Path graph (a tree) on n vertices. χ = 2."""
    g = Graph()
    for i in range(n):
        g.add_vertex(i)
    for i in range(n - 1):
        g.add_edge(i, i + 1)
    return g


def build_mycielski(k:int) -> Graph:
    """
    Build the k-th Mycielski graph M_k via recursive construction.

    Starts from M_2 = K_2 and applies the Mycielski transformation
    (k - 2) times. Each transformation increases the chromatic number
    by 1 without introducing any triangle.

    Properties:
        M_2: n=2,  m=1,   χ=2
        M_3: n=5,  m=5,   χ=3   (= C_5)
        M_4: n=11, m=20,  χ=4   (Grötzsch graph)
        M_5: n=23, m=71,  χ=5
        M_6: n=47, m=236, χ=6

    All M_k for k >= 2 are triangle-free.

    Args:
        k (int): Index in the Mycielski sequence (k >= 2).

    Returns:
        Graph: The k-th Mycielski graph.
    """
    if k < 2:
        raise ValueError("Mycielski sequence starts at k=2 (K_2)")

    g = Graph()
    g.add_vertex(0)
    g.add_vertex(1)
    g.add_edge(0, 1)
    for _ in range(k - 2):
        g = _mycielski_step(g)

    return g


def _mycielski_step(g:Graph) -> Graph:
    """
    One Mycielski transformation: given graph G with vertices v_1..v_n
    and edges, produce μ(G) with:
        - original vertices  v_1..v_n
        - shadow vertices    u_1..u_n  (one per original)
        - one apex vertex    w
    Edges:
        - all original (v_i, v_j) edges
        - for each original (v_i, v_j): also (u_i, v_j) and (v_i, u_j)
        - (u_i, w) for every i

    The result is reindexed to use clean integer keys 0..2n.
    """
    original = list(g.get_vertices())
    n = len(original)

    orig_idx = {v: i for i, v in enumerate(original)}
    shadow_idx = {v: n + i for i, v in enumerate(original)}
    apex_idx = 2 * n

    new_g = Graph()
    for k in range(2 * n + 1):
        new_g.add_vertex(k)

    seen = set()
    for v in original:
        vi = orig_idx[v]
        for nb in g.get_vertex(v).get_neighbors():
            ni = orig_idx[nb]
            edge = (min(vi, ni), max(vi, ni))
            if edge in seen:
                continue
            seen.add(edge)
            new_g.add_edge(vi, ni)
            new_g.add_edge(shadow_idx[v], ni)
            new_g.add_edge(vi, shadow_idx[nb])

    # Apex connects to every shadow
    for v in original:
        new_g.add_edge(shadow_idx[v], apex_idx)

    return new_g


# Each entry: (name, graph, k_to_try, expected_chromatic)

BENCHMARK_CASES = [
    ('K15',                build_complete(15),                    15, 15),
    ('C51_odd_cycle',      build_cycle(51),                       10,  3),
    ('C100_even_cycle',    build_cycle(100),                      10,  2),
    ('K20,20_bipartite',   build_complete_bipartite(20, 20),      10,  2),
    ('tree_30',            build_path_tree(30),                   10,  2),
    ('random_n=20_easy',   generate_graph(20, 0.3, seed=1),       10, None),
    ('random_n=50_easy',   generate_graph(50, 0.3, seed=2),       15, None),
    ('random_n=100_easy',  generate_graph(100, 0.3, seed=3),      20, None),
    ('phase_n=30_tight',   generate_graph(30, 0.5, seed=1),        7,  7),
    ('phase_n=40_tight',   generate_graph(40, 0.4, seed=1),        7,  7),
    ('phase_n=30_impossible', generate_graph(30, 0.5, seed=1),     6,  7),
    ('big_sparse_n=300',   generate_graph(300, 0.05, seed=42),    10, None),
    ('big_sparse_n=500',   generate_graph(500, 0.02, seed=42),    10, None),
    ('big_dense_n=300',    generate_graph(300, 0.5,  seed=42),    80, None),
    ('large_dense_n=500',    generate_graph(500, 0.55,  seed=42),    80, None),
    ('mycielski_M10',       build_mycielski(10),                     10,  10),
]
