"""Ancient resources: what the states of 509 BC dig, cut, breed and harvest (round 21).

The engine and the base game's scripts know seven resource keys (oil, aluminium, rubber, tungsten, steel, chromium,
coal: common/resources/00_resources.txt, the defines OIL/FUEL/ENERGY_RESOURCE, hundreds of base-game files). We keep
the KEYS and give them ancient meanings, names and icons - nothing in the base game breaks, and every tooltip that
shows a resource shows ours:

    key        ancient resource   used for (tools/army.py)
    steel      Iron               spears and swords, siege engines
    aluminium  Copper             bronze: the hoplite panoply (with tin)
    tungsten   Tin                bronze: the hoplite panoply (with copper) - rare: Britain, Iberia, Bohemia, Bactria
    rubber     Timber             bows and javelins, chariots, siege engines, ships
    chromium   Horses             horses and tack, chariots
    oil        Pitch              ships (caulking); bitumen of Mesopotamia and the Dead Sea
    coal       Grain              feeds the workshops (the engine's energy resource)

Where: real ancient sources (mines, pitch forests, horse plains, granaries; DEPOSITS below, lon/lat) go to the state
nearest to them, and the land itself adds more: forests give timber, plains (most of all the steppe) horses and grain.

Called by tools/world.py (assign() before the states are written, write_files() after the localisation folder is
wiped). Writes:
  gfx/interface/resources_strip.dds, missing_resources_strip.dds  the icons (same paths as the game's: replaced)
  localisation/english/replace/ante_resources_l_english.yml        the names
"""
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

MOD = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from geo import to_xy  # noqa: E402

# key: (icon frame in the strip, name, description, colour of the icon)
RESOURCES = {
    "oil": (1, "Pitch", "Pine resin boiled down to pitch, and bitumen from the springs of Mesopotamia: no ship is "
            "watertight without it.", (40, 34, 30)),
    "aluminium": (2, "Copper", "Red copper from Cyprus, Tartessos and the Sinai. With a tenth part of tin it becomes "
                  "bronze - helmets, cuirasses and greaves.", (196, 110, 56)),
    "rubber": (3, "Timber", "Oak, pine, fir and the cedars of Lebanon: shafts and bows, chariots, siege towers and "
               "the long ships.", (138, 92, 50)),
    "tungsten": (4, "Tin", "The rarest metal of the bronze-smith. It comes from the ends of the earth - the Tin "
                 "Islands, the Ore Mountains, Bactria - and the Phoenicians keep the routes secret.", (150, 162, 176)),
    "steel": (5, "Iron", "Bloomery iron from Elba, Noricum and the land of the Chalybes: spearheads, swords and the "
              "tools of every smith.", (104, 106, 114)),
    "chromium": (6, "Horses", "Thessalian, Nisaean, Numidian: bred horses for the cavalry and the chariots.",
                 (120, 72, 40)),
    "coal": (7, "Grain", "Wheat and barley from the Nile, Babylonia, Sicily and the black earth of Scythia. Grain "
             "feeds the workers of the workshops.", (196, 140, 52)),
}

