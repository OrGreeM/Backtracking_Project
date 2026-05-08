"""
Unified CLI Hub for Backtracking & CSP Workspace.
Provides both an interactive menu-driven interface and a command-line argument router.

Приклади використання (Usage Examples):

  1. Інтерактивний режим (Interactive Menu):
     python cli.py

  2. Кросворд (Crossword CSP):
     python cli.py crossword --grid-size 5 --block-ratio 0.25 --seed 42
     python cli.py crossword --no-vis --algs mrv mrv_fc

  3. Лабіринт (Maze Pathfinding):
     python cli.py maze solve --size 41 --algorithm astar --show-maze
     python cli.py maze benchmark --size 101
     python cli.py maze solve --size 25 --algorithm dfs smart --vis


  4. Судоку (Sudoku Solver):
     python cli.py sudoku solve --builtin escargot --algo mrv_fc
     python cli.py sudoku generate --difficulty expert --show-solution
     python cli.py sudoku benchmark --difficulties easy medium hard

  5. N-Queens:
     python cli.py nqueens visualize --size 6
     python cli.py nqueens compare --size 8 --no-vis

  6. Розфарбування графів (Graph Coloring):
     python cli.py coloring --n 15 --p 0.3 --k 4
     python cli.py coloring --file some_matrix.txt --k 3
"""

import os
import sys
import subprocess
import argparse


if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


SCRIPTS = {
    "crossword": os.path.join(BASE_DIR, "Crossword", "crossword.py"),
    "maze": os.path.join(BASE_DIR, "Maze", "main.py"),
    "sudoku": os.path.join(BASE_DIR, "sudoku", "sudoku.py"),
    "nqueens_viz": os.path.join(BASE_DIR, "N-Queens", "n_queens.py"),
    "nqueens_cmp": os.path.join(BASE_DIR, "N-Queens", "n_compare.py"),
    "graph_coloring": os.path.join(BASE_DIR, "graph_coloring", "main.py"),
}


C_BLUE = "\033[1;34m"
C_CYAN = "\033[1;36m"
C_GREEN = "\033[1;32m"
C_YELLOW = "\033[1;33m"
C_RED = "\033[1;31m"
C_MAGENTA = "\033[1;35m"
C_RESET = "\033[0m"
C_BOLD = "\033[1m"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    banner = f"""{C_CYAN}
 ╔══════════════════════════════════════════════════════════════════════════╗
 ║                                                                          ║
 ║██████╗  █████╗  ██████╗██╗  ██╗████████╗██████╗  █████╗  ██████╗██╗  ██╗ ║
 ║██╔══██╗██╔══██╗██╔════╝██║ ██╔╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝ ║
 ║██████╔╝███████║██║     █████╔╝    ██║   ██████╔╝███████║██║     █████╔╝  ║
 ║██╔══██╗██╔══██║██║     ██╔═██╗    ██║   ██╔══██╗██╔══██║██║     ██╔═██╗  ║
 ║██████╔╝██║  ██║╚██████╗██║  ██╗   ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗ ║
 ║╚══════╝ ╚═╝  ╚═╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝ ╚═╝ ╚══════╝╚═╝╚═╝ ║
 ║                                                                          ║
 ║                       BACKTRACKING & CSP SOLVER HUB                      ║
 ╚══════════════════════════════════════════════════════════════════════════╝{C_RESET}"""
    print(banner)


def run_subcommand(script_key, args_list=None):
    """Execute target python script with forwarded arguments."""
    if args_list is None:
        args_list = []

    script_path = SCRIPTS.get(script_key)
    if not script_path or not os.path.exists(script_path):
        print(f"\n{C_RED}[ПОМИЛКА]{C_RESET} Скрипт '{script_key}' не знайдено за шляхом: {script_path}")
        input(f"\nНатисніть Enter для повернення...")
        return

    cmd = [sys.executable, script_path] + args_list
    try:

        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n{C_RED}[ПОМИЛКА]{C_RESET} Процес завершився з кодом помилки: {e.returncode}")
        input(f"\nНатисніть Enter для повернення...")
    except KeyboardInterrupt:
        print(f"\n\n{C_YELLOW}[ІНФО]{C_RESET} Роботу програми перервано користувачем.")
        input(f"\nНатисніть Enter для повернення...")


