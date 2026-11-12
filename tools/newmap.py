"""Generate the Ante Imperium map: a 3x zoomed crop of the vanilla map (Europe, North Africa,
Near East up to the Urals/Caspian/Arabia) with a new, denser province layout.

usage: python tools/newmap.py            (writes mod/map/** and tools/cache/newmap.*)

Reads vanilla map layers (read-only), writes only inside the mod folder.
Province layout: seeds are placed with a density map (densest in Italy), grown inside
(vanilla strategic region x land/sea/lake) domains, relaxed twice (Lloyd), small ones merged.
Every new province therefore lies in exactly one vanilla strategic region.
"""
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
import mapdata  # noqa: E402

GAME, MOD = mapdata.GAME, mapdata.MOD
VMAP = GAME / "map"
OUT = MOD / "map"
CACHE = MOD / "tools" / "cache"

# crop in vanilla pixels (y from top) and zoom
import os
X0, Y0 = (0, 0) if os.environ.get("ANTE_MAP") in ("vanilla", "identity") else (2530, 0)
import os
# map size and zoom; ANTE_MAP=small -> 2304x2048 (vanilla height) for engine tests
if os.environ.get("ANTE_MAP") == "small":
    SCALE, W, H = 1.6, 2304, 2048
elif os.environ.get("ANTE_MAP") == "wide":
    SCALE, W, H = 1.6, 5632, 2048   # vanilla dimensions, Europe zoomed 1.6x, rest filler
elif os.environ.get("ANTE_MAP") == "identity":
    SCALE, W, H = 1, 5632, 2048   # engine test: vanilla provinces through our writers
elif os.environ.get("ANTE_MAP") == "vanilla":
    SCALE, W, H = 1, 5632, 2048   # engine test: vanilla geometry, our generated content
elif os.environ.get("ANTE_MAP") == "big":
    SCALE, W, H = 3, 4096, 3840   # crashes while loading textures (engine limit) - kept for reference
else:
    SCALE, W, H = 2.4, 3328, 3072
AF = (SCALE / 3) ** 2          # area factor: targets below are tuned for SCALE 3
LF = SCALE / 3                 # length factor
SEA_MAX, LAND_MIN = 89, 95
RNG = np.random.default_rng(509)

LAND, SEA, LAKE = 1, 2, 3


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)


# ------------------------------------------------------------------ sampling helpers
def src_index():
    """nearest vanilla pixel for every output pixel"""
    ys = (np.floor((np.arange(H) + 0.5) / SCALE) + Y0).astype(int).clip(0, 2047)
    xs = (np.floor((np.arange(W) + 0.5) / SCALE) + X0).astype(int).clip(0, 5631)
    return ys, xs


def nearest(arr, ys, xs):
    return arr[np.ix_(ys, xs)]


def resample(img, x0, y0, scale, ow, oh, method):
    """crop img at (x0, y0) and scale so that the result is ow x oh"""
    import math
    bw, bh = math.ceil(ow / scale) + 2, math.ceil(oh / scale) + 2
    x0, y0 = int(x0), int(y0)
    im = img.crop((x0, y0, x0 + bw, y0 + bh)).resize((round(bw * scale), round(bh * scale)), method)
    return im.crop((0, 0, ow, oh))


