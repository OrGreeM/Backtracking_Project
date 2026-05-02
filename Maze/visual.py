import pygame
import sys
from models import Point, Maze
from generator import MazeGenerator
from solvers import SmartMazeSolver, MazeSolver

WIDTH, HEIGHT = 800, 800
FPS = 30
MAZE_SIZE = 41

WALL_COLOR = (40, 40, 40)       # Темно-сірий
PATH_COLOR = (240, 240, 240)    # Світло-сірий
VISITED_COLOR = (173, 216, 230) # Світло-блакитний (де алгоритм вже був)
CURRENT_PATH = (0, 0, 255)      # Синій (поточний правильний шлях)
HEAD_COLOR = (255, 0, 0)        # Червоний (де алгоритм знаходиться ПРЯМО ЗАРАЗ)
START_COLOR = (0, 255, 0)       # Зелений
END_COLOR = (255, 165, 0)       # Помаранчевий

def draw_maze(screen, maze, cell_size, state):
    """Малює лабіринт та поточний стан алгоритму."""
    screen.fill(WALL_COLOR) # Заливаємо фон кольором стін

    for r in range(maze.height):
        for c in range(maze.width):
            if not maze.is_wall(Point(r, c)):
                rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, PATH_COLOR, rect)

    if state:
        visited = state.get("visited", set())
        path = state.get("path", [])
        current = state.get("current", None)

        for p in visited:
            rect = pygame.Rect(p.y * cell_size, p.x * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, VISITED_COLOR, rect)

        for p in path:
            rect = pygame.Rect(p.y * cell_size, p.x * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, CURRENT_PATH, rect)

        if current:
            rect = pygame.Rect(current.y * cell_size, current.x * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, HEAD_COLOR, rect)

    start_rect = pygame.Rect(maze.start_point.y * cell_size, maze.start_point.x * cell_size, cell_size, cell_size)
    pygame.draw.rect(screen, START_COLOR, start_rect)

    end_rect = pygame.Rect(maze.end_point.y * cell_size, maze.end_point.x * cell_size, cell_size, cell_size)
    pygame.draw.rect(screen, END_COLOR, end_rect)


def main():
    sys.setrecursionlimit(100_000)
    print("Генерація лабіринту...")
    generator = MazeGenerator(MAZE_SIZE, MAZE_SIZE)
    my_maze = generator.generate()

    my_maze.break_random_walls(MAZE_SIZE * MAZE_SIZE // 100)

    solver = SmartMazeSolver(my_maze)
    solver_generator = solver.solve_generator()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Maze Backtracking Visualizer")
    clock = pygame.time.Clock()

    cell_w = WIDTH // my_maze.width
    cell_h = HEIGHT // my_maze.height
    cell_size = min(cell_w, cell_h)

    state = None
    is_solving = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if is_solving:
            try:
                state = next(solver_generator)
            except StopIteration:
                is_solving = False
                print("Шлях знайдено (або алгоритм завершив роботу)!")

        draw_maze(screen, my_maze, cell_size, state)

        pygame.display.flip()

        clock.tick(FPS)

if __name__ == "__main__":
    main()
