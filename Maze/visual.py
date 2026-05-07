import pygame
import sys
from models import Point, Maze
from generator import MazeGenerator
from solvers import SmartMazeSolver, MazeSolver, BFSMazeSolver, AStarMazeSolver

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

ALGORITHMS = [
    ("DFS (класичний)", MazeSolver),
    ("Smart DFS (евристика)", SmartMazeSolver),
    ("BFS (пошук у ширину)", BFSMazeSolver),
    ("A* (A-Star)", AStarMazeSolver),
]

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


def draw_ui(screen, algo_name, is_solving, visited_count, path_len):
    """Малює UI-панель зверху з інформацією про алгоритм."""
    font = pygame.font.SysFont("Arial", 18)

    overlay = pygame.Surface((WIDTH, 30))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    status = "Пошук..." if is_solving else "Готово!"
    info = f"{algo_name}  |  {status}  |  Відвідано: {visited_count}  |  Шлях: {path_len}  |  [1-4] змінити алгоритм  [R] перезапуск"
    text = font.render(info, True, (255, 255, 255))
    screen.blit(text, (10, 5))


def main():
    sys.setrecursionlimit(100_000)
    print("Генерація лабіринту...")
    generator = MazeGenerator(MAZE_SIZE, MAZE_SIZE)
    my_maze = generator.generate()

    my_maze.break_random_walls(MAZE_SIZE * MAZE_SIZE // 100)

    current_algo_idx = 1  # Smart DFS за замовчуванням
    algo_name, SolverClass = ALGORITHMS[current_algo_idx]
    solver = SolverClass(my_maze)
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
    visited_count = 0
    path_len = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                new_idx = None
                if event.key == pygame.K_1:
                    new_idx = 0
                elif event.key == pygame.K_2:
                    new_idx = 1
                elif event.key == pygame.K_3:
                    new_idx = 2
                elif event.key == pygame.K_4:
                    new_idx = 3
                elif event.key == pygame.K_r:
                    new_idx = current_algo_idx  # перезапуск поточного

                if new_idx is not None:
                    current_algo_idx = new_idx
                    algo_name, SolverClass = ALGORITHMS[current_algo_idx]
                    solver = SolverClass(my_maze)
                    solver_generator = solver.solve_generator()
                    state = None
                    is_solving = True
                    visited_count = 0
                    path_len = 0
                    pygame.display.set_caption(f"Maze Visualizer — {algo_name}")

        if is_solving:
            try:
                state = next(solver_generator)
                visited_count = len(state.get("visited", set()))
                path_len = len(state.get("path", []))
            except StopIteration:
                is_solving = False
                print(f"[{algo_name}] Шлях знайдено! Відвідано: {visited_count}, Довжина шляху: {path_len}")

        draw_maze(screen, my_maze, cell_size, state)
        draw_ui(screen, algo_name, is_solving, visited_count, path_len)

        pygame.display.flip()

        clock.tick(FPS)

if __name__ == "__main__":
    main()
