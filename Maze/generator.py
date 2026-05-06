from Maze.models import Maze, Point
import random

class MazeGenerator:
    def __init__(self, height, width):
        if not height % 2 or not width% 2:
            raise ValueError("Cannot generate a maze without sizes being odd number")

        self.maze = Maze(height, width)


    def generate(self) -> Maze:
        start_point = Point(1,1)
        self.maze.set_passable(start_point)

        stack = [start_point]

        while stack:
            current = stack[-1]
            unvisited_neighbors = []

            for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
                p = Point(current.x + dx, current.y + dy)

                if self.maze.is_in_bounds(p) and self.maze.is_wall(p):
                    unvisited_neighbors.append(p)
            if unvisited_neighbors:
                chosen = random.choice(unvisited_neighbors)

                mid_x = (chosen.x + current.x)//2
                mid_y = (chosen.y + current.y)//2

                new_passable = Point(mid_x, mid_y)


                self.maze.set_passable(new_passable)
                self.maze.set_passable(chosen)


                stack.append(chosen)
            else:
                stack.pop()
        self._destroy_random_walls()
        return self.maze

    def _destroy_random_walls(self, percentage=0.05):
        inner_walls = []
        for r in range(1, self.maze.height - 1):
            for c in range(1, self.maze.width - 1):
                p = Point(r, c)
                if self.maze.is_wall(p):
                    inner_walls.append(p)
                    
        num_to_destroy = int(len(inner_walls) * percentage)
        if num_to_destroy > 0:
            walls_to_destroy = random.sample(inner_walls, num_to_destroy)
            for w in walls_to_destroy:
                self.maze.set_passable(w)


if __name__ == "__main__":
    generator = MazeGenerator(21, 21)
    my_maze = generator.generate()
    print(my_maze)
