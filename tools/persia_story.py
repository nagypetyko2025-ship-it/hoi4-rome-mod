"""Persia's story systems: the unrest of the satrapies, revolts, the breaking of the empire, and the Great King's goal
(used by tools/content.py; built like rome_story.py and carthage_story.py). Plan: docs/persia_focus_tree.md.

Round 40 (Peti): "Persia's life should not be too easy: its size becomes a small handicap - a few countries (in
Anatolia, Egypt, ...) want to break away, Persia must handle it with decisions, and if it does not pay attention and
it climbs too high, the country falls apart into a 3-4 sided civil war and some countries become independent.
Persia needs a goal to reach, like Rome or Carthage."

  Five restless satrapies, each with a meter PRS_unrest_<key> (0-100):
      Egypt (KMT), Babylon (BBL), Ionia (ION), Lydia and Phrygia (LYD), Bactria (BKT)
      - the breakaway countries are defined in tools/data/world_509bc.py (RELEASABLE) with cores on their regions.
  Every week each meter rises by the same drift: 0.18 for the sheer size of the empire, more at war, with low
  stability and beyond 100 states; focuses (the satrap system, the King's Eyes, tolerance, the Royal Road...) and the
  Great King's goal bring the drift down, the regional focuses calm one satrapy each.
  The national spirit "Unrest of the Satrapies" follows the average: +3 % stability / +0.05 political power at 0,
  -17 % / -0.25 at 100.
  Decisions (category "The Satrapies"), for each satrapy: the King's Eye (50 PP, -15), a garrison (25 PP and 3000 men,
  -20), honours for its gods and nobles (100 PP, -30).
  At 60 a satrapy grows restless (an event with choices), at 100 it rises: it is released with an army and fights
  for its freedom. When three satrapies stand above 70 at once, the empire breaks: every one of them above 70 rises,
  and a pretender takes Media and the north in a civil war - a war of four or more sides.
  The goal: "King of the Four Corners of the World" - Hellas (Athens, Sparta, Thebes, Corinth, Argos, Euboea,
  Thessaly, Macedon) under the King or his subjects, Egypt and Babylon still his: a great spirit, the unrest falls
  and stays low.

Writes (content.py calls write_all): common/dynamic_modifiers/PRS_dynamic_modifiers.txt,
common/scripted_effects/PRS_scripted_effects.txt, events/PRS_events.txt, common/decisions/PRS_decisions.txt,
common/decisions/categories/PRS_categories.txt, gfx/flags/(medium/, small/)PRS_PRETENDER.tga.
"""
import re
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent
LOC = {}
IDEAS = {}

# key, breakaway tag, name, unrest at the start (509 BC: Ionia is ten years from its great revolt)
SATRAPIES = [("egypt", "KMT", "Egypt", 30), ("babylon", "BBL", "Babylon", 25), ("ionia", "ION", "Ionia", 40),
             ("lydia", "LYD", "Lydia and Phrygia", 15), ("bactria", "BKT", "Bactria", 20)]
REBELS = {"egypt": 6, "babylon": 5, "ionia": 4, "lydia": 4, "bactria": 4}   # divisions of a rising
PRETENDER_REGIONS = ("Mada", "Raga", "Armina", "Varkana", "Parthava")      # the north rises with a pretender
GREECE = ["ATH", "LAK", "THB", "KRN", "AGS", "EUB", "THL", "MKD"]           # the Great King's goal


def idea(key, name, pic, **mods):
    IDEAS[key] = (name, "generic_" + pic, mods)


def _ind(text, tabs):
    pad = "\t" * tabs
    return "\n".join(pad + l if l.strip() else l for l in text.splitlines())


