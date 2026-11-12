"""Rewrite the position files from the final province map: map/buildings.txt and map/unitstacks.txt.

usage: python tools/positions.py

Needs only this mod folder (numpy + Pillow) - no game install and no tools/cache. It runs the very
functions the generators use (newmap.inside_points / coast_points / write_static_files and
build.write_buildings) on the committed provinces.bmp, definition.csv and history/states, so the
positions can be repaired or re-rolled without regenerating the map.
"""
import re
import struct
import sys
from pathlib import Path

import numpy as np

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import newmap as N  # noqa: E402
import build as B  # noqa: E402

MOD = TOOLS.parent
MAP = MOD / "map"


def load_map():
    defs = {}
    for line in (MAP / "definition.csv").read_text(encoding="utf-8").splitlines():
        p = line.split(";")
        if len(p) >= 8 and int(p[0]):
            defs[int(p[0])] = dict(rgb=(int(p[1]), int(p[2]), int(p[3])), type=p[4], terrain=p[6], continent=int(p[7]))
    raw = (MAP / "provinces.bmp").read_bytes()
    off = struct.unpack("<I", raw[10:14])[0]
    w, h = struct.unpack("<ii", raw[18:26])
    stride = (w * 3 + 3) & ~3
    bgr = np.frombuffer(raw, np.uint8, count=stride * h, offset=off).reshape(h, stride)[::-1, :w * 3].reshape(h, w, 3)
    packed = (bgr[..., 2].astype(np.int32) << 16) | (bgr[..., 1].astype(np.int32) << 8) | bgr[..., 0]
    keys = np.array(sorted((r << 16 | g << 8 | b, i) for i, d in defs.items() for (r, g, b) in [d["rgb"]]))
    idx = np.clip(np.searchsorted(keys[:, 0], packed), 0, len(keys) - 1)
    assert (keys[idx, 0] == packed).all(), "provinces.bmp has colours that are not in definition.csv"
    return defs, keys[idx, 1].astype(np.int32)


def province_table(defs, labels):
    n = max(defs)
    flat = labels.ravel()
    cnt = np.bincount(flat, minlength=n + 1)
    yy, xx = np.indices(labels.shape)
    cy = np.bincount(flat, yy.ravel(), minlength=n + 1) / np.maximum(cnt, 1)
    cx = np.bincount(flat, xx.ravel(), minlength=n + 1) / np.maximum(cnt, 1)
    a = np.concatenate([labels[:, :-1].ravel(), labels[:-1, :].ravel(), labels[:, -1]])
    b = np.concatenate([labels[:, 1:].ravel(), labels[1:, :].ravel(), labels[:, 0]])   # incl. the east-west wrap
    m = a != b
    pairs = np.unique(np.stack([np.minimum(a[m], b[m]), np.maximum(a[m], b[m])], 1), axis=0)
    nb = [set() for _ in range(n + 1)]
    for p, q in pairs.tolist():
        nb[p].add(q)
        nb[q].add(p)
    provs = {}
    for i in range(1, n + 1):
        d = defs[i]
        provs[i] = dict(type=d["type"], terrain=d["terrain"], continent=d["continent"],
                        x=round(float(cx[i]), 1), y=round(float(cy[i]), 1), px=int(cnt[i]), n=sorted(nb[i]))
    for i, p in provs.items():
        other = {"land": "sea", "sea": "land"}.get(p["type"])
        p["coastal"] = bool(other) and any(provs[q]["type"] == other for q in p["n"])
    return provs, cx, cy


def load_states():
    states = []
    for fp in (MOD / "history" / "states").glob("*.txt"):
        t = re.sub(r"#[^\n]*", "", fp.read_text(encoding="utf-8-sig"))
        states.append(dict(id=int(re.search(r"\bid\s*=\s*(\d+)", t).group(1)),
                           provinces=[int(x) for x in re.search(r"provinces\s*=\s*\{([^}]*)\}", t).group(1).split()]))
    return sorted(states, key=lambda s: s["id"])


def main():
    defs, labels = load_map()
    h, w = labels.shape
    assert (w, h) == (N.W, N.H), f"map is {w}x{h}, newmap.py is set up for {N.W}x{N.H} (ANTE_MAP)"
    provs, cx, cy = province_table(defs, labels)
    N.inside_points(labels, provs, cx, cy)
    N.coast_points(labels, provs)
    hmap = np.asarray(B.Image.open(MAP / "heightmap.bmp"))
    N.write_static_files(provs, hmap)                                    # unitstacks.txt
    B.write_buildings(dict(provinces=provs, size=[w, h]), load_states())  # buildings.txt
    ports = sum(1 for p in provs.values() if p.get("coast"))
    print(f"positions rewritten: {len(provs)} provinces, {ports} coastal land provinces with a port position")


if __name__ == "__main__":
    main()
