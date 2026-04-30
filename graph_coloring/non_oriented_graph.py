"""
not oriented graph implementation
"""

class Vertex:
    """Vertex identified by a key, with weighted edges to neighbors."""

    def __init__(self, key:int | str):
        self.key = key
        self.neighbors: dict = {} # where key is vertex and value is weight

    def add_neighbor(self, other: 'Vertex', weight:any=0):
        """Record an edge to other with the given weight (default 0)."""
        self.neighbors[other] = weight

    def get_neighbors(self):
        """Return neighbor vertices (adjacency map keys)."""
        return self.neighbors.keys()

    def get_neighbor(self, other:'Vertex'):
        """Return the weight to other, or None if not adjacent."""
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
    """Adjacency-list graph: vertices keyed by user labels"""

    def __init__(self):
        self.vertices: dict = {} # where key is key of vertex and value is vertex

    def add_vertex(self, key:int | str):
        """Insert key if missing and return the Vertex for that key."""
        if key not in self.vertices:
            self.vertices[key] = Vertex(key)
        return self.vertices[key]

    def add_edge(self, key1:int|str, key2:int|str, weight:any=0):
        """Add a non directed edge: (key1, key2)"""

        if key1 not in self.vertices:
            self.add_vertex(key1)

        if key2 not in self.vertices:
            self.add_vertex(key2)

        self.vertices[key1].add_neighbor(self.vertices[key2], weight)
        self.vertices[key2].add_neighbor(self.vertices[key1], weight)

    def get_vertex(self, key:int | str):
        """Return the Vertex for key, or None."""
        return self.vertices.get(key, None)

    def get_vertices(self):
        """Return all vertex keys."""
        return self.vertices.keys()

    def __iter__(self):
        return iter(self.vertices.values())

    def __contains__(self, key:any):
        return key in self.vertices
