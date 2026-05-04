'''Sudoku — Backtracking solver with optimizations'''

import random
import time
from typing import Optional

#  Board instruments
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

def get_candidates(board: list[list[int]], row: int, col: int) -> list[int]:
    '''Return a list of all valid numbers for a given cell'''
    return [n for n in range(1, 10) if is_valid(board, row, col, n)]

def board_copy(board: list[list[int]]) -> list[list[int]]:
    '''Copies the board'''
    return [row[:] for row in board]


# Backtracking
class PureBacktracking:
    '''Classic DFS backtracking'''

    def __init__(self):
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

    def solve_visual(self, board: list[list[int]]):
        '''Generator for visual solving'''
        cell = find_empty(board)
        if cell is None:
            return True

        row, col = cell
        for num in range(1, 10):
            self.steps += 1
            if is_valid(board, row, col, num):
                board[row][col] = num
                yield (row, col, num)
                
                if (yield from self.solve_visual(board)):
                    return True
                    
                board[row][col] = 0
                self.backtracks += 1
                yield (row, col, 0)
        return False


# Backtracking + MRV
class BacktrackingMRV:
    '''Backtracking with Minimum Remaining Values'''

    def __init__(self):
        self.steps = 0
        self.backtracks = 0

    def find_mrv_cell(self, board: list[list[int]]) -> Optional[tuple[int, int]]:
        '''Returns the empty cell with the minimum number of valid candidates'''
        best = None
        best_count = 10
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    count = len(get_candidates(board, r, c))
                    if count == 0:
                        return None   # Dead end
                    if count < best_count:
                        best_count = count
                        best = (r, c)
        return best

    def solve(self, board: list[list[int]]) -> bool:
        '''Checking the state of the board: whether it is solved ot not'''
        cell = self.find_mrv_cell(board)
        if cell is None:
            # Either solved or dead end
            return find_empty(board) is None

        row, col = cell
        for num in get_candidates(board, row, col):
            self.steps += 1
            board[row][col] = num
            if self.solve(board):
                return True
            board[row][col] = 0
            self.backtracks += 1
        return False

    def solve_visual(self, board: list[list[int]]):
        '''Generator for visual solving'''
        cell = self.find_mrv_cell(board)
        if cell is None:
            return find_empty(board) is None

        row, col = cell
        for num in get_candidates(board, row, col):
            self.steps += 1
            board[row][col] = num
            yield (row, col, num)
            
            if (yield from self.solve_visual(board)):
                return True
                
            board[row][col] = 0
            self.backtracks += 1
            yield (row, col, 0)
        return False


#  Backtracking + MRV + Forward Checking
class BacktrackingMRVFC:
    '''Backtracking with MRV + Forward Checking'''

    def __init__(self):
        self.steps = 0
        self.backtracks = 0

    def find_mrv_cell(self, board):
        '''Finding cells for mrv'''
        best = None
        best_count = 10
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    count = len(get_candidates(board, r, c))
                    if count == 0:
                        return None
                    if count < best_count:
                        best_count = count
                        best = (r, c)
        return best

    def _forward_check(self, board, row, col) -> bool:
        '''
        After placing board[row][col], check all peers
        Returns False if any peer has zero candidates (dead end)
        '''
        peers = set()
        for i in range(9):
            peers.add((row, i))
            peers.add((i, col))

        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                peers.add((r, c))
        peers.discard((row, col))

        for r, c in peers:
            if board[r][c] == 0:
                if len(get_candidates(board, r, c)) == 0:
                    return False
        return True

    def solve(self, board: list[list[int]]) -> bool:
        '''Checking the state of the board: whether it is solved ot not'''
        cell = self.find_mrv_cell(board)
        if cell is None:
            return find_empty(board) is None

        row, col = cell
        for num in get_candidates(board, row, col):
            self.steps += 1
            board[row][col] = num
            if self._forward_check(board, row, col):
                if self.solve(board):
                    return True
            board[row][col] = 0
            self.backtracks += 1
        return False

    def solve_visual(self, board: list[list[int]]):
        '''Generator for visual solving'''
        cell = self.find_mrv_cell(board)
        if cell is None:
            return find_empty(board) is None

        row, col = cell
        for num in get_candidates(board, row, col):
            self.steps += 1
            board[row][col] = num
            yield (row, col, num)
            
            if self._forward_check(board, row, col):
                if (yield from self.solve_visual(board)):
                    return True
                    
            board[row][col] = 0
            self.backtracks += 1
            yield (row, col, 0)
        return False

