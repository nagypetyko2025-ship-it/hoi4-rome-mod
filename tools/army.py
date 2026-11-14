"""Ancient armies (reads the base game once for two blocks it keeps; ~5 s).

Writes
  common/units/ante_units.txt                ancient battalions and support companies
  common/units/equipment/ante_equipment.txt  their equipment (spears and shields, hoplite panoply, bows, horses...)
  common/units/<vanilla name>.txt            empty overrides: tanks, motorised, modern artillery etc. are gone
  common/units/equipment/infantry.txt        the base game's rifles, no longer available from the start
  interface/ante_units.gfx + gfx/interface/... HoI4-style icons drawn here (green silhouette + unit symbol,
                                             brown equipment silhouettes) - our own art, CC0
  history/units/<TAG>_245.txt                every country's army at the start, sized by its manpower
  localisation/english/ante_army_l_english.yml

Run after tools/world.py (reads history/states and history/countries). Ships and aircraft are untouched for now.
"""
import math
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

MOD = Path(__file__).resolve().parent.parent
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))


def game_dir():
    from mapdata import GAME  # finds the game on any drive (HOI4_DIR overrides)
    return Path(GAME)


def write(rel, text, bom=False):
    p = MOD / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8-sig" if bom else "utf-8", newline="\n")


# ============================================================================ equipment
# key: (name, short, desc, type, stats, cost, resources, active). Resources are the base game's keys with ancient
# meanings (tools/resources.py): steel = iron, aluminium = copper, tungsten = tin, rubber = timber, chromium = horses,
# oil = pitch, coal = grain.
EQUIPMENT = {
    "ante_arms_equipment": ("Spears and Shields", "Spears", "Spear, shield, a knife or an axe: the arms of every free warrior.",
                            "infantry", dict(defense=20, breakthrough=2, soft_attack=3, hard_attack=0.2, ap_attack=0.5,
                                             maximum_speed=4, reliability=0.9), 0.4, {"steel": 1}, True),
    "ante_panoply_equipment": ("Hoplite Panoply", "Panoply", "Bronze helmet, cuirass, greaves, the great round shield and the thrusting spear.",
                               "infantry", dict(defense=32, breakthrough=4, soft_attack=4, hard_attack=0.4, ap_attack=1,
                                                maximum_speed=4, reliability=0.9), 0.9, {"aluminium": 1, "tungsten": 1}, True),
    "ante_ranged_equipment": ("Bows and Slings", "Missiles", "Bows, slings and bundles of javelins.",
                              "infantry", dict(defense=8, breakthrough=1, soft_attack=6, hard_attack=0.1, ap_attack=0.2,
                                               maximum_speed=4, reliability=0.9), 0.35, {"rubber": 1}, True),
    "ante_horse_equipment": ("Horses and Tack", "Horses", "Riding horses, bridles and saddle cloths - stirrups are a thousand years away.",
                             "infantry", dict(defense=4, breakthrough=4, soft_attack=3, hard_attack=0.1, ap_attack=0.2,
                                              maximum_speed=6, reliability=0.85), 0.8, {"chromium": 2}, True),
    "ante_chariot_equipment": ("War Chariots", "Chariots", "Two-wheeled cars of wood and wicker, drawn by small horses.",
                               "infantry", dict(defense=6, breakthrough=8, soft_attack=6, hard_attack=0.3, ap_attack=0.5,
                                                maximum_speed=6, reliability=0.75), 1.6, {"chromium": 1, "rubber": 1}, True),
    "ante_siege_equipment": ("Siege Engines", "Siege", "Rams, ladders, mantlets and siege towers.",
                             "artillery", dict(defense=4, breakthrough=1, soft_attack=8, hard_attack=0.5, ap_attack=2,
                                               maximum_speed=3, reliability=0.8), 2.5, {"rubber": 2, "steel": 1}, True),
    "ante_elephant_equipment": ("War Elephants", "Elephants", "Trained elephants with their drivers - not yet seen in the Mediterranean.",
                                "infantry", dict(defense=14, breakthrough=16, soft_attack=12, hard_attack=1, ap_attack=2,
                                                 maximum_speed=4, reliability=0.7), 4.0, {}, False),
}

# better models, unlocked by the tech tree (tools/tech.py): archetype -> [(level, name, short, stat factor)]
VARIANTS = {
    "ante_arms_equipment": [(2, "Iron Weapons", "Iron", 1.15), (3, "Forged Steel", "Steel", 1.30)],
    "ante_panoply_equipment": [(2, "Linothorax Panoply", "Linothorax", 1.15), (3, "Mail and Scutum", "Mail", 1.30)],
    "ante_ranged_equipment": [(2, "Composite Bows", "Comp. bows", 1.15), (3, "Lead Sling Shot", "Lead shot", 1.30)],
    "ante_horse_equipment": [(2, "Bred Warhorses", "Warhorses", 1.15), (3, "Horned Saddles", "Saddles", 1.30)],
    "ante_chariot_equipment": [(2, "Scythed Chariots", "Scythed", 1.20)],
    "ante_siege_equipment": [(2, "Siege Towers", "Towers", 1.15), (3, "Torsion Engines", "Torsion", 1.35)],
}
SCALED = ("defense", "breakthrough", "soft_attack", "hard_attack", "ap_attack")


