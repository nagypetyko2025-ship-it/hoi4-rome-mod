"""Generate Ante Imperium game files from tools/data/world_245.py.

usage: python tools/build.py
Writes ONLY inside the mod folder, plus the launcher descriptor in Documents/.../mod.
Generated paths are wiped and rewritten on each run (see GENERATED).
"""
import colorsys
import importlib
import math
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import mapdata  # noqa: E402

GAME, MOD = mapdata.GAME, mapdata.MOD
DOCS_DESCRIPTOR = Path.home() / "Documents" / "Paradox Interactive" / "Hearts of Iron IV" / "mod" / "ante_imperium.mod"
W = importlib.import_module("data.world_245")

REPLACE_PATHS = [
    "common/bookmarks",
    "common/country_tags",
    "history/countries",
    "history/states",
    "history/units",
    "map/supplyareas",
    "common/national_focus",
    "events",
    "common/decisions",
    "common/decisions/categories",
    "common/characters",
    "common/ai_strategy",
    "common/ai_strategy_plans",
    "common/on_actions",
]

GENERATED = [
    "history/states", "history/countries", "history/units", "map/supplyareas", "map/buildings.txt",
    "common/country_tags", "common/countries", "common/bookmarks", "gfx/flags",
    "localisation/english/replace",
]

GOV_IDEOLOGY = {"republic": "democratic", "monarchy": "neutrality", "tyranny": "fascism", "tribal": "neutrality"}
URBAN = {"latin", "etruscan", "greek", "punic"}

# per-state building types in vanilla buildings.txt and how many positions each state needs
STATE_LEVEL = {"air_base": 1, "anti_air_building": 3, "arms_factory": 6, "industrial_complex": 6,
               "fuel_silo": 1, "nuclear_reactor_spawn": 1, "radar_station": 1, "rocket_site_spawn": 1,
               "stronghold_network": 1, "synthetic_refinery": 1}


def fail(msg):
    print("ERROR:", msg)
    sys.exit(1)


def write(rel, text, bom=False):
    p = MOD / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8-sig" if bom else "utf-8", newline="\n")


# ---------------------------------------------------------------- validation
def validate(d):
    seen = {}
    for key, name, owner, provs, pop, ex in W.STATES:
        if owner not in W.COUNTRIES:
            fail(f"state {key}: unknown owner {owner}")
        for p in provs:
            if p not in d["defs"]:
                fail(f"state {key}: province {p} does not exist")
            if d["defs"][p]["type"] != "land":
                fail(f"state {key}: province {p} is {d['defs'][p]['type']}")
            if p in seen:
                fail(f"province {p} in both {seen[p]} and {key}")
            seen[p] = key
        for p in ex.get("port", []):
            if p not in provs or not d["defs"][p]["coastal"]:
                fail(f"state {key}: port {p} not a coastal province of the state")
        for p in ex.get("vp", {}):
            if p not in provs:
                fail(f"state {key}: VP province {p} not in state")
        # connectivity warning
        provset, start = set(provs), provs[0]
        stack, comp = [start], {start}
        while stack:
            for n in d["stats"][stack.pop()]["n"]:
                if n in provset and n not in comp:
                    comp.add(n)
                    stack.append(n)
        if comp != provset:
            print(f"WARN: state {key} is not contiguous by land: {sorted(provset - comp)} detached")
    for tag in W.COUNTRIES:
        if tag in ("CON", "PRN", "AUX", "NUL"):
            fail(f"tag {tag} is a reserved Windows file name")
        if tag != W.WASTELAND_TAG and not any(s[2] == tag for s in W.STATES):
            fail(f"country {tag} owns no state")
    return seen


# ---------------------------------------------------------------- states
def category(pop, culture):
    if pop >= 100_000:
        return "large_city"
    if pop >= 60_000:
        return "city" if culture in URBAN else "large_town"
    if pop >= 30_000:
        return "large_town" if culture in URBAN else "town"
    if pop >= 15_000:
        return "town" if culture in URBAN else "rural"
    return "rural"