# ------------------------------------------------------------------ meters
def unrest(key, n):
    """an effect line: one satrapy's unrest moves by n (with a tooltip)"""
    name = dict((k, nm) for k, _, nm, _ in SATRAPIES)[key]
    tt = f"PRS_TT_UNREST_{key.upper()}_{'P' if n > 0 else 'M'}{abs(n)}"
    LOC[tt] = f"Unrest in {name}: {'§R+' if n > 0 else '§G'}{n}§!"
    return (f"custom_effect_tooltip = {tt}\n"
            f"hidden_effect = {{ add_to_variable = {{ PRS_unrest_{key} = {n} }} PRS_unrest_update = yes }}")


def unrest_all(n):
    tt = f"PRS_TT_UNREST_ALL_{'P' if n > 0 else 'M'}{abs(n)}"
    LOC[tt] = f"Unrest in every satrapy: {'§R+' if n > 0 else '§G'}{n}§!"
    body = " ".join(f"add_to_variable = {{ PRS_unrest_{k} = {n} }}" for k, *_ in SATRAPIES)
    return f"custom_effect_tooltip = {tt}\nhidden_effect = {{ {body} PRS_unrest_update = yes }}"


def drift_flag(flag, text):
    """a focus that lowers the weekly drift for good (the flag is read by WEEKLY)"""
    LOC[f"PRS_TT_DRIFT_{flag.upper()}"] = text
    return f"set_country_flag = {flag}\ncustom_effect_tooltip = PRS_TT_DRIFT_{flag.upper()}"


DRIFT_FLAGS = {   # flag -> change of the weekly drift of every satrapy (focuses set them)
    "PRS_satrap_system": -0.03, "PRS_kings_eyes": -0.05, "PRS_royal_road_built": -0.02, "PRS_law_of_the_king": -0.03,
    "PRS_gods_of_every_people": -0.04, "PRS_satrap_armies": 0.03, "PRS_four_corners": -0.10,
}
REGION_FLAGS = {  # flag -> (satrapy, weekly change)
    "PRS_pharaoh": ("egypt", -0.10), "PRS_marduk_honoured": ("babylon", -0.10), "PRS_marduk_melted": ("babylon", 0.08),
    "PRS_ionian_democracies": ("ionia", -0.10), "PRS_ionian_tyrants": ("ionia", 0.05),
    "PRS_lydian_nobles": ("lydia", -0.08), "PRS_bactrian_prince": ("bactria", -0.10),
}

DYNAMIC = """# Generated by tools/persia_story.py - the unrest of the satrapies, shown as a national spirit
PRS_satrapal_unrest = {
	enable = { always = yes }
	icon = GFX_idea_generic_disjointed_gov
	stability_factor = PRS_dm_stab
	political_power_gain = PRS_dm_pp
}
"""

EFFECTS = ["# Generated by tools/persia_story.py", "PRS_unrest_update = {"]
EFFECTS += [f"\tclamp_variable = {{ var = PRS_unrest_{k} min = 0 max = 100 }}" for k, *_ in SATRAPIES]
EFFECTS += ["\tset_variable = { PRS_unrest_avg = 0 }"]
EFFECTS += [f"\tadd_to_variable = {{ PRS_unrest_avg = PRS_unrest_{k} }}" for k, *_ in SATRAPIES]
EFFECTS += [f"\tdivide_variable = {{ PRS_unrest_avg = {len(SATRAPIES)} }}",
            "\tset_variable = { PRS_dm_stab = PRS_unrest_avg }", "\tmultiply_variable = { PRS_dm_stab = -0.002 }",
            "\tadd_to_variable = { PRS_dm_stab = 0.03 }",
            "\tset_variable = { PRS_dm_pp = PRS_unrest_avg }", "\tmultiply_variable = { PRS_dm_pp = -0.003 }",
            "\tadd_to_variable = { PRS_dm_pp = 0.05 }", "\tforce_update_dynamic_modifier = yes", "}", ""]


