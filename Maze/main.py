"""
Maze solver CLI — run a single algorithm or benchmark all of them.

Usage examples:
    python main.py solve --algorithm astar --size 41
    python main.py solve --algorithm dfs --size 101 --show-maze
    python main.py benchmark --size 201
    python main.py benchmark --size 401 --show-maze
"""

import argparse
import copy
import sys
import time

from generator import MazeGenerator
from models import Maze
from solvers import MazeSolver, SmartMazeSolver, BFSMazeSolver, AStarMazeSolver


ALGORITHMS = {
    "dfs":   ("DFS (класичний)",      MazeSolver),
    "smart": ("Smart DFS (евристика)", SmartMazeSolver),
    "bfs":   ("BFS (пошук у ширину)",  BFSMazeSolver),
    "astar": ("A* (A-Star)",           AStarMazeSolver),
}


def _validate_size(value: str) -> int:
    n = int(value)
    if n < 5:
        raise argparse.ArgumentTypeError("Maze size must be at least 5")
    if n % 2 == 0:
        n += 1
    return n


def _generate_maze(size: int) -> Maze:
    print(f"Генерація лабіринту {size}×{size}...")
    generator = MazeGenerator(size, size)
    maze = generator.generate()
    walls_to_break = size * size // 100
    if walls_to_break > 0:
        print(f"Ламаємо {walls_to_break} стін для створення циклів...")
        maze.break_random_walls(walls_to_break)
    return maze


def _run_solver(solver_class, maze: Maze) -> tuple:
    """Run a solver and return (solver, elapsed_ms)."""
    solver = solver_class(maze)
    start = time.perf_counter()
    solver.solve()
    elapsed_ms = (time.perf_counter() - start) * 1000
    return solver, elapsed_ms


def cmd_solve(args):
    """Handle the 'solve' subcommand."""
    size = args.size
    sys.setrecursionlimit(size * size)

    maze = _generate_maze(size)
    algo_name, solver_class = ALGORITHMS[args.algorithm]

    print(f"\n--- {algo_name} ---")
    solver, elapsed_ms = _run_solver(solver_class, maze)

    print(f"Відвідано клітинок: {len(solver.visited)}")
    print(f"Час виконання:      {elapsed_ms:.4f} мс")
    print(f"Довжина шляху:      {len(solver.path)}")

    if args.show_maze:
        print()
        print(maze.__str__(path=solver.path))


def cmd_benchmark(args):
    """Handle the 'benchmark' subcommand."""
    size = args.size
    sys.setrecursionlimit(size * size)

    maze = _generate_maze(size)

    results = []

    for _, value in ALGORITHMS.items():
        algo_name, solver_class = value
        maze_copy = copy.deepcopy(maze)

        print(f"\nЗапуск: {algo_name}...")
        solver, elapsed_ms = _run_solver(solver_class, maze_copy)
        results.append((algo_name, elapsed_ms, len(solver.visited), len(solver.path), solver, maze_copy))

        print(f"  Відвідано: {len(solver.visited)},  Час: {elapsed_ms:.4f} мс,  Шлях: {len(solver.path)}")

    # Summary table
    print("\n" + "=" * 70)
    print("ПІДСУМКОВА ТАБЛИЦЯ ПОРІВНЯННЯ")
    print("=" * 70)
    print(f"{'Алгоритм':<25} {'Час (мс)':<15} {'Відвідано':<15} {'Довжина шляху':<15}")
    print("-" * 70)
    for algo_name, elapsed_ms, visited, path_len, _, _ in results:
        print(f"{algo_name:<25} {elapsed_ms:<15.4f} {visited:<15} {path_len:<15}")
    print("=" * 70)

    if args.show_maze:
        for algo_name, _, _, _, solver, maze_copy in results:
            print(f"\n--- Лабіринт: {algo_name} ---")
            print(maze_copy.__str__(path=solver.path))


def main():
    parser = argparse.ArgumentParser(
        description="Maze Solver CLI — розв'язання та порівняння алгоритмів пошуку шляху в лабіринті.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Доступні команди")

    solve_parser = subparsers.add_parser("solve", help="Запустити один алгоритм")
    solve_parser.add_argument(
        "-a", "--algorithm",
        choices=list(ALGORITHMS.keys()),
        default="astar",
        help="Алгоритм для запуску (default: astar)",
    )
    solve_parser.add_argument(
        "-s", "--size",
        type=_validate_size,
        default=41,
        help="Розмір лабіринту (непарне число, default: 41)",
    )
    solve_parser.add_argument(
        "--show-maze",
        action="store_true",
        help="Показати лабіринт з шляхом у консолі",
    )

    bench_parser = subparsers.add_parser("benchmark", help="Порівняти всі алгоритми")
    bench_parser.add_argument(
        "-s", "--size",
        type=_validate_size,
        default=41,
        help="Розмір лабіринту (непарне число, default: 41)",
    )
    bench_parser.add_argument(
        "--show-maze",
        action="store_true",
        help="Показати лабіринт з шляхом у консолі для кожного алгоритму",
    )

    args = parser.parse_args()

    if args.command == "solve":
        cmd_solve(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)


if __name__ == "__main__":
    main()
