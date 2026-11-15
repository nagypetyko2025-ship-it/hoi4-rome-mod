"""Persia's story systems: the unrest of the satrapies, revolts, the breaking of the empire, and the Great King's goal
(used by tools/content.py; built like rome_story.py and carthage_story.py). Plan: docs/persia_focus_tree.md.

Round 40 (Peti): "Persia's life should not be too easy: its size becomes a small handicap - a few countries (in
Anatolia, Egypt, ...) want to break away, Persia must handle it with decisions, and if it does not pay attention and
it climbs too high, the country falls apart into a 3-4 sided civil war and some countries become independent.
Persia needs a goal to reach, like Rome or Carthage."

  Five restless satrapies, each with a meter PRS_unrest_<key> (0-100):
      Egypt (KMT), Babylon (BBL), Ionia (ION), Lydia and Phrygia (LYD), Bactria (BKT)
      - the breakaway countries are defined in tools/data/world_509bc.py (RELEASABLE) with cores on their regions.
  Every week each meter rises by the same drift: 0.08 for every state Persia controls (round 47: 6.5 at the start), more at war, with low
  stability, beyond 80 and 100 states; focuses (the satrap system, the King's Eyes, tolerance, the Royal Road...) and the
  Great King's goal bring the drift down, the regional focuses calm one satrapy each.
  The national spirit "Unrest of the Satrapies" follows the average: +3 % stability / +0.05 political power at 0,
  -17 % / -0.25 at 100.
  Decisions (category "The Satrapies"), for each satrapy: the King's Eye (50 PP, -15), a garrison (25 PP and 3000 men,
  -20), honours for its gods and nobles (100 PP, -30).
  At 60 a satrapy grows restless (an event with choices), at 100 it rises: it is released with an army and fights
  for its freedom. When two satrapies have risen and a third stands above 70, the empire breaks (round 50): every one above 70 rises,
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
import victory  # noqa: E402   the victory screen (round 42)
LOC = {}
IDEAS = {}

# key, breakaway tag, name, unrest at the start (509 BC: Ionia is ten years from its great revolt)
# round 47 (Peti): every satrapy starts equally restless and rises at the same pace - left alone, each one rises
# within two months; Ionia (ten years from its great revolt) starts higher and goes first
SATRAPIES = [("egypt", "KMT", "Egypt", 40), ("babylon", "BBL", "Babylon", 40), ("ionia", "ION", "Ionia", 50),
             ("lydia", "LYD", "Lydia and Phrygia", 40), ("bactria", "BKT", "Bactria", 40)]
# divisions of a rising (round 47: real armies - the levies of the satrapy go over to the rebels, and the King
# loses 6000 men for each of their divisions)
REBELS = {"egypt": 16, "babylon": 14, "ionia": 10, "lydia": 12, "bactria": 12}
DRIFT_PER_STATE = 0.0185  # weekly unrest for every state Persia controls (round 52, Peti: 81 states = 1.5 a week)
AI_DRIFT_FACTOR = 0.3    # an AI Persia: 30 % of that (2.2 a week at the start) - the AI cannot keep up (round 48)
PRETENDER_REGIONS = ("Mada", "Raga", "Armina", "Varkana", "Parthava")      # the north rises with a pretender
GREECE = ["ATH", "LAK", "THB", "KRN", "AGS", "EUB", "THL", "MKD"]           # the Great King's goal
# the goal needs everything the focus tree can win (round 45, Peti): (tooltip key, original owners, text)
GOAL_GROUPS = [("HELLAS", GREECE, "All of Hellas (Athens, Sparta, Thebes, Corinth, Argos, Euboea, Thessaly, Macedon)"),
               ("PHOENICIA", ["SDN", "TYR", "ARW"], "Phoenicia (Sidon, Tyre, Arwad)"),
               ("STEPPE", ["SCY", "MSG"], "The steppe (the Scythians, the Massagetae)"),
               ("AFRICA", ["KSH", "MRM", "KYR"], "Africa beyond Egypt (Kush, the Marmaridae, Cyrene)")]


def idea(key, name, pic, **mods):
    IDEAS[key] = (name, "generic_" + pic, mods)


idea("PRS_rebel_fervour_spirit", "Fighting for Freedom", "morale_bonus", army_attack_factor=0.15,
     army_defence_factor=0.15, army_org_factor=0.10)


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


def unrest_below(key, n):
    """a trigger: one satrapy's unrest is below n"""
    name = dict((k, nm) for k, _, nm, _ in SATRAPIES)[key]
    LOC[f"PRS_TT_UNREST_{key.upper()}_BELOW_{n}"] = f"Unrest in {name} is below {n} (now: [?PRS_unrest_{key}|Y0])"
    return (f"custom_trigger_tooltip = {{ tooltip = PRS_TT_UNREST_{key.upper()}_BELOW_{n} "
            f"check_variable = {{ PRS_unrest_{key} < {n} }} }}")


