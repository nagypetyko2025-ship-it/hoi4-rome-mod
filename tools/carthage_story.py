"""Carthage's story systems: two meters, events and decisions (used by tools/content.py; built like rome_story.py).

The focus tree (tools/national_trees.py, plan docs/carthage_focus_tree.md) decides WHAT Carthage becomes; this file
makes the road uneven. One meter for each road, both move UP and DOWN (Rome's lesson: no focus may wait for a number
that can only go one way):

  The House of Mago - CAR_suspicion (0-100), "the Suspicion of the Council".
      Starts at 30. War raises it every week (victorious generals are dangerous), peace lowers it; ruling by the
      sword raises it, bargaining lowers it; gifts to the council (decision) lower it, triumphs raise it.
      Spirit: from +5 % stability / +0.1 political power at 0 to -25 % stability / -0.3 political power at 100.
      Above 50 the council plots (ante_carthage.20); at 100 it strikes (ante_carthage.21): the House of Mago falls and
      Carthage takes the road of the Hundred and Four after all.
  The Hundred and Four - CAR_arrears (0-100), "the Mercenaries' Arrears".
      Starts at 20. War raises it every week (more mercenaries, longer campaigns), a mercenary army raises it more,
      peace and a citizen army lower it; paying the mercenaries (decision) and the silver of Iberia lower it.
      Spirit: from +3 % stability / +5 % organisation at 0 to -22 % stability / -15 % organisation at 100.
      At 80 the mercenaries mutiny (ante_carthage.30).

Writes (content.py calls write_all): common/dynamic_modifiers/CAR_dynamic_modifiers.txt,
common/scripted_effects/CAR_scripted_effects.txt, common/scripted_localisation/CAR_scripted_localisation.txt,
events/CAR_events.txt, common/decisions/CAR_decisions.txt, common/decisions/categories/CAR_categories.txt.
Event pictures: the ones of rome_story.py (senate, crowd, war, vote, king, conspiracy, fire).
"""
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent
LOC = {}
IDEAS = {}

MAGO, COUNCIL = "has_country_flag = CAR_dynasty", "has_country_flag = CAR_council"
ROAD_MAGO = "§YRoad of the House of Mago§!"
ROAD_COUNCIL = "§YRoad of the Hundred and Four§!"


def idea(key, name, pic, **mods):
    IDEAS[key] = (name, "generic_" + pic, mods)


def _ind(text, tabs):
    pad = "\t" * tabs
    return "\n".join(pad + l if l.strip() else l for l in text.splitlines())


# ------------------------------------------------------------------ meters
def _meter(var, n, name, good_when_down=True):
    sign = "+" if n > 0 else ""
    bad = (n > 0) == good_when_down
    key = f"CAR_TT_{var.upper()}_{'P' if n > 0 else 'M'}{abs(n)}"
    LOC[key] = f"{name}: {'§R' if bad else '§G'}{sign}{n}§!"
    return (f"custom_effect_tooltip = {key}\n"
            f"hidden_effect = {{ add_to_variable = {{ {var} = {n} }} {var}_update = yes }}")


def suspicion(n):
    return _meter("CAR_suspicion", n, "Suspicion of the Council")


def arrears(n):
    return _meter("CAR_arrears", n, "Mercenaries' Arrears")


def suspicion_below(n):
    LOC[f"CAR_TT_SUSPICION_BELOW_{n}"] = f"Suspicion of the Council is at most {n} (now: [?CAR_suspicion|Y0])"
    return (f"custom_trigger_tooltip = {{ tooltip = CAR_TT_SUSPICION_BELOW_{n} "
            f"check_variable = {{ CAR_suspicion < {n + 0.01} }} }}")


def arrears_below(n):
    LOC[f"CAR_TT_ARREARS_BELOW_{n}"] = f"Mercenaries' Arrears are at most {n} (now: [?CAR_arrears|Y0])"
    return (f"custom_trigger_tooltip = {{ tooltip = CAR_TT_ARREARS_BELOW_{n} "
            f"check_variable = {{ CAR_arrears < {n + 0.01} }} }}")


