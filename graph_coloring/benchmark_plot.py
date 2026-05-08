"""
graph_coloring/benchmark_plot.py
Compact comparison of 4 graph-colouring algorithms across 16 benchmark cases.
Run from project root:  python graph_coloring/benchmark_plot.py
"""
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np


BG, PANEL, GRID = '#0d1117', '#161b22', '#30363d'
A_CLR = ['#e8a838', '#4a9eff', '#c678dd', '#2ea043']
ALGS  = ['Simple BT', 'MRV + FC', 'Greedy W-P', 'DFS']
NaN   = float('nan')


CASES = [
    'K15',    'C51',    'C100',   'K20.20', 'tree30',   # structural
    'rnd20',  'rnd50',  'rnd100',                        # random
    'tight30','tight40','imposs30',                      # tight / impossible
    'spar300','spar500','dens300', 'dens500',             # large
    'Myciel',
]
N   = len(CASES)
xi  = np.arange(N)
w   = 0.19
off = np.array([-1.5, -0.5, 0.5, 1.5]) * w

CAT_SEP = [4.5, 7.5, 10.5, 14.5]
CAT_LBL = ['Structural\n(χ known)', 'Random\n(k>χ)',
            'Tight / Impossible', 'Large graphs', 'Myciel']
CAT_CTR = [2.0, 6.0, 9.0, 12.5, 15.0]

TIME = np.array([   # milliseconds
    [0.307, 0.354, 0.730, 0.339, 0.210,  0.198, 0.667,   1.9,
     1610., 16010., 306000.,   8.6,  19.6,  50.7,  258.3,  39.2],
    [0.944,   6.6,  24.5,   6.6,   2.7,    1.2,   8.3,  37.8,
       38.6,   13.2,   2030., 573.6, 1770., 1180., 4940., 6320.],
    [0.138, 0.616, 0.530, 0.282, 0.205,  0.152, 0.708, 0.764,
      0.231,  0.244,  0.166,   2.1,   2.9,   7.4,  16.2,   7.4],
    [0.155, 0.275, 0.537, 0.402, 0.184,  0.157, 0.389,   1.2,
      0.171,  0.255,  0.185,   3.6,   3.3,  10.6,  23.0,  16.4],
])

MEM = np.array([    # kilobytes
    [  1.7,   5.4,  10.5,   3.2,   3.0,   1.9,   5.4,  10.5,
       5.8,   6.2,   5.7,  22.6,  45.7,  22.6,  45.7,  95.1],
    [ 18.3,  56.6, 109.9,  42.7,  33.6,  22.2,  56.9, 266.1,
      37.0,  46.7,  35.8, 316.2, 527.6,2670.0,4450.0, 828.0],
    [  2.4,   6.5,  11.2,   4.2,   3.6,   2.2,   6.5,  11.2,
       3.3,   4.4,   3.0,  19.6,  34.7,  19.6,  36.0,  63.8],
    [  2.8,   4.5,   8.3,   5.6,   2.7,   2.4,   7.1,  19.1,
       4.0,   5.1,   4.0,  30.1,  46.7, 193.9, 580.6, 233.1],
])

NCOLS = np.array([  # colours used  (NaN = no solution)
    [15, 3, 2, 2, 2,   5,  8, 13,    7,   7, NaN,   9,  8, 47,  80, 10],
    [15, 3, 2, 2, 2,   4,  8, 12,    7,   7, NaN,   7,  5, 45,  72, 10],
    [15, 3, 2, 2, 2,   5,  8, 12,  NaN, NaN, NaN,   8,  7, 46,  78, 10],
    [15, 3, 2, 2, 2,   5,  9, 15,  NaN, NaN, NaN,   9,  7, 47, NaN, 10],
])


