import sys, time, copy, argparse, random
sys.setrecursionlimit(100000)
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button, Slider


parser = argparse.ArgumentParser(description="Crossword CSP Solver")
parser.add_argument("--no-vis", action="store_true", help="Не показувати візуалізацію")
parser.add_argument("--algs", nargs="+", choices=["basic", "fc", "mrv", "mrv_fc"],
                    default=["basic", "fc", "mrv", "mrv_fc"], help="Алгоритми для запуску")
parser.add_argument("--grid-size", type=int, default=None, metavar="N",
                    help="Розмір випадкової сітки N×N (наприклад, 5, 6, 7)")
parser.add_argument("--block-ratio", type=float, default=0.25, metavar="R",
                    help="Частка заблокованих клітинок для випадкової сітки (0.0–0.5, default: 0.25)")
parser.add_argument("--seed", type=int, default=None, help="Seed для генерації випадкової сітки")
parser.add_argument("--words-file", type=str, default=None, metavar="PATH",
                    help="Шлях до текстового файлу зі словами (по одному на рядок). Default: en.txt поруч зі скриптом")
args = parser.parse_args()

def generate_random_grid(n, block_ratio=0.25, seed=None):
    """Generate a random n×n crossword grid with 180° rotational symmetry.

    The grid uses '.' for open cells and '#' for blocked cells.
    Blocks are placed symmetrically so that grid[r][c] == grid[n-1-r][n-1-c].
    After placement, isolated single-cell open slots (length 1) are removed
    by converting them to blocks, and we ensure at least 2 valid slots exist.

    Args:
        n:           Grid side length (minimum 4).
        block_ratio: Fraction of cells to block (0.0 – 0.5). Values above 0.5
                     are clamped because symmetry doubles each placement.
        seed:        Optional RNG seed for reproducibility.

    Returns:
        A list of n strings, each of length n, containing '.' and '#'.
    """
    if n < 4:
        raise ValueError("Grid size must be at least 4")

    rng = random.Random(seed)
    block_ratio = max(0.0, min(block_ratio, 0.5))

    grid = [['.' for _ in range(n)] for _ in range(n)]

    # Collect all unique symmetric pairs of cells
    pairs = []
    for r in range(n):
        for c in range(n):
            sr, sc = n - 1 - r, n - 1 - c
            pair = tuple(sorted(((r, c), (sr, sc))))
            if pair not in pairs:
                pairs.append(pair)

    # Determine how many pairs to block
    total_cells = n * n
    target_blocks = int(total_cells * block_ratio)
    # Each pair blocks 2 cells (or 1 if it's the centre cell of an odd grid)
    rng.shuffle(pairs)

    blocked = 0
    for pair in pairs:
        if blocked >= target_blocks:
            break
        (r1, c1), (r2, c2) = pair
        grid[r1][c1] = '#'
        grid[r2][c2] = '#'
        blocked += (2 if (r1, c1) != (r2, c2) else 1)

    # Clean up: remove isolated single open cells (would create length-1 "slots")
    changed = True
    while changed:
        changed = False
        for r in range(n):
            for c in range(n):
                if grid[r][c] != '.':
                    continue
                # Check horizontal span
                h_len = 0
                cc = c
                while cc < n and grid[r][cc] == '.':
                    h_len += 1
                    cc += 1
                cc = c - 1
                while cc >= 0 and grid[r][cc] == '.':
                    h_len += 1
                    cc -= 1
                # Check vertical span
                v_len = 0
                rr = r
                while rr < n and grid[rr][c] == '.':
                    v_len += 1
                    rr += 1
                rr = r - 1
                while rr >= 0 and grid[rr][c] == '.':
                    v_len += 1
                    rr -= 1
                # If the cell only belongs to runs of length 1, block it
                if h_len <= 1 and v_len <= 1:
                    grid[r][c] = '#'
                    sr, sc = n - 1 - r, n - 1 - c
                    grid[sr][sc] = '#'
                    changed = True

    return [''.join(row) for row in grid]


DEFAULT_GRID = ['....', '.##.', '.##.', '....']

if args.grid_size is not None:
    GRID_TEMPLATE = generate_random_grid(args.grid_size, args.block_ratio, args.seed)
    print(f"Згенерована випадкова сітка {args.grid_size}x{args.grid_size}:")
    for row in GRID_TEMPLATE:
        print(f"  {row}")
else:
    GRID_TEMPLATE = DEFAULT_GRID

import os as _os

