"""Fit the game's day/night shading to this map (needs the game install).

usage: python tools/daynight.py            day and night as in the base game, at the right hours for this map
       python tools/daynight.py --off      no night shading at all
       python tools/daynight.py --remove   delete the shader copy again (back to the game's own)

Why: the map shader (gfx/FX/standardfuncsgfx.fxh) works out where it is day or night with constants of
the VANILLA world map that are written into the shader source:
    static const float GMT_OFFSET = 2793.0f;        // X position on map, of Greenwich GMT+0
    static const float SOUTH_POLE_OFFSET = 0.17f;   // how much of the globe the map misses in the south
    ... ( vWorldXZ.x - GMT_OFFSET ) / MAP_SIZE_X ...  // the WIDTH OF THE MAP is taken to be 360 degrees
Our map is a zoomed crop: Greenwich is at x = 631 and the whole width is only 88.6 degrees. With the
game's own shader half of the map is always in the night and the line between day and night stands
in the middle of it as a hard vertical edge (seen in game 2026-11-13).
The constants are compiled into the shader, a define cannot change them. So this tool copies the
game's own shader file into the mod (gfx/FX/) with those values changed and the longitude scaled by
LONGITUDE_SHARE. Run it again after a game update if the game's shader changed (the copy must match
the installed version; 1.19.4 and 1.19.5 are identical).
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


def longitude_share():
    """which part of the vanilla map's width (= of the 360 degrees) this map covers"""
    import newmap as N
    return round(N.W / N.SCALE / VANILLA_W, 4)


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
        # the map is not the whole globe: scale the longitude (see the docstring)
        if "LONGITUDE_SHARE" not in new:
            new, k1 = re.subn(r"(?m)^([ \t]*)(static const float GMT_OFFSET = [^\r\n]*)(\r?\n)",
                              lambda m: (m.group(1) + m.group(2) + " (Ante Imperium map)" + m.group(3) + m.group(1)
                                         + f"static const float LONGITUDE_SHARE = {longitude_share()}f; // Ante Imperium: the map is "
                                         + f"{longitude_share() * 360:.1f} of the 360 degrees wide, not the whole globe" + m.group(3)),
                              new, count=1)
            new, k2 = re.subn(r"/ MAP_SIZE_X \+ DayNight_Hour_SunDir\.x", "/ MAP_SIZE_X * LONGITUDE_SHARE + DayNight_Hour_SunDir.x", new)
            if k1 and not k2:
                print(f"WARN: {fp.name}: GMT_OFFSET found but not the longitude formula - the shader changed, check it by hand",
                      file=sys.stderr)
                new = old
        if off:
            # the game's own switch, if this version still has it; otherwise make the night fully transparent
            new, k = re.subn(r"(?m)^([ \t]*)//[ \t]*(#define[ \t]+NO_NIGHT\b)", r"\1\2", new)
            if not k and "#define NO_NIGHT" not in new:
                pat, fn = number("NIGHT_OPACITY", "0.0")
                new = re.sub(pat, fn, new)
        if new != old:
            out[f"gfx/FX/{fp.name}"] = new.encode("latin-1")
            import difflib
            for line in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0):
                if line[:1] in "+-" and line[:3] not in ("+++", "---"):
                    notes.append(f"{fp.name}: {line[0]} {line[1:].strip()}")
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