# a rising: the satrapy is released with an army and fights for its freedom (scope: PRS)
def revolt_effect(key, tag, n):
    units = "\n".join(
        f'\t\t\tcreate_unit = {{ division = "name = \\"Rebels {i + 1}\\" division_template = \\"Host of the Rising\\" '
        f'start_experience_factor = 0.2 start_equipment_factor = 1" owner = {tag} }}' for i in range(n))
    return f"""PRS_revolt_{key} = {{
	if = {{
		limit = {{ NOT = {{ country_exists = {tag} }} any_owned_state = {{ is_core_of = {tag} }} }}
		release = {tag}
		if = {{ limit = {{ {tag} = {{ is_subject_of = PRS }} }} end_puppet = {tag} }}   # free, not a puppet
		{tag} = {{
			add_manpower = {2000 * n}
			division_template = {{
				name = "Host of the Rising"
				regiments = {{
					ante_spearmen = {{ x = 0 y = 0 }}
					ante_spearmen = {{ x = 0 y = 1 }}
					ante_levy = {{ x = 0 y = 2 }}
					ante_archers = {{ x = 1 y = 0 }}
				}}
			}}
			capital_scope = {{
{units}
			}}
			add_equipment_to_stockpile = {{ type = ante_arms_equipment_1 amount = {150 * n} producer = {tag} }}
			add_equipment_to_stockpile = {{ type = ante_ranged_equipment_1 amount = {60 * n} producer = {tag} }}
			declare_war_on = {{ target = PRS type = annex_everything }}
		}}
		log = "ANTE|[GetDateText]|revolt|PRS|{tag}"
	}}
	set_variable = {{ PRS_unrest_{key} = 0 }}
	PRS_unrest_update = yes
}}
"""


for _k, _t, _n, _s in SATRAPIES:
    EFFECTS.append(revolt_effect(_k, _t, REBELS[_k]))


def _states_where(pred):
    out = []
    for fp in sorted((MOD / "history" / "states").glob("*.txt")):
        t = fp.read_text(encoding="utf-8-sig")
        sid = int(re.search(r"\bid\s*=\s*(\d+)", t).group(1))
        owner = re.search(r"\bowner\s*=\s*(\w+)", t).group(1)
        if pred(fp.stem.split("-", 1)[1], owner, t):
            out.append(sid)
    return out


def pretender_states():
    return _states_where(lambda name, owner, t: owner == "PRS" and any(r in name for r in PRETENDER_REGIONS))


def greek_states():
    return _states_where(lambda name, owner, t: owner in GREECE)


def core_states(tag):
    return _states_where(lambda name, owner, t: f"add_core_of = {tag}" in t)


# ------------------------------------------------------------------ events
EVENTS = []


def event(eid, title, desc, pic, options, immediate=""):
    n = f"ante_persia.{eid}"
    LOC[f"{n}.t"] = title
    LOC[f"{n}.d"] = desc
    lines = ["country_event = {", f"\tid = {n}", f"\ttitle = {n}.t", f"\tdesc = {n}.d",
             f"\tpicture = GFX_ante_event_{pic}", "\tis_triggered_only = yes"]
    if immediate:
        lines += ["\timmediate = {", _ind(immediate, 2), "\t}"]
    for i, (text, eff, ai) in enumerate(options):
        key = f"{n}.{'abcde'[i]}"
        LOC[key] = text
        lines += ["\toption = {", f"\t\tname = {key}", f"\t\tai_chance = {{ factor = {ai} }}"]
        if eff:
            lines.append(_ind(eff, 2))
        lines.append("\t}")
    lines.append("}")
    EVENTS.append("\n".join(lines))


