'''Sudoku — Backtracking solver with optimizations'''

import random
import time
import copy
from typing import Optional


def print_board(board: list[list[int]], title: str = '') -> None:
    '''Printing the board for sudoke'''
    if title:
        print(f'\n{'─' * 37}')
        print(f'  {title}')
        print(f'{'─' * 37}')
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print('├───────┼───────┼───────┤')
        row = ''
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row += ' │'
            val = board[r][c]
            row += f' {val if val != 0 else '.'}'
        print(f'│{row} │')
    print(f'{'─' * 37}')


def is_valid(board: list[list[int]], row: int, col: int, num: int) -> bool:
    '''Checking if placing num at (row, col) violates any Sudoku logic'''
    if num in board[row]:
        return False
    if num in [board[r][col] for r in range(9)]:
        return False
    br, bc = (row // 3) * 3, (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] == num:
                return False
    return True


def find_empty(board: list[list[int]]) -> Optional[tuple[int, int]]:
    '''Finds the next empty cell'''
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return (r, c)
    return None


def getcandidates(board: list[list[int]], row: int, col: int) -> list[int]:
    '''Returns all valid numbers for a given cell.'''
    return [n for n in range(1, 10) if is_valid(board, row, col, n)]


def boardcopy(board: list[list[int]]) -> list[list[int]]:
    return [row[:] for row in board]


class PureBacktracking:
    '''Classic DFS backtracking'''

    def _init__(self):
        self.steps = 0
        self.backtracks = 0

    def solve(self, board: list[list[int]]) -> bool:
        '''Checking the state of the board: whether it is solved ot not'''
        cell = find_empty(board)
        if cell is None:
            return True

        row, col = cell
        for num in range(1, 10):
            self.steps += 1
            if is_valid(board, row, col, num):
                board[row][col] = num
                if self.solve(board):
                    return True
                board[row][col] = 0
                self.backtracks += 1
        return False


PEERS: list[list[frozenset]] = []
for r in range(9):
    row = []
    for c in range(9):
        p = set()
        for i in range(9):
            p.add((r, i))
            p.add((i, c))
        br, bc = (r // 3) * 3, (c // 3) * 3
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                p.add((i, j))
        p.discard((r, c))
        row.append(frozenset(p))
    PEERS.append(row)


class BacktrackingMRV:
    ''''Backtracking with Minimum Remaining Values'''

    def _init__(self):
        self.steps = 0
        self.backtracks = 0

    def buildcandidates(self, board: list[list[int]]) -> list[list[set]]:
        '''Compute the initial candidate sets from the starting board.'''
        cands = [[set() if board[r][c] != 0 else set(range(1, 10))
                  for c in range(9)] for r in range(9)]
        for r in range(9):
            for c in range(9):
                if board[r][c] != 0:
                    d = board[r][c]
                    for (pr, pc) in PEERS[r][c]:
                        cands[pr][pc].discard(d)
        return cands

    def find_mrvcell(self, board, cands) -> Optional[tuple[int, int]]:
        '''Returns the empty cell with the minimum number of valid candidates'''
        best, bestcount = None, 10
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    n = len(cands[r][c])
                    if n == 0:
                        return None        # Dead end
                    if n < bestcount:
                        bestcount, best = n, (r, c)
        return best

    def solve(self, board: list[list[int]]) -> bool:
        '''Checking the state of the board: whether it is solved ot not'''
        cands = self.buildcandidates(board)
        return self._solve(board, cands)

    def _solve(self, board, cands) -> bool:
        '''Checking the state of the board: whether it is solved ot not'''
        cell = self.find_mrvcell(board, cands)
        if cell is None:
            return find_empty(board) is None

        row, col = cell
        for num in list(cands[row][col]):
            self.steps += 1
            board[row][col] = num
            saved_own = cands[row][col].copy()
            cands[row][col] = set()
            removed: list[tuple[int, int]] = []
            for (pr, pc) in PEERS[row][col]:
                if num in cands[pr][pc]:
                    cands[pr][pc].discard(num)
                    removed.append((pr, pc))
            if self._solve(board, cands):
                return True
            # Undo placement and restore candidate sets
            board[row][col] = 0
            cands[row][col] = saved_own
            for (pr, pc) in removed:
                cands[pr][pc].add(num)
            self.backtracks += 1
        return False



class BacktrackingMRVFC:
    '''Backtracking with MRV + Forward Checking'''

    def _init__(self):
        self.steps = 0
        self.backtracks = 0

    def buildcandidates(self, board):
        cands = [[set() if board[r][c] != 0 else set(range(1, 10))
                  for c in range(9)] for r in range(9)]
        for r in range(9):
            for c in range(9):
                if board[r][c] != 0:
                    d = board[r][c]
                    for (pr, pc) in PEERS[r][c]:
                        cands[pr][pc].discard(d)
        return cands

    def find_mrvcell(self, board, cands):
        '''Returns the empty cell with the minimum number of valid candidates'''
        best, bestcount = None, 10
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    n = len(cands[r][c])
                    if n == 0:
                        return None
                    if n < bestcount:
                        bestcount, best = n, (r, c)
        return best

    def solve(self, board: list[list[int]]) -> bool:
        '''Checking the state of the board: whether it is solved ot not'''
        cands = self.buildcandidates(board)
        return self._solve(board, cands)

    def _solve(self, board, cands) -> bool:
        '''Checking the state of the board: whether it is solved ot not'''
        cell = self.find_mrvcell(board, cands)
        if cell is None:
            return find_empty(board) is None

        row, col = cell
        for num in list(cands[row][col]):
            self.steps += 1
            board[row][col] = num
            saved_own = cands[row][col].copy()
            cands[row][col] = set()
            removed: list[tuple[int, int]] = []
            wipeout = False
            for (pr, pc) in PEERS[row][col]:
                if num in cands[pr][pc]:
                    cands[pr][pc].discard(num)
                    removed.append((pr, pc))
                    if board[pr][pc] == 0 and len(cands[pr][pc]) == 0:
                        wipeout = True
                        break

            if not wipeout and self._solve(board, cands):
                return True

            board[row][col] = 0
            cands[row][col] = saved_own
            for (pr, pc) in removed:
                cands[pr][pc].add(num)
            self.backtracks += 1

        return False


class GreedySolver:
    '''Greedy algorithm'''

    def _init__(self):
        self.steps = 0
        self.backtracks = 0

    def find_mrvcell(self, board):
        '''Returns the empty cell with the minimum number of valid candidates'''
        best = None
        bestcount = 10
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    cands = getcandidates(board, r, c)
                    if len(cands) == 0:
                        return None, []
                    if len(cands) < bestcount:
                        bestcount = len(cands)
                        best = (r, c)
        if best is None:
            return None, []
        return best, getcandidates(board, best[0], best[1])

    def solve(self, board: list[list[int]]) -> bool:
        '''Checking the state of the board: whether it is solved ot not'''
        cell, candidates = self.find_mrvcell(board)
        if cell is None:
            return find_empty(board) is None

        row, col = cell
        if candidates:
            self.steps += 1
            board[row][col] = candidates[0]
            if self.solve(board):
                return True
            for num in candidates[1:]:
                self.steps += 1
                self.backtracks += 1
                board[row][col] = num
                if self.solve(board):
                    return True
            board[row][col] = 0
            self.backtracks += 1
        return False


DIFFICULTY = {
    'easy':   40,
    'medium': 30,
    'hard':   22,
    'expert': 17,
}


def generatepuzzle(difficulty: str = 'medium') -> tuple[list[list[int]], list[list[int]]]:
    '''
    Generates a random valid Sudoku puzzle.
    Returns:
        puzzle  — board with some cells removed (zeros = empty)
        solution — the complete solved board
    '''
    givencount = DIFFICULTY.get(difficulty, 30)

    board = [[0] * 9 for _ in range(9)]
    fill_diagonal_boxes(board)
    solver = BacktrackingMRVFC()
    solver.solve(board)
    solution = boardcopy(board)

    puzzle = boardcopy(solution)
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    removed = 0
    targetremove = 81 - givencount
    for r, c in cells:
        if removed >= targetremove:
            break
        backup = puzzle[r][c]
        puzzle[r][c] = 0
        test = boardcopy(puzzle)
        s = BacktrackingMRVFC()
        if s.solve(test):
            removed += 1
        else:
            puzzle[r][c] = backup

    return puzzle, solution


def fill_diagonal_boxes(board: list[list[int]]) -> None:
    '''Fills the three diagonal 3x3 boxes with random digits (they don't affect each other).'''
    for box in range(3):
        digits = list(range(1, 10))
        random.shuffle(digits)
        start = box * 3
        for i in range(3):
            for j in range(3):
                board[start + i][start + j] = digits[i * 3 + j]


# Benchmark with the results

def run_benchmark(puzzle: list[list[int]], difficulty: str) -> None:
    algorithms = [
        ('Pure Backtracking',         PureBacktracking),
        ('Backtracking + MRV',        BacktrackingMRV),
        ('Backtracking + MRV + FC',   BacktrackingMRVFC),
        ('Greedy / DFS',              GreedySolver),
    ]

    print(f'\n{'═' * 60}')
    print(f'  Benchmark — difficulty: {difficulty.upper()}')
    print(f'{'═' * 60}')
    print(f'  {'Algorithm':<28} {'Steps':>8} {'Backtracks':>11} {'Time (ms)':>10}')
    print(f'  {'─' * 28} {'─' * 8} {'─' * 11} {'─' * 10}')

    for name, AlgClass in algorithms:
        board = boardcopy(puzzle)
        alg = AlgClass()
        t0 = time.perfcounter()
        solved = alg.solve(board)
        elapsed = (time.perfcounter() - t0) * 1000
        status = '✓' if solved else '✗'
        print(f'  {status} {name:<27} {alg.steps:>8,} {alg.backtracks:>11,} {elapsed:>9.2f}')

    print(f'{'═' * 60}')


#  Interactive solver (manual input)

def parse_board(flat: str) -> list[list[int]]:
    '''
    Parse a board from a flat 81-char string.
    '0' or '.' represent empty cells.
    Example:
        '530070000600195000098000060800060003400803001700020006060000280000419005000080079'
    '''
    flat = flat.replace('.', '0').replace(' ', '').replace('\n', '')
    if len(flat) != 81:
        raise ValueError(f'Expected 81 characters, got {len(flat)}')
    board = []
    for i in range(9):
        board.append([int(flat[i * 9 + j]) for j in range(9)])
    return board


def solvepuzzle(puzzle: list[list[int]], algorithm: str = 'mrv_fc') -> dict:
    '''
    Solve a puzzle with the chosen algorithm.

    algorithm options: 'pure', 'mrv', 'mrv_fc', 'greedy'
    Returns a dict with: solved, board, steps, backtracks, time_ms
    '''
    alg_map = {
        'pure':   PureBacktracking,
        'mrv':    BacktrackingMRV,
        'mrv_fc': BacktrackingMRVFC,
        'greedy': GreedySolver,
    }
    AlgClass = alg_map.get(algorithm, BacktrackingMRVFC)
    board = boardcopy(puzzle)
    alg = AlgClass()
    t0 = time.perfcounter()
    solved = alg.solve(board)
    elapsed = (time.perfcounter() - t0) * 1000
    return {
        'solved':      solved,
        'board':       board,
        'steps':       alg.steps,
        'backtracks':  alg.backtracks,
        'time_ms':     round(elapsed, 3),
    }


BUILTINpUZZLES = {
    'classic': (
        '530070000'
        '600195000'
        '098000060'
        '800060003'
        '400803001'
        '700020006'
        '060000280'
        '000419005'
        '000080079'
    ),
    'escargot': (
        '100007090'
        '030020008'
        '009600500'
        '005300900'
        '010080002'
        '600004000'
        '300000010'
        '040000007'
        '007000300'
    ),
}

ALG_NAMES = {
    'pure':    'Pure Backtracking',
    'mrv':     'Backtracking + MRV',
    'mrv_fc':  'Backtracking + MRV + FC',
    'greedy':  'Greedy / DFS',
}


#  CLI subcommand handlers

def cmd_solve(args) -> None:
    '''
    Solve a single puzzle and print the result

    Sources (in priority order):
      --puzzle   raw 81-char string
      --builtin  name from BUILTINpUZZLES
      --generate difficulty level  (random puzzle)
    '''
    # Obtain the puzzle
    if args.puzzle:
        try:
            puzzle = parse_board(args.puzzle)
        except ValueError as e:
            print(f'Error: {e}')
            return
        label = 'Custom puzzle'

    elif args.generate:
        diff = args.generate
        print(f'  Generating {diff} puzzle...')
        puzzle, _ = generatepuzzle(diff)
        given = sum(cell != 0 for row in puzzle for cell in row)
        label = f'Random {diff} puzzle ({given} given)'

    else:
        name = args.builtin or 'classic'
        if name not in BUILTINpUZZLES:
            print(f'Error: unknown built-in '{name}'. Choose from: {', '.join(BUILTINpUZZLES)}')
            return
        puzzle = parse_board(BUILTINpUZZLES[name])
        label = f'Built-in puzzle: {name}'

    # Print input board
    print_board(puzzle, f'{label} — input')

    # Solve
    algo = args.algo or 'mrv_fc'
    result = solvepuzzle(puzzle, algorithm=algo)

    status = 'Solved ✓' if result['solved'] else 'No solution found ✗'
    alg_label = ALG_NAMES.get(algo, algo)

    print(f'\n  Algorithm : {alg_label}')
    print(f'  Status    : {status}')
    print(f'  Steps     : {result['steps']:,}')
    print(f'  Backtracks: {result['backtracks']:,}')
    print(f'  Time      : {result['time_ms']} ms')

    if result['solved']:
        print_board(result['board'], 'Solution')


def cmd_benchmark(args) -> None:
    '''
    Runs all four algorithms on one or more difficulty levels and
    print a comparison table
    '''
    difficulties = args.difficulties or ['easy', 'medium', 'hard', 'expert']

    for diff in difficulties:
        if args.puzzle:
            try:
                puzzle = parse_board(args.puzzle)
            except ValueError as e:
                print(f'Error: {e}')
                return
        elif args.builtin:
            name = args.builtin
            if name not in BUILTINpUZZLES:
                print(f'Error: unknown built-in '{name}'.')
                return
            puzzle = parse_board(BUILTINpUZZLES[name])
            diff = name
        else:
            print(f'  Generating {diff} puzzle...')
            puzzle, _ = generatepuzzle(diff)

        run_benchmark(puzzle, diff)

        if args.puzzle or args.builtin:
            break


def cmd_generate(args) -> None:
    '''
    Generate a puzzle and print it (without solving).
    '''
    diff = args.difficulty
    print(f'  Generating {diff} puzzle...')
    puzzle, solution = generatepuzzle(diff)
    given = sum(cell != 0 for row in puzzle for cell in row)
    print_board(puzzle,    f'Puzzle ({given} given cells)')
    if args.show_solution:
        print_board(solution, 'Solution')


#  argparse setup

def buildparser() -> 'argparse.ArgumentParser':
    import argparse

    parser = argparse.ArgumentParser(
        prog='sudoku',
        description='Sudoku solver — backtracking & optimisations',
        formatterclass=argparse.RawDescriptionHelpFormatter,
        epilog='''
examples:
  python sudoku.py solve
  python sudoku.py solve --builtin escargot --algo pure
  python sudoku.py solve --generate hard
  python sudoku.py solve --puzzle 530070000600195000098000060800060003400803001700020006060000280000419005000080079
  python sudoku.py benchmark
  python sudoku.py benchmark --difficulties hard expert
  python sudoku.py benchmark --builtin escargot
  python sudoku.py generate --difficulty expert --show-solution
        ''',
    )

    sub = parser.add_subparsers(dest='command', metavar='COMMAND')
    sub.required = True

    # solve
    p_solve = sub.addparser('solve', help='Solve a single puzzle')

    src = p_solve.add_mutually_exclusive_group()
    src.add_argument(
        '--puzzle', metavar='STRING',
        help='81-char puzzle string (0 or . for empty cells)',
    )
    src.add_argument(
        '--builtin', metavar='NAME',
        choices=list(BUILTINpUZZLES),
        help=f'Use a built-in puzzle: {', '.join(BUILTINpUZZLES)}',
    )
    src.add_argument(
        '--generate', metavar='DIFFICULTY',
        choices=list(DIFFICULTY),
        help='Generate a random puzzle at the given difficulty',
    )

    p_solve.add_argument(
        '--algo', metavar='ALGO',
        choices=list(ALG_NAMES),
        default='mrv_fc',
        help='Algorithm to use (default: mrv_fc). Choices: %(choices)s',
    )

    # benchmark
    p_bench = sub.addparser(
        'benchmark',
        help='Compare all algorithms on one or more puzzles',
    )

    src2 = p_bench.add_mutually_exclusive_group()
    src2.add_argument(
        '--puzzle', metavar='STRING',
        help='81-char puzzle string to benchmark',
    )
    src2.add_argument(
        '--builtin', metavar='NAME',
        choices=list(BUILTINpUZZLES),
        help='Use a built-in puzzle',
    )
    src2.add_argument(
        '--difficulties', metavar='DIFF', nargs='+',
        choices=list(DIFFICULTY),
        help='Generate random puzzles at these difficulties (default: all four)',
    )

    # generate
    p_gen = sub.addparser('generate', help='Generate and print a puzzle')
    p_gen.add_argument(
        '--difficulty', metavar='DIFF',
        choices=list(DIFFICULTY),
        default='medium',
        help='Difficulty level (default: medium)',
    )
    p_gen.add_argument(
        '--show-solution', action='store_true',
        help='Also print the solution',
    )

    return parser


def main() -> None:
    import argparse
    parser = buildparser()
    args = parser.parse_args()

    dispatch = {
        'solve':     cmd_solve,
        'benchmark': cmd_benchmark,
        'generate':  cmd_generate,
    }
    dispatch[args.command](args)


if __name__ == '__main__':
    main()