# ============================================================================ battalions
# key: dict(name, desc, group, sprite, cats, need, extra stats, terrain, abbr, active, width, cav, support)
FRONT = ["category_front_line", "category_army"]
INF = FRONT + ["category_light_infantry", "category_all_infantry", "category_infantry_and_bicycle"]
UNITS = {
    "ante_levy": dict(name="Levies", abbr="LEV", desc="Farmers and herdsmen called to arms: many, cheap and brittle.",
                      group="infantry", sprite="infantry", cats=INF, need={"ante_arms_equipment": 80},
                      stats=dict(max_organisation=40, default_morale=0.25, training_time=45, suppression=1.0,
                                 supply_consumption=0.05), terrain={}),
    "ante_spearmen": dict(name="Spearmen", abbr="SPR", desc="The warrior band of the free men, shield to shield.",
                          group="infantry", sprite="infantry", cats=INF, need={"ante_arms_equipment": 100},
                          stats=dict(max_organisation=60, default_morale=0.3, training_time=90, suppression=1.5,
                                     supply_consumption=0.06), terrain={"forest": (0.05, 0.05)}),
    "ante_hoplites": dict(name="Hoplites", abbr="HOP", desc="Heavy infantry in the close order of the phalanx: unbreakable in front, slow and clumsy in rough country.",
                          group="infantry", sprite="infantry", cats=INF, need={"ante_panoply_equipment": 100},
                          stats=dict(max_organisation=70, default_morale=0.4, training_time=150, suppression=1.5,
                                     supply_consumption=0.07),
                          terrain={"plains": (0.1, 0.1), "forest": (-0.15, -0.1), "hills": (-0.05, 0), "mountain": (-0.2, -0.1)}),
    "ante_skirmishers": dict(name="Skirmishers", abbr="SKR", desc="Slingers and javelin men who wear down the enemy before the lines meet.",
                             group="infantry", sprite="infantry", cats=INF, need={"ante_ranged_equipment": 80},
                             stats=dict(max_organisation=50, default_morale=0.25, training_time=60, suppression=1.0,
                                        supply_consumption=0.05),
                             terrain={"forest": (0.1, 0.05), "hills": (0.1, 0.05), "mountain": (0.1, 0.05)}),
    "ante_archers": dict(name="Archers", abbr="ARC", desc="Massed bowmen - the strength of Persia, Kush and the steppe.",
                         group="infantry", sprite="infantry", cats=INF, need={"ante_ranged_equipment": 100},
                         stats=dict(max_organisation=50, default_morale=0.3, training_time=90, suppression=1.0,
                                    supply_consumption=0.05), terrain={"plains": (0.1, 0.1), "desert": (0.1, 0.05)}),
    "ante_cavalry": dict(name="Cavalry", abbr="CAV", desc="Noble horsemen with spear and javelin.",
                         group="mobile", sprite="cavalry", cats=FRONT + ["category_cavalry"], cav=True,
                         need={"ante_horse_equipment": 100, "ante_arms_equipment": 30},
                         stats=dict(max_organisation=70, default_morale=0.35, training_time=120, suppression=2,
                                    supply_consumption=0.08, maximum_speed=0.6, breakthrough=0.2),
                         terrain={"plains": (0.1, 0), "forest": (-0.1, 0), "mountain": (-0.2, 0), "marsh": (-0.2, 0)}),
    "ante_horse_archers": dict(name="Horse Archers", abbr="HAR", desc="The steppe's own way of war: shoot, wheel away, shoot again.",
                               group="mobile", sprite="cavalry", cats=FRONT + ["category_cavalry"], cav=True,
                               need={"ante_horse_equipment": 100, "ante_ranged_equipment": 60},
                               stats=dict(max_organisation=70, default_morale=0.35, training_time=150, suppression=2,
                                          supply_consumption=0.08, maximum_speed=0.8, breakthrough=0.1),
                               terrain={"plains": (0.15, 0), "desert": (0.1, 0), "forest": (-0.2, -0.1), "mountain": (-0.2, 0)}),
    "ante_chariots": dict(name="Chariots", abbr="CHR", desc="Swift two-horse chariots - of the Britons and the Garamantes, and of kings of old.",
                          group="mobile", sprite="cavalry", cats=FRONT + ["category_cavalry"], cav=True,
                          need={"ante_chariot_equipment": 40},
                          stats=dict(max_organisation=50, default_morale=0.3, training_time=120, suppression=1.5,
                                     supply_consumption=0.08, maximum_speed=0.5, breakthrough=0.3),
                          terrain={"plains": (0.2, 0), "desert": (0.1, 0), "forest": (-0.3, -0.1), "hills": (-0.2, 0),
                                   "mountain": (-0.4, -0.2), "marsh": (-0.4, -0.2)}),
    "ante_war_elephants": dict(name="War Elephants", abbr="ELE", desc="Living siege towers. They break any line - sometimes their own.",
                               group="mobile", sprite="cavalry", cats=FRONT + ["category_cavalry"], cav=True, active=False,
                               need={"ante_elephant_equipment": 20},
                               stats=dict(max_organisation=40, default_morale=0.3, training_time=180, suppression=3,
                                          supply_consumption=0.15, maximum_speed=0.0, breakthrough=0.5),
                               terrain={"plains": (0.2, 0), "forest": (-0.3, 0), "mountain": (-0.5, -0.2)}),
    # support companies
    "ante_siege_engines": dict(name="Siege Train", abbr="SIE", desc="Engineers with rams, ladders and towers. Indispensable against walls.",
                               group="support", sprite="artillery", cats=["category_support_battalions", "category_divisional_support_battalions", "category_army"],
                               support=True, need={"ante_siege_equipment": 12}, manpower=150,
                               stats=dict(max_organisation=20, default_morale=0.3, training_time=120,
                                          supply_consumption=0.04, entrenchment=1),
                               terrain={"fort": (0.3, 0.1), "river": (0.1, 0.1)}),
    "ante_scouts": dict(name="Mounted Scouts", abbr="SCT", desc="Riders who go ahead of the host and find the enemy first.",
                        group="support", sprite="cavalry", cats=["category_support_battalions", "category_divisional_support_battalions", "category_army", "category_recon"],
                        support=True, need={"ante_horse_equipment": 30}, manpower=100,
                        stats=dict(max_organisation=20, default_morale=0.3, training_time=90, supply_consumption=0.03,
                                   recon=1), terrain={}),
}

# vanilla land unit files emptied by override (ships and aircraft stay for now)
VANILLA_LAND = ["amphibious_armor", "amphibious_mech", "anti-air", "anti-air_brigade", "anti_tank", "anti_tank_brigade",
                "armored_car_battalion", "artillery", "artillery_brigade", "blackshirt_assault_battalion", "bus",
                "cavalry", "engineer", "field_hospital", "fire_support", "flame_tank", "heavy_armor",
                "helicopter_brigade", "land_cruiser", "light_armor", "logistics", "maintenance", "medium_armor",
                "military_police", "modern_armor", "railway_gun", "recon", "signal", "sp_anti-air_brigade",
                "sp_artillery_brigade", "sturmtruppe_battalion", "super_heavy_armor", "tank_destroyer_brigade",
                "infantry"]