def menu_crossword():
    while True:
        clear_screen()
        print_banner()
        print(f"\n{C_GREEN}🧩 НАЛАШТУВАННЯ КРОСВОРДУ{C_RESET}")
        print("─" * 40)
        print("1. Запустити за замовчуванням (4х4)")
        print("2. Згенерувати випадкову сітку")
        print("3. Налаштувати параметри запуску (розширені)")
        print("4. Назад до головного меню")

        choice = input(f"\n{C_BOLD}Оберіть дію (1-4): {C_RESET}").strip()
        if choice == "1":
            run_subcommand("crossword")
            break
        elif choice == "2":
            size = input(f"Введіть розмір сітки N (мінімум 4, за замовчуванням 5): ").strip() or "5"
            ratio = input(f"Введіть відсоток блоків (0.0 - 0.5, за замовчуванням 0.25): ").strip() or "0.25"
            seed = input(f"Введіть seed для випадковості (необов'язково): ").strip()

            args = ["--grid-size", size, "--block-ratio", ratio]
            if seed:
                args += ["--seed", seed]
            run_subcommand("crossword", args)
            break
        elif choice == "3":
            print(f"\n{C_CYAN}Доступні алгоритми: basic, fc, mrv, mrv_fc{C_RESET}")
            algs = input("Введіть алгоритми через пробіл (за замовчуванням усі): ").strip()
            no_vis = input("Вимкнути графічну візуалізацію? (y/n, за замовчуванням n): ").strip().lower() == "y"

            args = []
            if algs:
                args += ["--algs"] + algs.split()
            if no_vis:
                args += ["--no-vis"]
            run_subcommand("crossword", args)
            break
        elif choice == "4":
            break


def menu_maze():
    while True:
        clear_screen()
        print_banner()
        print(f"\n{C_GREEN}🌀 НАЛАШТУВАННЯ ЛАБІРИНТУ{C_RESET}")
        print("─" * 40)
        print("1. Знайти вихід (один алгоритм)")
        print("2. Порівняти всі алгоритми (Benchmark)")
        print("3. Назад")

        choice = input(f"\n{C_BOLD}Оберіть дію (1-3): {C_RESET}").strip()
        if choice in ("1", "2"):
            size = input("Розмір лабіринту (непарне число >= 5, за замовчуванням 41): ").strip() or "41"
            show_text = input("Показати лабіринт символами в консолі? (y/n, за замовчуванням n): ").strip().lower() == "y"

            if choice == "1":
                print(f"\n{C_CYAN}Алгоритми: dfs, smart, bfs, astar{C_RESET}")
                algo_input = input("Оберіть алгоритми через пробіл (наприклад: 'dfs astar', за замовчуванням astar): ").strip().lower() or "astar"
                algos = algo_input.split()
                show_vis = input("Запустити графічну візуалізацію через Pygame? (y/n, за замовчуванням y): ").strip().lower() != "n"
                args = ["solve", "--size", size, "--algorithm"] + algos
                if show_text:
                    args += ["--show-maze"]
                if show_vis:
                    args += ["--vis"]
                run_subcommand("maze", args)
                input(f"\nНатисніть Enter для продовження...")
            else:
                args = ["benchmark", "--size", size]
                if show_text:
                    args += ["--show-maze"]
                run_subcommand("maze", args)
                input(f"\nНатисніть Enter для продовження...")
            break
        elif choice == "3":
            break


