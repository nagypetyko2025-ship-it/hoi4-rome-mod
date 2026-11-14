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
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

TOOLS = Path(__file__).resolve().parent
MOD = TOOLS.parent
sys.path.insert(0, str(TOOLS))
from data.tech_tree import TECHS  # noqa: E402
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


FIRST, LAST = 245, 365   # AUC of the first and the last labelled row of every page (round 17: 485 = far too slow)
DESIGN_LAST = 485        # the years in tech_tree.py run 245..485 and are squeezed into FIRST..LAST
WIDE = {"armour_folder", "artillery_folder", "industry_folder", "electronics_folder"}  # time runs down: boxes side by side need 3 slots
STEP = {"naval_folder": 3}  # rows used: multiples of this from the top row (big ship boxes need more room)


def page_scale(folder, rows, labels):
    """(y of the top label, y of the bottom label): AUC grows linearly with y in between"""
    ys = [rows[folder][yr] for yr in labels.get(folder, set()) if yr in rows.get(folder, {})]
    assert len(ys) >= 2, f"no rows on {folder}"
    return min(ys), max(ys)


def auc_of(y, scale):
    y0, y1 = scale
    return int(round((FIRST + (y - y0) * (LAST - FIRST) / (y1 - y0)) / 5) * 5)


def place(folder, auc, rows, labels):
    y0, y1 = scale = page_scale(folder, rows, labels)
    step = STEP.get(folder, 2)
    auc = FIRST + (auc - FIRST) * (LAST - FIRST) / (DESIGN_LAST - FIRST)
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
                "helmet": (196, 150, 64), "sword": (170, 170, 176), "tent": (190, 170, 130), "tower": (190, 180, 160),
                "wheat": (214, 180, 90), "pick": (130, 120, 110)}


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
    used, placed = set(), {}
    icon_dir = MOD / "gfx" / "interface" / "technologies"
    icon_dir.mkdir(parents=True, exist_ok=True)
    for key, name, desc, folder, x, auc, pre, eff, icon, cost in TECHS:
        y, year = place(folder, auc, rows, labels)
        x = x * 3 // 2 if folder in WIDE else x
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
        # icon
        if icon.startswith("eq:"):
            pic = army.product_icon(icon[3:])
            lvl = re.search(r"_equipment_(\d)\b", eff)
            if lvl and int(lvl.group(1)) > 1:   # II / III for the better models
                d = ImageDraw.Draw(pic)
                txt = "I" * int(lvl.group(1))
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    d.text((96 + dx - 3 * len(txt), 17 + dy), txt, fill=(30, 22, 14, 255))
                d.text((96 - 3 * len(txt), 17), txt, fill=(235, 215, 160, 255))
        else:
            pic = shaded(glyph(icon), GLYPH_COLOUR[icon])
        pic.save(icon_dir / f"{key}.dds")
        sprites.append(f'\tspriteType = {{ name = "GFX_{key}_medium" texturefile = "gfx/interface/technologies/{key}.dds" }}')
    for key, *_r in TECHS:   # prerequisites must lie in earlier (or the same) years
        for p in [t for t in TECHS if t[0] == key][0][6]:
            assert placed[p] <= placed[key], f"{key} ({placed[key]}) comes before its prerequisite {p} ({placed[p]})"
    out.append("}")
    sprites.append("}")
    write("common/technologies/ante_technologies.txt", "\n".join(out) + "\n")
    write("interface/ante_technologies.gfx", "\n".join(sprites) + "\n")
    for f, (name, desc) in FOLDERS.items():
        loc += [f' {f}:0 "{name}"', f' {f}_desc:0 "{desc}"']
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
        new = []
        for r in roots.get(folder, []):
            new += [re.sub(rf'"{anchor}"', f'"{r}_tree"', l) for l in block]
        lines[top:top] = new
    write("interface/countrytechtreeview.gui", "\n".join(lines))
    print(f"written: {len(TECHS)} techs on {len(FOLDERS)} pages, year labels in AUC")


if __name__ == "__main__":
    main()