START_DYNASTY = """set_country_flag = CAR_dynasty
set_variable = { CAR_suspicion = 30 }
CAR_suspicion_update = yes
add_dynamic_modifier = { modifier = CAR_suspicion_of_the_council }
custom_effect_tooltip = CAR_TT_START_DYNASTY
country_event = { id = ante_carthage.1 days = 60 random_days = 30 }
country_event = { id = ante_carthage.5 days = 900 random_days = 300 }"""
START_COUNCIL = """set_country_flag = CAR_council
set_variable = { CAR_arrears = 20 }
CAR_arrears_update = yes
add_dynamic_modifier = { modifier = CAR_mercenaries_arrears }
custom_effect_tooltip = CAR_TT_START_COUNCIL
country_event = { id = ante_carthage.1 days = 60 random_days = 30 }
country_event = { id = ante_carthage.5 days = 900 random_days = 300 }"""
# the council strikes: the dynasty falls, Carthage becomes the republic of the Hundred and Four after all
COUP = """set_country_flag = CAR_council_coup
clr_country_flag = CAR_dynasty
remove_dynamic_modifier = { modifier = CAR_suspicion_of_the_council }
set_variable = { CAR_suspicion = 0 }
if = { limit = { has_idea = CAR_magonid_rule_spirit } remove_ideas = CAR_magonid_rule_spirit }
if = { limit = { has_idea = CAR_military_monarchy_spirit } remove_ideas = CAR_military_monarchy_spirit }
add_stability = -0.10
complete_national_focus = CAR_hundred_and_four
set_country_flag = CAR_council
if = {
	limit = { NOT = { has_dynamic_modifier = { modifier = CAR_mercenaries_arrears } } }
	add_dynamic_modifier = { modifier = CAR_mercenaries_arrears }
}
set_variable = { CAR_arrears = 40 }
CAR_arrears_update = yes"""
LOC["CAR_TT_START_DYNASTY"] = ("§YThe Suspicion of the Council§! begins at §Y30§!. War and the rule of the sword raise it, "
                               "peace and gifts lower it; above §R50§! the council plots, at §R100§! it strikes and the "
                               "House of Mago falls.")
LOC["CAR_TT_START_COUNCIL"] = ("§YThe Mercenaries' Arrears§! begin at §Y20§!. War and a mercenary army raise them, peace, "
                               "pay and the silver of Iberia lower them; at §R80§! the mercenaries mutiny.")
LOC["CAR_TT_COUP"] = ("§RThe council strikes.§! The House of Mago falls: Carthage takes the road of the Hundred and Four "
                      "(§YThe Hundred and Four§! is completed), the dynasty's own focuses close, and the §YMercenaries' "
                      "Arrears§! begin at §R40§!.")

DYNAMIC = """# Generated by tools/carthage_story.py - Carthage's two meters, shown as national spirits
CAR_suspicion_of_the_council = {
	enable = { always = yes }
	icon = GFX_idea_generic_political_support
	stability_factor = CAR_dm_stab
	political_power_gain = CAR_dm_pp
	army_morale_factor = CAR_dm_morale
}

CAR_mercenaries_arrears = {
	enable = { always = yes }
	icon = GFX_idea_generic_manpower_bonus
	stability_factor = CAR_dm_stab
	army_org_factor = CAR_dm_org
	war_support_factor = CAR_dm_ws
}
"""


def _scale(var, out, mult, add=0.0):
    lines = [f"\tset_variable = {{ {out} = {var} }}", f"\tmultiply_variable = {{ {out} = {mult} }}"]
    if add:
        lines.append(f"\tadd_to_variable = {{ {out} = {add} }}")
    return lines


EFFECTS = "\n".join(
    ["# Generated by tools/carthage_story.py - keep a meter within 0..100 and recompute its national spirit",
     "CAR_suspicion_update = {", "\tclamp_variable = { var = CAR_suspicion min = 0 max = 100 }"]
    + _scale("CAR_suspicion", "CAR_dm_stab", -0.003, 0.05) + _scale("CAR_suspicion", "CAR_dm_pp", -0.004, 0.10)
    + _scale("CAR_suspicion", "CAR_dm_morale", -0.0015, 0.05)
    + ["\tforce_update_dynamic_modifier = yes", "}", "",
       "CAR_arrears_update = {", "\tclamp_variable = { var = CAR_arrears min = 0 max = 100 }"]
    + _scale("CAR_arrears", "CAR_dm_stab", -0.0025, 0.03) + _scale("CAR_arrears", "CAR_dm_org", -0.002, 0.05)
    + _scale("CAR_arrears", "CAR_dm_ws", -0.001, 0.02)
    + ["\tforce_update_dynamic_modifier = yes", "}"]) + "\n"
