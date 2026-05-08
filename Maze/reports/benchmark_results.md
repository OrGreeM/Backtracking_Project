# Benchmark Results — Maze Pathfinding Algorithms

Results obtained by running `python main.py benchmark --size <N>` on a randomly generated maze with ~1% of inner walls broken to introduce cycles.

> **Environment:** Windows 11, Python 3.13, single-core execution.  
> Each maze is generated once and then deep-copied for each algorithm so all solvers operate on an identical maze.

---

## Small Maze — 41×41 (1 681 cells, ~840 passable)

| Algorithm          | Time (ms) | Visited Cells | Path Length |
|--------------------|----------:|---------------:|------------:|
| DFS (classic)      |    1.6229 |            289 |         257 |
| Smart DFS          |    0.9866 |            158 |         127 |
| BFS                |    3.9669 |            809 |          97 |
| A\* (A-Star)       |    4.1129 |            365 |          97 |

---

## Medium Maze — 101×101 (10 201 cells, ~5 100 passable)

| Algorithm          | Time (ms) | Visited Cells | Path Length |
|--------------------|----------:|---------------:|------------:|
| DFS (classic)      |   16.1478 |          2 586 |         993 |
| Smart DFS          |   25.5990 |          2 827 |         351 |
| BFS                |   28.8912 |          4 994 |         223 |
| A\* (A-Star)       |   15.9521 |          1 636 |         223 |

---

## Large Maze — 201×201 (40 401 cells, ~20 200 passable)

| Algorithm          | Time (ms) | Visited Cells | Path Length |
|--------------------|----------:|---------------:|------------:|
| DFS (classic)      |   98.6377 |         16 304 |       6 301 |
| Smart DFS          |   17.8569 |          2 818 |       1 841 |
| BFS                |  126.7251 |         21 374 |         579 |
| A\* (A-Star)       |  165.7999 |         21 161 |         579 |

---

## Stress Test — 401×401 (160 801 cells, ~80 400 passable)

| Algorithm          | Time (ms) | Visited Cells | Path Length |
|--------------------|----------:|---------------:|------------:|
| DFS (classic)      |   47.3274 |         21 433 |       9 189 |
| Smart DFS          |   16.3545 |          6 094 |       4 113 |
| BFS                |  174.1557 |         85 532 |       1 141 |
| A\* (A-Star)       |  346.7027 |         83 182 |       1 141 |

---

## Key Observations

- **Path optimality:** BFS and A\* always find the **shortest** (optimal) path. DFS and Smart DFS find an arbitrary valid path, which is significantly longer (often 5× to 8× longer on larger mazes).
- **Heuristic guidance vs Heap overhead:** 
  - On smaller and medium mazes, A\* explores far fewer cells than BFS (e.g. 1,636 vs 4,994 on 101×101) and finishes much faster.
  - However, on very large mazes where both algorithms are forced to explore a high percentage of the grid (e.g., ~83k cells on 401×401), BFS can actually run faster in Python. This happens because BFS operates with $O(1)$ operations on a standard `deque`, whereas A\* incurs an $O(\log N)$ priority queue overhead with `heapq` on every single node insertion and deletion.
- **DFS High Variance:** Classic and Smart DFS show high variance because they stop searching as soon as they reach the goal. On 101×101, classic DFS got lucky and solved the maze faster than Smart DFS. However, on 201×201, Smart DFS's heuristic was incredibly effective, visiting only 2,818 cells compared to classic DFS's 16,304 cells.
- **Recursion Depth:** Both DFS variants rely on recursive backtracking. For large mazes, the maximum recursion depth matches the maze size. The benchmark script dynamically configures `sys.setrecursionlimit(h * w)` to prevent stack overflows.