# ------------------------------------------------------------------ the end of the road for a satrapy (round 41, Peti)
# A focus pair for each satrapy at the end of the tree: integrate it for good (only when its unrest is below 20), or
# set it free as a loyal puppet of the lowest autonomy. Either way its unrest is gone for good.
def tag_of(key):
    return dict((k, t) for k, t, _, _ in SATRAPIES)[key]


def can_settle(key):
    """the satrapy has not broken away, and the King still holds its land"""
    tag = tag_of(key)
    name = dict((k, nm) for k, _, nm, _ in SATRAPIES)[key]
    LOC[f"PRS_TT_SETTLE_{key.upper()}"] = f"{name} has not broken away, and the King holds its land"
    return (f"custom_trigger_tooltip = {{ tooltip = PRS_TT_SETTLE_{key.upper()} NOT = {{ country_exists = {tag} }} "
            f"any_owned_state = {{ is_core_of = {tag} }} }}")


def integrate(key):
    tag = tag_of(key)
    name = dict((k, nm) for k, _, nm, _ in SATRAPIES)[key]
    LOC[f"PRS_TT_INTEGRATED_{key.upper()}"] = (f"§G{name} becomes part of the empire for good:§! its unrest is gone, it "
                                               f"can never rise again, and its states are the King's own cores.")
    return (f"set_country_flag = PRS_integrated_{key}\ncustom_effect_tooltip = PRS_TT_INTEGRATED_{key.upper()}\n"
            f"hidden_effect = {{\n\tset_variable = {{ PRS_unrest_{key} = 0 }}\n\tPRS_unrest_update = yes\n"
            f"\tevery_state = {{\n\t\tlimit = {{ is_core_of = {tag} }}\n\t\tremove_core_of = {tag}\n"
            f"\t\tif = {{ limit = {{ is_owned_by = ROOT }} add_core_of = ROOT }}\n\t}}\n}}\n"
            f"add_stability = 0.03\nadd_political_power = 50")


def set_free(key):
    tag = tag_of(key)
    name = dict((k, nm) for k, _, nm, _ in SATRAPIES)[key]
    LOC[f"PRS_TT_FREED_{key.upper()}"] = (f"§Y{name}§! is released as a loyal subject of the lowest autonomy "
                                          f"(integrated puppet): no more unrest, no more risings.")
    return (f"set_country_flag = PRS_freed_{key}\ncustom_effect_tooltip = PRS_TT_FREED_{key.upper()}\n"
            f"hidden_effect = {{\n\trelease_puppet = {tag}\n"
            f"\tif = {{ limit = {{ country_exists = {tag} }} set_autonomy = {{ target = {tag} autonomy_state = autonomy_integrated_puppet }} }}\n"
            f"\tset_variable = {{ PRS_unrest_{key} = 0 }}\n\tPRS_unrest_update = yes\n}}\n"
            f"add_stability = 0.05\n" + unrest_all(-5))


def drift_flag(flag, text):
    """a focus that lowers the weekly drift for good (the flag is read by WEEKLY)"""
    LOC[f"PRS_TT_DRIFT_{flag.upper()}"] = text
    return f"set_country_flag = {flag}\ncustom_effect_tooltip = PRS_TT_DRIFT_{flag.upper()}"


