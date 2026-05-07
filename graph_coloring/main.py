"""
CLI for the graph_coloring lab.

Run from the project root:

    python graph_coloring/main.py
    python graph_coloring/main.py --n 15 --p 0.3 --k 3
    python graph_coloring/main.py --n 20 --p 0.4 --k 4
    python graph_coloring/main.py --file my_graph.txt --k 3

Generates a random graph (default) or loads one from an adjacency-matrix
file, then opens a matplotlib animation of simple backtracking.

Adjacency-matrix file format:
    one row per line, entries 0/1 separated by spaces or commas.
"""

import argparse

from generate_graph import generate_graph
from graph_converter import convert
from visualize import show_animation


def _read_matrix(path):
    matrix = []
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = [int(x) for x in line.replace(',', ' ').split()]
            matrix.append(row)
    return matrix


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='graph_coloring',
        description='Color a graph with backtracking and watch the animation.',
    )
    parser.add_argument('--file', default=None,
                        help='path to an adjacency-matrix file '
                             '(0/1 entries, rows on separate lines, '
                             'separators: spaces or commas). '
                             'If omitted, a random graph is generated.')
    parser.add_argument('--n', type=int, default=15,
                        help='vertices in the random graph (default: 15)')
    parser.add_argument('--p', type=float, default=0.3,
                        help='edge probability for the random graph (default: 0.3)')
    parser.add_argument('--k', type=int, default=4,
                        help='number of colors (default: 4)')

    args = parser.parse_args(argv)

    if args.file:
        graph = convert(_read_matrix(args.file))
        source = f'file: {args.file}'
    else:
        graph = generate_graph(args.n, args.p)
        source = f'random n={args.n} p={args.p}'

    show_animation(graph, k=args.k, title=f'Backtracking ({source}, k={args.k})')


if __name__ == '__main__':
    main()
