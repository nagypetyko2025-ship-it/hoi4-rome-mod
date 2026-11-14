"""Build the world of 509 BC on the committed map: states, countries and everything derived from them.

usage:  python tools/world.py                 write the game files, then run tools/validate.py
        python tools/world.py --preview DIR   only compute the world and draw political maps into DIR
        python tools/world.py --freeze-core   (one-off) store Italy's states in tools/data/core_states_245.json

Needs only this mod folder, numpy and Pillow - no game install.

What is kept as it is (proven to load and run in the game): provinces.bmp, definition.csv, every raster,
the strategic regions, adjacencies, weather positions.
What is rebuilt from tools/data/world_509bc.py:
    history/states, history/countries, common/countries (+ colors.txt), common/country_tags,
    common/names, common/bookmarks, gfx/flags, localisation/english/replace, map/supply_nodes.txt,
    map/railways.txt, and through tools/positions.py map/buildings.txt and map/unitstacks.txt.

How land is shared out: Italy, Sicily, Sardinia, Corsica and Punic Africa keep their hand-made states
(core_states_245.json). Every other land province goes to the region whose seed reaches it first
overland (mountains, deserts and marshes slow the spread; a region's `power` speeds it up), islands
without a seed join the nearest shore. A region is then cut into states that each lie inside one
strategic region (engine rule) and are not too big.
"""
import colorsys
import heapq
import importlib
import json
import math
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

TOOLS = Path(__file__).resolve().parent
MOD = TOOLS.parent
sys.path.insert(0, str(TOOLS))
import positions as P  # noqa: E402   (load_map / province_table, and the position writers)
from geo import to_xy  # noqa: E402
import resources as R  # noqa: E402  ancient resources (round 21)
from data.leaders_509bc import LEADERS, LATER  # noqa: E402
import data.tech_tree as TT  # noqa: E402

D = importlib.import_module("data.world_509bc")
OLD = importlib.import_module("data.world_245")
CORE_JSON = TOOLS / "data" / "core_states_245.json"
WLD = "WLD"

# how hard a province is to cross / how many people it feeds
TERRAIN_COST = {"plains": 1.0, "urban": 1.0, "forest": 1.15, "hills": 1.3, "desert": 1.35, "marsh": 1.4,
                "jungle": 1.4, "mountain": 2.1}
TERRAIN_FOOD = {"plains": 1.0, "urban": 1.6, "forest": 0.6, "hills": 0.7, "desert": 0.12, "marsh": 0.35,
                "jungle": 0.4, "mountain": 0.3}
INFRA_SCALE = 2   # roads: 10 levels of 10% instead of the base game's 5 of 20% (tools/buildings.py, defines)
GOV_IDEOLOGY = {"republic": "democratic", "monarchy": "neutrality", "tyranny": "fascism", "tribal": "communism"}   # ideologies renamed: tools/content.py (ancient forms)
IDEOLOGIES = ("democratic", "fascism", "communism", "neutrality")
# "parties" of the ancient world (short name, long name): who rules, by form of government ...
PARTY_BY_GOV = {
    ("republic", "democratic"): ("Assembly", "Assembly of the Citizens"),
    ("monarchy", "neutrality"): ("Royal Court", "Court of the King"),
    ("tribal", "communism"): ("Elders", "Council of the Elders"),
    ("tyranny", "fascism"): ("Tyrant", "Household of the Tyrant"),
}
# ... and the factions out of power
PARTY_OTHER = {
    "democratic": ("Citizens", "Party of the Citizens"),
    "fascism": ("Would-be Tyrants", "Followers of the Strongman"),
    "communism": ("Clansmen", "Gathering of the Clans"),
    "neutrality": ("Royalists", "Friends of the King"),
}
PARTIES = {   # the ones history gave a name
    ("ROM", "democratic"): ("Senatus", "Senatus Populusque Romanus"),
    ("CAR", "democratic"): ("Adirim", "Council of the Mighty Ones"),
    ("ATH", "democratic"): ("Ekklesia", "Ekklesia of the Athenians"),
    ("LAK", "neutrality"): ("Gerousia", "Kings and Gerousia of Lakedaimon"),
    ("PRS", "neutrality"): ("King of Kings", "Court of the King of Kings"),
    ("MKD", "neutrality"): ("Argeads", "House of the Argeads"),
    ("SYR", "democratic"): ("Gamoroi", "Assembly of the Gamoroi"),
}
SLOTS = {"wasteland": 0, "pastoral": 1, "rural": 2, "town": 4, "large_town": 5, "city": 6, "large_city": 8,
         "metropolis": 10, "megalopolis": 12}
# tags the script parser reads as something else (NUM and RED were found the hard way) or Windows refuses as file names
RESERVED = {"NUM", "RED", "AND", "NOT", "ALL", "ANY", "TAG", "OOB", "LOG", "SET", "ADD", "MAX", "MIN", "VAR", "YES",
            "REB", "CON", "PRN", "AUX", "NUL"}


def fail(msg):
    print("ERROR:", msg)
    sys.exit(1)


def write(rel, text, bom=False):
    p = MOD / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8-sig" if bom else "utf-8", newline="\n")


