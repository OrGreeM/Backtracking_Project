import sys, time, copy
sys.setrecursionlimit(100000)
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button, Slider
GRID_TEMPLATE = ['....', '.##.', '.##.', '....']
WORDS_DB = ['AURA', 'AXIS', 'BABY', 'BACK', 'BARD', 'BARE', 'BARK', 'BASE', 'BASS', 'BEAR', 'BEEF', 'BIRD', 'BLUE', 'BOAT', 'BOMB', 'BONE', 'BOOK', 'BOSS', 'BOWL', 'BULK', 'BULL', 'BUSH', 'CAKE', 'CALF', 'CAMP', 'CARD', 'CARE', 'CASH', 'CAST', 'CAVE', 'CELL', 'CHAT', 'CHEF', 'CITY', 'CLUB', 'COAL', 'COAT', 'CODE', 'COIN', 'COOK', 'COOL', 'COPE', 'COPY', 'CORE', 'CORN', 'COST', 'CRAB', 'CROP', 'CROW', 'DARK', 'DART', 'DASH', 'DATA', 'DATE', 'DAWN', 'DEAD', 'DEAL', 'DEAN', 'DEAR', 'DECK', 'DEEP', 'DEER', 'DESK', 'DIAL', 'DIET', 'DIRT', 'DISH', 'DISK', 'DIVE', 'DOCK', 'DOOR', 'DOSE', 'DOWN', 'DRAW', 'DROP', 'DUAL', 'DUST', 'DUTY', 'EACH', 'EARN', 'EASY', 'EDGE', 'EPIC', 'EVEN', 'EVER', 'EVIL', 'EXIT', 'FACE', 'FACT', 'FADE', 'FAIL', 'FAIR', 'FALL', 'FARM', 'FAST', 'FEAR', 'FEED', 'FEEL', 'FILE', 'FILL', 'FILM', 'FIND', 'FINE', 'FIRE', 'FIRM', 'FISH', 'FIVE', 'FLAG', 'FLAT', 'FLOW', 'FOLD', 'FOOD', 'FOOT', 'FORD', 'FORM', 'FUND', 'GAME', 'GANG', 'GATE', 'GEAR', 'GIFT', 'GIRL', 'GLAD', 'GOAL', 'GOES', 'GOLD', 'GOLF', 'GOOD', 'GRAY', 'GREY', 'GRIP', 'GROW', 'GULF', 'HAIR', 'HALF', 'HALL', 'HAND', 'HANG', 'HARD', 'HARM', 'HATE', 'HEAD', 'HEAL', 'HEAR', 'HEAT', 'HELP', 'HERO', 'HIDE', 'HIGH', 'HILL', 'HIRE', 'HOLD', 'HOPE', 'HOST', 'HOUR', 'HUGE', 'HUNT', 'HURT', 'IDEA', 'IRON', 'ITEM', 'JACK', 'JOIN', 'JOKE', 'JUMP', 'JURY', 'JUST', 'KEEP', 'KICK', 'KILL', 'KIND', 'KING', 'KISS', 'KNEE', 'LACK', 'LAKE', 'LAND', 'LAST', 'LATE', 'LEAD', 'LEAF', 'LEAN', 'LEFT', 'LESS', 'LIFE', 'LIFT', 'LINE', 'LINK', 'LION', 'LIST', 'LIVE', 'LOAD', 'LOAN', 'LOCK', 'LOGO', 'LONG', 'LOOK', 'LOSS', 'LOST', 'LOVE', 'LUCK', 'MAKE', 'MALE', 'MALL', 'MARK', 'MASS', 'MATH', 'MEAL', 'MEAT', 'MEET', 'MENU', 'MILD', 'MILE', 'MILK', 'MIND', 'MINE', 'MODE', 'MOON', 'MORE', 'MOST', 'MOVE', 'MUCH', 'MUST', 'NAME', 'NAVY', 'NEAR', 'NECK', 'NEED', 'NEWS', 'NICE', 'NINE', 'NONE', 'NOSE', 'NOTE', 'ONLY', 'OPEN', 'ORAL', 'OVEN', 'OVER', 'PACE', 'PAGE', 'PAIN', 'PAIR', 'PALM', 'PARK', 'PART', 'PASS', 'PAST', 'PATH', 'PEAK', 'PEER', 'PICK', 'PILL', 'PINE', 'PIPE', 'PLAN', 'PLAY', 'PLOT', 'PLUG', 'PLUS', 'POEL', 'POEM', 'POET', 'POLE', 'POOL', 'POOR', 'PORT', 'POST', 'PULL', 'PURE', 'PUSH', 'RACE', 'RAIN', 'RARE', 'RATE', 'READ', 'REAL', 'REAR', 'RELY', 'RENT', 'REST', 'RICE', 'RICH', 'RIDE', 'RING', 'RISE', 'RISK', 'ROAD', 'ROCK', 'ROLE', 'ROLL', 'ROOF', 'ROOM', 'ROOT', 'ROPE', 'ROSE', 'RULE', 'RUSH', 'SAFE', 'SAID', 'SAKE', 'SALE', 'SALT', 'SAME', 'SAND', 'SAVE', 'SEAT', 'SEED', 'SEEK', 'SEEM', 'SELL', 'SEND', 'SHIP', 'SHOE', 'SHOP', 'SHOT', 'SHOW', 'SHUT', 'SICK', 'SIDE', 'SIGN', 'SITE', 'SIZE', 'SKIN', 'SLIP', 'SLOW', 'SNOW', 'SOFT', 'SOIL', 'SOME', 'SONG', 'SOON', 'SORT', 'SOUL', 'SOUP', 'SPOT', 'STAR', 'STAY', 'STEP', 'STOP', 'SUCH', 'SUIT', 'SURE', 'TAKE', 'TALE', 'TALK', 'TALL', 'TANK', 'TAPE', 'TASK', 'TEAM', 'TEAR', 'TELL', 'TEND', 'TENT', 'TERM', 'TEST', 'TEXT', 'THAN', 'THAT', 'THEN', 'THEY', 'THIN', 'THIS', 'THUS', 'TILL', 'TIME', 'TINY', 'TOLD', 'TOLL', 'TONE', 'TOOK', 'TOOL', 'TOUR', 'TOWN', 'TREE', 'TRIP', 'TRUE', 'TUNE', 'TURN', 'TWIN', 'TYPE', 'UNIT', 'UPON', 'USED', 'USER', 'VAST', 'VERY', 'VICE', 'VIEW', 'VOID', 'VOTE', 'WAIT', 'WAKE', 'WALK', 'WALL', 'WANT', 'WARD', 'WASH', 'WAVE', 'WAYS', 'WEAK', 'WEAR', 'WEEK', 'WELL', 'WENT', 'WERE', 'WEST', 'WHAT', 'WHEN', 'WHOM', 'WIDE', 'WIFE', 'WILD', 'WILL', 'WIND', 'WINE', 'WING', 'WIRE', 'WISE', 'WISH', 'WITH', 'WOOD', 'WORD', 'WORK', 'WRAP', 'YARD', 'YEAR', 'YOUR', 'ZERO', 'ZONE', 'COLD', 'WARM', 'CREW', 'DOOM']
N_ROWS = len(GRID_TEMPLATE)
N_COLS = len(GRID_TEMPLATE[0])