#  Greedy algorithm
class GreedySolver:
    '''Greedy algorithm'''

    def __init__(self):
        self.steps = 0
        self.backtracks = 0

    def find_mrv_cell(self, board):
        '''Finding cells for mrv'''
        best = None
        best_count = 10
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    cands = get_candidates(board, r, c)
                    if len(cands) == 0:
                        return None, []
                    if len(cands) < best_count:
                        best_count = len(cands)
                        best = (r, c)
        if best is None:
            return None, []
        return best, get_candidates(board, best[0], best[1])

    def solve(self, board: list[list[int]]) -> bool:
        '''Checking the state of the board: whether it is solved ot not'''
        cell, candidates = self.find_mrv_cell(board)
        if cell is None:
            return find_empty(board) is None

        row, col = cell
        # Greedy: try only first candidate without exploring others
        if candidates:
            self.steps += 1
            board[row][col] = candidates[0]
            if self.solve(board):
                return True
            # If greedy fails, fall back to trying remaining candidates
            for num in candidates[1:]:
                self.steps += 1
                self.backtracks += 1
                board[row][col] = num
                if self.solve(board):
                    return True
            board[row][col] = 0
            self.backtracks += 1
        return False

    def solve_visual(self, board: list[list[int]]):
        '''Generator for visual solving'''
        cell, candidates = self.find_mrv_cell(board)
        if cell is None:
            return find_empty(board) is None

        row, col = cell
        if candidates:
            self.steps += 1
            board[row][col] = candidates[0]
            yield (row, col, candidates[0])
            
            if (yield from self.solve_visual(board)):
                return True
                
            for num in candidates[1:]:
                self.steps += 1
                self.backtracks += 1
                board[row][col] = num
                yield (row, col, num)
                
                if (yield from self.solve_visual(board)):
                    return True
                    
            board[row][col] = 0
            self.backtracks += 1
            yield (row, col, 0)
        return False


#  Sudoku Generator
DIFFICULTY = {
    'easy':   40,
    'medium': 30,
    'hard':   22,
    'expert': 17,
}


def generate_puzzle(difficulty: str = 'medium') -> tuple[list[list[int]], list[list[int]]]:
    '''
    Generate a random valid Sudoku puzzle.
    Returns:
        puzzle  — board with some cells removed (zeros = empty)
        solution — the complete solved board
    '''
    given_count = DIFFICULTY.get(difficulty, 30)

    board = [[0] * 9 for _ in range(9)]
    _fill_diagonal_boxes(board)
    solver = BacktrackingMRVFC()
    solver.solve(board)
    solution = board_copy(board)

    puzzle = board_copy(solution)
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    removed = 0
    target_remove = 81 - given_count
    for r, c in cells:
        if removed >= target_remove:
            break
        backup = puzzle[r][c]
        puzzle[r][c] = 0
        # Verifying the puzzle still has a unique solution
        test = board_copy(puzzle)
        s = BacktrackingMRVFC()
        if s.solve(test):
            removed += 1
        else:
            puzzle[r][c] = backup  # Restores if no unique solution

    return puzzle, solution


def _fill_diagonal_boxes(board: list[list[int]]) -> None:
    '''Fill the three diagonal 3x3 boxes with random digits (they don't affect each other).'''
    for box in range(3):
        digits = list(range(1, 10))
        random.shuffle(digits)
        start = box * 3
        for i in range(3):
            for j in range(3):
                board[start + i][start + j] = digits[i * 3 + j]