def menu_sudoku():
    while True:
        clear_screen()
        print_banner()
        print(f"\n{C_GREEN}🔢 НАЛАШТУВАННЯ СУДОКУ{C_RESET}")
        print("─" * 40)
        print("1. Розв'язати вбудовану задачу (classic або escargot)")
        print("2. Згенерувати нову головоломку та розв'язати")
        print("3. Порівняти ефективність алгоритмів (Benchmark)")
        print("4. Назад")

        choice = input(f"\n{C_BOLD}Оберіть дію (1-4): {C_RESET}").strip()
        if choice == "1":
            builtin = input("Оберіть задачу (classic / escargot, за замовчуванням classic): ").strip().lower() or "classic"
            print(f"\n{C_CYAN}Алгоритми: pure (базовий), mrv, mrv_fc, greedy{C_RESET}")
            algo = input("Введіть алгоритм (за замовчуванням mrv_fc): ").strip().lower() or "mrv_fc"
            run_subcommand("sudoku", ["solve", "--builtin", builtin, "--algo", algo])
            input(f"\nНатисніть Enter для продовження...")
            break
        elif choice == "2":
            diff = input("Складність (easy, medium, hard, expert, за замовчуванням medium): ").strip().lower() or "medium"
            show_sol = input("Показати розв'язок? (y/n, за замовчуванням y): ").strip().lower() != "n"
            args = ["generate", "--difficulty", diff]
            if show_sol:
                args += ["--show-solution"]
            run_subcommand("sudoku", args)
            input(f"\nНатисніть Enter для продовження...")
            break
        elif choice == "3":
            diffs = input("Складності для порівняння через пробіл (наприклад: easy medium, за замовчуванням усі): ").strip()
            args = ["benchmark"]
            if diffs:
                args += ["--difficulties"] + diffs.split()
            run_subcommand("sudoku", args)
            input(f"\nНатисніть Enter для продовження...")
            break
        elif choice == "4":
            break


def menu_nqueens():
    while True:
        clear_screen()
        print_banner()
        print(f"\n{C_GREEN}♛ ЗАДАЧА N ФЕРЗІВ{C_RESET}")
        print("─" * 40)
        print("1. Покрокова візуалізація дерева та шахівниці (один алгоритм)")
        print("2. Порівняння алгоритмів та графік продуктивності")
        print("3. Назад")

        choice = input(f"\n{C_BOLD}Оберіть дію (1-3): {C_RESET}").strip()
        if choice == "1":
            n = input("Введіть розмір дошки N (за замовчуванням 5): ").strip() or "5"
            run_subcommand("nqueens_viz", [n])
            break
        elif choice == "2":
            n = input("Введіть розмір дошки N (за замовчуванням 6): ").strip() or "6"
            no_vis = input("Вимкнути графічну візуалізацію кроків? (y/n, за замовчуванням n): ").strip().lower() == "y"
            args = ["--size", n]
            if no_vis:
                args += ["--no-vis"]
            run_subcommand("nqueens_cmp", args)
            break
        elif choice == "3":
            break


def menu_graph_coloring():
    while True:
        clear_screen()
        print_banner()
        print(f"\n{C_GREEN}🎨 РОЗФАРБОВУВАННЯ ГРАФІВ{C_RESET}")
        print("─" * 40)
        print("1. Запустити на випадковому графі")
        print("2. Завантажити матрицю суміжності з файлу")
        print("3. Назад")

        choice = input(f"\n{C_BOLD}Оберіть дію (1-3): {C_RESET}").strip()
        if choice == "1":
            n = input("Кількість вершин N (за замовчуванням 15): ").strip() or "15"
            p = input("Ймовірність ребра p (0.0 - 1.0, за замовчуванням 0.3): ").strip() or "0.3"
            k = input("Кількість кольорів K (за замовчуванням 4): ").strip() or "4"
            run_subcommand("graph_coloring", ["--n", n, "--p", p, "--k", k])
            break
        elif choice == "2":
            path = input("Введіть повний шлях до файлу матриці: ").strip()
            k = input("Кількість кольорів K (за замовчуванням 4): ").strip() or "4"
            if not os.path.exists(path):
                print(f"{C_RED}[ПОМИЛКА]{C_RESET} Файл не існує.")
                input("\nНатисніть Enter...")
                continue
            run_subcommand("graph_coloring", ["--file", path, "--k", k])
            break
        elif choice == "3":
            break


