"""
not oriented graph implementation
"""

class Vertex:
    """Vertex identified by a key, with weighted edges to neighbors."""

    def __init__(self, key):
        self.key: any = key
        self.neighbors: dict[Vertex, any] = {}

    def add_neighbor(self, other: 'Vertex', weight:any=0):
        """Record an edge to ``other`` with the given weight (default 0)."""
        self.neighbors[other] = weight

    def get_neighbors(self):
        """Return neighbor vertices (adjacency map keys)."""
        return self.neighbors.keys()

    def get_neighbor(self, other:'Vertex'):
        """Return the weight to ``other``, or ``None`` if not adjacent."""
        return self.neighbors.get(other, None)

    def __repr__(self):
        return f"Vertex({self.key!r})"

    def __str__(self):
        pairs = [(x.key, self.neighbors[x]) for x in self.neighbors]
        return f"{self.key} connected to: {pairs}"

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other:'Vertex'):
        return isinstance(other, Vertex) and self.key == other.key


class Graph:
    """Adjacency-list graph: vertices keyed by user labels (e.g. strings)."""

    def __init__(self):
        self.vertices: dict[any, Vertex] = {}

    def add_vertex(self, key:any):
        """Insert ``key`` if missing and return the ``Vertex`` for that key."""
        if key not in self.vertices:
            self.vertices[key] = Vertex(key)
        return self.vertices[key]

    def add_edge(self, vertex1:Vertex, vertex2:Vertex, weight:any=0):
        """Add a non directed edge ``vertex1`` - ``vertex2``"""

        vertex1.add_neighbor(vertex2, weight)
        vertex2.add_neighbor(vertex1, weight)


    def remove_vertex(self, key:any):
        """Remove the vertex ``key`` and any incident edges."""
        vertex_to_remove = self.get_vertex(key)
        if vertex_to_remove:
            for vertex in self.vertices.values():
                vertex.neighbors.pop(vertex_to_remove, None)
            del self.vertices[key]


    def get_vertex(self, key:any):
        """Return the ``Vertex`` for ``key``, or ``None``."""
        return self.vertices.get(key, None)

    def get_vertices(self):
        """Return all vertex keys."""
        return self.vertices.keys()

    def __iter__(self):
        return iter(self.vertices.values())

    def __contains__(self, key:any):
        return key in self.vertices
