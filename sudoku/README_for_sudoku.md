# Sudoku Solver — Backtracking & Optimisations

A 9×9 Sudoku solver implemented in Python for a Discrete Mathematics course.
The project demonstrates the backtracking algorithm and three progressively
smarter optimisations, a random puzzle generator, and a performance benchmark
that lets you directly compare how each approach behaves on the same puzzle.

---

## Requirements

- Python 3.10 or newer (uses `list[list[int]]` type hints)
- No third-party libraries required

---

## How to run

```bash
python sudoku.py <command> [options]
```

There are three commands: `solve`, `benchmark`, and `generate`.
Every command has its own `--help` flag:

```bash
python sudoku.py --help
python sudoku.py solve --help
python sudoku.py benchmark --help
python sudoku.py generate --help
```

---

## Commands

### `solve` — solve a single puzzle

Solves a puzzle and prints the input board, the solution, and solver statistics
(steps, backtracks, elapsed time).

```bash
python sudoku.py solve
```

**Puzzle source** (pick one, mutually exclusive):

| Flag | Description |
|------|-------------|
| *(none)* | Uses the built-in `classic` puzzle |
| `--builtin classic` | Built-in classic puzzle |
| `--builtin escargot` | Al Escargot — one of the hardest published Sudoku puzzles |
| `--generate <diff>` | Generate a random puzzle at the given difficulty |
| `--puzzle <string>` | Your own puzzle as an 81-character string |

`--generate` accepts: `easy` (40 givens), `medium` (30), `hard` (22), `expert` (17)

**Algorithm** (optional, default: `mrv_fc`):

| Flag | Algorithm |
|------|-----------|
| `--algo pure` | Pure backtracking |
| `--algo mrv` | Backtracking + MRV |
| `--algo mrv_fc` | Backtracking + MRV + Forward Checking |
| `--algo greedy` | Greedy / DFS |

**Examples:**

```bash
# Solve the default classic puzzle with the best algorithm
python sudoku.py solve

# Solve with pure backtracking to see the difference
python sudoku.py solve --algo pure

# Solve the hardest built-in puzzle
python sudoku.py solve --builtin escargot

# Solve a randomly generated hard puzzle
python sudoku.py solve --generate hard

# Solve with a specific algorithm
python sudoku.py solve --builtin escargot --algo mrv_fc

# Solve your own puzzle (81 chars, 0 or . for empty cells)
python sudoku.py solve --puzzle 530070000600195000098000060800060003400803001700020006060000280000419005000080079
```

---

### `benchmark` — compare all four algorithms

Runs all four algorithms on the same puzzle and prints a side-by-side table
showing steps, backtracks, and time for each. This is the most useful command
for seeing why optimisations matter.

```bash
python sudoku.py benchmark
```

By default generates random puzzles at all four difficulty levels in sequence.

**Options:**

| Flag | Description |
|------|-------------|
| *(none)* | Generate random puzzles at easy, medium, hard, and expert |
| `--difficulties hard expert` | Only benchmark the given difficulties |
| `--builtin escargot` | Benchmark on a built-in puzzle |
| `--puzzle <string>` | Benchmark on your own 81-char puzzle |

**Examples:**

```bash
# Full benchmark across all difficulties
python sudoku.py benchmark

# Only hard and expert
python sudoku.py benchmark --difficulties hard expert

# All algorithms on Al Escargot
python sudoku.py benchmark --builtin escargot
```

---

### `generate` — generate and print a puzzle

Generates a valid random puzzle and prints it without solving it.
Useful for getting a puzzle to paste into `--puzzle` or to solve by hand.

```bash
python sudoku.py generate
```

**Options:**

| Flag | Description |
|------|-------------|
| `--difficulty <level>` | `easy`, `medium`, `hard`, `expert` — default: `medium` |
| `--show-solution` | Also print the complete solution |

**Examples:**

```bash
# Generate a medium puzzle
python sudoku.py generate

# Generate an expert puzzle and show its solution
python sudoku.py generate --difficulty expert --show-solution
```

---

## Puzzle string format

Puzzles can be passed as an 81-character string, reading left-to-right,
top-to-bottom. Use `0` or `.` for empty cells. Spaces and newlines are ignored.

```
530070000600195000098000060800060003400803001700020006060000280000419005000080079
```

This corresponds to:

```
5 3 . │ . 7 . │ . . .
6 . . │ 1 9 5 │ . . .
. 9 8 │ . . . │ . 6 .
──────┼───────┼──────
8 . . │ . 6 . │ . . 3
4 . . │ 8 . 3 │ . . 1
7 . . │ . 2 . │ . . 6
──────┼───────┼──────
. 6 . │ . . . │ 2 8 .
. . . │ 4 1 9 │ . . 5
. . . │ . 8 . │ . 7 9
```

---