FLAVOUR = {
    "egypt": ("The priests of Sais remember the pharaohs of their own blood; the farmers of the Delta remember the "
              "tribute. In the temples, men speak of a new king of Upper and Lower Egypt."),
    "babylon": ("Babylon was the greatest city of the world when Persia was a tribe of shepherds. At the New Year "
                "festival, nobody takes the hands of Marduk for the King - and the crowds notice."),
    "ionia": ("The tyrants the King set over the Greek cities are hated, and the merchants of Miletus count the tribute. "
              "Envoys sail west to Athens and Eretria to ask for ships."),
    "lydia": ("Sardis was the capital of Croesus, the richest king of the world. The Lydian and Phrygian nobles serve the "
              "satrap - and wonder why they should."),
    "bactria": ("Bactria is far from Susa and close to the steppe. Its satrap commands horsemen enough to make himself a "
                "king, and the nomads beyond the Oxus would gladly ride with him."),
}
for i, (k, tag, name, _) in enumerate(SATRAPIES):
    event(10 + i, f"Unrest in {name}", FLAVOUR[k] + f" (Unrest in {name}: [?PRS_unrest_{k}|0])", "crowd", [
        ("Send the army - and let them see it.", "add_manpower = -2000\n" + unrest(k, -15), 50),
        ("Gold and honours for the great families.", "add_political_power = -50\n" + unrest(k, -20), 40),
        ("The satrap will deal with it.", unrest(k, 5), 10)])
    event(20 + i, f"{name} Rises!", f"The satrapy of {name} has thrown off the rule of the King. Its nobles have "
          f"crowned a king of their own, and an army marches against the King's garrisons.", "war", [
        ("They will learn what rebellion costs.", "add_war_support = 0.05", 95),
        ("Let them go. The empire is large enough.",
         f"white_peace = {{ tag = {tag} }}\nadd_stability = -0.05\n" + unrest_all(10), 5)],
        immediate=f"PRS_revolt_{k} = yes")

LOC["PRS_TT_EMPIRE_BREAKS"] = ("§RThe empire breaks:§! every satrapy above 70 unrest rises, and a pretender takes Media "
                               "and the north in a civil war.")
EMPIRE_BREAKS = ["set_country_flag = { flag = PRS_empire_broke days = 3650 value = 1 }",
                 "custom_effect_tooltip = PRS_TT_EMPIRE_BREAKS", "hidden_effect = {"]
EMPIRE_BREAKS += [f"\tif = {{ limit = {{ check_variable = {{ PRS_unrest_{k} > 69.9 }} }} PRS_revolt_{k} = yes }}"
                  for k, *_ in SATRAPIES]
EMPIRE_BREAKS += ["}"]


def collapse_event():
    states = " ".join(str(s) for s in pretender_states())
    eff = "\n".join(EMPIRE_BREAKS) + f"""
start_civil_war = {{
	ideology = fascism
	size = 0.3
	states = {{ {states} }}
	states_filter = {{ is_owned_by = ROOT }}
	set_cosmetic_tag = PRS_PRETENDER
}}
log = "ANTE|[GetDateText]|empire_breaks|PRS|PRS"
""" + "\n".join(f"set_variable = {{ PRS_unrest_{k} = 20 }}" for k, *_ in SATRAPIES) + "\nPRS_unrest_update = yes"
    event(40, "The Empire Breaks", "Too many satrapies, too many enemies, too few loyal men. Egypt, Babylon or the "
          "Greek cities rise at once - and in Media a man of the old royal house calls himself King of Kings. "
          "The empire of Darius is at war with itself.", "war", [
              ("The Truth will defeat the Lie.", "add_war_support = 0.10\nadd_manpower = 5000", 100)], immediate=eff)


