"""The ancient tech tree (reads the game once, like tools/army.py and tools/buildings.py).

Source: tools/data/tech_tree.py. Writes
  common/technologies/ante_technologies.txt     (replace_path: the base game's techs are gone)
  common/technology_tags/00_technology.txt      the game's file with the folders changed: one naval page for everyone,
                                                no air pages, the base armour page for everyone
  interface/countrytechtreeview.gui             the game's file with the year labels in AUC (YEAR_AUC)
  interface/ante_technologies.gfx + gfx/interface/technologies/ante_*.dds   icons (own art, CC0)
  localisation/english/replace/ante_technologies_l_english.yml
Run AFTER tools/world.py (it wipes localisation/english/replace) and tools/army.py (equipment pictures).

Rows: every page of the tech screen has its year labels at fixed places. A tech of year A goes to the row of the
label whose AUC year (YEAR_AUC) is nearest to A on that page, and gets exactly that year as start_year, so the
labels, the rows and the ahead-of-time penalty agree.
"""
import os
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

TOOLS = Path(__file__).resolve().parent
MOD = TOOLS.parent
sys.path.insert(0, str(TOOLS))
from data.tech_tree import TECHS, LANES, TABS, EQUIPMENT_NAMES  # noqa: E402
import army  # noqa: E402

# base-game year label -> AUC year shown instead (and used as start_year)
YEAR_AUC = {1918: 245, 1922: 245, 1924: 260, 1933: 275, 1934: 280, 1935: 285, 1936: 290, 1937: 300, 1938: 305,
            1939: 320, 1940: 335, 1941: 365, 1942: 395, 1943: 425, 1944: 455, 1945: 485, 1946: 515, 1950: 545}
FOLDERS = {   # page: (name, description)
    "infantry_folder": ("Arms and Armour", "Weapons, armour and the drill of the foot soldiers."),
    "support_folder": ("Auxiliaries and Supply", "Baggage, scouts, camps and surgeons."),
    "armour_folder": ("Horse and Chariot", "Horsemen, chariots and war elephants."),
    "artillery_folder": ("Siege Craft", "Engines of war, walls and the art of taking cities."),
    "naval_folder": ("Seafaring", "Oared warships, harbours and landings."),
    "electronics_folder": ("Learning", "Writing, philosophy, mathematics, astronomy and medicine."),
    "industry_folder": ("Crafts and Building", "Metalwork, building, farming and mining."),
}
ANCHOR = {   # page -> the base-game grid box whose place our tree roots take (see main)
    "infantry_folder": "support_weapons_tree", "support_folder": "tech_support_tree", "armour_folder": "gwtank_tree",
    "artillery_folder": "gw_artillery_tree", "naval_folder": "early_destroyer_tree",
    "industry_folder": "basic_machine_tools_tree", "electronics_folder": "electronic_mechanical_engineering_tree"}
HIDDEN = ["nsb_armour_folder", "mtgnavalfolder", "mtgnavalsupportfolder", "air_techs_folder", "bba_air_techs_folder"]
CATEGORY = {"infantry_folder": "infantry_weapons", "support_folder": "infantry_tech", "armour_folder": "armor",
            "artillery_folder": "artillery", "naval_folder": "naval_equipment", "electronics_folder": "electronics",
            "industry_folder": "industry construction_tech"}
NOT_MODIFIERS = {"naval_invasion_capacity", "naval_invasion_prep_days", "naval_invasion_division_cap",
                 "naval_invasion_plan_cap", "enable_equipments", "enable_subunits"}


def game_dir():
    return army.game_dir()


def strip_comments(text):
    return "\n".join(line.split("#")[0] for line in text.splitlines())


def blocks(text, start):
    """top-level 'key = { ... }' blocks inside text[start:] at depth 1 -> [(key, body)]"""
    out, depth, i, key_start = [], 0, start, None
    for m in re.finditer(r"([A-Za-z_0-9@.]+)\s*=\s*\{|\{|\}", text[start:]):
        tok = m.group(0)
        if tok.endswith("{"):
            if depth == 1 and m.group(1):
                key_start = (m.group(1), start + m.end())
            depth += 1
        else:
            depth -= 1
            if depth == 1 and key_start:
                out.append((key_start[0], text[key_start[1]:start + m.start()]))
                key_start = None
            if depth == 0:
                break
    return out


def vanilla_rows(g):
    """page -> {base-game year: row y} (most common y of that year's techs)"""
    rows = {}
    for fp in (g / "common" / "technologies").glob("*.txt"):
        text = strip_comments(fp.read_text(encoding="utf-8-sig", errors="replace"))
        consts = {k: int(v) for k, v in re.findall(r"(@\d+)\s*=\s*(-?\d+)", text)}
        m = re.search(r"technologies\s*=\s*\{", text)
        if not m:
            continue
        for key, body in blocks(text, m.start()):
            ym = re.search(r"start_year\s*=\s*(\d+)", body)
            for fm in re.finditer(r"name\s*=\s*(\w+)\s+position\s*=\s*\{\s*x\s*=\s*(-?[\w@]+)\s+y\s*=\s*(-?[\w@]+)", body):
                if not ym:
                    continue
                y = fm.group(3)
                y = consts.get(y, None) if y.startswith("@") else int(y)
                if y is None:
                    continue
                rows.setdefault(fm.group(1), {}).setdefault(int(ym.group(1)), []).append(y)
    return {f: {yr: max(set(ys), key=ys.count) for yr, ys in d.items()} for f, d in rows.items()}


