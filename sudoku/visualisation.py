'''
Visualisation

Usage
-----
  python sudoku_vis.py                          # classic puzzle, mrv_fc
  python sudoku_vis.py --algo pure              # watch pure backtracking
  python sudoku_vis.py --generate hard          # random hard puzzle
  python sudoku_vis.py --builtin escargot       # Al Escargot
  python sudoku_vis.py --puzzle 530...079       # 81-char string
  python sudoku_vis.py --algo pure --speed 2    # 1=slow … 5=fast (default 3)

Controls (while the window is open)
-------------------------------------
  SPACE   pause / resume
  R       restart with a new puzzle (same settings)
  Q / ESC quit
'''

import sys
import time
import argparse
import threading
import queue

import pygame

try:
    from sudoku import (
        board_copy, parse_board, generate_puzzle,
        find_empty, is_valid, get_candidates,
        PEERS, DIFFICULTY,
        PureBacktracking, BacktrackingMRV, BacktrackingMRVFC, GreedySolver,
        BUILTIN_PUZZLES, ALG_NAMES,
    )
except ImportError as e:
    print(f"Error: could not import from sudoku.py — {e}")
    print("Make sure sudoku_vis.py is in the same directory as sudoku.py.")
    sys.exit(1)



COL_BG          = (245, 245, 245)
COL_GRID_THIN   = (180, 180, 180)
COL_GRID_THICK  = ( 40,  40,  40)
COL_GIVEN_BG    = (220, 225, 235)
COL_GIVEN_TEXT  = ( 30,  60, 130)
COL_SOLVED_TEXT = ( 20, 120,  60)
COL_ACTIVE      = ( 80, 160, 255)
COL_PLACE       = (180, 235, 180)
COL_BACKTRACK   = (255, 190, 190)
COL_PANEL_BG    = ( 30,  30,  40)
COL_PANEL_TEXT  = (220, 220, 220)
COL_LABEL       = (160, 160, 170)
COL_HIGHLIGHT   = (255, 210,  50)
COL_DONE_BG     = ( 30, 140,  80)
COL_DONE_TEXT   = (255, 255, 255)
COL_BTN         = ( 60,  70,  90)
COL_BTN_HOVER   = ( 90, 105, 130)
COL_BTN_TEXT    = (220, 220, 220)



#  Layout constants

CELL        = 62
GRID_SIZE   = CELL * 9
MARGIN      = 20
PANEL_W     = 220
WIN_W       = GRID_SIZE + MARGIN * 2 + PANEL_W
WIN_H       = GRID_SIZE + MARGIN * 2 + 60
GRID_X      = MARGIN
GRID_Y      = MARGIN + 50



class RecordingPureBacktracking:
    def __init__(self):
        self.steps_count  = 0
        self.backtracks   = 0
        self.history: list[dict] = []

    def solve(self, board):
        cell = find_empty(board)
        if cell is None:
            return True
        row, col = cell
        for num in range(1, 10):
            self.steps_count += 1
            if is_valid(board, row, col, num):
                board[row][col] = num
                self.history.append({"kind": "place", "r": row, "c": col, "val": num})
                if self.solve(board):
                    return True
                board[row][col] = 0
                self.history.append({"kind": "backtrack", "r": row, "c": col, "val": 0})
                self.backtracks += 1
        return False


class RecordingMRVFC:
    def __init__(self):
        self.steps_count  = 0
        self.backtracks   = 0
        self.history: list[dict] = []

    def _build_candidates(self, board):
        cands = [[set() if board[r][c] != 0 else set(range(1, 10))
                  for c in range(9)] for r in range(9)]
        for r in range(9):
            for c in range(9):
                if board[r][c] != 0:
                    d = board[r][c]
                    for (pr, pc) in PEERS[r][c]:
                        cands[pr][pc].discard(d)
        return cands

    def _find_mrv(self, board, cands):
        best, best_n = None, 10
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    n = len(cands[r][c])
                    if n == 0:
                        return None
                    if n < best_n:
                        best_n, best = n, (r, c)
        return best

    def solve(self, board):
        cands = self._build_candidates(board)
        return self._solve(board, cands)

    def _solve(self, board, cands):
        cell = self._find_mrv(board, cands)
        if cell is None:
            return find_empty(board) is None
        row, col = cell
        for num in list(cands[row][col]):
            self.steps_count += 1
            board[row][col] = num
            self.history.append({"kind": "place", "r": row, "c": col, "val": num})

            saved_own = cands[row][col].copy()
            cands[row][col] = set()
            removed = []
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
            self.history.append({"kind": "backtrack", "r": row, "c": col, "val": 0})
            cands[row][col] = saved_own
            for (pr, pc) in removed:
                cands[pr][pc].add(num)
            self.backtracks += 1
        return False


