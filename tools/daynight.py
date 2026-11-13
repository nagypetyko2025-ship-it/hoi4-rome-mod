"""Fit the game's day/night shading to this map (needs the game install).

usage: python tools/daynight.py            day/night stays, but at the right hours for this map
       python tools/daynight.py --off      no night shading at all (recommended for this mod)
       python tools/daynight.py --remove   delete the shader copy again (back to the game's own)

Why: the map shader places the day/night line with constants of the VANILLA map that are written
into the shader source (gfx/FX, in 1.7 standardfuncsgfx.fxh, later daynight.fxh):
    static const float GMT_OFFSET = 2793.0f;        // X position on map, of Greenwich GMT+0
    static const float SOUTH_POLE_OFFSET = 0.17f;   // how much of the globe the map misses in the south
    //#define NO_NIGHT                               // switch: no night shading
On our map Greenwich is at x = 631, not 2793. (1130 - 2793) / 3328 = -0.5: Italy is exactly half a
day off, so at 12:00 - when every game starts - it is MIDNIGHT there, and the night side of the map is
drawn dark and almost colourless (land 80 % desaturated, half as bright).
The constants are compiled into the shader, a define cannot change them. So this tool copies the
game's own shader file(s) that hold them into the mod (gfx/FX/) with only those values changed.
Run it again after every game update (the copy must match the installed game version).
"""
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
MOD = TOOLS.parent
VANILLA_GMT, VANILLA_SOUTH, VANILLA_NORTH, VANILLA_W, VANILLA_H = 2793.0, 0.17, 0.93, 5632, 2048


def map_constants():
    """(GMT_OFFSET, SOUTH_POLE_OFFSET, NORTH_POLE_OFFSET) for the crop and zoom of tools/newmap.py"""
    import newmap as N
    gmt = (VANILLA_GMT - N.X0) * N.SCALE
    span = VANILLA_NORTH - VANILLA_SOUTH

    def pole(row):                      # vanilla pixel row (0 = top) -> position on the pole-to-pole scale
        return VANILLA_SOUTH + span * (1.0 - row / VANILLA_H)

    return round(gmt, 1), round(pole(N.Y0 + N.H / N.SCALE), 3), round(pole(N.Y0), 3)


def number(name, value):
    """regex substitution: <name> = <number>[f]  ->  <name> = <value>[f]"""
    return (r"(\b" + name + r"\s*=\s*)-?[0-9]*\.?[0-9]+(f?)", lambda m: m.group(1) + value + m.group(2))


def patch_files(off, game=None):
    """-> {path inside the mod: new bytes} for every shader file of the game that needed a change"""
    import mapdata
    fx = Path(game or mapdata.GAME) / "gfx" / "FX"
    out, notes = {}, []
    if not fx.is_dir():
        print(f"WARN: {fx} not found - is the game installed there? (path: tools/mapdata.py GAME)", file=sys.stderr)
        return out, notes
    gmt, south, north = map_constants()
    for fp in sorted(fx.iterdir()):
        if fp.suffix.lower() not in (".fxh", ".shader", ".fx"):
            continue
        old = fp.read_bytes().decode("latin-1")              # latin-1: every byte survives the round trip
        new = old
        for name, value in (("GMT_OFFSET", f"{gmt}"), ("SOUTH_POLE_OFFSET", f"{south}"), ("NORTH_POLE_OFFSET", f"{north}")):
            pat, fn = number(name, value)
            new = re.sub(pat, fn, new)
        if off:
            # the game's own switch, if this version still has it; otherwise make the night fully transparent
            new, k = re.subn(r"(?m)^([ \t]*)//[ \t]*(#define[ \t]+NO_NIGHT\b)", r"\1\2", new)
            if not k and "#define NO_NIGHT" not in new:
                pat, fn = number("NIGHT_OPACITY", "0.0")
                new = re.sub(pat, fn, new)
        if new != old:
            out[f"gfx/FX/{fp.name}"] = new.encode("latin-1")
            for a, b in zip(old.splitlines(), new.splitlines()):
                if a != b:
                    notes.append(f"{fp.name}: {a.strip()}  ->  {b.strip()}")
    if not out:
        print(f"WARN: no GMT_OFFSET / NO_NIGHT / NIGHT_OPACITY found in {fx} - nothing to patch", file=sys.stderr)
    return out, notes


def main():
    target = MOD / "gfx" / "FX"
    if "--remove" in sys.argv:
        for fp in target.glob("*") if target.is_dir() else []:
            fp.unlink()
            print("removed", fp.relative_to(MOD))
        return
    files, notes = patch_files("--off" in sys.argv)
    for rel, data in files.items():
        p = MOD / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    for n in notes:
        print(n)
    if files:
        print(f"{len(files)} shader file(s) written to gfx/FX - test in game, then commit them")


if __name__ == "__main__":
    main()