def interactive_menu():
    while True:
        clear_screen()
        print_banner()
        print(f"\n  {C_CYAN}ГОЛОВНЕ МЕНЮ ПРОЄКТУ{C_RESET}")
        print(" ╠" + "═" * 36 + "╣")
        print(f" ║ {C_YELLOW}1.{C_RESET} 🧩 Кросворд (Crossword CSP)     ║")
        print(f" ║ {C_YELLOW}2.{C_RESET} 🌀 Лабіринт (Maze Pathfinding)  ║")
        print(f" ║ {C_YELLOW}3.{C_RESET} 🔢 Судоку (Sudoku Solver)       ║")
        print(f" ║ {C_YELLOW}4.{C_RESET} ♛ Задача N ферзів (N-Queens)    ║")
        print(f" ║ {C_YELLOW}5.{C_RESET} 🎨 Розфарбування графів (Graph) ║")
        print(f" ║ {C_YELLOW}6.{C_RESET} ❌ Вихід (Exit)                 ║")
        print(" ╚" + "═" * 36 + "╝")

        choice = input(f"\n{C_BOLD}Оберіть розділ (1-6): {C_RESET}").strip()
        if choice == "1":
            menu_crossword()
        elif choice == "2":
            menu_maze()
        elif choice == "3":
            menu_sudoku()
        elif choice == "4":
            menu_nqueens()
        elif choice == "5":
            menu_graph_coloring()
        elif choice == "6":
            clear_screen()
            print(f"\n{C_GREEN}Дякуємо за використання Backtracking & CSP Solver Hub! До зустрічі!{C_RESET}\n")
            sys.exit(0)


def build_arg_parser():
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Unified CLI interface for the Backtracking and Constraint Satisfaction Project.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Якщо запустити без аргументів, відкриється зручне інтерактивне меню.

Приклади використання (Usage Examples):

  1. Інтерактивний режим:
     python cli.py

  2. Кросворд (Crossword CSP):
     python cli.py crossword --grid-size 5 --block-ratio 0.25 --seed 42
     python cli.py crossword --no-vis --algs mrv mrv_fc

  3. Лабіринт (Maze Pathfinding):
     python cli.py maze solve --size 41 --algorithm astar --show-maze
     python cli.py maze benchmark --size 101

  4. Судоку (Sudoku):
     python cli.py sudoku solve --builtin escargot --algo mrv_fc
     python cli.py sudoku generate --difficulty expert --show-solution
     python cli.py sudoku benchmark --difficulties easy medium hard

  5. Задача N-Ферзів (N-Queens):
     python cli.py nqueens visualize --size 6
     python cli.py nqueens compare --size 8 --no-vis

  6. Розфарбування графів (Graph Coloring):
     python cli.py coloring --n 15 --p 0.3 --k 4
     python cli.py coloring --file some_matrix.txt --k 3