def _style(ax, title, ylabel, log=False):
    ax.set_facecolor(PANEL)
    ax.set_title(title, color='white', fontsize=9.5, fontweight='bold', pad=5)
    ax.set_ylabel(ylabel, color='#8b949e', fontsize=8)
    ax.set_xticks(xi)
    ax.set_xticklabels(CASES, rotation=45, ha='right', fontsize=6.5)
    ax.tick_params(colors='white', labelsize=7)
    for sp in ax.spines.values():
        sp.set_color(GRID)
    ax.grid(axis='y', color=GRID, ls='--', alpha=0.5, zorder=0)
    if log:
        ax.set_yscale('log')
        ax.yaxis.set_minor_formatter(mticker.NullFormatter())


def _cats(ax):
    for b in CAT_SEP:
        ax.axvline(b, color=GRID, lw=1, ls=':', alpha=0.8, zorder=1)


fig = plt.figure(figsize=(22, 13), facecolor=BG)
fig.suptitle('Graph Coloring — Algorithm Benchmark', color='white',
             fontsize=14, fontweight='bold', y=0.99)

gs = gridspec.GridSpec(2, 3, height_ratios=[1, 0.85],
                       hspace=0.55, wspace=0.28,
                       left=0.05, right=0.98, top=0.95, bottom=0.06)

ax_t  = fig.add_subplot(gs[0, 0])
ax_m  = fig.add_subplot(gs[0, 1])
ax_sp = fig.add_subplot(gs[0, 2])
ax_h  = fig.add_subplot(gs[1, 0:2])
ax_sc = fig.add_subplot(gs[1, 2])

leg_p = [mpatches.Patch(color=c, label=a) for c, a in zip(A_CLR, ALGS)]

# ── 1. Execution time ─────────────────────────────────────────────────────────
for i in range(4):
    ax_t.bar(xi + off[i], TIME[i], w, color=A_CLR[i], alpha=0.88, zorder=3)
_cats(ax_t)
_style(ax_t, 'Execution Time  (ms, log)', 'ms', log=True)
ax_t.legend(handles=leg_p, fontsize=7, facecolor=PANEL, edgecolor=GRID,
            labelcolor='white', loc='upper left', ncol=2)

# ── 2. Peak memory ────────────────────────────────────────────────────────────
for i in range(4):
    ax_m.bar(xi + off[i], MEM[i], w, color=A_CLR[i], alpha=0.88, zorder=3)
_cats(ax_m)
_style(ax_m, 'Peak Memory  (KB, log)', 'KB', log=True)

# ── 3. Speedup  BT / MRV+FC ──────────────────────────────────────────────────
spd  = TIME[0] / TIME[1]
bclr = ['#2ea043' if s >= 1 else '#e8a838' for s in spd]
bars = ax_sp.bar(xi, spd, 0.55, color=bclr, alpha=0.88, zorder=3)
ax_sp.axhline(1, color='white', lw=1.2, ls='--', alpha=0.6, zorder=4)
ax_sp.set_yscale('log')
ax_sp.yaxis.set_minor_formatter(mticker.NullFormatter())
ax_sp.set_ylim(5e-4, 5e5)
_cats(ax_sp)
_style(ax_sp, 'Speedup  BT ÷ MRV+FC  (log)\n(green ≥ 1  →  MRV+FC faster)', 'ratio')

for bar, s in zip(bars, spd):
    cx = bar.get_x() + bar.get_width() / 2
    if s > 40:
        ax_sp.text(cx, s * 2.5, f'{s:.0f}×',
                   ha='center', va='bottom', fontsize=6,
                   color='white', fontweight='bold', zorder=5)
    elif s < 0.015:
        ax_sp.text(cx, 1.8, f'1/{1/s:.0f}×',
                   ha='center', va='bottom', fontsize=5.5,
                   color='white', fontweight='bold', zorder=5)