KEEP_FROM_INFANTRY = ["fake_intel_unit"]  # used by the engine's intelligence system


def fmt(v):
    return f"{v:g}" if isinstance(v, float) else str(v)


def units_file():
    out = ["# Generated by tools/army.py - ancient battalions. Base-game unit files of modern troops are emptied.",
           "sub_units = {"]
    for key, u in UNITS.items():
        out += [f"\t{key} = {{", f'\t\tabbreviation = "{u["abbr"]}"', f"\t\tsprite = {u['sprite']}",
                f"\t\tmap_icon_category = {'other' if u['group'] != 'infantry' else 'infantry'}",
                "\t\tpriority = 600", "\t\tai_priority = 200", f"\t\tactive = {'yes' if u.get('active', True) else 'no'}"]
        if u.get("cav"):
            out.append("\t\tcavalry = yes")
        out += ["\t\ttype = { " + ("support" if u.get("support") else "infantry") + " }", f"\t\tgroup = {u['group']}",
                "\t\tcategories = {"] + [f"\t\t\t{c}" for c in u["cats"]] + ["\t\t}"]
        out += [f"\t\tcombat_width = {0 if u.get('support') else 2}", "\t\tmax_strength = " + ("2" if u.get("support") else "25"),
                f"\t\tmanpower = {u.get('manpower', 500)}",  # ancient units: 500 men a battalion
                "\t\tweight = " + ("0.1" if u.get("support") else "0.5")]
        out += [f"\t\t{k} = {fmt(v)}" for k, v in u["stats"].items()]
        out += ["\t\tneed = {"] + [f"\t\t\t{k} = {v}" for k, v in u["need"].items()] + ["\t\t}"]
        for terr, (att, mov) in u["terrain"].items():
            out += [f"\t\t{terr} = {{", f"\t\t\tattack = {fmt(att)}"]
            if mov:
                out.append(f"\t\t\t{'defence' if terr in ('fort', 'river') else 'movement'} = {fmt(mov)}")
            out.append("\t\t}")
        out.append("\t}")
    out += ships_units()
    out.append("}")
    return "\n".join(out) + "\n"


def equipment_file():
    out = ["# Generated by tools/army.py - ancient equipment (one model each for now; the tech tree will add more).",
           "equipments = {"]
    for key, (name, short, desc, typ, st, cost, res, active) in EQUIPMENT.items():
        out += [f"\t{key} = {{", "\t\tyear = 1", "\t\tis_archetype = yes", f"\t\tpicture = archetype_{key}",
                "\t\tis_buildable = no", f"\t\ttype = {typ}", "\t\tgroup_by = archetype",
                "\t\tinterface_category = interface_category_land", f"\t\tactive = {'yes' if active else 'no'}"]
        out += [f"\t\t{k} = {fmt(v)}" for k, v in st.items()]
        out += ["\t\tarmor_value = 0", "\t\thardness = 0", "\t\tair_attack = 0", "\t\tlend_lease_cost = 1",
                f"\t\tbuild_cost_ic = {fmt(cost)}", "\t\tresources = {"] + [f"\t\t\t{r} = {n}" for r, n in res.items()] + ["\t\t}", "\t}"]
        out += [f"\t{key}_1 = {{", "\t\tyear = 1", f"\t\tarchetype = {key}", f"\t\tactive = {'yes' if active else 'no'}",
                "\t\tpriority = 10", "\t\tvisual_level = 0", "\t}"]
        for lvl, vname, vshort, fac in VARIANTS.get(key, []):
            out += [f"\t{key}_{lvl} = {{", f"\t\tyear = {lvl}", f"\t\tarchetype = {key}", f"\t\tparent = {key}_{lvl - 1}",
                    "\t\tactive = no", "\t\tpriority = 10", f"\t\tvisual_level = {lvl - 1}"]
            out += [f"\t\t{k} = {fmt(round(v * fac, 2) if k in SCALED else v)}" for k, v in st.items()]
            out += [f"\t\tbuild_cost_ic = {fmt(round(cost * (1 + (fac - 1) * 0.6), 2))}", "\t\tresources = {"] + \
                   [f"\t\t\t{r} = {n}" for r, n in res.items()] + ["\t\t}", "\t}"]
    for key, s in SHIPS.items():
        eq = f"{key}_hull"
        out += [f"\t{eq} = {{", "\t\tyear = 1", "\t\tis_archetype = yes", "\t\tis_buildable = no",
                f"\t\tpicture = archetype_{eq}", f"\t\ttype = {s['type']}", f"\t\tinterface_category = {s['cat']}",
                "\t\tpriority = 2000", f"\t\tactive = {'yes' if s['active'] else 'no'}"]
        out += [f"\t\t{k} = {fmt(v)}" for k, v in s["stats"].items()]
        out += ["\t\thg_attack = 0", "\t\thg_armor_piercing = 0", "\t\ttorpedo_attack = 0", "\t\tsub_attack = 0",
                "\t\tanti_air_attack = 0", "\t\tsub_detection = 0", "\t\tfuel_consumption = 0",
                "\t\tnaval_weather_penalty_factor = 1",
                "\t\tresources = { " + " ".join(f"{r} = {n}" for r, n in s["res"].items()) + " }", "\t}",
                f"\t{eq}_1 = {{", "\t\tyear = 1", f"\t\tarchetype = {eq}", f"\t\tactive = {'yes' if s['active'] else 'no'}",
                "\t\tpriority = 2000", "\t}"]
    out.append("}")
    return "\n".join(out) + "\n"