class Slot:

    def __init__(self, id, r, c, length, d):
        self.id = id
        self.r = r
        self.c = c
        self.length = length
        self.d = d

def extract_slots(grid):
    slots = []
    slot_id = 0
    for r in range(N_ROWS):
        c = 0
        while c < N_COLS:
            if grid[r][c] == '.':
                length = 0
                while c + length < N_COLS and grid[r][c + length] == '.':
                    length += 1
                if length > 1:
                    slots.append(Slot(slot_id, r, c, length, 'H'))
                    slot_id += 1
                c += length
            else:
                c += 1
    for c in range(N_COLS):
        r = 0
        while r < N_ROWS:
            if grid[r][c] == '.':
                length = 0
                while r + length < N_ROWS and grid[r + length][c] == '.':
                    length += 1
                if length > 1:
                    slots.append(Slot(slot_id, r, c, length, 'V'))
                    slot_id += 1
                r += length
            else:
                r += 1
    return slots

def get_intersections(slots):
    intersections = {}
    for s1 in slots:
        for s2 in slots:
            if s1.id >= s2.id or s1.d == s2.d:
                continue
            h_slot = s1 if s1.d == 'H' else s2
            v_slot = s2 if s2.d == 'V' else s1
            if h_slot.c <= v_slot.c < h_slot.c + h_slot.length and v_slot.r <= h_slot.r < v_slot.r + v_slot.length:
                h_idx = v_slot.c - h_slot.c
                v_idx = h_slot.r - v_slot.r
                if s1.d == 'H':
                    intersections[s1.id, s2.id] = (h_idx, v_idx)
                    intersections[s2.id, s1.id] = (v_idx, h_idx)
                else:
                    intersections[s1.id, s2.id] = (v_idx, h_idx)
                    intersections[s2.id, s1.id] = (h_idx, v_idx)
    return intersections