class RecordingMRV:
    """MRV without forward checking — same recording pattern."""
    def __init__(self):
        self.steps_count  = 0
        self.backtracks   = 0
        self.history: list[dict] = []

    def _build_candidates(self, board):
        cands = [[set() if board[r][c] != 0 else set(range(1, 10))
                  for c in range(9)] for r in range(9)]
        for r in range(9):
            for c in range(9):
                if board[r][c] != 0:
                    d = board[r][c]
                    for (pr, pc) in PEERS[r][c]:
                        cands[pr][pc].discard(d)
        return cands

    def _find_mrv(self, board, cands):
        best, best_n = None, 10
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    n = len(cands[r][c])
                    if n == 0:
                        return None
                    if n < best_n:
                        best_n, best = n, (r, c)
        return best

    def solve(self, board):
        cands = self._build_candidates(board)
        return self._solve(board, cands)

    def _solve(self, board, cands):
        cell = self._find_mrv(board, cands)
        if cell is None:
            return find_empty(board) is None
        row, col = cell
        for num in list(cands[row][col]):
            self.steps_count += 1
            board[row][col] = num
            self.history.append({"kind": "place", "r": row, "c": col, "val": num})
            saved_own = cands[row][col].copy()
            cands[row][col] = set()
            removed = []
            for (pr, pc) in PEERS[row][col]:
                if num in cands[pr][pc]:
                    cands[pr][pc].discard(num)
                    removed.append((pr, pc))
            if self._solve(board, cands):
                return True
            board[row][col] = 0
            self.history.append({"kind": "backtrack", "r": row, "c": col, "val": 0})
            cands[row][col] = saved_own
            for (pr, pc) in removed:
                cands[pr][pc].add(num)
            self.backtracks += 1
        return False


class RecordingGreedy:
    def __init__(self):
        self.steps_count  = 0
        self.backtracks   = 0
        self.history: list[dict] = []

    def _find_mrv_cell(self, board):
        best, best_count = None, 10
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

    def solve(self, board):
        cell, candidates = self._find_mrv_cell(board)
        if cell is None:
            return find_empty(board) is None
        row, col = cell
        if candidates:
            self.steps_count += 1
            board[row][col] = candidates[0]
            self.history.append({"kind": "place", "r": row, "c": col, "val": candidates[0]})
            if self.solve(board):
                return True
            for num in candidates[1:]:
                self.steps_count += 1
                self.backtracks += 1
                board[row][col] = num
                self.history.append({"kind": "place", "r": row, "c": col, "val": num})
                if self.solve(board):
                    return True
                self.history.append({"kind": "backtrack", "r": row, "c": col, "val": 0})
            board[row][col] = 0
            self.history.append({"kind": "backtrack", "r": row, "c": col, "val": 0})
            self.backtracks += 1
        return False


RECORDING_SOLVERS = {
    "pure":   RecordingPureBacktracking,
    "mrv":    RecordingMRV,
    "mrv_fc": RecordingMRVFC,
    "greedy": RecordingGreedy,
}


SPEED_DELAY = {1: 300, 2: 80, 3: 18, 4: 4, 5: 0}



def cell_rect(r, c) -> pygame.Rect:
    x = GRID_X + c * CELL
    y = GRID_Y + r * CELL
    return pygame.Rect(x, y, CELL, CELL)


def draw_grid(surf, given, board, active_rc, flash):
    """Draw every cell: background, value, candidates hint."""
    font_big  = pygame.font.SysFont("segoeui", 34, bold=True)
    font_small= pygame.font.SysFont("segoeui", 13)

    for r in range(9):
        for c in range(9):
            rect = cell_rect(r, c)
            rc   = (r, c)

            if rc == active_rc:
                bg = COL_ACTIVE
            elif rc in flash:
                bg = COL_PLACE if flash[rc] == "place" else COL_BACKTRACK
            elif given[r][c]:
                bg = COL_GIVEN_BG
            else:
                bg = COL_BG

            pygame.draw.rect(surf, bg, rect)


            val = board[r][c]
            if val != 0:
                colour = COL_GIVEN_TEXT if given[r][c] else COL_SOLVED_TEXT
                txt = font_big.render(str(val), True, colour)
                surf.blit(txt, txt.get_rect(center=rect.center))

    for i in range(10):
        thick = 3 if i % 3 == 0 else 1
        col   = COL_GRID_THICK if i % 3 == 0 else COL_GRID_THIN
        # horizontal
        y = GRID_Y + i * CELL
        pygame.draw.line(surf, col, (GRID_X, y), (GRID_X + GRID_SIZE, y), thick)
        # vertical
        x = GRID_X + i * CELL
        pygame.draw.line(surf, col, (x, GRID_Y), (x, GRID_Y + GRID_SIZE), thick)


