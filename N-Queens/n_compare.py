"""
N-Queens: порівняння 4 алгоритмів
1. Базовий бектрекінг
2. Forward Checking (FC)
3. MRV (Minimum Remaining Values)
4. MRV + FC (Constraint Propagation)
"""
import sys, time
import argparse
sys.setrecursionlimit(100_000)
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button, Slider

parser = argparse.ArgumentParser(description="N-Queens Backtracking Comparison")
parser.add_argument("-n", "--size", type=int, default=6, help="Розмір дошки N x N")
parser.add_argument("--no-vis", action="store_true", help="Не показувати візуалізацію")
parser.add_argument("--algs", nargs="+", choices=["basic", "fc", "mrv", "mrv_fc"],
                    default=["basic", "fc", "mrv", "mrv_fc"], help="Алгоритми для запуску")
args = parser.parse_args()

N = args.size

BG        = '#0d1117'
SQ_LIGHT  = '#f0d9b5'
SQ_DARK   = '#b58863'
SQ_QUEEN  = '#c9d46e'
Q_TEXT    = '#1a1a2e'
SOL_CLR   = '#2ea043'
ALGO_CLR  = ['#e8a838', '#4a9eff', '#c678dd', '#2ea043']
ALGO_NAMES = ['Базовий бектрекінг', 'Forward Checking', 'MRV', 'MRV + FC']
ALGO_SHORT = ['Базовий\nбектрекінг', 'Forward\nChecking', 'MRV', 'MRV + FC']

def solve_basic(n):
    steps, board = [], [-1] * n
    s = {'nodes': 0, 'backs': 0, 'solutions': 0}

    def safe(row, col):
        for r in range(row):
            if board[r] == col or abs(board[r] - col) == row - r:
                return False
        return True

    def bt(row):
        if row == n:
            s['solutions'] += 1
            steps.append(('sol', board[:]))
            return
        for col in range(n):
            s['nodes'] += 1
            if safe(row, col):
                board[row] = col
                steps.append(('put', board[:]))
                bt(row + 1)
                board[row] = -1
                s['backs'] += 1
                steps.append(('rm', board[:]))

    t0 = time.perf_counter(); bt(0)
    s['ms'] = (time.perf_counter() - t0) * 1000
    return steps, s

def solve_fc(n):
    steps, board = [], [-1] * n
    s = {'nodes': 0, 'backs': 0, 'solutions': 0}
    avail = [set(range(n)) for _ in range(n)]

    def propagate(row, col):
        pruned, ok = {}, True
        for r in range(row + 1, n):
            d  = r - row
            rm = {c for c in (col, col - d, col + d) if 0 <= c < n and c in avail[r]}
            if rm:
                avail[r] -= rm
                pruned[r] = rm
                if not avail[r]:
                    ok = False
                    break
        return pruned, ok

    def restore(pruned):
        for r, cs in pruned.items():
            avail[r] |= cs

    def bt(row):
        if row == n:
            s['solutions'] += 1
            steps.append(('sol', board[:]))
            return
        for col in sorted(avail[row]):
            s['nodes'] += 1
            board[row] = col
            steps.append(('put', board[:]))
            pruned, ok = propagate(row, col)
            if ok:
                bt(row + 1)
            restore(pruned)
            board[row] = -1
            s['backs'] += 1
            steps.append(('rm', board[:]))

    t0 = time.perf_counter(); bt(0)
    s['ms'] = (time.perf_counter() - t0) * 1000
    return steps, s

def solve_mrv(n):
    steps, board = [], [-1] * n
    s = {'nodes': 0, 'backs': 0, 'solutions': 0}

    def domain(row):
        result = set()
        for col in range(n):
            ok = all(
                board[r] != col and abs(board[r] - col) != abs(r - row)
                for r in range(n) if board[r] != -1
            )
            if ok:
                result.add(col)
        return result

    def bt(unassigned):
        if not unassigned:
            s['solutions'] += 1
            steps.append(('sol', board[:]))
            return
        doms = {r: domain(r) for r in unassigned}
        row  = min(unassigned, key=lambda r: len(doms[r]))
        dom  = doms[row]
        rest = unassigned - {row}
        for col in sorted(dom):
            s['nodes'] += 1
            board[row] = col
            steps.append(('put', board[:]))
            bt(rest)
            board[row] = -1
            s['backs'] += 1
            steps.append(('rm', board[:]))

    t0 = time.perf_counter(); bt(set(range(n)))
    s['ms'] = (time.perf_counter() - t0) * 1000
    return steps, s