# real ancient sources: key -> [(lon, lat, amount, place)]
DEPOSITS = {
    "steel": [
        (10.3, 42.8, 8, "Elba and Populonia"), (14.6, 47.2, 7, "Noricum"), (37.5, 41.0, 7, "the Chalybes"),
        (-3.0, 43.2, 6, "Cantabria"), (-4.0, 38.3, 2, "the Sierra Morena"), (2.4, 47.1, 4, "the Bituriges"),
        (0.7, 45.2, 3, "the Petrocorii"), (0.3, 51.0, 3, "the Weald"), (8.0, 50.8, 4, "the Siegerland"),
        (14.5, 49.8, 3, "Bohemia"), (17.8, 44.2, 4, "Illyricum"), (23.0, 45.9, 4, "Dacia"),
        (22.4, 37.0, 3, "Laconia"), (23.6, 38.5, 2, "Euboea"), (23.3, 40.6, 3, "Chalcidice"),
        (34.7, 37.3, 3, "the Taurus"), (44.7, 41.3, 4, "Iberia of the Caucasus"), (45.5, 36.5, 3, "the Zagros"),
        (33.75, 16.9, 6, "Meroe"), (57.0, 30.3, 3, "Carmania"), (68.0, 36.5, 3, "Bactria"),
        (24.5, 41.8, 2, "the Rhodope"), (-1.5, 47.3, 2, "Armorica"), (30.0, 52.0, 2, "the Neuri"),
        (11.5, 57.5, 2, "Scandia"), (9.2, 33.9, 1, "the Djerid"), (-8.0, 40.5, 2, "Lusitania"),
        (6.2, 48.7, 3, "Lorraine"), (-2.6, 51.8, 2, "the Forest of Dean"), (10.6, 51.8, 2, "the Harz"),
        (10.2, 45.7, 2, "the Alpine valleys of the Cenomani"), (-1.8, 41.8, 3, "Moncayo"), (22.0, 41.0, 2, "Macedonia"),
        (16.1, 39.1, 1, "Bruttium"), (12.5, 42.4, 1, "the Sabine hills"), (5.5, 44.5, 2, "the Allobroges"),
        (-4.0, 56.5, 1, "Caledonia"), (2.0, 36.5, 1, "the Atlas of the Mauri"),
        (10.6, 43.05, 3, "Campiglia in Etruria"), (13.6, 41.7, 2, "the Volscian hills"), (14.8, 41.2, 2, "Samnium"), (7.7, 45.3, 2, "the Salassi"),
    ],
    "aluminium": [
        (33.0, 35.0, 10, "Cyprus"), (-6.6, 37.7, 8, "Tartessos"), (35.4, 30.6, 5, "Faynan and Timna"),
        (39.8, 38.3, 6, "Ergani"), (23.6, 38.46, 3, "Chalcis"), (10.9, 43.1, 4, "the Metal Hills of Etruria"),
        (8.9, 40.1, 3, "Sardinia"), (56.5, 24.2, 5, "Magan"), (45.0, 40.3, 3, "Armenia"),
        (13.1, 47.4, 3, "the Eastern Alps"), (-3.85, 53.3, 2, "the Great Orme"), (25.7, 42.4, 2, "Thrace"),
        (53.7, 33.3, 4, "Anarak"), (33.6, 26.0, 2, "the Eastern Desert"), (33.7, 28.9, 3, "the Sinai"),
        (22.2, 44.4, 3, "Moesia"), (-8.0, 37.9, 2, "Lusitania"), (60.5, 36.0, 2, "Parthia"),
        (16.1, 39.1, 3, "Temesa in Bruttium"), (-0.5, 42.6, 2, "the Pyrenees"), (11.0, 46.5, 2, "the Raetian Alps"),
        (24.0, 41.4, 2, "the Rhodope"), (-1.0, 37.6, 2, "Carthago Nova"), (7.0, 36.8, 1, "Numidia"),
        (11.6, 42.9, 3, "Monte Amiata"), (10.4, 45.9, 2, "the Camonni"), (15.4, 40.5, 1, "Lucania"),
    ],
    "tungsten": [
        (-5.2, 50.3, 9, "Belerion"), (-8.0, 42.5, 7, "the Cassiterides of Gallaecia"), (-3.3, 47.9, 3, "Armorica"),
        (13.0, 50.5, 4, "the Ore Mountains"), (10.6, 43.05, 2, "Campiglia in Etruria"), (34.6, 37.5, 2, "Kestel"),
        (19.5, 44.6, 1, "Mount Cer"), (34.0, 25.0, 1, "the Eastern Desert"), (66.5, 35.0, 4, "Bactria"),
        (-2.0, 47.3, 2, "the Loire mouth"), (-6.8, 41.5, 2, "the Durius valley"), (8.8, 39.5, 1, "Sardinia"),
        (67.5, 39.5, 3, "Sogdiana"), (49.0, 33.5, 1, "Media"),
        (10.9, 43.2, 1, "the Colline Metallifere"),
    ],
    "oil": [
        (16.5, 39.3, 6, "the Sila forest"), (22.6, 40.9, 4, "Macedonia"), (26.9, 39.8, 3, "Mount Ida"),
        (-0.9, 44.2, 3, "the Landes"), (41.7, 42.2, 3, "Colchis"), (42.8, 33.6, 6, "the bitumen of Is"),
        (35.5, 31.4, 3, "the Dead Sea"), (20.8, 37.75, 1, "Zakynthos"), (19.6, 40.6, 2, "the Nymphaeum of Apollonia"),
        (49.3, 32.0, 3, "Susiana"), (36.0, 34.2, 2, "the Lebanon"), (9.1, 42.1, 2, "Corsica"),
        (49.9, 40.4, 2, "the fire springs of the Caspian"), (34.0, 41.6, 2, "Paphlagonia"),
        (13.5, 42.3, 2, "the pines of the Apennines"), (8.8, 44.4, 2, "Liguria"),
    ],
    "rubber": [
        (35.9, 34.2, 6, "the cedars of Lebanon"), (22.6, 40.9, 4, "Macedonia"), (16.5, 39.3, 3, "the Sila"),
        (9.1, 42.1, 2, "Corsica"), (36.5, 41.2, 3, "Pontus"), (32.3, 41.3, 2, "Bithynia"), (33.0, 35.2, 2, "Cyprus"),
        (36.8, 37.0, 2, "the Amanus"),
        (13.5, 42.5, 4, "the Apennine forests"), (11.0, 43.3, 3, "the Ciminian forest"), (8.9, 44.4, 2, "Liguria"), (15.6, 39.3, 3, "Bruttium"),
    ],
    "chromium": [
        (22.3, 39.6, 6, "Thessaly"), (48.0, 34.5, 7, "the Nisaean plain"), (35.5, 38.7, 6, "Cappadocia"),
        (6.5, 36.0, 6, "Numidia"), (-4.0, 39.5, 3, "Celtiberia"), (16.0, 41.3, 4, "Apulia"), (14.3, 41.0, 2, "Campania"),
        (21.8, 32.7, 4, "Cyrenaica"), (26.0, 42.2, 3, "Thrace"), (60.0, 38.0, 4, "Parthia"), (64.0, 37.5, 3, "Margiana"),
        (45.0, 24.5, 2, "Arabia"), (3.0, 47.0, 3, "Gaul"), (19.5, 47.0, 3, "the Pannonian plain"),
        (40.0, 40.0, 4, "Armenia"),
        (11.4, 42.6, 2, "the Maremma"), (14.6, 41.4, 2, "Samnium"), (12.4, 45.5, 3, "the Veneti"), (13.7, 42.7, 1, "Picenum"),
    ],
    "coal": [
        (31.2, 30.8, 10, "the Nile Delta"), (31.0, 27.5, 6, "Middle Egypt"), (32.7, 25.7, 4, "Upper Egypt"),
        (44.4, 32.5, 8, "Babylonia"), (46.2, 31.3, 4, "Sumer"), (14.2, 37.5, 6, "Sicily"),
        (9.6, 36.6, 5, "the Bagradas valley"), (33.0, 46.8, 6, "the black earth of Scythia"), (14.4, 40.95, 3, "Campania"),
        (10.5, 45.0, 3, "the Po plain"), (22.3, 39.6, 2, "Thessaly"), (36.5, 35.8, 3, "the Orontes"),
        (35.4, 32.6, 2, "the Jezreel valley"), (36.0, 45.2, 3, "the Bosporan plain"), (27.5, 44.0, 2, "the Danube"),
        (21.8, 32.8, 2, "Cyrenaica"), (39.0, 36.8, 2, "Harran"),
        (12.5, 41.85, 3, "Latium"), (11.6, 42.8, 3, "Etruria"), (16.0, 41.3, 3, "Apulia"), (12.0, 44.4, 3, "the Po delta"), (15.3, 37.5, 2, "the plain of Catana"), (8.8, 39.9, 2, "the Campidano"),
    ],
}