# ============================================================================ the map as it is
class Map:
    def __init__(self):
        self.defs, self.labels = P.load_map()
        self.H, self.W = self.labels.shape
        self.provs, self.cx, self.cy = P.province_table(self.defs, self.labels)
        lab = self.labels
        a = np.concatenate([lab[:, :-1].ravel(), lab[:-1, :].ravel()])           # no east-west wrap:
        b = np.concatenate([lab[:, 1:].ravel(), lab[1:, :].ravel()])             # peoples do not spread over the seam
        m = a != b
        key = np.minimum(a[m], b[m]).astype(np.int64) * 100000 + np.maximum(a[m], b[m])
        keys, counts = np.unique(key, return_counts=True)
        self.border = {(int(k // 100000), int(k % 100000)): int(c) for k, c in zip(keys, counts)}
        self.land = {i for i, p in self.provs.items() if p["type"] == "land"}
        walls = set()                                                            # impassable borders (adjacencies.csv)
        for line in (MOD / "map" / "adjacencies.csv").read_text(encoding="utf-8").splitlines()[1:]:
            f = line.split(";")
            if len(f) > 3 and f[2] == "impassable":
                walls.add((min(int(f[0]), int(f[1])), max(int(f[0]), int(f[1]))))
        self.adj = defaultdict(dict)                                             # land province -> {land neighbour: border px}
        for (p, q), c in self.border.items():
            if p in self.land and q in self.land and (p, q) not in walls:
                self.adj[p][q] = c
                self.adj[q][p] = c
        self.sreg = {}
        for fp in (MOD / "map" / "strategicregions").glob("*.txt"):
            t = re.sub(r"#[^\n]*", "", fp.read_text(encoding="utf-8-sig"))
            rid = int(re.search(r"\bid\s*=\s*(\d+)", t).group(1))
            for p in re.search(r"provinces\s*=\s*\{([^}]*)\}", t).group(1).split():
                self.sreg[int(p)] = rid

    def dist(self, p, q):
        return math.hypot(self.cx[p] - self.cx[q], self.cy[p] - self.cy[q])

    def cost(self, p, q):
        t = (TERRAIN_COST.get(self.provs[p]["terrain"], 1.2) + TERRAIN_COST.get(self.provs[q]["terrain"], 1.2)) / 2
        return self.dist(p, q) * t

    def near(self, x, y, ok, maxd):
        """land provinces with a pixel within maxd of (x, y), nearest first -> [(distance, province)]"""
        xi, yi, r = int(round(x)), int(round(y)), int(maxd) + 1
        y0, y1, x0, x1 = max(0, yi - r), min(self.H, yi + r + 1), max(0, xi - r), min(self.W, xi + r + 1)
        if y0 >= y1 or x0 >= x1:
            return []
        sub = self.labels[y0:y1, x0:x1]
        yy, xx = np.nonzero(ok[sub])
        if not len(yy):
            return []
        d = np.hypot(yy + y0 - y, xx + x0 - x)
        ps = sub[yy, xx]
        order = np.argsort(d, kind="stable")
        uniq, first = np.unique(ps[order], return_index=True)
        out = sorted((float(d[order][f]), int(p)) for p, f in zip(uniq, first))
        return [(dd, p) for dd, p in out if dd <= maxd]


def components(nodes, adj):
    """connected groups of `nodes` -> list of sets"""
    nodes, out = set(nodes), []
    while nodes:
        s = nodes.pop()
        comp, stack = {s}, [s]
        while stack:
            for q in adj[stack.pop()]:
                if q in nodes:
                    nodes.discard(q)
                    comp.add(q)
                    stack.append(q)
        out.append(comp)
    return out


# ============================================================================ Italy as it was built
def parse_state_files():
    out = []
    for fp in (MOD / "history" / "states").glob("*.txt"):
        raw = fp.read_text(encoding="utf-8-sig")
        t = re.sub(r"#[^\n]*", "", raw)
        g = lambda pat, text=t: re.search(pat, text)  # noqa: E731
        s = dict(id=int(g(r"\bid\s*=\s*(\d+)").group(1)), name=g(r'name\s*=\s*"[^"]*"\s*#\s*(.+)', raw).group(1).strip(),
                 owner=g(r"\bowner\s*=\s*(\w+)").group(1), pop=int(g(r"manpower\s*=\s*(\d+)").group(1)),
                 category=g(r"state_category\s*=\s*(\w+)").group(1),
                 provinces=[int(x) for x in g(r"provinces\s*=\s*\{([^}]*)\}").group(1).split()],
                 cores=re.findall(r"add_core_of\s*=\s*(\w+)", t),
                 vps=[[int(p), int(v), c.strip()] for p, v, c in
                      re.findall(r"victory_points\s*=\s*\{\s*(\d+)\s+(\d+)\s*\}\s*#\s*(.+)", raw)],
                 ports={int(p): int(v) for p, v in re.findall(r"(\d+)\s*=\s*\{\s*naval_base\s*=\s*(\d+)", t)},
                 buildings={k: int(g(k + r"\s*=\s*(\d+)").group(1)) for k in
                            ("infrastructure", "industrial_complex", "arms_factory") if g(k + r"\s*=\s*(\d+)")})
        out.append(s)
    return sorted(out, key=lambda s: s["id"])


def freeze_core():
    """One-off: Italy, Sicily, Sardinia, Corsica and Punic Africa were laid out by hand on the vanilla
    province grid (tools/data/world_245.py) and translated to this map by the first generator. Their
    state files are stored here so that this tool no longer needs the game or that translation."""
    states = [s for s in parse_state_files() if s["owner"] != WLD]
    caps = {}
    for fp in (MOD / "history" / "countries").glob("*.txt"):
        m = re.search(r"\bcapital\s*=\s*(\d+)", fp.read_text(encoding="utf-8-sig"))
        caps[fp.name[:3]] = int(m.group(1))
    by_id = {s["id"]: s for s in states}
    for tag, sid in caps.items():
        if sid in by_id:
            by_id[sid]["capital"] = True
    defs, _ = P.load_map()
    lakes = sorted(p for s in parse_state_files() for p in s["provinces"] if defs[p]["type"] == "lake")
    CORE_JSON.write_text(json.dumps(dict(states=states, lakes_in_states=lakes), indent=1, ensure_ascii=False),
                         encoding="utf-8", newline="\n")
    print(f"frozen: {len(states)} states of {len({s['owner'] for s in states})} countries, "
          f"{len(lakes)} lake provinces that sit in a state")


# ============================================================================ who lives where
def countries():
    """tag -> dict(name, adj, culture, gov, color, gfx, flag, names, urban)"""
    out = {}
    for tag, c in OLD.COUNTRIES.items():
        cul = OLD.CULTURES[c["culture"]]
        out[tag] = dict(c, gfx=cul["gfx"][:-4], flag=cul["flag"], names=c["culture"], core=True,
                        urban=c["culture"] in ("latin", "etruscan", "greek", "punic"))
    for tag, c in D.PEOPLES.items():
        cul = D.CULTURES[c["culture"]]
        out[tag] = dict(c, gfx=cul["gfx"], flag=cul["flag"], names=cul["names"], urban=cul["urban"], core=False)
    for tag in out:
        if tag in RESERVED:
            fail(f"tag {tag} is a reserved word")
    return out


def assign(M, core):
    """-> regions (list of dicts with 'provinces'), province -> region index"""
    core_prov = {p: s["id"] for s in core["states"] for p in s["provinces"]}
    free = M.land - set(core_prov)
    ok = np.zeros(max(M.provs) + 1, bool)
    ok[list(free)] = True
    regions = []
    for r in D.REGIONS:
        regions.append(dict(r, wild=False))
    for name, seeds in D.WILDS:
        regions.append(dict(owner=WLD, name=name, pop=1000, power=1.0, cities=[], seeds=seeds, wild=True,
                            lon=seeds[0][0], lat=seeds[0][1]))
    taken, heap, dropped = {}, [], []
    # heartlands first, the most important city first: where two cities fall into the same province
    # (the grid is coarse in Greece), the greater one gets it and the other moves to a free province
    # next door - or is left out if there is none within half a province
    order = sorted(range(len(regions)), key=lambda i: (regions[i]["wild"], -(regions[i]["cities"][0][3] if regions[i]["cities"] else 0),
                                                       -regions[i]["pop"], i))
    for ri in order:
        r = regions[ri]
        x, y = to_xy(*r["seeds"][0])
        cand = M.near(x, y, ok, 60 if r["wild"] else 40)
        spots = [(d, p) for d, p in cand if p not in taken and d <= cand[0][0] + (60 if r["wild"] else 14)]
        if not spots:
            by = regions[taken[cand[0][1]]] if cand else None
            dropped.append(f"{r['owner']}/{r['name']}" + (f" (place taken by {by['owner']}/{by['name']})" if by else " (no land)"))
            r["dead"] = True
            continue
        r["home"], r["snap"] = spots[0][1], spots[0][0]
        r["moved"] = spots[0][1] != cand[0][1]
        taken[spots[0][1]] = ri
    for ri, r in enumerate(regions):
        if r.get("dead"):
            continue
        for lon, lat in r["seeds"][1:]:
            x, y = to_xy(lon, lat)
            cand = [(d, p) for d, p in M.near(x, y, ok, 40) if p not in taken]
            if cand:
                taken[cand[0][1]] = ri
    for p, ri in taken.items():
        heapq.heappush(heap, (0.0, p, ri))
    owner, best = {}, {}
    while heap:
        t, p, ri = heapq.heappop(heap)
        if p in owner:
            continue
        owner[p] = ri
        speed = regions[ri]["power"]
        for q in M.adj[p]:
            if q in free and q not in owner:
                nt = t + M.cost(p, q) / speed
                if nt < best.get(q, 1e18):
                    best[q] = nt
                    heapq.heappush(heap, (nt, q, ri))
    # islands nobody landed on: join the nearest shore (a region, or one of Italy's states)
    left = free - set(owner)
    attach = defaultdict(list)                            # core state id -> provinces
    if left:
        known = np.array(sorted(set(owner) | set(core_prov)))
        kx, ky = M.cx[known], M.cy[known]
        for comp in components(left, M.adj):
            cxm, cym = np.mean([M.cx[p] for p in comp]), np.mean([M.cy[p] for p in comp])
            k = int(known[np.argmin((kx - cxm) ** 2 + (ky - cym) ** 2)])
            for p in comp:
                if k in owner:
                    owner[p] = owner[k]
                else:
                    attach[core_prov[k]].append(p)
    for r in regions:
        r["provinces"] = []
    for p, ri in owner.items():
        regions[ri]["provinces"].append(p)
    if dropped:
        print("regions without room on this map (left out):", "; ".join(dropped))
    moved = [f"{r['owner']}/{r['name']}" for r in regions if r.get("moved")]
    if moved:
        print("heartlands moved to the province next door:", ", ".join(moved))
    return regions, owner, attach


# ============================================================================ previews
def font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def preview(M, prov_color, prov_state, labels_xy, out, name="world", zoom=None):
    """political map: provinces in their owner's colour, state borders thin, country borders dark"""
    n = max(M.provs) + 1
    lut = np.zeros((n, 3), np.uint8)
    lut[:] = (58, 92, 128)
    for p, c in prov_color.items():
        lut[p] = c
    for p, pr in M.provs.items():
        if pr["type"] == "lake":
            lut[p] = (90, 130, 165)
    img = lut[M.labels]
    st = np.zeros(n, np.int32)
    ow = np.zeros(n, np.int32)
    ids = {}
    for p, (sid, tag) in prov_state.items():
        st[p] = sid
        ow[p] = ids.setdefault(tag, len(ids) + 1)
    S, O = st[M.labels], ow[M.labels]
    sb = np.zeros(S.shape, bool)
    sb[:, 1:] |= S[:, 1:] != S[:, :-1]
    sb[1:, :] |= S[1:, :] != S[:-1, :]
    ob = np.zeros(S.shape, bool)
    ob[:, 1:] |= O[:, 1:] != O[:, :-1]
    ob[1:, :] |= O[1:, :] != O[:-1, :]
    ob[:, :-1] |= ob[:, 1:]
    ob[:-1, :] |= ob[1:, :]
    land = (S > 0)
    pb = np.zeros(S.shape, bool)
    pb[:, 1:] |= M.labels[:, 1:] != M.labels[:, :-1]
    pb[1:, :] |= M.labels[1:, :] != M.labels[:-1, :]
    img = img.copy()
    img[pb & land] = (img[pb & land] * 0.9).astype(np.uint8)
    img = img.copy()
    img[sb & land] = (img[sb & land] * 0.72).astype(np.uint8)
    img[ob] = (25, 20, 20)
    im = Image.fromarray(img, "RGB")
    out.mkdir(parents=True, exist_ok=True)
    im.save(out / f"{name}_full.png")
    f1, f2 = font(15), font(12)

    def tile(box, scale, fname, minvp):
        x0, y0, x1, y1 = box
        part = im.crop(box).resize((int((x1 - x0) * scale), int((y1 - y0) * scale)), Image.LANCZOS)
        d = ImageDraw.Draw(part)
        for (x, y, text, vp, kind) in labels_xy:
            if not (x0 <= x < x1 and y0 <= y < y1):
                continue
            px, py = (x - x0) * scale, (y - y0) * scale
            if kind == "tag":
                d.text((px, py), text, fill=(255, 255, 255), font=f1, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
            elif vp >= minvp:
                d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 255), outline=(0, 0, 0))
                d.text((px + 4, py - 6), text, fill=(255, 255, 220), font=f2, stroke_width=1, stroke_fill=(0, 0, 0))
        part.save(out / fname)

    if zoom:                                                  # one detail picture: x0,y0,x1,y1,scale
        x0, y0, x1, y1, sc = zoom
        tile((int(x0), int(y0), int(x1), int(y1)), sc, f"{name}_zoom.png", 1)
        return
    tile((0, 0, M.W, M.H), 0.5, f"{name}_all.png", 99)
    for nm, box in (("west", (150, 750, 1150, 1950)), ("italy_balkans", (900, 1300, 1900, 2050)),
                    ("north", (850, 250, 2050, 1400)), ("east", (1650, 1250, 2650, 2250)),
                    ("far_east", (2300, 1150, 3328, 2400)), ("africa", (200, 1750, 1900, 3072)),
                    ("arabia", (1700, 2000, 3000, 3072)), ("steppe", (1600, 600, 3328, 1500))):
        tile(box, 1.0 if (box[2] - box[0]) <= 1100 else 0.75, f"{name}_{nm}.png", 1)


# ============================================================================ regions -> states
def tidy(M, regions, owner):
    """A sliver of a region that pokes into another strategic region would become a state of one or two
    provinces: hand it to the neighbour that already has land in that strategic region."""
    moved = 0
    for ri, r in enumerate(regions):
        if not r["provinces"] or "home" not in r:
            continue
        groups = defaultdict(list)
        for p in r["provinces"]:
            groups[M.sreg[p]].append(p)
        for sr, ps in groups.items():
            if sr == M.sreg[r["home"]] or len(ps) >= 3:
                continue
            cand = Counter()
            for p in ps:
                for q, bl in M.adj[p].items():
                    rq = owner.get(q)
                    if rq is not None and rq != ri and M.sreg[q] == sr:
                        cand[rq] += bl
            if cand:
                to = cand.most_common(1)[0][0]
                for p in ps:
                    owner[p] = to
                moved += len(ps)
    for r in regions:
        r["provinces"] = []
    for p, ri in owner.items():
        regions[ri]["provinces"].append(p)
    return moved


def split(M, ps, k):
    """cut a group of provinces into k compact, connected parts"""
    ps = sorted(ps)
    if k <= 1 or len(ps) <= 1:
        return [ps]
    xy = np.array([(M.cx[p], M.cy[p]) for p in ps])
    centres = [xy[np.argmin(xy[:, 0] + xy[:, 1])]]
    while len(centres) < k:                                   # farthest point first
        d = np.min([((xy - c) ** 2).sum(1) for c in centres], axis=0)
        centres.append(xy[int(np.argmax(d))])
    centres = np.array(centres)
    w = np.array([M.provs[p]["px"] for p in ps], float)
    for _ in range(12):
        lab = np.argmin(((xy[:, None, :] - centres[None]) ** 2).sum(2), axis=1)
        for j in range(k):
            if (lab == j).any():
                centres[j] = np.average(xy[lab == j], axis=0, weights=w[lab == j])
    part = {p: int(j) for p, j in zip(ps, lab)}
    for _ in range(3):                                        # detached bits join the part they touch
        for j in range(k):
            comps = sorted(components([p for p in ps if part[p] == j], M.adj), key=len, reverse=True)
            for comp in comps[1:]:
                cand = Counter()
                for p in comp:
                    for q, bl in M.adj[p].items():
                        if q in part and part[q] != j:
                            cand[part[q]] += bl
                if cand:
                    to = cand.most_common(1)[0][0]
                    for p in comp:
                        part[p] = to
    out = defaultdict(list)
    for p, j in part.items():
        out[j].append(p)
    return [sorted(v) for v in out.values() if v]


CITY_XY = {}       # victory point province -> where the town really lies (for the previews)
DIRS = ["Eastern", "South-Eastern", "Southern", "South-Western", "Western", "North-Western", "Northern", "North-Eastern"]


def category(pop, urban):
    for limit, a, b in ((600_000, "megalopolis", "megalopolis"), (300_000, "metropolis", "metropolis"),
                        (120_000, "large_city", "large_city"), (60_000, "city", "large_town"),
                        (30_000, "large_town", "town"), (15_000, "town", "rural"), (5_000, "rural", "rural")):
        if pop >= limit:
            return a if urban else b
    return "pastoral"


def industry(playable, C):
    """Workshops per country, not per head: a people's economy grows slower than its numbers
    (2 for Rome's 40 thousand, about 50 for the Persian Empire), half for peoples without towns.
    They are then spread over the states by population, within each state's building slots."""
    by_tag = defaultdict(list)
    for s in playable:
        if not C[s["owner"]]["core"]:
            by_tag[s["owner"]].append(s)
    for tag, sts in by_tag.items():
        tot = sum(s["pop"] for s in sts)
        civ = round(2 * (tot / 40_000) ** 0.65 * (1.0 if C[tag]["urban"] else 0.5))
        if tot >= 15_000:
            civ = max(civ, 1)
        mil = max(1 if tot >= 30_000 else 0, round(civ * 0.35))
        for kind, n in (("arms_factory", mil), ("industrial_complex", civ)):
            for _ in range(n):
                room = [s for s in sts if sum(s["buildings"].get(k, 0) for k in ("arms_factory", "industrial_complex")) < SLOTS[s["category"]]]
                if not room:
                    break
                s = max(room, key=lambda s: (s["pop"] / (s["buildings"].get(kind, 0) + 1), -len(s["provinces"])))
                s["buildings"][kind] = s["buildings"].get(kind, 0) + 1


def make_states(M, core, regions, owner, attach, C):
    states = []
    for s in core["states"]:
        st = dict(s, waste=False, core=True, provinces=list(s["provinces"]))
        sr = M.sreg[s["provinces"][0]]
        st["provinces"] += [p for p in attach.get(s["id"], []) if M.sreg[p] == sr]
        states.append(st)
    for sid, ps in attach.items():                            # islands off Italy in another strategic region
        s = next(x for x in core["states"] if x["id"] == sid)
        groups = defaultdict(list)
        for p in ps:
            if M.sreg[p] != M.sreg[s["provinces"][0]]:
                groups[M.sreg[p]].append(p)
        for sr, g in groups.items():
            states.append(dict(name=f"{s['name']} Islands", owner=s["owner"], provinces=sorted(g), pop=2000,
                               category="pastoral", cores=[s["owner"]], vps=[], ports={},
                               buildings=dict(infrastructure=1), waste=False))
    playable, waste = [], []
    capitals = {}
    seen_tags = set()
    for ri, r in enumerate(regions):
        if not r["provinces"]:
            continue
        c = C[r["owner"]]
        wild = r["wild"]
        density = r["pop"] / len(r["provinces"])              # thinly peopled lands get fewer, bigger states
        cap = 60 if wild else 40 if density < 300 else 28 if density < 600 else 12 if c["urban"] else 16
        parts = []
        groups = defaultdict(list)
        for p in r["provinces"]:
            groups[M.sreg[p]].append(p)
        for sr in sorted(groups):
            parts += split(M, groups[sr], math.ceil(len(groups[sr]) / cap))
        if wild:
            for ps in parts:
                waste.append(dict(name=r["name"], owner=WLD, provinces=ps, pop=1000, category="wasteland",
                                  cores=[], vps=[], ports={}, buildings={}, waste=True))
            continue
        # cities -> provinces of this region
        okm = np.zeros(max(M.provs) + 1, bool)
        okm[r["provinces"]] = True
        part_of = {p: i for i, ps in enumerate(parts) for p in ps}
        vps = defaultdict(list)                               # part -> [prov, value, name]
        ports = defaultdict(dict)
        used = set()
        for ci, (name, lon, lat, vp, port) in enumerate(r["cities"]):
            x, y = to_xy(lon, lat)
            cand = [(d, p) for d, p in M.near(x, y, okm, 60 if ci == 0 else 18) if p not in used]
            if not cand:
                if ci:
                    continue                                  # a lesser town with no province of its own
                cand = [(0.0, r["home"] if r["home"] in part_of else r["provinces"][0])]
            pick = cand[0][1]
            if port:
                coast = [p for d, p in cand if M.provs[p]["coastal"] and d <= cand[0][0] + 20]
                if coast:
                    pick = coast[0]
                else:
                    port = False
            used.add(pick)
            CITY_XY[pick] = (x, y)
            vps[part_of[pick]].append([pick, vp, name])
            if port:
                ports[part_of[pick]][pick] = 3 if vp >= 10 else 2 if vp >= 4 else 1
            if ci == 0:
                home_part = part_of[pick]
        # people
        food = [sum(M.provs[p]["px"] * TERRAIN_FOOD.get(M.provs[p]["terrain"], 0.5) for p in ps) for ps in parts]
        tot_food, tot_vp = sum(food) or 1, sum(v for i in vps for _, v, _ in vps[i])
        hx, hy = np.mean([M.cx[p] for p in parts[home_part]]), np.mean([M.cy[p] for p in parts[home_part]])
        names_used = {r["name"]}
        for i, ps in enumerate(parts):
            share = food[i] / tot_food
            if tot_vp:
                share = 0.55 * share + 0.45 * sum(v for _, v, _ in vps[i]) / tot_vp
            pop = max(1000, int(round(r["pop"] * share, -2)))
            if i == home_part:
                name = r["name"]
            else:
                big = max(vps[i], key=lambda v: v[1]) if vps[i] else None
                if big and big[2] not in names_used and big[1] >= 2:
                    name = big[2]
                else:
                    ang = math.degrees(math.atan2(np.mean([M.cy[p] for p in ps]) - hy,
                                                  np.mean([M.cx[p] for p in ps]) - hx)) % 360
                    k = int((ang + 22.5) // 45) % 8
                    for cand in ([f"{DIRS[k]} {r['name']}", f"Farther {DIRS[k]} {r['name']}"]
                                 + [f"{DIRS[(k + j) % 8]} {r['name']}" for j in (1, 7, 2, 6)]
                                 + [f"{DIRS[k]} {r['name']} {n}" for n in ("II", "III", "IV", "V", "VI", "VII", "VIII")]):
                        name = cand
                        if name not in names_used:
                            break
            names_used.add(name)
            cat = category(pop, c["urban"])
            b = dict(infrastructure=3 if pop >= 300_000 else 2 if (c["urban"] or pop >= 100_000) else 1)
            if c["core"]:                                     # Carthage's outer lands: the yardstick of its heartland
                mil = 1 if pop >= 30_000 else 0
                ic = min(max(0, round(pop / 25_000)), SLOTS[cat] - mil)
                if ic > 0:
                    b["industrial_complex"] = ic
                if mil:
                    b["arms_factory"] = mil
            st = dict(name=name, owner=r["owner"], provinces=ps, pop=pop, category=cat, cores=[r["owner"]],
                      vps=sorted(vps[i], key=lambda v: -v[1]), ports=ports[i], buildings=b, waste=False)
            if i == home_part and r["owner"] not in seen_tags and not c["core"]:
                st["capital"] = True
            playable.append(st)
        seen_tags.add(r["owner"])
    industry(playable, C)
    states += playable + waste
    for i, s in enumerate(states, 1):
        s["id"] = i
    # lakes that sat in a state stay in one: the state of the nearest shore in the same strategic region
    in_state = {p: s for s in states for p in s["provinces"]}
    land_by_sr = defaultdict(list)
    for p in M.land:
        land_by_sr[M.sreg[p]].append(p)
    lost = 0
    for lake in core["lakes_in_states"]:
        if lake in in_state:
            continue
        cand = land_by_sr.get(M.sreg[lake])
        if not cand:
            lost += 1
            continue
        touching = [q for (a, b) in M.border if lake in (a, b) for q in (a, b) if q in M.land and M.sreg[q] == M.sreg[lake]]
        q = touching[0] if touching else min(cand, key=lambda q: M.dist(lake, q))
        in_state[q]["provinces"].append(lake)
        in_state[lake] = in_state[q]
    if lost:
        print(f"WARN: {lost} lakes in strategic regions without land stay outside any state")
    return states


# ============================================================================ colours
HUES = {  # culture -> (hue from, hue to) in degrees
    "celtic": (82, 152), "iberian": (48, 72), "germanic": (176, 204), "northern": (236, 270), "greek": (204, 232),
    "illyrian": (284, 318), "thracian": (326, 352), "scythian": (14, 32), "caucasian": (156, 176),
    "anatolian": (0, 12), "persian": (40, 52), "phoenician": (266, 292), "arabian": (150, 186), "libyan": (24, 40),
    "nilotic": (8, 22), "african": (68, 92),
}


def colour_distance(a, b):
    rm = (a[0] + b[0]) / 2
    dr, dg, db = a[0] - b[0], a[1] - b[1], a[2] - b[2]
    return math.sqrt((2 + rm / 256) * dr * dr + 4 * dg * dg + (2 + (255 - rm) / 256) * db * db)


def pick_colours(M, C, states):
    tag_of = {p: s["owner"] for s in states for p in s["provinces"]}
    near = defaultdict(set)
    for (p, q) in M.border:
        a, b = tag_of.get(p), tag_of.get(q)
        if a and b and a != b:
            near[a].add(b)
            near[b].add(a)
    todo = [t for t, c in C.items() if not c.get("color")]
    for tag in sorted(todo, key=lambda t: (-len(near[t]), t)):
        h0, h1 = HUES[C[tag]["culture"]]
        cands = []
        for i in range(7):
            for s in (0.52, 0.66, 0.82):
                for v in (0.58, 0.72, 0.88):
                    rgb = colorsys.hsv_to_rgb(((h0 + (h1 - h0) * i / 6) % 360) / 360, s, v)
                    cands.append(tuple(int(x * 255) for x in rgb))
        first = [C[t]["color"] for t in near[tag] if C[t].get("color")]
        second = [C[u]["color"] for t in near[tag] for u in near[t] if u != tag and C[u].get("color")]
        salt = sum(ord(ch) for ch in tag)

        def score(col, k):
            s1 = min((colour_distance(col, o) for o in first), default=400)
            s2 = min((colour_distance(col, o) for o in second), default=400)
            return min(s1, 1.6 * s2) + ((salt * 31 + k * 17) % 13) * 0.5      # the tie-break keeps the map varied
        C[tag]["color"] = max(((score(c, k), c) for k, c in enumerate(cands)))[1]


# ============================================================================ roads and supply
def network(M, states):
    """One supply node per playable state (its main town), joined by level-1 'roads' (railways): a tree
    inside every country from its capital, plus one link over every land border between two countries.
    -> (node provinces, list of province chains)"""
    play = [s for s in states if not s["waste"]]
    tag_of = {p: s["owner"] for s in play for p in s["provinces"] if p in M.land}

    def node(s):
        if s["vps"]:
            return s["vps"][0][0]
        land = [p for p in s["provinces"] if p in M.land]
        mx, my = np.mean([M.cx[p] for p in land]), np.mean([M.cy[p] for p in land])
        return min(land, key=lambda p: math.hypot(M.cx[p] - mx, M.cy[p] - my) * TERRAIN_COST.get(M.provs[p]["terrain"], 1.2))

    nodes = {s["id"]: node(s) for s in play}
    by_tag = defaultdict(list)
    for s in sorted(play, key=lambda s: (not s.get("capital"), s["id"])):
        by_tag[s["owner"]].append(nodes[s["id"]])
    used, chains, net = set(), [], {}

    def add(path):
        run = [path[0]]
        for a, b in zip(path, path[1:]):
            e = (min(a, b), max(a, b))
            if e in used:
                if len(run) > 1:
                    chains.append(run)
                run = [b]
            else:
                used.add(e)
                run.append(b)
        if len(run) > 1:
            chains.append(run)

    def spread(sources, tag):
        dist, parent, heap = {}, {}, [(0.0, p, p) for p in sources]
        while heap:
            d, p, par = heapq.heappop(heap)
            if p in dist:
                continue
            dist[p], parent[p] = d, par
            for q in M.adj[p]:
                if q not in dist and tag_of.get(q) == tag:
                    heapq.heappush(heap, (d + M.cost(p, q), q, p))
        return dist, parent

    for tag, todo in by_tag.items():
        todo = list(todo)
        while todo:                                           # one tree per landmass the country holds
            root = todo.pop(0)
            net[root] = tag
            dist, parent = spread([root], tag)
            for t in sorted([t for t in todo if t in dist], key=lambda t: dist[t]):
                path = [t]
                while path[-1] not in net:
                    path.append(parent[path[-1]])
                for p in path:
                    net[p] = tag
                add(path)
                todo.remove(t)
    # links over the borders: the cheapest way between the two road nets
    dist, parent = {}, {}
    for tag in by_tag:
        d, par = spread([p for p, t in net.items() if t == tag], tag)
        dist.update(d)
        parent.update(par)
    best = {}
    for (p, q) in M.border:
        a, b = tag_of.get(p), tag_of.get(q)
        if a and b and a != b and p in dist and q in dist:
            c = dist[p] + M.cost(p, q) + dist[q]
            key = (min(a, b), max(a, b))
            if c < best.get(key, (1e18,))[0]:
                best[key] = (c, p, q)
    for key in sorted(best):
        _, p, q = best[key]
        left, right = [p], [q]
        while parent[left[-1]] != left[-1]:
            left.append(parent[left[-1]])
        while parent[right[-1]] != right[-1]:
            right.append(parent[right[-1]])
        add(left[::-1] + right)
    return sorted(set(nodes.values())), chains


# ============================================================================ flags
def flag_image(tag, c):
    base = tuple(c["color"])
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in base))
    light = tuple(int(v * 255) for v in colorsys.hls_to_rgb(h, min(0.9, l + 0.33), s * 0.6))
    dark = tuple(int(v * 255) for v in colorsys.hls_to_rgb(h, max(0.1, l - 0.28), s))
    gold = (222, 184, 78)
    if colour_distance(base, gold) < 150:                     # gold on gold: use the dark shade instead
        gold = dark
    im = Image.new("RGBA", (82, 52), base + (255,))
    d = ImageDraw.Draw(im)
    seed = sum(ord(ch) * (i + 3) for i, ch in enumerate(tag))
    k = seed % 3
    style = c["flag"]
    if style == "celtic":                                     # a torc, or three dots in a ring
        d.rectangle([0, 0, 81, 6], fill=light)
        d.rectangle([0, 45, 81, 51], fill=light)
        if k == 0:
            d.arc([27, 12, 55, 40], 300, 240, fill=gold, width=5)
            d.ellipse([31, 10, 39, 18], fill=gold)
            d.ellipse([43, 10, 51, 18], fill=gold)
        elif k == 1:
            for ang in (90, 210, 330):
                x, y = 41 + 10 * math.cos(math.radians(ang)), 26 - 10 * math.sin(math.radians(ang))
                d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=gold)
        else:
            d.ellipse([29, 14, 53, 38], outline=gold, width=4)
            d.line([41, 14, 41, 38], fill=gold, width=3)
            d.line([29, 26, 53, 26], fill=gold, width=3)
    elif style == "iberian":
        d.rectangle([0, 26, 81, 51], fill=dark)
        d.polygon([(41, 10), (57, 26), (41, 42), (25, 26)], fill=gold)
        d.rectangle([34, 19, 48, 33], fill=light if k else base)
    elif style == "germanic":                                 # a rune on a dark field
        d.rectangle([0, 0, 81, 51], fill=dark)
        d.rectangle([4, 4, 77, 47], outline=light, width=2)
        d.line([41, 11, 41, 41], fill=light, width=4)
        if k == 0:
            d.line([41, 24, 30, 12], fill=light, width=4)
            d.line([41, 24, 52, 12], fill=light, width=4)
        elif k == 1:
            d.line([41, 11, 30, 22], fill=light, width=4)
            d.line([41, 11, 52, 22], fill=light, width=4)
        else:
            d.line([30, 18, 52, 34], fill=light, width=4)
    elif style == "northern":                                 # a woven band
        pts = [(x, 20 if (x // 8) % 2 else 32) for x in range(0, 90, 8)]
        d.line(pts, fill=light, width=4)
        d.line([(x, 52 - y) for x, y in pts], fill=gold, width=3)
    elif style == "greek":                                    # a shield device
        d.rectangle([0, 0, 81, 51], fill=light)
        d.ellipse([22, 7, 59, 44], fill=base, outline=gold, width=3)
        if tag == "LAK":
            d.line([(33, 36), (41, 14), (49, 36)], fill=gold, width=4)        # the lambda of Lakedaimon
        elif k == 0:
            d.polygon([(41, 14), (49, 34), (33, 34)], fill=gold)
        elif k == 1:                                          # a rayed star
            for ang in range(0, 180, 45):
                dx, dy = 11 * math.cos(math.radians(ang)), 11 * math.sin(math.radians(ang))
                d.line([41 - dx, 25.5 - dy, 41 + dx, 25.5 + dy], fill=gold, width=3)
            d.ellipse([36, 21, 46, 31], fill=gold)
        else:
            d.ellipse([34, 19, 48, 33], fill=gold)
            d.ellipse([38, 23, 44, 29], fill=base)
    elif style == "illyrian":
        d.polygon([(0, 0), (81, 0), (41, 30)], fill=light)
        d.ellipse([35, 32, 47, 44], fill=gold)
    elif style == "thracian":
        d.polygon([(0, 51), (0, 36), (60, 0), (81, 0), (81, 15), (21, 51)], fill=light)
        d.ellipse([8, 6, 26, 24], fill=gold)
        d.ellipse([13, 6, 31, 24], fill=base)
    elif style == "steppe":                                   # an arrow over the grass
        d.rectangle([0, 40, 81, 51], fill=dark)
        d.line([14, 24, 62, 24], fill=gold, width=4)
        d.polygon([(60, 15), (74, 24), (60, 33)], fill=gold)
        d.line([14, 24, 8, 17], fill=gold, width=3)
        d.line([14, 24, 8, 31], fill=gold, width=3)
    elif style == "caucasian":                                # sun over the mountains
        d.polygon([(0, 51), (22, 22), (41, 44), (58, 18), (81, 51)], fill=light)
        d.ellipse([33, 4, 49, 20], fill=gold)
    elif style == "anatolian":                                # a double axe
        d.rectangle([0, 0, 12, 51], fill=light)
        d.rectangle([69, 0, 81, 51], fill=light)
        d.line([41, 8, 41, 44], fill=gold, width=4)
        d.polygon([(41, 20), (27, 12), (27, 30)], fill=gold)
        d.polygon([(41, 20), (55, 12), (55, 30)], fill=gold)
    elif style == "persian":                                  # a winged disc
        d.rectangle([0, 0, 81, 5], fill=dark)
        d.rectangle([0, 46, 81, 51], fill=dark)
        d.polygon([(41, 26), (10, 16), (16, 32)], fill=gold)
        d.polygon([(41, 26), (72, 16), (66, 32)], fill=gold)
        d.ellipse([32, 17, 50, 35], fill=gold, outline=dark, width=2)
    elif style == "punic":                                    # disc and crescent
        d.ellipse([33, 12, 49, 28], fill=gold)
        d.arc([26, 22, 56, 46], 20, 160, fill=gold, width=4)
        d.rectangle([0, 46, 81, 51], fill=light)
    elif style == "arabian":
        d.rectangle([0, 0, 81, 8], fill=light)
        d.ellipse([28, 14, 54, 40], fill=gold)
        d.ellipse([28, 8, 54, 34], fill=base)
        d.ellipse([38, 14, 44, 20], fill=gold)
    elif style == "nilotic":                                  # the sun over the river
        d.rectangle([0, 38, 81, 51], fill=light)
        d.ellipse([30, 9, 52, 31], fill=gold)
        d.rectangle([0, 34, 81, 37], fill=dark)
    elif style == "african":
        for x in (30, 41, 52):
            d.line([x, 8, x, 44], fill=light, width=3)
            d.polygon([(x - 4, 14), (x, 4), (x + 4, 14)], fill=gold)
    else:                                                     # tribal: a slanted band
        d.polygon([(0, 0), (30, 0), (81, 51), (51, 51)], fill=light)
        d.polygon([(0, 51), (0, 30), (21, 51)], fill=gold)
    return im


# ============================================================================ writers
def state_text(s):
    lines = ["state = {", f"\tid = {s['id']}", f"\tname = \"STATE_{s['id']}\"  # {s['name']}",
             f"\tmanpower = {s['pop']}"]
    if s["waste"]:
        lines += ["\tstate_category = wasteland", "\timpassable = yes"]
    else:
        lines.append(f"\tstate_category = {s['category']}")
        lines += R.state_block(s.get("resources"))           # iron, copper, tin, timber, horses, pitch, grain
    lines += ["\thistory = {", f"\t\towner = {s['owner']}"]
    if s["waste"]:
        lines.append("\t\tbuildings = { infrastructure = 0 }")
    else:
        lines += [f"\t\tadd_core_of = {t}" for t in s["cores"]]
        lines += [f"\t\tvictory_points = {{ {p} {v} }}  # {city}" for p, v, city in s["vps"]]
        lines.append("\t\tbuildings = {")
        # roads have 10 levels (round 22): the levels of the sources (1-5 scale) are doubled when written
        lines += [f"\t\t\t{k} = {min(10, v * INFRA_SCALE) if k == 'infrastructure' else v}" for k, v in s["buildings"].items()]
        lines += [f"\t\t\t{p} = {{ naval_base = {lv} }}" for p, lv in sorted(s["ports"].items())]
        lines.append("\t\t}")
    lines += ["\t}", "\tprovinces = {", "\t\t" + " ".join(str(p) for p in s["provinces"]), "\t}",
              "\tlocal_supplies = 0.0", "}"]
    return "\n".join(lines) + "\n"


def safe_name(name):
    return re.sub(r"[^A-Za-z0-9_ ]", "", name).strip() or "state"


def esc(s):
    return s.replace('"', '\\"')


def name_block(items, tabs):
    pad, rows, row = "\t" * tabs, [], []
    for n in items:
        row.append(f'"{n}"' if " " in n else n)
        if len(row) == 8:
            rows.append(pad + " ".join(row))
            row = []
    if row:
        rows.append(pad + " ".join(row))
    return "\n".join(rows)


def write_world(M, C, states):
    # --- wipe what this tool owns
    for rel in ("history/states", "history/countries", "gfx/flags", "localisation/english/replace", "common/bookmarks"):
        if (MOD / rel).is_dir():
            shutil.rmtree(MOD / rel)
    dyn = re.findall(r"^D\d\d = \{.*?^\}", (MOD / "common" / "countries" / "colors.txt").read_text(encoding="utf-8-sig"),
                     re.S | re.M)
    if len(dyn) < 50:
        fail("common/countries/colors.txt lost the colours of the dynamic tags D01.. - restore it from git")
    for fp in (MOD / "common" / "countries").glob("ante_*.txt"):
        fp.unlink()
    # --- resources (tools/resources.py): amounts per state, icons and names
    for line in R.assign(M, states):
        print("resources:", line)
    R.write_files()
    # --- states
    for s in states:
        write(f"history/states/{s['id']}-{safe_name(s['name'])}.txt", state_text(s))
    # --- countries
    capital = {}
    for s in states:
        if s.get("capital"):
            capital[s["owner"]] = s["id"]
    for s in states:
        capital.setdefault(s["owner"], s["id"])
    tags_txt = ["# Generated by tools/world.py"]
    colors_txt = ["#reload countrycolors", ""]
    for tag, c in C.items():
        r, g, b = c["color"]
        tags_txt.append(f'{tag} = "countries/ante_{tag}.txt"')
        write(f"common/countries/ante_{tag}.txt",
              f"graphical_culture = {c['gfx']}_gfx\ngraphical_culture_2d = {c['gfx']}_2d\ncolor = {{ {r} {g} {b} }}\n")
        ui = tuple(min(255, int(v * 1.25)) for v in c["color"])
        colors_txt += [f"{tag} = {{", f"\tcolor = rgb {{ {r} {g} {b} }}",
                       f"\tcolor_ui = rgb {{ {ui[0]} {ui[1]} {ui[2]} }}", "}"]
        ide = GOV_IDEOLOGY[c["gov"]]
        hist = [f"capital = {capital[tag]}", "set_research_slots = 2", "set_stability = 0.6", "set_war_support = 0.3",
                "", "set_politics = {", f"\truling_party = {ide}", '\tlast_election = "240.1.1"',
                "\telection_frequency = 12", f"\telections_allowed = {'yes' if ide == 'democratic' else 'no'}", "}",
                "set_popularities = {"] + [f"\t{k} = {100 if k == ide else 0}" for k in
                                           ("democratic", "fascism", "communism", "neutrality")] + ["}"]
        # starting techs (tools/data/tech_tree.py, tools/tech.py)
        if tag != "WLD":
            techs = TT.START + (TT.START_CIVILISED if c["names"] in TT.CIVILISED or tag == "ROM" else [])
            hist += ["set_technology = {"] + [f"\t{t} = 1" for t in techs] + ["\tpopup = no", "}"]
        # named leaders (common/characters/ante_leaders.txt, written by tools/content.py)
        hist += [f"recruit_character = {tag}_{key}" for t, key, *_ in LEADERS if t == tag]
        # culture national spirit (common/ideas/ante_generic_ideas.txt, tools/content.py); Rome has its own
        if c["names"] != "none":
            hist.append(f"add_ideas = ante_culture_{'roman' if tag == 'ROM' else c['names']}")
        # starting army: history/units/<TAG>_245.txt, written by tools/army.py (the wilds have none)
        if tag != "WLD":
            hist += [f'oob = "{tag}_245"', f'set_naval_oob = "{tag}_245_naval"']
        write(f"history/countries/{tag} - {safe_name(c['name'])}.txt", "\n".join(hist) + "\n", bom=True)
    write("common/country_tags/00_ante_countries.txt", "\n".join(tags_txt) + "\n")
    write("common/countries/colors.txt", "\n".join(colors_txt + dyn) + "\n")
    # --- names
    lists = dict(importlib.import_module("data.names_245").NAMES)
    lists.update(importlib.import_module("data.names_509bc").NAMES)
    calls = importlib.import_module("data.names_245").CALLSIGNS
    out = ["# Generated by tools/world.py from tools/data/names_245.py and names_509bc.py"]
    for tag, c in C.items():
        n = lists[c["names"]]
        out += [f"{tag} = {{", "\tmale = {", "\t\tnames = {", name_block(n["male"], 3), "\t\t}", "\t}",
                "\tfemale = {", "\t\tnames = {", name_block(n["female"], 3), "\t\t}", "\t}",
                "\tsurnames = {", name_block(n["surnames"], 2), "\t}",
                "\tcallsigns = {", name_block(n.get("callsigns", calls), 2), "\t}", "}"]
    write("common/names/ante_names.txt", "\n".join(out) + "\n")
    # --- flags
    import build as B
    for sub in ("", "medium", "small"):
        (MOD / "gfx" / "flags" / sub).mkdir(parents=True, exist_ok=True)
    # The engine prefers TAG_<ideology>.tga over TAG.tga. Where the base game ships such flags for a tag we
    # reuse, ours must exist too - or Rome (ROM) flies the flag of Romania.
    clash = importlib.import_module("data.vanilla_flag_tags").VANILLA_FLAG_TAGS
    for tag, c in C.items():
        im = B.flag_image(tag, c) if c["core"] else flag_image(tag, c)
        names = [tag] + ([f"{tag}_{ide}" for ide in IDEOLOGIES] if tag in clash else [])
        for name in names:
            im.save(MOD / "gfx" / "flags" / f"{name}.tga")
            im.resize((41, 26), Image.LANCZOS).save(MOD / "gfx" / "flags" / "medium" / f"{name}.tga")
            im.resize((10, 7), Image.LANCZOS).save(MOD / "gfx" / "flags" / "small" / f"{name}.tga")
    # --- localisation
    lines = ["l_english:"]
    for tag, c in C.items():
        lines += [f' {tag}:0 "{esc(c["name"])}"', f' {tag}_DEF:0 "{esc(c["name"])}"', f' {tag}_ADJ:0 "{esc(c["adj"])}"']
        for ide in IDEOLOGIES:
            lines += [f' {tag}_{ide}:0 "{esc(c["name"])}"', f' {tag}_{ide}_DEF:0 "{esc(c["name"])}"',
                      f' {tag}_{ide}_ADJ:0 "{esc(c["adj"])}"']
            # party names: without these a reused tag shows the base game's parties (Rome: "PNL")
            short, long = PARTIES.get((tag, ide)) or PARTY_BY_GOV[(c["gov"], ide)] if ide == GOV_IDEOLOGY[c["gov"]] \
                else PARTIES.get((tag, ide)) or PARTY_OTHER[ide]
            lines += [f' {tag}_{ide}_party:0 "{esc(short)}"', f' {tag}_{ide}_party_long:0 "{esc(long)}"']
    write("localisation/english/replace/ante_countries_l_english.yml", "\n".join(lines) + "\n", bom=True)
    lines = ["l_english:"]
    for s in states:
        lines.append(f' STATE_{s["id"]}:0 "{esc(s["name"])}"')
        lines += [f' VICTORY_POINTS_{p}:0 "{esc(city)}"' for p, v, city in s["vps"]]
    write("localisation/english/replace/ante_states_l_english.yml", "\n".join(lines) + "\n", bom=True)
    # --- bookmark
    lines = ["# Generated by tools/world.py", "bookmarks = {", "\tbookmark = {",
             '\t\tname = "ANTE_BOOKMARK_REPUBLIC_NAME"', '\t\tdesc = "ANTE_BOOKMARK_REPUBLIC_DESC"',
             "\t\tdate = 245.1.1.12", '\t\tpicture = "GFX_select_date_1936"',
             f'\t\tdefault_country = "{D.BOOKMARK_COUNTRIES[0]}"', "\t\tdefault = yes", ""]
    def bm_entry(tag, minor=False):
        names = C[tag].get("names", "none")
        idea = "ante_culture_roman" if tag == "ROM" else ("" if names == "none" else f"ante_culture_{names}")
        return [f'\t\t"{tag}" = {{'] + (["\t\t\tminor = yes"] if minor else []) + [   # minor: the lower strip
                f'\t\t\thistory = "ANTE_BOOKMARK_{tag}"',   # text: tools/content.py
                f"\t\t\tideology = {GOV_IDEOLOGY[C[tag]['gov']]}", f"\t\t\tideas = {{ {idea} }}",
                "\t\t\tfocuses = { }", "\t\t}"]
    for tag in D.BOOKMARK_COUNTRIES:                     # the major slots of the selection screen
        lines += bm_entry(tag)
    lines += ['\t\t"---" = {', '\t\t\thistory = "ANTE_BOOKMARK_REPUBLIC_DESC"', "\t\t}"]
    for tag in getattr(D, "BOOKMARK_MINORS", []):         # listed after "---"
        if tag in C:
            lines += bm_entry(tag, minor=True)
    lines += ["",
              "\t\teffect = {", "\t\t\trandomize_weather = 22345 # <- Obligatory in every bookmark !",
              "\t\t}", "\t}", "}"]
    write("common/bookmarks/ante_imperium_bookmarks.txt", "\n".join(lines) + "\n")
    # --- roads and supply
    nodes, chains = network(M, states)
    write("map/supply_nodes.txt", "".join(f"1 {p} \n" for p in nodes))
    write("map/railways.txt", "".join(f"1 {len(ch)} {' '.join(str(p) for p in ch)} \n" for ch in chains))
    print(f"written: {len(states)} states, {len(C)} countries, {len(nodes)} supply nodes, {len(chains)} roads "
          f"({sum(len(ch) - 1 for ch in chains)} province steps)")


# ============================================================================ main
def build_world():
    M = Map()
    core = json.loads(CORE_JSON.read_text(encoding="utf-8"))
    for s in core["states"]:
        s["ports"] = {int(p): v for p, v in s["ports"].items()}
    C = countries()
    regions, owner, attach = assign(M, core)
    moved = tidy(M, regions, owner)
    states = make_states(M, core, regions, owner, attach, C)
    pick_colours(M, C, states)
    owners = Counter(s["owner"] for s in states)
    for tag in list(C):
        if tag not in owners:
            print(f"WARN: {tag} ({C[tag]['name']}) holds no land on this map - left out")
            del C[tag]
    play = [s for s in states if not s["waste"]]
    print(f"{len(M.land)} land provinces: {len(states)} states ({len(play)} playable, {len(states) - len(play)} "
          f"wasteland), {len(C) - 1} countries, {sum(s['pop'] for s in play):,} people; {moved} sliver provinces moved")
    return M, C, regions, states


def draw_preview(M, C, regions, states, out):
    prov_color = {p: tuple(C[s["owner"]]["color"]) for s in states for p in s["provinces"] if p in M.land}
    prov_state = {p: (s["id"], s["owner"]) for s in states for p in s["provinces"] if p in M.land}
    labels = []
    by_tag = defaultdict(list)
    for s in states:
        if not s["waste"]:
            by_tag[s["owner"]] += [p for p in s["provinces"] if p in M.land]
        for p, v, name in s["vps"]:
            x, y = CITY_XY.get(p, (M.cx[p], M.cy[p]))
            labels.append((x, y, name, v, "city"))
    for tag, ps in by_tag.items():
        comp = max(components(ps, M.adj), key=len)
        w = np.array([M.provs[p]["px"] for p in comp], float)
        labels.append((np.average([M.cx[p] for p in comp], weights=w), np.average([M.cy[p] for p in comp], weights=w),
                       tag, 0, "tag"))
    zoom = None
    if "--zoom" in sys.argv:
        zoom = [float(v) for v in sys.argv[sys.argv.index("--zoom") + 1].split(",")]
    preview(M, prov_color, prov_state, labels, Path(out), zoom=zoom)


def main():
    if "--freeze-core" in sys.argv:
        return freeze_core()
    M, C, regions, states = build_world()
    if "--preview" in sys.argv:
        draw_preview(M, C, regions, states, sys.argv[sys.argv.index("--preview") + 1])
        sizes = sorted(((sum(len(s["provinces"]) for s in states if s["owner"] == t), t) for t in C), reverse=True)
        print("biggest:", ", ".join(f"{t} {n}" for n, t in sizes[:30]))
        print("smallest:", ", ".join(f"{t} {n}" for n, t in sizes[-60:]))
        return
    write_world(M, C, states)
    P.main()                                                  # buildings.txt / unitstacks.txt for the new states


if __name__ == "__main__":
    main()