## How the puzzle generator works

Generating a valid Sudoku puzzle is a two-step process: first build a complete
fully solved board, then carefully remove cells from it.

### Step 1 — Build a complete solution

A blank 9×9 board is created and the **three diagonal 3×3 boxes** are filled
first, each with a shuffled permutation of digits 1–9. These three boxes
(top-left, centre, bottom-right) share no row, column, or box with each other,
so they can be filled independently without any constraint checks. Filling them
randomly is what seeds the uniqueness of every generated puzzle.

```
■ ■ ■ │ . . . │ . . .
■ ■ ■ │ . . . │ . . .
■ ■ ■ │ . . . │ . . .
───────┼───────┼───────
. . . │ ■ ■ ■ │ . . .
. . . │ ■ ■ ■ │ . . .
. . . │ ■ ■ ■ │ . . .
───────┼───────┼───────
. . . │ . . . │ ■ ■ ■
. . . │ . . . │ ■ ■ ■
. . . │ . . . │ ■ ■ ■
```

Once the diagonal boxes are filled, the remaining 54 empty cells are solved
using the `mrv_fc` algorithm. Because the diagonal boxes were filled randomly,
every run produces a completely different valid solution.

### Step 2 — Remove cells to create the puzzle

The target number of "given" (pre-filled) cells depends on difficulty:

| Difficulty | Given cells | Empty cells |
|------------|-------------|-------------|
| Easy       | 40          | 41          |
| Medium     | 30          | 51          |
| Hard       | 22          | 59          |
| Expert     | 17          | 64          |

All 81 cell positions are shuffled randomly. The generator removes cells one
by one, and after each removal runs the solver on the board to verify it still
has at least one valid solution. If removing a cell would break the puzzle,
that cell is restored and skipped. This continues until the target number of
given cells is reached, guaranteeing every generated puzzle is solvable.

---

## How the algorithms work

All four algorithms are forms of **depth-first search (DFS)** over the space
of partial board assignments. Think of every possible board state as a node
in a massive tree — the root is the empty board, each edge is "place digit N
in some cell", and the leaves are either complete solutions or contradictions.
The algorithms differ only in which cell they pick next, and how much they
look ahead to prune dead branches before going deeper.

### Constraint basics

Every time a digit is placed, three constraints must hold simultaneously:

- No duplicate in its **row** (9 cells)
- No duplicate in its **column** (9 cells)
- No duplicate in its **3×3 box** (9 cells)

A cell's **candidates** are the digits 1–9 that currently satisfy all three
constraints for that cell. A cell with zero candidates is a dead end — it
cannot be filled without violating a constraint somewhere, so the current
path must be abandoned and we backtrack.

---

### Algorithm 1 — Pure Backtracking

**Core idea:** search the tree blindly. Pick the next empty cell in fixed
order (left-to-right, top-to-bottom), try every digit 1–9, recurse, and undo
when stuck.

**Thinking behind it:** this is the simplest possible correct search. The key
insight is the **undo step** — by setting a cell back to 0 on failure, we
guarantee that every attempted digit in every branch is truly independent. The
algorithm is complete: it will always find a solution if one exists, and always
correctly report failure if none does.

**Why it can be slow:** it makes no attempt to detect impossible states early.
Imagine placing digit 5 in row 1, column 1. This immediately eliminates 5 as
a candidate for 20 other cells (the rest of row 1, column 1, and the top-left
box). Pure backtracking ignores this — it doesn't update anything globally. It
will later try to place a digit in a cell that has been made impossible, fail,
and only then backtrack. On hard puzzles it can explore hundreds of thousands
of states before finding the contradiction that was created much earlier.

```
find first empty cell (r, c)
for num in 1..9:
    if num is valid at (r, c):
        place num
        if solve(board): return True
        remove num        ← backtrack
return False              ← no digit worked, signal failure upward
```

---

### Algorithm 2 — Backtracking + MRV

**Core idea:** instead of always picking the first empty cell in order, pick
the empty cell that currently has the **fewest valid candidates**. This is the
Minimum Remaining Values (MRV) heuristic, also called the "fail-first" principle.

**Thinking behind it:** if a cell has only 1 candidate, there is no choice —
fill it now, it costs nothing and narrows the search. If a cell has 2 candidates
and you pick wrong, you discover the mistake almost immediately and backtrack
before wasting work on dozens of unrelated cells. Cells with many candidates
left for later when the board is more constrained. The analogy is to solve the
most constrained parts of a puzzle first, just as a human would naturally do.

**Why naive MRV is still slow:** to find the MRV cell, you need to count valid
candidates for every empty cell. Computing candidates means calling `is_valid`
9 times per cell (once per digit), and `is_valid` itself scans a row, column,
and box. Doing this from scratch at every recursive level is expensive and
largely undoes the gain from choosing cells smartly.