LOC["CAR_suspicion_of_the_council"] = "Suspicion of the Council ([?CAR_suspicion|Y0])"
LOC["CAR_suspicion_of_the_council_desc"] = ("The elders of Carthage fear a king more than any enemy. Every victory of a "
                                            "Magonid makes them more afraid. Above 50 they plot, at 100 they strike.")
LOC["CAR_mercenaries_arrears"] = "Mercenaries' Arrears ([?CAR_arrears|Y0])"
LOC["CAR_mercenaries_arrears_desc"] = ("Iberians, Gauls, Libyans and Balearic slingers fight for pay - and remember every "
                                       "coin they have not received. At 80 they turn their spears on Carthage.")

# weekly drift and the thresholds (inside the weekly on_action, scope = every country)
WEEKLY = """if = {
	limit = { original_tag = CAR has_country_flag = CAR_dynasty }
	if = {
		limit = { has_war = yes }
		add_to_variable = { CAR_suspicion = 0.25 }
	}
	else = {
		add_to_variable = { CAR_suspicion = -0.15 }
	}
	if = { limit = { has_country_flag = CAR_rule_by_sword } add_to_variable = { CAR_suspicion = 0.10 } }
	if = { limit = { has_country_flag = CAR_bargain } add_to_variable = { CAR_suspicion = -0.10 } }
	CAR_suspicion_update = yes
	if = {
		limit = { check_variable = { CAR_suspicion > 99.9 } NOT = { has_country_flag = CAR_council_coup } }
		country_event = { id = ante_carthage.21 }
	}
	else_if = {
		limit = { check_variable = { CAR_suspicion > 49.9 } NOT = { has_country_flag = CAR_plot_cooldown } }
		random = {
			chance = 4
			set_country_flag = { flag = CAR_plot_cooldown days = 180 value = 1 }
			country_event = { id = ante_carthage.20 }
		}
	}
}
if = {
	limit = { original_tag = CAR has_country_flag = CAR_council }
	if = {
		limit = { has_war = yes }
		add_to_variable = { CAR_arrears = 0.30 }
	}
	else = {
		add_to_variable = { CAR_arrears = -0.15 }
	}
	if = { limit = { has_country_flag = CAR_mercenary_army } add_to_variable = { CAR_arrears = 0.12 } }
	if = { limit = { has_country_flag = CAR_citizen_army } add_to_variable = { CAR_arrears = -0.10 } }
	CAR_arrears_update = yes
	if = {
		limit = { check_variable = { CAR_arrears > 79.9 } NOT = { has_country_flag = CAR_mutiny_cooldown } }
		set_country_flag = { flag = CAR_mutiny_cooldown days = 540 value = 1 }
		country_event = { id = ante_carthage.30 }
	}
	if = {
		limit = { has_country_flag = CAR_court_sits has_war = yes NOT = { has_country_flag = CAR_court_cooldown } }
		random = {
			chance = 3
			set_country_flag = { flag = CAR_court_cooldown days = 365 value = 1 }
			country_event = { id = ante_carthage.31 }
		}
	}
}"""

# ------------------------------------------------------------------ timed spirits of events and decisions
idea("CAR_mutiny_spirit", "The Mercenaries Mutiny", "disjointed_gov",
     army_org_factor=-0.20, stability_factor=-0.15, conscription_factor=-0.30)
idea("CAR_numidian_riders_spirit", "Numidian Riders", "morale_bonus", army_speed_factor=0.10)
idea("CAR_caravan_gold_spirit", "Gold of the Caravans", "economic_increase", industrial_capacity_factory=0.05)
idea("CAR_precinct_sacrifice_spirit", "The Gods Have Been Given Their Due", "morale_bonus",
     army_defence_factor=0.15, war_support_factor=0.15, stability_factor=0.05)