# the land itself: key -> ({terrain: weight}, total for the world, zones [(polygon lon/lat, factor)])
STEPPE = [(26.5, 44.0), (27.0, 49.5), (45.0, 52.0), (66.0, 52.0), (66.0, 41.5), (52.0, 41.0), (40.0, 44.0)]
IRAN = [(44.0, 30.0), (44.0, 39.0), (62.0, 39.0), (66.0, 36.0), (62.0, 29.0)]
NORTH = [(-15.0, 54.0), (-15.0, 70.0), (70.0, 70.0), (70.0, 54.0)]          # beyond the grain lands
# Italy (the peninsula, the Po plain and Sicily) - round 25, Peti: "too few resources in Italy". The game is about
# Italy, so its land counts 3.5 times in every terrain pool (the world totals stay, the rest of the map gives a little).
ITALY = [(7.0, 44.0), (7.5, 46.5), (13.9, 46.6), (13.8, 45.5), (12.3, 44.3), (14.2, 42.4), (16.2, 41.9),
         (18.7, 40.3), (18.3, 39.8), (16.6, 38.4), (15.9, 37.7), (15.7, 36.6), (12.3, 37.6), (12.4, 38.3),
         (15.6, 38.3), (15.6, 39.6), (13.8, 41.0), (12.2, 41.5), (11.0, 42.4), (10.0, 43.9), (8.5, 44.2)]