**Incremental candidate tracking:** the solution is to maintain a live
`candidates[r][c]` set for every empty cell and update it as placements happen:

- **Place** digit `d` at `(r, c)` → remove `d` from the candidate set of every
  **peer** (every cell that shares a row, column, or box). There are exactly 20
  peers for any cell in a 9×9 grid.
- **Backtrack** → add `d` back to exactly the peer sets it was removed from.

This makes finding the MRV cell a simple scan of set sizes — no `is_valid`
calls at all inside the hot recursive loop.

**Peer table:** to avoid rebuilding the peer set on every call, `PEERS[r][c]`
is precomputed once at startup as a `frozenset` of 20 `(row, col)` pairs for
every cell. This is a classic space-for-time trade-off.

```
build initial candidate sets from given cells
find cell (r, c) with minimum candidate count
for num in candidates[r][c]:
    place num, propagate removal to peer candidate sets
    if solve(): return True
    undo: restore num to (r,c) and all peer sets   ← backtrack
return False
```

---

### Algorithm 3 — Backtracking + MRV + Forward Checking

**Core idea:** after placing a digit and propagating it to peer candidate sets,
immediately inspect those updated sets. If any empty peer now has **zero
candidates**, the current placement has already made the board unsolvable.
Undo immediately without recursing any deeper.

**Thinking behind it:** MRV already detects wipe-outs at the start of each
recursive call — `_find_mrv_cell` returns `None` if any empty cell has no
candidates. But by then, we have already recursed into a dead branch. Forward
Checking catches the same wipe-out **one level earlier**, the instant it is
created during propagation. This prunes the subtree before it is ever entered.

The mental model: after placing digit 7 in a cell, you scan all 20 peers. If
one peer's candidate set just became empty, you already know this branch is
dead. There is no need to pick the next cell, try digits, or go any deeper —
undo and try something else immediately.

**Why it barely costs extra:** MRV already iterates over every peer to update
candidate sets. Forward Checking adds just one `len() == 0` check per peer
update — effectively free. There are no extra board scans or `is_valid` calls.

**The wipeout handling:** the propagation loop breaks as soon as a wipe-out
is detected, but the undo step still runs unconditionally — it restores every
peer set that was modified before the break, leaving the board in exactly the
same state it was in before the placement.

```
build initial candidate sets
find MRV cell (r, c)
for num in candidates[r][c]:
    place num
    propagate to peers:
        for each peer:
            remove num from peer's candidates
            if peer's candidates is now empty → wipeout, stop loop
    if no wipeout:
        if solve(): return True
    undo: restore (r,c) and all modified peer sets   ← backtrack
return False
```

---

### Algorithm 4 — Greedy / DFS

**Core idea:** use MRV to pick the best cell, but then commit to the **first**
candidate without exploring alternatives — the greedy choice. Only fall back to
trying other candidates if the greedy path leads to failure.

**Thinking behind it:** a greedy algorithm makes the locally best choice at
each step and never reconsiders. In Sudoku, the "locally best" value for a
cell is often the smallest or first valid digit. On easy puzzles where most
cells are heavily constrained, the greedy choice is usually correct and the
algorithm terminates quickly without any backtracking.

**Why it is here:** the greedy solver serves as a comparison baseline to
demonstrate a fundamental point — choosing **which cell** to fill (MRV) matters
far more than choosing **which value** to try first (greedy). Both MRV and
Greedy use the same cell selection, and on hard puzzles they typically take
the same number of steps. The greedy value choice provides no reliable
advantage and on some puzzles makes things slightly worse.

**Its real lesson:** greedy strategies work well on easy instances of a problem
but offer no correctness guarantee on hard ones. When the greedy choice is
wrong, the algorithm must fall back to full backtracking anyway, making it no
better than MRV in the worst case and harder to reason about.

```
find MRV cell (r, c)
try candidates[0] first (greedy)
    if solve(): return True
try candidates[1], candidates[2], ... in order (backtracking fallback)
    if any succeeds: return True
undo and return False
```

---

## Performance comparison

The table below is a representative benchmark on a hard randomly generated
puzzle. Exact numbers vary per run due to OS scheduling and Python interpreter
variance, but the relative ordering is consistent.

```
════════════════════════════════════════════════════════════
  Benchmark — difficulty: HARD
════════════════════════════════════════════════════════════
  Algorithm                    Steps  Backtracks  Time (ms)
  ──────────────────────────── ─────  ──────────  ─────────
  ✓ Pure Backtracking         80,491       8,911    128.93
  ✓ Backtracking + MRV           217         159      0.38
  ✓ Backtracking + MRV + FC      217         159      0.41
  ✓ Greedy / DFS                 217         159      1.20
════════════════════════════════════════════════════════════
```
les because both use identical
  cell selection. The greedy value choice is not a reliable improvement.