"""
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Доступні підмодулі")


    p_crossword = subparsers.add_parser("crossword", help="Розв'язання кросвордів")
    p_crossword.add_argument("--grid-size", "-g", type=int, help="Розмір випадкової сітки")
    p_crossword.add_argument("--block-ratio", "-b", type=float, help="Частка заблокованих клітинок")
    p_crossword.add_argument("--seed", "-s", type=int, help="Seed для випадковості")
    p_crossword.add_argument("--words-file", "-w", type=str, help="Текстовий файл зі словами")
    p_crossword.add_argument("--algs", nargs="+", help="Алгоритми (basic, fc, mrv, mrv_fc)")
    p_crossword.add_argument("--no-vis", action="store_true", help="Вимкнути візуалізацію")


    p_maze = subparsers.add_parser("maze", help="Пошук виходу з лабіринту")
    p_maze.add_argument("mode", choices=["solve", "benchmark"], help="Режим роботи")
    p_maze.add_argument("--size", "-s", type=int, default=41, help="Розмір непарної сітки")
    p_maze.add_argument("--algorithm", "-a", choices=["dfs", "smart", "bfs", "astar"], nargs="+", default=["astar"], help="Алгоритм(и)")
    p_maze.add_argument("--show-maze", action="store_true", help="Символьний вивід в консоль")
    p_maze.add_argument("--vis", action="store_true", help="Запустити графічну візуалізацію через Pygame")


    p_sudoku = subparsers.add_parser("sudoku", help="Розв'язання Судоку")
    p_sudoku.add_argument("mode", choices=["solve", "benchmark", "generate"], help="Режим роботи")
    p_sudoku.add_argument("--puzzle", type=str, help="Рядок судоку з 81 символу")
    p_sudoku.add_argument("--builtin", choices=["classic", "escargot"], help="Вбудований судоку")
    p_sudoku.add_argument("--generate", choices=["easy", "medium", "hard", "expert"], help="Генерувати рівень складності")
    p_sudoku.add_argument("--algo", choices=["pure", "mrv", "mrv_fc", "greedy"], help="Алгоритм для розв'язання")
    p_sudoku.add_argument("--difficulty", choices=["easy", "medium", "hard", "expert"], help="Рівень для генерування")
    p_sudoku.add_argument("--show-solution", action="store_true", help="Показати рішення")
    p_sudoku.add_argument("--difficulties", nargs="+", help="Списк складностей для порівняння")


    p_nqueens = subparsers.add_parser("nqueens", help="Задача N-ферзів")
    p_nqueens.add_argument("mode", choices=["visualize", "compare"], help="Режим роботи")
    p_nqueens.add_argument("--size", "-n", type=int, default=5, help="Розмір дошки")
    p_nqueens.add_argument("--no-vis", action="store_true", help="Вимкнути анімацію")
    p_nqueens.add_argument("--algs", nargs="+", help="Алгоритми для порівняння")


    p_coloring = subparsers.add_parser("coloring", help="Розфарбування графів")
    p_coloring.add_argument("--file", type=str, help="Матриця суміжності з файлу")
    p_coloring.add_argument("--n", type=int, help="Кількість вершин випадкового графа")
    p_coloring.add_argument("--p", type=float, help="Ймовірність ребра випадкового графа")
    p_coloring.add_argument("--k", type=int, help="Кількість кольорів K")

    return parser


def main():
    if len(sys.argv) == 1:

        try:
            interactive_menu()
        except KeyboardInterrupt:
            print(f"\n\n{C_GREEN}Дякуємо за використання! Вихід...{C_RESET}\n")
            sys.exit(0)


    parser = build_arg_parser()
    args = parser.parse_args()


    forward_args = []

    if args.subcommand == "crossword":
        if args.grid_size is not None:
            forward_args += ["--grid-size", str(args.grid_size)]
        if args.block_ratio is not None:
            forward_args += ["--block-ratio", str(args.block_ratio)]
        if args.seed is not None:
            forward_args += ["--seed", str(args.seed)]
        if args.words_file:
            forward_args += ["--words-file", args.words_file]
        if args.algs:
            forward_args += ["--algs"] + args.algs
        if args.no_vis:
            forward_args += ["--no-vis"]
        run_subcommand("crossword", forward_args)

    elif args.subcommand == "maze":
        forward_args += [args.mode, "--size", str(args.size)]
        if args.mode == "solve":
            forward_args += ["--algorithm"] + args.algorithm
            if args.vis:
                forward_args += ["--vis"]
        if args.show_maze:
            forward_args += ["--show-maze"]
        run_subcommand("maze", forward_args)

    elif args.subcommand == "sudoku":
        forward_args += [args.mode]
        if args.puzzle:
            forward_args += ["--puzzle", args.puzzle]
        if args.builtin:
            forward_args += ["--builtin", args.builtin]
        if args.generate:
            forward_args += ["--generate", args.generate]
        if args.algo:
            forward_args += ["--algo", args.algo]
        if args.difficulty:
            forward_args += ["--difficulty", args.difficulty]
        if args.show_solution:
            forward_args += ["--show-solution"]
        if args.difficulties:
            forward_args += ["--difficulties"] + args.difficulties
        run_subcommand("sudoku", forward_args)

    elif args.subcommand == "nqueens":
        if args.mode == "visualize":
            run_subcommand("nqueens_viz", [str(args.size)])
        else:
            forward_args += ["--size", str(args.size)]
            if args.no_vis:
                forward_args += ["--no-vis"]
            if args.algs:
                forward_args += ["--algs"] + args.algs
            run_subcommand("nqueens_cmp", forward_args)

    elif args.subcommand == "coloring":
        if args.file:
            forward_args += ["--file", args.file]
        if args.n is not None:
            forward_args += ["--n", str(args.n)]
        if args.p is not None:
            forward_args += ["--p", str(args.p)]
        if args.k is not None:
            forward_args += ["--k", str(args.k)]
        run_subcommand("graph_coloring", forward_args)


if __name__ == "__main__":
    main()