# ------------------------------------------------------------------ weekly drift and thresholds
def weekly():
    init = "\n".join(f"\t\tset_variable = {{ PRS_unrest_{k} = {s} }}" for k, _, _, s in SATRAPIES)
    drift = ["\tset_variable = { PRS_drift = 0.18 }",
             "\tif = { limit = { has_war = yes } add_to_variable = { PRS_drift = 0.12 } }",
             "\tif = { limit = { has_stability < 0.5 } add_to_variable = { PRS_drift = 0.12 } }",
             "\tif = { limit = { num_of_controlled_states > 100 } add_to_variable = { PRS_drift = 0.08 } }"]
    drift += [f"\tif = {{ limit = {{ has_country_flag = {f} }} add_to_variable = {{ PRS_drift = {v} }} }}"
              for f, v in DRIFT_FLAGS.items()]
    per = []
    for k, tag, _, _ in SATRAPIES:
        reg = " ".join(f"if = {{ limit = {{ has_country_flag = {f} }} add_to_variable = {{ PRS_unrest_{k} = {v} }} }}"
                       for f, (kk, v) in REGION_FLAGS.items() if kk == k)
        per.append(f"\tif = {{ limit = {{ NOT = {{ country_exists = {tag} }} }} "
                   f"add_to_variable = {{ PRS_unrest_{k} = PRS_drift }} {reg} }}\n"
                   f"\telse = {{ set_variable = {{ PRS_unrest_{k} = 0 }} }}")
    hot = ["\tset_variable = { PRS_hot = 0 }"] + [
        f"\tif = {{ limit = {{ check_variable = {{ PRS_unrest_{k} > 69.9 }} }} add_to_variable = {{ PRS_hot = 1 }} }}"
        for k, *_ in SATRAPIES]
    rise = []
    for i, (k, tag, _, _) in enumerate(SATRAPIES):
        rise.append(f"""		if = {{
			limit = {{ check_variable = {{ PRS_unrest_{k} > 99.9 }} NOT = {{ country_exists = {tag} }} }}
			country_event = {{ id = ante_persia.{20 + i} }}
		}}
		else_if = {{
			limit = {{ check_variable = {{ PRS_unrest_{k} > 59.9 }} NOT = {{ has_country_flag = PRS_warned_{k} }} }}
			random = {{
				chance = 6
				set_country_flag = {{ flag = PRS_warned_{k} days = 365 value = 1 }}
				country_event = {{ id = ante_persia.{10 + i} }}
			}}
		}}""")
    return f"""if = {{
	limit = {{ original_tag = PRS }}
	if = {{
		limit = {{ NOT = {{ has_country_flag = PRS_unrest_started }} }}
		set_country_flag = PRS_unrest_started
{init}
		add_dynamic_modifier = {{ modifier = PRS_satrapal_unrest }}
	}}
{chr(10).join(drift)}
{chr(10).join(per)}
	PRS_unrest_update = yes
{chr(10).join(hot)}
	if = {{
		limit = {{ check_variable = {{ PRS_hot > 2.9 }} NOT = {{ has_country_flag = PRS_empire_broke }} }}
		country_event = {{ id = ante_persia.40 }}
	}}
	else = {{
{chr(10).join(rise)}
	}}
}}"""


# ------------------------------------------------------------------ decisions
DECISIONS = []


def decision(key, name, desc, icon, visible, available, cost, effect, ai, days_re_enable=0, extra=""):
    LOC[key] = name
    LOC[f"{key}_desc"] = desc
    lines = [f"\t{key} = {{", f"\t\ticon = {icon}", "\t\tallowed = { original_tag = PRS }",
             "\t\tvisible = {", _ind(visible, 3), "\t\t}"]
    if available:
        lines += ["\t\tavailable = {", _ind(available, 3), "\t\t}"]
    if extra:
        lines.append(_ind(extra, 2))
    lines.append(f"\t\tcost = {cost}")
    if days_re_enable:
        lines.append(f"\t\tdays_re_enable = {days_re_enable}")
    lines += ["\t\tcomplete_effect = {", _ind(effect, 3), "\t\t}",
              "\t\tai_will_do = {", _ind(ai, 3), "\t\t}", "\t}"]
    DECISIONS.append("\n".join(lines))