TERRAIN = {
    "rubber": ({"forest": 1.0, "jungle": 0.6, "hills": 0.25, "mountain": 0.12}, 300, [(ITALY, 3.5)]),
    "chromium": ({"plains": 1.0, "hills": 0.2, "desert": 0.08}, 170, [(STEPPE, 3.0), (IRAN, 1.6), (ITALY, 3.5)]),
    "coal": ({"plains": 1.0, "urban": 1.5, "hills": 0.3, "marsh": 0.2}, 320, [(NORTH, 0.25), (ITALY, 3.5)]),
    # round 22 (Peti: "too few resources, and what there is sits in Persia"): every hill country digs a little
    # iron and copper, every pine forest boils some pitch - on top of the famous sources above. Iran's huge states
    # get less of it, so the new metal goes to Europe, Anatolia and Africa.
    "steel": ({"mountain": 1.0, "hills": 0.6, "forest": 0.15}, 75, [(IRAN, 0.4), (NORTH, 0.6), (ITALY, 3.5)]),
    "aluminium": ({"mountain": 1.0, "hills": 0.4}, 55, [(IRAN, 0.4), (NORTH, 0.4), (ITALY, 3.5)]),
    "oil": ({"forest": 0.7, "mountain": 0.3, "hills": 0.15}, 60, [(IRAN, 0.4), (ITALY, 3.5)]),
    "tungsten": ({"mountain": 0.4, "hills": 0.1}, 18, [(IRAN, 0.4), (ITALY, 3.5)]),
}
SCALE = {"steel": 2.4, "aluminium": 1.5, "tungsten": 1.2, "oil": 1.0, "rubber": 1.0, "chromium": 1.0, "coal": 1.0}
CAP = 24          # no state gets more than this of one resource
POWER = 0.55      # terrain: big states get more, but much less than in proportion to their size


def inside(x, y, poly):
    """ray casting: is (x, y) inside poly (list of (x, y))?"""
    n, hit = len(poly), False
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            hit = not hit
    return hit


def assign(M, states):
    """sets s["resources"] = {key: amount} on every playable state; returns a report (list of lines)"""
    play = [s for s in states if not s["waste"]]
    prov_state = {p: s for s in play for p in s["provinces"] if p in M.land}
    okm = np.zeros(max(M.provs) + 1, bool)
    okm[list(prov_state)] = True
    got = {id(s): defaultdict(float) for s in play}
    report, missed = [], []
    for key, pts in DEPOSITS.items():
        for lon, lat, amount, place in pts:
            x, y = to_xy(lon, lat)
            near = M.near(x, y, okm, 90)
            if not near:
                missed.append(f"{key} {place}")
                continue
            got[id(prov_state[near[0][1]])][key] += amount * SCALE[key]
    for key, (weights, total, zones) in TERRAIN.items():
        polys = [([to_xy(lo, la) for lo, la in poly], f) for poly, f in zones]
        raw = {}
        for s in play:
            v = 0.0
            for p in s["provinces"]:
                if p not in M.land:
                    continue
                w = weights.get(M.provs[p]["terrain"], 0.0)
                if w:
                    for poly, f in polys:
                        if inside(M.cx[p], M.cy[p], poly):
                            w *= f
                    v += M.provs[p]["px"] * w
            raw[id(s)] = v ** POWER
        k = total / (sum(raw.values()) or 1)
        for s in play:
            got[id(s)][key] += raw[id(s)] * k * SCALE[key]
    for s in play:
        # a fraction becomes one more unit with that chance (a fixed hash of state and resource, the same every run):
        # small states get their share now and then instead of never, and the world total stays as planned
        s["resources"] = {}
        for key, v in sorted(got[id(s)].items()):
            h = int(hashlib.md5(f"{s['id']}:{key}".encode()).hexdigest()[:8], 16) / 0x100000000
            n = min(CAP, int(v) + (1 if v - int(v) > h else 0))
            if n:
                s["resources"][key] = n
    for key, (frame, name, *_r) in RESOURCES.items():
        amounts = [s["resources"].get(key, 0) for s in play]
        n = sum(1 for a in amounts if a)
        report.append(f"{name:7} ({key:9}) {sum(amounts):4} in {n:3} states, most {max(amounts)}")
    if missed:
        report.append("no state near: " + ", ".join(missed))
    return report


