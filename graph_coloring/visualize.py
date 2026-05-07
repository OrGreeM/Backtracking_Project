"""
Visualization module for graph coloring.

Opens a matplotlib GUI window showing the simple backtracking
algorithm step-by-step on a graph.

A generator version of the simple backtracking is implemented here
(separate from the production algorithm) so visualization does
not affect the original code.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx

from graph_coloring.graph import Graph

COLOR_PALETTE = [
    '#e74c3c', '#3498db', '#2ecc71', '#f39c12',
    '#9b59b6', '#1abc9c', '#e67e22', '#34495e',
    '#16a085', '#c0392b', '#8e44ad', '#27ae60',
]
UNCOLORED = '#ecf0f1'
CURRENT   = '#000000'


def to_networkx(graph:Graph) -> nx.Graph:
    """Convert our Graph instance into a networkx Graph for layout/drawing."""
    nx_g = nx.Graph()
    seen = set()
    for v in graph:
        nx_g.add_node(v.key)
        for nb_key in v.get_neighbors():
            edge = frozenset([v.key, nb_key])
            if edge not in seen:
                seen.add(edge)
                nx_g.add_edge(v.key, nb_key)
    return nx_g

def simple_bt_steps(k:int, graph:Graph):
    """
    Generator version of simple backtracking.
    Yields (current_vertex_key, colors_dict) at each significant step:
        - when a vertex is being considered
        - when a color is assigned
        - when a color is removed (backtrack)
    """
    colors:dict = {}
    vertices = list(graph.get_vertices())

    def _is_valid(vertex_key, color):
        for nb in graph.get_vertex(vertex_key).get_neighbors():
            if colors.get(nb) == color:
                return False
        return True

    def solve(index):
        if index == len(vertices):
            yield (None, dict(colors))
            return True

        vertex_key = vertices[index]
        yield (vertex_key, dict(colors))

        for color in range(k):
            if _is_valid(vertex_key, color):
                colors[vertex_key] = color
                yield (vertex_key, dict(colors))

                if (yield from solve(index + 1)):
                    return True

                del colors[vertex_key]
                yield (vertex_key, dict(colors))

        return False

    yield from solve(0)

def show_animation(graph:Graph, k:int,
                   title:str = 'Simple Backtracking',
                   seed:int = 42,
                   figsize:tuple = (8, 8),
                   interval_ms:int = 400,
                   max_frames:int = 300):
    """
    Open a matplotlib window with a step-by-step animation of
    simple backtracking on `graph` with `k` colors.

    Args:
        graph: our Graph instance.
        k: number of colors available.
        title: window title.
        seed: layout seed for reproducibility.
        figsize: figure size in inches.
        interval_ms: delay between frames in milliseconds.
        max_frames: cap on the number of frames.
    """
    all_frames = list(simple_bt_steps(k, graph))
    if len(all_frames) > max_frames:
        frames = all_frames[:max_frames - 1] + [all_frames[-1]]
        truncated = True
    else:
        frames = all_frames
        truncated = False

    nx_g = to_networkx(graph)
    pos = nx.spring_layout(nx_g, seed=seed)

    fig, ax = plt.subplots(figsize=figsize)

    def render_frame(frame_idx):
        ax.clear()
        ax.set_axis_off()

        current_key, coloring = frames[frame_idx]

        node_colors = []
        edge_colors = []
        edge_widths = []
        for node in nx_g.nodes:
            if node in coloring:
                node_colors.append(COLOR_PALETTE[coloring[node] % len(COLOR_PALETTE)])
            else:
                node_colors.append(UNCOLORED)

            if node == current_key:
                edge_colors.append(CURRENT)
                edge_widths.append(3.5)
            else:
                edge_colors.append('black')
                edge_widths.append(1.0)

        nx.draw_networkx_edges(nx_g, pos, ax=ax, edge_color='#bdc3c7', width=1.5)
        nx.draw_networkx_nodes(nx_g, pos, ax=ax,
                               node_color=node_colors,
                               node_size=600,
                               edgecolors=edge_colors,
                               linewidths=edge_widths)
        nx.draw_networkx_labels(nx_g, pos, ax=ax, font_size=10, font_weight='bold')

        step_label = f'Step {frame_idx + 1}/{len(frames)}'
        if truncated and frame_idx == len(frames) - 1:
            step_label = f'Step {len(all_frames)}/{len(all_frames)} (truncated)'
        if current_key is not None:
            step_label += f'  |  current: {current_key}'
        used_colors = len(set(coloring.values())) if coloring else 0
        step_label += f'  |  colors used: {used_colors}'

        if frame_idx == len(frames) - 1:
            all_colored = current_key is None and len(coloring) == nx_g.number_of_nodes()
            if all_colored:
                step_label += '   ✓ coloring found'
            else:
                step_label += '   ✗ no valid coloring with k colors'

        ax.set_title(f'{title}\n{step_label}', fontsize=12)

    anim = animation.FuncAnimation(
        fig, render_frame,
        frames=len(frames),
        interval=interval_ms,
        repeat=False,
    )

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    from benchmark_suite import build_mycielski
    g = build_mycielski(4)
    show_animation(g, k=4, title='Backtracking algorithm on Mycielski M4 (k = 4 = χ)')
    show_animation(g, k=3, title='Backtracking algorithm on Mycielski M4 (k = 3 < χ)')