# ============================================================================ ships
SHIPS = {
    "ante_penteconter": dict(name="Penteconter", abbr="PEN", sprite="destroyer", unit_type="screen_ship",
                             type="screen_ship", cat="interface_category_screen_ships", active=True,
                             desc="Fifty oars, a bronze ram and a mast: the long ship of pirates, colonists and small cities.",
                             org=30, stats=dict(lg_attack=2, lg_armor_piercing=1, armor_value=0, surface_detection=10,
                                                surface_visibility=8, naval_speed=8, reliability=0.7, naval_range=300,
                                                max_strength=10, build_cost_ic=60, manpower=60,
                                                naval_dominance_factor=5), res={"rubber": 1, "oil": 1}),
    "ante_trireme": dict(name="Trireme", abbr="TRI", sprite="light_cruiser", unit_type="capital_ship",
                         type="capital_ship", cat="interface_category_capital_ships", active=True,
                         desc="Three banks of oars and 170 rowers drive the ram into the enemy's side - the new queen of the seas.",
                         org=40, stats=dict(lg_attack=6, lg_armor_piercing=3, armor_value=1, surface_detection=12,
                                            surface_visibility=12, naval_speed=9, reliability=0.7, naval_range=400,
                                            max_strength=25, build_cost_ic=150, manpower=200,
                                            naval_dominance_factor=15), res={"rubber": 2, "oil": 1}),
    "ante_quinquereme": dict(name="Quinquereme", abbr="QUI", sprite="heavy_cruiser", unit_type="capital_ship",
                             type="capital_ship", cat="interface_category_capital_ships", active=False,
                             desc="A heavier galley with marines on deck - built by Carthage and Rome in the age of the Punic Wars.",
                             org=45, stats=dict(lg_attack=10, lg_armor_piercing=5, armor_value=3, surface_detection=12,
                                                surface_visibility=16, naval_speed=7, reliability=0.75, naval_range=400,
                                                max_strength=45, build_cost_ic=300, manpower=400,
                                                naval_dominance_factor=25), res={"rubber": 3, "oil": 1, "aluminium": 1}),
}
VANILLA_NAVAL = ["battleship", "battlecruiser", "carrier", "destroyer", "heavy_cruiser", "light_cruiser", "submarine",
                 "repair_ships", "support_ships"]


def ships_units():
    out = []
    for key, s in SHIPS.items():
        out += [f"\t{key} = {{", f'\t\tabbreviation = "{s["abbr"]}"', f"\t\tsprite = {s['sprite']}",
                "\t\tmap_icon_category = ship", "\t\tpriority = 3", f"\t\tactive = {'yes' if s['active'] else 'no'}",
                f"\t\ttype = {{ {s['unit_type']} }}", f"\t\tneed = {{ {key}_hull = 1 }}", f"\t\tmax_organisation = {s['org']}",
                "\t\tsupply_consumption = 0.03",
                "\t\tcritical_parts = { on_fire rudder_jammed }", "\t\tcritical_part_damage_chance_mult = 1",
                "\t\thit_profile_mult = 1.0", "\t}"]
    return out


def vanilla_overrides():
    g = game_dir()
    inf = (g / "common" / "units" / "infantry.txt").read_text(encoding="utf-8-sig")
    keep = []
    for k in KEEP_FROM_INFANTRY:
        m = re.search(rf"(?ms)^\t{k} = \{{.*?^\t\}}", inf)
        if not m:
            sys.exit(f"ERROR: {k} not found in the base game's infantry.txt")
        keep.append(m.group(0))
    for name in VANILLA_LAND + VANILLA_NAVAL:
        body = "\n".join(keep) if name == "infantry" else ""
        write(f"common/units/{name}.txt", f"# Ante Imperium (tools/army.py): replaces the base game's {name}.txt - "
                                          f"no modern troops or warships in 509 BC.\nsub_units = {{\n{body}\n}}\n")
    eq = (g / "common" / "units" / "equipment" / "infantry.txt").read_text(encoding="utf-8-sig")
    eq = re.sub(r"active = yes", "active = no", eq)
    write("common/units/equipment/infantry.txt",
          "# Ante Imperium (tools/army.py): the base game's infantry equipment, but not available (no rifles in 509 BC).\n" + eq)


# ============================================================================ icons (HoI4 style, our own drawing)
K = 6  # supersampling