for k, tag, name, _ in SATRAPIES:
    vis = f"NOT = {{ country_exists = {tag} }}\nhas_country_flag = PRS_unrest_started"
    decision(f"PRS_kings_eye_{k}", f"The King's Eye in {name}",
             f"An inspector of the King, with an escort and the power to dismiss officials, travels to {name}. "
             f"(Unrest now: [?PRS_unrest_{k}|0].)", "GFX_decision_generic_political_discourse", vis, "", 50,
             unrest(k, -15), f"base = 0\nmodifier = {{ add = 5 check_variable = {{ PRS_unrest_{k} > 45 }} }}",
             days_re_enable=90)
    decision(f"PRS_garrison_{k}", f"Garrison {name}",
             f"Persian and Median spearmen in the citadels of {name}: rebels count the King's soldiers first. "
             f"(Unrest now: [?PRS_unrest_{k}|0].)", "GFX_decision_generic_military", vis, "has_manpower > 3000", 25,
             "add_manpower = -3000\n" + unrest(k, -20),
             f"base = 0\nmodifier = {{ add = 4 check_variable = {{ PRS_unrest_{k} > 60 }} }}", days_re_enable=180)
    decision(f"PRS_honours_{k}", f"Honour the Gods and Nobles of {name}",
             f"Gifts to the temples, offices and land for the great families of {name}, a royal visit. "
             f"(Unrest now: [?PRS_unrest_{k}|0].)", "GFX_decision_generic_civil_support", vis, "", 100,
             unrest(k, -30), f"base = 0\nmodifier = {{ add = 8 check_variable = {{ PRS_unrest_{k} > 75 }} }}",
             days_re_enable=365)

# the goal: King of the Four Corners of the World
idea("PRS_four_corners_spirit", "King of the Four Corners of the World", "pp_unity_bonus",
     stability_factor=0.15, political_power_gain=0.30, war_support_factor=0.10, industrial_capacity_factory=0.10,
     conscription=0.02)


def goal_decision():
    greek = greek_states()
    held = "\n".join(f"{s} = {{ controller = {{ OR = {{ tag = ROOT is_subject_of = ROOT }} }} }}" for s in greek)
    egypt = "\n".join(f"controls_state = {s}" for s in core_states("KMT"))
    babylon = "\n".join(f"controls_state = {s}" for s in core_states("BBL"))
    LOC["PRS_TT_HELLAS_HELD"] = (f"All of Hellas ({len(greek)} states: Athens, Sparta, Thebes, Corinth, Argos, Euboea, "
                                 "Thessaly, Macedon) is held by the King or his subjects")
    LOC["PRS_TT_EGYPT_BABYLON_HELD"] = "Egypt and Babylon are still the King's"
    decision("PRS_four_corners", "King of the Four Corners of the World",
             "I am Darius, the Great King, King of Kings, King of the lands of all peoples, King of this great earth "
             "far and wide. Hellas has given earth and water; from Egypt to Bactria every land obeys.",
             "GFX_decision_generic_formable_nations", "NOT = { has_country_flag = PRS_four_corners }",
             f"custom_trigger_tooltip = {{\n\ttooltip = PRS_TT_HELLAS_HELD\n{_ind(held, 1)}\n}}\n"
             f"custom_trigger_tooltip = {{\n\ttooltip = PRS_TT_EGYPT_BABYLON_HELD\n{_ind(egypt, 1)}\n{_ind(babylon, 1)}\n}}",
             50, drift_flag("PRS_four_corners", "The unrest of every satrapy grows §G0.10 slower§! every week, for good.")
             + "\nadd_ideas = PRS_four_corners_spirit\n" + unrest_all(-40)
             + "\nevery_owned_state = {\n\tlimit = { OR = { " + " ".join(f"state = {s}" for s in greek)
             + " } }\n\tadd_core_of = ROOT\n}",
             "base = 100",
             extra="highlight_states = {\n\thighlight_state_targets = {\n"
                   + "\n".join(f"\t\tstate = {s}" for s in greek) + "\n\t}\n}\non_map_mode = decision_view_only\n"
                   "fire_only_once = yes")


LOC["PRS_satrapies_category"] = "The Satrapies"
LOC["PRS_satrapies_category_desc"] = (
    "Unrest in the satrapies (0-100): Egypt §Y[?PRS_unrest_egypt|0]§!, Babylon §Y[?PRS_unrest_babylon|0]§!, "
    "Ionia §Y[?PRS_unrest_ionia|0]§!, Lydia and Phrygia §Y[?PRS_unrest_lydia|0]§!, Bactria §Y[?PRS_unrest_bactria|0]§!.\\n"
    "The size of the empire makes them grow every week - faster at war, with low stability and beyond 100 states. "
    "At §R60§! a satrapy grows restless, at §R100§! it rises; when three stand above §R70§! at once, the empire breaks "
    "into civil war.")
