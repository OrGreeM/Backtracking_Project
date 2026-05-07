from models import Maze, Point
from generator import MazeGenerator
from collections import deque
import heapq



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

class BFSMazeSolver(MazeSolver):
    def _reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def solve(self):
        self.path = []
        self.visited = set()

        start = self.maze.start_point
        queue = deque([start])
        self.visited.add(start)
        came_from = {}

        while queue:
            current_point = queue.popleft()

            if current_point == self.maze.end_point:
                self.path = self._reconstruct_path(came_from, current_point)
                return self.path

            for neigh in self.maze.get_passable_neighbours(current_point):
                if neigh not in self.visited:
                    self.visited.add(neigh)
                    came_from[neigh] = current_point
                    queue.append(neigh)

        return []

    def solve_generator(self):
        self.path = []
        self.visited = set()
        yield from self._bfs_generator()

    def _bfs_generator(self):
        start = self.maze.start_point
        queue = deque([start])
        self.visited.add(start)
        came_from = {}

        while queue:
            current_point = queue.popleft()
            self.path = self._reconstruct_path(came_from, current_point)

            yield {"current": current_point, "visited": set(self.visited), "path": list(self.path)}

            if current_point == self.maze.end_point:
                return True

            for neigh in self.maze.get_passable_neighbours(current_point):
                if neigh not in self.visited:
                    self.visited.add(neigh)
                    came_from[neigh] = current_point
                    queue.append(neigh)

        yield {"current": current_point, "visited": set(self.visited), "path": list(self.path)}
        return False


class AStarMazeSolver(MazeSolver):
    def _heuristic(self, p1: Point, p2: Point) -> int:
        return abs(p1.x - p2.x) + abs(p1.y - p2.y)

    def _reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def solve(self):
        self.path = []
        self.visited = set()

        start = self.maze.start_point
        end = self.maze.end_point

        counter = 0
        queue = [(self._heuristic(start, end), counter, start)]
        g_scores = {start: 0}
        came_from = {}

        while queue:
            _, _, current_point = heapq.heappop(queue)

            if current_point in self.visited:
                continue

            self.visited.add(current_point)

            if current_point == end:
                self.path = self._reconstruct_path(came_from, current_point)
                return self.path

            cur_g = g_scores[current_point]
            for neigh in self.maze.get_passable_neighbours(current_point):
                tentative_g = cur_g + 1

                if neigh not in g_scores or tentative_g < g_scores[neigh]:
                    g_scores[neigh] = tentative_g
                    came_from[neigh] = current_point
                    counter += 1
                    heapq.heappush(queue, (tentative_g + self._heuristic(neigh, end), counter, neigh))

        return []

    def solve_generator(self):
        self.path = []
        self.visited = set()
        yield from self._astar_generator()

    def _astar_generator(self):
        start = self.maze.start_point
        end = self.maze.end_point

        counter = 0
        queue = [(self._heuristic(start, end), counter, start)]
        g_scores = {start: 0}
        came_from = {}

        while queue:
            _, _, current_point = heapq.heappop(queue)

            if current_point in self.visited:
                continue

            self.visited.add(current_point)
            self.path = self._reconstruct_path(came_from, current_point)

            yield {"current": current_point, "visited": set(self.visited), "path": list(self.path)}

            if current_point == end:
                return True

            cur_g = g_scores[current_point]
            for neigh in self.maze.get_passable_neighbours(current_point):
                tentative_g = cur_g + 1

                if neigh not in g_scores or tentative_g < g_scores[neigh]:
                    g_scores[neigh] = tentative_g
                    came_from[neigh] = current_point
                    counter += 1
                    heapq.heappush(queue, (tentative_g + self._heuristic(neigh, end), counter, neigh))

        yield {"current": current_point, "visited": set(self.visited), "path": list(self.path)}
        return False