def solve_mrv_fc(n):
    steps, board = [], [-1] * n
    s = {'nodes': 0, 'backs': 0, 'solutions': 0}
    domains = [set(range(n)) for _ in range(n)]

    def propagate(row, col, unassigned):
        pruned, ok = {}, True
        for r in unassigned:
            d  = abs(r - row)
            rm = {c for c in (col, col - d, col + d) if 0 <= c < n and c in domains[r]}
            if rm:
                domains[r] -= rm
                pruned[r] = rm
                if not domains[r]:
                    ok = False
                    break
        return pruned, ok

    def restore(pruned):
        for r, cs in pruned.items():
            domains[r] |= cs

    def bt(unassigned):
        if not unassigned:
            s['solutions'] += 1
            steps.append(('sol', board[:]))
            return
        row  = min(unassigned, key=lambda r: len(domains[r]))
        rest = unassigned - {row}
        for col in sorted(domains[row]):
            s['nodes'] += 1
            board[row] = col
            steps.append(('put', board[:]))
            pruned, ok = propagate(row, col, rest)
            if ok:
                bt(rest)
            restore(pruned)
            board[row] = -1
            s['backs'] += 1
            steps.append(('rm', board[:]))

    t0 = time.perf_counter(); bt(set(range(n)))
    s['ms'] = (time.perf_counter() - t0) * 1000
    return steps, s

if N > 9:
    print(f"Увага: N={N} може бути повільним для базового алгоритму та MRV")

print(f"N={N}: обчислення...")

algo_mapping = {'basic': solve_basic, 'fc': solve_fc, 'mrv': solve_mrv, 'mrv_fc': solve_mrv_fc}
idx_mapping = {'basic': 0, 'fc': 1, 'mrv': 2, 'mrv_fc': 3}
solvers = [algo_mapping[k] for k in args.algs]
active_clr = [ALGO_CLR[idx_mapping[k]] for k in args.algs]
active_short = [ALGO_SHORT[idx_mapping[k]] for k in args.algs]

all_steps, all_stats = [], []
for fn in solvers:
    st, ss = fn(N)
    all_steps.append(st)
    all_stats.append(ss)
    tag = fn.__name__[6:]
    print(f"  {tag:10s}  кроків={len(st):6d}  вузлів={ss['nodes']:6d}  "
          f"відкатів={ss['backs']:6d}  рішень={ss['solutions']}  {ss['ms']:.2f}мс")

if args.no_vis:
    sys.exit(0)

max_frames = max(len(s) for s in all_steps)

fig_cmp, axs = plt.subplots(1, 3, figsize=(14, 5), facecolor=BG)
fig_cmp.suptitle(f'Порівняння алгоритмів  ·  N-Queens  N={N}',
                 color='white', fontsize=14, fontweight='bold')

metrics = [
    ('nodes', 'Вузлів досліджено'),
    ('backs', 'Кількість відкатів'),
    ('ms',    'Час виконання (мс)'),
]
short_names = active_short

for ax, (key, title) in zip(axs, metrics):
    ax.set_facecolor('#161b22')
    vals = [ss[key] for ss in all_stats]
    bars = ax.bar(range(len(solvers)), vals, color=active_clr, edgecolor='none', width=0.55, zorder=3)
    ax.set_xticks(range(len(solvers)))
    ax.set_xticklabels(short_names, color='white', fontsize=10)
    ax.set_title(title, color='white', fontsize=12, fontweight='bold', pad=8)
    ax.tick_params(axis='y', colors='white')
    ax.tick_params(axis='x', length=0)
    for sp in ax.spines.values():
        sp.set_color('#30363d')
    ax.set_facecolor('#161b22')
    ax.grid(axis='y', color='#30363d', linestyle='--', alpha=0.4, zorder=0)
    maxv = max(vals) if max(vals) > 0 else 1
    for bar, val in zip(bars, vals):
        label = f'{val:.2f}' if key == 'ms' else str(val)
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + maxv * 0.015,
                label, ha='center', va='bottom',
                color='white', fontsize=9, fontweight='bold', zorder=5)

fig_cmp.tight_layout(rect=[0, 0, 1, 0.94])

fig_anim = plt.figure(figsize=(22, 7), facecolor=BG)

n_plots_anim = len(solvers)
gs = fig_anim.add_gridspec(
    1, n_plots_anim, left=0.01, right=0.99, bottom=0.13, top=0.90, wspace=0.05
)
anim_axes = [fig_anim.add_subplot(gs[0, i]) for i in range(n_plots_anim)]
for ax in anim_axes:
    ax.set_facecolor(BG)
    ax.axis('off')