def silhouette(kind, w, h):
    """white silhouette mask of an ancient unit / equipment, drawn into a w x h box"""
    im = Image.new("L", (w * K, h * K), 0)
    d = ImageDraw.Draw(im)

    def P(pts):
        return [(x * w * K, y * h * K) for x, y in pts]

    def E(x0, y0, x1, y1):
        d.ellipse((x0 * w * K, y0 * h * K, x1 * w * K, y1 * h * K), fill=255)

    def L(pts, wd):
        d.line(P(pts), fill=255, width=max(1, int(wd * h * K)), joint="curve")

    def horse(x=0.0, s=1.0):
        E(x + 0.2 * s, 0.36, x + 0.74 * s, 0.68)                       # body
        d.polygon(P([(x + 0.6 * s, 0.42), (x + 0.72 * s, 0.12), (x + 0.8 * s, 0.1), (x + 0.98 * s, 0.38),
                     (x + 0.93 * s, 0.45), (x + 0.8 * s, 0.32), (x + 0.74 * s, 0.56)]), fill=255)  # neck, head down
        d.polygon(P([(x + 0.72 * s, 0.12), (x + 0.74 * s, 0.02), (x + 0.78 * s, 0.11)]), fill=255)  # ears
        for lx in (0.27, 0.36, 0.58, 0.67):                               # legs
            L([(x + lx * s, 0.6), (x + (lx - 0.02) * s, 0.95)], 0.07)
        L([(x + 0.24 * s, 0.45), (x + 0.12 * s, 0.75)], 0.06)            # tail

    if kind in ("ante_levy", "ante_spearmen", "ante_arms_equipment"):
        L([(0.15, 0.95), (0.85, 0.05)], 0.07)
        d.polygon(P([(0.85, 0.05), (0.78, 0.2), (0.9, 0.16)]), fill=255)
        E(0.18, 0.25, 0.58, 0.95) if kind != "ante_levy" else E(0.25, 0.4, 0.55, 0.9)
    elif kind in ("ante_hoplites", "ante_panoply_equipment"):
        # Corinthian helmet in profile: dome, face guard with the eye slit, crest
        d.chord((0.18 * w * K, 0.22 * h * K, 0.78 * w * K, 1.0 * h * K), 180, 360, fill=255)
        d.polygon(P([(0.18, 0.6), (0.78, 0.6), (0.8, 0.98), (0.62, 0.98), (0.6, 0.75), (0.42, 0.75), (0.36, 0.98),
                     (0.18, 0.98)]), fill=255)
        d.chord((0.1 * w * K, -0.02 * h * K, 0.9 * w * K, 0.5 * h * K), 180, 360, fill=255)  # horsehair crest
        d.polygon(P([(0.52, 0.55), (0.84, 0.55), (0.84, 0.7), (0.52, 0.7)]), fill=0)   # eye opening
    elif kind in ("ante_skirmishers",):
        for a in (-0.15, 0.0, 0.15):
            L([(0.2 + a, 0.95), (0.8 + a, 0.05)], 0.06)
            d.polygon(P([(0.8 + a, 0.05), (0.74 + a, 0.2), (0.86 + a, 0.16)]), fill=255)
    elif kind in ("ante_archers", "ante_ranged_equipment"):
        d.arc((0.15 * w * K, 0.02 * h * K, 0.75 * w * K, 0.98 * h * K), 280, 80, fill=255, width=int(0.1 * h * K))
        L([(0.73, 0.1), (0.73, 0.9)], 0.03)
        L([(0.1, 0.5), (0.95, 0.5)], 0.05)
        d.polygon(P([(0.95, 0.5), (0.85, 0.4), (0.85, 0.6)]), fill=255)
    elif kind in ("ante_cavalry", "ante_horse_equipment", "ante_scouts"):
        horse(0.0, 1.0)
        if kind == "ante_cavalry":
            L([(0.2, 0.25), (0.95, 0.0)], 0.05)
    elif kind == "ante_horse_archers":
        horse(0.0, 1.0)
        d.arc((0.3 * w * K, -0.1 * h * K, 0.6 * w * K, 0.45 * h * K), 200, 340, fill=255, width=int(0.08 * h * K))
    elif kind in ("ante_chariots", "ante_chariot_equipment"):
        horse(0.35, 0.65)
        d.ellipse((0.05 * w * K, 0.45 * h * K, 0.35 * w * K, 0.98 * h * K), outline=255, width=int(0.09 * h * K))
        L([(0.2, 0.45), (0.2, 0.98)], 0.04)
        L([(0.05, 0.72), (0.35, 0.72)], 0.04)
        d.polygon(P([(0.08, 0.2), (0.38, 0.2), (0.4, 0.6), (0.06, 0.6)]), fill=255)
        L([(0.38, 0.55), (0.6, 0.55)], 0.05)
    elif kind.startswith(("ante_penteconter", "ante_trireme", "ante_quinquereme")):
        banks = 1 if "penteconter" in kind else 3 if "trireme" in kind else 4
        # hull: ram at the bow (right), raised stern (left)
        d.polygon(P([(0.02, 0.35), (0.08, 0.55), (0.82, 0.58), (1.0, 0.66), (0.86, 0.72), (0.12, 0.72),
                     (0.04, 0.6)]), fill=255)
        L([(0.03, 0.36), (0.0, 0.18)], 0.05)                              # stern post
        L([(0.48, 0.55), (0.48, 0.05)], 0.05)                             # mast
        d.polygon(P([(0.36, 0.1), (0.62, 0.1), (0.6, 0.42), (0.38, 0.42)]), fill=255)  # sail
        for b in range(banks):                                            # oars
            for i in range(9):
                x = 0.16 + i * 0.075 + b * 0.012
                L([(x, 0.7), (x - 0.06, 0.98 - b * 0.05)], 0.025)
    elif kind in ("ante_siege_engines", "ante_siege_equipment"):
        d.polygon(P([(0.1, 0.95), (0.3, 0.1), (0.7, 0.1), (0.9, 0.95)]), fill=255)   # siege tower
        for y in (0.35, 0.6):
            L([(0.2, y), (0.8, y)], 0.04)
        for cx in (0.25, 0.75):
            d.ellipse(((cx - 0.08) * w * K, 0.82 * h * K, (cx + 0.08) * w * K, 1.0 * h * K), fill=0)
    elif kind in ("ante_war_elephants", "ante_elephant_equipment"):
        E(0.15, 0.25, 0.75, 0.75)
        E(0.6, 0.15, 0.9, 0.55)
        L([(0.85, 0.45), (0.92, 0.75), (0.85, 0.95)], 0.09)               # trunk
        for lx in (0.22, 0.35, 0.55, 0.67):
            L([(lx, 0.6), (lx, 0.98)], 0.1)
    im = im.resize((w, h), Image.LANCZOS)
    return im


