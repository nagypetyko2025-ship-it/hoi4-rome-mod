"""Write one bisect variant of the mod's map files into a folder (used by tools/bisect_launch.ps1).

usage: python tools/make_variants.py <variant> <out_dir>     (python tools/make_variants.py --list)

A variant is a small set of replacement files, each a simplified version of one generated file.
Starting the game with a variant swapped in tells us whether that file is what crashes the game.
Needs only this mod folder and numpy - no game install.
"""
import re
import struct
import sys
from pathlib import Path

import numpy as np

MOD = Path(__file__).resolve().parent.parent
MAP = MOD / "map"
STATE_LEVEL = ("air_base", "anti_air_building", "arms_factory", "industrial_complex", "fuel_silo",
               "nuclear_reactor_spawn", "radar_station", "rocket_site_spawn", "stronghold_network",
               "synthetic_refinery")


def bmp_parts(path):
    """-> (bytes before the pixel data, pixel array incl. row padding, width, height, bits per pixel)"""
    raw = path.read_bytes()
    off = struct.unpack("<I", raw[10:14])[0]
    w, h, _planes, bpp = struct.unpack("<iiHH", raw[18:30])
    stride = ((w * bpp // 8) + 3) & ~3
    body = np.frombuffer(raw, np.uint8, count=stride * abs(h), offset=off).reshape(abs(h), stride).copy()
    return raw[:off], body, w, abs(h), bpp


def text(rel):
    return (MOD / rel).read_text(encoding="utf-8-sig")


def land_mask():
    """rivers.bmp doubles as a land mask: 254 is water, everything else lies on land"""
    _head, body, w, _h, _bpp = bmp_parts(MAP / "rivers.bmp")
    return body[:, :w] != 254


def rivers_blank():
    head, body, w, _h, _ = bmp_parts(MAP / "rivers.bmp")
    px = body[:, :w]
    px[px < 12] = 255
    return {"map/rivers.bmp": head + body.tobytes()}


def trees_blank():
    head, body, _w, _h, _ = bmp_parts(MAP / "trees.bmp")
    body[:] = 0
    return {"map/trees.bmp": head + body.tobytes()}


def cities_blank():
    head, body, w, _h, _ = bmp_parts(MAP / "cities.bmp")
    vals, counts = np.unique(body[:, :w], return_counts=True)
    body[:, :w] = vals[np.argmax(counts)]          # the "no city" index is by far the most common one
    return {"map/cities.bmp": head + body.tobytes()}


def height_flat():
    land = land_mask()
    head, body, w, _h, _ = bmp_parts(MAP / "heightmap.bmp")
    body[:, :w] = np.where(land, 100, 85)
    out = {"map/heightmap.bmp": head + body.tobytes()}
    head, body, w, _h, _ = bmp_parts(MAP / "world_normal.bmp")
    body[:, :w * 3] = np.tile(np.array([255, 128, 128], np.uint8), w)   # BGR: flat normal
    out["map/world_normal.bmp"] = head + body.tobytes()
    return out


def buildings(keep):
    lines = [ln for ln in text("map/buildings.txt").splitlines() if ln.split(";")[1:2] and keep(ln.split(";")[1])]
    return {"map/buildings.txt": ("\n".join(lines) + "\n").encode()}


def adjacencies_min():
    head = text("map/adjacencies.csv").splitlines()[0]
    return {"map/adjacencies.csv": (head + "\r\n-1;-1;-1;-1;-1;-1;-1;-1;-1\r\n").encode()}


def supply_min():
    return {"map/supply_nodes.txt": (text("map/supply_nodes.txt").splitlines()[0] + "\n").encode(),
            "map/railways.txt": (text("map/railways.txt").splitlines()[0] + "\n").encode()}


def no_ports():
    out = {}
    for fp in (MOD / "history" / "states").glob("*.txt"):
        t = fp.read_text(encoding="utf-8-sig")
        t2 = re.sub(r"[ \t]*\d+\s*=\s*\{\s*naval_base\s*=\s*\d+\s*\}[ \t]*\r?\n", "", t)
        if t2 != t:
            out[f"history/states/{fp.name}"] = t2.encode()
    return out


def weather(size):
    lines = [re.sub(r";(big|large)$", ";" + size, ln) for ln in text("map/weatherpositions.txt").splitlines()]
    return {"map/weatherpositions.txt": ("\r\n".join(lines) + "\r\n").encode()}


def no_region_defines():
    """the vanilla NGeography.MEDITERRANEAN_SEA_REGIONS (vanilla region ids) instead of our translated list"""
    return {"common/defines/zz_ante_regions.lua": b"-- bisect variant: no region id overrides (vanilla lists apply)\n"}


def unitstacks_min():
    """like the mapit generator: land provinces only, stack types 0 and 38"""
    land = set()
    for ln in text("map/definition.csv").splitlines():
        p = ln.split(";")
        if len(p) > 4 and p[4] == "land":
            land.add(p[0])
    lines = [ln for ln in text("map/unitstacks.txt").splitlines()
             if ln.split(";")[0] in land and ln.split(";")[1] in ("0", "38")]
    return {"map/unitstacks.txt": ("\n".join(lines) + "\n").encode()}


def no_impassable():
    out = {}
    for fp in (MOD / "history" / "states").glob("*.txt"):
        t = fp.read_text(encoding="utf-8-sig")
        t2 = re.sub(r"[ \t]*impassable\s*=\s*yes[ \t]*\r?\n", "", t)
        if t2 != t:
            out[f"history/states/{fp.name}"] = t2.encode()
    return out


def combine(*parts):
    out = {}
    for p in parts:
        out.update(p())
    return out


VARIANTS = {
    "baseline": (lambda: {}, "the files exactly as committed"),
    "no_region_defines": (no_region_defines, "WITHOUT the translated region-id defines (control: expected to crash)"),
    "unitstacks_min": (unitstacks_min, "unit stack positions for land provinces only, types 0 and 38"),
    "no_impassable": (no_impassable, "wasteland states passable"),
    "rivers_blank": (rivers_blank, "no rivers at all"),
    "buildings_no_state_level": (lambda: buildings(lambda t: t not in STATE_LEVEL),
                                 "buildings.txt without the state-level lines (air_base, arms_factory, ...)"),
    "buildings_ports_only": (lambda: buildings(lambda t: t in ("naval_base_spawn", "floating_harbor")),
                             "buildings.txt with nothing but naval base / floating harbour positions"),
    "no_ports": (no_ports, "no naval bases in the state history"),
    "supply_min": (supply_min, "one supply node and one railway only"),
    "adjacencies_min": (adjacencies_min, "no strait crossings / impassable borders"),
    "trees_blank": (trees_blank, "no trees"),
    "cities_blank": (cities_blank, "no city sprawl"),
    "height_flat": (height_flat, "flat heightmap and normal map"),
    "weather_large": (lambda: weather("large"), "weather size 'large' instead of 'big'"),
    "graphics_min": (lambda: combine(rivers_blank, trees_blank, cities_blank, height_flat),
                     "rivers, trees, cities and height all blank at once"),
    "all_min": (lambda: combine(rivers_blank, trees_blank, cities_blank, height_flat, adjacencies_min, supply_min,
                                no_ports, lambda: buildings(lambda t: t not in STATE_LEVEL)),
                "every simplification at once: if this still crashes, the cause is the province layout, "
                "the map size, the states or the strategic regions"),
}


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        for name, (_fn, desc) in VARIANTS.items():
            print(f"{name}\t{desc}")
        return
    if len(sys.argv) != 3 or sys.argv[1] not in VARIANTS:
        sys.exit(__doc__)
    out_dir = Path(sys.argv[2])
    files = VARIANTS[sys.argv[1]][0]()
    for rel, data in files.items():
        p = out_dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        print(rel)


if __name__ == "__main__":
    main()
