"""
Візуалізація N-Queens backtracking.
Ліворуч — шахова дошка, праворуч — дерево відкату.
Використання: python n_queens_viz.py [N]   (стандартно N=5)
"""

import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button, Slider

N = int(sys.argv[1]) if len(sys.argv) > 1 else 5

class Node:
    _nid = 0

    @classmethod
    def reset(cls):
        cls._nid = 0

    def __init__(self, row, col, parent=None):
        self.nid = Node._nid
        Node._nid += 1
        self.row = row
        self.col = col
        self.parent = parent
        self.children = []
        self.x = 0.0
        self.y = 0.5 if row < 0 else -float(row)
        if parent is not None:
            parent.children.append(self)



def safe(board, row, col):
    n = len(board)
    for i in range(row):
        if board[i][col]:
            return False
    r, c = row - 1, col - 1
    while r >= 0 and c >= 0:
        if board[r][c]:
            return False
        r -= 1; c -= 1
    r, c = row - 1, col + 1
    while r >= 0 and c < n:
        if board[r][c]:
            return False
        r -= 1; c += 1
    return True


steps = []


def solve(board, row, parent):
    if row == N:
        steps.append(('solution', [r[:] for r in board], parent))
        return
    for col in range(N):
        if safe(board, row, col):
            board[row][col] = 1
            nd = Node(row, col, parent)
            steps.append(('place', [r[:] for r in board], nd))
            solve(board, row + 1, nd)
            board[row][col] = 0
            steps.append(('backtrack', [r[:] for r in board], nd))


Node.reset()
ROOT = Node(-1, -1)
solve([[0] * N for _ in range(N)], 0, ROOT)

n_sol_total = sum(1 for e, _, _ in steps if e == 'solution')
print(f"N={N}: {n_sol_total} рішень, {len(steps)} кроків")

sol_path_ids = set()
for ev, _, nd in steps:
    if ev == 'solution':
        cur = nd
        while cur and cur.row >= 0:
            sol_path_ids.add(cur.nid)
            cur = cur.parent

_leaf = [0]


def assign_x(node):
    if not node.children:
        node.x = float(_leaf[0])
        _leaf[0] += 1
    else:
        for ch in node.children:
            assign_x(ch)
        node.x = (node.children[0].x + node.children[-1].x) / 2.0


assign_x(ROOT)
_denom = max(_leaf[0] - 1, 1)


def norm_x(node):
    node.x /= _denom
    for ch in node.children:
        norm_x(ch)


norm_x(ROOT)

all_nodes = {}
stack = [ROOT]
while stack:
    nd = stack.pop()
    all_nodes[nd.nid] = nd
    stack.extend(nd.children)

def path_ids(node):
    ids = []
    cur = node
    while cur and cur.row >= 0:
        ids.append(cur.nid)
        cur = cur.parent
    return frozenset(ids)


visible_snaps = []
active_snaps = []
nsol_snaps = []
vis = set()
nsol = 0

for ev, brd, nd in steps:
    if ev == 'place':
        vis.add(nd.nid)
    if ev == 'solution':
        nsol += 1
    visible_snaps.append(frozenset(vis))
    nsol_snaps.append(nsol)
    if ev in ('place', 'solution'):
        active_snaps.append(path_ids(nd))
    else:
        active_snaps.append(path_ids(nd.parent) if nd.parent else frozenset())


BG     = '#0d1117'
SQ_LT  = '#f0d9b5'
SQ_DK  = '#b58863'
SQ_HL  = '#c9d46e'
Q_CLR  = '#1a1a2e'
C_ROOT = '#586069'
C_CUR  = '#ffd700'
C_PATH = '#e8a838'
C_SOL  = '#2ea043'
C_DEAD = '#da3633'
C_EDGE = '#30363d'

fig = plt.figure(figsize=(16, 9), facecolor=BG)
gs = fig.add_gridspec(
    1, 2, width_ratios=[1, 2.4],
    left=0.03, right=0.97, bottom=0.11, top=0.91, wspace=0.05
)
ax_b = fig.add_subplot(gs[0])
ax_t = fig.add_subplot(gs[1])
for ax in (ax_b, ax_t):
    ax.set_facecolor(BG)
    ax.axis('off')

def draw_board(brd, is_solution=False):
    ax_b.cla()
    ax_b.set_facecolor(BG)
    ax_b.axis('off')
    ax_b.set_xlim(-0.65, N + 0.15)
    ax_b.set_ylim(-0.65, N + 0.15)
    ax_b.set_aspect('equal')
    ax_b.set_title('Шахова дошка', color='white', fontsize=13,
                   fontweight='bold', pad=8)

    for r in range(N):
        for c in range(N):
            has_q = bool(brd[r][c])
            fc = SQ_HL if has_q else (SQ_LT if (r + c) % 2 == 0 else SQ_DK)
            ax_b.add_patch(patches.Rectangle((c, N - 1 - r), 1, 1, lw=0, fc=fc))
            if has_q:
                ax_b.text(c + .5, N - .5 - r, '♛',
                          ha='center', va='center',
                          fontsize=max(12, 32 - 3 * N),
                          color=Q_CLR, fontweight='bold', zorder=3)

    border_clr = C_SOL if is_solution else '#4a5568'
    border_lw = 4 if is_solution else 2.5
    ax_b.add_patch(patches.Rectangle(
        (0, 0), N, N, lw=border_lw, ec=border_clr, fc='none', zorder=4))

    fs = 9 if N <= 8 else 7
    for i in range(N):
        ax_b.text(-.3, N - .5 - i, str(i), ha='center', va='center',
                  fontsize=fs, color='#718096')
        ax_b.text(i + .5, -.3, str(i), ha='center', va='center',
                  fontsize=fs, color='#718096')