def glow_icon(mask, colour, glow):
    """vanilla look: flat coloured silhouette with a soft light halo"""
    w, h = mask.size
    halo = mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.6))
    out = Image.new("RGBA", (w, h), glow + (0,))
    out.putalpha(halo.point(lambda v: min(255, int(v * 0.8))))
    body = Image.new("RGBA", (w, h), colour + (255,))
    body.putalpha(mask)
    # a little shading: lighter top
    shade = Image.linear_gradient("L").resize((w, h)).point(lambda v: 255 - v // 3)
    body = Image.composite(body, Image.new("RGBA", (w, h), tuple(int(c * 0.75) for c in colour) + (255,)),
                           shade.point(lambda v: 255 if v > 200 else v))
    body.putalpha(mask)
    return Image.alpha_composite(out, body)


SYMBOL = {"ante_levy": "x", "ante_spearmen": "x", "ante_hoplites": "x=", "ante_skirmishers": "x.", "ante_archers": "x)",
          "ante_cavalry": "/", "ante_horse_archers": "/)", "ante_chariots": "/o", "ante_war_elephants": "/=",
          "ante_siege_engines": ".", "ante_scouts": "/"}


def nato(w, h, sym):
    im = Image.new("RGBA", (w * K, h * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pad = int(0.08 * h * K)
    box = (pad, pad, w * K - pad, h * K - pad)
    for y in range(box[1], box[3]):
        t = (y - box[1]) / (box[3] - box[1])
        c = int(222 - 60 * t)
        d.line((box[0], y, box[2], y), fill=(c, c, c, 255))
    lw = max(2, int(0.06 * h * K))
    d.rectangle(box, outline=(10, 10, 10, 255), width=lw)
    x0, y0, x1, y1 = box
    if "x" in sym:
        d.line((x0, y0, x1, y1), fill=(10, 10, 10, 255), width=lw)
        d.line((x0, y1, x1, y0), fill=(10, 10, 10, 255), width=lw)
    if "/" in sym:
        d.line((x0, y1, x1, y0), fill=(10, 10, 10, 255), width=lw)
    cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, (y1 - y0) * 0.12
    if "." in sym:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(10, 10, 10, 255))
    if "=" in sym:
        d.line((x0, y0 + (y1 - y0) * 0.2, x1, y0 + (y1 - y0) * 0.2), fill=(10, 10, 10, 255), width=lw * 2)
    if ")" in sym:
        d.arc((cx - r * 3, y0 + lw, cx + r * 3, y1 - lw), 300, 60, fill=(10, 10, 10, 255), width=lw)
    if "o" in sym:
        d.ellipse((cx - r * 2, cy - r * 2, cx + r * 2, cy + r * 2), outline=(10, 10, 10, 255), width=lw)
    return im.resize((w, h), Image.LANCZOS)


MATERIAL = {"ante_arms_equipment": (176, 132, 70), "ante_panoply_equipment": (196, 150, 64),
            "ante_ranged_equipment": (138, 92, 52), "ante_horse_equipment": (126, 76, 44),
            "ante_chariot_equipment": (150, 104, 58), "ante_siege_equipment": (128, 90, 54),
            "ante_elephant_equipment": (136, 130, 124)}


def product_icon(key):
    """coloured 'object' picture for the production screen (109 x 30), shaded like the base game's"""
    wide = key.endswith("_hull")
    w, h = (100, 28) if wide else (64, 28)
    mask = silhouette(key, w, h)
    base = MATERIAL.get(key, (120, 82, 48))
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
    pic = Image.new("RGBA", (109, 30), (0, 0, 0, 0))
    x = (109 - w) // 2
    pic.alpha_composite(shadow, (x + 2, 2))
    pic.alpha_composite(obj, (x, 1))
    return pic


def icons():
    sprites = ["# Generated by tools/army.py - icons of the ancient units and equipment (own art, CC0)", "spriteTypes = {"]
    for key in UNITS:
        large = Image.new("RGBA", (152, 42), (0, 0, 0, 0))
        large.alpha_composite(glow_icon(silhouette(key, 62, 34), (78, 118, 72), (225, 235, 215)), (7, 4))
        large.alpha_composite(nato(76, 42, SYMBOL[key]), (76, 0))
        small = Image.new("RGBA", (60, 12), (0, 0, 0, 0))
        small.alpha_composite(glow_icon(silhouette(key, 26, 11), (215, 215, 215), (255, 255, 255)), (2, 0))
        small.alpha_composite(nato(30, 12, SYMBOL[key]), (30, 0))
        large.save(MOD / "gfx" / "interface" / "counters" / "divisions_large" / f"{key}_icon.dds")
        small.save(MOD / "gfx" / "interface" / "counters" / "divisions_small" / f"{key}_icon_small.dds")
        for suffix, tex in (("medium", f"gfx/interface/counters/divisions_large/{key}_icon.dds"),
                            ("medium_white", f"gfx/interface/counters/divisions_small/{key}_icon_small.dds"),
                            ("small", f"gfx/interface/counters/divisions_small/{key}_icon_small.dds")):
            sprites.append(f'\tspriteType = {{ name = "GFX_unit_{key}_icon_{suffix}" '
                           f'textureFile = "{tex}" noOfFrames = 2 }}')
    equipment_keys = list(EQUIPMENT) + [f"{k}_hull" for k in SHIPS]
    for key in equipment_keys:
        wide = key.endswith("_hull")
        im = glow_icon(silhouette(key, 70 if wide else 40, 21), (168, 122, 80), (240, 225, 205))
        pic = Image.new("RGBA", (81, 23), (0, 0, 0, 0))
        pic.alpha_composite(im, (5 if wide else 20, 1))
        pic.save(MOD / "gfx" / "interface" / "archetypes" / f"archetype_{key}.dds")
        sprites.append(f'\tspriteType = {{ name = "GFX_archetype_{key}_medium" '
                       f'texturefile = "gfx/interface/archetypes/archetype_{key}.dds" }}')
        # production line picture of the model (the engine looks for GFX_<equipment>_medium)
        product_icon(key).save(MOD / "gfx" / "interface" / "technologies" / f"{key}_1.dds")
        sprites.append(f'\tspriteType = {{ name = "GFX_{key}_1_medium" '
                       f'texturefile = "gfx/interface/technologies/{key}_1.dds" }}')
        for lvl, *_v in VARIANTS.get(key, []):   # the better models show the same object
            sprites.append(f'\tspriteType = {{ name = "GFX_{key}_{lvl}_medium" '
                           f'texturefile = "gfx/interface/technologies/{key}_1.dds" }}')
    # ships: naval combat / fleet icons (86 x 18, two frames) and the small map counter
    for key in SHIPS:
        big = Image.new("RGBA", (86, 18), (0, 0, 0, 0))
        for f, col in ((0, (205, 205, 200)), (1, (240, 220, 140))):
            big.alpha_composite(glow_icon(silhouette(key, 40, 16), col, (255, 255, 255)), (f * 43 + 1, 1))
        small = glow_icon(silhouette(key, 28, 11), (235, 235, 235), (255, 255, 255))
        sm = Image.new("RGBA", (30, 12), (0, 0, 0, 0))
        sm.alpha_composite(small, (1, 0))
        big.save(MOD / "gfx" / "interface" / "counters" / "divisions_large" / f"{key}_ship.dds")
        sm.save(MOD / "gfx" / "interface" / "counters" / "divisions_small" / f"{key}_ship_small.dds")
        sprites += [f'\tspriteType = {{ name = "GFX_unit_{key}_icon_medium" '
                    f'texturefile = "gfx/interface/counters/divisions_large/{key}_ship.dds" noOfFrames = 2 }}',
                    f'\tspriteType = {{ name = "GFX_unit_{key}_icon_medium_white" '
                    f'texturefile = "gfx/interface/counters/divisions_small/{key}_ship_small.dds" }}',
                    f'\tspriteType = {{ name = "GFX_unit_{key}_icon_medium_black" '
                    f'texturefile = "gfx/interface/counters/divisions_small/{key}_ship_small.dds" }}']
    sprites.append("}")
    write("interface/ante_units.gfx", "\n".join(sprites) + "\n")


# ============================================================================ armies at the start
# culture (world.py name list) -> (main template, second template, share of second)
T_PHALANX = ("Phalanx", {"ante_hoplites": 3, "ante_skirmishers": 1}, ["ante_scouts"])
T_ROMAN = ("Legio", {"ante_hoplites": 2, "ante_spearmen": 1, "ante_skirmishers": 1}, ["ante_scouts"])
T_ITALIC = ("Touta", {"ante_spearmen": 3, "ante_skirmishers": 1}, ["ante_scouts"])
T_WARBAND = ("Warband", {"ante_spearmen": 2, "ante_levy": 1, "ante_skirmishers": 1}, ["ante_scouts"])
T_HORSE = ("Horsemen", {"ante_cavalry": 3}, [])
T_STEPPE = ("Horde", {"ante_horse_archers": 3, "ante_cavalry": 1}, [])
T_PERSIAN = ("Hazarabam", {"ante_spearmen": 2, "ante_archers": 2}, ["ante_scouts", "ante_siege_engines"])
T_PUNIC = ("Host", {"ante_spearmen": 2, "ante_skirmishers": 1, "ante_levy": 1}, ["ante_scouts"])
T_DESERT = ("Raiders", {"ante_skirmishers": 2, "ante_spearmen": 1, "ante_cavalry": 1}, [])
T_KUSH = ("Bowmen", {"ante_archers": 3, "ante_spearmen": 1}, [])
T_CHARIOTS = ("Chariots", {"ante_chariots": 2, "ante_skirmishers": 1}, [])
T_LEVY = ("Levy", {"ante_levy": 3, "ante_skirmishers": 1}, [])

CULTURE_ARMY = {
    "greek": (T_PHALANX, T_HORSE, 0.15), "latin": (T_ROMAN, T_HORSE, 0.15), "italic": (T_ITALIC, T_HORSE, 0.15),
    "iapygian": (T_ITALIC, T_HORSE, 0.2), "etruscan": (T_PHALANX, T_HORSE, 0.15), "celtic": (T_WARBAND, T_HORSE, 0.25),
    "iberian": (T_WARBAND, T_HORSE, 0.2), "germanic": (T_WARBAND, T_LEVY, 0.3), "northern": (T_WARBAND, T_LEVY, 0.4),
    "thracian": (T_WARBAND, T_HORSE, 0.35), "scythian": (T_STEPPE, T_WARBAND, 0.2), "persian": (T_PERSIAN, T_HORSE, 0.3),
    "punic": (T_PUNIC, T_HORSE, 0.2), "libyan": (T_DESERT, T_CHARIOTS, 0.2), "arabian": (T_DESERT, T_LEVY, 0.3),
    "nilotic": (T_KUSH, T_LEVY, 0.3), "caucasian": (T_WARBAND, T_HORSE, 0.3), "anatolian": (T_WARBAND, T_HORSE, 0.3),
    "island": (T_WARBAND, T_LEVY, 0.3),
}
# a few known armies on top of the rule
BONUS = {"ROM": 1, "LAK": 2, "THL": 1, "MKD": 1, "CAR": 1}
SECOND = {"THL": (T_HORSE, 0.5), "MKD": (T_HORSE, 0.35), "GAR": (T_CHARIOTS, 0.4), "CAL": (T_CHARIOTS, 0.3),
          "SYR": (T_HORSE, 0.25)}


def divisions_for(manpower, tag):
    n = int(round(math.sqrt(manpower / 20000)))
    return max(1, min(24, n + BONUS.get(tag, 0)))


def template_block(t):
    name, regs, sup = t
    out = ["division_template = {", f'\tname = "{name}"', "\tregiments = {"]
    x = 0
    for unit, n in regs.items():
        for _ in range(n):
            out.append(f"\t\t{unit} = {{ x = {x // 4} y = {x % 4} }}")
            x += 1
    out.append("\t}")
    if sup:
        out += ["\tsupport = {"] + [f"\t\t{u} = {{ x = 0 y = {i} }}" for i, u in enumerate(sup)] + ["\t}"]
    out.append("}")
    return out


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def armies():
    import world
    C = world.countries()
    states, ports = {}, {}
    for fp in (MOD / "history" / "states").glob("*.txt"):
        t = fp.read_text(encoding="utf-8-sig")
        owner = re.search(r"owner = (\w+)", t).group(1)
        if "impassable = yes" in t:
            continue
        vp = re.search(r"victory_points = \{ (\d+) (\d+)", t)
        prov = int(vp.group(1)) if vp else int(re.search(r"provinces = \{\s*(\d+)", t).group(1))
        states.setdefault(owner, []).append((int(vp.group(2)) if vp else 0,
                                             int(re.search(r"manpower = (\d+)", t).group(1)), prov))
        for pp, lvl in re.findall(r"(\d+) = \{ naval_base = (\d+) \}", t):
            ports.setdefault(owner, []).append((int(lvl), int(vp.group(2)) if vp else 0, int(pp)))
    total = nships = 0
    for tag, c in C.items():
        if tag == "WLD" or tag not in states:
            continue
        own = sorted(states[tag], reverse=True)  # most important first
        mp = sum(s[1] for s in own)
        n = divisions_for(mp, tag)
        main, second, share = CULTURE_ARMY.get(c["names"], (T_WARBAND, T_HORSE, 0.2))
        if tag in SECOND:
            second, share = SECOND[tag]
        n2 = int(round(n * share)) if n > 1 else 0
        out = [f"# Generated by tools/army.py - army of {c['name']} in 509 BC ({mp:,} manpower)"]
        out += template_block(main)
        if n2:
            out += template_block(second)
        out += ["units = {"]
        for i in range(n):
            t = second if i >= n - n2 else main
            prov = own[i % len(own)][2]
            out += ["\tdivision = {", f'\t\tname = "{ordinal(i + 1)} {c["adj"]} {t[0]}"',
                    f"\t\tlocation = {prov}", f'\t\tdivision_template = "{t[0]}"', "\t\tstart_experience_factor = 0.3",
                    "\t\tstart_equipment_factor = 1", "\t}"]
        out += ["}", "", "instant_effect = {"]
        for eq, amount in (("ante_arms_equipment_1", 200 * n), ("ante_ranged_equipment_1", 80 * n),
                           ("ante_horse_equipment_1", 40 * n)):
            out.append(f"\tadd_equipment_to_stockpile = {{ type = {eq} amount = {amount} producer = {tag} }}")
        out.append("}")
        write(f"history/units/{tag}_245.txt", "\n".join(out) + "\n")
        total += n
        nships += fleet(tag, c, mp, ports.get(tag))
    return total, nships


# naval tradition: ships per sqrt(manpower / 20000), share of triremes (new in the late 6th century)
NAVAL = {"punic": (3.0, 0.5), "greek": (1.2, 0.3), "etruscan": (1.2, 0.2), "latin": (0.6, 0.0), "island": (0.6, 0.0),
         "iberian": (0.4, 0.0), "italic": (0.3, 0.0), "iapygian": (0.4, 0.0), "arabian": (0.3, 0.0),
         "celtic": (0.3, 0.0), "northern": (0.3, 0.0), "germanic": (0.3, 0.0), "libyan": (0.2, 0.0)}
FIXED_FLEET = {"PRS": (20, 0.6)}  # the Phoenician and Ionian squadrons of the King


def roman(n):
    out = ""
    for v, r in ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += r
            n -= v
    return out


def fleet(tag, c, mp, port_list):
    """history/units/<TAG>_245_naval.txt - always written (empty without ports) so the history line never breaks"""
    lines = [f"# Generated by tools/army.py - fleet of {c['name']} in 509 BC", "units = {"]
    n, tri = 0, 0.0
    if port_list:
        w, tri = NAVAL.get(c["names"], (0.2, 0.0))
        n = int(round(w * math.sqrt(mp / 20000)))
        if n == 0 and w >= 0.5:
            n = 1
        if tag in FIXED_FLEET:
            n, tri = FIXED_FLEET[tag]
        n = min(n, 30)
    if n:
        base = sorted(port_list, reverse=True)[0][2]
        n_tri = int(round(n * tri))
        lines += ["\tfleet = {", f'\t\tname = "{c["adj"]} Fleet"', f"\t\tnaval_base = {base}",
                  "\t\ttask_force = {", f'\t\t\tname = "{c["adj"]} Squadron"', f"\t\t\tlocation = {base}"]
        count = {}
        for i in range(n):
            key = "ante_trireme" if i < n_tri else "ante_penteconter"
            count[key] = count.get(key, 0) + 1
            nm = f'{c["adj"]} {SHIPS[key]["name"]} {roman(count[key])}'
            lines.append(f'\t\t\tship = {{ name = "{nm}" definition = {key} start_experience_factor = 0.2 '
                         f'equipment = {{ {key}_hull_1 = {{ amount = 1 owner = {tag} }} }} }}')
        lines += ["\t\t}", "\t}"]
    lines.append("}")
    write(f"history/units/{tag}_245_naval.txt", "\n".join(lines) + "\n")
    return n


def localisation():
    out = ["l_english:"]
    for key, u in UNITS.items():
        out += [f' {key}:0 "{u["name"]}"', f' {key}_desc:0 "{u["desc"]}"']
    for key, (name, short, desc, *_r) in EQUIPMENT.items():
        out += [f' {key}:0 "{name}"', f' {key}_desc:0 "{desc}"', f' {key}_1:0 "{name}"',
                f' {key}_1_short:0 "{short}"', f' {key}_1_desc:0 "{desc}"']
        for lvl, vname, vshort, fac in VARIANTS.get(key, []):
            out += [f' {key}_{lvl}:0 "{vname}"', f' {key}_{lvl}_short:0 "{vshort}"',
                    f' {key}_{lvl}_desc:0 "{desc} Better made: +{round((fac - 1) * 100)}% fighting strength."']
    for key, sh in SHIPS.items():
        out += [f' {key}:0 "{sh["name"]}"', f' {key}_desc:0 "{sh["desc"]}"', f' {key}_hull:0 "{sh["name"]}"',
                f' {key}_hull_desc:0 "{sh["desc"]}"', f' {key}_hull_1:0 "{sh["name"]}"',
                f' {key}_hull_1_short:0 "{sh["name"]}"', f' {key}_hull_1_desc:0 "{sh["desc"]}"']
    write("localisation/english/ante_army_l_english.yml", "\n".join(out) + "\n", bom=True)


def main():
    for sub in ("counters/divisions_large", "counters/divisions_small", "archetypes", "technologies"):
        (MOD / "gfx" / "interface" / sub).mkdir(parents=True, exist_ok=True)
    vanilla_overrides()
    write("common/units/ante_units.txt", units_file())
    write("common/units/equipment/ante_equipment.txt", equipment_file())
    icons()
    localisation()
    n, ships = armies()
    print(f"written: {len(UNITS)} unit types, {len(SHIPS)} ship types, {len(EQUIPMENT) + len(SHIPS)} equipment types, "
          f"{len(VANILLA_LAND) + len(VANILLA_NAVAL)} base-game unit files emptied, {n} divisions and {ships} ships")


if __name__ == "__main__":
    main()