idea("CAR_plague_spirit", "The Plague", "disjointed_gov", monthly_population=-0.30, stability_factor=-0.05)
idea("CAR_crucified_general_spirit", "A General on the Cross", "political_support", stability_factor=0.05,
     army_morale_factor=-0.05)
idea("CAR_triumph_spirit", "The General's Triumph", "morale_bonus", war_support_factor=0.10, army_morale_factor=0.05)
idea("CAR_walls_hold_spirit", "The Walls Must Hold", "fortify_the_borders", army_defence_factor=0.15,
     army_core_defence_factor=0.10)

# ------------------------------------------------------------------ events
EVENTS = []


def event(eid, title, desc, pic, options, trigger="", immediate=""):
    """options: [(text, effect, ai_chance, trigger)]"""
    n = f"ante_carthage.{eid}"
    LOC[f"{n}.t"] = title
    LOC[f"{n}.d"] = desc
    lines = ["country_event = {", f"\tid = {n}", f"\ttitle = {n}.t", f"\tdesc = {n}.d",
             f"\tpicture = GFX_ante_event_{pic}", "\tis_triggered_only = yes"]
    if trigger:
        lines += ["\ttrigger = {", _ind(trigger, 2), "\t}"]
    if immediate:
        lines += ["\timmediate = {", _ind(immediate, 2), "\t}"]
    for i, (text, eff, ai, trig) in enumerate(options):
        key = f"{n}.{'abcde'[i]}"
        LOC[key] = text
        lines += ["\toption = {", f"\t\tname = {key}"]
        if trig:
            lines += ["\t\ttrigger = {", _ind(trig, 3), "\t\t}"]
        lines += [f"\t\tai_chance = {{ factor = {ai} }}"]
        if eff:
            lines.append(_ind(eff, 2))
        lines.append("\t}")
    lines.append("}")
    EVENTS.append("\n".join(lines))


def per_road(mago, council):
    """an effect that differs by road (the right meter for each)"""
    out = []
    if mago:
        out.append(f"if = {{ limit = {{ {MAGO} }}\n{_ind(mago, 1)}\n}}")
    if council:
        out.append(f"if = {{ limit = {{ {COUNCIL} }}\n{_ind(council, 1)}\n}}")
    return "\n".join(out)


# --- both roads
event(1, "Malchus at the Gates",
      "Malchus, the general who conquered half of Sicily and lost Sardinia, was sent into exile. Now his army stands "
      "before Carthage and he demands to come home - as master. His own son came out to meet him dressed as a priest; "
      "Malchus had him crucified.",
      "war",
      [("Open the gates - then put him on trial.", "add_stability = 0.05\n" + per_road(suspicion(-8), arrears(-5)), 60, ""),
       ("Let him rule the army. Carthage needs generals.", "army_experience = 25\nadd_war_support = 0.05\n"
        + per_road(suspicion(10), arrears(5)), 40, "")])
event(2, "Hanno Returns",
      "Hanno is back from the ocean coast of Africa: new cities founded, a burning mountain seen from the sea, and the "
      "skins of three 'gorillas' hung in the temple of Tanit.",
      "vote",
      [("Hang the skins in the temple for all to see.", "add_stability = 0.05\narmy_experience = 5", 50, ""),
       ("Keep the route secret: the ocean is ours.", "add_political_power = 75", 50, "")])
event(3, "Himilco Returns",
      "Four months north along the ocean, past seas of weed and fog, Himilco has found the islands of tin. No Greek "
      "will ever learn the way.",
      "vote",
      [("The tin trade is Carthage's alone.", "add_political_power = 50\n" + per_road(suspicion(-5), arrears(-5)), 100, "")])
event(4, "The News from Himera",
      "The army of Hamilcar is destroyed before Himera. They say the general watched the battle from the altar, "
      "throwing whole victims into the fire, and at the end threw himself in.",
      "fire",
      [("Honour him: he gave himself to the gods.", "add_war_support = 0.10\nadd_stability = -0.05", 50, ""),
       ("Blame him: his house has led us to ruin.", "add_stability = 0.03\n" + per_road(suspicion(15), arrears(-10)), 50, "")])