def draw_panel(surf, algo_key, steps, backtracks, elapsed_ms,
               paused, done, speed, waiting=False):
    """Draw the right-hand info panel."""
    px = GRID_X + GRID_SIZE + MARGIN
    py = GRID_Y
    pw = PANEL_W - MARGIN
    ph = GRID_SIZE


    pygame.draw.rect(surf, COL_PANEL_BG, (px, py, pw, ph), border_radius=10)

    font_title = pygame.font.SysFont("segoeui", 16, bold=True)
    font_label = pygame.font.SysFont("segoeui", 13)
    font_val   = pygame.font.SysFont("segoeui", 26, bold=True)
    font_key   = pygame.font.SysFont("segoeui", 13)

    y = py + 18
    gap_section = 28
    gap_stat    = 50

    alg_name = ALG_NAMES.get(algo_key, algo_key)

    words = alg_name.split()
    line, lines = "", []
    for w in words:
        test = (line + " " + w).strip()
        if font_title.size(test)[0] < pw - 20:
            line = test
        else:
            lines.append(line); line = w
    lines.append(line)
    for ln in lines:
        t = font_title.render(ln, True, COL_PANEL_TEXT)
        surf.blit(t, (px + 12, y))
        y += 20
    y += 6


    pygame.draw.line(surf, (80, 80, 100), (px + 10, y), (px + pw - 10, y), 1)
    y += gap_section

    stats = [
        ("Steps",      f"{steps:,}"),
        ("Backtracks", f"{backtracks:,}"),
        ("Time",       f"{elapsed_ms:.0f} ms"),
        ("Speed",      f"{'▶' * speed}  ({speed}/5)"),
    ]
    for label, value in stats:
        lbl = font_label.render(label, True, COL_LABEL)
        surf.blit(lbl, (px + 12, y))
        val = font_val.render(value, True, COL_HIGHLIGHT)
        surf.blit(val, (px + 12, y + 16))
        y += gap_stat

    y += 10
    pygame.draw.line(surf, (80, 80, 100), (px + 10, y), (px + pw - 10, y), 1)
    y += gap_section

    if waiting:
        badge_col  = (60, 40, 110)
        badge_text = " PRESS SPACE "
    elif done:
        badge_col  = COL_DONE_BG
        badge_text = "  SOLVED  "
    elif paused:
        badge_col  = (100, 80, 20)
        badge_text = "  PAUSED  "
    else:
        badge_col  = (40, 80, 140)
        badge_text = " SOLVING… "

    bt = font_title.render(badge_text, True, COL_DONE_TEXT)
    br = bt.get_rect()
    br.topleft = (px + 12, y)
    pygame.draw.rect(surf, badge_col, br.inflate(6, 6), border_radius=6)
    surf.blit(bt, br)
    y += 40


    hints = [
        ("SPACE", "start / pause"),
        ("R",     "restart"),
        ("Q/ESC", "quit"),
        ("↑↓",    "change speed"),
    ]
    for key, hint in hints:
        k = font_key.render(f"[{key}]", True, COL_HIGHLIGHT)
        h = font_key.render(f"  {hint}", True, COL_LABEL)
        surf.blit(k, (px + 12, y))
        surf.blit(h, (px + 12 + k.get_width(), y))
        y += 18


def draw_title(surf, label):
    font = pygame.font.SysFont("segoeui", 20, bold=True)
    t = font.render(f"Sudoku Solver  —  {label}", True, COL_GRID_THICK)
    surf.blit(t, (GRID_X, MARGIN + 12))




