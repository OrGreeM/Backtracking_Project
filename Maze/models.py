from random import randint

class Point:
    def __init__(self, x, y):

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

        self.start_point = Point(1,1)
        self.end_point = Point(height-2,width-2)

    def is_in_bounds(self, point: Point) -> bool:
        if not isinstance(point, Point):
            return False

        return 0 <= point.x < self.height and 0 <= point.y < self.width



    def is_wall(self, point: Point) -> bool:
        if self.is_in_bounds(point):
            return self.grid[point.x][point.y] == 1
        return True
    def set_passable(self, point: Point):
        if self.is_in_bounds(point):
            self.grid[point.x][point.y] = 0

    def set_wall(self, point):
        if self.is_in_bounds(point):
            self.grid[point.x][point.y] = 1


    def get_passable_neighbours(self, point: Point) -> list[Point]:
        passable = []
        x = point.x
        y = point.y
        for xr, yr in [(-1,0), (1,0), (0,1), (0,-1)]:
            if self.grid[xr+x][yr+y] == 0:
                passable.append(Point(xr+x, yr+y))
        return passable

    def break_random_walls(self, count: int):
        walls_broken = 0
        while walls_broken < count:
            r = randint(1, self.height-2)
            c = randint(1, self.width-2)
            point = Point(r,c)

            if self.is_wall(point):
                self.set_passable(point)
                walls_broken += 1

    def __str__(self, path=None):
        path_set = set(path) if path else set()
        res = []
        for r in range(self.height):
            row_str = ""
            for c in range(self.width):
                current_p = Point(r, c)

                if current_p == self.start_point:
                    row_str += "AA"
                elif current_p == self.end_point:
                    row_str += "BB"
                elif current_p in path_set:
                    row_str += "··"
                elif self.grid[r][c] == 1:
                    row_str += "██"
                else:
                    row_str += "  "
            res.append(row_str)
        return "\n".join(res)

if __name__ == "__main__":
    m = Maze(10, 10)
    print(m)