def draw_board(ax, board, title, color, is_sol=False, done=False):
    """board[row] = col  (-1 = пусто)"""
    ax.cla()
    ax.set_facecolor(BG)
    ax.axis('off')
    ax.set_xlim(-0.25, N + 0.25)
    ax.set_ylim(-0.55, N + 0.25)
    ax.set_aspect('equal')
    ax.set_title(title, color=color, fontsize=9, fontweight='bold', pad=4,
                 linespacing=1.5)

    for r in range(N):
        for c in range(N):
            has_q = (board[r] == c)
            fc = SQ_QUEEN if has_q else (SQ_LIGHT if (r + c) % 2 == 0 else SQ_DARK)
            ax.add_patch(patches.Rectangle((c, N - 1 - r), 1, 1, lw=0, fc=fc))
            if has_q:
                ax.text(c + .5, N - .5 - r, '♛',
                        ha='center', va='center',
                        fontsize=max(9, 26 - 3 * N),
                        color=Q_TEXT, fontweight='bold', zorder=3)

    bc = SOL_CLR if is_sol else ('#30363d' if done else '#4a5568')
    bw = 3.0 if is_sol else 1.5
    ax.add_patch(patches.Rectangle((0, 0), N, N, lw=bw, ec=bc, fc='none', zorder=4))

    # Кольорова смужка знизу — ідентифікує алгоритм
    ax.add_patch(patches.Rectangle((0, -0.42), N, 0.2, lw=0, fc=color, zorder=5, alpha=0.85))

    if done:
        ax.text(N / 2, N / 2, '✓', ha='center', va='center',
                fontsize=48, color='#2ea043', alpha=0.18,
                fontweight='bold', zorder=6)


frame   = [0]
running = [True]


def render(f):
    for steps, ax, color, short in zip(all_steps, anim_axes, active_clr, active_short):
        fi     = min(f, len(steps) - 1)
        ev, bd = steps[fi]
        is_sol = (ev == 'sol')
        done   = (f >= len(steps))
        nsol   = sum(1 for e, _ in steps[:fi + 1] if e == 'sol')
        pct    = fi * 100 // max(len(steps) - 1, 1)
        status = '✓ DONE' if done else f'{pct}%'
        title  = f'{short}\nкрок {fi+1}/{len(steps)}  рішень: {nsol}  [{status}]'
        draw_board(ax, bd, title, color, is_sol, done)

    fig_anim.suptitle(
        f'N-Queens  N={N}   ·   крок {f + 1} / {max_frames}',
        color='white', fontsize=12, fontweight='bold', y=0.978
    )
    fig_anim.canvas.draw_idle()

ax_pp   = fig_anim.add_axes([0.38, 0.025, 0.08, 0.05])
ax_prev = fig_anim.add_axes([0.28, 0.025, 0.08, 0.05])
ax_next = fig_anim.add_axes([0.47, 0.025, 0.08, 0.05])
ax_spd  = fig_anim.add_axes([0.10, 0.035, 0.14, 0.03])

for a in (ax_pp, ax_prev, ax_next, ax_spd):
    a.set_facecolor('#161b22')

btn_pp   = Button(ax_pp,   'Пауза',    color='#161b22', hovercolor='#21262d')
btn_prev = Button(ax_prev, '◀ Назад',  color='#161b22', hovercolor='#21262d')
btn_next = Button(ax_next, 'Вперед ▶', color='#161b22', hovercolor='#21262d')
sld_spd  = Slider(ax_spd, 'fps', 1.0, 30.0, valinit=8.0, color='#ffd700')

for btn in (btn_pp, btn_prev, btn_next):
    btn.label.set_color('white')
    btn.label.set_fontsize(9)
sld_spd.label.set_color('white')
sld_spd.valtext.set_color('white')


def on_pp(e):
    running[0] = not running[0]
    btn_pp.label.set_text('Далі' if not running[0] else 'Пауза')
    fig_anim.canvas.draw_idle()


def on_prev(e):
    running[0] = False
    btn_pp.label.set_text('Далі')
    frame[0] = max(0, frame[0] - 1)
    render(frame[0])


def on_next(e):
    running[0] = False
    btn_pp.label.set_text('Далі')
    frame[0] = min(max_frames - 1, frame[0] + 1)
    render(frame[0])


def on_spd(v):
    timer.stop()
    timer.interval = int(1000.0 / max(1.0, v))
    if running[0]:
        timer.start()


btn_pp.on_clicked(on_pp)
btn_prev.on_clicked(on_prev)
btn_next.on_clicked(on_next)
sld_spd.on_changed(on_spd)


def tick():
    if running[0]:
        frame[0] = (frame[0] + 1) % max_frames
        render(frame[0])


timer = fig_anim.canvas.new_timer(interval=125)
timer.add_callback(tick)
timer.start()

render(0)
plt.show()
