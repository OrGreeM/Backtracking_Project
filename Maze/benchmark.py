import copy
import sys
import time
from models import Maze, Point
from generator import MazeGenerator
from solvers import MazeSolver, OptimizedMazeSolver, SmartMazeSolver

if __name__ == "__main__":
    sys.setrecursionlimit(100_000)

    print("Генерація лабіринту...")
    generator = MazeGenerator(101, 101)
    original_maze = generator.generate()

    # --- СТВОРЮЄМО ЦИКЛИ ---
    walls_to_break = 1000
    print(f"Ламаємо {walls_to_break} стін для створення циклів...")
    original_maze.break_random_walls(walls_to_break)

    # Тепер копіюємо "зіпсований" лабіринт для обох алгоритмів
    maze_for_classic = copy.deepcopy(original_maze)
    maze_for_optimized = copy.deepcopy(original_maze)
    maze_for_smart = copy.deepcopy(original_maze)

    # --- 1. Класичний алгоритм ---
    classic_solver = MazeSolver(maze_for_classic)

    start_time_classic = time.perf_counter()
    classic_solver.solve()
    end_time_classic = time.perf_counter()

    time_classic_ms = (end_time_classic - start_time_classic) * 1000

    print("\n--- Запуск класичного Backtracking ---")
    print(f"Відвідано клітинок: {len(classic_solver.visited)}")
    print(f"Час виконання: {time_classic_ms:.4f} мс")

    # --- 2. Оптимізований алгоритм (Dead-end filling) ---
    opt_solver = OptimizedMazeSolver(maze_for_optimized)

    start_time_opt = time.perf_counter()
    opt_solver.solve()
    end_time_opt = time.perf_counter()

    time_opt_ms = (end_time_opt - start_time_opt) * 1000

    print("\n--- Запуск оптимізованого алгоритму (Dead-end filling) ---")
    print(f"Відвідано клітинок (під час пошуку): {len(opt_solver.visited)}")
    print(f"Загальний час виконання (з обробкою): {time_opt_ms:.4f} мс")

    # 3

    sm_solver = SmartMazeSolver(maze_for_smart)

    start_sm = time.perf_counter()
    sm_solver.solve()
    end_sm = time.perf_counter()

    time_sm_ms = (end_sm - start_sm) * 1000
    print("\n--- Запуск оптимізованого алгоритму (MRV) ---")
    print(f"Відвідано клітинок (під час пошуку): {len(sm_solver.visited)}")
    print(f"Загальний час виконання (з обробкою): {time_sm_ms:.4f} мс")
