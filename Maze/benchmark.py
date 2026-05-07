import copy
import sys
import time

from generator import MazeGenerator
from solvers import MazeSolver, SmartMazeSolver, BFSMazeSolver, AStarMazeSolver

if __name__ == "__main__":
    h = w = 401
    sys.setrecursionlimit(h * w)

    print("Генерація лабіринту...")
    generator = MazeGenerator(h, w)
    original_maze = generator.generate()

    walls_to_break = h * w // 100
    print(f"Ламаємо {walls_to_break} стін для створення циклів...")
    original_maze.break_random_walls(walls_to_break)

    maze_for_classic = copy.deepcopy(original_maze)
    maze_for_smart = copy.deepcopy(original_maze)
    maze_for_bfs = copy.deepcopy(original_maze)
    maze_for_astar = copy.deepcopy(original_maze)

    # 1. Classic DFS
    classic_solver = MazeSolver(maze_for_classic)
    start_time_classic = time.perf_counter()
    classic_solver.solve()
    end_time_classic = time.perf_counter()
    time_classic_ms = (end_time_classic - start_time_classic) * 1000

    print("\n--- Запуск класичного Backtracking ---")
    print(f"Відвідано клітинок: {len(classic_solver.visited)}")
    print(f"Час виконання: {time_classic_ms:.4f} мс")
    print(f"Довжина знайденого шляху: {len(classic_solver.path)}")

    # 2. Smart DFS
    sm_solver = SmartMazeSolver(maze_for_smart)
    start_sm = time.perf_counter()
    sm_solver.solve()
    end_sm = time.perf_counter()
    time_sm_ms = (end_sm - start_sm) * 1000

    print("\n--- Запуск оптимізованого алгоритму (MRV) ---")
    print(f"Відвідано клітинок (під час пошуку): {len(sm_solver.visited)}")
    print(f"Загальний час виконання (з обробкою): {time_sm_ms:.4f} мс")
    print(f"Довжина знайденого шляху: {len(sm_solver.path)}")

    # 3. BFS
    bfs_solver = BFSMazeSolver(maze_for_bfs)
    start_bfs = time.perf_counter()
    bfs_solver.solve()
    end_bfs = time.perf_counter()
    time_bfs_ms = (end_bfs - start_bfs) * 1000

    print("\n--- Запуск BFS (Пошук у ширину) ---")
    print(f"Відвідано клітинок: {len(bfs_solver.visited)}")
    print(f"Час виконання: {time_bfs_ms:.4f} мс")
    print(f"Довжина знайденого шляху: {len(bfs_solver.path)}")

    # 4. A*
    astar_solver = AStarMazeSolver(maze_for_astar)
    start_astar = time.perf_counter()
    astar_solver.solve()
    end_astar = time.perf_counter()
    time_astar_ms = (end_astar - start_astar) * 1000

    print("\n--- Запуск A* (A-Star) ---")
    print(f"Відвідано клітинок: {len(astar_solver.visited)}")
    print(f"Час виконання: {time_astar_ms:.4f} мс")
    print(f"Довжина знайденого шляху: {len(astar_solver.path)}")

    # Summary table
    print("\n" + "="*70)
    print("ПІДСУМКОВА ТАБЛИЦЯ ПОРІВНЯННЯ")
    print("="*70)
    print(f"{'Алгоритм':<25} {'Час (мс)':<15} {'Відвідано':<15} {'Довжина шляху':<15}")
    print("-"*70)
    print(f"{'DFS (класичний)':<25} {time_classic_ms:<15.4f} {len(classic_solver.visited):<15} {len(classic_solver.path):<15}")
    print(f"{'Smart DFS (евристика)':<25} {time_sm_ms:<15.4f} {len(sm_solver.visited):<15} {len(sm_solver.path):<15}")
    print(f"{'BFS (пошук у ширину)':<25} {time_bfs_ms:<15.4f} {len(bfs_solver.visited):<15} {len(bfs_solver.path):<15}")
    print(f"{'A* (A-Star)':<25} {time_astar_ms:<15.4f} {len(astar_solver.visited):<15} {len(astar_solver.path):<15}")
    print("="*70)