SLOTS = extract_slots(GRID_TEMPLATE)
INTERSECTIONS = get_intersections(SLOTS)

def solve_basic():
    steps, s = ([], {'nodes': 0, 'backs': 0, 'solutions': 0, 'ms': 0})
    board = [list(row) for row in GRID_TEMPLATE]
    assigned_words = set()

    def fits(word, slot):
        for i in range(slot.length):
            r = slot.r + (0 if slot.d == 'H' else i)
            c = slot.c + (i if slot.d == 'H' else 0)
            if board[r][c] != '.' and board[r][c] != word[i]:
                return False
        return True

    def place(word, slot):
        old_chars = []
        for i in range(slot.length):
            r = slot.r + (0 if slot.d == 'H' else i)
            c = slot.c + (i if slot.d == 'H' else 0)
            old_chars.append(board[r][c])
            board[r][c] = word[i]
        return old_chars

    def remove(slot, old_chars):
        for i in range(slot.length):
            r = slot.r + (0 if slot.d == 'H' else i)
            c = slot.c + (i if slot.d == 'H' else 0)
            board[r][c] = old_chars[i]

    def bt(idx):
        if idx == len(SLOTS):
            s['solutions'] += 1
            steps.append(('sol', copy.deepcopy(board)))
            return True
        slot = SLOTS[idx]
        for word in WORDS_DB:
            if len(word) != slot.length or word in assigned_words:
                continue
            s['nodes'] += 1
            if fits(word, slot):
                old = place(word, slot)
                assigned_words.add(word)
                steps.append(('put', copy.deepcopy(board)))
                if bt(idx + 1):
                    return True
                assigned_words.remove(word)
                remove(slot, old)
                s['backs'] += 1
                steps.append(('rm', copy.deepcopy(board)))
        return False
    t0 = time.perf_counter()
    bt(0)
    s['ms'] = (time.perf_counter() - t0) * 1000
    return (steps, s)