def fill_rows(rows, labels):
    """a label year without a base-game tech on that page: its row from the neighbouring known years
    (interpolated between them, or extended from the last two)"""
    for f, yrs in labels.items():
        known = rows.setdefault(f, {})
        pts = sorted(p for p in known.items() if p[0] >= 1930) or sorted(known.items())   # 1918 = 'pre-war' row
        if len(pts) < 2:
            continue
        for yr in sorted(yrs):
            if yr in known:
                continue
            lo = [p for p in pts if p[0] < yr]
            hi = [p for p in pts if p[0] > yr]
            a, b = (lo[-1], hi[0]) if lo and hi else ((pts[0], pts[1]) if hi else (pts[-2], pts[-1]))
            known[yr] = int(round(a[1] + (b[1] - a[1]) * (yr - a[0]) / (b[0] - a[0])))
    return rows


def gui_labels(gui):
    """page -> set of base-game years that have a visible label"""
    out, cur = {}, None
    for line in gui.splitlines():
        m = re.search(r'name\s*=\s*"(\w+folder)"', line)
        if m:
            cur = m.group(1)
        m = re.search(r'^\s*text\s*=\s*"(19\d\d)"', line)
        if m and cur:
            out.setdefault(cur, set()).add(int(m.group(1)))
    return out


# AUC of the first and the last labelled row of every page. Round 17: 485 = far too slow. Round 18: 365 still left
# 15-100 years between a tech and the next one while a tech took 6-15 months (BASE_TECH_COST 180): players ran out
# of time and paid the ahead-of-time penalty everywhere. Round 21: 280, with BASE_TECH_COST 270 (common/defines) -
# 66 techs at 2-3 research slots take about 30-40 years, the length of the tree.
FIRST, LAST = 245, 280
YEAR_ROUND = 1           # years on the labels and start_year are rounded to this (was 5: rows a few years apart merged)
DESIGN_LAST = 485        # the years in tech_tree.py run 245..485 and are squeezed into FIRST..LAST
WIDE = {"armour_folder", "artillery_folder", "industry_folder", "electronics_folder"}  # time runs down: boxes side by side need 3 slots
STEP = {"naval_folder": 3}  # rows used: multiples of this from the top row (big ship boxes need more room)
# lane x of tech_tree.py -> grid column. The learning page has 60 px slots and 204 px wide boxes: 3 slots (180 px)
# made neighbouring boxes overlap, 4 slots leave a gap like on the other pages.
SPREAD = {"armour_folder": 1.5, "artillery_folder": 1.5, "industry_folder": 1.5, "electronics_folder": 2}


def column(folder, x):
    return int(x * SPREAD[folder]) if folder in SPREAD else x


# How the game draws a tech box (interface/countrytechtreeview.gui):
#  - a tech that enables equipment gets the BIG box, every other tech the SMALL one (72 x 72). The learning and
#    crafts pages have no small box: everything is big there.
#  - small box: the icon's top left corner sits at (3, 3) - an icon must be 64 x 64 to look centred (like the game's).
#  - big box: the icon is centred on a point: arms/support/horse/siege in the middle of the box (wide production
#    pictures, about 110 x 30), the naval box on its right part (the picture may be ~70 wide, or it sticks out),
#    learning and crafts on the square at the left (64 x 64).
# Round 17 used 109 x 30 production pictures and 61 x 54 glyphs everywhere: off-centre in the small boxes and
# sticking out of the starting techs' boxes.
NO_SMALL_BOX = {"industry_folder", "electronics_folder"}
BIG_PICTURE = {"naval_folder": (72, 40)}       # other pages: (112, 34)


def is_big(folder, eff):
    return folder in NO_SMALL_BOX or "enable_equipments" in eff


def object_picture(key, w, h):
    """the production picture of an equipment / hull, drawn at w x h and cropped to its content"""
    mask = army.silhouette(key, w, h)
    pic = shaded(mask, army.MATERIAL.get(key, (120, 82, 48)))
    return pic.crop(pic.getbbox())


