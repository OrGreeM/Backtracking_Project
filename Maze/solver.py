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


if __name__ == "__main__":
    import sys

    sys.setrecursionlimit(100_000)
    generator = MazeGenerator(11, 11)
    my_maze = generator.generate()

    solver = MazeSolver(my_maze)
    solver.solve()

    print(my_maze.__str__(path=solver.path))
    print(f"\nFinal Path Distance: {len(solver.path)} steps")
    print(f"Total Explored Cells: {len(solver.visited)}")