def solve_fc():
    steps, s = ([], {'nodes': 0, 'backs': 0, 'solutions': 0, 'ms': 0})
    board = [list(row) for row in GRID_TEMPLATE]
    domains = {slot.id: set((w for w in WORDS_DB if len(w) == slot.length)) for slot in SLOTS}

    def place(word, slot):
        old_chars = []
        for i in range(slot.length):
            r = slot.r + (0 if slot.d == 'H' else i)
            c = slot.c + (i if slot.d == 'H' else 0)
            old_chars.append(board[r][c])
            board[r][c] = word[i]
        return old_chars

    def remove(slot, old_chars):
        for i in range(slot.length):
            r = slot.r + (0 if slot.d == 'H' else i)
            c = slot.c + (i if slot.d == 'H' else 0)
            board[r][c] = old_chars[i]

    def propagate(slot_id, word, unassigned):
        pruned = {vid: set() for vid in unassigned}
        for vid in unassigned:
            if word in domains[vid]:
                domains[vid].remove(word)
                pruned[vid].add(word)
                if not domains[vid]:
                    return (pruned, False)
        for vid in unassigned:
            if (slot_id, vid) in INTERSECTIONS:
                idx_u, idx_v = INTERSECTIONS[slot_id, vid]
                char_needed = word[idx_u]
                to_remove = set()
                for w in domains[vid]:
                    if w[idx_v] != char_needed:
                        to_remove.add(w)
                domains[vid] -= to_remove
                pruned[vid] |= to_remove
                if not domains[vid]:
                    return (pruned, False)
        return (pruned, True)

    def restore(pruned):
        for vid, words in pruned.items():
            domains[vid] |= words

    def bt(idx, unassigned):
        if idx == len(SLOTS):
            s['solutions'] += 1
            steps.append(('sol', copy.deepcopy(board)))
            return True
        slot = SLOTS[idx]
        rest = unassigned - {slot.id}
        for word in list(domains[slot.id]):
            s['nodes'] += 1
            old = place(word, slot)
            steps.append(('put', copy.deepcopy(board)))
            pruned, ok = propagate(slot.id, word, rest)
            if ok:
                if bt(idx + 1, rest):
                    return True
            restore(pruned)
            remove(slot, old)
            s['backs'] += 1
            steps.append(('rm', copy.deepcopy(board)))
        return False
    t0 = time.perf_counter()
    bt(0, set((s.id for s in SLOTS)))
    s['ms'] = (time.perf_counter() - t0) * 1000
    return (steps, s)

def solve_mrv():
    steps, s = ([], {'nodes': 0, 'backs': 0, 'solutions': 0, 'ms': 0})
    board = [list(row) for row in GRID_TEMPLATE]
    assigned_words = set()

    def fits(word, slot):
        for i in range(slot.length):
            r = slot.r + (0 if slot.d == 'H' else i)
            c = slot.c + (i if slot.d == 'H' else 0)
            if board[r][c] != '.' and board[r][c] != word[i]:
                return False
        return True

    def get_domain(slot):
        return [w for w in WORDS_DB if len(w) == slot.length and w not in assigned_words and fits(w, slot)]

    def place(word, slot):
        old_chars = []
        for i in range(slot.length):
            r = slot.r + (0 if slot.d == 'H' else i)
            c = slot.c + (i if slot.d == 'H' else 0)
            old_chars.append(board[r][c])
            board[r][c] = word[i]
        return old_chars

    def remove(slot, old_chars):
        for i in range(slot.length):
            r = slot.r + (0 if slot.d == 'H' else i)
            c = slot.c + (i if slot.d == 'H' else 0)
            board[r][c] = old_chars[i]

    def bt(unassigned):
        if not unassigned:
            s['solutions'] += 1
            steps.append(('sol', copy.deepcopy(board)))
            return True
        doms = {sid: get_domain(next((s for s in SLOTS if s.id == sid))) for sid in unassigned}
        best_sid = min(unassigned, key=lambda sid: len(doms[sid]))
        slot = next((s for s in SLOTS if s.id == best_sid))
        rest = unassigned - {best_sid}
        for word in doms[best_sid]:
            s['nodes'] += 1
            old = place(word, slot)
            assigned_words.add(word)
            steps.append(('put', copy.deepcopy(board)))
            if bt(rest):
                return True
            assigned_words.remove(word)
            remove(slot, old)
            s['backs'] += 1
            steps.append(('rm', copy.deepcopy(board)))
        return False
    t0 = time.perf_counter()
    bt(set((s.id for s in SLOTS)))
    s['ms'] = (time.perf_counter() - t0) * 1000
    return (steps, s)

