import sys
import os
import pygame

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models import Maze, Point

COLOR_BG = (15, 23, 42)          # Deep slate background
COLOR_WALL = (30, 41, 59)        # Dark navy gray for walls
COLOR_PATH = (15, 23, 42)        # Same as BG or slightly lighter for path (slate)
COLOR_VISITED = (147, 197, 253)  # Soft glowing sky blue for visited
COLOR_ACTIVE_PATH = (52, 211, 153) # Vibrant mint green for the final/current path
COLOR_HEAD = (244, 63, 94)       # Hot pink/crimson for current explorer node
COLOR_START = (59, 130, 246)     # Deep blue for Start
COLOR_END = (239, 68, 68)        # Vibrant red for End
COLOR_TEXT = (241, 245, 249)     # Soft white for text
COLOR_PANEL = (30, 41, 59)       # Dark panel background for info text
COLOR_BORDER = (71, 85, 105)     # Border color

def draw_maze_pygame(screen, maze: Maze, state: dict, cell_size: int, offset_y: int, offset_x: int = 0):
    """
    Renders the maze and current pathfinding states onto the pygame screen.
    """
    # 1. Draw maze walls and empty channels
    for r in range(maze.height):
        for c in range(maze.width):
            rect = pygame.Rect(offset_x + c * cell_size, offset_y + r * cell_size, cell_size, cell_size)
            if maze.grid[r][c] == 1:
                pygame.draw.rect(screen, COLOR_WALL, rect)
            else:
                pygame.draw.rect(screen, COLOR_PATH, rect)

    # 2. Draw visited cells (from state)
    if state and "visited" in state:
        for p in state["visited"]:
            # Skip start and end for specialized colors
            if p == maze.start_point or p == maze.end_point:
                continue
            rect = pygame.Rect(offset_x + p.y * cell_size, offset_y + p.x * cell_size, cell_size, cell_size)
            # Add a small inner margin for a rounded/glowing card effect
            pygame.draw.rect(screen, COLOR_VISITED, rect.inflate(-1, -1), border_radius=max(1, cell_size // 4))

    # 3. Draw current active path
    if state and "path" in state:
        for p in state["path"]:
            if p == maze.start_point or p == maze.end_point:
                continue
            rect = pygame.Rect(offset_x + p.y * cell_size, offset_y + p.x * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, COLOR_ACTIVE_PATH, rect.inflate(-1, -1), border_radius=max(1, cell_size // 4))

    # 4. Draw Start Point (AA) and End Point (BB) with nice circular markers
    for p, color, label in [(maze.start_point, COLOR_START, "S"), (maze.end_point, COLOR_END, "E")]:
        center_x = offset_x + p.y * cell_size + cell_size // 2
        center_y = offset_y + p.x * cell_size + cell_size // 2
        radius = max(3, int(cell_size * 0.4))
        pygame.draw.circle(screen, color, (center_x, center_y), radius)
        # Draw a nice thin white border around start/end
        pygame.draw.circle(screen, COLOR_TEXT, (center_x, center_y), radius, 1)

    # 5. Draw active explorer head (current node)
    if state and "current" in state:
        p = state["current"]
        center_x = offset_x + p.y * cell_size + cell_size // 2
        center_y = offset_y + p.x * cell_size + cell_size // 2
        radius = max(4, int(cell_size * 0.45))
        pygame.draw.circle(screen, COLOR_HEAD, (center_x, center_y), radius)

def run_pygame_visualizer(maze: Maze, solver_class, algo_name: str):
    """
    Runs the interactive Pygame window to visualize the pathfinding process.
    """
    pygame.init()
    pygame.display.set_caption(f"Maze Pathfinding: {algo_name}")

    # Layout configurations
    info_panel_height = 80
    screen_width = 800
    screen_height = 800 + info_panel_height

    # Calculate optimal cell size based on maze size to fit inside 800x800
    cell_size = min(screen_width // maze.width, 800 // maze.height)
    if cell_size < 1:
        cell_size = 1

    # Recalculate screen size exactly to fit the grid perfectly
    grid_width = maze.width * cell_size
    grid_height = maze.height * cell_size
    screen_width = grid_width
    screen_height = grid_height + info_panel_height

    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()

    # Font initialization
    try:
        font_large = pygame.font.SysFont("Inter", 20, bold=True)
        font_small = pygame.font.SysFont("Inter", 14)
    except Exception:
        font_large = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 16)

    # Initialize pathfinder generator
    solver = solver_class(maze)
    generator = solver.solve_generator()

    state = {
        "current": maze.start_point,
        "visited": {maze.start_point},
        "path": [maze.start_point]
    }

    running = True
    paused = False
    finished = False
    speed_steps_per_frame = 1  # How many steps we run per frame (for faster speed)
    fps = 30                  # Standard target framerate

    # Timing and statistics
    start_time = pygame.time.get_ticks()
    elapsed_time_ms = 0
    steps_count = 0

    while running:
        # Handle user events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_UP or event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
                    speed_steps_per_frame = min(50, speed_steps_per_frame + 1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_KP_MINUS or event.key == pygame.K_MINUS:
                    speed_steps_per_frame = max(1, speed_steps_per_frame - 1)
                elif event.key == pygame.K_r:
                    # Restart simulation
                    solver = solver_class(maze)
                    generator = solver.solve_generator()
                    state = {
                        "current": maze.start_point,
                        "visited": {maze.start_point},
                        "path": [maze.start_point]
                    }
                    finished = False
                    paused = False
                    steps_count = 0
                    start_time = pygame.time.get_ticks()

        # Step the generator if not paused or finished
        if not paused and not finished:
            for _ in range(speed_steps_per_frame):
                try:
                    next_state = next(generator)
                    if next_state:
                        state = next_state
                        steps_count += 1
                except StopIteration:
                    finished = True
                    break

            if not finished:
                elapsed_time_ms = pygame.time.get_ticks() - start_time

        # Draw frame background
        screen.fill(COLOR_BG)

        # 1. Draw the maze, path, and nodes
        draw_maze_pygame(screen, maze, state, cell_size, offset_y=info_panel_height, offset_x=0)

        # 2. Draw top information panel
        panel_rect = pygame.Rect(0, 0, screen_width, info_panel_height)
        pygame.draw.rect(screen, COLOR_PANEL, panel_rect)
        pygame.draw.line(screen, COLOR_BORDER, (0, info_panel_height - 1), (screen_width, info_panel_height - 1), 2)

        # Labels & Stats
        title_text = font_large.render(f"Алгоритм: {algo_name}", True, COLOR_TEXT)
        screen.blit(title_text, (15, 10))

        status_str = "Пошук шляху..."
        status_color = (252, 211, 77)  # Warm amber
        if paused:
            status_str = "Пауза"
            status_color = (156, 163, 175) # Cool grey
        elif finished:
            if state and "path" in state and len(state["path"]) > 1:
                status_str = "Шлях знайдено! ✓"
                status_color = COLOR_ACTIVE_PATH
            else:
                status_str = "Шлях не існує! ✗"
                status_color = COLOR_END

        status_text = font_large.render(status_str, True, status_color)
        screen.blit(status_text, (15, 45))

        # Stats right side
        visited_count = len(state["visited"]) if state and "visited" in state else 0
        path_len = len(state["path"]) if state and "path" in state else 0

        stats_line1 = f"Відвідано: {visited_count} | Шлях: {path_len}"
        stats_line2 = f"Швидкість: {speed_steps_per_frame}x | Час: {elapsed_time_ms / 1000:.2f}с"
        controls_line = "Керування: [Space] Пауза | [+/-] Швидкість | [R] Скинути | [Esc] Вихід"

        txt_stats1 = font_small.render(stats_line1, True, COLOR_TEXT)
        txt_stats2 = font_small.render(stats_line2, True, COLOR_TEXT)
        txt_controls = font_small.render(controls_line, True, (148, 163, 184)) # Soft slate grey

        screen.blit(txt_stats1, (screen_width - txt_stats1.get_width() - 15, 10))
        screen.blit(txt_stats2, (screen_width - txt_stats2.get_width() - 15, 30))
        screen.blit(txt_controls, (screen_width - txt_controls.get_width() - 15, 52))

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()

def run_pygame_comparison_visualizer(maze: Maze, solver1_class, algo1_name: str, solver2_class, algo2_name: str):
    """
    Runs an interactive side-by-side Pygame comparison for two pathfinding algorithms on the exact same maze.
    """
    pygame.init()
    pygame.display.set_caption(f"Maze Pathfinding Comparison: {algo1_name} vs {algo2_name}")

    info_panel_height = 90
    gap = 20

    # Optimal cell size to fit two mazes side-by-side on screen
    cell_size = min((1600 - gap) // (2 * maze.width), 800 // maze.height)
    if cell_size < 1:
        cell_size = 1

    grid_width = maze.width * cell_size
    grid_height = maze.height * cell_size

    screen_width = 2 * grid_width + gap
    screen_height = grid_height + info_panel_height

    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()

    try:
        font_large = pygame.font.SysFont("Inter", 18, bold=True)
        font_small = pygame.font.SysFont("Inter", 13)
    except Exception:
        font_large = pygame.font.Font(None, 22)
        font_small = pygame.font.Font(None, 15)

    # Initialize pathfinders
    solver1 = solver1_class(maze)
    generator1 = solver1.solve_generator()
    state1 = {
        "current": maze.start_point,
        "visited": {maze.start_point},
        "path": [maze.start_point]
    }

    solver2 = solver2_class(maze)
    generator2 = solver2.solve_generator()
    state2 = {
        "current": maze.start_point,
        "visited": {maze.start_point},
        "path": [maze.start_point]
    }

    running = True
    paused = False
    finished1 = False
    finished2 = False
    speed_steps_per_frame = 1
    fps = 30

    start_time = pygame.time.get_ticks()
    elapsed1_ms = 0
    elapsed2_ms = 0
    steps1 = 0
    steps2 = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_UP or event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
                    speed_steps_per_frame = min(50, speed_steps_per_frame + 1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_KP_MINUS or event.key == pygame.K_MINUS:
                    speed_steps_per_frame = max(1, speed_steps_per_frame - 1)
                elif event.key == pygame.K_r:
                    # Restart both
                    solver1 = solver1_class(maze)
                    generator1 = solver1.solve_generator()
                    state1 = {
                        "current": maze.start_point,
                        "visited": {maze.start_point},
                        "path": [maze.start_point]
                    }
                    finished1 = False
                    steps1 = 0
                    elapsed1_ms = 0

                    solver2 = solver2_class(maze)
                    generator2 = solver2.solve_generator()
                    state2 = {
                        "current": maze.start_point,
                        "visited": {maze.start_point},
                        "path": [maze.start_point]
                    }
                    finished2 = False
                    steps2 = 0
                    elapsed2_ms = 0

                    paused = False
                    start_time = pygame.time.get_ticks()

        # Step generators
        if not paused:
            # Step solver 1
            if not finished1:
                for _ in range(speed_steps_per_frame):
                    try:
                        next_state = next(generator1)
                        if next_state:
                            state1 = next_state
                            steps1 += 1
                    except StopIteration:
                        finished1 = True
                        break
                if not finished1:
                    elapsed1_ms = pygame.time.get_ticks() - start_time

            # Step solver 2
            if not finished2:
                for _ in range(speed_steps_per_frame):
                    try:
                        next_state = next(generator2)
                        if next_state:
                            state2 = next_state
                            steps2 += 1
                    except StopIteration:
                        finished2 = True
                        break
                if not finished2:
                    elapsed2_ms = pygame.time.get_ticks() - start_time

        # Render everything
        screen.fill(COLOR_BG)

        # Draw Left Grid
        draw_maze_pygame(screen, maze, state1, cell_size, offset_y=info_panel_height, offset_x=0)

        # Draw Right Grid
        draw_maze_pygame(screen, maze, state2, cell_size, offset_y=info_panel_height, offset_x=grid_width + gap)

        # Draw visual vertical divider
        pygame.draw.rect(screen, COLOR_PANEL, pygame.Rect(grid_width, info_panel_height, gap, grid_height))
        pygame.draw.line(screen, COLOR_BORDER, (grid_width, info_panel_height), (grid_width, screen_height), 1)
        pygame.draw.line(screen, COLOR_BORDER, (grid_width + gap, info_panel_height), (grid_width + gap, screen_height), 1)

        # Draw info panel
        panel_rect = pygame.Rect(0, 0, screen_width, info_panel_height)
        pygame.draw.rect(screen, COLOR_PANEL, panel_rect)
        pygame.draw.line(screen, COLOR_BORDER, (0, info_panel_height - 1), (screen_width, info_panel_height - 1), 2)

        # Split panel into two column headers
        col_width = screen_width // 2

        # Column 1: Algorithm 1 Info
        title1 = font_large.render(f"1. {algo1_name}", True, COLOR_TEXT)
        screen.blit(title1, (15, 8))

        status1_str = "Пошук..."
        status1_color = (252, 211, 77)
        if paused:
            status1_str = "Пауза"
            status1_color = (156, 163, 175)
        elif finished1:
            if state1 and "path" in state1 and len(state1["path"]) > 1:
                status1_str = f"Знайдено за {elapsed1_ms/1000:.3f}с! ✓"
                status1_color = COLOR_ACTIVE_PATH
            else:
                status1_str = "Шлях не існує! ✗"
                status1_color = COLOR_END

        lbl_status1 = font_large.render(status1_str, True, status1_color)
        screen.blit(lbl_status1, (15, 33))

        visited1 = len(state1["visited"]) if state1 and "visited" in state1 else 0
        path_len1 = len(state1["path"]) if state1 and "path" in state1 else 0
        stats1_str = f"Кроків: {steps1} | Відвідано: {visited1} | Довжина: {path_len1}"
        lbl_stats1 = font_small.render(stats1_str, True, COLOR_TEXT)
        screen.blit(lbl_stats1, (15, 62))

        # Column 2: Algorithm 2 Info
        title2 = font_large.render(f"2. {algo2_name}", True, COLOR_TEXT)
        screen.blit(title2, (col_width + 15, 8))

        status2_str = "Пошук..."
        status2_color = (252, 211, 77)
        if paused:
            status2_str = "Пауза"
            status2_color = (156, 163, 175)
        elif finished2:
            if state2 and "path" in state2 and len(state2["path"]) > 1:
                status2_str = f"Знайдено за {elapsed2_ms/1000:.3f}с! ✓"
                status2_color = COLOR_ACTIVE_PATH
            else:
                status2_str = "Шлях не існує! ✗"
                status2_color = COLOR_END

        lbl_status2 = font_large.render(status2_str, True, status2_color)
        screen.blit(lbl_status2, (col_width + 15, 33))

        visited2 = len(state2["visited"]) if state2 and "visited" in state2 else 0
        path_len2 = len(state2["path"]) if state2 and "path" in state2 else 0
        stats2_str = f"Кроків: {steps2} | Відвідано: {visited2} | Довжина: {path_len2}"
        lbl_stats2 = font_small.render(stats2_str, True, COLOR_TEXT)
        screen.blit(lbl_stats2, (col_width + 15, 62))

        # Center/Controls line at the very bottom of the panel
        controls_str = f"Швидкість: {speed_steps_per_frame}x | [Space] Пауза | [+/-] Швидкість | [R] Скинути | [Esc] Вихід"
        lbl_controls = font_small.render(controls_str, True, (148, 163, 184))
        screen.blit(lbl_controls, (screen_width // 2 - lbl_controls.get_width() // 2, 70))

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()