event(5, "The Plague",
      "396 BC: a plague breaks out in the army before Syracuse and spreads to Africa. The Libyans rise, and the city "
      "believes that Demeter and Kore, whose temple was plundered in Sicily, are taking their revenge.",
      "crowd",
      [("Bring the goddesses to Carthage, with Greek priests.", "add_timed_idea = { idea = CAR_plague_spirit days = 120 }\n"
        "add_stability = 0.03", 60, ""),
       ("Pray to Eshmun and wait.", "add_timed_idea = { idea = CAR_plague_spirit days = 270 }", 40, "")],
      trigger="NOT = { has_completed_focus = CAR_demeter_and_kore }")
event(6, "Agathocles in Africa",
      "310 BC: the tyrant of Syracuse has slipped past our fleet, landed at Cape Bon and burnt his ships behind him. "
      "His army ravages the estates of the Bagradas.",
      "war",
      [("Every man to the walls!", "add_timed_idea = { idea = CAR_walls_hold_spirit days = 365 }\nadd_manpower = 3000", 70, ""),
       ("Buy him off.", "add_political_power = -100\nadd_stability = 0.05", 30, "")])
event(7, "Messana Calls",
      "The Mamertines of Messana, beset by Syracuse, ask for a Punic garrison. Rome has been asked too.",
      "senate",
      [("Send the garrison - the strait is ours.", "add_war_support = 0.05\nnavy_experience = 15", 70, ""),
       ("Messana is not worth a war with Rome.", "add_stability = 0.05\nadd_political_power = 50", 30, "")])
# --- the House of Mago
event(20, "Whispers in the Council",
      "Elders meet at night in each other's houses. They speak of Malchus, of kings, of what Tyre did to its kings.",
      "conspiracy",
      [("Arrest the ringleaders.", suspicion(-15) + "\nadd_stability = -0.05", 50, ""),
       ("Send gifts and marriage offers.", "add_political_power = -50\n" + suspicion(-10), 40, ""),
       ("Let them whisper.", suspicion(5), 10, "")])
event(21, "The Council Strikes",
      "The elders have called the citizens to the assembly; the Sacred Band has taken their side. The House of Mago "
      "is finished: Carthage will be ruled by the Hundred and Four.",
      "fire",
      [("So it ends.", "custom_effect_tooltip = CAR_TT_COUP\nhidden_effect = {\n" + _ind(COUP, 1) + "\n}", 100, "")])
# --- the Hundred and Four
event(30, "The Mercenaries Mutiny",
      "Unpaid for months, the mercenaries have seized their camp and the Libyan towns are joining them. They demand "
      "their pay - all of it, now.",
      "war",
      [("Pay them, whatever it costs.", "add_political_power = -150\n" + arrears(-50), 50, ""),
       ("Crush them.", "add_timed_idea = { idea = CAR_mutiny_spirit days = 365 }\narmy_experience = 20\n" + arrears(-40), 50, "")])
event(31, "A General before the Court",
      "The Hundred and Four have summoned a general who lost a battle. The city waits for the verdict.",
      "senate",
      [("Crucify him: let every general fear defeat more than the enemy.",
        "add_timed_idea = { idea = CAR_crucified_general_spirit days = 365 }\n" + arrears(-5), 60, ""),
       ("Acquit him: we need every commander.", "add_political_power = -50\narmy_experience = 10", 40, "")])
event(32, "The Coup of Hanno",
      "Hanno, the richest man in Carthage, has armed twenty thousand slaves and plans to poison the senate at his "
      "daughter's wedding.",
      "conspiracy",
      [("Seize him before the wedding.", "add_stability = 0.05\nadd_political_power = 50", 70, ""),
       ("Buy his followers.", "add_political_power = -75\nadd_stability = 0.03", 30, "")])


# ------------------------------------------------------------------ decisions (category Res Punica)
DECISIONS = []