def solve_mrv_fc():
    steps, s = ([], {'nodes': 0, 'backs': 0, 'solutions': 0, 'ms': 0})
    board = [list(row) for row in GRID_TEMPLATE]
    domains = {slot.id: set((w for w in WORDS_DB if len(w) == slot.length)) for slot in SLOTS}

    def place(word, slot):
        old_chars = []
        for i in range(slot.length):
            r = slot.r + (0 if slot.d == 'H' else i)
            c = slot.c + (i if slot.d == 'H' else 0)
            old_chars.append(board[r][c])
            board[r][c] = word[i]
        return old_chars

    def remove(slot, old_chars):
        for i in range(slot.length):
            r = slot.r + (0 if slot.d == 'H' else i)
            c = slot.c + (i if slot.d == 'H' else 0)
            board[r][c] = old_chars[i]

    def propagate(slot_id, word, unassigned):
        pruned = {vid: set() for vid in unassigned}
        for vid in unassigned:
            if word in domains[vid]:
                domains[vid].remove(word)
                pruned[vid].add(word)
                if not domains[vid]:
                    return (pruned, False)
        for vid in unassigned:
            if (slot_id, vid) in INTERSECTIONS:
                idx_u, idx_v = INTERSECTIONS[slot_id, vid]
                char_needed = word[idx_u]
                to_remove = set((w for w in domains[vid] if w[idx_v] != char_needed))
                domains[vid] -= to_remove
                pruned[vid] |= to_remove
                if not domains[vid]:
                    return (pruned, False)
        return (pruned, True)

    def restore(pruned):
        for vid, words in pruned.items():
            domains[vid] |= words

    def bt(unassigned):
        if not unassigned:
            s['solutions'] += 1
            steps.append(('sol', copy.deepcopy(board)))
            return True
        best_sid = min(unassigned, key=lambda sid: len(domains[sid]))
        slot = next((s for s in SLOTS if s.id == best_sid))
        rest = unassigned - {best_sid}
        for word in list(domains[best_sid]):
            s['nodes'] += 1
            old = place(word, slot)
            steps.append(('put', copy.deepcopy(board)))
            pruned, ok = propagate(best_sid, word, rest)
            if ok:
                if bt(rest):
                    return True
            restore(pruned)
            remove(slot, old)
            s['backs'] += 1
            steps.append(('rm', copy.deepcopy(board)))
        return False
    t0 = time.perf_counter()
    bt(set((s.id for s in SLOTS)))
    s['ms'] = (time.perf_counter() - t0) * 1000
    return (steps, s)
print('Обчислення кросворда...')
solvers = [solve_basic, solve_fc, solve_mrv, solve_mrv_fc]
all_steps, all_stats = ([], [])
for fn in solvers:
    st, ss = fn()
    if not st:
        st = [('put', [list(row) for row in GRID_TEMPLATE])]
    all_steps.append(st)
    all_stats.append(ss)
    tag = fn.__name__[6:]
    print(f"  {tag:10s}  кроків={len(st):6d}  вузлів={ss['nodes']:6d}  відкатів={ss['backs']:6d}  рішень={ss['solutions']}  {ss['ms']:.2f}мс")
BG = '#0d1117'
SQ_EMPTY = '#ffffff'
SQ_BLOCK = '#161b22'
SQ_TEXT = '#1a1a2e'
SOL_CLR = '#2ea043'
ALGO_CLR = ['#e8a838', '#4a9eff', '#c678dd', '#2ea043']
ALGO_SHORT = ['Базовий\nбектрекінг', 'Forward\nChecking', 'MRV', 'MRV + FC']
max_frames = max((len(s) for s in all_steps))
fig_cmp, axs = plt.subplots(1, 3, figsize=(14, 5), facecolor=BG)
fig_cmp.suptitle('Порівняння алгоритмів  ·  Crossword CSP', color='white', fontsize=14, fontweight='bold')
metrics = [('nodes', 'Вузлів досліджено'), ('backs', 'Кількість відкатів'), ('ms', 'Час виконання (мс)')]
for ax, (key, title) in zip(axs, metrics):
    ax.set_facecolor('#161b22')
    vals = [ss[key] for ss in all_stats]
    bars = ax.bar(range(4), vals, color=ALGO_CLR, edgecolor='none', width=0.55, zorder=3)
    ax.set_xticks(range(4))
    ax.set_xticklabels(['Базовий', 'FC', 'MRV', 'MRV+FC'], color='white', fontsize=10)
    ax.set_title(title, color='white', fontsize=12, fontweight='bold', pad=8)
    ax.tick_params(axis='y', colors='white')
    ax.tick_params(axis='x', length=0)
    for sp in ax.spines.values():
        sp.set_color('#30363d')
    ax.grid(axis='y', color='#30363d', linestyle='--', alpha=0.4, zorder=0)
    maxv = max(vals) if max(vals) > 0 else 1
    for bar, val in zip(bars, vals):
        label = f'{val:.2f}' if key == 'ms' else str(val)
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + maxv * 0.015, label, ha='center', va='bottom', color='white', fontsize=9, fontweight='bold', zorder=5)
fig_cmp.tight_layout(rect=[0, 0, 1, 0.94])
fig_anim = plt.figure(figsize=(22, 7), facecolor=BG)
gs = fig_anim.add_gridspec(1, 4, left=0.01, right=0.99, bottom=0.13, top=0.9, wspace=0.05)
anim_axes = [fig_anim.add_subplot(gs[0, i]) for i in range(4)]