def run_visualiser(puzzle: list[list[int]], algo_key: str,
                   speed: int, label: str) -> bool:
    """
    Run the pygame window.
    Returns True if the user pressed R (restart), False to quit.
    """
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Sudoku — Backtracking Visualiser")
    clock  = pygame.time.Clock()


    given = [[puzzle[r][c] != 0 for c in range(9)] for r in range(9)]


    board_work = board_copy(puzzle)
    Solver     = RECORDING_SOLVERS[algo_key]
    solver     = Solver()

    solve_thread = threading.Thread(target=solver.solve, args=(board_work,), daemon=True)
    solve_thread.start()

    # Playback state
    board_vis  = board_copy(puzzle)
    step_idx   = 0
    paused     = False
    waiting    = True
    done       = False
    last_step  = time.perf_counter()
    elapsed_ms = 0.0
    flash: dict[tuple[int,int], str] = {}
    flash_ttl:  dict[tuple[int,int], int]   = {}
    active_rc  = None
    steps_shown    = 0
    backtracks_shown = 0

    FLASH_FRAMES = 6

    while True:
        dt_ms = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit()
                    return False
                if event.key == pygame.K_r:
                    pygame.quit()
                    return True
                if event.key == pygame.K_SPACE:
                    if waiting:
                        waiting = False
                    else:
                        paused = not paused
                if event.key == pygame.K_UP:
                    speed = min(5, speed + 1)
                if event.key == pygame.K_DOWN:
                    speed = max(1, speed - 1)


        delay = SPEED_DELAY[speed] / 1000.0

        if not waiting and not paused and not done:
            now = time.perf_counter()

            steps_per_frame = 1 if delay > 0 else 200

            for _ in range(steps_per_frame):
                if step_idx < len(solver.history):
                    if delay == 0 or (now - last_step) >= delay:
                        step = solver.history[step_idx]
                        step_idx += 1
                        r, c, val, kind = step["r"], step["c"], step["val"], step["kind"]
                        board_vis[r][c] = val
                        active_rc = (r, c)
                        flash[(r, c)]     = kind
                        flash_ttl[(r, c)] = FLASH_FRAMES
                        if kind == "place":
                            steps_shown += 1
                        else:
                            backtracks_shown += 1
                        elapsed_ms += delay * 1000
                        last_step = now
                elif solve_thread.is_alive():
                    pass
                else:
                    done = True
                    active_rc = None
                    elapsed_ms = solver.steps_count * delay * 1000
                    break

        for rc in list(flash_ttl.keys()):
            flash_ttl[rc] -= 1
            if flash_ttl[rc] <= 0:
                del flash_ttl[rc]
                del flash[rc]

        screen.fill(COL_BG)
        draw_title(screen, label)
        draw_grid(screen, given, board_vis, active_rc, flash)
        draw_panel(screen, algo_key,
                   steps_shown, backtracks_shown, elapsed_ms,
                   paused, done, speed, waiting)
        pygame.display.flip()

    return False


def build_parser():
    p = argparse.ArgumentParser(
        prog="sudoku_vis",
        description="Pygame visualiser for the Sudoku backtracking solver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python sudoku_vis.py
  python sudoku_vis.py --algo pure
  python sudoku_vis.py --algo pure --speed 2
  python sudoku_vis.py --generate hard
  python sudoku_vis.py --builtin escargot --algo mrv_fc
  python sudoku_vis.py --puzzle 530070000600195000098000060800060003400803001700020006060000280000419005000080079
        """,
    )

    src = p.add_mutually_exclusive_group()
    src.add_argument("--puzzle",  metavar="STRING",
                     help="81-char puzzle string (0 or . = empty)")
    src.add_argument("--builtin", metavar="NAME",
                     choices=list(BUILTIN_PUZZLES),
                     help=f"Built-in puzzle: {', '.join(BUILTIN_PUZZLES)}")
    src.add_argument("--generate", metavar="DIFF",
                     choices=list(DIFFICULTY),
                     help="Generate a random puzzle at this difficulty")

    p.add_argument("--algo",  metavar="ALGO",
                   choices=list(RECORDING_SOLVERS),
                   default="mrv_fc",
                   help="Algorithm (default: mrv_fc)")
    p.add_argument("--speed", metavar="N", type=int,
                   choices=[1, 2, 3, 4, 5], default=1,
                   help="Animation speed 1 (slow) … 5 (instant) — default 1")
    return p


def main():
    args = build_parser().parse_args()

    if args.puzzle:
        try:
            puzzle = parse_board(args.puzzle)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
        label = "custom puzzle"

    elif args.generate:
        print(f"Generating {args.generate} puzzle…", flush=True)
        puzzle, _ = generate_puzzle(args.generate)
        given_n   = sum(puzzle[r][c] != 0 for r in range(9) for c in range(9))
        label     = f"random {args.generate} ({given_n} given)"

    else:
        name   = args.builtin or "classic"
        puzzle = parse_board(BUILTIN_PUZZLES[name])
        label  = f"built-in: {name}"

    algo  = args.algo
    speed = args.speed


    while True:
        restart = run_visualiser(puzzle, algo, speed, label)
        if not restart:
            break


if __name__ == "__main__":
    main()