DRIFT_FLAGS = {   # flag -> change of the weekly drift of every satrapy (focuses set them)
    "PRS_satrap_system": -0.12, "PRS_kings_eyes": -0.20, "PRS_royal_road_built": -0.08, "PRS_law_of_the_king": -0.12,
    "PRS_gods_of_every_people": -0.16, "PRS_satrap_armies": 0.12, "PRS_four_corners": -0.40,
}
REGION_FLAGS = {  # flag -> (satrapy, weekly change)
    "PRS_pharaoh": ("egypt", -0.40), "PRS_marduk_honoured": ("babylon", -0.40), "PRS_marduk_melted": ("babylon", 0.32),
    "PRS_ionian_democracies": ("ionia", -0.40), "PRS_ionian_tyrants": ("ionia", 0.20),
    "PRS_lydian_nobles": ("lydia", -0.32), "PRS_bactrian_prince": ("bactria", -0.40),
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
			add_manpower = {5000 * n}
			add_timed_idea = {{ idea = PRS_rebel_fervour_spirit days = 365 }}
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
			add_equipment_to_stockpile = {{ type = ante_arms_equipment_1 amount = {250 * n} producer = {tag} }}
			add_equipment_to_stockpile = {{ type = ante_ranged_equipment_1 amount = {100 * n} producer = {tag} }}
			declare_war_on = {{ target = PRS type = annex_everything }}
		}}
		add_manpower = -{6000 * n}
		set_country_flag = PRS_revolted_{key}   # once crushed, it never rises again (weekly)
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
        ("Send the army - and let them see it.", "add_manpower = -10000\n" + unrest(k, -25), 50),
        ("Gold and honours for the great families.", "add_political_power = -50\n" + unrest(k, -30), 40),
        ("The satrap will deal with it.", unrest(k, 10), 10)])
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
if = {{
	limit = {{ NOT = {{ has_government = fascism }} }}
	start_civil_war = {{
		ideology = fascism
		size = 0.3
		states = {{ {states} }}
		states_filter = {{ is_owned_by = ROOT }}
		set_cosmetic_tag = PRS_PRETENDER
	}}
}}
else = {{
	start_civil_war = {{
		ideology = neutrality
		size = 0.3
		states = {{ {states} }}
		states_filter = {{ is_owned_by = ROOT }}
		set_cosmetic_tag = PRS_PRETENDER
	}}
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
    # round 47 (Peti): "Ionia should rise within two months if you do not watch it - Persia starts with more than half
    # a million men, its size must be turned against it". The drift grows with the empire: 0.08 a week for every
    # state it controls (81 at the start = 6.5 a week, Ionia from 40 to 100 in about 9 weeks); war and low stability
    # add 2.5 each; the focuses take some of it away, but never below 0.5.
    drift = ["\tset_variable = { PRS_drift = num_controlled_states }",
             f"\tmultiply_variable = {{ PRS_drift = {DRIFT_PER_STATE} }}",
             "\tif = { limit = { has_war = yes } add_to_variable = { PRS_drift = 0.5 } }",
             "\tif = { limit = { has_stability < 0.5 } add_to_variable = { PRS_drift = 0.5 } }"]
    drift += [f"\tif = {{ limit = {{ has_country_flag = {f} }} add_to_variable = {{ PRS_drift = {v} }} }}"
              for f, v in DRIFT_FLAGS.items()]
    # round 48 (Peti): the AI cannot keep up with that pace - an AI Persia's satrapies grow at 30 %
    drift += [f"\tif = {{ limit = {{ is_ai = yes }} multiply_variable = {{ PRS_drift = {AI_DRIFT_FACTOR} }} }}",
              "\tif = { limit = { check_variable = { PRS_drift < 0.1 } } set_variable = { PRS_drift = 0.1 } }"]
    per = []
    for k, tag, _, _ in SATRAPIES:
        reg = " ".join(f"if = {{ limit = {{ has_country_flag = {f} }} add_to_variable = {{ PRS_unrest_{k} = {v} }} }}"
                       for f, (kk, v) in REGION_FLAGS.items() if kk == k)
        # a rising that was crushed (the rebel country is gone again): the satrapy never rises again (round 47)
        per.append(f"\tif = {{ limit = {{ has_country_flag = PRS_revolted_{k} NOT = {{ country_exists = {tag} }} "
                   f"NOT = {{ has_country_flag = PRS_integrated_{k} }} }} set_country_flag = PRS_integrated_{k} "
                   f"every_state = {{ limit = {{ is_core_of = {tag} }} remove_core_of = {tag} }} "
                   f"log = \"ANTE|[GetDateText]|crushed|PRS|{tag}\" }}")
        per.append(f"\tif = {{ limit = {{ NOT = {{ country_exists = {tag} }} NOT = {{ has_country_flag = PRS_integrated_{k} }} }} "
                   f"add_to_variable = {{ PRS_unrest_{k} = PRS_drift }} {reg} }}\n"
                   f"\telse = {{ set_variable = {{ PRS_unrest_{k} = 0 }} }}")
    # round 50: the empire breaks only when two satrapies have actually risen (their rebel countries stand) and a
    # third is above 70. The first test broke the empire in its fifth week: all five grow at the same pace, so three
    # stood above 70 at once before the player could do anything at all.
    hot = ["\tset_variable = { PRS_hot = 0 }", "\tset_variable = { PRS_risen = 0 }"] + [
        f"\tif = {{ limit = {{ check_variable = {{ PRS_unrest_{k} > 69.9 }} }} add_to_variable = {{ PRS_hot = 1 }} }}"
        for k, *_ in SATRAPIES] + [
        f"\tif = {{ limit = {{ country_exists = {tag} has_country_flag = PRS_revolted_{k} }} "
        f"add_to_variable = {{ PRS_risen = 1 }} }}" for k, tag, *_ in SATRAPIES]
    rise = []
    for i, (k, tag, _, _) in enumerate(SATRAPIES):
        rise.append(f"""		if = {{
			limit = {{ check_variable = {{ PRS_unrest_{k} > 99.9 }} NOT = {{ country_exists = {tag} }} }}
			country_event = {{ id = ante_persia.{20 + i} }}
		}}
		else_if = {{
			limit = {{ check_variable = {{ PRS_unrest_{k} > 59.9 }} NOT = {{ has_country_flag = PRS_warned_{k} }} }}
			random = {{
				chance = 30
				set_country_flag = {{ flag = PRS_warned_{k} days = 120 value = 1 }}
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
		limit = {{ check_variable = {{ PRS_risen > 1.9 }} check_variable = {{ PRS_hot > 0.9 }} NOT = {{ has_country_flag = PRS_empire_broke }} }}
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
    vis = (f"NOT = {{ country_exists = {tag} }}\nhas_country_flag = PRS_unrest_started\n"
           f"NOT = {{ has_country_flag = PRS_integrated_{k} }}")
    decision(f"PRS_kings_eye_{k}", f"The King's Eye in {name}",
             f"An inspector of the King, with an escort and the power to dismiss officials, travels to {name}. "
             f"(Unrest now: [?PRS_unrest_{k}|0].)", "GFX_decision_generic_political_discourse", vis, "", 25,
             unrest(k, -25), f"base = 0\nmodifier = {{ add = 5 check_variable = {{ PRS_unrest_{k} > 35 }} }}",
             days_re_enable=30)
    # round 47: the King's half a million men are the price - every garrison eats 15 000 of them
    decision(f"PRS_garrison_{k}", f"Garrison {name}",
             f"Persian and Median spearmen in the citadels of {name}: rebels count the King's soldiers first. "
             f"(Unrest now: [?PRS_unrest_{k}|0].)", "GFX_decision_generic_military", vis, "has_manpower > 15000", 10,
             "add_manpower = -15000\n" + unrest(k, -40),
             f"base = 0\nmodifier = {{ add = 6 check_variable = {{ PRS_unrest_{k} > 50 }} }}", days_re_enable=45)
    decision(f"PRS_honours_{k}", f"Honour the Gods and Nobles of {name}",
             f"Gifts to the temples, offices and land for the great families of {name}, a royal visit. "
             f"(Unrest now: [?PRS_unrest_{k}|0].)", "GFX_decision_generic_civil_support", vis, "", 75,
             unrest(k, -60), f"base = 0\nmodifier = {{ add = 8 check_variable = {{ PRS_unrest_{k} > 70 }} }}",
             days_re_enable=120)

# the goal: King of the Four Corners of the World
idea("PRS_four_corners_spirit", "King of the Four Corners of the World", "pp_unity_bonus",
     stability_factor=0.15, political_power_gain=0.30, war_support_factor=0.10, industrial_capacity_factory=0.10,
     conscription=0.02)


# the Satrap Empire's goal (round 53, Peti: "this Persia sets out to conquer the Balkans"): the Balkans, Hellas, and
# Arabaya back - (tooltip key, original owners, text)
EUROPE_GROUPS = [
    ("THRACE", ["ODR", "BES", "GTA", "TRB", "PAE", "THS"], "Thrace (the Odrysae, Bessi, Getae, Triballi, Paeonia, Thasos)"),
    ("ILLYRIA", ["DRD", "ENC", "TLN", "AUT", "EPD"], "Illyria (the Dardani, Enchelei, Taulantii, Autariatae, Epidamnos)"),
    ("PONTUS", ["BYZ", "APP", "ITR"], "The Pontic cities (Byzantion, Apollonia, Istros)"),
    ("HELLAS", GREECE + ["CHK"], "All of Hellas and Macedon (with the Chalkidike)"),
]
idea("PRS_king_of_europe_spirit", "King of Europe and Asia", "pp_unity_bonus", stability_factor=0.15,
     political_power_gain=0.30, war_support_factor=0.10, industrial_capacity_factory=0.10, conscription=0.02)


def europe_goal_decision():
    def held(ids):
        return "\n".join(f"{x} = {{ controller = {{ OR = {{ tag = ROOT is_subject_of = ROOT }} }} }}" for x in ids)
    groups = []
    for key, tags, text in EUROPE_GROUPS:
        ids = _states_where(lambda name, owner, t, tags=tags: owner in tags)
        LOC[f"PRS_TT_EUROPE_{key}"] = f"{text} ({len(ids)} states) is held by the King or his subjects"
        groups.append((key, ids))
    ids = core_states("ARB")
    LOC["PRS_TT_EUROPE_ARABAYA"] = f"Arabaya ({len(ids)} states) is the King's again"
    groups.append(("ARABAYA", ids))
    every = sorted({x for _, ids in groups for x in ids})
    avail = "\n".join(f"custom_trigger_tooltip = {{\n\ttooltip = PRS_TT_EUROPE_{key}\n{_ind(held(ids), 1)}\n}}"
                      for key, ids in groups)
    decision("PRS_king_of_europe", "King of Europe and Asia",
             "From the Danube to the Euphrates, from the Adriatic to the Halys: the Satrap Empire rules both shores of "
             "the straits. The house of Achaemenes had its day - this is the day of Sardis.",
             "GFX_decision_generic_form_nation",
             "has_country_flag = PRS_satraps_road\nNOT = { has_country_flag = PRS_king_of_europe }", avail, 50,
             "set_country_flag = PRS_king_of_europe\nadd_ideas = PRS_king_of_europe_spirit\n"
             "every_owned_state = {\n\tlimit = { OR = { " + " ".join(f"state = {x}" for x in every)
             + " } }\n\tadd_core_of = ROOT\n}\n" + victory.FIRE["PRS_SATRAPS"], "base = 100",
             extra="highlight_states = {\n\thighlight_state_targets = {\n"
                   + "\n".join(f"\t\tstate = {x}" for x in every) + "\n\t}\n}\non_map_mode = decision_view_only\n"
                   "fire_only_once = yes")


def goal_decision():
    """round 45 (Peti: too easy): everything the focus tree can win - Hellas, the Phoenician cities, the Scythians and
    the Massagetae, Kush, the Marmaridae and Cyrene - and Egypt and Babylon kept. Every state is outlined on the map."""
    def held(ids):
        return "\n".join(f"{s} = {{ controller = {{ OR = {{ tag = ROOT is_subject_of = ROOT }} }} }}" for s in ids)
    groups = []
    for key, tags, text in GOAL_GROUPS:
        ids = _states_where(lambda name, owner, t, tags=tags: owner in tags)
        LOC[f"PRS_TT_GOAL_{key}"] = f"{text} ({len(ids)} states) is held by the King or his subjects"
        groups.append((key, ids))
    ids = core_states("KMT") + core_states("BBL")
    LOC["PRS_TT_GOAL_HOME"] = "Egypt and Babylon are still the King's (or his loyal subjects')"
    groups.append(("HOME", ids))
    every = sorted({s for _, ids in groups for s in ids})
    won = sorted({s for key, ids in groups if key != "HOME" for s in ids})
    avail = "\n".join(f"custom_trigger_tooltip = {{\n\ttooltip = PRS_TT_GOAL_{key}\n{_ind(held(ids), 1)}\n}}"
                      for key, ids in groups)
    decision("PRS_four_corners", "King of the Four Corners of the World",
             "I am Darius, the Great King, King of Kings, King of the lands of all peoples, King of this great earth "
             "far and wide. Hellas has given earth and water, Phoenicia sails for me, the Scythians and the Massagetae "
             "are beaten, Kush and Libya send their tribute; from Egypt to Bactria every land obeys.",
             "GFX_decision_generic_form_nation",
             "NOT = { has_country_flag = PRS_four_corners }\nNOT = { has_country_flag = PRS_satraps_road }", avail,
             50, drift_flag("PRS_four_corners", "The unrest of every satrapy grows §G0.40 slower§! every week, for good.")
             + "\nadd_ideas = PRS_four_corners_spirit\n" + unrest_all(-40)
             + "\nevery_owned_state = {\n\tlimit = { OR = { " + " ".join(f"state = {s}" for s in won)
             + " } }\n\tadd_core_of = ROOT\n}\n" + victory.FIRE["PRS"],
             "base = 100",
             extra="highlight_states = {\n\thighlight_state_targets = {\n"
                   + "\n".join(f"\t\tstate = {s}" for s in every) + "\n\t}\n}\non_map_mode = decision_view_only\n"
                   "fire_only_once = yes")


LOC["PRS_satrapies_category"] = "The Satrapies"
LOC["PRS_satrapies_category_desc"] = (
    "Unrest in the satrapies (0-100): Egypt §Y[?PRS_unrest_egypt|0]§!, Babylon §Y[?PRS_unrest_babylon|0]§!, "
    "Ionia §Y[?PRS_unrest_ionia|0]§!, Lydia and Phrygia §Y[?PRS_unrest_lydia|0]§!, Bactria §Y[?PRS_unrest_bactria|0]§!.\\n"
    "The size of the empire makes them grow every week - faster at war, with low stability and beyond 100 states. "
    "At §R60§! a satrapy grows restless, at §R100§! it rises; when two have risen and a third stands above §R70§!, the empire breaks "
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
	visible = { NOT = { has_country_flag = PRS_satraps_road } }
	priority = 100
}

PRS_great_king_category = {
	icon = generic_formable_nations
	allowed = { original_tag = PRS }
	priority = 90
}
"""
# the goal has a category of its own, like Rome's Latin Culture and Carthage's Punic World (round 44, Peti)
LOC["PRS_great_king_category"] = "The Great King"
LOC["PRS_great_king_category_desc"] = ("Darius rules twenty peoples. One goal remains: Hellas must give earth and water, "
                                       "while Egypt and Babylon stay loyal - then the King is King of the Four Corners "
                                       "of the World.")


def pretender_flag(key="PRS_PRETENDER", field=(60, 40, 80)):
    """a pretender or the loyalists: a dark field with a golden winged sun disc (own art)"""
    from PIL import Image, ImageDraw
    S = 4
    W, H = 82 * S, 52 * S
    im = Image.new("RGBA", (W, H), field + (255,))
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
        p = (MOD / "gfx" / "flags" / sub / f"{key}.tga") if sub else (MOD / "gfx" / "flags" / f"{key}.tga")
        p.parent.mkdir(parents=True, exist_ok=True)
        big.resize(size, Image.LANCZOS).save(p)


# ------------------------------------------------------------------ the Satraps' Revolt (round 49, Peti)
# The left road of Persia's start tree: Egypt, Arabaya and Bactria go free (not at war), Babylon and Ionia rise (war), the satraps of the west crown
# Oroetes of Sardis (the player's Persia becomes the 'tyranny' of the ancient world), and Persis, Media and the east
# stay loyal to Darius in a civil war. The usurper's own tree (national_trees.py, PRS_satraps) starts once it is won.
# round 54 (Peti): Egypt, Arabaya and Bactria go free in peace; Babylon and Ionia rise and fight in the civil war
SECEDE = {"KMT": 10, "ARB": 6, "BKT": 8, "BBL": 12, "ION": 8}    # divisions of the countries that go free
FIGHT = {"BBL", "ION"}
LOYAL_REGIONS = ("Parsa", "Uvja", "Mada", "Raga", "Karmana", "Maka", "Varkana", "Parthava", "Haraiva", "Zranka",
                 "Harauvatish")


def secede_effect(tag, n, war=False):
    fight = "\t\t\tdeclare_war_on = { target = PRS type = annex_everything }   # they fight in the civil war\n" if war else ""
    units = "\n".join(
        f'\t\t\tcreate_unit = {{ division = "name = \\"Guard {i + 1}\\" division_template = \\"Host of the Rising\\" '
        f'start_experience_factor = 0.2 start_equipment_factor = 1" owner = {tag} }}' for i in range(n))
    return f"""PRS_secede_{tag} = {{
	if = {{
		limit = {{ NOT = {{ country_exists = {tag} }} any_owned_state = {{ is_core_of = {tag} }} }}
		release = {tag}
		if = {{ limit = {{ {tag} = {{ is_subject_of = PRS }} }} end_puppet = {tag} }}
		{tag} = {{
			add_manpower = {4000 * n}
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
			add_equipment_to_stockpile = {{ type = ante_arms_equipment_1 amount = {250 * n} producer = {tag} }}
			add_equipment_to_stockpile = {{ type = ante_ranged_equipment_1 amount = {100 * n} producer = {tag} }}
{fight}		}}
		log = "ANTE|[GetDateText]|secede|PRS|{tag}"
	}}
}}
"""


for _t, _n in SECEDE.items():
    EFFECTS.append(secede_effect(_t, _n, _t in FIGHT))


def loyal_states():
    return _states_where(lambda name, owner, t: owner == "PRS" and any(r in name for r in LOYAL_REGIONS))


def sardis():
    return _states_where(lambda name, owner, t: name == "Sparda")[0]


LOC["PRS_TT_SATRAPS_REVOLT"] = ("§YEgypt, Arabaya and Bactria§! go their own way in peace; §RBabylon and Ionia§! rise and "
                                "§Rmake war on you§!. The satraps of the west "
                                "crown §YOroetes of Sardis§! (Tyranny) - the §YSatrap Empire§!; §RPersis, Media and the "
                                "east§! stay loyal to Darius in a §Rcivil war§!. The satrapies no longer rise against you. "
                                "Win the war for the throne - then the usurper's own focus tree opens.")
LOC["PRS_SATRAPS"] = "Satrap Empire"
LOC["PRS_SATRAPS_DEF"] = "the Satrap Empire"
LOC["PRS_SATRAPS_ADJ"] = "Satrapal"
for _ide in ("democratic", "fascism", "communism", "neutrality"):
    LOC[f"PRS_SATRAPS_{_ide}"] = LOC["PRS_SATRAPS"]
    LOC[f"PRS_SATRAPS_{_ide}_DEF"] = LOC["PRS_SATRAPS_DEF"]
    LOC[f"PRS_SATRAPS_{_ide}_ADJ"] = LOC["PRS_SATRAPS_ADJ"]
# map colours of the cosmetic tags (common/countries/cosmetic.txt): the usurper crimson, the loyalists the old purple
COSMETIC_COLOURS = {"PRS_SATRAPS": (160, 30, 40), "PRS_LOYALISTS": (212, 176, 62), "PRS_PRETENDER": (70, 50, 90)}
# peace with Egypt and Bactria once the throne is won - only Arabaya is still to be taken back (round 53)
LOC["PRS_TT_PEACE_EGYPT_BACTRIA"] = ("Peace with §YEgypt§!, §YBactria§! and §YArabaya§!; Egypt and Bactria are friends now "
                                     "(non-aggression). Only Arabaya is still to be taken back.")
THRONE_PEACE = "\n".join(["custom_effect_tooltip = PRS_TT_PEACE_EGYPT_BACTRIA", "hidden_effect = {"] + [
    f"\tif = {{ limit = {{ country_exists = {t} has_war_with = {t} }} white_peace = {{ tag = {t} }} }}"
    for t in ("KMT", "BKT", "ARB")] + [
    f"\tif = {{ limit = {{ country_exists = {t} NOT = {{ has_war_with = {t} }} }} "
    f"diplomatic_relation = {{ country = {t} relation = non_aggression_pact active = yes }} }}" for t in ("KMT", "BKT")]
    + ["}"])
LOC["PRS_LOYALISTS"] = "Persian Empire"   # round 53 (Peti): the loyalists are the original Persia
LOC["PRS_LOYALISTS_DEF"] = "the Persian Empire"
LOC["PRS_LOYALISTS_ADJ"] = "Persian"
for _ide in ("democratic", "fascism", "communism", "neutrality"):
    LOC[f"PRS_LOYALISTS_{_ide}"] = LOC["PRS_LOYALISTS"]
    LOC[f"PRS_LOYALISTS_{_ide}_DEF"] = LOC["PRS_LOYALISTS_DEF"]
    LOC[f"PRS_LOYALISTS_{_ide}_ADJ"] = LOC["PRS_LOYALISTS_ADJ"]
DRIFT_FLAGS["PRS_satraps_road"] = -0.4      # the satraps rule: the satrapies are calmer on this road
SATRAPS_REVOLT = "\n".join([
    "set_country_flag = PRS_satraps_road", "custom_effect_tooltip = PRS_TT_SATRAPS_REVOLT", "hidden_effect = {",
    "\tset_cosmetic_tag = PRS_SATRAPS",
    "\tPRS_secede_KMT = yes", "\tPRS_secede_ARB = yes", "\tPRS_secede_BKT = yes",
    "\tPRS_secede_BBL = yes", "\tPRS_secede_ION = yes",
    f"\tset_capital = {{ state = {sardis()} }}",
    "\tset_politics = { ruling_party = fascism elections_allowed = no }",
    "\tset_popularities = { fascism = 70 neutrality = 30 democratic = 0 communism = 0 }",
    "\tpromote_character = PRS_oroetes",
    "\tstart_civil_war = {", "\t\tideology = neutrality", "\t\tsize = 0.5",
    "\t\tstates = { " + " ".join(str(x) for x in loyal_states()) + " }",
    "\t\tstates_filter = { is_owned_by = ROOT }", "\t\tset_cosmetic_tag = PRS_LOYALISTS", "\t}",
    # round 53 (Peti): the satraps rule themselves on this road - no satrapy unrest at all
    ] + [f"\tset_country_flag = PRS_integrated_{k}" for k, *_ in SATRAPIES]
    + [f"\tset_variable = {{ PRS_unrest_{k} = 0 }}" for k, *_ in SATRAPIES] + [
    "\tPRS_unrest_update = yes",
    "\tif = { limit = { has_dynamic_modifier = { modifier = PRS_satrapal_unrest } } "
    "remove_dynamic_modifier = { modifier = PRS_satrapal_unrest } }",
    '\tlog = "ANTE|[GetDateText]|satraps_revolt|PRS|PRS"', "}",
    "add_war_support = 0.15", "add_political_power = 100"])


def satraps_flag():
    """the Satrap Empire: a crimson field, a golden band at the hoist, an eight-rayed golden sun (own art)"""
    import math
    from PIL import Image, ImageDraw
    S = 4
    W, H = 82 * S, 52 * S
    im = Image.new("RGBA", (W, H), (160, 30, 40, 255))
    d = ImageDraw.Draw(im)
    gold = (232, 190, 80, 255)
    d.rectangle((0, 0, 12 * S, H), fill=gold)
    cx, cy = W // 2 + 6 * S, H // 2
    pts = []
    for i in range(16):
        r = (17 if i % 2 == 0 else 7) * S
        a = math.pi * i / 8
        pts.append((cx + r * math.sin(a), cy - r * math.cos(a)))
    d.polygon(pts, fill=gold)
    d.ellipse((cx - 5 * S, cy - 5 * S, cx + 5 * S, cy + 5 * S), fill=(160, 30, 40, 255))
    d.ellipse((cx - 3 * S, cy - 3 * S, cx + 3 * S, cy + 3 * S), fill=gold)
    big = im.resize((82, 52), Image.LANCZOS)
    for sub_, size in (("", (82, 52)), ("medium", (41, 26)), ("small", (10, 7))):
        q = (MOD / "gfx" / "flags" / sub_ / "PRS_SATRAPS.tga") if sub_ else (MOD / "gfx" / "flags" / "PRS_SATRAPS.tga")
        q.parent.mkdir(parents=True, exist_ok=True)
        big.resize(size, Image.LANCZOS).save(q)


WEEKLY = ""   # filled by build() (needs history/states)


def build():
    global WEEKLY
    if not EVENTS or not any("ante_persia.40" in e for e in EVENTS):
        collapse_event()
    WEEKLY = weekly()


def write_all():
    build()
    n = len(DECISIONS)
    goal_decision()
    europe_goal_decision()
    goal = DECISIONS[n:]          # the goal goes to the category of the Great King
    del DECISIONS[n:]

    def write(rel, text):
        p = MOD / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")

    write("common/dynamic_modifiers/PRS_dynamic_modifiers.txt", DYNAMIC)
    write("common/scripted_effects/PRS_scripted_effects.txt", "\n".join(EFFECTS) + "\n")
    write("events/PRS_events.txt", "# Generated by tools/persia_story.py\nadd_namespace = ante_persia\n\n"
          + "\n\n".join(EVENTS) + "\n")
    write("common/decisions/PRS_decisions.txt", "# Generated by tools/persia_story.py\nPRS_satrapies_category = {\n"
          + "\n\n".join(DECISIONS) + "\n}\n\nPRS_great_king_category = {\n" + "\n\n".join(goal) + "\n}\n")
    write("common/decisions/categories/PRS_categories.txt", CATEGORY)
    pretender_flag()
    for sub_ in ("", "medium", "small"):    # the loyalists fly the original flag of Persia
        d = MOD / "gfx" / "flags" / sub_ if sub_ else MOD / "gfx" / "flags"
        (d / "PRS_LOYALISTS.tga").write_bytes((d / "PRS.tga").read_bytes())
    satraps_flag()
    write("common/countries/cosmetic.txt", "# Generated by tools/persia_story.py - map colours of cosmetic tags\n" + "".join(
        f"{k} = {{\n\tcolor = rgb {{ {r} {g} {b} }}\n\tcolor_ui = rgb {{ {min(255, r + 40)} {min(255, g + 40)} {min(255, b + 40)} }}\n}}\n"
        for k, (r, g, b) in COSMETIC_COLOURS.items()))
    return len(EVENTS), len(DECISIONS) + len(goal)
