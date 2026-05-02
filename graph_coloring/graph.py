"""
Implementation of graph

Graph follows be next rules:
    1. Graph contains dictionary, where each pair is
    Key of vertex : vertex
    2. Each vertex is contain inforamtion of its key and neighboors
    3. Graph is not weighted
    4. Graph is non oriented
"""

class Vertex:
    """Vertex identified by a key, with weighted edges to neighbors."""

    def __init__(self, key:int | str):
        self.key = key
        self.neighbors: dict = {} # where key is vertex' key and value is vertex

    def add_neighbor(self, other: 'Vertex'):
        """Record an edge to other with the given weight."""
        self.neighbors[other.key] = other

    def get_neighbors(self):
        """Return neighbors' keys"""
        return self.neighbors.keys()

    def __str__(self):
        pairs = list(self.neighbors)
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

    def add_edge(self, key1:int|str, key2:int|str):
        """Add a non directed edge: (key1, key2)"""

        if key1 not in self.vertices:
            self.add_vertex(key1)

        if key2 not in self.vertices:
            self.add_vertex(key2)

        self.vertices[key1].add_neighbor(self.vertices[key2])
        self.vertices[key2].add_neighbor(self.vertices[key1])

    def get_vertex(self, key:int | str):
        """Return the Vertex for key, or None."""
        return self.vertices.get(key, None)

    def get_vertices(self):
        """Return all vertex keys."""
        return self.vertices.keys()

    def __iter__(self):
        return iter(self.vertices.values())

    def __contains__(self, key:int | str):
        return key in self.vertices

    def __str__(self):
        result = []
        for vertex in self:
            result.append(str(vertex))

        return '\n'.join(result)