_FALLBACK_WORDS = ['AURA', 'AXIS', 'BABY', 'BACK', 'BASE', 'BEAR', 'BIRD', 'BLUE', 'BOAT', 'BONE', 'BOOK', 'CAKE', 'CARD', 'CARE', 'CAVE', 'CELL', 'CITY', 'CLUB', 'COAL', 'CODE', 'DARK', 'DATA', 'DEAD', 'DESK', 'DISH', 'DIVE', 'DOOR', 'DROP', 'DUST', 'EACH', 'EARN', 'EASY', 'EDGE', 'EVIL', 'EXIT', 'FACE', 'FACT', 'FAIL', 'FAIR', 'FALL', 'FARM', 'FAST', 'FEAR', 'FILE', 'FILL', 'FILM', 'FIND', 'FINE', 'FIRE', 'FIRM', 'FISH', 'FLAG', 'FLAT', 'FLOW', 'FOLD', 'FOOD', 'FOOT', 'FORM', 'FUND', 'GAME', 'GATE', 'GEAR', 'GIFT', 'GIRL', 'GOAL', 'GOLD', 'GOOD', 'HAIR', 'HALF', 'HALL', 'HAND', 'HARD', 'HARM', 'HEAD', 'HEAL', 'HEAR', 'HEAT', 'HELP', 'HERO', 'HIDE', 'HIGH', 'HILL', 'HOLD', 'HOPE', 'HOST', 'HOUR', 'HUGE', 'HUNT', 'HURT', 'IDEA', 'IRON', 'ITEM', 'JACK', 'JOIN', 'JOKE', 'JUMP', 'JUST', 'KEEP', 'KICK', 'KILL', 'KIND', 'KING', 'KISS', 'KNEE', 'LACK', 'LAKE', 'LAND', 'LAST', 'LATE', 'LEAD', 'LEAF', 'LEAN', 'LEFT', 'LESS', 'LIFE', 'LIFT', 'LINE', 'LINK', 'LION', 'LIST', 'LIVE', 'LOAD', 'LOAN', 'LOCK', 'LONG', 'LOOK', 'LOSS', 'LOST', 'LOVE', 'LUCK', 'MAKE', 'MALE', 'MALL', 'MARK', 'MASS', 'MATH', 'MEAL', 'MEAT', 'MEET', 'MILD', 'MILE', 'MILK', 'MIND', 'MINE', 'MODE', 'MOON', 'MORE', 'MOST', 'MOVE', 'MUCH', 'MUST', 'NAME', 'NAVY', 'NEAR', 'NECK', 'NEED', 'NEWS', 'NICE', 'NINE', 'NONE', 'NOSE', 'NOTE', 'ONLY', 'OPEN', 'ORAL', 'OVEN', 'OVER', 'PACE', 'PAGE', 'PAIN', 'PAIR', 'PALM', 'PARK', 'PART', 'PASS', 'PAST', 'PATH', 'PEAK', 'PICK', 'PILL', 'PINE', 'PIPE', 'PLAN', 'PLAY', 'PLOT', 'PLUG', 'PLUS', 'POEM', 'POET', 'POLE', 'POOL', 'POOR', 'PORT', 'POST', 'PULL', 'PURE', 'PUSH', 'RACE', 'RAIN', 'RARE', 'RATE', 'READ', 'REAL', 'RENT', 'REST', 'RICE', 'RICH', 'RIDE', 'RING', 'RISE', 'RISK', 'ROAD', 'ROCK', 'ROLE', 'ROLL', 'ROOF', 'ROOM', 'ROOT', 'ROPE', 'ROSE', 'RULE', 'RUSH', 'SAFE', 'SAID', 'SAKE', 'SALE', 'SALT', 'SAME', 'SAND', 'SAVE', 'SEAT', 'SEED', 'SEEK', 'SEEM', 'SELL', 'SEND', 'SHIP', 'SHOE', 'SHOP', 'SHOT', 'SHOW', 'SHUT', 'SICK', 'SIDE', 'SIGN', 'SITE', 'SIZE', 'SKIN', 'SLIP', 'SLOW', 'SNOW', 'SOFT', 'SOIL', 'SOME', 'SONG', 'SOON', 'SORT', 'SOUL', 'SOUP', 'SPOT', 'STAR', 'STAY', 'STEP', 'STOP', 'SUCH', 'SUIT', 'SURE', 'TAKE', 'TALE', 'TALK', 'TALL', 'TANK', 'TAPE', 'TASK', 'TEAM', 'TEAR', 'TELL', 'TEND', 'TENT', 'TERM', 'TEST', 'TEXT', 'THAN', 'THAT', 'THEN', 'THEY', 'THIN', 'THIS', 'TILL', 'TIME', 'TINY', 'TOLD', 'TOLL', 'TONE', 'TOOK', 'TOOL', 'TOUR', 'TOWN', 'TREE', 'TRIP', 'TRUE', 'TUNE', 'TURN', 'TWIN', 'TYPE', 'UNIT', 'UPON', 'USED', 'USER', 'VAST', 'VERY', 'VICE', 'VIEW', 'VOID', 'VOTE', 'WAIT', 'WAKE', 'WALK', 'WALL', 'WANT', 'WARD', 'WASH', 'WAVE', 'WEAK', 'WEAR', 'WEEK', 'WELL', 'WENT', 'WERE', 'WEST', 'WHAT', 'WHEN', 'WHOM', 'WIDE', 'WIFE', 'WILD', 'WILL', 'WIND', 'WINE', 'WING', 'WIRE', 'WISE', 'WISH', 'WITH', 'WOOD', 'WORD', 'WORK', 'WRAP', 'YARD', 'YEAR', 'YOUR', 'ZERO', 'ZONE', 'COLD', 'WARM', 'CREW', 'DOOM']

