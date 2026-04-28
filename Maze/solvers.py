from models import Maze, Point
from generator import MazeGenerator



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

class OptimizedMazeSolver(MazeSolver):
    def _apply_dead_end_filling(self):
        while True:
            changed = False

            for i in range(1, self.maze.height-1):
                for k in range(1, self.maze.width-1):
                    point = Point(i, k)
                    if point in (self.maze.start_point, self.maze.end_point):
                        continue
                    if not self.maze.is_wall(point):
                        passable = self.maze.get_passable_neighbours(point)
                        if len(passable) == 1:
                            self.maze.set_wall(point)
                            changed = True
            if not changed:
                break

    def solve(self):
        self._apply_dead_end_filling()
        return super().solve()



class SmartMazeSolver(MazeSolver):
    def _get_ordered_neighbours(self, point: Point) -> list[Point]:
        passable = self.maze.get_passable_neighbours(point)
        end = self.maze.end_point
        return sorted(passable, key=lambda p: abs(p.x - end.x) + abs(p.y - end.y))


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
