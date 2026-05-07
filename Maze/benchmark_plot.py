"""
Benchmark visualizer for Maze pathfinding algorithms.

Runs 100 trials per maze size. On each trial, a single maze is generated
and all algorithms for that size solve it (on deep copies). Results are
averaged and plotted with matplotlib.

BFS is excluded from the large maze because it must visit ~100% of cells
and adds no new information at that scale.

Run:
    python benchmark_plot.py
"""

import copy
import sys
import time

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from generator import MazeGenerator
from solvers import MazeSolver, SmartMazeSolver, BFSMazeSolver, AStarMazeSolver


# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
ALL_ALGORITHMS = [
    ("DFS",       MazeSolver,       "#e74c3c"),
    ("Smart DFS", SmartMazeSolver,  "#f39c12"),
    ("BFS",       BFSMazeSolver,    "#3498db"),
    ("A*",        AStarMazeSolver,  "#2ecc71"),
]

# Per-size config: (display_label, size, [algo_names_to_include])
# BFS excluded from large — it trivially visits ~100% of cells
SIZES = [
    ("Small\n41×41",    41,  ["DFS", "Smart DFS", "BFS", "A*"]),
    ("Medium\n101×101", 101, ["DFS", "Smart DFS", "BFS", "A*"]),
    ("Large\n401×401",  401, ["DFS", "Smart DFS", "A*"]),
]

N_RUNS = 100

# ──────────────────────────────────────────────
# Lookup helpers
# ──────────────────────────────────────────────
_ALGO_MAP   = {name: cls   for name, cls, _   in ALL_ALGORITHMS}
_COLOR_MAP  = {name: color for name, _,  color in ALL_ALGORITHMS}
_ALL_NAMES  = [name for name, _, _ in ALL_ALGORITHMS]


# ──────────────────────────────────────────────
# Benchmark runner
# ──────────────────────────────────────────────

def run_benchmark(size: int, algo_names: list[str], n_runs: int) -> dict:
    """
    Returns {algo_name: {"times": [...], "visited": [...], "path": [...]}}
    Only the algorithms listed in algo_names are run.
    """
    results = {name: {"times": [], "visited": [], "path": []} for name in algo_names}

    for run_idx in range(n_runs):
        if (run_idx + 1) % 10 == 0 or run_idx == 0:
            print(f"    run {run_idx + 1}/{n_runs}", flush=True)

        generator = MazeGenerator(size, size)
        maze = generator.generate()
        walls_to_break = max(1, size * size // 100)
        maze.break_random_walls(walls_to_break)

        for name in algo_names:
            solver = _ALGO_MAP[name](copy.deepcopy(maze))
            t0 = time.perf_counter()
            solver.solve()
            elapsed_ms = (time.perf_counter() - t0) * 1000

            results[name]["times"].append(elapsed_ms)
            results[name]["visited"].append(len(solver.visited))
            results[name]["path"].append(len(solver.path))

    return results


# ──────────────────────────────────────────────
# Plotting helpers
# ──────────────────────────────────────────────

def _bar_group(ax, x_positions, x_labels, bars_data, ylabel, title, log_scale=False):
    """
    Grouped bar chart.
    bars_data: list of (algo_name, values_per_x, stds_per_x)
    x_positions: np.arange(n_groups)
    Missing values (None) are skipped.
    """
    n_algos = len(bars_data)
    width = 0.8 / n_algos
    offsets = np.linspace(-(n_algos - 1) / 2, (n_algos - 1) / 2, n_algos) * width

    for i, (name, values, stds) in enumerate(bars_data):
        color = _COLOR_MAP[name]
        for j, (val, std) in enumerate(zip(values, stds)):
            if val is None:
                continue
            xpos = x_positions[j] + offsets[i]
            ax.bar(xpos, val, width=width * 0.92, color=color,
                   yerr=std, capsize=3,
                   error_kw={"elinewidth": 1, "alpha": 0.7},
                   alpha=0.88, label=name if j == 0 else "_nolegend_")
            lbl = f"{val:.1f}" if val < 100 else f"{int(val):,}"
            ax.text(xpos, val + std * 0.05 + val * 0.02, lbl,
                    ha="center", va="bottom", fontsize=6.5, color="#333333")

    if log_scale:
        ax.set_yscale("log")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)