def _load_words(path=None):
    """Load words from a text file (one word per line).

    Words are uppercased and filtered to alphabetic-only characters.
    Duplicates are removed while preserving order.
    Falls back to the built-in word list if the file cannot be read.
    """
    if path is None:
        # Default: en.txt next to this script
        path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'en.txt')
    try:
        seen = set()
        words = []
        with open(path, encoding='utf-8', errors='ignore') as fh:
            for line in fh:
                w = line.strip().upper()
                if w.isalpha() and w not in seen:
                    seen.add(w)
                    words.append(w)
        if not words:
            raise ValueError('File is empty or contains no valid words')
        print(f'Loaded {len(words):,} words from "{_os.path.basename(path)}"')
        return words
    except (OSError, ValueError) as e:
        print(f'Warning: could not load words file ({e}). Using built-in word list.')
        return list(_FALLBACK_WORDS)

WORDS_DB = _load_words(args.words_file)
WORDS_BY_LEN = {}
for w in WORDS_DB:
    WORDS_BY_LEN.setdefault(len(w), []).append(w)

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
        for word in WORDS_BY_LEN.get(slot.length, []):
            if word in assigned_words:
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
    domains = {slot.id: set(WORDS_BY_LEN.get(slot.length, [])) for slot in SLOTS}

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
        return [w for w in WORDS_BY_LEN.get(slot.length, []) if w not in assigned_words and fits(w, slot)]

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
    domains = {slot.id: set(WORDS_BY_LEN.get(slot.length, [])) for slot in SLOTS}

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
algo_mapping = {'basic': solve_basic, 'fc': solve_fc, 'mrv': solve_mrv, 'mrv_fc': solve_mrv_fc}
idx_mapping = {'basic': 0, 'fc': 1, 'mrv': 2, 'mrv_fc': 3}

solvers = [algo_mapping[k] for k in args.algs]
all_steps, all_stats = ([], [])
for fn in solvers:
    st, ss = fn()
    if not st:
        st = [('put', [list(row) for row in GRID_TEMPLATE])]
    all_steps.append(st)
    all_stats.append(ss)
    tag = fn.__name__[6:]
    print(f"  {tag:10s}  кроків={len(st):6d}  вузлів={ss['nodes']:6d}  відкатів={ss['backs']:6d}  рішень={ss['solutions']}  {ss['ms']:.2f}мс")

if args.no_vis:
    sys.exit(0)

BG = '#0d1117'
SQ_EMPTY = '#ffffff'
SQ_BLOCK = '#161b22'
SQ_TEXT = '#1a1a2e'
SOL_CLR = '#2ea043'
ALGO_CLR = ['#e8a838', '#4a9eff', '#c678dd', '#2ea043']
ALGO_SHORT = ['Базовий\nбектрекінг', 'Forward\nChecking', 'MRV', 'MRV + FC']

active_clr = [ALGO_CLR[idx_mapping[k]] for k in args.algs]
active_short = [ALGO_SHORT[idx_mapping[k]] for k in args.algs]

# Collapse consecutive identical boards per algorithm to cut redundant frames
def _dedup(steps):
    """Remove consecutive duplicate board states, keeping first and last."""
    out = [steps[0]]
    for ev, bd in steps[1:]:
        if bd != out[-1][1]:
            out.append((ev, bd))
        elif ev == 'sol':          # always keep the solution frame
            out.append((ev, bd))
    return out

all_steps = [_dedup(s) for s in all_steps]
max_frames = max((len(s) for s in all_steps))
fig_cmp, axs = plt.subplots(1, 3, figsize=(14, 5), facecolor=BG)
fig_cmp.suptitle('Порівняння алгоритмів  ·  Crossword CSP', color='white', fontsize=14, fontweight='bold')
metrics = [('nodes', 'Вузлів досліджено'), ('backs', 'Кількість відкатів'), ('ms', 'Час виконання (мс)')]
for ax, (key, title) in zip(axs, metrics):
    ax.set_facecolor('#161b22')
    vals = [ss[key] for ss in all_stats]
    bars = ax.bar(range(len(solvers)), vals, color=active_clr, edgecolor='none', width=0.55, zorder=3)
    ax.set_xticks(range(len(solvers)))
    ax.set_xticklabels([short.replace('\n', ' ') for short in active_short], color='white', fontsize=10)
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
n_plots_anim = len(solvers)
gs = fig_anim.add_gridspec(1, n_plots_anim, left=0.01, right=0.99, bottom=0.13, top=0.9, wspace=0.05)
anim_axes = [fig_anim.add_subplot(gs[0, i]) for i in range(n_plots_anim)]

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
    for steps, ax, color, short in zip(all_steps, anim_axes, active_clr, active_short):
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
        next_f = frame[0] + 1
        if next_f >= max_frames:
            # reached the end — stop and show final frame
            running[0] = False
            btn_pp.label.set_text('Далі')
            frame[0] = max_frames - 1
            render(frame[0])
            timer.stop()
        else:
            frame[0] = next_f
            render(frame[0])
timer = fig_anim.canvas.new_timer(interval=125)
timer.add_callback(tick)
timer.start()
render(0)
plt.show()