#  Benchmark with the results
def run_benchmark(puzzle: list[list[int]], difficulty: str) -> None:
    '''Running a benchmark'''
    algorithms = [
        ('Pure Backtracking',         PureBacktracking),
        ('Backtracking + MRV',        BacktrackingMRV),
        ('Backtracking + MRV + FC',   BacktrackingMRVFC),
        ('Greedy / DFS',              GreedySolver),
    ]

    print(f'\n{'─' * 60}')
    print(f'  Benchmark difficulty: {difficulty.upper()}')
    print(f'{'─' * 60}')
    print(f'  {'Algorithm':<28} {'Steps':>8} {'Backtracks':>11} {'Time (ms)':>10}')
    print(f'  {'─' * 28} {'─' * 8} {'─' * 11} {'─' * 10}')

    for name, AlgClass in algorithms:
        board = board_copy(puzzle)
        alg = AlgClass()
        t0 = time.perf_counter()
        solved = alg.solve(board)
        elapsed = (time.perf_counter() - t0) * 1000
        status = '✓' if solved else '✗'
        print(f'  {status} {name:<27} {alg.steps:>8,} {alg.backtracks:>11,} {elapsed:>9.2f}')

    print(f'{'═' * 60}')


#  Interactive solver
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

def solve_puzzle(puzzle: list[list[int]], algorithm: str = 'mrv_fc') -> dict:
    '''Solves a puzzle with the chosen algorithm.'''
    alg_map = {
        'pure':   PureBacktracking,
        'mrv':    BacktrackingMRV,
        'mrv_fc': BacktrackingMRVFC,
        'greedy': GreedySolver,
    }
    AlgClass = alg_map.get(algorithm, BacktrackingMRVFC)
    board = board_copy(puzzle)
    alg = AlgClass()
    t0 = time.perf_counter()
    solved = alg.solve(board)
    elapsed = (time.perf_counter() - t0) * 1000
    return {
        'solved':      solved,
        'board':       board,
        'steps':       alg.steps,
        'backtracks':  alg.backtracks,
        'time_ms':     round(elapsed, 3),
    }


def main():
    print(r'''  _____           _       _
 / ____|         | |     | |
| (___  _   _  __| | ___ | | ___   _
 \___ \| | | |/ _` |/ _ \| |/ / | | |
 ____) | |_| | (_| | (_) |   <| |_| |
|_____/ \__,_|\__,_|\___/|_|\_\\__,_|

 _____       _
/ ____|     | |
| (___   ___ | |_   _____ _ __
 \___ \ / _ \| \ \ / / _ \ '__|
 ____) | (_) | |\ V /  __/ |
|_____/ \___/|_| \_/ \___|_|   ''')

    classic = parse_board(
        '530070000'
        '600195000'
        '098000060'
        '800060003'
        '400803001'
        '700020006'
        '060000280'
        '000419005'
        '000080079'
    )
    print_board(classic, 'Classic puzzle (input)')

    result = solve_puzzle(classic, algorithm='mrv_fc')
    print_board(result['board'], 'Solved (MRV + Forward Checking)')
    print(f'  Steps: {result['steps']:,}  |  Backtracks: {result['backtracks']:,}  |  Time: {result['time_ms']} ms')

    # Random puzzle generation + benchmark
    for diff in ['easy', 'medium', 'hard', 'expert']:
        print(f'\n  Generating {diff} puzzle...')
        puzzle, solution = generate_puzzle(diff)
        given = sum(1 for r in range(9) for c in range(9) if puzzle[r][c] != 0)
        print(f'  Given cells: {given}')
        if diff == 'hard':
            print_board(puzzle, f'Random {diff} puzzle')
        run_benchmark(puzzle, diff)

    #  Solve a user-supplied puzzle
    print('\n' + '─' * 60)
    print("Solving a 'World's Hardest Sudoku'")
    hard_puzzle = parse_board(
        '100007090'
        '030020008'
        '009600500'
        '005300900'
        '010080002'
        '600004000'
        '300000010'
        '040000007'
        '007000300'
    )
    print_board(hard_puzzle, 'Al Escargot hard puzzle')
    for alg_name, alg_key in [('Pure Backtracking', 'pure'), ('MRV + FC', 'mrv_fc')]:
        r = solve_puzzle(hard_puzzle, alg_key)
        status = 'Solved' if r['solved'] else 'Failed'
        print(f'  {alg_name}: {status} | Steps: {r['steps']:,} | Backtracks: {r['backtracks']:,} | {r['time_ms']} ms')


if __name__ == '__main__':
    main()
