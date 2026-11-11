"""Read-only access to vanilla HoI4 map data (provinces, states) with a JSON cache.

Never writes into the base game. Cache lives in tools/cache/ (gitignored).
"""
import csv
import json
import os
import re
from pathlib import Path

import numpy as np
from PIL import Image

GAME = Path(r"D:/SteamLibrary/steamapps/common/Hearts of Iron IV")
MOD = Path(__file__).resolve().parent.parent
CACHE = MOD / "tools" / "cache"


def load_definitions():
    """id -> dict(rgb, type, coastal, terrain, continent)"""
    defs = {}
    with open(GAME / "map" / "definition.csv", encoding="utf-8", errors="replace") as f:
        for row in csv.reader(f, delimiter=";"):
            if len(row) < 8 or not row[0].isdigit():
                continue
            pid = int(row[0])
            if pid == 0:
                continue
            defs[pid] = {
                "rgb": (int(row[1]), int(row[2]), int(row[3])),
                "type": row[4],
                "coastal": row[5] == "true",
                "terrain": row[6],
                "continent": int(row[7]),
            }
    return defs


def province_id_image(defs=None):
    """2D int32 array of province ids (row 0 = top of the bitmap)."""
    defs = defs or load_definitions()
    rgb = np.asarray(Image.open(GAME / "map" / "provinces.bmp").convert("RGB"), dtype=np.int32)
    packed = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    keys = np.array(sorted((r << 16 | g << 8 | b, pid) for pid, d in defs.items() for (r, g, b) in [d["rgb"]]))
    idx = np.searchsorted(keys[:, 0], packed)
    idx = np.clip(idx, 0, len(keys) - 1)
    ids = np.where(keys[idx, 0] == packed, keys[idx, 1], 0).astype(np.int32)
    return ids


def compute_province_stats(ids):
    """centroid, pixel count and neighbours for every province."""
    n = int(ids.max()) + 1
    h, w = ids.shape
    ys, xs = np.indices(ids.shape)
    flat = ids.ravel()
    count = np.bincount(flat, minlength=n)
    sx = np.bincount(flat, weights=xs.ravel(), minlength=n)
    sy = np.bincount(flat, weights=ys.ravel(), minlength=n)
    stats = {}
    for pid in np.nonzero(count)[0]:
        if pid == 0:
            continue
        c = count[pid]
        stats[int(pid)] = {"px": int(c), "x": round(sx[pid] / c, 1), "y": round(sy[pid] / c, 1)}
    pairs = set()
    for a, b in ((ids[:, :-1], ids[:, 1:]), (ids[:-1, :], ids[1:, :])):
        m = a != b
        for p, q in zip(a[m].tolist(), b[m].tolist()):
            if p and q:
                pairs.add((min(p, q), max(p, q)))
    neigh = {pid: [] for pid in stats}
    for p, q in pairs:
        neigh.setdefault(p, []).append(q)
        neigh.setdefault(q, []).append(p)
    for pid, s in stats.items():
        s["n"] = sorted(neigh.get(pid, []))
    return stats, (w, h)


STATE_ID_RE = re.compile(r"\bid\s*=\s*(\d+)")
PROV_RE = re.compile(r"provinces\s*=\s*\{([^}]*)\}", re.S)
OWNER_RE = re.compile(r"\bowner\s*=\s*(\w+)")
NAME_RE = re.compile(r"^(\d+)-(.*)\.txt$")


def load_vanilla_states():
    """state id -> dict(file, name, owner, provinces)"""
    states = {}
    for fp in (GAME / "history" / "states").glob("*.txt"):
        text = fp.read_text(encoding="utf-8-sig", errors="replace")
        text_nc = re.sub(r"#[^\n]*", "", text)
        sid = int(STATE_ID_RE.search(text_nc).group(1))
        provs = [int(x) for x in PROV_RE.search(text_nc).group(1).split()]
        owner = OWNER_RE.search(text_nc)
        m = NAME_RE.match(fp.name)
        states[sid] = {
            "file": fp.name,
            "name": m.group(2) if m else fp.stem,
            "owner": owner.group(1) if owner else None,
            "provinces": provs,
        }
    return states


def load_all(rebuild=False):
    """Returns dict with defs, stats, size, states, prov2state. Cached as JSON."""
    CACHE.mkdir(parents=True, exist_ok=True)
    cf = CACHE / "mapdata.json"
    if cf.exists() and not rebuild:
        d = json.loads(cf.read_text())
        d["defs"] = {int(k): v for k, v in d["defs"].items()}
        d["stats"] = {int(k): v for k, v in d["stats"].items()}
        d["states"] = {int(k): v for k, v in d["states"].items()}
        d["prov2state"] = {int(k): v for k, v in d["prov2state"].items()}
        return d
    defs = load_definitions()
    ids = province_id_image(defs)
    stats, size = compute_province_stats(ids)
    states = load_vanilla_states()
    prov2state = {p: sid for sid, s in states.items() for p in s["provinces"]}
    d = {"defs": defs, "stats": stats, "size": size, "states": states, "prov2state": prov2state}
    cf.write_text(json.dumps(d))
    np.save(CACHE / "ids.npy", ids)
    return d


def load_ids():
    f = CACHE / "ids.npy"
    if not f.exists():
        load_all(rebuild=True)
    return np.load(f)


if __name__ == "__main__":
    d = load_all(rebuild=True)
    land = [p for p, v in d["defs"].items() if v["type"] == "land"]
    no_state = [p for p in land if p not in d["prov2state"]]
    print(f"size={d['size']} provinces={len(d['defs'])} land={len(land)} "
          f"states={len(d['states'])} land_without_state={len(no_state)}")
