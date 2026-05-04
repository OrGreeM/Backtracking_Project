"""
Benchmark module that runs every coloring algorithm on every
case from the benchmark suite, measuring time and peak memory.

Algorithms compared:
    - Simple Backtracking         (graph_coloring.color_graph)
    - Backtracking + MRV + FC     (graph_coloring_optimized.color_graph)
    - Greedy (Welsh-Powell)       (graph_coloring_baselines.greedy_color)
    - DFS coloring                (graph_coloring_baselines.dfs_color)

Metrics:
    - time     — wall-clock execution time (seconds)
    - peak_mem — peak Python memory allocated during the run, via tracemalloc (KiB)
    - colors   — number of distinct colors actually used (None on failure / timeout)

Per-run timeout: 300 seconds. Hard timeouts are enforced via a
worker process; if the algorithm cannot finish in time it is killed
and the run is recorded as 'TIMEOUT'.
"""

import multiprocessing as mp
import sys
import time
import tracemalloc
from typing import Callable

import graph_coloring_optimized
import graph_coloring_baselines
from benchmark_suite import BENCHMARK_CASES
import graph_coloring

TIMEOUT_SECONDS = 300

ALGORITHMS:list[tuple[str, Callable]] = [
    ('Simple Backtracking', graph_coloring.color_graph),
    ('MRV + FC', graph_coloring_optimized.color_graph),
    ('Greedy', graph_coloring_baselines.greedy_color),
    ('DFS', graph_coloring_baselines.dfs_color),
]

def _worker(algorithm:Callable, k:int, graph, queue:mp.Queue):
    """
    Runs `algorithm(k, graph)` inside a child process, measuring
    wall time and peak Python memory. Pushes a result dict onto `queue`.
    """
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
            'solved':      result is not None,
        })
    except Exception as e:
        tracemalloc.stop()
        queue.put({
            'status': 'error',
            'error':  f'{type(e).__name__}: {e}',
            'time':   time.perf_counter() - t0,
        })


def run_with_timeout(algorithm:Callable, k:int, graph,
                     timeout:int = TIMEOUT_SECONDS) -> dict:
    """
    Run an algorithm in a subprocess with a hard timeout.
    Returns a metrics dict with 'status' in {'ok','timeout','error'}.
    """
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
        return {'status': 'timeout', 'time': timeout, 'peak_mem_kb': None, 'colors': None}

    if not queue.empty():
        return queue.get()

    return {'status': 'error', 'error': 'no result returned', 'time': None}

def _fmt_time(t):
    if t is None:
        return '—'
    if t < 0.001:
        return f'{t*1e6:.0f}µs'
    if t < 1:
        return f'{t*1e3:.1f}ms'
    return f'{t:.2f}s'


def _fmt_mem(kb):
    if kb is None:
        return '—'
    if kb < 1024:
        return f'{kb:.1f}KB'
    return f'{kb/1024:.2f}MB'


def _fmt_status(metrics:dict, expected_chi:int|None) -> str:
    """Produce a short status string for a single run."""
    if metrics['status'] == 'timeout':
        return 'TIMEOUT'
    if metrics['status'] == 'error':
        return f"ERROR ({metrics.get('error', '?')[:30]})"

    colors = metrics.get('colors')
    if colors is None:
        return 'no solution'

    marker = ''
    if expected_chi is not None:
        if colors == expected_chi:
            marker = ' ✓'
        elif colors > expected_chi:
            marker = f' (+{colors - expected_chi})'
        else:
            marker = ' (!?)'
    return f'{colors} colors{marker}'


def print_case_header(name:str, n:int, m:int, k:int, chi:int|None):
    chi_str = f'χ={chi}' if chi is not None else 'χ=?'
    print()
    print(f'─── {name}  (n={n}, m={m}, k={k}, {chi_str}) ' + '─' * max(0, 25 - len(name)))


def print_case_results(results:dict, expected_chi:int|None):
    """Print one row per algorithm for a single case."""
    print(f"  {'algorithm':<14} {'time':>10} {'peak mem':>11}  {'result':<20}")
    print(f"  {'─' * 14} {'─' * 10} {'─' * 11}  {'─' * 20}")
    for alg_name, metrics in results.items():
        t   = _fmt_time(metrics.get('time'))
        mem = _fmt_mem(metrics.get('peak_mem_kb'))
        st  = _fmt_status(metrics, expected_chi)
        print(f"  {alg_name:<14} {t:>10} {mem:>11}  {st:<20}")


def print_summary(all_results:dict):
    """Print a final summary table across all cases."""
    print()
    print('═' * 75)
    print('  SUMMARY (time / colors-used)')
    print('═' * 75)

    alg_names = [name for name, _ in ALGORITHMS]
    header = f"{'case':<25}" + ''.join(f"{n[:13]:>14}" for n in alg_names)
    print(header)
    print('─' * len(header))

    for case_name, (case_results, chi) in all_results.items():
        row = f'{case_name:<25}'
        for alg_name in alg_names:
            m = case_results[alg_name]
            if m['status'] == 'timeout':
                cell = 'TIMEOUT'
            elif m['status'] == 'error':
                cell = 'ERROR'
            elif m.get('colors') is None:
                cell = 'fail'
            else:
                cell = f"{_fmt_time(m['time'])}/{m['colors']}c"
            row += f"{cell:>14}"
        print(row)

    print('═' * 75)


def run_benchmark():
    print(f'Running benchmark: {len(ALGORITHMS)} algorithms × {len(BENCHMARK_CASES)} cases')
    print(f'Per-run timeout: {TIMEOUT_SECONDS}s')

    all_results = {}

    for name, graph, k, chi in BENCHMARK_CASES:
        n = len(list(graph.get_vertices()))
        m = sum(len(list(v.get_neighbors())) for v in graph) // 2

        print_case_header(name, n, m, k, chi)

        case_results = {}
        for alg_name, alg_func in ALGORITHMS:
            print(f'  running {alg_name}...', end=' ', flush=True)
            metrics = run_with_timeout(alg_func, k, graph)
            case_results[alg_name] = metrics
            if metrics['status'] == 'ok':
                print(f"done in {_fmt_time(metrics['time'])}")
            else:
                print(metrics['status'])

        print_case_results(case_results, chi)
        all_results[name] = (case_results, chi)

    print_summary(all_results)


if __name__ == '__main__':
    run_benchmark()
