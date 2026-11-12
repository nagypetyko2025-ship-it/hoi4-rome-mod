"""Static validator for the Ante Imperium mod. Needs no game install.

usage: python tools/validate.py [mod_dir]

Checks the generated map and history files against the engine rules that make
Hearts of Iron IV crash or refuse to load (see README, "Motorszabalyok").
Exit code 1 when an ERROR is found.
"""
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

MOD = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
MAP = MOD / "map"
errors, warnings = [], []


def err(msg):
    errors.append(msg)
    print("ERROR:", msg)


def warn(msg):
    warnings.append(msg)
    print("WARN: ", msg)


def info(msg):
    print("      ", msg)


def strip_comments(t):
    return re.sub(r"#[^\n]*", "", t)


# ---------------------------------------------------------------- bitmaps
def bmp_header(path):
    raw = open(path, "rb").read(54)
    off = struct.unpack("<I", raw[10:14])[0]
    w, h, planes, bpp, comp = struct.unpack("<iiHHI", raw[18:34])
    return dict(w=w, h=h, bpp=bpp, comp=comp, off=off, size=path.stat().st_size)


def read_bmp(path):
    """-> array (h, w) for 8 bit, (h, w, 3) RGB for 24 bit; row 0 = top"""
    hd = bmp_header(path)
    w, h, bpp = hd["w"], abs(hd["h"]), hd["bpp"]
    stride = ((w * bpp // 8) + 3) & ~3
    data = np.fromfile(path, np.uint8, offset=hd["off"], count=stride * h).reshape(h, stride)
    if hd["h"] > 0:
        data = data[::-1]
    if bpp == 8:
        return data[:, :w]
    return data[:, :w * 3].reshape(h, w, 3)[:, :, ::-1]


def load_definitions():
    defs = {}
    for ln, line in enumerate((MAP / "definition.csv").read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        p = line.split(";")
        if len(p) < 8:
            err(f"definition.csv:{ln}: {len(p)} fields")
            continue
        defs[int(p[0])] = dict(rgb=(int(p[1]), int(p[2]), int(p[3])), type=p[4], coastal=p[5] == "true",
                               terrain=p[6], continent=int(p[7]))
    return defs


def province_labels(defs):
    rgb = read_bmp(MAP / "provinces.bmp").astype(np.int32)
    packed = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    keys = np.array(sorted((r << 16 | g << 8 | b, pid) for pid, d in defs.items() if pid for (r, g, b) in [d["rgb"]]))
    idx = np.clip(np.searchsorted(keys[:, 0], packed), 0, len(keys) - 1)
    ok = keys[idx, 0] == packed
    return np.where(ok, keys[idx, 1], 0).astype(np.int32), int((~ok).sum())


def neighbours(labels):
    """4-neighbour province pairs incl. the east-west wrap"""
    a = np.concatenate([labels[:, :-1].ravel(), labels[:-1, :].ravel(), labels[:, -1]])
    b = np.concatenate([labels[:, 1:].ravel(), labels[1:, :].ravel(), labels[:, 0]])
    m = a != b
    pairs = np.unique(np.stack([np.minimum(a[m], b[m]), np.maximum(a[m], b[m])], 1), axis=0)
    n = defaultdict(set)
    for p, q in pairs.tolist():
        n[p].add(q)
        n[q].add(p)
    return n


def check_bitmaps(defs):
    print("== bitmaps")
    hd = bmp_header(MAP / "provinces.bmp")
    W, H = hd["w"], abs(hd["h"])
    info(f"provinces.bmp {W}x{H} {hd['bpp']} bit")
    if hd["bpp"] != 24 or hd["comp"]:
        err("provinces.bmp must be an uncompressed 24 bit BMP")
    if W % 256 or H % 256:
        err(f"map size {W}x{H} is not a multiple of 256")
    if W * H > 13_107_200:
        err(f"map area {W * H} px is above the engine limit (about 13.1 million px)")
    if hd["size"] > 40 * 1024 * 1024:
        err("provinces.bmp is larger than 40 MiB")
    for name in ("heightmap.bmp", "terrain.bmp", "rivers.bmp"):
        h2 = bmp_header(MAP / name)
        if (h2["w"], abs(h2["h"])) != (W, H) or h2["bpp"] != 8 or h2["comp"]:
            err(f"{name}: {h2['w']}x{h2['h']} {h2['bpp']} bit, expected {W}x{H} 8 bit")
        if h2["h"] < 0:
            err(f"{name}: top-down BMP")
    for name in ("cities.bmp", "trees.bmp"):
        h2 = bmp_header(MAP / name)
        if h2["bpp"] != 8 or h2["comp"]:
            err(f"{name}: must be an uncompressed 8 bit BMP")
        info(f"{name} {h2['w']}x{h2['h']}")
    h2 = bmp_header(MAP / "world_normal.bmp")
    info(f"world_normal.bmp {h2['w']}x{h2['h']} {h2['bpp']} bit")
    if h2["bpp"] != 24:
        err("world_normal.bmp must be 24 bit")
    for f in sorted((MAP / "terrain").glob("*.dds")):
        raw = open(f, "rb").read(128)
        if raw[:4] != b"DDS ":
            err(f"{f.name}: not a DDS file")
            continue
        hh, ww = struct.unpack("<II", raw[12:20])
        mips = struct.unpack("<I", raw[28:32])[0]
        fourcc = raw[84:88]
        info(f"terrain/{f.name} {ww}x{hh} mips={mips} fourcc={fourcc!r} bits={struct.unpack('<I', raw[88:92])[0]}")
    # rivers palette indices
    riv = read_bmp(MAP / "rivers.bmp")
    vals = np.unique(riv)
    bad = [int(v) for v in vals if not (v <= 11 or v >= 254)]
    if bad:
        err(f"rivers.bmp uses palette indices outside 0-11/254/255: {bad[:10]}")
    return W, H


def check_provinces(defs, labels, unknown, W, H):
    print("== provinces")
    if unknown:
        err(f"provinces.bmp: {unknown} pixels with a colour that is not in definition.csv")
    ids = sorted(defs)
    if ids != list(range(len(ids))):
        err("definition.csv ids are not contiguous from 0")
    cols = Counter(d["rgb"] for i, d in defs.items() if i)
    dup = [c for c, k in cols.items() if k > 1]
    if dup:
        err(f"definition.csv: {len(dup)} duplicate colours")
    cnt = np.bincount(labels.ravel(), minlength=len(ids))
    missing = [i for i in ids if i and cnt[i] == 0]
    if missing:
        err(f"{len(missing)} provinces of definition.csv have no pixel on the map, e.g. {missing[:10]}")
    info(f"{len(ids) - 1} provinces: " + ", ".join(f"{k} {v}" for k, v in Counter(d['type'] for i, d in defs.items() if i).items()))
    # NGraphics.MINIMUM_PROVINCE_SIZE_IN_PIXELS = 8: "Province X has only N pixels"
    small = [i for i in ids if i and 0 < cnt[i] <= 8]
    if small:
        err(f"{len(small)} provinces of 8 px or less, e.g. {[(i, int(cnt[i])) for i in small[:8]]}")
    # X crossings / 4 corners (interior and across the wrap)
    ext = np.concatenate([labels, labels[:, :1]], axis=1)
    a, b, c, d = ext[:-1, :-1], ext[:-1, 1:], ext[1:, :-1], ext[1:, 1:]
    m1 = (a == d) & (b != a) & (c != a)
    m2 = (b == c) & (a != b) & (d != b)
    m3 = (a != b) & (a != c) & (a != d) & (b != c) & (b != d) & (c != d)
    # a diagonal touch is only a problem when the two pixels are not connected otherwise nearby;
    # the engine complains about every such vertex, so count them all
    if m3.any():
        ys, xs = np.nonzero(m3)
        err(f"{int(m3.sum())} vertices where 4 provinces meet, e.g. {list(zip(xs[:5].tolist(), ys[:5].tolist()))}")
    nx = int(m1.sum() + m2.sum())
    if nx:
        ys, xs = np.nonzero(m1 | m2)
        err(f"{nx} X crossings (pixels touching only diagonally), e.g. {list(zip(xs[:5].tolist(), ys[:5].tolist()))}")
    # connectivity: every province must be one 4-connected piece
    frag = []
    try:
        from scipy import ndimage
    except ImportError:
        ndimage = None
    if ndimage is not None:
        for i, sl in enumerate(ndimage.find_objects(labels), 1):
            if sl is None:
                continue
            _, k = ndimage.label(labels[sl] == i)
            if k > 1:
                frag.append((i, k))
    else:  # numpy only: spread the smallest pixel index through every 4-connected piece
        comp = np.arange(H * W, dtype=np.int64).reshape(H, W)
        for _ in range(20000):
            c = comp.copy()
            for sl_t, sl_s in (((slice(None), slice(1, None)), (slice(None), slice(None, -1))),
                               ((slice(None), slice(None, -1)), (slice(None), slice(1, None))),
                               ((slice(1, None), slice(None)), (slice(None, -1), slice(None))),
                               ((slice(None, -1), slice(None)), (slice(1, None), slice(None)))):
                same = labels[sl_t] == labels[sl_s]
                np.minimum(c[sl_t], np.where(same, c[sl_s], c[sl_t]), out=c[sl_t])
            if (c == comp).all():
                break
            comp = c
        roots = np.unique(comp)
        k = np.bincount(labels.ravel()[roots], minlength=len(ids))
        frag = [(int(i), int(k[i])) for i in np.nonzero(k > 1)[0] if i]
    if frag:
        err(f"{len(frag)} provinces consist of several pieces, e.g. {frag[:10]}")
    return cnt


def check_definitions(defs, neigh):
    print("== definition.csv")
    terrains = {"plains", "forest", "hills", "mountain", "urban", "jungle", "marsh", "desert", "ocean", "lakes",
                "unknown", "water_fjords", "water_shallow_sea", "water_deep_ocean"}
    bad_coast, bad_cont, bad_terr, bad_type = [], [], [], []
    for i, d in defs.items():
        if not i:
            continue
        if d["type"] not in ("land", "sea", "lake"):
            bad_type.append(i)
        if d["terrain"] not in terrains:
            bad_terr.append((i, d["terrain"]))
        if d["type"] == "land":
            real = any(defs[q]["type"] == "sea" for q in neigh[i])
            if real != d["coastal"]:
                bad_coast.append(i)
            if d["continent"] == 0:
                bad_cont.append(i)
            if d["terrain"] in ("ocean", "lakes", "unknown"):
                bad_terr.append((i, d["terrain"]))
        elif d["type"] == "sea":
            real = any(defs[q]["type"] == "land" for q in neigh[i])
            if real != d["coastal"]:
                bad_coast.append(i)
            if d["continent"] != 0:
                bad_cont.append(i)
        else:
            if d["continent"] != 0:
                bad_cont.append(i)
    if bad_type:
        err(f"bad province types: {bad_type[:10]}")
    if bad_terr:
        err(f"{len(bad_terr)} bad terrain entries, e.g. {bad_terr[:10]}")
    if bad_cont:
        err(f"{len(bad_cont)} provinces with a wrong continent (land needs >0, water 0), e.g. {bad_cont[:10]}")
    if bad_coast:
        err(f"{len(bad_coast)} provinces whose coastal flag does not match the bitmap, e.g. {bad_coast[:10]} "
            f"(sea: {sum(defs[i]['type'] == 'sea' for i in bad_coast)}, land: {sum(defs[i]['type'] == 'land' for i in bad_coast)})")
    info("continents used: " + str(sorted(Counter(d["continent"] for d in defs.values()).items())))
    info("terrains used: " + str(sorted(Counter(d["terrain"] for d in defs.values()).items())))


# ---------------------------------------------------------------- states / regions
def load_states():
    states = {}
    for fp in sorted((MOD / "history" / "states").glob("*.txt")):
        t = strip_comments(fp.read_text(encoding="utf-8-sig"))
        if t.count("{") != t.count("}"):
            err(f"{fp.name}: unbalanced braces")
        sid = int(re.search(r"\bid\s*=\s*(\d+)", t).group(1))
        provs = [int(x) for x in re.search(r"provinces\s*=\s*\{([^}]*)\}", t).group(1).split()]
        owner = re.search(r"\bowner\s*=\s*(\w+)", t)
        if sid in states:
            err(f"state id {sid} twice: {fp.name} and {states[sid]['file']}")
        states[sid] = dict(file=fp.name, provinces=provs, owner=owner.group(1) if owner else None,
                           cores=re.findall(r"add_core_of\s*=\s*(\w+)", t),
                           vps=[(int(a), int(b)) for a, b in re.findall(r"victory_points\s*=\s*\{\s*(\d+)\s+([\d.]+)\s*\}", t)],
                           ports=[int(a) for a in re.findall(r"(\d+)\s*=\s*\{\s*naval_base", t)],
                           category=re.search(r"state_category\s*=\s*(\w+)", t).group(1),
                           impassable="impassable" in t, text=t)
    return states


def load_regions():
    regions = {}
    for fp in sorted((MAP / "strategicregions").glob("*.txt")):
        t = strip_comments(fp.read_text(encoding="utf-8-sig"))
        if t.count("{") != t.count("}"):
            err(f"strategicregions/{fp.name}: unbalanced braces")
        rid = int(re.search(r"\bid\s*=\s*(\d+)", t).group(1))
        provs = [int(x) for x in re.search(r"provinces\s*=\s*\{([^}]*)\}", t).group(1).split()]
        if rid in regions:
            err(f"strategic region id {rid} twice")
        regions[rid] = dict(file=fp.name, provinces=provs, weather="weather" in t,
                            periods=len(re.findall(r"\bperiod\s*=", t)),
                            naval_terrain=re.search(r"naval_terrain\s*=\s*(\w+)", t))
    return regions


def check_states(defs, neigh, states, regions, tags):
    print("== states / strategic regions")
    ids = sorted(states)
    if ids != list(range(1, len(ids) + 1)):
        err(f"state ids are not contiguous 1..{len(ids)}")
    prov_state = {}
    for sid, s in states.items():
        if not s["provinces"]:
            err(f"state {sid} has no provinces")
        for p in s["provinces"]:
            if p not in defs or p == 0:
                err(f"state {sid}: province {p} does not exist")
                continue
            if defs[p]["type"] == "sea":
                err(f"state {sid}: province {p} is a sea province")
            if p in prov_state:
                err(f"province {p} is in states {prov_state[p]} and {sid}")
            prov_state[p] = sid
        if not any(defs.get(p, {}).get("type") == "land" for p in s["provinces"]):
            err(f"state {sid} ({s['file']}) has no land province")
        if s["owner"] not in tags:
            err(f"state {sid}: owner {s['owner']} is not a country tag")
        for c in s["cores"]:
            if c not in tags:
                err(f"state {sid}: core of unknown tag {c}")
        for p, v in s["vps"]:
            if p not in s["provinces"]:
                err(f"state {sid}: victory point province {p} is not in the state")
            elif defs[p]["type"] != "land":
                err(f"state {sid}: victory point province {p} is not land")
        for p in s["ports"]:
            if p not in s["provinces"]:
                err(f"state {sid}: naval base province {p} is not in the state")
            elif not defs[p]["coastal"] or defs[p]["type"] != "land":
                err(f"state {sid}: naval base province {p} is not a coastal land province")
    land = [i for i, d in defs.items() if i and d["type"] == "land"]
    nostate = [i for i in land if i not in prov_state]
    if nostate:
        err(f"{len(nostate)} land provinces are in no state, e.g. {nostate[:10]}")
    lakes_out = [i for i, d in defs.items() if d["type"] == "lake" and i not in prov_state]
    info(f"{len(states)} states, {sum(1 for s in states.values() if not s['impassable'])} playable; "
         f"lakes outside states: {len(lakes_out)}")
    # regions
    rids = sorted(regions)
    if rids != list(range(1, len(rids) + 1)):
        err(f"strategic region ids are not contiguous 1..{len(rids)}: {rids[:5]}..{rids[-5:]}")
    prov_reg = {}
    for rid, r in regions.items():
        if not r["provinces"]:
            err(f"strategic region {rid} has no provinces")
        if not r["weather"] or r["periods"] != 12:
            err(f"strategic region {rid}: weather block with {r['periods']} periods (12 needed)")
        for p in r["provinces"]:
            if p not in defs or p == 0:
                err(f"strategic region {rid}: province {p} does not exist")
                continue
            if p in prov_reg:
                err(f"province {p} is in strategic regions {prov_reg[p]} and {rid}")
            prov_reg[p] = rid
    noreg = [i for i in defs if i and i not in prov_reg]
    if noreg:
        err(f"{len(noreg)} provinces are in no strategic region, e.g. {noreg[:10]}")
    for sid, s in states.items():
        rs = {prov_reg.get(p) for p in s["provinces"]}
        if len(rs) != 1:
            err(f"state {sid} spans strategic regions {sorted(rs, key=str)}")
    # naval regions must be contiguous
    for rid, r in regions.items():
        members = set(r["provinces"])
        sea = [p for p in members if defs.get(p, {}).get("type") == "sea"]
        if not sea:
            continue
        comp, stack = {sea[0]}, [sea[0]]
        while stack:
            for q in neigh[stack.pop()]:
                if q in members and q not in comp and defs[q]["type"] == "sea":
                    comp.add(q)
                    stack.append(q)
        if len(comp) != len(sea):
            err(f"strategic region {rid}: sea provinces are not contiguous ({len(sea) - len(comp)} detached)")
        landn = sum(defs[p]["type"] == "land" for p in members)
        if landn and sea:
            pass  # mixed regions exist in vanilla as well
    return prov_state, prov_reg


# ---------------------------------------------------------------- positions
def check_buildings(defs, labels, neigh, states, prov_state, W, H):
    print("== buildings.txt")
    wrong_state, outside, bad_sea, types = Counter(), 0, Counter(), Counter()
    examples = defaultdict(list)
    per_state = defaultdict(Counter)
    naval_prov = defaultdict(set)
    for ln, line in enumerate((MAP / "buildings.txt").read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        p = line.split(";")
        if len(p) != 7:
            err(f"buildings.txt:{ln}: {len(p)} fields")
            continue
        sid, typ, x, y, z, rot, sea = int(p[0]), p[1], float(p[2]), float(p[3]), float(p[4]), float(p[5]), int(p[6])
        types[typ] += 1
        per_state[sid][typ] += 1
        if sid not in states:
            err(f"buildings.txt:{ln}: state {sid} does not exist")
            continue
        px, py = int(x), int(H - z)
        if not (0 <= px < W and 0 <= py < H):
            outside += 1
            continue
        prov = int(labels[py, px])
        if prov_state.get(prov) != sid:
            wrong_state[typ] += 1
            if len(examples[typ]) < 3:
                examples[typ].append((ln, sid, prov, defs[prov]["type"], prov_state.get(prov)))
        if sea and typ not in ("naval_base_spawn", "naval_base", "floating_harbor"):
            bad_sea[typ + ":takes no sea province (vanilla has 0)"] += 1
        if sea:
            if sea not in defs or defs[sea]["type"] != "sea":
                bad_sea[typ + ":not sea"] += 1
            elif sea not in neigh[prov]:
                bad_sea[typ + ":not adjacent"] += 1
            naval_prov[typ].add(prov)
        elif typ in ("naval_base_spawn", "naval_base", "floating_harbor"):
            bad_sea[typ + ":no sea province"] += 1
    info("types: " + ", ".join(f"{k} {v}" for k, v in sorted(types.items())))
    if outside:
        err(f"{outside} building positions outside the map")
    for typ, n in wrong_state.items():
        err(f"{n} '{typ}' positions lie in a province of another state / in water, e.g. (line, state, province, type, real state) {examples[typ]}")
    for k, n in bad_sea.items():
        err(f"{n} buildings with a bad adjacent sea province ({k})")
    # every coastal land province should have a naval base position (ports can be built anywhere)
    coastal = {i for i, d in defs.items() if i and d["type"] == "land" and d["coastal"]}
    for typ in ("naval_base_spawn", "floating_harbor"):
        miss = coastal - naval_prov[typ]
        if miss:
            err(f"{len(miss)} coastal provinces without a '{typ}' position, e.g. {sorted(miss)[:8]}")
    for sid, s in states.items():
        for p in s["ports"]:
            if p not in naval_prov["naval_base_spawn"]:
                err(f"state {sid}: naval base in {p} has no naval_base_spawn position in buildings.txt")
    nob = [sid for sid in states if not per_state[sid]["air_base"]]
    if nob:
        warn(f"{len(nob)} states without an air_base position")


def check_unitstacks(defs, labels, W, H):
    print("== unitstacks.txt")
    arr = np.loadtxt(MAP / "unitstacks.txt", delimiter=";")
    prov, typ, x, z = arr[:, 0].astype(int), arr[:, 1].astype(int), arr[:, 2], arr[:, 4]
    px, py = x.astype(int), (H - z).astype(int)
    out = (px < 0) | (px >= W) | (py < 0) | (py >= H)
    if out.any():
        err(f"{int(out.sum())} unit stack positions outside the map")
    px, py = px.clip(0, W - 1), py.clip(0, H - 1)
    at = labels[py, px]
    wrong = at != prov
    # types 19/20 (disembark / ship in port) may sit on the shore line
    hard = wrong & ~np.isin(typ, (19, 20))
    if hard.any():
        err(f"{int(hard.sum())} unit stack positions outside their province, e.g. provinces {np.unique(prov[hard])[:10].tolist()}")
    if (wrong & ~hard).any():
        warn(f"{int((wrong & ~hard).sum())} port stack positions (type 19/20) outside their province")
    have = defaultdict(set)
    for p, t in zip(prov.tolist(), typ.tolist()):
        have[p].add(t)
    nostack = [i for i in defs if i and 0 not in have[i]]
    if nostack:
        err(f"{len(nostack)} provinces without a unit stack position, e.g. {nostack[:10]}")
    bad = [i for i in have if i not in defs]
    if bad:
        err(f"unit stacks for unknown provinces: {bad[:10]}")
    info(f"{len(arr)} positions, types per land province: {len(have[next(i for i, d in defs.items() if d['type'] == 'land' and i)])}")


def check_supply(defs, neigh, prov_state, states):
    print("== supply nodes / railways")
    nodes = []
    for ln, line in enumerate((MAP / "supply_nodes.txt").read_text(encoding="utf-8").splitlines(), 1):
        p = line.split()
        if not p:
            continue
        if len(p) != 2:
            err(f"supply_nodes.txt:{ln}: '{line}'")
            continue
        prov = int(p[1])
        nodes.append(prov)
        if prov not in defs or defs[prov]["type"] != "land":
            err(f"supply_nodes.txt:{ln}: province {prov} is not land")
        elif states[prov_state[prov]]["impassable"]:
            err(f"supply_nodes.txt:{ln}: province {prov} is in an impassable state")
    dup = [p for p, k in Counter(nodes).items() if k > 1]
    if dup:
        err(f"duplicate supply nodes: {dup}")
    rails = 0
    for ln, line in enumerate((MAP / "railways.txt").read_text(encoding="utf-8").splitlines(), 1):
        p = [int(x) for x in line.split()]
        if not p:
            continue
        rails += 1
        level, n, provs = p[0], p[1], p[2:]
        if n != len(provs):
            err(f"railways.txt:{ln}: count {n} but {len(provs)} provinces")
        if not 1 <= level <= 5:
            err(f"railways.txt:{ln}: level {level}")
        for a in provs:
            if a not in defs or defs[a]["type"] != "land":
                err(f"railways.txt:{ln}: province {a} is not land")
        for a, b in zip(provs, provs[1:]):
            if b not in neigh[a]:
                err(f"railways.txt:{ln}: {a} and {b} are not adjacent")
    info(f"{len(nodes)} supply nodes, {rails} railways")
    return nodes


def check_misc(defs, neigh, states, regions, prov_state, W, H, labels):
    print("== adjacencies / weather / airports / rocket sites")
    lines = (MAP / "adjacencies.csv").read_text(encoding="utf-8").splitlines()
    pairs = set()
    for ln, line in enumerate(lines[1:], 2):
        p = line.split(";")
        if not line.strip():
            continue
        if len(p) < 9:
            err(f"adjacencies.csv:{ln}: {len(p)} fields")
            continue
        f, t, typ, thr = int(p[0]), int(p[1]), p[2], int(p[3])
        if f == -1:
            continue
        for q in (f, t):
            if q not in defs or q == 0:
                err(f"adjacencies.csv:{ln}: province {q} does not exist")
        if typ not in ("", "sea", "impassable", "river", "large_river", "lake"):
            err(f"adjacencies.csv:{ln}: type '{typ}'")
        if thr != -1 and (thr not in defs or thr == 0):
            err(f"adjacencies.csv:{ln}: through province {thr} does not exist")
        if typ == "sea" and thr != -1 and defs.get(thr, {}).get("type") != "sea":
            err(f"adjacencies.csv:{ln}: through province {thr} is not sea")
        key = (min(f, t), max(f, t))
        if key in pairs:
            err(f"adjacencies.csv:{ln}: provinces {f} {t} listed twice")
        pairs.add(key)
        if typ == "impassable" and t not in neigh[f]:
            err(f"adjacencies.csv:{ln}: impassable border between non-adjacent provinces {f} {t}")
        if typ == "sea" and thr != -1 and thr in defs and not (f in neigh[thr] and t in neigh[thr]):
            err(f"adjacencies.csv:{ln}: through province {thr} does not touch both {f} and {t}")
        if typ in ("", "sea") and thr == -1 and t not in neigh[f]:
            err(f"adjacencies.csv:{ln}: connects {f} and {t}, which do not touch, without a through province")
    if not lines or lines[-1].strip() != "-1;-1;-1;-1;-1;-1;-1;-1;-1":
        err("adjacencies.csv must end with the terminator line -1;-1;-1;-1;-1;-1;-1;-1;-1")
    for name in ("definition.csv", "adjacencies.csv"):
        raw = (MAP / name).read_bytes()
        if raw.count(b"\n") != raw.count(b"\r\n"):
            err(f"{name}: needs Windows (CRLF) line endings")
    # weather positions
    seen = defaultdict(set)
    for ln, line in enumerate((MAP / "weatherpositions.txt").read_text(encoding="utf-8").splitlines(), 1):
        p = line.split(";")
        if not line.strip():
            continue
        rid, x, z, size = int(p[0]), float(p[1]), float(p[3]), p[4]
        seen[rid].add(size)
        if rid not in regions:
            err(f"weatherpositions.txt:{ln}: region {rid} does not exist")
        elif not (0 <= x < W and 0 <= H - z < H):
            err(f"weatherpositions.txt:{ln}: outside the map")
        else:
            prov = int(labels[int(H - z), int(x)])
            if prov not in regions[rid]["provinces"]:
                warn(f"weatherpositions.txt:{ln}: position lies outside region {rid}")
    # the engine knows the sizes "large" and "small" only and crashes without one of each
    odd = sorted({s for v in seen.values() for s in v} - {"large", "small"})
    if odd:
        err(f"weatherpositions.txt: unknown sizes {odd} (only 'large' and 'small' exist)")
    miss = [r for r in regions if seen[r] != {"large", "small"}]
    if miss:
        err(f"{len(miss)} strategic regions without large+small weather position, e.g. {miss[:10]}")
    for name in ("airports.txt", "rocketsites.txt"):
        if (MAP / name).exists():
            warn(f"map/{name}: removed from the game in 1.15 (air_base / rocket_site_spawn lines in buildings.txt)")
    # the vanilla tutorial references vanilla state ids: crash after country selection
    fp = MOD / "tutorial" / "tutorial.txt"
    if not fp.exists():
        err("tutorial/tutorial.txt is missing: the vanilla tutorial (vanilla state ids) would be used")
    else:
        t = strip_comments(fp.read_text(encoding="utf-8-sig"))
        if not re.search(r"tutorial\s*=\s*\{", t):
            err("tutorial/tutorial.txt has no tutorial = { } block")
        for m in re.finditer(r"\bstate\s*=\s*(\d+)", t):
            if int(m.group(1)) not in states:
                err(f"tutorial/tutorial.txt: state {m.group(1)} does not exist")


# ---------------------------------------------------------------- countries
def check_countries(states):
    print("== countries")
    tags, files = {}, {}
    dyn = False
    for fp in sorted((MOD / "common" / "country_tags").glob("*.txt")):
        for line in strip_comments(fp.read_text(encoding="utf-8-sig")).splitlines():
            m = re.match(r"\s*(\w+)\s*=\s*\"([^\"]+)\"", line)
            if m:
                tags[m.group(1)] = (m.group(2), "dynamic" in fp.name)
    real = {t for t, (f, d) in tags.items() if not d}
    for t, (f, d) in tags.items():
        if not d and not (MOD / "common" / f).exists():
            err(f"country tag {t}: common/{f} is missing")
        if len(t) != 3:
            err(f"country tag {t} is not 3 characters")
    hist = {}
    for fp in sorted((MOD / "history" / "countries").glob("*.txt")):
        tag = fp.name[:3]
        if tag in hist:
            err(f"two history files for {tag}")
        hist[tag] = fp
        t = strip_comments(fp.read_text(encoding="utf-8-sig"))
        if t.count("{") != t.count("}"):
            err(f"{fp.name}: unbalanced braces")
        m = re.search(r"\bcapital\s*=\s*(\d+)", t)
        if not m:
            err(f"{fp.name}: no capital")
            continue
        cap = int(m.group(1))
        if cap not in states:
            err(f"{fp.name}: capital state {cap} does not exist")
        elif states[cap]["owner"] != tag:
            err(f"{fp.name}: capital state {cap} is owned by {states[cap]['owner']}")
        elif not states[cap]["vps"] and not states[cap]["impassable"]:
            warn(f"{fp.name}: capital state {cap} has no victory point")
        for m in re.finditer(r"\boob\s*=\s*\"([^\"]+)\"", t):
            if not (MOD / "history" / "units" / (m.group(1) + ".txt")).exists():
                err(f"{fp.name}: oob {m.group(1)} missing in history/units")
    for t in real:
        if t not in hist:
            err(f"country {t} has no history file")
        owned = [s for s in states.values() if s["owner"] == t]
        if not owned:
            err(f"country {t} owns no state")
        for size in ("", "medium/", "small/"):
            if not (MOD / "gfx" / "flags" / f"{size}{t}.tga").exists():
                err(f"flag gfx/flags/{size}{t}.tga missing")
    for t in hist:
        if t not in real:
            err(f"history file for unknown tag {t}")
    info(f"{len(real)} countries, {len(tags) - len(real)} dynamic tags")
    return real | {t for t in tags}


def check_flags_and_ai(regions):
    print("== flags / ai areas")
    n = 0
    for sub, size in (("", (82, 52)), ("medium", (41, 26)), ("small", (10, 7))):
        for fp in (MOD / "gfx" / "flags" / sub).glob("*.tga"):
            n += 1
            raw = open(fp, "rb").read(18)
            idlen, cmap, itype = raw[0], raw[1], raw[2]
            w, h, bpp = struct.unpack("<HHB", raw[12:17])
            if itype != 2 or cmap or bpp != 32 or (w, h) != size:
                err(f"{fp.relative_to(MOD)}: must be an uncompressed 32 bit {size[0]}x{size[1]} TGA "
                    f"(type {itype}, {bpp} bit, {w}x{h})")
    info(f"{n} flag files")
    fp = MOD / "common" / "ai_areas" / "default.txt"
    if fp.exists():
        t = strip_comments(fp.read_text(encoding="utf-8-sig"))
        if t.count("{") != t.count("}"):
            err("common/ai_areas/default.txt: unbalanced braces")
        empty = 0
        for m in re.finditer(r"strategic_regions\s*=\s*\{([^}]*)\}", t):
            ids = [int(x) for x in m.group(1).split()]
            empty += not ids
            for i in ids:
                if i not in regions:
                    err(f"common/ai_areas/default.txt: strategic region {i} does not exist")
        info(f"ai areas: {empty} with an empty region list")


def check_text_files():
    print("== script syntax")
    n = 0
    for sub in ("common", "history", "events", "interface", "map/strategicregions", "map/supplyareas"):
        for fp in (MOD / sub).rglob("*"):
            if fp.suffix not in (".txt", ".gui", ".gfx", ".lua") or not fp.is_file():
                continue
            n += 1
            raw = fp.read_bytes()
            t = raw.decode("utf-8-sig", errors="replace")
            body = re.sub(r"--[^\n]*", "", t) if fp.suffix == ".lua" else strip_comments(t)
            body = re.sub(r'"[^"\n]*"', '""', body)
            if body.count("{") != body.count("}"):
                err(f"{fp.relative_to(MOD)}: unbalanced braces")
    for fp in (MOD / "localisation").rglob("*.yml"):
        raw = fp.read_bytes()
        if not raw.startswith(b"\xef\xbb\xbf"):
            err(f"{fp.relative_to(MOD)}: no UTF-8 BOM")
        lines = raw.decode("utf-8-sig").splitlines()
        if not lines or not re.match(r"l_\w+:\s*$", lines[0]):
            err(f"{fp.relative_to(MOD)}: first line must be l_<language>:")
        keys = Counter()
        for ln, line in enumerate(lines[1:], 2):
            if not line.strip() or line.strip().startswith("#"):
                continue
            m = re.match(r' (\S+?):\d* "(.*)"\s*$', line)
            if not m:
                err(f"{fp.relative_to(MOD)}:{ln}: bad line: {line[:60]}")
            else:
                keys[m.group(1)] += 1
        dup = [k for k, c in keys.items() if c > 1]
        if dup:
            warn(f"{fp.relative_to(MOD)}: duplicate keys {dup[:5]}")
    info(f"{n} script files")


def main():
    defs = load_definitions()
    W, H = check_bitmaps(defs)
    labels, unknown = province_labels(defs)
    check_provinces(defs, labels, unknown, W, H)
    neigh = neighbours(labels)
    check_definitions(defs, neigh)
    states = load_states()
    regions = load_regions()
    tags = check_countries(states)
    prov_state, prov_reg = check_states(defs, neigh, states, regions, tags)
    check_buildings(defs, labels, neigh, states, prov_state, W, H)
    check_unitstacks(defs, labels, W, H)
    check_supply(defs, neigh, prov_state, states)
    check_misc(defs, neigh, states, regions, prov_state, W, H, labels)
    check_flags_and_ai(regions)
    check_text_files()
    print(f"\n{len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
