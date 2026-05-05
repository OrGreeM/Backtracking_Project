from Maze.models import Maze, Point
from Maze.generator import MazeGenerator



class MazeSolver:
    def __init__(self, maze: Maze):
        self.maze = maze
        self.path = []
        self.visited = set()



    def solve(self):
        self._backtrack(self.maze.start_point)
        return self.path


    def _backtrack(self, current_point: Point) -> bool:
        if current_point == self.maze.end_point:
            self.path.append(current_point)
            return True
        self.visited.add(current_point)
        self.path.append(current_point)
        cur_neigh = self.maze.get_passable_neighbours(current_point)

        for neigh in cur_neigh:
            if neigh not in self.visited:
                res = self._backtrack(neigh)
                if res:
                    return True
        self.path.pop()

        return False

    def solve_generator(self):
        self.path = []
        self.visited = set()
        yield from self._backtrack_generator(self.maze.start_point)

    def _backtrack_generator(self, current_point: Point):
        self.visited.add(current_point)
        self.path.append(current_point)

        yield {"current": current_point, "visited": set(self.visited), "path": list(self.path)}

        if current_point == self.maze.end_point:
            return True

        cur_neigh = self.maze.get_passable_neighbours(current_point)
        for neigh in cur_neigh:
            if neigh not in self.visited:
                res = yield from self._backtrack_generator(neigh)
                if res:
                    return True

        self.path.pop()
        yield {"current": current_point, "visited": set(self.visited), "path": list(self.path)}
        return False





class SmartMazeSolver(MazeSolver):
    def _get_ordered_neighbours(self, point: Point) -> list[Point]:
        x, y = point.x, point.y
        ex, ey = self.maze.end_point.x, self.maze.end_point.y
        grid = self.maze.grid

        dx_pref = 1 if ex > x else -1
        dy_pref = 1 if ey > y else -1

        if abs(ex - x) > abs(ey - y):
            directions = [(dx_pref, 0), (0, dy_pref), (0, -dy_pref), (-dx_pref, 0)]
        else:
            directions = [(0, dy_pref), (dx_pref, 0), (-dx_pref, 0), (0, -dy_pref)]

        passable = []
        for dx, dy in directions:
            if grid[x + dx][y + dy] == 0:
                passable.append(Point(x + dx, y + dy))

        return passable


    def _backtrack(self, current_point: Point) -> bool:
        if current_point == self.maze.end_point:
            self.path.append(current_point)
            return True
        self.visited.add(current_point)
        self.path.append(current_point)
        cur_neigh = self._get_ordered_neighbours(current_point)

        for neigh in cur_neigh:
            if neigh not in self.visited:
                res = self._backtrack(neigh)
                if res:
                    return True
        self.path.pop()
        return False

    def _backtrack_generator(self, current_point: Point):
        self.visited.add(current_point)
        self.path.append(current_point)

        yield {"current": current_point, "visited": set(self.visited), "path": list(self.path)}

        if current_point == self.maze.end_point:
            return True

        cur_neigh = self._get_ordered_neighbours(current_point)
        for neigh in cur_neigh:
            if neigh not in self.visited:
                res = yield from self._backtrack_generator(neigh)
                if res:
                    return True

        self.path.pop()
        yield {"current": current_point, "visited": set(self.visited), "path": list(self.path)}
        return False





# if __name__ == "__main__":
#     import sys

#     sys.setrecursionlimit(100_000)
#     generator = MazeGenerator(41, 41)
#     my_maze = generator.generate()

#     solver = MazeSolver(my_maze)
#     solver.solve()
#     print(my_maze.__str__(path=solver.path))
#     print(f"\nFinal Path Distance unoptimized: {len(solver.path)} steps")
#     print(f"Total Explored Cells1: {len(solver.visited)}")


#     solver2 = OptimizedMazeSolver(my_maze)
#     solver2.solve()
#     print(my_maze.__str__(path=solver2.path))
#     print(f"\nFinal Path Distance deadend optimization: {len(solver2.path)} steps")
#     print(f"Total Explored Cells2: {len(solver2.visited)}")