def build_states(d, assigned):
    states = []  # dicts in final id order
    for key, name, owner, provs, pop, ex in W.STATES:
        states.append(dict(key=key, name=name, owner=owner, provinces=list(provs), pop=pop, ex=ex, waste=False))
    # wasteland: leftovers of every vanilla state, keeping vanilla grouping
    for sid in sorted(d["states"]):
        vs = d["states"][sid]
        left = [p for p in vs["provinces"] if p not in assigned and d["defs"].get(p, {}).get("type") == "land"]
        if left:
            states.append(dict(key=f"waste_{sid}", name="Terra Incognita", owner=W.WASTELAND_TAG,
                               provinces=left, pop=1000, ex={}, waste=True, vanilla=sid))
    for i, s in enumerate(states, 1):
        s["id"] = i
    return states


def state_text(s, culture):
    ex = s["ex"]
    lines = ["state = {", f"\tid = {s['id']}", f"\tname = \"STATE_{s['id']}\"  # {s['name']}",
             f"\tmanpower = {s['pop']}"]
    if s["waste"]:
        lines += ["\tstate_category = wasteland", "\timpassable = yes"]
    else:
        lines.append(f"\tstate_category = {category(s['pop'], culture)}")
    lines.append("\thistory = {")
    lines.append(f"\t\towner = {s['owner']}")
    if not s["waste"]:
        for tag in [s["owner"]] + ex.get("cores", []):
            lines.append(f"\t\tadd_core_of = {tag}")
        for p, (v, city) in ex.get("vp", {}).items():
            lines.append(f"\t\tvictory_points = {{ {p} {v} }}  # {city}")
        urban = culture in URBAN
        infra = 2 if urban else 1
        ic = max(0, round(s["pop"] / (25_000 if urban else 50_000)))
        mil = 1 if s["pop"] >= 30_000 else 0
        lines.append("\t\tbuildings = {")
        lines.append(f"\t\t\tinfrastructure = {infra}")
        if ic:
            lines.append(f"\t\t\tindustrial_complex = {ic}")
        if mil:
            lines.append(f"\t\t\tarms_factory = {mil}")
        for p in ex.get("port", []):
            lines.append(f"\t\t\t{p} = {{ naval_base = {2 if s['pop'] >= 30_000 else 1} }}")
        lines.append("\t\t}")
    else:
        lines.append("\t\tbuildings = { infrastructure = 0 }")
    lines.append("\t}")
    lines.append("\tprovinces = {")
    lines.append("\t\t" + " ".join(str(p) for p in s["provinces"]))
    lines.append("\t}")
    lines.append("\tlocal_supplies = 0.0")
    lines.append("}")
    return "\n".join(lines) + "\n"


def safe_name(name):
    return re.sub(r"[^A-Za-z0-9_ ]", "", name).strip() or "state"


def write_states(states):
    for s in states:
        culture = W.COUNTRIES[s["owner"]]["culture"]
        write(f"history/states/{s['id']}-{safe_name(s['name'])}.txt", state_text(s, culture))


