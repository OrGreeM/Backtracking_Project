from generate_graph import generate_graph
from graph import Graph, Vertex
from graph_converter import convert


def main(n:int, p:int|float, k:int, graph:Graph|list[list[int]]=None):
    if graph is None:
        graph = generate_graph(n, p)

    else:
        graph = convert(graph)

    return graph, color_graph(k, graph)


def _select_vertex(domains:dict[int | str, set[int]], colors:dict[int | str, int]) -> int | str:
    unassigned = {key: domain for key, domain in domains.items() if key not in colors}
    return min(unassigned, key=lambda key: len(unassigned[key]))


def _forward_check(vertex:Vertex, color:int, domains:dict[int | str, set[int]],
                   colors:dict[int | str, int]) -> dict[int | str, int] | None:
    removed = {}
    for neighbor in vertex.get_neighbors():
        if neighbor not in colors and color in domains[neighbor]:
            domains[neighbor].discard(color)
            removed.setdefault(neighbor, set()).add(color)

            if not domains[neighbor]:
                return None

    return removed


def _restore_domains(removed:dict[int | str, set[int]], domains:dict[int | str, set[int]]):
    for key, values in removed.items():
        domains[key].update(values)


def color_graph(k:int, graph:Graph):
    colors = {}
    vertices = list(graph.get_vertices())
    domains = {key: set(range(k)) for key in vertices}

    def solve():
        if len(colors) == len(vertices):
            return True

        vertex_key = _select_vertex(domains, colors)
        vertex = graph.get_vertex(vertex_key)

        for color in list(domains[vertex_key]):
            colors[vertex_key] = color
            saved = domains[vertex_key]
            domains[vertex_key] = {color}

            removed = _forward_check(vertex, color, domains, colors)

            if removed is not None:
                if solve():
                    return True

            if removed is not None:
                _restore_domains(removed, domains)

            domains[vertex_key] = saved
            del colors[vertex_key]

        return False

    if solve():
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

    adjacency_matrix = [[0,1,0,1,1,0,0,1,0,0],
                        [1,0,1,0,1,1,0,0,0,0],
                        [0,1,0,0,1,1,0,1,0,0],
                        [1,0,0,0,0,0,1,0,0,0],
                        [1,1,1,0,0,0,1,1,1,0],
                        [0,1,1,0,0,0,0,0,1,1],
                        [0,1,0,0,1,0,0,0,0,0],
                        [1,0,1,0,1,0,0,0,1,0],
                        [0,0,0,0,1,1,0,1,0,1],
                        [0,0,0,0,0,1,0,0,1,0]
    ]

    g, colored_graph = main(0, 0, 10, adjacency_matrix)
    print(g)
    print(colored_graph)