def draw_board(ax, board, title, color, is_sol=False, done=False):
    ax.cla()
    ax.set_facecolor(BG)
    ax.axis('off')
    ax.set_xlim(-0.5, N_COLS + 0.5)
    ax.set_ylim(-0.5, N_ROWS + 0.5)
    ax.set_aspect('equal')
    ax.set_title(title, color=color, fontsize=10, fontweight='bold', pad=6, linespacing=1.5)
    for r in range(N_ROWS):
        for c in range(N_COLS):
            char = board[r][c]
            is_block = char == '#'
            fc = SQ_BLOCK if is_block else SQ_EMPTY
            ax.add_patch(patches.Rectangle((c, N_ROWS - 1 - r), 1, 1, lw=1.5, ec='#30363d', fc=fc))
            if char not in ('.', '#'):
                ax.text(c + 0.5, N_ROWS - 0.5 - r, char, ha='center', va='center', fontsize=20, color=SQ_TEXT, fontweight='bold', zorder=3)
    bc = SOL_CLR if is_sol else '#30363d' if done else '#4a5568'
    bw = 4.0 if is_sol else 2.0
    ax.add_patch(patches.Rectangle((0, 0), N_COLS, N_ROWS, lw=bw, ec=bc, fc='none', zorder=4))
    ax.add_patch(patches.Rectangle((0, -0.6), N_COLS, 0.3, lw=0, fc=color, zorder=5, alpha=0.85))
    if done:
        ax.text(N_COLS / 2, N_ROWS / 2, '✓', ha='center', va='center', fontsize=60, color='#2ea043', alpha=0.25, fontweight='bold', zorder=6)
frame = [0]
running = [True]

def render(f):
    for steps, ax, color, short in zip(all_steps, anim_axes, ALGO_CLR, ALGO_SHORT):
        fi = min(f, len(steps) - 1)
        ev, bd = steps[fi]
        is_sol = ev == 'sol'
        done = f >= len(steps) - 1
        pct = fi * 100 // max(len(steps) - 1, 1)
        status = '✓ DONE' if done else f'{pct}%'
        title = f'{short}\nкрок {fi + 1}/{len(steps)}  [{status}]'
        draw_board(ax, bd, title, color, is_sol, done)
    fig_anim.suptitle(f'Кросворд CSP  ·  крок {f + 1} / {max_frames}', color='white', fontsize=12, fontweight='bold', y=0.978)
    fig_anim.canvas.draw_idle()
ax_pp = fig_anim.add_axes([0.38, 0.025, 0.08, 0.05])
ax_prev = fig_anim.add_axes([0.28, 0.025, 0.08, 0.05])
ax_next = fig_anim.add_axes([0.47, 0.025, 0.08, 0.05])
ax_spd = fig_anim.add_axes([0.1, 0.035, 0.14, 0.03])
for a in (ax_pp, ax_prev, ax_next, ax_spd):
    a.set_facecolor('#161b22')
btn_pp = Button(ax_pp, 'Пауза', color='#161b22', hovercolor='#21262d')
btn_prev = Button(ax_prev, '◀ Назад', color='#161b22', hovercolor='#21262d')
btn_next = Button(ax_next, 'Вперед ▶', color='#161b22', hovercolor='#21262d')
sld_spd = Slider(ax_spd, 'fps', 1.0, 30.0, valinit=8.0, color='#ffd700')
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