# ---------------------------------------------------------------- buildings.txt
def write_buildings(d, states, prov_new):
    ids = mapdata.load_ids()
    H, Wd = ids.shape
    hm = np.asarray(Image.open(GAME / "map" / "heightmap.bmp"))
    stats = d["stats"]

    def nearest_in(provs, x, y):
        return min(provs, key=lambda p: (stats[p]["x"] - x) ** 2 + (stats[p]["y"] - y) ** 2)

    per_state = defaultdict(list)  # new sid -> list of (type, rest-of-line)
    out = []
    for line in (GAME / "map" / "buildings.txt").read_text(encoding="utf-8-sig").splitlines():
        parts = line.strip().split(";")
        if len(parts) < 7:
            continue
        old_sid, btype = int(parts[0]), parts[1]
        x, z = float(parts[2]), float(parts[4])
        px, py = min(Wd - 1, max(0, int(x))), min(H - 1, max(0, H - 1 - int(z)))
        pid = int(ids[py, px])
        if pid not in prov_new:
            vprovs = [p for p in d["states"].get(old_sid, {}).get("provinces", []) if p in prov_new]
            if not vprovs:
                continue
            pid = nearest_in(vprovs, px, py)
        nsid = prov_new[pid]
        if btype in STATE_LEVEL:
            per_state[nsid].append((btype, parts[2:]))
        else:
            out.append(";".join([str(nsid), btype] + parts[2:]))
    rng = np.random.default_rng(245)
    for s in states:
        have = Counter(t for t, _ in per_state[s["id"]])
        kept = Counter()
        for btype, rest in per_state[s["id"]]:
            if kept[btype] < STATE_LEVEL[btype]:
                out.append(";".join([str(s["id"]), btype] + rest))
                kept[btype] += 1
        big = max(s["provinces"], key=lambda p: stats[p]["px"])
        for btype, need in STATE_LEVEL.items():
            for _ in range(need - min(have[btype], need)):
                cx = stats[big]["x"] + rng.uniform(-2, 2)
                cy = stats[big]["y"] + rng.uniform(-2, 2)
                if int(ids[int(cy), int(cx)]) != big:
                    cx, cy = stats[big]["x"], stats[big]["y"]
                y = hm[int(cy), int(cx)] / 10.0
                out.append(f"{s['id']};{btype};{cx:.2f};{y:.2f};{H - cy:.2f};{rng.uniform(0, 6.28):.2f};0")
    write("map/buildings.txt", "\n".join(out) + "\n")


# ---------------------------------------------------------------- supply areas
def write_supply_areas(d, states):
    # Supply areas are a legacy leftover (vanilla ships one file with 4 states); keep one valid stub.
    write("map/supplyareas/1-SupplyArea.txt",
          "supply_area={\n\tid=1\n\tname=\"SUPPLYAREA_1\"\n\tvalue=12\n\tstates={\n\t\t1\n\t}\n}\n")


# ---------------------------------------------------------------- countries
def write_countries(states):
    capital = {s["owner"]: s["id"] for s in states if s["ex"].get("capital")}
    for s in states:
        capital.setdefault(s["owner"], s["id"])
    tags_txt = ["# Generated by tools/build.py"]
    colors_txt = ["#reload countrycolors", ""]
    for tag, c in W.COUNTRIES.items():
        cul = W.CULTURES[c["culture"]]
        tags_txt.append(f'{tag} = "countries/ante_{tag}.txt"')
        r, g, b = c["color"]
        write(f"common/countries/ante_{tag}.txt",
              f"graphical_culture = {cul['gfx']}\ngraphical_culture_2d = {cul['gfx2d']}\n"
              f"color = {{ {r} {g} {b} }}\n")
        ui = tuple(min(255, int(v * 1.25)) for v in c["color"])
        colors_txt += [f"{tag} = {{", f"\tcolor = rgb {{ {r} {g} {b} }}",
                       f"\tcolor_ui = rgb {{ {ui[0]} {ui[1]} {ui[2]} }}", "}"]
        ideology = GOV_IDEOLOGY[c["gov"]]
        pops = {k: 0 for k in ("democratic", "fascism", "communism", "neutrality")}
        pops[ideology] = 100
        hist = [f"capital = {capital[tag]}", "set_research_slots = 2", "set_stability = 0.6",
                "set_war_support = 0.3", "", "set_politics = {", f"\truling_party = {ideology}",
                '\tlast_election = "240.1.1"', "\telection_frequency = 12",
                f"\telections_allowed = {'yes' if ideology == 'democratic' else 'no'}", "}",
                "set_popularities = {"] + [f"\t{k} = {v}" for k, v in pops.items()] + ["}"]
        write(f"history/countries/{tag} - {safe_name(c['name'])}.txt", "\n".join(hist) + "\n", bom=True)
    # keep vanilla dynamic tags (civil wars etc.) and their colours
    dyn = (GAME / "common" / "country_tags" / "zz_dynamic_countries.txt").read_text(encoding="utf-8-sig")
    write("common/country_tags/00_ante_countries.txt", "\n".join(tags_txt) + "\n")
    write("common/country_tags/zz_dynamic_countries.txt", dyn)
    van_colors = (GAME / "common" / "countries" / "colors.txt").read_text(encoding="utf-8-sig")
    for m in re.finditer(r"^(D\d\d) = \{.*?^\}", van_colors, re.S | re.M):
        colors_txt.append(m.group(0))
    write("common/countries/colors.txt", "\n".join(colors_txt) + "\n")
    # dynamic country files are referenced as countries/Dxx.txt -> vanilla files still exist (not replaced)
    return capital