def decision(key, name, desc, icon, visible, available, cost, effect, ai, days_re_enable=0, days_remove=0,
             remove_effect=""):
    LOC[key] = name
    LOC[f"{key}_desc"] = desc
    lines = [f"\t{key} = {{", f"\t\ticon = {icon}", "\t\tallowed = { original_tag = CAR }",
             "\t\tvisible = {", _ind(visible, 3), "\t\t}"]
    if available:
        lines += ["\t\tavailable = {", _ind(available, 3), "\t\t}"]
    lines.append(f"\t\tcost = {cost}")
    if days_re_enable:
        lines.append(f"\t\tdays_re_enable = {days_re_enable}")
    if days_remove:
        lines.append(f"\t\tdays_remove = {days_remove}")
    lines += ["\t\tcomplete_effect = {", _ind(effect, 3), "\t\t}"]
    if remove_effect:
        lines += ["\t\tremove_effect = {", _ind(remove_effect, 3), "\t\t}"]
    lines += ["\t\tai_will_do = {", _ind(ai, 3), "\t\t}", "\t}"]
    DECISIONS.append("\n".join(lines))


EITHER = f"OR = {{ {MAGO} {COUNCIL} }}"
MERC = per_road("", arrears(6))
# both roads: hire mercenaries (the Council pays for it in arrears)
decision("CAR_hire_iberians", "Hire Iberian Mercenaries",
         "Short swords and the falcata: the warriors of the Iberian hills fight for silver. (Council: +6 arrears.)",
         "GFX_decision_generic_military", EITHER, "", 50, "add_manpower = 3000\narmy_experience = 5\n" + MERC,
         "base = 0\nmodifier = { add = 3 has_war = yes }", days_re_enable=180)
decision("CAR_hire_balearic_slingers", "Hire Balearic Slingers",
         "The islanders learn the sling as boys: their bread is set on a post and they eat only what they hit. "
         "(Council: +6 arrears.)",
         "GFX_decision_generic_military", EITHER, "", 40, "add_manpower = 1500\narmy_experience = 10\n" + MERC,
         "base = 0\nmodifier = { add = 2 has_war = yes }", days_re_enable=180)
decision("CAR_hire_gauls", "Hire Gallic Warriors",
         "Big men with long swords and terrible tempers - brave in the charge and quick to riot. (Council: +6 arrears.)",
         "GFX_decision_generic_military", EITHER, "", 60, "add_manpower = 4000\nadd_war_support = -0.02\n" + MERC,
         "base = 0\nmodifier = { add = 2 has_war = yes }", days_re_enable=240)
decision("CAR_numidian_riders", "Call the Numidian Riders",
         "Our Numidian friends send their light horsemen, who ride without bridles.",
         "GFX_decision_generic_military", EITHER, "has_completed_focus = CAR_numidian_alliance", 50,
         "add_manpower = 2000\nadd_timed_idea = { idea = CAR_numidian_riders_spirit days = 180 }",
         "base = 0\nmodifier = { add = 3 has_war = yes }", days_re_enable=240)
decision("CAR_silver_from_iberia", "Silver from Iberia",
         "A convoy of silver ingots from the mines of the Sierra Morena. (Council: -15 arrears.)",
         "GFX_decision_generic_trade", EITHER, "has_completed_focus = CAR_iberia", 25,
         "add_political_power = 75\n" + per_road("", arrears(-15)), "base = 2", days_re_enable=365)
decision("CAR_caravan", "Caravan to the Garamantes",
         "Salt and Punic cloth south across the desert; gold, ivory and carbuncles back north.",
         "GFX_decision_generic_trade", EITHER, "has_completed_focus = CAR_saharan_caravans", 50,
         "add_timed_idea = { idea = CAR_caravan_gold_spirit days = 365 }", "base = 2", days_re_enable=400)
decision("CAR_precinct_sacrifice", "Sacrifice in the Precinct",
         "When the enemy is at the gates, the great families give the gods their own children. Only in the hour of "
         "greatest danger.",
         "GFX_decision_generic_prepare_civil_war", EITHER, "has_war = yes\nsurrender_progress > 0.1", 50,
         "add_timed_idea = { idea = CAR_precinct_sacrifice_spirit days = 180 }\nadd_stability = -0.05",
         "base = 0\nmodifier = { add = 5 surrender_progress > 0.2 }", days_re_enable=720)