# ------------------------------------------------------------------ growth
SHIFTS4 = [(0, 1), (0, -1), (1, 0), (-1, 0)]
SHIFTS8 = SHIFTS4 + [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def _sl(d, n):
    """slices for target and source along one axis for shift d"""
    if d > 0:
        return slice(d, n), slice(0, n - d)
    if d < 0:
        return slice(0, n + d), slice(-d, n)
    return slice(0, n), slice(0, n)


def grow(labels, domain, max_iter=10_000):
    """Multi-source region growing: unassigned (-1) pixels take a neighbour's label when the
    neighbour has the same domain value. Pixels with domain < 0 are never assigned."""
    it = 0
    while it < max_iter:
        changed = 0
        shifts = SHIFTS8 if it % 2 else SHIFTS4
        for dy, dx in shifts:
            ty, sy = _sl(dy, H)
            tx, sx = _sl(dx, W)
            tgt = labels[ty, tx]
            src = labels[sy, sx]
            m = (tgt == -1) & (src >= 0) & (domain[ty, tx] == domain[sy, sx])
            n = int(m.sum())
            if n:
                tgt[m] = src[m]
                changed += n
        it += 1
        if not changed:
            break
    return it


# ------------------------------------------------------------------ main steps
def load_vanilla():
    d = mapdata.load_all()
    vids = mapdata.load_ids()
    return d, vids


def strategic_regions_vanilla():
    regs, files = {}, {}
    for fp in (VMAP / "strategicregions").glob("*.txt"):
        t = fp.read_text(encoding="utf-8-sig")
        tn = re.sub(r"#[^\n]*", "", t)
        rid = int(re.search(r"\bid\s*=\s*(\d+)", tn).group(1))
        files[rid] = t
        for p in re.search(r"provinces\s*=\s*\{([^}]*)\}", tn).group(1).split():
            regs[int(p)] = rid
    return regs, files


def build_class_and_vid(d, vids, ys, xs):
    log("sampling vanilla provinces")
    n = max(d["defs"]) + 1
    typ = np.zeros(n, np.int8)
    for p, v in d["defs"].items():
        typ[p] = {"land": LAND, "sea": SEA, "lake": LAKE}[v["type"]]
    vid = nearest(vids, ys, xs).astype(np.int32)
    cls0 = typ[vid]
    # smooth coastlines: argmax of blurred class indicators
    log("smoothing coastlines")
    stack = []
    for k in (LAND, SEA, LAKE):
        im = Image.fromarray(((cls0 == k) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.4 * LF))
        stack.append(np.asarray(im, np.int16))
    stack = np.stack(stack)
    stack[0] += 1  # ties -> land
    cls = (np.argmax(stack, axis=0) + 1).astype(np.int8)
    del stack
    # pixels whose class changed take a vanilla id from neighbours of the same class
    lab = np.where(cls == cls0, vid, -1).astype(np.int32)
    grow(lab, cls.astype(np.int32))
    lab[lab < 0] = vid[lab < 0]
    cls[typ[lab] != cls] = typ[lab][typ[lab] != cls]
    return cls, lab, typ


def area_target(cls, vid, d, ys, xs):
    """desired province area (output pixels) per pixel"""
    vy = ys[:, None].astype(np.float32)
    vx = xs[None, :].astype(np.float32)
    terrain_names = {p: v["terrain"] for p, v in d["defs"].items()}
    n = max(d["defs"]) + 1
    harsh = np.zeros(n, bool)
    for p, t in terrain_names.items():
        if t in ("desert",):
            harsh[p] = True
    area = np.full((H, W), 950.0, np.float32)
    medit = (vx >= 2600) & (vx <= 3420) & (vy >= 560) & (vy <= 1000)
    italy = (vx >= 2880) & (vx <= 3135) & (vy >= 585) & (vy <= 812)
    remote = (vy < 250) | (vx > 3450)
    area = np.where(medit, 520.0, area)
    area = np.where(remote & ~medit, 2400.0, area)
    area = np.where(harsh[vid], 6500.0, area)
    area = np.where(italy, 300.0, area)
    outside = (vx < 2530) | (vx > 3900) | (vy > 1290)
    area = np.where(outside, 25000.0, area)
    # sea: small near coasts, big in open water
    land = Image.fromarray(((cls == LAND) * 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(max(1, round(24 * LF))))
    near = np.asarray(land) > 3
    area = np.where(cls == SEA, np.where(near, 2600.0, 9000.0), area)
    area = np.where((cls == SEA) & italy, 1600.0, area)
    return area * AF


def make_provinces(cls, vid, region_of_vid, typ, area):
    log("seeding provinces")
    reg = region_of_vid[vid]
    domain = (reg * 4 + cls).astype(np.int32)
    # lakes: one province per vanilla lake
    labels = np.full((H, W), -1, np.int32)
    p = RNG.random((H, W), dtype=np.float32) < (1.0 / area)
    p &= cls != LAKE
    seeds = np.argwhere(p)
    log(f"{len(seeds)} seeds")
    lake_mask = cls == LAKE
    lake_ids = np.unique(vid[lake_mask])
    for it in range(3):
        labels[:] = -1
        labels[seeds[:, 0], seeds[:, 1]] = np.arange(len(seeds), dtype=np.int32)
        base = len(seeds)
        # lake provinces keep the vanilla lake grouping
        lake_map = {v: base + i for i, v in enumerate(lake_ids)}
        lk = np.zeros(int(vid.max()) + 1, np.int32) - 1
        for v, i in lake_map.items():
            lk[v] = i
        labels[lake_mask] = lk[vid[lake_mask]]
        n_it = grow(labels, domain)
        # unreachable pockets (islands without a seed): seed them on a grid until none left
        while (labels[(domain >= 0)] == -1).any():
            left = np.argwhere(labels == -1)
            pick = left[(left[:, 0] % 6 == 0) & (left[:, 1] % 6 == 0)]
            if len(pick) == 0:
                pick = left[:1]
            nxt = labels.max() + 1
            labels[pick[:, 0], pick[:, 1]] = np.arange(nxt, nxt + len(pick), dtype=np.int32)
            grow(labels, domain)
        log(f"growth pass {it}: {n_it} iterations, {labels.max() + 1} provinces")
        if it == 2:
            break
        # Lloyd relaxation: move seeds to centroids (if the centroid lies inside the province)
        flat = labels.ravel()
        cnt = np.bincount(flat)
        yy, xx = np.indices((H, W))
        cy = np.bincount(flat, yy.ravel()) / np.maximum(cnt, 1)
        cx = np.bincount(flat, xx.ravel()) / np.maximum(cnt, 1)
        del yy, xx
        nseed = len(seeds)
        cyi, cxi = cy.round().astype(int).clip(0, H - 1), cx.round().astype(int).clip(0, W - 1)
        ok = labels[cyi, cxi] == np.arange(len(cnt))
        new = []
        for i in range(len(cnt)):
            if i >= nseed and i < nseed + len(lake_ids):
                continue  # lakes are not seeds
            if cnt[i] == 0:
                continue
            new.append((cyi[i], cxi[i]) if ok[i] else ((seeds[i][0], seeds[i][1]) if i < nseed else (cyi[i], cxi[i])))
        seeds = np.array([s for s in new if labels[s[0], s[1]] >= 0 and cls[s[0], s[1]] != LAKE])
    return labels, domain


def merge_small(labels, domain, cls, min_land=45 * AF, min_sea=500 * AF, rounds=3):
    for r in range(rounds):
        flat = labels.ravel()
        size = np.bincount(flat)
        dom_of = np.zeros(len(size), np.int64)
        dom_of[flat] = domain.ravel()
        cls_of = np.zeros(len(size), np.int8)
        cls_of[flat] = cls.ravel()
        minsz = np.where(cls_of == SEA, min_sea, min_land)
        small = (size > 0) & (size < minsz) & (cls_of != LAKE)
        if not small.any():
            break
        a = np.concatenate([labels[:, :-1].ravel(), labels[:-1, :].ravel()])
        b = np.concatenate([labels[:, 1:].ravel(), labels[1:, :].ravel()])
        m = (a != b)
        a, b = a[m], b[m]
        a, b = np.concatenate([a, b]), np.concatenate([b, a])
        keep = small[a] & (dom_of[a] == dom_of[b])
        a, b = a[keep], b[keep]
        if len(a) == 0:
            break
        key = a.astype(np.int64) * (len(size) + 1) + b
        uk, uc = np.unique(key, return_counts=True)
        ua, ub = uk // (len(size) + 1), uk % (len(size) + 1)
        order = np.lexsort((-uc, ua))
        ua, ub = ua[order], ub[order]
        first = np.unique(ua, return_index=True)[1]
        remap = np.arange(len(size))
        for x, y in zip(ua[first], ub[first]):
            if remap[y] == x:  # avoid swapping pairs
                continue
            remap[x] = y
        # resolve chains
        for _ in range(5):
            remap = remap[remap]
        labels = remap[labels]
        log(f"merge round {r}: merged {int((remap != np.arange(len(size))).sum())}")
    return labels


def _x_masks(labels):
    a, b = labels[:-1, :-1], labels[:-1, 1:]
    c, d = labels[1:, :-1], labels[1:, 1:]
    m1 = (a == d) & (b != a) & (c != a)   # main diagonal touches only at a corner
    m2 = (b == c) & (a != b) & (d != b)   # anti diagonal
    m3 = (a != b) & (a != c) & (a != d) & (b != c) & (b != d) & (c != d)  # four provinces at one vertex
    return m1, m2 | m3


def fix_x_crossings(labels, domain):
    """HoI4 rejects provinces whose pixels touch only diagonally, and one-pixel spots.
    Repaint offending pixels, preferring a neighbour of the same domain (class + region)."""
    for rnd in range(30):
        m1, m2 = _x_masks(labels)
        n = int(m1.sum() + m2.sum())
        # one-pixel spots: no 4-neighbour shares the label
        lab = labels
        same = np.zeros(lab.shape, bool)
        same[:, 1:] |= lab[:, 1:] == lab[:, :-1]
        same[:, :-1] |= lab[:, :-1] == lab[:, 1:]
        same[1:, :] |= lab[1:, :] == lab[:-1, :]
        same[:-1, :] |= lab[:-1, :] == lab[1:, :]
        lone = ~same
        lone[0, :] = lone[-1, :] = lone[:, 0] = lone[:, -1] = False
        n1 = int(lone.sum())
        if n == 0 and n1 == 0:
            break
        # X: bottom-right pixel of m1 takes the top-right label; for m2 the bottom-left takes top-left
        ys, xs = np.nonzero(m1)
        labels[ys + 1, xs + 1] = labels[ys, xs + 1]
        ys, xs = np.nonzero(m2)
        ok = domain[ys + 1, xs] == domain[ys, xs]
        labels[ys[ok] + 1, xs[ok]] = labels[ys[ok], xs[ok]]
        ys, xs = ys[~ok], xs[~ok]
        ok = domain[ys + 1, xs + 1] == domain[ys + 1, xs]
        labels[ys[ok] + 1, xs[ok] + 1] = labels[ys[ok] + 1, xs[ok]]
        ys, xs = ys[~ok], xs[~ok]
        labels[ys + 1, xs] = labels[ys, xs]
        # lone pixels take the label of a same-domain 4-neighbour (else any neighbour)
        ys, xs = np.nonzero(lone)
        for dy, dx in SHIFTS4:
            ok = domain[ys + dy, xs + dx] == domain[ys, xs]
            labels[ys[ok], xs[ok]] = labels[ys[ok] + dy, xs[ok] + dx]
            ys, xs = ys[~ok], xs[~ok]
        if len(ys):
            labels[ys, xs] = labels[ys, xs + 1]
        log(f"x/lone repair round {rnd}: {n} X, {n1} lone")
    m1, m2 = _x_masks(labels)
    if m1.any() or m2.any():
        log(f"WARN: {int(m1.sum() + m2.sum())} X crossings left")
    return labels


def fix_seam(labels, cls=None, domain=None):
    """The map wraps east-west, so the last and the first pixel column are neighbours too and the
    engine checks X crossings there as well. fix_x_crossings() does not look across that seam:
    repair 4-province vertices and diagonal-only touches there by letting the upper pixel on the
    east edge take the province (and land/sea class) below it."""
    for rnd in range(10):
        a, b = labels[:-1, -1], labels[:-1, 0]
        c, d = labels[1:, -1], labels[1:, 0]
        bad = ((a != b) & (a != c) & (a != d) & (b != c) & (b != d) & (c != d)) \
            | ((a == d) & (b != a) & (c != a)) | ((b == c) & (a != b) & (d != b))
        ys = np.nonzero(bad)[0]
        if not len(ys):
            break
        labels[ys, W - 1] = labels[ys + 1, W - 1]
        for arr in (cls, domain):
            if arr is not None:
                arr[ys, W - 1] = arr[ys + 1, W - 1]
        log(f"seam repair round {rnd}: {len(ys)} vertices")
    return labels


def grow_tiny(labels, cls=None, domain=None, below=10, target=12, forbidden=None):
    """The engine reports provinces of NGraphics.MINIMUM_PROVINCE_SIZE_IN_PIXELS (8) pixels or less
    ("Province X has only N pixels"). These are islets with no neighbour of their own kind to merge
    with, so they take single pixels from their neighbours until they have `target` pixels.
    A pixel is only taken when the donor stays in one piece and no diagonal touch / 4-province
    vertex appears. `forbidden` marks pixels that must stay (positions already written to files)."""
    size = np.bincount(labels.ravel())
    changed = []

    def vertex_ok(y, x):
        a, b, c, d = labels[y, x], labels[y, x + 1], labels[y + 1, x], labels[y + 1, x + 1]
        if a == d and b != a and c != a:
            return False
        if b == c and a != b and d != b:
            return False
        return len({int(a), int(b), int(c), int(d)}) < 4

    def donor_stays_whole(y, x, don):
        win = labels[y - 1:y + 2, x - 1:x + 2] == don
        win[1, 1] = False
        ring = [(0, 1), (1, 0), (1, 2), (2, 1)]
        starts = [p for p in ring if win[p]]
        if not starts:
            return False
        seen, stack = {starts[0]}, [starts[0]]
        while stack:
            cy, cx = stack.pop()
            for dy, dx in SHIFTS4:
                q = (cy + dy, cx + dx)
                if 0 <= q[0] < 3 and 0 <= q[1] < 3 and win[q] and q not in seen:
                    seen.add(q)
                    stack.append(q)
        return all(p in seen for p in starts)

    for i in np.nonzero((size > 0) & (size < below))[0].tolist():
        pix = [tuple(p) for p in np.argwhere(labels == i).tolist()]
        own_cls = cls[pix[0]] if cls is not None else None
        own_dom = domain[pix[0]] if domain is not None else None
        while len(pix) < target:
            cands = {}
            for y, x in pix:
                for dy, dx in SHIFTS4:
                    q = (y + dy, x + dx)
                    if 2 <= q[0] < H - 2 and 2 <= q[1] < W - 2 and labels[q] != i:
                        cands[q] = cands.get(q, 0) + 1
            done = False
            for (y, x), _ in sorted(cands.items(), key=lambda kv: (-kv[1], kv[0])):
                don = int(labels[y, x])
                if size[don] < 4 * target or (forbidden is not None and forbidden[y, x]):
                    continue
                if not donor_stays_whole(y, x, don):
                    continue
                labels[y, x] = i
                if all(vertex_ok(vy, vx) for vy in (y - 1, y) for vx in (x - 1, x)):
                    size[don] -= 1
                    size[i] += 1
                    pix.append((y, x))
                    changed.append((y, x))
                    if cls is not None:
                        cls[y, x] = own_cls
                    if domain is not None:
                        domain[y, x] = own_dom
                    done = True
                    break
                labels[y, x] = don
            if not done:
                log(f"WARN: province {i} stays at {len(pix)} px (no pixel can be taken safely)")
                break
    if changed:
        log(f"grew tiny provinces by {len(changed)} px")
    return labels, changed


def absorb_enclosed_sea(labels, cls, domain):
    """Sea provinces without any sea neighbour (lagoons cut off by smoothing) join the land
    province they share the longest border with."""
    for _ in range(3):
        n = int(labels.max()) + 1
        pcls = majority(labels, cls.astype(np.int64), n - 1)
        a = np.concatenate([labels[:, :-1].ravel(), labels[:-1, :].ravel()])
        b = np.concatenate([labels[:, 1:].ravel(), labels[1:, :].ravel()])
        m = a != b
        a, b = a[m], b[m]
        a, b = np.concatenate([a, b]), np.concatenate([b, a])
        sea_nb = np.zeros(n, bool)
        sea_nb[a[(pcls[a] == SEA) & (pcls[b] == SEA)]] = True
        enclosed = (pcls == SEA) & ~sea_nb
        enclosed[0] = False
        sel = enclosed[a] & (pcls[b] == LAND)
        if not sel.any():
            break
        key = a[sel].astype(np.int64) * n + b[sel]
        uk, uc = np.unique(key, return_counts=True)
        ua, ub = uk // n, uk % n
        order = np.lexsort((-uc, ua))
        ua, ub = ua[order], ub[order]
        first = np.unique(ua, return_index=True)[1]
        remap = np.arange(n)
        remap[ua[first]] = ub[first]
        moved = np.isin(labels, ua[first])
        labels = remap[labels]
        cls[moved] = LAND
        # moved pixels inherit the domain of the province they joined
        ys, xs = np.nonzero(moved)
        for dy, dx in SHIFTS4:
            yy, xx = (ys + dy).clip(0, H - 1), (xs + dx).clip(0, W - 1)
            ok = (labels[yy, xx] == labels[ys, xs]) & ~moved[yy, xx]
            domain[ys[ok], xs[ok]] = domain[yy[ok], xx[ok]]
        log(f"absorbed {len(first)} enclosed sea provinces")
    return labels


def components(labels):
    """4-connected component id per pixel (min pixel index of the component)"""
    comp = np.arange(H * W, dtype=np.int64).reshape(H, W)
    for _ in range(5000):
        c = comp.copy()
        for dy, dx in SHIFTS4:
            ty, sy = _sl(dy, H)
            tx, sx = _sl(dx, W)
            same = labels[ty, tx] == labels[sy, sx]
            np.minimum(c[ty, tx], np.where(same, c[sy, sx], c[ty, tx]), out=c[ty, tx])
        if (c == comp).all():
            break
        comp = c
    return comp


def drop_fragments(labels, cls):
    """Every province keeps only its largest 4-connected piece; the other pieces are regrown
    from neighbouring provinces of the same class (any class as a last resort)."""
    for rnd in range(12):  # regrowing can cut another province in two, so repeat until nothing is left
        comp = components(labels)
        key = labels.ravel().astype(np.int64) * (H * W) + comp.ravel()
        uk, uc = np.unique(key, return_counts=True)
        ul = uk // (H * W)
        if len(np.unique(ul)) == len(ul):
            break
        if rnd == 11:
            log(f"WARN: {len(ul) - len(np.unique(ul))} province fragments left (run tools/validate.py)")
            break
        order = np.lexsort((-uc, ul))
        uk, ul = uk[order], ul[order]
        first = np.unique(ul, return_index=True)[1]
        keep = np.zeros(len(uk), bool)
        keep[first] = True
        bad_keys = uk[~keep]
        bad = np.isin(key, bad_keys).reshape(H, W)
        log(f"fragments round {rnd}: {len(bad_keys)} pieces, {int(bad.sum())} px")
        labels = labels.copy()
        labels[bad] = -1
        grow(labels, cls.astype(np.int32))
        left = labels < 0
        if left.any():
            grow(labels, np.zeros((H, W), np.int32))
    return labels


def renumber(labels):
    u, inv = np.unique(labels, return_inverse=True)
    return (inv.reshape(labels.shape) + 1).astype(np.int32), len(u)


def province_colors(n):
    cols = set()
    out = np.zeros((n + 1, 3), np.uint8)
    rng = np.random.default_rng(245)
    i = 1
    while i <= n:
        c = tuple(int(v) for v in rng.integers(1, 255, 3))
        if c in cols:
            continue
        cols.add(c)
        out[i] = c
        i += 1
    return out


def majority(labels, values, n, ignore=None):
    key = labels.ravel().astype(np.int64) * (int(values.max()) + 1) + values.ravel()
    if ignore is not None:
        key = key[values.ravel() != ignore]
    uk, uc = np.unique(key, return_counts=True)
    ul, uv = uk // (int(values.max()) + 1), uk % (int(values.max()) + 1)
    order = np.lexsort((-uc, ul))
    ul, uv = ul[order], uv[order]
    first = np.unique(ul, return_index=True)[1]
    out = np.zeros(n + 1, np.int64)
    out[ul[first]] = uv[first]
    return out


# ------------------------------------------------------------------ layer writers
def save_bmp8(path, arr, src_path):
    """8-bit paletted BMP with the exact palette bytes and header style of a vanilla file."""
    import struct
    raw = open(src_path, "rb").read()
    off = struct.unpack("<I", raw[10:14])[0]
    pal = raw[54:off]
    h, w = arr.shape
    stride = (w + 3) & ~3
    rows = np.zeros((h, stride), np.uint8)
    rows[:, :w] = arr[::-1]
    body = rows.tobytes()
    hdr = struct.pack("<IiiHHIIiiII", 40, w, h, 1, 8, 0, len(body), 2834, 2834, 0, 0)
    fh = b"BM" + struct.pack("<IHHI", 14 + 40 + len(pal) + len(body), 0, 0, 14 + 40 + len(pal))
    with open(path, "wb") as f:
        f.write(fh + hdr + pal + body)


def write_layers(cls, ys, xs):
    log("writing heightmap/terrain/cities/trees/normal/colormaps")
    hm = Image.open(VMAP / "heightmap.bmp")
    h = np.asarray(resample(hm, X0, Y0, SCALE, W, H, Image.BICUBIC))
    h = h.astype(np.int16)
    h = np.where(cls == LAND, np.maximum(h, LAND_MIN), np.minimum(h, SEA_MAX)).astype(np.uint8)
    Image.fromarray(h, "L").save(OUT / "heightmap.bmp")
    for name in ("terrain.bmp", "cities.bmp"):
        src = Image.open(VMAP / name)
        arr = nearest(np.asarray(src), ys, xs)
        save_bmp8(OUT / name, arr, VMAP / name)
    # trees: same ratio to the map as vanilla
    tr = Image.open(VMAP / "trees.bmp")
    rx, ry = 5632 / tr.width, 2048 / tr.height
    tw, th = round(W / rx), round(H / ry)
    tim = resample(tr, X0 / rx, Y0 / ry, SCALE, tw, th, Image.NEAREST)
    save_bmp8(OUT / "trees.bmp", np.asarray(tim), VMAP / "trees.bmp")
    # normal map: half resolution
    nm = Image.open(VMAP / "world_normal.bmp")
    resample(nm, X0 / 2, Y0 / 2, SCALE, W // 2, H // 2, Image.BICUBIC).save(OUT / "world_normal.bmp")
    # colormaps (half resolution)
    (OUT / "terrain").mkdir(parents=True, exist_ok=True)
    cm = Image.open(VMAP / "terrain" / "colormap_rgb_cityemissivemask_a.dds")
    resample(cm, X0 / 2, Y0 / 2, SCALE, W // 2, H // 2, Image.BICUBIC).save(
        OUT / "terrain" / "colormap_rgb_cityemissivemask_a.dds")
    for lod in range(3):
        wm = Image.open(VMAP / "terrain" / f"colormap_water_{lod}.dds")
        f = 2 ** (lod + 1)
        wim = resample(wm, X0 / f, Y0 / f, SCALE, W // f, H // f, Image.BICUBIC).convert("RGBA")
        wim.save(OUT / "terrain" / f"colormap_water_{lod}.dds", pixel_format="DXT5")


def write_rivers(cls):
    log("rivers")
    rv = Image.open(VMAP / "rivers.bmp")
    pal = rv.getpalette()
    src = np.asarray(rv)
    out = np.where(cls == LAND, 255, 254).astype(np.uint8)
    import math
    cw, ch = math.ceil(W / SCALE) + 1, math.ceil(H / SCALE) + 1
    crop = src[Y0:Y0 + ch, X0:X0 + cw]
    ch, cw = crop.shape
    river = crop < 12
    ry, rx = np.nonzero(river)

    def ctr(v):
        return int((v + 0.5) * SCALE)

    def put(y, x, v):
        if 0 <= y < H and 0 <= x < W:
            out[y, x] = v

    for y, x in zip(ry, rx):
        put(ctr(y), ctr(x), crop[y, x])
    for (dy, dx) in ((0, 1), (1, 0)):
        both = river[:ch - dy, :cw - dx] & river[dy:, dx:]
        for y, x in zip(*np.nonzero(both)):
            a, b = int(crop[y, x]), int(crop[y + dy, x + dx])
            v = max(a, b) if min(a, b) < 3 else min(a, b)
            if v < 3:
                v = 3
            if dx:
                for xx in range(ctr(x) + 1, ctr(x + 1)):
                    put(ctr(y), xx, v)
            else:
                for yy in range(ctr(y) + 1, ctr(y + 1)):
                    put(yy, ctr(x), v)
    out[(out < 12) & (cls != LAND)] = 254
    repair_rivers(out, cls)
    save_bmp8(OUT / "rivers.bmp", out, VMAP / "rivers.bmp")


def repair_rivers(out, cls, min_px=8):
    """Make every river system of the (upscaled, cropped) river layer valid, in place.

    Engine rules: a river is a 1 px wide, 4-connected line; every connected system has exactly
    ONE source pixel (index 0) at an open end; a tributary's last pixel before the junction is a
    flow-in marker (1), a branch leaving the river starts with a flow-out marker (2).
    Cropping the map, coast smoothing and lakes cut vanilla rivers apart, which leaves systems
    without a source, stray pixels, loops and diagonal contacts. Those are removed or completed."""
    def bg(p):
        return 255 if cls[p] == LAND else 254

    def neighbours(p, pix):
        y, x = p
        return [q for q in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)) if q in pix]

    # rivers must not run off the bitmap: clear a two pixel frame, the cut ends are repaired below
    frame = np.zeros(out.shape, bool)
    frame[:2] = frame[-2:] = True
    frame[:, :2] = frame[:, -2:] = True
    frame &= out < 12
    out[frame] = np.where(cls[frame] == LAND, 255, 254)
    stats = dict(edge=int(frame.sum()), diagonal=0, loops=0, dropped=0, sources=0, markers=0, moved=0)
    for _ in range(20):
        changed = 0
        pix = {tuple(p) for p in np.argwhere(out < 12).tolist()}
        # 1. two river pixels touching only diagonally: drop the one with fewer river neighbours
        for (y, x) in sorted(pix):
            for q in ((y + 1, x + 1), (y + 1, x - 1)):
                if q in pix and (y, x) in pix and (y, q[1]) not in pix and (q[0], x) not in pix:
                    a, b = (y, x), q
                    kill = a if len(neighbours(a, pix)) <= len(neighbours(b, pix)) else b
                    if out[kill] < 3 and out[b if kill == a else a] >= 3:
                        kill = b if kill == a else a   # keep sources and markers
                    out[kill] = bg(kill)
                    pix.discard(kill)
                    stats["diagonal"] += 1
                    changed += 1
        # 2. connected systems
        seen = set()
        for start in sorted(pix):
            if start in seen or start not in pix:
                continue
            comp, stack, parent = [start], [start], {start: None}
            seen.add(start)
            cycle_edge = None
            while stack:
                p = stack.pop()
                for q in neighbours(p, pix):
                    if q not in parent:
                        parent[q] = p
                        seen.add(q)
                        comp.append(q)
                        stack.append(q)
                    elif parent[p] != q and parent.get(q) != p and cycle_edge is None:
                        cycle_edge = (p, q)
            if len(comp) < min_px:                       # stray pixels and stumps
                for p in comp:
                    out[p] = bg(p)
                    pix.discard(p)
                stats["dropped"] += 1
                changed += 1
                continue
            if cycle_edge is not None:                   # a loop: cut it at a plain river pixel
                path, p = [], cycle_edge[0]
                while p is not None:
                    path.append(p)
                    p = parent[p]
                anc = set(path)
                other, p = [], cycle_edge[1]
                while p is not None and p not in anc:
                    other.append(p)
                    p = parent[p]
                ring = path[:path.index(p) + 1] + other if p is not None else path + other
                plain = [c for c in ring if out[c] >= 3 and len(neighbours(c, pix)) == 2] or ring
                cut = plain[len(plain) // 2]
                out[cut] = bg(cut)
                pix.discard(cut)
                stats["loops"] += 1
                changed += 1
                continue                                 # re-examine the pieces in the next pass
            deg = {p: len(neighbours(p, pix)) for p in comp}
            # 3. junctions: every branch but two (the main channel) needs a marker next to the junction
            for j in [p for p in comp if deg[p] >= 3]:
                nb = neighbours(j, pix)
                # upscaling leaves the marker a few pixels up its branch: pull it next to the junction
                for q in nb:
                    if out[q] in (1, 2):
                        continue
                    prev, cur = j, q
                    for _step in range(4):
                        if deg.get(cur, 0) != 2:
                            break
                        prev, cur = cur, next(r for r in neighbours(cur, pix) if r != prev)
                        if out[cur] in (1, 2) and deg.get(cur, 0) == 2:
                            out[q], out[cur] = out[cur], (out[q] if out[q] >= 3 else 3)
                            stats["moved"] += 1
                            changed += 1
                            break
                plain = [q for q in nb if out[q] >= 3 or out[q] == 0]
                need = len(plain) - 2
                if need <= 0:
                    continue

                def reach(q):                            # length of the branch leaving j through q
                    n, prev, cur = 1, j, q
                    while deg.get(cur, 0) == 2 and n < 100000:
                        prev, cur = cur, next(r for r in neighbours(cur, pix) if r != prev)
                        n += 1
                    return n

                for q in sorted(plain, key=reach)[:need]:
                    if out[q] == 0 or deg[q] == 1:       # a one-pixel tributary: remove it
                        out[q] = bg(q)
                        pix.discard(q)
                    else:
                        out[q] = 1
                    stats["markers"] += 1
                    changed += 1
            # a marker whose junction is gone (the other river was cut away) is an ordinary river pixel
            for p in comp:
                if p in pix and out[p] in (1, 2) and not any(len(neighbours(q, pix)) >= 3 for q in neighbours(p, pix)):
                    widths = [int(out[q]) for q in neighbours(p, pix) if out[q] >= 3]
                    out[p] = min(widths) if widths else 3
                    stats["markers"] += 1
                    changed += 1
            # 4. exactly one source
            srcs = [p for p in comp if p in pix and out[p] == 0]
            for p in srcs[1:]:
                out[p] = 3
                changed += 1
            if not srcs:
                ends = [p for p in comp if p in pix and len(neighbours(p, pix)) == 1]
                if not ends:
                    continue

                def score(e):
                    prev, cur = None, e
                    while len(neighbours(cur, pix)) <= 2:
                        nxt = [r for r in neighbours(cur, pix) if r != prev]
                        if not nxt:
                            break
                        prev, cur = cur, nxt[0]
                    branch = prev is not None and len(neighbours(cur, pix)) >= 3 and out[prev] in (1, 2)
                    y, x = e
                    near = cls[max(0, y - 3):y + 4, max(0, x - 3):x + 4]
                    water = 2 if (near == SEA).any() else (1 if (near == LAKE).any() else 0)
                    # the head of the main channel: not a tributary, far from the sea, narrow
                    return (branch, water, int(out[e]), e)

                head = min(ends, key=score)
                out[head] = 0
                stats["sources"] += 1
                changed += 1
        if not changed:
            break
    log(f"rivers repaired: {stats}")
    return stats


def write_definitions(labels, n, cls, vid, d, colors, typ):
    log("definitions / province stats")
    flat = labels.ravel()
    cnt = np.bincount(flat, minlength=n + 1)
    yy, xx = np.indices((H, W))
    cy = np.bincount(flat, yy.ravel(), minlength=n + 1) / np.maximum(cnt, 1)
    cx = np.bincount(flat, xx.ravel(), minlength=n + 1) / np.maximum(cnt, 1)
    del yy, xx
    pcls = majority(labels, cls.astype(np.int64), n).astype(np.int8)
    # vanilla origin: only pixels whose vanilla type matches the province type count
    pvid = majority(labels, np.where(typ[vid] == pcls[labels], vid, 0).astype(np.int64), n, ignore=0)
    fallback = majority(labels, vid.astype(np.int64), n)
    pvid = np.where(pvid == 0, fallback, pvid)
    # adjacency
    a = np.concatenate([labels[:, :-1].ravel(), labels[:-1, :].ravel(), labels[:, -1]])
    b = np.concatenate([labels[:, 1:].ravel(), labels[1:, :].ravel(), labels[:, 0]])  # east-west wrap
    m = a != b
    pairs = np.unique(np.stack([np.minimum(a[m], b[m]), np.maximum(a[m], b[m])], 1), axis=0)
    neigh = [[] for _ in range(n + 1)]
    for p, q in pairs:
        neigh[p].append(int(q))
        neigh[q].append(int(p))
    coastal = np.zeros(n + 1, bool)
    for p, q in pairs:
        # like vanilla, both sides are coastal: the land province and the sea province it touches
        if {int(pcls[p]), int(pcls[q])} == {LAND, SEA}:
            coastal[p] = coastal[q] = True
    lines = ["0;0;0;0;land;false;unknown;0"]
    provs = {}
    for i in range(1, n + 1):
        v = int(pvid[i])
        vd = d["defs"].get(v, {})
        t = {LAND: "land", SEA: "sea", LAKE: "lake"}[int(pcls[i])]
        terrain = vd.get("terrain", "plains") if t == "land" else ("ocean" if t == "sea" else "lakes")
        if t == "land" and terrain in ("ocean", "lakes", "unknown"):
            terrain = "plains"
        cont = vd.get("continent", 1) if t == "land" else 0
        r, g, b_ = colors[i]
        lines.append(f"{i};{r};{g};{b_};{t};{'true' if coastal[i] else 'false'};{terrain};{cont}")
        provs[i] = {"type": t, "coastal": bool(coastal[i]), "terrain": terrain, "continent": int(cont),
                    "x": round(float(cx[i]), 1), "y": round(float(cy[i]), 1), "px": int(cnt[i]),
                    "vid": v, "n": sorted(neigh[i])}
    # the engine wants Windows line endings in this file (kept as-is by .gitattributes)
    (OUT / "definition.csv").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\r\n")
    inside_points(labels, provs, cx, cy)
    return provs


def inside_points(labels, provs, cx, cy, k=8):
    """Positions guaranteed to lie inside each province (centroids may not):
    'c' = interior pixel closest to the centroid, 'pts' = up to k random interior pixels."""
    log("inside points")
    inner = np.ones(labels.shape, bool)
    for dy, dx in SHIFTS4:
        ty, sy = _sl(dy, H)
        tx, sx = _sl(dx, W)
        inner[ty, tx] &= labels[ty, tx] == labels[sy, sx]
    ys, xs = np.nonzero(inner)
    lab = labels[ys, xs]
    have = np.zeros(len(cx), bool)
    have[lab] = True
    if not have[1:].all():  # very thin provinces: any of their pixels
        miss = np.isin(labels, np.nonzero(~have)[0])
        my, mx = np.nonzero(miss)
        ys, xs, lab = np.concatenate([ys, my]), np.concatenate([xs, mx]), np.concatenate([lab, labels[my, mx]])
    dist = (xs - cx[lab]) ** 2 + (ys - cy[lab]) ** 2
    order = np.lexsort((dist, lab))
    lo, xo, yo = lab[order], xs[order], ys[order]
    first = np.unique(lo, return_index=True)[1]
    for j in first:
        provs[int(lo[j])]["c"] = [float(xo[j]) + 0.5, float(yo[j]) + 0.5]
    rnd = RNG.permutation(len(lab))
    order = rnd[np.argsort(lab[rnd], kind="stable")]
    sl = lab[order]
    starts = np.searchsorted(sl, np.arange(len(cx)))
    ends = np.searchsorted(sl, np.arange(len(cx)), side="right")
    for i in provs:
        sel = order[starts[i]:min(ends[i], starts[i] + k)]
        provs[i]["pts"] = [[float(xs[s]) + 0.5, float(ys[s]) + 0.5] for s in sel] or [provs[i]["c"]]


def drop_empty_ai_areas(text, continents_on_map):
    """Remove the AI areas (common/ai_areas) that cover nothing on this map: no strategic region
    left after the translation and no continent that has land here (Pacific, Japan, America ...).
    Returns (new text, list of dropped area names)."""
    m = re.search(r"areas\s*=\s*\{", text)
    out, pos, depth, start, dropped = [text[:m.end()]], m.end(), 1, None, []
    j, n = m.end(), len(text)
    while j < n:
        ch = text[j]
        if ch == "#":
            j = text.find("\n", j)
            j = n if j < 0 else j
            continue
        if depth == 1 and start is None and (ch.isalnum() or ch == "_"):
            start = j
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 1 and start is not None:
                block = text[start:j + 1]
                body = re.sub(r"#[^\n]*", "", block)
                regs = re.search(r"strategic_regions\s*=\s*\{([^}]*)\}", body)
                conts = re.search(r"continents\s*=\s*\{([^}]*)\}", body)
                covered = bool(regs and regs.group(1).split()) or \
                    bool(conts and set(conts.group(1).split()) & set(continents_on_map))
                out.append(text[pos:start])
                if covered:
                    out.append(block)
                else:
                    dropped.append(re.match(r"\w+", block).group(0))
                pos, start = j + 1, None
            elif depth == 0:
                break
        j += 1
    out.append(text[pos:])
    return "".join(out), dropped


def sea_region_ids(d, region_of_vid):
    """vanilla strategic regions that are naval regions (they hold sea provinces)"""
    return {int(region_of_vid[vp]) for vp, v in d["defs"].items() if v["type"] == "sea"}


def settle_regions(provs, sea_regions):
    """Give every province a strategic region of its own kind, in provs[i]["vreg"].

    Vanilla never mixes the two kinds: a naval region holds sea provinces only, a land region land
    and lakes only. The new province layout breaks that (islets grown on vanilla sea, sea provinces
    grown on vanilla land), and a land province inside a naval region crashes the game at start.
    1. every province in a region of the wrong kind moves, together with the touching provinces in
       the same situation, to the region of the nearest province of its own kind;
    2. naval regions must be contiguous ("fractioned" map error): detached groups of sea provinces
       join the naval region they touch."""
    from collections import Counter

    def is_sea(i):
        return provs[i]["type"] == "sea"

    def wrong(i):
        return is_sea(i) != (provs[i]["vreg"] in sea_regions)

    def nearest_region(comp, want_sea):
        seen, frontier = set(comp), list(comp)
        while frontier:
            nxt = []
            for i in frontier:
                for q in provs[i]["n"]:
                    if q in seen:
                        continue
                    seen.add(q)
                    if is_sea(q) == want_sea and not wrong(q):
                        return provs[q]["vreg"]
                    nxt.append(q)
            frontier = nxt
        return None

    stats = dict(land_out_of_naval=0, sea_out_of_land=0, sea_reattached=0, unresolved=0)
    todo = sorted(i for i in provs if wrong(i))
    todo_set, seen = set(todo), set()
    for s in todo:
        if s in seen:
            continue
        comp, stack = [s], [s]
        seen.add(s)
        while stack:
            for q in provs[stack.pop()]["n"]:
                if q in todo_set and q not in seen and is_sea(q) == is_sea(s):
                    seen.add(q)
                    comp.append(q)
                    stack.append(q)
        r = nearest_region(comp, is_sea(s))
        if r is None:
            stats["unresolved"] += len(comp)
            continue
        for i in comp:
            provs[i]["vreg"] = r
        stats["sea_out_of_land" if is_sea(s) else "land_out_of_naval"] += len(comp)
    for _ in range(10):
        changed = 0
        members = {}
        for i, p in provs.items():
            if is_sea(i):
                members.setdefault(p["vreg"], []).append(i)
        for r, mem in sorted(members.items()):
            mset, comps, seen = set(mem), [], set()
            for s in mem:
                if s in seen:
                    continue
                comp, stack = {s}, [s]
                seen.add(s)
                while stack:
                    for q in provs[stack.pop()]["n"]:
                        if q in mset and q not in seen:
                            seen.add(q)
                            comp.add(q)
                            stack.append(q)
                comps.append(comp)
            comps.sort(key=lambda c: -sum(provs[i]["px"] for i in c))
            for comp in comps[1:]:
                votes = Counter(provs[q]["vreg"] for i in comp for q in provs[i]["n"]
                                if q not in comp and is_sea(q) and provs[q]["vreg"] != r)
                if not votes:
                    stats["unresolved"] += len(comp)
                    continue
                new = votes.most_common(1)[0][0]
                for i in comp:
                    provs[i]["vreg"] = new
                changed += len(comp)
        stats["sea_reattached"] += changed
        if not changed:
            break
    log(f"strategic regions settled: {stats}")
    if stats["unresolved"]:
        log("WARN: some provinces could not be given a region of their own kind (run tools/validate.py)")
    return stats


def write_regions(provs, labels, region_of_vid, reg_files, sea_regions):
    log("strategic regions")
    for i, p in provs.items():
        p["vreg"] = int(region_of_vid[p["vid"]])
    settle_regions(provs, sea_regions)
    by_reg = {}
    for i, p in provs.items():
        by_reg.setdefault(p["vreg"], []).append(i)
    sr = OUT / "strategicregions"
    if sr.exists():
        for f in sr.glob("*.txt"):
            f.unlink()
    sr.mkdir(parents=True, exist_ok=True)
    newid = {}
    weather = []
    for k, r in enumerate(sorted(by_reg), 1):
        newid[r] = k
        t = reg_files[r]
        t = re.sub(r"\bid\s*=\s*\d+", f"id = {k}", t, count=1)
        t = re.sub(r"provinces\s*=\s*\{[^}]*\}", "provinces = {\n\t\t" + " ".join(map(str, by_reg[r])) + "\n\t}", t,
                   count=1)
        (sr / f"{k}-region.txt").write_text(t, encoding="utf-8")
        ps = by_reg[r]
        big = max(ps, key=lambda i: provs[i]["px"])
        bx, by = provs[big]["c"]
        sx_, sy_ = provs[big]["pts"][-1]
        # the sizes in the real game files are "big" and "small" (the wiki prose says "large", the
        # files of working mods such as Kaiserreich say "big"); the engine wants one of each
        weather.append(f"{k};{bx:.2f};10.00;{H - by:.2f};big")
        weather.append(f"{k};{sx_:.2f};10.00;{H - sy_:.2f};small")
    for p in provs.values():
        p["region"] = newid[p["vreg"]]
    (OUT / "weatherpositions.txt").write_text("\n".join(weather) + "\n", encoding="utf-8")
    # AI areas reference strategic region ids: translate vanilla ids, drop regions outside the map
    src = (GAME / "common" / "ai_areas" / "default.txt").read_text(encoding="utf-8-sig")

    def fix_block(m):
        ids = [int(x) for x in re.findall(r"\b\d+\b", re.sub(r"#[^\n]*", "", m.group(1)))]
        new = sorted({newid[i] for i in ids if i in newid})
        return "strategic_regions = {\n\t\t\t" + " ".join(map(str, new)) + "\n\t\t}"

    out = re.sub(r"strategic_regions\s*=\s*\{([^}]*)\}", fix_block, src)
    names = re.search(r"continents\s*=\s*\{([^}]*)\}",
                      re.sub(r"#[^\n]*", "", (VMAP / "continent.txt").read_text(encoding="utf-8-sig"))).group(1).split()
    used = {p["continent"] for p in provs.values() if p["type"] == "land"}
    out, dropped = drop_empty_ai_areas(out, {n for k, n in enumerate(names, 1) if k in used})
    log(f"AI areas outside the map dropped: {dropped}")
    ai = MOD / "common" / "ai_areas"
    ai.mkdir(parents=True, exist_ok=True)
    (ai / "default.txt").write_text(out, encoding="utf-8")
    log(f"{len(by_reg)} strategic regions")


def write_adjacencies(provs, labels, d):
    log("adjacencies")
    hdr = "From;To;Type;Through;start_x;start_y;stop_x;stop_y;adjacency_rule_name;Comment"
    out = [hdr]
    text = (VMAP / "adjacencies.csv").read_text(encoding="utf-8-sig").splitlines()[1:]
    vst = d["stats"]

    def new_at(vp, want):
        s = vst.get(vp)
        if not s:
            return None
        x = int((s["x"] - X0) * SCALE + SCALE / 2)
        y = int((s["y"] - Y0) * SCALE + SCALE / 2)
        if not (0 <= x < W and 0 <= y < H):
            return None
        p = int(labels[y, x])
        if provs[p]["type"] != want:
            # nearest province of the wanted type among those with this vanilla id
            cands = [i for i, q in provs.items() if q["vid"] == vp and q["type"] == want]
            return cands[0] if cands else None
        return p

    seen = set()
    for line in text:
        parts = line.split(";")
        if len(parts) < 9 or not parts[0].lstrip("-").isdigit():
            continue
        f, t, typ, thr = int(parts[0]), int(parts[1]), parts[2], int(parts[3])
        if f < 0:
            continue
        ft = d["defs"].get(f, {}).get("type")
        tt = d["defs"].get(t, {}).get("type")
        nf, nt = new_at(f, ft), new_at(t, tt)
        if not nf or not nt or nf == nt:
            continue
        key = (min(nf, nt), max(nf, nt))
        if key in seen:
            continue  # two vanilla crossings can collapse onto the same pair of new provinces
        adjacent = nt in provs[nf]["n"]
        nthr = -1
        if typ == "impassable":
            if not adjacent:
                continue  # can only block a border that exists on the new map
        elif typ == "sea":
            # strait crossing: two land provinces that do not touch, through a sea province touching both
            if adjacent or ft != "land" or tt != "land" or thr < 0:
                continue
            nthr = new_at(thr, "sea")
            if not nthr or nf not in provs[nthr]["n"] or nt not in provs[nthr]["n"]:
                continue
        else:
            # vanilla sea-to-sea straits/canals only make sense with their adjacency rule; we ship no
            # rules yet, and between provinces that no longer touch the line would be a teleport
            continue
        seen.add(key)
        out.append(f"{nf};{nt};{typ};{nthr};-1;-1;-1;-1;;{parts[9] if len(parts) > 9 else ''}")
    log(f"{len(out) - 1} adjacencies kept")
    out.append("-1;-1;-1;-1;-1;-1;-1;-1;-1")  # vanilla terminator: must be the last line of the file
    (OUT / "adjacencies.csv").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\r\n")


def write_static_files(provs, hmap):
    (OUT / "adjacency_rules.txt").write_text("# Ante Imperium: no special adjacency rules yet\n", encoding="utf-8")
    (OUT / "ambient_object.txt").write_text("", encoding="utf-8")
    (OUT / "positions.txt").write_text("", encoding="utf-8")
    lines = []
    # unit stack position types, as used by vanilla per province kind
    land_t = list(range(0, 11)) + list(range(21, 30)) + [38]
    sea_t = list(range(0, 19)) + list(range(21, 39))
    lake_t = [0, 1, 2, 3, 4, 5, 9, 10, 21, 22, 23, 24, 25, 26, 38]
    for i, p in provs.items():
        x, y = p["x"], p["y"]
        types = {"land": land_t, "sea": sea_t, "lake": lake_t}[p["type"]]
        pts = [p["c"]] + p["pts"]
        for k, t in enumerate(types):
            px, py = pts[k % len(pts)]
            hh = hmap[min(H - 1, int(py)), min(W - 1, int(px))] / 10.0
            lines.append(f"{i};{t};{px:.2f};{hh:.2f};{H - py:.2f};0.00;0.30")
        if p["type"] == "land" and p.get("coast"):
            cx, cy, _ = p["coast"]
            hh = hmap[min(H - 1, int(cy)), min(W - 1, int(cx))] / 10.0
            for t in (19, 20):
                lines.append(f"{i};{t};{cx:.2f};{hh:.2f};{H - cy:.2f};0.00;0.30")
    (OUT / "unitstacks.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def coast_points(labels, provs):
    """for coastal land provinces: a land pixel touching the sea and the sea province id"""
    log("coast points")
    pts = {}
    for dy, dx in SHIFTS4:
        ty, sy = _sl(dy, H)
        tx, sx = _sl(dx, W)
        a = labels[ty, tx]
        b = labels[sy, sx]
        m = a != b
        ys, xs = np.nonzero(m)
        av, bv = a[m], b[m]
        for y, x, p, q in zip(ys[::7], xs[::7], av[::7], bv[::7]):
            p, q = int(p), int(q)
            if p in pts or provs[p]["type"] != "land" or provs[q]["type"] != "sea":
                continue
            pts[p] = (int(x + tx.start), int(y + ty.start), q)
    for p, v in provs.items():
        if v["type"] == "land" and v["coastal"] and p not in pts:
            sea = next((q for q in v["n"] if provs[q]["type"] == "sea"), None)
            pts[p] = (int(v["x"]), int(v["y"]), sea)
    for p, (x, y, q) in pts.items():
        provs[p]["coast"] = [x, y, q]


def identity_rest(d, labels, n, cls, vid, typ, region_of_vid, reg_files):
    colors = province_colors(n)
    Image.fromarray(colors[labels], "RGB").save(OUT / "provinces.bmp")
    provs = write_definitions(labels, n, cls, vid, d, colors, typ)
    write_regions(provs, labels, region_of_vid, reg_files, sea_region_ids(d, region_of_vid))
    write_adjacencies(provs, labels, d)
    ys, xs = src_index()
    write_layers(cls, ys, xs)
    write_rivers(cls)
    hmap = np.asarray(Image.open(OUT / "heightmap.bmp"))
    coast_points(labels, provs)
    write_static_files(provs, hmap)
    np.save(CACHE / "newmap_labels.npy", labels)
    (CACHE / "newmap.json").write_text(json.dumps({"size": [W, H], "x0": X0, "y0": Y0, "scale": SCALE,
                                                   "provinces": provs}))
    log(f"identity done: {n} provinces")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    d, vids = load_vanilla()
    ys, xs = src_index()
    regs, reg_files = strategic_regions_vanilla()
    region_of_vid = np.zeros(max(d["defs"]) + 1, np.int32)
    for p, r in regs.items():
        region_of_vid[p] = r
    if os.environ.get("ANTE_MAP") == "identity":
        n0 = max(d["defs"]) + 1
        typ = np.zeros(n0, np.int8)
        for p, v in d["defs"].items():
            typ[p] = {"land": LAND, "sea": SEA, "lake": LAKE}[v["type"]]
        vid = vids.astype(np.int32)
        cls = typ[vid]
        domain = (region_of_vid[vid] * 4 + cls).astype(np.int32)
        labels, n = renumber(vid)
        return identity_rest(d, labels, n, cls, vid, typ, region_of_vid, reg_files)
    cls, vid, typ = build_class_and_vid(d, vids, ys, xs)
    area = area_target(cls, vid, d, ys, xs)
    labels, domain = make_provinces(cls, vid, region_of_vid, typ, area)
    del area
    labels = merge_small(labels, domain, cls)
    labels = absorb_enclosed_sea(labels, cls, domain)
    labels = fix_x_crossings(labels, domain)
    # the repairs can undo each other (a repainted pixel may split a province, a regrown fragment
    # may create a new diagonal touch), so repeat them until the province map no longer changes
    for _ in range(5):
        before = labels.copy()
        labels, _ = grow_tiny(labels, cls, domain)
        labels = drop_fragments(labels, cls)
        labels = fix_x_crossings(labels, domain)
        labels = fix_seam(labels, cls, domain)
        labels = fix_x_crossings(labels, domain)
        if (labels == before).all():
            break
    else:
        log("WARN: province repairs did not settle - run tools/validate.py")
    assert (labels >= 0).all(), "unassigned pixels left"
    labels, n = renumber(labels)
    log(f"{n} provinces")
    colors = province_colors(n)
    Image.fromarray(colors[labels], "RGB").save(OUT / "provinces.bmp")
    provs = write_definitions(labels, n, cls, vid, d, colors, typ)
    write_regions(provs, labels, region_of_vid, reg_files, sea_region_ids(d, region_of_vid))
    write_adjacencies(provs, labels, d)
    # the repairs moved pixels between provinces: the layers must follow the final province types,
    # so that every land pixel is above and every water pixel below sea level, and no river runs on water
    ptype = np.zeros(n + 1, np.int8)
    for i, p in provs.items():
        ptype[i] = {"land": LAND, "sea": SEA, "lake": LAKE}[p["type"]]
    cls = ptype[labels]
    write_layers(cls, ys, xs)
    write_rivers(cls)
    hmap = np.asarray(Image.open(OUT / "heightmap.bmp"))
    coast_points(labels, provs)
    write_static_files(provs, hmap)
    np.save(CACHE / "newmap_labels.npy", labels)
    (CACHE / "newmap.json").write_text(json.dumps({"size": [W, H], "x0": X0, "y0": Y0, "scale": SCALE,
                                                   "provinces": provs}))
    kinds = {}
    for p in provs.values():
        kinds[p["type"]] = kinds.get(p["type"], 0) + 1
    log(f"done: {kinds}")


if __name__ == "__main__":
    main()