# ---------------------------------------------------------------- flags
def flag_image(tag, c):
    style = W.CULTURES[c["culture"]]["flag"]
    base = tuple(c["color"])
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in base))
    light = tuple(int(v * 255) for v in colorsys.hls_to_rgb(h, min(0.92, l + 0.4), s * 0.6))
    gold = (215, 175, 70)
    im = Image.new("RGBA", (82, 52), base + (255,))
    dr = ImageDraw.Draw(im)
    seed = sum(ord(ch) * (i + 1) for i, ch in enumerate(tag))
    if style == "latin":
        dr.rectangle([0, 0, 81, 51], fill=base)
        dr.rectangle([4, 4, 77, 47], outline=gold, width=3)
        dr.polygon([(41, 12), (52, 26), (41, 40), (30, 26)], fill=gold)
    elif style == "italic":
        dr.rectangle([0, 0, 27, 51], fill=light)
        dr.rectangle([54, 0, 81, 51], fill=light)
        dr.ellipse([33, 18, 48, 33], fill=gold)
    elif style == "etruscan":
        for i in range(0, 52, 13):
            if (i // 13) % 2:
                dr.rectangle([0, i, 81, i + 12], fill=light)
        dr.ellipse([30, 15, 51, 36], fill=gold, outline=(60, 30, 10), width=2)
    elif style == "greek":
        dr.rectangle([0, 0, 81, 51], fill=light)
        dr.ellipse([22, 7, 59, 44], fill=base, outline=gold, width=3)
        k = seed % 3
        if k == 0:
            dr.polygon([(41, 14), (49, 34), (33, 34)], fill=gold)
        elif k == 1:
            dr.rectangle([38, 14, 44, 37], fill=gold)
        else:
            dr.ellipse([35, 20, 47, 31], fill=gold)
    elif style == "punic":
        dr.ellipse([33, 16, 49, 32], fill=gold)
        dr.arc([26, 26, 56, 46], 200, 340, fill=gold, width=3)
        dr.rectangle([0, 46, 81, 51], fill=light)
    elif style == "tribal":
        dr.polygon([(0, 0), (30, 0), (81, 51), (51, 51)], fill=light)
        dr.polygon([(0, 51), (0, 30), (21, 51)], fill=gold)
    else:
        dr.rectangle([0, 0, 81, 51], fill=(70, 70, 70))
    return im


def write_flags():
    for sub, size in (("", (82, 52)), ("medium/", (41, 26)), ("small/", (10, 7))):
        (MOD / "gfx" / "flags" / sub).mkdir(parents=True, exist_ok=True)
    for tag, c in W.COUNTRIES.items():
        im = flag_image(tag, c)
        im.save(MOD / "gfx" / "flags" / f"{tag}.tga")
        im.resize((41, 26), Image.LANCZOS).save(MOD / "gfx" / "flags" / "medium" / f"{tag}.tga")
        im.resize((10, 7), Image.LANCZOS).save(MOD / "gfx" / "flags" / "small" / f"{tag}.tga")


# ---------------------------------------------------------------- localisation
def yml_escape(s):
    return s.replace('"', '\\"')


def write_localisation(states):
    lines = ["l_english:"]
    for tag, c in W.COUNTRIES.items():
        lines += [f' {tag}:0 "{yml_escape(c["name"])}"', f' {tag}_DEF:0 "{yml_escape(c["name"])}"',
                  f' {tag}_ADJ:0 "{yml_escape(c["adj"])}"']
        for ide in ("democratic", "fascism", "communism", "neutrality"):
            lines += [f' {tag}_{ide}:0 "{yml_escape(c["name"])}"', f' {tag}_{ide}_DEF:0 "{yml_escape(c["name"])}"',
                      f' {tag}_{ide}_ADJ:0 "{yml_escape(c["adj"])}"']
    write("localisation/english/replace/ante_countries_l_english.yml", "\n".join(lines) + "\n", bom=True)
    lines = ["l_english:"]
    for s in states:
        lines.append(f' STATE_{s["id"]}:0 "{yml_escape(s["name"])}"')
        for p, (v, city) in s["ex"].get("vp", {}).items():
            lines.append(f' VICTORY_POINTS_{p}:0 "{yml_escape(city)}"')
    write("localisation/english/replace/ante_states_l_english.yml", "\n".join(lines) + "\n", bom=True)


# ---------------------------------------------------------------- bookmark + descriptor
def write_bookmark():
    lines = ["# Generated by tools/build.py", "bookmarks = {", "\tbookmark = {",
             '\t\tname = "ANTE_BOOKMARK_REPUBLIC_NAME"', '\t\tdesc = "ANTE_BOOKMARK_REPUBLIC_DESC"',
             "\t\tdate = 245.1.1.12", '\t\tpicture = "GFX_select_date_1936"',
             f'\t\tdefault_country = "{W.BOOKMARK_COUNTRIES[0]}"', "\t\tdefault = yes", ""]
    for tag in W.BOOKMARK_COUNTRIES:
        ide = GOV_IDEOLOGY[W.COUNTRIES[tag]["gov"]]
        lines += [f'\t\t"{tag}" = {{', f'\t\t\thistory = "ANTE_BOOKMARK_REPUBLIC_DESC"',
                  f"\t\t\tideology = {ide}", "\t\t\tideas = { }", "\t\t\tfocuses = { }", "\t\t}"]
    lines += ['\t\t"---" = {', '\t\t\thistory = "ANTE_BOOKMARK_REPUBLIC_DESC"', "\t\t}", "",
              "\t\teffect = {", "\t\t\trandomize_weather = 22345 # <- Obligatory in every bookmark !",
              "\t\t}", "\t}", "}"]
    write("common/bookmarks/ante_imperium_bookmarks.txt", "\n".join(lines) + "\n")


def write_descriptors():
    body = ['version="0.0.2"', "tags={", '\t"Alternative History"', '\t"Historical"', '\t"Map"',
            '\t"Gameplay"', "}", 'name="Ante Imperium"', 'supported_version="1.19.*"']
    body += [f'replace_path="{p}"' for p in REPLACE_PATHS]
    write("descriptor.mod", "\n".join(body) + "\n")
    DOCS_DESCRIPTOR.write_text("\n".join(body + [f'path="{MOD.as_posix()}"']) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- main
def main():
    d = mapdata.load_all()
    assigned = validate(d)
    for rel in GENERATED:
        p = MOD / rel
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
    states = build_states(d, assigned)
    prov_new = {p: s["id"] for s in states for p in s["provinces"]}
    land = [p for p, v in d["defs"].items() if v["type"] == "land"]
    missing = [p for p in land if p not in prov_new]
    if missing:
        fail(f"{len(missing)} land provinces without state, e.g. {missing[:10]}")
    write_states(states)
    write_buildings(d, states, prov_new)
    write_supply_areas(d, states)
    write_countries(states)
    write_flags()
    write_localisation(states)
    write_bookmark()
    write_descriptors()
    (MOD / "history" / "units").mkdir(parents=True, exist_ok=True)
    write("history/units/.keep", "")
    play = [s for s in states if not s["waste"]]
    print(f"OK: {len(W.COUNTRIES)} countries, {len(play)} playable states, "
          f"{len(states) - len(play)} wasteland states, {sum(s['pop'] for s in play):,} people")


if __name__ == "__main__":
    main()