# the House of Mago
decision("CAR_gifts_to_the_council", "Mago: Gifts to the Council",
         f"{ROAD_MAGO}. Estates, offices and daughters for the great houses: suspicion sleeps on full stomachs.",
         "GFX_decision_generic_political_discourse", MAGO, "", 75, suspicion(-15),
         "base = 0\nmodifier = { add = 5 check_variable = { CAR_suspicion > 45 } }", days_re_enable=240)
decision("CAR_triumph", "Mago: A Triumph for the General",
         f"{ROAD_MAGO}. Parade the spoils through the streets: the people love victors - the elders less so.",
         "GFX_decision_generic_military", MAGO, "has_war = no", 25,
         "add_timed_idea = { idea = CAR_triumph_spirit days = 180 }\n" + suspicion(10),
         "base = 0\nmodifier = { add = 2 check_variable = { CAR_suspicion < 30 } }", days_re_enable=365)
# the Hundred and Four
decision("CAR_pay_the_mercenaries", "Council: Pay the Mercenaries",
         f"{ROAD_COUNCIL}. Open the treasury and pay what is owed - before the soldiers come to take it.",
         "GFX_decision_generic_civil_support", COUNCIL, "", 75, arrears(-20),
         "base = 0\nmodifier = { add = 5 check_variable = { CAR_arrears > 50 } }", days_re_enable=180)
decision("CAR_disband_mercenaries", "Council: Send the Mercenaries Home",
         f"{ROAD_COUNCIL}. In peace the city needs no hired swords: pay them off and ship them home.",
         "GFX_decision_generic_civil_support", COUNCIL, "has_war = no", 25, "add_manpower = -3000\n" + arrears(-25),
         "base = 0\nmodifier = { add = 3 check_variable = { CAR_arrears > 40 } }", days_re_enable=365)

LOC["CAR_res_punica"] = "Res Punica"
LOC["CAR_res_punica_desc"] = "[Root.GetCARResPunica]"
LOC["CAR_res_punica_state_mago"] = (f"{ROAD_MAGO}: the Suspicion of the Council stands at §Y[?CAR_suspicion|0]§! of 100. "
                                    "War and the rule of the sword raise it; peace and gifts lower it. Above §R50§! the "
                                    "council plots, at §R100§! the House of Mago falls.")
LOC["CAR_res_punica_state_council"] = (f"{ROAD_COUNCIL}: the Mercenaries' Arrears stand at §Y[?CAR_arrears|0]§! of 100. "
                                       "War and a mercenary army raise them; peace, pay and the silver of Iberia lower "
                                       "them. At §R80§! the mercenaries mutiny.")
CATEGORY = """# Generated by tools/carthage_story.py
CAR_res_punica = {
	icon = generic_political_actions
	allowed = { original_tag = CAR }
	visible = { OR = { has_country_flag = CAR_dynasty has_country_flag = CAR_council } }
	priority = 100
}
"""
SCRIPTED_LOC = """# Generated by tools/carthage_story.py - the text of Carthage's decision category follows the road taken
defined_text = {
	name = GetCARResPunica
	text = { trigger = { has_country_flag = CAR_dynasty } localization_key = CAR_res_punica_state_mago }
	text = { localization_key = CAR_res_punica_state_council }
}
"""


def write_all():
    def write(rel, text):
        p = MOD / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")

    write("common/dynamic_modifiers/CAR_dynamic_modifiers.txt", DYNAMIC)
    write("common/scripted_effects/CAR_scripted_effects.txt", EFFECTS)
    write("common/scripted_localisation/CAR_scripted_localisation.txt", SCRIPTED_LOC)
    write("events/CAR_events.txt", "# Generated by tools/carthage_story.py\nadd_namespace = ante_carthage\n\n"
          + "\n\n".join(EVENTS) + "\n")
    write("common/decisions/CAR_decisions.txt", "# Generated by tools/carthage_story.py\nCAR_res_punica = {\n"
          + "\n\n".join(DECISIONS) + "\n}\n")
    write("common/decisions/categories/CAR_categories.txt", CATEGORY)
    return len(EVENTS), len(DECISIONS)