# ── 4. Quality heatmap ────────────────────────────────────────────────────────
quality = np.full((4, N), 0.5)
for j in range(N):
    valid = [NCOLS[i, j] for i in range(4) if not np.isnan(NCOLS[i, j])]
    if not valid:
        continue
    mn, mx = min(valid), max(valid)
    for i in range(4):
        v = NCOLS[i, j]
        if   np.isnan(v): quality[i, j] = -1
        elif mx == mn:    quality[i, j] =  0.75
        else:             quality[i, j] =  1.0 - (v - mn) / (mx - mn)

ax_h.set_facecolor(PANEL)
ax_h.set_xlim(-0.5, N - 0.5)
ax_h.set_ylim(-0.5, 3.5)
cmap = plt.cm.RdYlGn

for i in range(4):
    for j in range(N):
        q  = quality[i, j]
        fc = '#c0392b' if q == -1 else cmap(q * 0.9 + 0.05)
        ax_h.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                     fc=fc, ec=GRID, lw=0.6, zorder=2))
        v_raw = NCOLS[i, j]
        txt = '✗' if q == -1 else (str(int(v_raw)) if not np.isnan(v_raw) else '?')
        tc  = 'white' if (q == -1 or q < 0.55) else '#1a1a2e'
        ax_h.text(j, i, txt, ha='center', va='center',
                  fontsize=7.5, color=tc, fontweight='bold', zorder=3)

ax_h.set_xticks(range(N))
ax_h.set_xticklabels(CASES, rotation=45, ha='right', fontsize=6.5)
ax_h.set_yticks(range(4))
ax_h.set_yticklabels(ALGS, fontsize=8.5, color='white')
ax_h.tick_params(colors='white', labelsize=7, length=0)
ax_h.set_title(
    'Solution Quality — colours used per case  '
    '(green = fewer colours = better  ·  ✗ = no solution)',
    color='white', fontsize=9.5, fontweight='bold', pad=5)
for sp in ax_h.spines.values():
    sp.set_color(GRID)
for b in CAT_SEP:
    ax_h.axvline(b, color='white', lw=1.5, alpha=0.4, zorder=4)

ax_ht = ax_h.twiny()
ax_ht.set_xlim(ax_h.get_xlim())
ax_ht.set_xticks(CAT_CTR)
ax_ht.set_xticklabels(CAT_LBL, fontsize=7, color='#8b949e')
ax_ht.tick_params(length=0, colors='white')
for sp in ax_ht.spines.values():
    sp.set_visible(False)

# ── 5. Time vs quality scatter ────────────────────────────────────────────────
ax_sc.set_facecolor(PANEL)
IDX = [5, 6, 7, 11, 12, 13, 14, 15]   # random + large + myciel

for i, (alg, c) in enumerate(zip(ALGS, A_CLR)):
    tx, cy, sz = [], [], []
    for j in IDX:
        if not np.isnan(NCOLS[i, j]):
            tx.append(TIME[i, j])
            cy.append(NCOLS[i, j])
            sz.append(MEM[i, j])
    if tx:
        ax_sc.scatter(tx, cy, s=[m * 0.3 + 15 for m in sz],
                      color=c, alpha=0.80, label=alg,
                      edgecolors='white', linewidths=0.4, zorder=3)

ax_sc.set_xscale('log')
ax_sc.set_xlabel('Time (ms, log)', color='#8b949e', fontsize=8)
ax_sc.set_ylabel('Colors used', color='#8b949e', fontsize=8)
ax_sc.set_title('Time vs Quality\n(bubble size ∝ memory  ·  ↙ = best)',
                color='white', fontsize=9.5, fontweight='bold', pad=5)
ax_sc.tick_params(colors='white', labelsize=7)
for sp in ax_sc.spines.values():
    sp.set_color(GRID)
ax_sc.grid(color=GRID, ls='--', alpha=0.4, zorder=0)
ax_sc.legend(fontsize=7, facecolor=PANEL, edgecolor=GRID,
             labelcolor='white', loc='upper left')

# ── Save ──────────────────────────────────────────────────────────────────────
out = 'benchmark_plot.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG, edgecolor='none')
print(f'Saved -> {out}')
plt.show()