def fit(pic, w, h):
    """pic scaled down (never up by more than 1.6x) to fit w x h, centred on a transparent w x h canvas"""
    s = min(w / pic.width, h / pic.height, 1.6)
    if abs(s - 1) > 0.02:
        pic = pic.resize((max(1, round(pic.width * s)), max(1, round(pic.height * s))), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(pic, ((w - pic.width) // 2, (h - pic.height) // 2))
    return out


def numeral(pic, level):
    """II / III in the bottom right corner of a big picture (the better models)"""
    d = ImageDraw.Draw(pic)
    txt = "I" * level
    x, y = pic.width - 4 - 4 * len(txt), pic.height - 12
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        d.text((x + dx, y + dy), txt, fill=(30, 22, 14, 255))
    d.text((x, y), txt, fill=(235, 215, 160, 255))


def tech_icon(folder, icon, eff):
    big = is_big(folder, eff)
    if icon.startswith("eq:"):
        key = icon[3:]
        wide = key.endswith("_hull")
        src = object_picture(key, 150 if wide else 96, 42)
    else:
        src = shaded(glyph(icon), GLYPH_COLOUR[icon])         # drawn on its 61 x 54 design grid
        src = src.crop(src.getbbox())
    if not big or folder in NO_SMALL_BOX or not icon.startswith("eq:"):
        return fit(src, 58, 58).crop((-3, -3, 61, 61))          # 64 x 64, content centred
    w, h = BIG_PICTURE.get(folder, (112, 34))
    pic = fit(src, w - 12, h)
    lvl = re.search(r"_equipment_(\d)\b|_hull_(\d)\b", eff)
    level = int(next(g for g in lvl.groups() if g)) if lvl else 1
    if level > 1:
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        canvas.alpha_composite(pic, (0, 0))
        numeral(canvas, level)
        return canvas
    return fit(pic.crop(pic.getbbox()), w, h)


MAX_GAP = 6   # years between two neighbouring year labels of a page, at most (research must keep moving)


def page_scale(folder, rows, labels):
    """the rows of the page's year labels, top to bottom: label i is year FIRST + i * step, step = the even share of
    FIRST..LAST but never more than MAX_GAP years (a page with few labels ends earlier than LAST)"""
    ys = sorted({rows[folder][yr] for yr in labels.get(folder, set()) if yr in rows.get(folder, {})})
    assert len(ys) >= 2, f"no rows on {folder}"
    return ys


def auc_of(y, scale):
    ys = scale
    step = min(MAX_GAP, (LAST - FIRST) / (len(ys) - 1))
    pts = [(yy, FIRST + i * step) for i, yy in enumerate(ys)]
    if y <= ys[0]:
        a, b = pts[0], pts[1]
    elif y >= ys[-1]:
        a, b = pts[-2], pts[-1]
    else:
        a, b = next((p, q) for p, q in zip(pts, pts[1:]) if p[0] <= y <= q[0])
    year = a[1] + (b[1] - a[1]) * (y - a[0]) / (b[0] - a[0])
    return int(round(year / YEAR_ROUND) * YEAR_ROUND)


def place(folder, auc, rows, labels):
    scale = page_scale(folder, rows, labels)
    y0, y1 = scale[0], scale[-1]
    step = STEP.get(folder, 2)
    page_last = auc_of(y1, scale)   # the page's own last year (earlier than LAST when MAX_GAP shortens it)
    auc = FIRST + (auc - FIRST) * (page_last - FIRST) / (DESIGN_LAST - FIRST)
    cands = list(range(y0, y1 + 1, step))
    y = min(cands, key=lambda c: (abs(auc_of(c, scale) - auc), c))
    return y, auc_of(y, scale)


# ---------------------------------------------------------------- icons
def glyph(kind, w=61, h=54):
    S = 4
    im = Image.new("L", (w * S, h * S), 0)
    d = ImageDraw.Draw(im)

    def P(*pts):
        return [(x * S, y * S) for x, y in pts]
    cx, cy = w / 2, h / 2
    if kind == "scroll":
        d.rectangle(P((14, 14), (47, 40)), 255)
        d.ellipse(P((8, 10), (20, 44)), 255)
        d.ellipse(P((41, 10), (53, 44)), 255)
        for y in (20, 26, 32):
            d.line(P((22, y), (40, y)), 0, 2 * S)
    elif kind == "column":
        d.rectangle(P((14, 8), (47, 13)), 255)
        d.rectangle(P((12, 42), (49, 47)), 255)
        for x in (18, 27, 36):
            d.rectangle(P((x, 14), (x + 6, 41)), 255)
    elif kind == "wheel":
        d.ellipse(P((10, 6), (51, 47)), 255)
        d.ellipse(P((16, 12), (45, 41)), 0)
        d.ellipse(P((26, 22), (35, 31)), 255)
        for a, b in (((30.5, 8), (30.5, 45)), ((12, 26.5), (49, 26.5)), ((17, 13), (44, 40)), ((44, 13), (17, 40))):
            d.line(P(a, b), 255, 3 * S)
    elif kind == "coin":
        d.ellipse(P((10, 6), (51, 47)), 255)
        d.ellipse(P((15, 11), (46, 42)), 0)
        d.ellipse(P((17, 13), (44, 40)), 255)
        d.polygon(P((24, 34), (30.5, 16), (37, 34)), 0)
    elif kind == "anvil":
        d.polygon(P((6, 14), (52, 14), (52, 22), (40, 26), (36, 36), (44, 44), (16, 44), (24, 36), (20, 26), (6, 20)), 255)
    elif kind == "wall":
        d.rectangle(P((6, 20), (55, 46)), 255)
        for x in (6, 18, 30, 42):
            d.rectangle(P((x, 12), (x + 8, 20)), 255)
        for y, off in ((27, 0), (34, 6), (41, 0)):
            d.line(P((6, y), (55, y)), 0, S)
            for x in range(6 + off, 55, 12):
                d.line(P((x, y - 7), (x, y)), 0, S)
    elif kind == "ship":
        d.polygon(P((4, 30), (56, 30), (50, 40), (12, 40)), 255)
        d.polygon(P((56, 30), (60, 36), (52, 36)), 255)
        d.line(P((30, 30), (30, 8)), 255, 2 * S)
        d.polygon(P((18, 10), (42, 10), (40, 26), (20, 26)), 255)
        for x in range(14, 50, 6):
            d.line(P((x, 40), (x - 4, 48)), 255, S)
    elif kind == "horse":
        d.polygon(P((16, 48), (20, 30), (24, 18), (32, 8), (40, 8), (50, 22), (46, 26), (38, 20), (36, 30), (40, 48)), 255)
        d.polygon(P((30, 10), (22, 16), (20, 26)), 255)
    elif kind == "eye":
        d.ellipse(P((6, 14), (55, 40)), 255)
        d.ellipse(P((20, 15), (41, 39)), 0)
        d.ellipse(P((25, 20), (36, 34)), 255)
    elif kind == "star":
        pts = []
        import math
        for i in range(16):
            r = 22 if i % 2 == 0 else 9
            a = math.pi * i / 8
            pts.append((cx + r * math.sin(a), cy - r * math.cos(a)))
        d.polygon(P(*pts), 255)
    elif kind == "cup":
        d.polygon(P((14, 10), (47, 10), (42, 28), (19, 28)), 255)
        d.rectangle(P((28, 28), (33, 40)), 255)
        d.rectangle(P((18, 40), (43, 46)), 255)
        d.line(P((20, 4), (40, 46)), 0, S)
    elif kind == "laurel":
        for side in (-1, 1):
            for i in range(6):
                y = 42 - i * 6
                x = cx + side * (16 - abs(i - 3) * 1.5)
                d.ellipse(P((x - 5, y - 3), (x + 5, y + 3)), 255)
        d.line(P((cx - 14, 44), (cx + 14, 44)), 255, 2 * S)
    elif kind == "helmet":
        d.chord(P((12, 6), (49, 44)), 180, 360, 255)
        d.rectangle(P((12, 25), (22, 46)), 255)
        d.rectangle(P((39, 25), (49, 46)), 255)
        d.rectangle(P((28, 25), (33, 38)), 255)
        d.polygon(P((20, 6), (41, 6), (36, 0), (25, 0)), 255)
    elif kind == "sword":
        d.polygon(P((28, 4), (33, 4), (34, 34), (30.5, 40), (27, 34)), 255)
        d.rectangle(P((20, 34), (41, 38)), 255)
        d.rectangle(P((28.5, 38), (32.5, 48)), 255)
        d.ellipse(P((26, 46), (35, 52)), 255)
    elif kind == "tent":
        d.polygon(P((6, 46), (30.5, 8), (55, 46)), 255)
        d.polygon(P((24, 46), (30.5, 28), (37, 46)), 0)
    elif kind == "catapult":     # an engine on wheels with its throwing arm raised
        d.rectangle(P((8, 34), (50, 40)), 255)
        d.ellipse(P((8, 36), (22, 50)), 255)
        d.ellipse(P((36, 36), (50, 50)), 255)
        d.polygon(P((26, 34), (30, 18), (34, 34)), 255)
        d.line(P((18, 36), (50, 6)), 255, 3 * S)
        d.chord(P((44, 0), (58, 12)), 0, 180, 255)
    elif kind == "tower":
        d.polygon(P((22, 48), (24, 16), (37, 16), (39, 48)), 255)
        d.rectangle(P((20, 12), (41, 16)), 255)
        d.ellipse(P((24, 2), (37, 13)), 255)
    elif kind == "wheat":
        d.line(P((30.5, 48), (30.5, 10)), 255, 2 * S)
        for i in range(5):
            y = 12 + i * 7
            d.ellipse(P((21, y), (30, y + 6)), 255)
            d.ellipse(P((31, y), (40, y + 6)), 255)
    elif kind == "pick":
        d.line(P((16, 48), (40, 14)), 255, 3 * S)
        d.chord(P((14, 4), (58, 34)), 200, 340, 255)
    else:
        raise KeyError(kind)
    return im.resize((w, h), Image.LANCZOS)


def shaded(mask, base):
    w, h = mask.size
    grad = Image.linear_gradient("L").resize((w, h))
    light = Image.new("RGBA", (w, h), tuple(min(255, int(c * 1.35)) for c in base) + (255,))
    dark = Image.new("RGBA", (w, h), tuple(int(c * 0.6) for c in base) + (255,))
    body = Image.composite(dark, light, grad)
    edge = Image.eval(mask, lambda v: 255 if v > 0 else 0).filter(ImageFilter.MaxFilter(3))
    outline = Image.new("RGBA", (w, h), (30, 22, 14, 255))
    outline.putalpha(edge)
    body.putalpha(mask)
    obj = Image.alpha_composite(outline, body)
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shadow.putalpha(mask.filter(ImageFilter.GaussianBlur(1.5)).point(lambda v: v // 2))
    pic = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pic.alpha_composite(shadow, (2, 2))
    pic.alpha_composite(obj, (0, 0))
    return pic


GLYPH_COLOUR = {"scroll": (205, 180, 130), "column": (200, 196, 186), "wheel": (150, 104, 58), "coin": (212, 170, 60),
                "anvil": (120, 120, 126), "wall": (176, 160, 130), "ship": (140, 96, 56), "horse": (126, 76, 44),
                "eye": (190, 170, 140), "star": (220, 190, 90), "cup": (196, 150, 64), "laurel": (110, 150, 70),
                "helmet": (196, 150, 64), "catapult": (150, 104, 58), "sword": (170, 170, 176), "tent": (190, 170, 130), "tower": (190, 180, 160),
                "wheat": (214, 180, 90), "pick": (130, 120, 110)}


# ---------------------------------------------------------------- the tech screen (a copy of the game's gui)
def block_end(lines, i):
    """index of the line that closes the block opened on line i (braces after '#' do not count)"""
    depth = 0
    for j in range(i, len(lines)):
        code = lines[j].split("#")[0]
        depth += code.count("{") - code.count("}")
        if depth <= 0 and j > i or (depth == 0 and "{" in code and "}" in code):
            return j
    return len(lines) - 1


# what does not belong on an ancient tech page: the photographs behind the trees (soldiers, tanks, guns,
# a submarine, factories), the captions of the modern lanes ("WEAPONS & EQUIPMENT", "ANTI-AIR", "DESTROYERS",
# "SYNTHETIC OIL" ...) and the empty frames of the train designer on the support page
MODERN = [
    ("iconType", re.compile(r'spriteType\s*=\s*"GFX_\w*(techtree_bg|armortech_bg|wonderweapons_bg)"')),
    ("instantTextBoxType", re.compile(r'text\s*=\s*"\w*(TITLE|SUBTITLE)\w*"')),
    ("containerWindowType", re.compile(r'name\s*=\s*"tiled_research_bg\w*"')),
    # the learning page has a second year column for the game's wonder-weapon tree: its years do not match ours
    ("containerWindowType", re.compile(r'name\s*=\s*"wonderweapon_year"')),
]


def strip_modern(lines):
    pages = [(i, m.group(1)) for i, l in enumerate(lines) if (m := re.search(r'^\t\t\tname = "(\w+folder)"', l))]
    drop = []
    for n, (i0, folder) in enumerate(pages):
        if folder not in FOLDERS:
            continue
        i1 = pages[n + 1][0] if n + 1 < len(pages) else len(lines)
        i = i0
        while i < i1:
            m = re.match(r"^\s*(iconType|instantTextBoxType|containerWindowType)\s*=\s*\{", lines[i])
            if m:
                j = block_end(lines, i)
                # a container is judged by its own name only (it holds other elements, a whole page even)
                body = "\n".join(lines[i:min(j, i + 3) + 1] if m.group(1) == "containerWindowType" else lines[i:j + 1])
                if any(kind == m.group(1) and pat.search(body) for kind, pat in MODERN):
                    drop.append((i, j))
                    i = j + 1
                    continue
            i += 1
    # not deleted: the game looks some of these elements up by name and then does not open the research screen
    # at all (seen 2026-11-14). They stay, but show nothing: an empty picture, an empty caption, a frame far
    # outside the page.
    for i, j in drop:
        for k in range(i, j + 1):
            lines[k] = re.sub(r'spriteType\s*=\s*"GFX_\w+"', f'spriteType = "{BLANK}"', lines[k])
            lines[k] = re.sub(r'text\s*=\s*"\w*(TITLE|SUBTITLE)\w*"', 'text = ""', lines[k])
        if re.match(r"^\s*containerWindowType", lines[i]):
            k = next(k for k in range(i, j) if re.search(r"^\s*position\s*=", lines[k]))
            lines[k] = re.sub(r"position\s*=\s*\{[^}]*\}", "position = { x = -9000 y = -9000 }", lines[k])
    return lines


BLANK = "GFX_ante_blank"     # a 1 x 1 transparent picture (interface/ante_technologies.gfx)


def lane_key(folder, x):
    return f"ANTE_TECH_LANE_{folder.upper()}_{x}"


def lane_labels(folder, block, top_row):
    """the headings of a page's lanes, in a container with the place and size of the page's grid box. Written
    BEFORE the grid boxes: these stay on top for the mouse.
    Measured in game (2026-11-14): a grid box with a size lays its techs out from the MIDDLE of that size (the
    horse page's box is 80 % wide: the tree stands in the middle of the screen), so the headings are anchored to
    the container's middle too (orientation center_up / center_left; a box without a size has its middle at its
    corner). On the pages where time runs to the right a row of boxes begins 100 px below the grid's y and the
    text box draws its text 37 px below its y: a heading at lane * slot - 67 ends just above its row. On the
    pages where time runs down the middle of a column is its x (+ the box's half width, see above)."""
    text = "\n".join(block)
    pos = re.search(r"position\s*=\s*\{[^}]*\}", text).group(0)
    size = re.search(r"^\s*size\s*=\s*\{[^}]*\}", text, re.M)
    size = size.group(0).strip() if size else "size = { width = 0 height = 0 }"
    slot = int(re.search(r"slotsize\s*=\s*\{\s*width\s*=\s*(\d+)", text).group(1))
    across = re.search(r'format\s*=\s*"(\w+)"', text).group(1) == "LEFT"     # LEFT: time runs to the right
    out = ["\t\t\tcontainerWindowType = {", f'\t\t\t\tname = "ante_{folder}_lanes"', f"\t\t\t\t{pos}",
           f"\t\t\t\t{size}", "\t\t\t\tclipping = no"]
    # time runs to the right: the rows begin lower by half the box's height (+10) when it has one (naval page)
    h = re.search(r"height\s*=\s*(\d+)\s*\}", size)
    drop = int(h.group(1)) // 2 + 10 if across and h and int(h.group(1)) else 0
    for x in LANES.get(folder, {}):
        if across:   # a heading above every row of boxes, at the left edge
            px, py, width, fmt, orient = 0, x * slot - 67 + drop, 500, "left", "upper_left"
        else:        # a heading above every column, centred on its boxes (the column's middle is its x)
            width = 200
            px, py, fmt, orient = column(folder, x) * slot - width // 2, top_row * slot - 38, "centre", "center_up"
        out += ["\t\t\t\tinstantTextBoxType = {", f'\t\t\t\t\tname = "ante_lane_{x}"',
                f"\t\t\t\t\tposition = {{ x = {px} y = {py} }}", f"\t\t\t\t\torientation = {orient}",
                '\t\t\t\t\tfont = "hoi_22tech"', "\t\t\t\t\tborderSize = { x = 0 y = 0 }",
                f'\t\t\t\t\ttext = "{lane_key(folder, x)}"', f"\t\t\t\t\tmaxWidth = {width}",
                "\t\t\t\t\tmaxHeight = 26", f"\t\t\t\t\tformat = {fmt}", "\t\t\t\t}"]
    return out + ["\t\t\t}"]


def fix_templates(lines):
    """the boxes and the tab row"""
    # The horse page draws its techs without equipment in a wide box but puts the icon at the corner (3, 3)
    # like in a small one (seen in game 2026-11-14): give that template the big box's size and centred icon.
    i = next(i for i, l in enumerate(lines) if 'name = "techtree_armour_folder_small_item"' in l)
    j = block_end(lines, i - 1)
    for k in range(i, j):
        lines[k] = lines[k].replace("position = { x=0 y=0 }", "position = { x=-55 y=0 }") \
                           .replace("size = { width = 72 height = 72 }", "size = { width = 183 height = 84 }")
        if re.search(r'name\s*=\s*"Icon"', lines[k]) and re.search(r"position\s*=\s*\{\s*x=3 y=3\s*\}", lines[k + 1]):
            lines[k + 1] = lines[k + 1].replace("x=3 y=3", "x=74 y=50") + "\n\t\t\tcenterposition = yes"
    # the tabs of the hidden pages (two naval DLC pages, two air pages) left a gap before learning and crafts
    i = next(i for i, l in enumerate(lines) if 'name = "folder_tabs"' in l)
    j = block_end(lines, i - 1)
    for k in range(i, j):
        lines[k] = re.sub(r"x\s*=\s*645(\s)", r"x = 467\1", lines[k])
        lines[k] = re.sub(r"x=645\}", "x=467}", lines[k])
        lines[k] = re.sub(r"x\s*=\s*734(\s)", r"x = 556\1", lines[k])
        lines[k] = re.sub(r"x=734\}", "x=556}", lines[k])
    return "\n".join(lines).split("\n")


TAB_FILES = {"infantry_folder": "techtree_infantry_tab.dds", "support_folder": "techtree_support_tab.dds",
             "armour_folder": "techtree_tank_tab.dds", "artillery_folder": "techtree_artillery_tab.dds",
             "naval_folder": "techtree_naval_tab.dds", "electronics_folder": "techtree_engineering_tab.dds",
             "industry_folder": "techtree_industry_tab.dds"}


def write_tabs(g):
    """the page tabs: the game's frame (2 frames side by side: active, inactive) with the helmet, soldier, tank, gun,
    anchor, valve and factory painted out and an ancient glyph in the same colour painted in"""
    out = MOD / "gfx" / "interface" / "techtree"
    out.mkdir(parents=True, exist_ok=True)
    for folder, fname in TAB_FILES.items():
        src = Image.open(g / "gfx" / "interface" / "techtree" / fname).convert("RGBA")
        w, h = src.size
        fw = w // 2
        raw = [src.crop((f * fw, 0, (f + 1) * fw, h)) for f in range(2)]
        # the old picture: coloured pixels well inside the frame (the inactive frame's picture is dimmer: its
        # mask is the union of a lower threshold and the active frame's mask)
        masks, colours = [], []
        for f, fr in enumerate(raw):
            px = fr.load()
            mask = Image.new("L", fr.size, 0)
            mp = mask.load()
            col, n = [0, 0, 0], 0
            lo_sat, lo_val = (22, 45) if f == 0 else (10, 28)
            for y in range(8, h - 8):
                for x in range(10, fw - 10):
                    r, gg, b, a = px[x, y]
                    if max(r, gg, b) - min(r, gg, b) > lo_sat and max(r, gg, b) > lo_val:
                        mp[x, y] = 255
                        col[0] += r; col[1] += gg; col[2] += b; n += 1
            colours.append(tuple(int(c / max(n, 1)) for c in col))
            masks.append(mask)
        masks[1] = Image.composite(Image.new("L", masks[1].size, 255), masks[1], masks[0])
        frames = []
        for f, fr in enumerate(raw):
            px = fr.load()
            colour = colours[f]
            mask = masks[f].filter(ImageFilter.MaxFilter(5))
            mp = mask.load()
            bb = mask.getbbox() or (0, 0, 0, 0)
            # paint it out: the frame's fine dark grid repeats, so a clean 8 px wide strip at the left of the
            # inside is repeated across the hole
            x0 = 14
            for y in range(h):
                for x in range(fw):
                    if mp[x, y]:
                        px[x, y] = px[x0 + (x - x0) % 8, y]
            # the new glyph, centred where the old picture was
            gl = glyph(TABS[folder])
            gl = gl.crop(gl.getbbox())
            s = min(34 / gl.width, 30 / gl.height)
            gl = gl.resize((max(1, round(gl.width * s)), max(1, round(gl.height * s))), Image.LANCZOS)
            body = Image.new("RGBA", gl.size, colour + (255,))
            shade = Image.linear_gradient("L").resize(gl.size).point(lambda v: 255 - v // 3)
            body = Image.composite(body, Image.new("RGBA", gl.size, tuple(int(c * 0.7) for c in colour) + (255,)), shade)
            body.putalpha(gl)
            cx = (bb[0] + bb[2]) // 2 if bb[2] else fw // 2
            cy = (bb[1] + bb[3]) // 2 if bb[3] else h // 2
            fr.alpha_composite(body, (cx - gl.width // 2, cy - gl.height // 2))
            frames.append(fr)
        tab = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        tab.paste(frames[0], (0, 0))
        tab.paste(frames[1], (fw, 0))
        tab.save(out / fname)


# ---------------------------------------------------------------- writers
def write(rel, text, bom=False):
    p = MOD / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8-sig" if bom else "utf-8", newline="\n")


def main():
    g = game_dir()
    gui = (g / "interface" / "countrytechtreeview.gui").read_text(encoding="utf-8-sig", errors="replace")
    labels = gui_labels(gui)
    rows = fill_rows(vanilla_rows(g), labels)
    mods_doc = (g / "documentation" / "modifiers_documentation.md").read_text(encoding="utf-8", errors="replace")
    known = set(re.findall(r"^## (\w+)", mods_doc, re.M))
    keys = {t[0] for t in TECHS}
    children = {}
    for t in TECHS:
        for p in t[6]:
            assert p in keys, f"{t[0]}: unknown prerequisite {p}"
            children.setdefault(p, []).append(t[0])
    out = ["# Generated by tools/tech.py from tools/data/tech_tree.py - the ancient tech tree", "technologies = {"]
    loc = ["l_english:"]
    sprites = ["# Generated by tools/tech.py - tech icons (own art, CC0)", "spriteTypes = {"]
    used, placed, tops = set(), {}, {}
    icon_dir = MOD / "gfx" / "interface" / "technologies"
    icon_dir.mkdir(parents=True, exist_ok=True)
    for key, name, desc, folder, x, auc, pre, eff, icon, cost in TECHS:
        y, year = place(folder, auc, rows, labels)
        x = column(folder, x)
        assert (folder, x, y) not in used, f"{key}: two techs at {folder} {x},{y}"
        used.add((folder, x, y))
        placed[key] = year
        for line in eff.splitlines():
            m = re.match(r"^(\w+)\s*=\s*[-\d.]+$", line.strip())
            if m and m.group(1) not in NOT_MODIFIERS and not re.match(r"production_speed_\w+_factor$", m.group(1)):
                assert m.group(1) in known, f"{key}: unknown modifier {m.group(1)}"
        b = [f"\t{key} = {{"]
        b += ["\t\t" + line for line in eff.splitlines() if line.strip()]
        for c in children.get(key, []):
            b += ["\t\tpath = {", f"\t\t\tleads_to_tech = {c}", "\t\t\tresearch_cost_coeff = 1", "\t\t}"]
        b += [f"\t\tresearch_cost = {cost}", f"\t\tstart_year = {year}",
              "\t\tfolder = {", f"\t\t\tname = {folder}", f"\t\t\tposition = {{ x = {x} y = {y} }}", "\t\t}",
              f"\t\tcategories = {{ {CATEGORY[folder]} }}",
              f"\t\tai_will_do = {{ factor = {2 if 'enable_' in eff else 1} }}", "\t}"]
        out += b
        loc += [f' {key}:0 "{name}"', f' {key}_desc:0 "{desc}"']
        # icon: sized for the box the game will draw (see tech_icon)
        tops.setdefault(folder, []).append(y)
        tech_icon(folder, icon, eff).save(icon_dir / f"{key}.dds")
        sprites.append(f'\tspriteType = {{ name = "GFX_{key}_medium" texturefile = "gfx/interface/technologies/{key}.dds" }}')
    for key, *_r in TECHS:   # prerequisites must lie in earlier (or the same) years
        for p in [t for t in TECHS if t[0] == key][0][6]:
            assert placed[p] <= placed[key], f"{key} ({placed[key]}) comes before its prerequisite {p} ({placed[p]})"
    out.append("}")
    Image.new("RGBA", (1, 1), (0, 0, 0, 0)).save(icon_dir / "ante_blank.dds")
    sprites.append(f'\tspriteType = {{ name = "{BLANK}" texturefile = "gfx/interface/technologies/ante_blank.dds" }}')
    sprites.append("}")
    write("common/technologies/ante_technologies.txt", "\n".join(out) + "\n")
    write("interface/ante_technologies.gfx", "\n".join(sprites) + "\n")
    for f, (name, desc) in FOLDERS.items():
        loc += [f' {f}:0 "{name}"', f' {f}_desc:0 "{desc}"']
    for f, lanes in LANES.items():
        loc += [f' {lane_key(f, x)}:0 "{text.upper()}"' for x, text in lanes.items()]
    for k, (name, desc) in EQUIPMENT_NAMES.items():
        loc += [f' {k}:0 "{name}"', f' {k}_desc:0 "{desc}"']
    write("localisation/english/replace/ante_technologies_l_english.yml", "\n".join(loc) + "\n", bom=True)
    # pages: the game's folder list with the availability changed
    tags = (g / "common" / "technology_tags" / "00_technology.txt").read_text(encoding="utf-8-sig", errors="replace")
    head, sep, folders = tags.partition("technology_folders = {")
    assert sep
    for f in list(FOLDERS) + HIDDEN:
        m = re.search(rf"\n\t{f} = \{{.*?\n\t\}}", folders, re.S)
        assert m, f
        body = m.group(0)
        ledger = re.search(r"ledger = (\w+)", body).group(1)
        avail = "always = yes" if f in FOLDERS else "always = no"
        folders = folders.replace(body, f"\n\t{f} = {{\n\t\tledger = {ledger}\n\t\tavailable = {{ {avail} }}\n\t}}", 1)
    write("common/technology_tags/00_technology.txt",
          "# Generated by tools/tech.py from the game's file: ancient pages for everyone, no air or DLC duplicates\n"
          + head + sep + folders)
    # year labels in AUC
    lines, cur = gui.split("\n"), None
    for i, line in enumerate(lines):
        m = re.search(r'name\s*=\s*"(\w+folder)"', line)
        if m:
            cur = m.group(1)
        m = re.search(r'(text\s*=\s*")(19\d\d)(")', line)
        if m and cur in FOLDERS and int(m.group(2)) in rows.get(cur, {}):
            scale = page_scale(cur, rows, labels)
            lines[i] = line[:m.start()] + f"{m.group(1)}{auc_of(rows[cur][int(m.group(2))], scale)}{m.group(3)}" + line[m.end():]
    # every tree root needs a grid box named <root>_tree on its page ("Found no grid box for tech ...", round 17):
    # one per root, all at the place (and with the size and direction) of one base-game box of that page, so all
    # our techs of a page share one origin and their rows match the year labels
    roots = {}
    for key, name, desc, folder, *_r in TECHS:
        if not [t for t in TECHS if t[0] == key][0][6]:
            roots.setdefault(folder, []).append(key)
    skip = set(os.environ.get("ANTE_TECH_SKIP", "").split(","))   # bisecting the gui changes
    if "strip" not in skip:
        lines = strip_modern(lines)
    for folder, anchor in ANCHOR.items():
        start = next(i for i, l in enumerate(lines) if re.search(rf'^\t\t\tname = "{folder}"', l))
        at = next(i for i in range(start, len(lines)) if re.search(rf'name\s*=\s*"{anchor}"', lines[i]))
        top = max(i for i in range(start, at) if re.search(r"gridbox[tT]ype\s*=", lines[i]))
        depth, end = 0, top
        for end in range(top, len(lines)):
            depth += lines[end].count("{") - lines[end].count("}")
            if depth == 0 and end > top:
                break
        block = lines[top:end + 1]
        # the game's box can be narrower than our page (industry 520 px, learning 680 px): no wrapping, no clipping
        new = [] if "lanes" in skip else lane_labels(folder, block, min(tops.get(folder, [0])))
        for r in roots.get(folder, []):
            new += [re.sub(rf'"{anchor}"', f'"{r}_tree"', l) for l in block]
        lines[top:top] = new
    if "templates" not in skip:
        lines = fix_templates(lines)
    write("interface/countrytechtreeview.gui", "\n".join(lines))
    write_tabs(g)
    n_doc = quiet_doctrines(g, {t[0] for t in TECHS})
    print(f"written: {len(TECHS)} techs on {len(FOLDERS)} pages, year labels in AUC; {n_doc} doctrine files quietened")


def quiet_doctrines(g, ours):
    """The base game's doctrine files ask has_tech for techs that no longer exist (marines, paratroopers ...).
    The game checks them all the time and wrote 228,000 'has_tech: Invalid tech' lines into error.log in one hour of
    play (round 26, tools/watch.py). Copies of those files where such a condition is 'always = no' instead."""
    n = 0
    base = g / "common" / "doctrines"
    for fp in base.rglob("*.txt"):
        text = fp.read_text(encoding="utf-8-sig", errors="replace")
        new = re.sub(r"has_tech\s*=\s*(\w+)", lambda m: m.group(0) if m.group(1) in ours else "always = no", text)
        out = MOD / "common" / "doctrines" / fp.relative_to(base)
        if new != text:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text("# Ante Imperium (tools/tech.py): the game's file, has_tech of removed techs -> always = no\n"
                           + new, encoding="utf-8", newline="\n")
            n += 1
        elif out.exists():
            out.unlink()
    return n


if __name__ == "__main__":
    main()