def _line_scaling(ax, all_results, metric, ylabel, title):
    """
    Line chart per algorithm. Only plots points where the algorithm was run.
    all_results: list of (label, size, algo_names, results_dict)
    """
    for name in _ALL_NAMES:
        xs, ys = [], []
        for _, size, algo_names, res in all_results:
            if name in algo_names:
                xs.append(size * size)
                ys.append(float(np.mean(res[name][metric])))
        if xs:
            ax.plot(xs, ys, marker="o", linewidth=2, markersize=6,
                    label=name, color=_COLOR_MAP[name])

    ax.set_xlabel("Maze size (cells)", fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    ax.set_xscale("log")
    ax.legend(fontsize=9, framealpha=0.85)


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    sys.setrecursionlimit(10_000_000)

    all_results = []  # (label, size, algo_names, results_dict)

    for label, size, algo_names in SIZES:
        print(f"\n{'='*55}")
        print(f"Benchmarking {label.replace(chr(10), ' ')} "
              f"[{', '.join(algo_names)}] — {N_RUNS} runs")
        print(f"{'='*55}")
        res = run_benchmark(size, algo_names, N_RUNS)
        all_results.append((label, size, algo_names, res))
        print("Done.")

    # ── Aggregate for grouped bar charts ──
    size_labels  = [lbl for lbl, _, _, _ in all_results]
    x_positions  = np.arange(len(size_labels))

    def build_bars(metric):
        """Returns [(name, [mean_or_None × n_sizes], [std_or_None × n_sizes])]"""
        out = []
        for name in _ALL_NAMES:
            means, stds = [], []
            for _, _, algo_names, res in all_results:
                if name in algo_names:
                    vals = res[name][metric]
                    means.append(float(np.mean(vals)))
                    stds.append(float(np.std(vals)))
                else:
                    means.append(None)
                    stds.append(None)
            out.append((name, means, stds))
        return out

    time_bars    = build_bars("times")
    visited_bars = build_bars("visited")
    path_bars    = build_bars("path")

    # ── Figure layout ──
    fig = plt.figure(figsize=(18, 14))
    fig.suptitle(
        f"Maze Pathfinding — Benchmark Results\n"
        f"({N_RUNS} runs per size · BFS excluded from Large · error bars = ±1 std)",
        fontsize=14, fontweight="bold", y=0.98,
    )

    gs = fig.add_gridspec(3, 2, hspace=0.48, wspace=0.32,
                          left=0.07, right=0.97, top=0.92, bottom=0.06)

    ax_time    = fig.add_subplot(gs[0, 0])
    ax_visited = fig.add_subplot(gs[0, 1])
    ax_path    = fig.add_subplot(gs[1, 0])
    ax_scale_t = fig.add_subplot(gs[1, 1])
    ax_box     = fig.add_subplot(gs[2, :])

    # 1. Execution time
    _bar_group(ax_time, x_positions, size_labels, time_bars,
               ylabel="Time (ms)", title="Execution Time (avg ± std)", log_scale=True)

    # 2. Visited cells
    _bar_group(ax_visited, x_positions, size_labels, visited_bars,
               ylabel="Cells visited", title="Cells Visited (avg ± std)")

    # 3. Path length
    _bar_group(ax_path, x_positions, size_labels, path_bars,
               ylabel="Path length (steps)", title="Path Length (avg ± std)")

    # 4. Time scaling line chart (BFS line ends at medium)
    _line_scaling(ax_scale_t, all_results, "times",
                  ylabel="Time (ms)", title="Time Scaling with Maze Size")

    # 5. Box plots — large maze only (algorithms that ran there)
    large_label, large_size, large_algos, large_res = all_results[-1]
    box_data   = [large_res[name]["times"] for name in large_algos]
    box_colors = [_COLOR_MAP[name] for name in large_algos]

    bp = ax_box.boxplot(box_data, patch_artist=True, notch=False,
                        medianprops={"linewidth": 2, "color": "white"},
                        whiskerprops={"linewidth": 1.2},
                        capprops={"linewidth": 1.2},
                        flierprops={"marker": "o", "markersize": 3, "alpha": 0.4})
    for patch, color in zip(bp["boxes"], box_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.85)

    ax_box.set_xticklabels(large_algos, fontsize=11)
    ax_box.set_ylabel("Time (ms)", fontsize=10)
    ax_box.set_title(
        f"Execution Time Distribution — Large maze "
        f"({large_size}×{large_size}, {N_RUNS} runs, BFS excluded)",
        fontsize=12, fontweight="bold", pad=8,
    )
    ax_box.spines[["top", "right"]].set_visible(False)
    ax_box.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax_box.set_axisbelow(True)

    # Global legend
    legend_patches = [
        mpatches.Patch(facecolor=_COLOR_MAP[name], label=name, alpha=0.88)
        for name in _ALL_NAMES
    ]
    # Mark BFS as "small/medium only"
    legend_patches[2] = mpatches.Patch(
        facecolor=_COLOR_MAP["BFS"], label="BFS (small & medium only)", alpha=0.88
    )
    fig.legend(handles=legend_patches, loc="upper right",
               bbox_to_anchor=(0.97, 0.965),
               fontsize=9, framealpha=0.9, ncol=4)

    plt.savefig("benchmark_results.png", dpi=150, bbox_inches="tight")
    print("\nPlot saved to benchmark_results.png")
    plt.show()


if __name__ == "__main__":
    main()
