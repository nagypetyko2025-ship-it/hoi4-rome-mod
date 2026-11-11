"""Render a labelled crop of the province map for planning.

usage: python tools/render_region.py x0 y0 x1 y1 out.png [scale] [--assign]
Coordinates are provinces.bmp pixels (y from top). Thin lines = provinces,
thick = vanilla states (or new states with --assign, read from build data).
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import mapdata  # noqa: E402


def render(x0, y0, x1, y1, out, scale=3, assign=None, colors=None):
    d = mapdata.load_all()
    ids = mapdata.load_ids()[y0:y1, x0:x1]
    groups = assign or d["prov2state"]
    st = np.vectorize(lambda p: groups.get(int(p), -1) if not isinstance(groups.get(int(p), -1), str)
                      else hash(groups[int(p)]) & 0xFFFFFF)(ids)
    img = np.full(ids.shape + (3,), 255, np.uint8)
    for pid in np.unique(ids):
        t = d["defs"].get(int(pid), {}).get("type")
        m = ids == pid
        if t == "sea":
            img[m] = (170, 200, 230)
        elif t == "lake":
            img[m] = (140, 180, 220)
        else:
            g = groups.get(int(pid))
            if colors and g in colors:
                img[m] = colors[g]
            else:
                h = (hash(str(g)) * 2654435761) & 0xFFFFFF
                img[m] = (180 + (h & 63), 170 + ((h >> 8) & 63), 150 + ((h >> 16) & 63))
    pe = np.zeros(ids.shape, bool)
    pe[:, 1:] |= ids[:, 1:] != ids[:, :-1]
    pe[1:, :] |= ids[1:, :] != ids[:-1, :]
    se = np.zeros(ids.shape, bool)
    se[:, 1:] |= st[:, 1:] != st[:, :-1]
    se[1:, :] |= st[1:, :] != st[:-1, :]
    img[pe] = (120, 120, 120)
    big = Image.fromarray(img).resize(((x1 - x0) * scale, (y1 - y0) * scale), Image.NEAREST)
    arr = np.asarray(big).copy()
    se_big = np.kron(se, np.ones((scale, scale), bool))
    arr[se_big] = (0, 0, 0)
    big = Image.fromarray(arr)
    dr = ImageDraw.Draw(big)
    try:
        font = ImageFont.truetype("arial.ttf", 11)
    except OSError:
        font = ImageFont.load_default()
    for pid in np.unique(ids):
        s = d["stats"].get(int(pid))
        if not s or d["defs"][int(pid)]["type"] != "land":
            continue
        cx, cy = (s["x"] - x0) * scale, (s["y"] - y0) * scale
        if 0 <= cx < big.width and 0 <= cy < big.height:
            dr.text((cx, cy), str(pid), fill=(150, 0, 0), font=font, anchor="mm")
    big.save(out)
    print("wrote", out, big.size)


if __name__ == "__main__":
    a = sys.argv[1:]
    render(int(a[0]), int(a[1]), int(a[2]), int(a[3]), a[4], int(a[5]) if len(a) > 5 else 3)