LOC["PRS_satrapal_unrest"] = "Unrest of the Satrapies (average [?PRS_unrest_avg|0])"
LOC["PRS_satrapal_unrest_desc"] = ("Twenty peoples, twenty satraps, one King. The decisions of the category 'The "
                                   "Satrapies' keep the restless ones quiet.")
LOC["PRS_PRETENDER"] = "Median Pretender"
LOC["PRS_PRETENDER_DEF"] = "the Median Pretender"
LOC["PRS_PRETENDER_ADJ"] = "Median"
for _ide in ("democratic", "fascism", "communism", "neutrality"):
    LOC[f"PRS_PRETENDER_{_ide}"] = LOC["PRS_PRETENDER"]
    LOC[f"PRS_PRETENDER_{_ide}_DEF"] = LOC["PRS_PRETENDER_DEF"]
    LOC[f"PRS_PRETENDER_{_ide}_ADJ"] = LOC["PRS_PRETENDER_ADJ"]

CATEGORY = """# Generated by tools/persia_story.py
PRS_satrapies_category = {
	icon = generic_political_actions
	allowed = { original_tag = PRS }
	priority = 100
}
"""


def pretender_flag():
    """the Median pretender: a dark field with a golden winged sun disc (own art)"""
    from PIL import Image, ImageDraw
    S = 4
    W, H = 82 * S, 52 * S
    im = Image.new("RGBA", (W, H), (60, 40, 80, 255))
    d = ImageDraw.Draw(im)
    gold = (226, 182, 72, 255)
    cx, cy = W // 2, H // 2
    d.ellipse((cx - 7 * S, cy - 7 * S, cx + 7 * S, cy + 7 * S), fill=gold)
    for side in (-1, 1):
        for k in range(4):
            y = cy - 6 * S + k * 4 * S
            d.polygon([(cx + side * 8 * S, y), (cx + side * (30 - 4 * k) * S, y - 2 * S),
                       (cx + side * (30 - 4 * k) * S, y + 2 * S), (cx + side * 8 * S, y + 3 * S)], fill=gold)
    big = im.resize((82, 52), Image.LANCZOS)
    for sub, size in (("", (82, 52)), ("medium", (41, 26)), ("small", (10, 7))):
        p = (MOD / "gfx" / "flags" / sub / "PRS_PRETENDER.tga") if sub else (MOD / "gfx" / "flags" / "PRS_PRETENDER.tga")
        p.parent.mkdir(parents=True, exist_ok=True)
        big.resize(size, Image.LANCZOS).save(p)


WEEKLY = ""   # filled by build() (needs history/states)


def build():
    global WEEKLY
    if not EVENTS or not any("ante_persia.40" in e for e in EVENTS):
        collapse_event()
    WEEKLY = weekly()


def write_all():
    build()
    goal_decision()

    def write(rel, text):
        p = MOD / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")

    write("common/dynamic_modifiers/PRS_dynamic_modifiers.txt", DYNAMIC)
    write("common/scripted_effects/PRS_scripted_effects.txt", "\n".join(EFFECTS) + "\n")
    write("events/PRS_events.txt", "# Generated by tools/persia_story.py\nadd_namespace = ante_persia\n\n"
          + "\n\n".join(EVENTS) + "\n")
    write("common/decisions/PRS_decisions.txt", "# Generated by tools/persia_story.py\nPRS_satrapies_category = {\n"
          + "\n\n".join(DECISIONS) + "\n}\n")
    write("common/decisions/categories/PRS_categories.txt", CATEGORY)
    pretender_flag()
    return len(EVENTS), len(DECISIONS)
