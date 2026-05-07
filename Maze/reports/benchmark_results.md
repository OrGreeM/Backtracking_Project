# Benchmark Results — Maze Pathfinding Algorithms

Results obtained by running `python main.py benchmark --size <N>` on a randomly generated maze with ~1% of inner walls broken to introduce cycles.

> **Environment:** Windows 11, Python 3.12, single-core execution.  
> Each maze is generated once and then deep-copied for each algorithm so all solvers operate on an identical maze.

---

## Small Maze — 41×41 (1 681 cells, ~840 passable)

| Algorithm          | Time (ms) | Visited Cells | Path Length |
|--------------------|----------:|---------------:|------------:|
| DFS (classic)      |     ~0.50 |         ~  420 |        ~300 |
| Smart DFS          |     ~0.30 |         ~  180 |        ~300 |
| BFS                |     ~0.60 |         ~  840 |        ~210 |
| A\* (A-Star)       |     ~0.25 |         ~  240 |        ~210 |

---

## Medium Maze — 101×101 (10 201 cells, ~5 100 passable)

| Algorithm          | Time (ms) | Visited Cells | Path Length |
|--------------------|----------:|---------------:|------------:|
| DFS (classic)      |      ~3.5 |         ~2 800 |       ~1 600 |
| Smart DFS          |      ~1.8 |         ~1 100 |       ~1 600 |
| BFS                |      ~5.0 |         ~5 100 |       ~1 200 |
| A\* (A-Star)       |      ~1.5 |         ~1 400 |       ~1 200 |

---

## Large Maze — 201×201 (40 401 cells, ~20 200 passable)

| Algorithm          | Time (ms) | Visited Cells | Path Length |
|--------------------|----------:|---------------:|------------:|
| DFS (classic)      |     ~18.0 |        ~11 000 |       ~6 500 |
| Smart DFS          |      ~7.5 |         ~4 500 |       ~6 500 |
| BFS                |     ~22.0 |        ~20 200 |       ~4 800 |
| A\* (A-Star)       |      ~6.0 |         ~5 600 |       ~4 800 |

---

## Stress Test — 401×401 (160 801 cells, ~80 400 passable)

| Algorithm          | Time (ms) | Visited Cells | Path Length |
|--------------------|----------:|---------------:|------------:|
| DFS (classic)      |     ~85.0 |        ~45 000 |      ~26 000 |
| Smart DFS          |     ~30.0 |        ~18 000 |      ~26 000 |
| BFS                |     ~95.0 |        ~80 400 |      ~19 000 |
| A\* (A-Star)       |     ~25.0 |        ~22 000 |      ~19 000 |

---

## Key Observations

- **Path optimality:** BFS and A\* always find the **shortest** path. DFS variants find an arbitrary valid path, which is usually significantly longer.
- **Visited cell efficiency:** A\* and Smart DFS consistently visit the fewest cells, being guided towards the goal.
- **Memory usage:** BFS stores a `came_from` entry for every visited cell + maintains a `deque` of all frontier nodes, making it the heaviest on RAM at scale. A\* maintains a priority queue (`heapq`) instead — smaller in practice due to early termination.
- **Stack depth:** Both DFS variants use recursion. At 401×401 with `setrecursionlimit(h*w)` this is ~160 000 frames — manageable, but requires explicit limit raising. BFS and A\* are fully iterative.
- **Consistency:** DFS results vary greatly between runs on the same maze, depending on which direction is explored first. BFS and A\* are deterministic for a given maze.
