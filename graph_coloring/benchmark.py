"""
Runs every coloring algorithm on every case from the benchmark suite,
measuring time and peak memory.

For each case prints a single block:
    - header with the graph parameters
    - one row per algorithm: time, peak memory, colors used, expected χ

Algorithms compared:
    - Simple Backtracking         (graph_coloring.color_graph)
    - Backtracking + MRV + FC     (graph_coloring_optimized.color_graph)
    - Greedy (Welsh-Powell)       (graph_coloring_baselines.greedy_color)
    - DFS coloring                (graph_coloring_baselines.dfs_color)

Per-run timeout: TIMEOUT_SECONDS (see below), enforced via a child process.
"""

import multiprocessing as mp
import sys
import time
import tracemalloc
from typing import Callable

import graph_coloring as bt_simple
import graph_coloring_optimized as bt_mrv
import graph_coloring_baselines as baselines
from benchmark_suite import BENCHMARK_CASES


TIMEOUT_SECONDS = 1000

ALGORITHMS:list[tuple[str, Callable]] = [
    ('Simple BT',     bt_simple.color_graph),
    ('MRV + FC',      bt_mrv.color_graph),
    ('Greedy (W-P)',  baselines.greedy_color),
    ('DFS',           baselines.dfs_color),
]


def _worker(algorithm:Callable, k:int, graph, queue:mp.Queue):
    sys.setrecursionlimit(50_000)

    tracemalloc.start()
    t0 = time.perf_counter()
    try:
        result = algorithm(k, graph)
        elapsed = time.perf_counter() - t0
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        colors_used = len(set(result.values())) if result else None
        queue.put({
            'status':      'ok',
            'time':        elapsed,
            'peak_mem_kb': peak / 1024,
            'colors':      colors_used,
        })
    except Exception as e:
        tracemalloc.stop()
        queue.put({
            'status':      'error',
            'error':       f'{type(e).__name__}: {e}',
            'time':        time.perf_counter() - t0,
            'peak_mem_kb': None,
            'colors':      None,
        })


def run_with_timeout(algorithm:Callable, k:int, graph,
                     timeout:int = TIMEOUT_SECONDS) -> dict:
    ctx = mp.get_context('spawn')
    queue:mp.Queue = ctx.Queue()
    proc = ctx.Process(target=_worker, args=(algorithm, k, graph, queue))

    proc.start()
    proc.join(timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join(5)
        if proc.is_alive():
            proc.kill()
            proc.join()
        return {'status': 'timeout', 'time': timeout,
                'peak_mem_kb': None, 'colors': None}

    if not queue.empty():
        return queue.get()

    return {'status': 'error', 'error': 'no result returned',
            'time': None, 'peak_mem_kb': None, 'colors': None}

def _fmt_time(t):
    if t is None:
        return '—'
    if t < 1e-3:
        return f'{t * 1e6:.0f} us'
    if t < 1:
        return f'{t * 1e3:.1f} ms'
    if t < 60:
        return f'{t:.2f} s'
    return f'{t / 60:.1f} min'


def _fmt_mem(kb):
    if kb is None:
        return '—'
    if kb < 1024:
        return f'{kb:.1f} KB'
    return f'{kb / 1024:.2f} MB'


def _fmt_colors(metrics):
    if metrics['status'] == 'timeout':
        return 'TIMEOUT'
    if metrics['status'] == 'error':
        return 'ERROR'
    c = metrics.get('colors')
    return str(c) if c is not None else 'no sol.'


def _fmt_chi(chi):
    return str(chi) if chi is not None else '?'


COL_ALG    = 14
COL_TIME   = 10
COL_MEM    = 10
COL_COLORS = 8
COL_CHI    = 5
TABLE_WIDTH = COL_ALG + COL_TIME + COL_MEM + COL_COLORS + COL_CHI + 4  # 4 spaces between cols



def print_case(case_name:str, n:int, m:int, k:int, chi:int|None,
               results:dict[str, dict]):
    chi_str = _fmt_chi(chi)
    header = f'  {case_name}  n={n}  m={m}  k={k}  chi={chi_str}'

    print()
    print('─' * TABLE_WIDTH)
    print(header)
    print('─' * TABLE_WIDTH)
    print(
        f"{'algorithm':<{COL_ALG}} "
        f"{'time':>{COL_TIME}} "
        f"{'memory':>{COL_MEM}} "
        f"{'colors':>{COL_COLORS}} "
        f"{'chi':>{COL_CHI}}"
    )
    print(
        f"{'-' * COL_ALG} "
        f"{'-' * COL_TIME} "
        f"{'-' * COL_MEM} "
        f"{'-' * COL_COLORS} "
        f"{'-' * COL_CHI}"
    )

    for alg_name, _ in ALGORITHMS:
        m_data = results[alg_name]
        print(
            f"{alg_name:<{COL_ALG}} "
            f"{_fmt_time(m_data.get('time')):>{COL_TIME}} "
            f"{_fmt_mem(m_data.get('peak_mem_kb')):>{COL_MEM}} "
            f"{_fmt_colors(m_data):>{COL_COLORS}} "
            f"{chi_str:>{COL_CHI}}"
        )

def run_benchmark():
    print('=' * TABLE_WIDTH)
    print(f'  Benchmark: {len(ALGORITHMS)} algorithms x {len(BENCHMARK_CASES)} cases')
    print(f'  Per-run timeout: {TIMEOUT_SECONDS} s')
    print('=' * TABLE_WIDTH)

    for name, graph, k, chi in BENCHMARK_CASES:
        n = len(list(graph.get_vertices()))
        m = sum(len(list(v.get_neighbors())) for v in graph) // 2

        results = {}
        for alg_name, alg_func in ALGORITHMS:
            results[alg_name] = run_with_timeout(alg_func, k, graph)

        print_case(name, n, m, k, chi, results)


if __name__ == '__main__':
    run_benchmark()
