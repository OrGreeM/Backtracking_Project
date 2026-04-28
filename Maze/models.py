

class Point:
    def __init__(self, x, y):
        # x - row, y - col
        self.x = x
        self.y = y

    def __eq__(self, other: "Point"):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f"({self.x},{self.y})"

    def __repr__(self):
        return f"({self.x},{self.y})"


class Maze:
    def __init__(self, height, width):
        self.height = height
        self.width = width

        self.grid = [[1 for _ in range(width)] for _ in range(height)]

    def is_in_bounds(self, point: Point) -> bool:
        if not isinstance(point, Point):
            return False
            #raise ValueError("is_in_bounds expects a Point class")
        return 0 <= point.x < self.height and 0 <= point.y < self.width
        #return IndexError("Point out of bounds")


    def is_wall(self, point: Point) -> bool:
        if self.is_in_bounds(point):
            return self.grid[point.x][point.y] == 1
        return True
    def set_passable(self, point: Point):
        if self.is_in_bounds(point):
            self.grid[point.x][point.y] = 0

    def get_passable_neighbours(self, point: Point) -> list[Point]:
        passable = []
        x = point.x
        y = point.y
        for xr, yr in [(-1,0), (1,0), (0,1), (0,-1)]:
            n_p = Point(xr+x, yr+y)
            if not self.is_wall(n_p):
                passable.append(n_p)
        return passable


    def __str__(self):
        res = []
        for row in self.grid:
            row_str = "".join(["██" if cell == 1 else "  " for cell in row])
            res.append(row_str)
        return "\n".join(res)

if __name__ == "__main__":
    m = Maze(10, 10)
    print(m)