def draw_tree(vis, act, cur_id):
    ax_t.cla()
    ax_t.set_facecolor(BG)
    ax_t.axis('off')
    ax_t.set_xlim(-0.02, 1.02)
    ax_t.set_ylim(-N - 0.9, 0.85)
    ax_t.set_title('Дерево відкату  (backtracking tree)', color='white',
                   fontsize=13, fontweight='bold', pad=8)


    for nid in vis:
        nd = all_nodes[nid]
        if nd.parent:
            on = nid in act
            ax_t.plot([nd.parent.x, nd.x], [nd.parent.y, nd.y],
                      color=(C_PATH if on else C_EDGE),
                      lw=(1.6 if on else 0.5),
                      alpha=(1.0 if on else 0.4), zorder=1)


    ax_t.plot(ROOT.x, ROOT.y, 's', color=C_ROOT, ms=9, zorder=3, mew=0)
    ax_t.text(ROOT.x, ROOT.y + 0.1, 'start',
              ha='center', va='bottom', fontsize=7, color='#586069')


    for nid in vis:
        nd = all_nodes[nid]
        if nid == cur_id:
            clr, ms, al = C_CUR,  10, 1.0
        elif nid in act:
            clr, ms, al = C_PATH,  7, 1.0
        elif nid in sol_path_ids:
            clr, ms, al = C_SOL,   6, 0.9
        else:
            clr, ms, al = C_DEAD,  5, 0.55

        ax_t.plot(nd.x, nd.y, 'o', color=clr, ms=ms, alpha=al,
                  zorder=3, mew=0)
        if N <= 6:
            ax_t.text(nd.x, nd.y, str(nd.col),
                      ha='center', va='center',
                      fontsize=5 if N <= 5 else 4,
                      color='white', fontweight='bold', zorder=5)

    for r in range(N):
        ax_t.text(-0.015, -float(r), f'р{r}',
                  ha='right', va='center', fontsize=7, color='#4a5568')

    legend = [(C_CUR, 'поточний'), (C_PATH, 'шлях'),
              (C_SOL, 'рішення'), (C_DEAD, 'тупик')]
    for i, (c, lbl) in enumerate(legend):
        ax_t.plot(0.05 + i * 0.24, -N - 0.55, 'o', color=c, ms=7, zorder=5)
        ax_t.text(0.09 + i * 0.24, -N - 0.55, lbl,
                  va='center', fontsize=7, color='white')

frame = [0]
running = [True]

def render(f):
    ev, brd, nd = steps[f]
    vis = visible_snaps[f]
    act = active_snaps[f]
    nsol_now = nsol_snaps[f]

    if ev in ('place', 'solution'):
        cur_id = nd.nid
    elif nd.parent and nd.parent.row >= 0:
        cur_id = nd.parent.nid
    else:
        cur_id = -1

    draw_board(brd, is_solution=(ev == 'solution'))
    draw_tree(vis, act, cur_id)

    msg = {
        'place':     f'Ставимо ферзя → рядок {nd.row}, стовпець {nd.col}',
        'backtrack': f'Відкат ← рядок {nd.row}, стовпець {nd.col}',
        'solution':  f'★ Знайдено рішення #{nsol_now}!',
    }[ev]
    clr = '#ffd700' if ev == 'solution' else ('white' if ev == 'place' else C_PATH)
    fig.suptitle(
        f'N-Queens  N={N}   ·   {msg}'
        f'   ·   крок {f + 1}/{len(steps)}'
        f'   ·   рішень: {nsol_now}/{n_sol_total}',
        color=clr, fontsize=10.5, fontweight='bold', y=0.97
    )
    fig.canvas.draw_idle()


render(0)

def tick():
    if running[0]:
        frame[0] = (frame[0] + 1) % len(steps)
        render(frame[0])


timer = fig.canvas.new_timer(interval=125)
timer.add_callback(tick)
timer.start()

ax_pp   = plt.axes([0.36, 0.025, 0.10, 0.05])
ax_prev = plt.axes([0.25, 0.025, 0.10, 0.05])
ax_next = plt.axes([0.47, 0.025, 0.10, 0.05])
ax_spd  = plt.axes([0.08, 0.035, 0.14, 0.03])

for a in (ax_pp, ax_prev, ax_next, ax_spd):
    a.set_facecolor('#161b22')

btn_pp   = Button(ax_pp,   'Пауза',   color='#161b22', hovercolor='#21262d')
btn_prev = Button(ax_prev, '< Назад', color='#161b22', hovercolor='#21262d')
btn_next = Button(ax_next, 'Вперед >', color='#161b22', hovercolor='#21262d')
sld_spd  = Slider(ax_spd, 'fps', 1.0, 40.0, valinit=8.0, color=C_CUR)

for btn in (btn_pp, btn_prev, btn_next):
    btn.label.set_color('white')
    btn.label.set_fontsize(9)
sld_spd.label.set_color('white')
sld_spd.valtext.set_color('white')


def on_pp(e):
    running[0] = not running[0]
    btn_pp.label.set_text('Далі' if not running[0] else 'Пауза')
    fig.canvas.draw_idle()


def on_prev(e):
    running[0] = False
    btn_pp.label.set_text('Далі')
    frame[0] = max(0, frame[0] - 1)
    render(frame[0])


def on_next(e):
    running[0] = False
    btn_pp.label.set_text('Далі')
    frame[0] = min(len(steps) - 1, frame[0] + 1)
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

plt.show()