# ---------------------------------------------------------------- icons (27 x 27 each, drawn 8x and scaled down)
S = 8
W = 27


def _parts(key, colour):
    """the icon as parts painted in order: [(draw(d, P), colour, outlined)] - every outlined part gets its own dark
    edge, so pieces lying on each other stay readable at 27 px"""
    parts = []

    def add(col, outlined=True):
        def deco(fn):
            parts.append((fn, col, outlined))
            return fn
        return deco
    if key == "oil":            # a clay pot brimming with black pitch, a drip down its side
        @add((176, 98, 58))
        def pot(d, P):
            d.chord(P((2, 9), (25, 28)), 0, 180, 255)
            d.rectangle(P((2, 17.5), (25, 19.5)), 255)

        @add(colour)
        def pitch(d, P):
            d.ellipse(P((4, 14.5), (23, 20.5)), 255)
            d.ellipse(P((9, 10), (18, 18)), 255)
            d.ellipse(P((18.5, 17), (21.5, 25)), 255)
    elif key == "aluminium":    # an oxhide ingot
        @add(colour)
        def ingot(d, P):
            d.polygon(P((2, 7), (8, 9.5), (19, 9.5), (25, 7), (22.5, 13.5), (25, 20), (19, 17.5), (8, 17.5), (2, 20),
                        (4.5, 13.5)), 255)

        @add((150, 78, 40), False)
        def hollow(d, P):
            d.ellipse(P((10, 12), (17, 15)), 255)
    elif key == "rubber":       # three logs, end on
        for x, y in ((2, 13), (13, 13), (7.5, 3.5)):
            @add((96, 62, 34))
            def bark(d, P, x=x, y=y):
                d.ellipse(P((x, y), (x + 12, y + 12)), 255)

            @add((214, 172, 112), False)
            def wood(d, P, x=x, y=y):
                d.ellipse(P((x + 2, y + 2), (x + 10, y + 10)), 255)

            @add((150, 104, 60), False)
            def ring(d, P, x=x, y=y):
                d.ellipse(P((x + 4.2, y + 4.2), (x + 7.8, y + 7.8)), 0, 255, int(0.9 * S))
    elif key == "tungsten":     # two round bun ingots
        for x, y in ((2, 10), (11, 4)):
            @add(colour)
            def bun(d, P, x=x, y=y):
                d.ellipse(P((x, y), (x + 14, y + 14)), 255)

            @add((230, 236, 242), False)
            def shine(d, P, x=x, y=y):
                d.ellipse(P((x + 3, y + 3), (x + 11, y + 11)), 0, 255, int(1.1 * S))
    elif key == "steel":        # two tapered currency bars of iron
        for dy in (8, 0):
            @add(colour)
            def bar(d, P, dy=dy):
                d.polygon(P((2, 13 + dy), (6, 8 + dy), (25, 6 + dy), (25, 10 + dy), (21, 15 + dy), (2, 16 + dy)), 255)
    elif key == "chromium":     # a horse's head with its mane
        @add(colour)
        def head(d, P):
            d.polygon(P((6, 26), (7, 16), (9.5, 10), (13.5, 4.5), (15.5, 1.5), (17, 4.5), (21, 8.5), (25.5, 15.5),
                        (24, 19.5), (19, 16.5), (17, 18), (19.5, 26)), 255)

        @add((48, 30, 20))
        def mane(d, P):
            d.polygon(P((6, 26), (7, 16), (9.5, 10), (13.5, 4.5), (12, 11), (10, 18), (9.5, 26)), 255)

        @add((20, 14, 10), False)
        def eye(d, P):
            d.ellipse(P((16.5, 8), (18.5, 10)), 255)
    elif key == "coal":         # two ears of wheat, crossed
        for top, root in (((7, 2), (17, 26)), ((20, 2), (10, 26))):
            @add((170, 130, 60))
            def stalk(d, P, top=top, root=root):
                d.line(P(top, root), 255, int(1.4 * S))
            (tx, ty), (rx, ry) = top, root
            for i in range(4):
                t = 0.08 + i * 0.13
                cx, cy = tx + (rx - tx) * t, ty + (ry - ty) * t
                for side in (-1, 1):
                    @add(colour)
                    def kernel(d, P, cx=cx, cy=cy, side=side):
                        d.ellipse(P((cx + side * 1.9 - 1.7, cy - 1.6), (cx + side * 1.9 + 1.7, cy + 1.9)), 255)
    return parts


def _icon(key, colour):
    pic = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    union = Image.new("L", (W, W), 0)
    for fn, col, outlined in _parts(key, colour):
        big = Image.new("L", (W * S, W * S), 0)
        fn(ImageDraw.Draw(big), lambda *pts: [(x * S, y * S) for x, y in pts])
        mask = big.resize((W, W), Image.LANCZOS)
        box = mask.getbbox() or (0, 0, W, W)
        grad = Image.new("L", (W, W), 0)                         # light at the top left of the part, dark below
        gh = max(1, box[3] - box[1])
        grad.paste(Image.linear_gradient("L").resize((W, gh)), (0, box[1]))
        grad.paste(255, (0, box[3], W, W))
        light = Image.new("RGBA", (W, W), tuple(min(255, int(c * 1.4 + 24)) for c in col) + (255,))
        dark = Image.new("RGBA", (W, W), tuple(int(c * 0.62) for c in col) + (255,))
        body = Image.composite(dark, light, grad)
        body.putalpha(mask)
        if outlined:
            edge = mask.point(lambda v: 255 if v > 50 else 0).filter(ImageFilter.MaxFilter(3))
            outline = Image.new("RGBA", (W, W), (18, 14, 10, 255))
            outline.putalpha(edge)
            pic = Image.alpha_composite(pic, outline)
        pic = Image.alpha_composite(pic, body)
        union = Image.composite(Image.new("L", (W, W), 255), union, mask.point(lambda v: 255 if v > 50 else 0))
    hi = Image.new("RGBA", (W, W), (255, 250, 235, 0))           # a soft highlight at the top left
    hl = Image.new("L", (W, W), 0)
    ImageDraw.Draw(hl).ellipse((3, 2, 13, 10), 60)
    hi.putalpha(Image.composite(hl.filter(ImageFilter.GaussianBlur(2)), Image.new("L", (W, W), 0), union))
    return Image.alpha_composite(pic, hi)


def _missing(icon):
    """the game's 'missing' look: the icon in an orange-red glow"""
    a = icon.getchannel("A").filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.6))
    glow = Image.new("RGBA", icon.size, (235, 90, 20, 0))
    glow.putalpha(a.point(lambda v: min(255, int(v * 1.6))))
    return Image.alpha_composite(glow, icon)


def write_files():
    strip = Image.new("RGBA", (W * 7, W), (0, 0, 0, 0))
    miss = Image.new("RGBA", (W * 7, W), (0, 0, 0, 0))
    for key, (frame, name, desc, colour) in RESOURCES.items():
        ic = _icon(key, colour)
        strip.alpha_composite(ic, ((frame - 1) * W, 0))
        miss.alpha_composite(_missing(ic), ((frame - 1) * W, 0))
    out = MOD / "gfx" / "interface"
    out.mkdir(parents=True, exist_ok=True)
    strip.save(out / "resources_strip.dds")
    miss.save(out / "missing_resources_strip.dds")
    loc = ["l_english:"]
    for key, (frame, name, desc, colour) in RESOURCES.items():
        ic = f"£resources_strip|{frame}"
        loc += [f' PRODUCTION_MATERIALS_{key.upper()}:0 "{name}"', f' {key}_desc:0 "{desc}"',
                f' state_resource_{key}:0 "{name}"', f' temporary_state_resource_{key}:0 "{name}"',
                f' country_resource_{key}:0 "{name}"', f' local_resources_{key}_factor:0 "{name} Gain Efficiency"',
                f' state_resource_cost_{key}:0 "{name} Consumption"', f' country_resource_cost_{key}:0 "{name} Consumption"',
                f' state_resources_{key}_factor:0 "Local Available {ic} {name}"',
                f' sabotage_{key}:0 "Sabotage {name}"']
    p = MOD / "localisation" / "english" / "replace" / "ante_resources_l_english.yml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(loc) + "\n", encoding="utf-8-sig", newline="\n")


def state_block(res):
    """the resources = { ... } lines of a state file (tools/world.py state_text)"""
    if not res:
        return []
    return ["\tresources = {"] + [f"\t\t{k} = {v}" for k, v in res.items()] + ["\t}"]


if __name__ == "__main__":
    write_files()
    print("written: resource icons and names (state amounts come with python tools/world.py)")
