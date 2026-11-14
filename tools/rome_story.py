"""Rome's story systems: two meters, events, decisions and event pictures (used by tools/content.py).

The focus tree (tools/national_trees.py) decides WHAT Rome becomes; this file makes the road there uneven.

  The Republic - ROM_discord (0-100), "the Struggle of the Orders": patricians against plebeians.
      Starts at 40 with the Regifugium. Every week of war adds to it (the soldiers' farms fall into debt),
      every week of peace takes a little away. Patrician choices raise it, concessions lower it.
      Its national spirit scales with it: from +10 % stability and +0.2 political power a day at 0
      to -20 % stability, -0.3 political power, -10 % war support and -20 % recruits at 100.
      At 80 the plebs march out of the city (event ante_rome.20). Lex Hortensia needs it at 30 or below.
  The Kingdom - ROM_hatred (0-100), "the People Hate the King".
      Starts at 70 with The King Remains. Tyranny pushes it up every week, a king for the people pulls it
      down, losing a war pushes it up hard. Its spirit scales with it (at 70: -21 % stability, -0.28 political
      power, -28 % population growth, -21 % recruits ...). Above 50 conspiracies hatch (ante_rome.40);
      at 100 Rome rises against the king (ante_rome.45; Brutus already at 80 if he was kept at court): a civil
      war once Rome holds 3+ states, before that a revolution - the king flees and Rome becomes the Republic
      after all. A Loyal Rome needs it below 30.

Writes (content.py calls write_all):
  common/dynamic_modifiers/ROM_dynamic_modifiers.txt, common/scripted_effects/ROM_scripted_effects.txt,
  events/ROM_events.txt, common/decisions/ROM_decisions.txt, common/decisions/categories/ROM_categories.txt,
  gfx/event_pictures/ante_rome_*.dds + interface/ante_events.gfx
and returns: IDEAS (timed spirits), LOC, WEEKLY (lines for the weekly on_action), helper effects for the tree.
Syntax checked against the game's own files and documentation (1.19.5, 2026-11-14).
"""
import math
import re
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

MOD = Path(__file__).resolve().parent.parent
LOC = {}
IDEAS = {}          # key -> (name, picture, modifiers)   - written by content.py like every other spirit


def idea(key, name, pic, **mods):
    IDEAS[key] = (name, "generic_" + pic, mods)


# ------------------------------------------------------------------ meters
def _meter(var, n, name, good_when_down=True):
    """effect lines: change a meter by n, with a readable tooltip"""
    sign = "+" if n > 0 else ""
    bad = (n > 0) == good_when_down
    key = f"ROM_TT_{var.upper()}_{'P' if n > 0 else 'M'}{abs(n)}"
    LOC[key] = f"{name}: {'§R' if bad else '§G'}{sign}{n}§!"
    return (f"custom_effect_tooltip = {key}\n"
            f"hidden_effect = {{ add_to_variable = {{ {var} = {n} }} {var}_update = yes }}")


def discord(n):
    return _meter("ROM_discord", n, "Struggle of the Orders")


def hatred(n):
    return _meter("ROM_hatred", n, "Hatred of the King")


def discord_below(n):
    LOC[f"ROM_TT_DISCORD_BELOW_{n}"] = f"Struggle of the Orders is at most {n} (now: [?ROM_discord|Y0])"
    return (f"custom_trigger_tooltip = {{ tooltip = ROM_TT_DISCORD_BELOW_{n} "
            f"check_variable = {{ ROM_discord < {n + 0.01} }} }}")


def discord_above(n):
    LOC[f"ROM_TT_DISCORD_ABOVE_{n}"] = f"Struggle of the Orders is at least {n} (now: [?ROM_discord|Y0])"
    return (f"custom_trigger_tooltip = {{ tooltip = ROM_TT_DISCORD_ABOVE_{n} "
            f"check_variable = {{ ROM_discord > {n - 0.01} }} }}")


def hatred_below(n):
    LOC[f"ROM_TT_HATRED_BELOW_{n}"] = f"Hatred of the King is below {n} (now: [?ROM_hatred|Y0])"
    return (f"custom_trigger_tooltip = {{ tooltip = ROM_TT_HATRED_BELOW_{n} "
            f"check_variable = {{ ROM_hatred < {n} }} }}")


# start of each road (focus rewards in national_trees.py)
START_REPUBLIC = """set_country_flag = ROM_republic
set_variable = { ROM_discord = 40 }
ROM_discord_update = yes
add_dynamic_modifier = { modifier = ROM_struggle_of_the_orders }
custom_effect_tooltip = ROM_TT_START_REPUBLIC
country_event = { id = ante_rome.1 days = 25 }
country_event = { id = ante_rome.10 days = 300 }"""
START_KINGDOM = """set_country_flag = ROM_kingdom
set_variable = { ROM_hatred = 70 }
ROM_hatred_update = yes
add_dynamic_modifier = { modifier = ROM_hatred_of_the_king }
custom_effect_tooltip = ROM_TT_START_KINGDOM
country_event = { id = ante_rome.42 days = 60 }
country_event = { id = ante_rome.44 days = 200 }"""
END_HATRED = """set_country_flag = ROM_loyal
clr_country_flag = ROM_kingdom
remove_dynamic_modifier = { modifier = ROM_hatred_of_the_king }
set_variable = { ROM_hatred = 0 }"""
# The uprising: a civil war needs land to split - Rome starts with ONE state, and start_civil_war then does
# nothing at all (tested 2026-11-14). A small Rome therefore drives the king out: the Regifugium happens
# after all (complete_national_focus works on the mutually exclusive root, tested), but in blood - the
# Struggle of the Orders starts at 55, not 40. The king's own focuses close (national_trees.py).
BIG_ENOUGH = "num_of_controlled_states > 2"
REVOLUTION = """set_country_flag = ROM_revolution
clr_country_flag = ROM_kingdom
remove_dynamic_modifier = { modifier = ROM_hatred_of_the_king }
set_variable = { ROM_hatred = 0 }
if = { limit = { has_idea = ROM_rex_tarquinius_spirit } remove_ideas = ROM_rex_tarquinius_spirit }
if = { limit = { has_idea = ROM_tyranny_spirit } remove_ideas = ROM_tyranny_spirit }
if = { limit = { has_idea = ROM_good_king_spirit } remove_ideas = ROM_good_king_spirit }
set_politics = { ruling_party = democratic elections_allowed = yes }
set_popularities = { democratic = 85 fascism = 0 communism = 0 neutrality = 15 }
retire_character = ROM_tarquinius
add_stability = -0.10
complete_national_focus = ROM_regifugium
set_variable = { ROM_discord = 55 }
ROM_discord_update = yes"""
LOC["ROM_TT_REVOLUTION"] = ("§RThe king is driven out.§! Rome becomes a Republic after all (§YRegifugium§! is completed), "
                            "the king's own focuses close, and the §YStruggle of the Orders§! begins at §R55§!.")
LOC["ROM_TT_START_REPUBLIC"] = ("§YThe Struggle of the Orders§! begins at §Y40§!. War drives it up, peace and concessions "
                                "bring it down; at §R80§! the plebs leave the city.")
LOC["ROM_TT_START_KINGDOM"] = ("§YThe Hatred of the King§! begins at §R70§!. Tyranny and defeats drive it up, the king's "
                               "favours bring it down; above §R50§! conspiracies hatch, at §R100§! Rome rises.")

DYNAMIC = """# Generated by tools/rome_story.py - Rome's two meters, shown as national spirits
ROM_struggle_of_the_orders = {
	enable = { always = yes }
	icon = GFX_idea_generic_political_support
	stability_factor = ROM_dm_stab
	political_power_gain = ROM_dm_pp
	war_support_factor = ROM_dm_ws
	conscription_factor = ROM_dm_cons
}

ROM_hatred_of_the_king = {
	enable = { always = yes }
	icon = GFX_idea_generic_disjointed_gov
	stability_factor = ROM_dm_stab
	political_power_gain = ROM_dm_pp
	war_support_factor = ROM_dm_ws
	conscription_factor = ROM_dm_cons
	monthly_population = ROM_dm_pop
	production_speed_buildings_factor = ROM_dm_build
}
"""


def _scale(var, out, mult, add=0.0):
    lines = [f"\tset_variable = {{ {out} = {var} }}", f"\tmultiply_variable = {{ {out} = {mult} }}"]
    if add:
        lines.append(f"\tadd_to_variable = {{ {out} = {add} }}")
    return lines


EFFECTS = "\n".join(
    ["# Generated by tools/rome_story.py - keep a meter within 0..100 and recompute its national spirit",
     "ROM_discord_update = {", "\tclamp_variable = { var = ROM_discord min = 0 max = 100 }"]
    + _scale("ROM_discord", "ROM_dm_stab", -0.003, 0.10) + _scale("ROM_discord", "ROM_dm_pp", -0.005, 0.20)
    + _scale("ROM_discord", "ROM_dm_ws", -0.0015, 0.05) + _scale("ROM_discord", "ROM_dm_cons", -0.003, 0.10)
    + ["\tforce_update_dynamic_modifier = yes", "}", "",
       "ROM_hatred_update = {", "\tclamp_variable = { var = ROM_hatred min = 0 max = 100 }"]
    + _scale("ROM_hatred", "ROM_dm_stab", -0.003) + _scale("ROM_hatred", "ROM_dm_pp", -0.004)
    + _scale("ROM_hatred", "ROM_dm_ws", -0.002) + _scale("ROM_hatred", "ROM_dm_cons", -0.003)
    + _scale("ROM_hatred", "ROM_dm_pop", -0.004) + _scale("ROM_hatred", "ROM_dm_build", -0.003)
    + ["\tforce_update_dynamic_modifier = yes", "}"]) + "\n"
LOC["ROM_struggle_of_the_orders"] = "Struggle of the Orders ([?ROM_discord|Y0])"
LOC["ROM_struggle_of_the_orders_desc"] = ("Patricians against plebeians: debts, land and the right to rule. The higher the "
                                          "discord, the weaker the Republic. War raises it week by week, peace and "
                                          "concessions lower it; at 80 the plebs leave the city.")
LOC["ROM_hatred_of_the_king"] = "The People Hate the King ([?ROM_hatred|Y0])"
LOC["ROM_hatred_of_the_king_desc"] = ("Rome remembers the Republic it nearly had. Families flee, fields lie empty and men "
                                      "whisper in the Forum. Above 50 they plot, at 100 they rise.")

# weekly drift and the thresholds (inside the weekly on_action, scope = every country)
WEEKLY = """if = {
	limit = { original_tag = ROM has_country_flag = ROM_republic NOT = { has_country_flag = ROM_concord } }
	if = {
		limit = { has_war = yes }
		add_to_variable = { ROM_discord = 0.35 }
	}
	else = {
		add_to_variable = { ROM_discord = -0.12 }
	}
	if = { limit = { has_country_flag = ROM_fathers_rule } add_to_variable = { ROM_discord = 0.12 } }
	if = { limit = { has_country_flag = ROM_tribunes } add_to_variable = { ROM_discord = -0.12 } }
	if = { limit = { has_country_flag = ROM_blood_in_the_forum } add_to_variable = { ROM_discord = 0.06 } }
	ROM_discord_update = yes
	if = {
		limit = { check_variable = { ROM_discord > 79.9 } NOT = { has_country_flag = ROM_secession_cooldown } }
		set_country_flag = { flag = ROM_secession_cooldown days = 540 value = 1 }
		country_event = { id = ante_rome.20 }
	}
}
if = {
	limit = { original_tag = ROM has_country_flag = ROM_kingdom }
	if = { limit = { has_country_flag = ROM_tyranny } add_to_variable = { ROM_hatred = 0.25 } }
	if = { limit = { has_country_flag = ROM_good_king } add_to_variable = { ROM_hatred = -0.12 } }
	if = { limit = { has_country_flag = ROM_king_listens } add_to_variable = { ROM_hatred = -0.1 } }
	if = { limit = { surrender_progress > 0.1 } add_to_variable = { ROM_hatred = 0.6 } }
	ROM_hatred_update = yes
	if = {
		limit = { check_variable = { ROM_hatred > 99.9 } NOT = { has_country_flag = ROM_rising_done } }
		set_country_flag = ROM_rising_done
		country_event = { id = ante_rome.45 }
	}
	else_if = {
		limit = { has_country_flag = ROM_brutus_at_court check_variable = { ROM_hatred > 79.9 } NOT = { has_country_flag = ROM_brutus_done } }
		set_country_flag = ROM_brutus_done
		country_event = { id = ante_rome.43 }
	}
	else_if = {
		limit = { check_variable = { ROM_hatred > 49.9 } NOT = { has_country_flag = ROM_plot_cooldown } }
		random = {
			chance = 4
			set_country_flag = { flag = ROM_plot_cooldown days = 150 value = 1 }
			country_event = { id = ante_rome.40 }
		}
		if = {
			limit = { has_country_flag = ROM_blood_in_the_forum NOT = { has_country_flag = ROM_plot_cooldown } }
			random = {
				chance = 4
				set_country_flag = { flag = ROM_plot_cooldown days = 150 value = 1 }
				country_event = { id = ante_rome.40 }
			}
		}
	}
}"""

# ------------------------------------------------------------------ timed spirits of events and decisions
idea("ROM_porsenna_terms_spirit", "The Peace of Porsenna", "political_support",
     army_attack_factor=-0.15, stability_factor=0.05)
idea("ROM_defend_the_city_spirit", "Every Man to the Walls", "fortify_the_borders",
     army_defence_factor=0.15, army_core_defence_factor=0.10, war_support_factor=0.10)
idea("ROM_dioscuri_spirit", "Castor and Pollux Ride with Us", "morale_bonus", army_attack_factor=0.10, army_morale_factor=0.10)
idea("ROM_patrician_consuls_spirit", "Patrician Consuls", "political_support", army_org_factor=0.05, political_power_gain=0.10)
idea("ROM_popular_consuls_spirit", "Consuls of the People", "pp_unity_bonus", stability_factor=0.05, conscription_factor=0.05)
idea("ROM_military_tribunes_spirit", "Military Tribunes with Consular Power", "morale_bonus",
     army_attack_factor=0.05, army_defence_factor=0.05)
idea("ROM_secession_spirit", "The Plebs on the Sacred Mount", "disjointed_gov",
     conscription_factor=-0.50, production_speed_buildings_factor=-0.30, stability_factor=-0.10)
idea("ROM_dictator_spirit", "Dictator Rei Gerundae Causa", "morale_bonus",
     army_attack_factor=0.10, army_defence_factor=0.10, army_org_factor=0.10, political_power_gain=0.30)
idea("ROM_the_king_wounded_spirit", "The King Lies Wounded", "disjointed_gov", political_power_gain=-0.30, stability_factor=-0.05)
idea("ROM_terror_spirit", "Spies in Every House", "political_support", stability_factor=0.05, political_power_gain=-0.10)
idea("ROM_bread_and_games_spirit", "The King's Games", "pp_unity_bonus", stability_factor=0.05)
idea("ROM_debt_relief_spirit", "Debts Forgiven", "pp_unity_bonus", stability_factor=0.03, war_support_factor=-0.03)

# ------------------------------------------------------------------ events
EVENTS = []


def event(eid, title, desc, pic, options, trigger="", immediate=""):
    """options: [(text, effect, ai_chance, trigger)]"""
    n = f"ante_rome.{eid}"
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


def _ind(text, tabs):
    pad = "\t" * tabs
    return "\n".join(pad + l if l.strip() else l for l in text.splitlines())


REVOLT_FX = "custom_effect_tooltip = ROM_TT_REVOLUTION\nhidden_effect = {\n" + _ind(REVOLUTION, 1) + "\n}"
CLU_FREE = "country_exists = CLU CLU = { is_subject = no } NOT = { has_war_with = CLU }"

# --- the Republic
event(1, "The Tarquins in Exile",
      "The last king and his sons have fled to Caere and from there to Clusium. Their palace, their herds and the "
      "fields by the Tiber stand empty. The plebs say: the land of the tyrant belongs to those who drove him out. "
      "The fathers say: the treasury of the Republic is empty.",
      "senate",
      [("Give the king's land to the people.", discord(-10) + "\nadd_political_power = -25", 50, ""),
       ("Sell it for the treasury of the Republic.", discord(10) + "\nadd_political_power = 75", 50, "")],
      immediate="country_event = { id = ante_rome.2 days = 150 random_days = 60 }")
event(2, "Porsenna Marches on Rome",
      "Lars Porsenna, king of Clusium and the greatest lord of Etruria, has taken up the cause of the Tarquins. "
      "His army is camped on the Janiculum; his envoys offer peace: hostages, the land across the Tiber - and "
      "iron only for the plough.",
      "war",
      [("Every man to the walls!",
        "set_country_flag = ROM_porsenna_done\nset_country_flag = { flag = ROM_porsenna_war days = 365 value = 1 }\n"
        "add_timed_idea = { idea = ROM_defend_the_city_spirit days = 365 }\n"
        "add_war_support = 0.05\n"
        # round 27 (Peti): Clusium declared war without a common border - a war nobody could fight or end.
        # Now only a neighbour marches; otherwise Porsenna's threat ends without a war (Mucius Scaevola).
        "if = { limit = { CLU = { is_neighbor_of = ROM } }\n"
        "\tCLU = { declare_war_on = { target = ROM type = puppet_wargoal_focus } }\n"
        "}\nelse = {\n\tcustom_effect_tooltip = ROM_TT_PORSENNA_WITHDRAWS\n\tclr_country_flag = ROM_porsenna_war\n"
        "\tarmy_experience = 10\n}",
        60, CLU_FREE),
       ("Accept his terms. Rome must survive to fight another day.",
        "set_country_flag = ROM_porsenna_done\nset_country_flag = ROM_porsenna_peace\n"
        "add_timed_idea = { idea = ROM_porsenna_terms_spirit days = 540 }\nadd_political_power = -50\n" + discord(-5),
        40, CLU_FREE),
       ("Porsenna has troubles of his own. The danger passes.", "set_country_flag = ROM_porsenna_done", 1,
        f"NOT = {{ {CLU_FREE} }}")])
event(10, "The Consular Elections",
      "On the Field of Mars the centuries vote, the richest first. Who will hold the fasces this year?",
      "vote",
      [("Two men of the old patrician houses.",
        "add_timed_idea = { idea = ROM_patrician_consuls_spirit days = 365 }\narmy_experience = 5\n" + discord(5), 40, ""),
       ("Men the plebs trust - like Valerius, the friend of the people.",
        "add_timed_idea = { idea = ROM_popular_consuls_spirit days = 365 }\n" + discord(-5), 40,
        "OR = { has_completed_focus = ROM_tribunes_of_the_plebs has_completed_focus = ROM_licinian_sextian_laws "
        "check_variable = { ROM_discord > 49.9 } }"),
       ("War on every side: elect military tribunes with consular power.",
        "add_timed_idea = { idea = ROM_military_tribunes_spirit days = 365 }\n" + discord(2), 60, "has_war = yes")],
      trigger="has_country_flag = ROM_republic",
      immediate="country_event = { id = ante_rome.10 days = 365 }")
event(20, "Secession of the Plebs",
      "The plebeians have left the city. Unarmed and silent they sit on the Sacred Mount beyond the Anio. No one "
      "ploughs, no one forges, no one answers the call to arms. Without the plebs there is no Rome - and they know it.",
      "crowd",
      [("Send Menenius Agrippa with the fable of the belly - and give way.",
        "add_political_power = -100\nset_country_flag = ROM_seceded\nset_country_flag = ROM_gave_way\n" + discord(-35), 60, ""),
       ("Wait. Hunger will bring them back.",
        "add_timed_idea = { idea = ROM_secession_spirit days = 120 }\nadd_stability = -0.05\nset_country_flag = ROM_seceded\n"
        + discord(-15), 30, ""),
       ("The legions will bring them back.",
        "add_stability = -0.15\nadd_war_support = -0.10\nadd_manpower = -1500\nset_country_flag = ROM_seceded\n"
        "set_country_flag = ROM_blood_in_the_forum\n" + discord(-45), 10,
        "OR = { has_country_flag = ROM_fathers_rule has_idea = ROM_dictator_spirit }")],
      immediate="add_timed_idea = { idea = ROM_secession_spirit days = 30 }")
event(25, "The Law of Spurius Cassius",
      "Spurius Cassius, three times consul and maker of the treaty with the Latins, proposes to share the public "
      "land among plebeians and Latins. The fathers whisper that he wants to be king.",
      "senate",
      [("Pass the land law.", "add_political_power = -50\n" + discord(-15), 50, ""),
       ("Accuse him of aiming at the crown. Hurl him from the Tarpeian Rock.",
        "add_political_power = 50\nadd_stability = 0.05\n" + discord(10), 50, "")],
      trigger="has_country_flag = ROM_republic")
event(30, "Lay Down the Fasces?",
      "The danger is past. The dictator's six months are over, and the law says he must lay down his power.",
      "senate",
      [("Like Cincinnatus, he returns to his plough.", "add_stability = 0.10\nadd_political_power = 50\n" + discord(-5), 70, ""),
       ("Rome still needs him. He stays.",
        "add_timed_idea = { idea = ROM_dictator_spirit days = 180 }\nadd_stability = -0.05\n" + discord(20), 30, "has_war = yes")])

# --- the Kingdom
event(40, "A Conspiracy Discovered",
      "A slave has talked. Young men of good families met at night and swore an oath over the blood of a man: "
      "the king must die. Their names are on a wax tablet before Tarquinius.",
      "conspiracy",
      [("Scourge and behead them in the Forum.", "add_political_power = 25\nadd_stability = 0.03\n" + hatred(6), 40, ""),
       ("Exile them and seize their estates.", "add_political_power = 50\n" + hatred(2), 35, ""),
       ("Pardon them before the people.",
        "add_political_power = -50\nset_country_flag = ROM_pardoned_plotters\n" + hatred(-8)
        + "\nrandom = { chance = 30 country_event = { id = ante_rome.41 days = 120 random_days = 120 } }", 25, "")],
      trigger="has_country_flag = ROM_kingdom")
event(41, "Daggers in the Forum",
      "Some of the pardoned were not grateful. As the king walked to the Comitium, three men drew daggers. "
      "Tarquinius lives - barely.",
      "conspiracy",
      [("The Celeres take bloody revenge.", "add_timed_idea = { idea = ROM_the_king_wounded_spirit days = 90 }\nadd_war_support = 0.05\n"
        + hatred(10), 50, ""),
       ("From his bed, the king forgives again.", "add_timed_idea = { idea = ROM_the_king_wounded_spirit days = 180 }\n"
        + hatred(-12), 50, "")],
      trigger="has_country_flag = ROM_kingdom")
event(42, "Brutus the Fool",
      "Lucius Junius, the king's nephew, plays the idiot so well that men call him Brutus - the dullard. The king "
      "keeps him at court for amusement. Only the queen does not laugh.",
      "king",
      [("Keep the fool at court. He is harmless.", "set_country_flag = ROM_brutus_at_court\nadd_political_power = 25", 50, ""),
       ("Send him to the Latins, out of sight.",
        "add_political_power = -25\nif = { limit = { country_exists = LAT } LAT = { add_war_support = 0.10 } }", 30, ""),
       ("A quiet death. A fool has no friends.", "add_political_power = 50\nretire_character = ROM_brutus\n" + hatred(10), 20, "")],
      trigger="has_country_flag = ROM_kingdom")
event(43, "Brutus Throws Off His Mask",
      "The fool is no fool. Lucius Junius Brutus stands on the rostra and calls the people of Rome to arms against "
      "the tyrant. Half the city follows him.",
      "fire",
      [("Then let it be war.", "start_civil_war = { ideology = democratic size = 0.35 }\n"
        "set_variable = { ROM_hatred = 45 }\nROM_hatred_update = yes", 100, BIG_ENOUGH),
       ("The gates are shut against us. The king rides for Caere.", REVOLT_FX, 100, "NOT = { " + BIG_ENOUGH + " }")],
      trigger="has_country_flag = ROM_kingdom")
event(44, "Lucretia",
      "Sextus, the king's son, has dishonoured Lucretia, wife of Collatinus. She has told her father and her "
      "husband - and taken her own life before them. The city is in uproar.",
      "king",
      [("The king's son is above the law.", "add_political_power = 50\n" + hatred(18), 30, ""),
       ("Banish Sextus. Even a king's son answers for this.", "add_political_power = -75\nadd_stability = -0.03\n" + hatred(-12), 50, ""),
       ("Give Sextus to the judgement of the people.", "add_political_power = -150\n" + hatred(-25), 20, "")],
      trigger="has_country_flag = ROM_kingdom")
event(45, "Rome Rises",
      "The hatred has boiled over. The gates are shut against the king; the Senate declares the Tarquins enemies "
      "of the people and calls the citizens to arms.",
      "fire",
      [("The king will fight for his throne.", "start_civil_war = { ideology = democratic size = 0.5 }\n"
        "set_variable = { ROM_hatred = 40 }\nROM_hatred_update = yes", 100, BIG_ENOUGH),
       ("Rome is one city, and the city is against him. The king flees.", REVOLT_FX, 100, "NOT = { " + BIG_ENOUGH + " }")],
      trigger="has_country_flag = ROM_kingdom")

# ------------------------------------------------------------------ decisions
DECISIONS = []


def decision(key, name, desc, icon, visible, available, cost, effect, ai, days_re_enable=0, days_remove=0,
             remove_effect=""):
    LOC[key] = name
    LOC[f"{key}_desc"] = desc
    lines = [f"\t{key} = {{", f"\t\ticon = {icon}", "\t\tallowed = { original_tag = ROM }",
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


REP, KING = "has_country_flag = ROM_republic", "has_country_flag = ROM_kingdom"
STRUGGLE = REP + "\nNOT = { has_country_flag = ROM_concord }"     # the orders not yet reconciled (Lex Hortensia)
END_DISCORD = """set_country_flag = ROM_concord
remove_dynamic_modifier = { modifier = ROM_struggle_of_the_orders }
set_variable = { ROM_discord = 0 }"""
decision("ROM_debt_relief", "Cancel the Debts",
         "Free the men in chains for debt and strike out what they owe. The creditors - the fathers - will not forget.",
         "GFX_decision_generic_civil_support", STRUGGLE, "", 75,
         discord(-12) + "\nadd_timed_idea = { idea = ROM_debt_relief_spirit days = 180 }",
         "base = 0\nmodifier = { add = 5 check_variable = { ROM_discord > 55 } }", days_re_enable=240)
decision("ROM_grain_dole", "Buy Grain from Sicily",
         "Famine in the city: the Senate buys grain from the Greeks of Sicily and sells it cheap.",
         "GFX_decision_generic_civil_support", STRUGGLE, "", 50, discord(-6) + "\nadd_stability = 0.02",
         "base = 0\nmodifier = { add = 3 check_variable = { ROM_discord > 45 } }", days_re_enable=180)
decision("ROM_levy_the_plebs", "Call Out the Levy",
         "Every man of property to the Field of Mars - and the poorest too, this once.",
         "GFX_decision_generic_military", REP, "has_war = yes", 25, "add_manpower = 3000\n" + discord(8),
         "base = 0\nmodifier = { add = 4 has_war = yes check_variable = { ROM_discord < 60 } }", days_re_enable=120)
decision("ROM_distribute_land", "Distribute the Conquered Land",
         "Allot the ager publicus to plebeian settlers, two iugera a family.",
         "GFX_decision_generic_construction", STRUGGLE,
         "has_completed_focus = ROM_ager_publicus\nnum_of_controlled_states > 4", 50,
         discord(-15) + "\nadd_manpower = 1500", "base = 0\nmodifier = { add = 5 check_variable = { ROM_discord > 35 } }",
         days_re_enable=365)
decision("ROM_appoint_dictator", "Appoint a Dictator",
         "In mortal danger the consuls name one man to rule alone - for six months, and not a day longer.",
         "GFX_decision_generic_prepare_civil_war", REP,
         "has_war = yes\nOR = {\n\tsurrender_progress > 0.05\n\thas_country_flag = ROM_porsenna_war\n\tcheck_variable = { ROM_discord > 69.9 }\n}",
         50, "add_timed_idea = { idea = ROM_dictator_spirit days = 180 }",
         "base = 0\nmodifier = { add = 10 surrender_progress > 0.1 }", days_re_enable=720, days_remove=180,
         remove_effect="country_event = { id = ante_rome.30 }")
decision("ROM_bread_and_games", "The King's Games",
         "Races in the Circus that the Tarquins built, meat and wine for the crowd - paid by the king.",
         "GFX_decision_generic_civil_support", KING, "", 75,
         hatred(-8) + "\nadd_timed_idea = { idea = ROM_bread_and_games_spirit days = 120 }",
         "base = 0\nmodifier = { add = 5 check_variable = { ROM_hatred > 40 } }", days_re_enable=150)
decision("ROM_spies_everywhere", "Spies in Every House",
         "Informers in the taverns, the baths and the temples. No plot will ripen unseen - and no man will speak freely.",
         "GFX_decision_generic_political_discourse", KING, "", 50,
         "add_timed_idea = { idea = ROM_terror_spirit days = 365 }\nset_country_flag = { flag = ROM_plot_cooldown days = 365 value = 1 }\n"
         + hatred(4), "base = 0\nmodifier = { add = 3 check_variable = { ROM_hatred > 60 } }", days_re_enable=400)
decision("ROM_forced_labour", "Forced Labour for the King's Works",
         "The plebs dig the great sewer and haul the stones of the Capitol - unpaid. The city grows; so does the anger.",
         "GFX_decision_generic_construction", KING, "", 25,
         """random_owned_controlled_state = {
	limit = { impassable = no free_building_slots = { building = industrial_complex size > 0 include_locked = yes } }
	add_extra_state_shared_building_slots = 1
	add_building_construction = { type = industrial_complex level = 1 instant_build = yes }
}
""" + hatred(12), "base = 0\nmodifier = { add = 3 check_variable = { ROM_hatred < 45 } }", days_re_enable=365)
# --- both roads: the Latins become Romans in peace; conquered land of Italy becomes Roman land (round 22, Peti)
decision("ROM_absorb_the_latins", "The Latins Become Romans",
         "The Latin towns already follow Rome in war - as allies or as subjects. Grant them Roman citizenship and the "
         "League ends without a battle: its land, its men and its gods become Rome's.",
         "GFX_decision_generic_political_discourse", "country_exists = LAT",
         "OR = {\n\tLAT = { is_subject_of = ROOT }\n\tis_in_faction_with = LAT\n}\nNOT = { has_war_with = LAT }\n"
         "", 150,
         "add_political_power = 0", "base = 5", days_remove=90,
         remove_effect="if = { limit = { country_exists = LAT OR = { LAT = { is_subject_of = ROOT } is_in_faction_with = LAT } }\n"
                       "\tannex_country = { target = LAT transfer_troops = yes }\n\tadd_stability = 0.03\n}")
ITALY = ["LAT", "VOL", "AEQ", "SAB", "MAR", "SAM", "PIC", "UMB", "VEI", "CAE", "TAR", "CLU", "VLT", "ARR", "FEL", "CAP",
         "CUM", "POS", "TAS", "MET", "KRO", "LOK", "RHE", "OEN", "DAU", "PEU", "MES", "LIG", "INS", "VEN", "RAE", "ROM"]


def italian_states():
    """state ids of mainland Italy: the states that the peoples of Italy own at the start (history/states)"""
    out = []
    for fp in (MOD / "history" / "states").glob("*.txt"):
        t = fp.read_text(encoding="utf-8-sig")
        m, o = re.search(r"\bid\s*=\s*(\d+)", t), re.search(r"\bowner\s*=\s*(\w+)", t)
        if m and o and o.group(1) in ITALY:
            out.append(int(m.group(1)))
    return sorted(out)


def integrate_decision():
    """a targeted decision: every Italian state Rome owns but has no core on can be made a core for 250 PP"""
    LOC["ROM_integrate_italy"] = "Make [FROM.GetName] Roman"
    LOC["ROM_integrate_italy_desc"] = ("Colonists, roads and Roman law: the land taken in war or won at the peace table "
                                       "becomes a true part of Rome.")
    targets = " ".join(map(str, italian_states()))
    return "\n".join([
        "\tROM_integrate_italy = {", "\t\ticon = GFX_decision_generic_construction",
        "\t\tallowed = { original_tag = ROM }", "\t\tstate_target = yes", f"\t\ttargets = {{ {targets} }}",
        "\t\ttarget_trigger = {", "\t\t\tFROM = {", "\t\t\t\tis_owned_by = ROOT", "\t\t\t\tis_controlled_by = ROOT",
        "\t\t\t\tNOT = { is_core_of = ROOT }", "\t\t\t}", "\t\t}",
        "\t\ton_map_mode = map_and_decisions_view", "\t\tcost = 250",
        "\t\tcomplete_effect = {", "\t\t\tFROM = { add_core_of = ROOT }", "\t\t}",
        "\t\tai_will_do = {", "\t\t\tbase = 1", "\t\t\tmodifier = { add = 4 has_political_power > 300 }", "\t\t}", "\t}"])


LOC["ROM_TT_PORSENNA_WITHDRAWS"] = ("Clusium does not border Rome: no war. Porsenna's host camps before the walls; a young "
                                    "Roman, Mucius Scaevola, burns his own hand in the king's fire - and Porsenna, "
                                    "impressed, makes peace and goes home.")
LOC["ROM_res_romana"] = "Res Romana"
LOC["ROM_res_romana_desc"] = "[Root.GetROMResRomana]"
LOC["ROM_res_romana_state_rep"] = ("The Struggle of the Orders stands at §Y[?ROM_discord|0]§! of 100. War raises it every "
                                   "week, peace lowers it. At §R80§! the plebs leave the city.")
LOC["ROM_res_romana_state_king"] = ("The Hatred of the King stands at §Y[?ROM_hatred|0]§! of 100. Above §R50§! conspiracies "
                                    "hatch, at §R100§! Rome rises. Below §G30§! a loyal Rome is within reach.")
CATEGORY = """# Generated by tools/rome_story.py
ROM_res_romana = {
	icon = generic_political_discourse
	allowed = { original_tag = ROM }
	visible = { OR = { has_country_flag = ROM_republic has_country_flag = ROM_kingdom } }
	priority = 100
}

# round 23 (Peti): making conquered Italian land Roman is a category of its own, open from the first day
ROM_latin_culture = {
	icon = generic_formable_nations
	allowed = { original_tag = ROM }
	priority = 90
}
"""
LOC["ROM_latin_culture"] = "Latin Culture"
LOC["ROM_latin_culture_desc"] = ("The land of Italy that Rome holds - by war or by treaty - can become Roman land: "
                                 "colonists, roads, the Latin tongue and Roman law. Every state costs 250 political power.")
SCRIPTED_LOC = """# Generated by tools/rome_story.py - the text of Rome's decision category follows the road taken
defined_text = {
	name = GetROMResRomana
	text = { trigger = { has_country_flag = ROM_republic } localization_key = ROM_res_romana_state_rep }
	text = { localization_key = ROM_res_romana_state_king }
}
"""


# ------------------------------------------------------------------ event pictures (own art, CC0)
PICS = {}


def _sky(d, w, h, top, bottom, ground, horizon):
    for y in range(h):
        t = y / h
        if y < horizon:
            c = tuple(int(top[i] + (bottom[i] - top[i]) * (y / horizon)) for i in range(3))
        else:
            c = tuple(int(ground[i] * (1 - 0.3 * (y - horizon) / (h - horizon))) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)


def _figure(d, x, y, s, col, toga=True, spear=False, crown=False):
    """a standing figure, feet at (x, y), height ~ 60*s"""
    d.ellipse([x - 5 * s, y - 60 * s, x + 5 * s, y - 50 * s], fill=col)
    if toga:
        d.polygon([(x - 9 * s, y), (x - 7 * s, y - 48 * s), (x + 7 * s, y - 48 * s), (x + 10 * s, y)], fill=col)
        d.line([(x - 7 * s, y - 44 * s), (x + 6 * s, y - 20 * s)], fill=tuple(min(255, c + 25) for c in col), width=max(1, int(2 * s)))
    else:
        d.polygon([(x - 7 * s, y - 25 * s), (x - 6 * s, y - 48 * s), (x + 6 * s, y - 48 * s), (x + 7 * s, y - 25 * s)], fill=col)
        d.line([(x - 4 * s, y - 25 * s), (x - 5 * s, y)], fill=col, width=max(1, int(4 * s)))
        d.line([(x + 4 * s, y - 25 * s), (x + 5 * s, y)], fill=col, width=max(1, int(4 * s)))
    if spear:
        d.line([(x + 9 * s, y - 75 * s), (x + 9 * s, y)], fill=col, width=max(1, int(2 * s)))
        d.polygon([(x + 7 * s, y - 75 * s), (x + 9 * s, y - 84 * s), (x + 11 * s, y - 75 * s)], fill=col)
        d.ellipse([x - 14 * s, y - 42 * s, x + 2 * s, y - 20 * s], fill=tuple(int(c * 0.8) for c in col))
    if crown:
        for k in (-4, 0, 4):
            d.polygon([(x + (k - 2) * s, y - 59 * s), (x + k * s, y - 66 * s), (x + (k + 2) * s, y - 59 * s)], fill=(220, 180, 70))


def _temple(d, x, y, w, h, col):
    d.polygon([(x - 6, y - h), (x + w / 2, y - h - h * 0.35), (x + w + 6, y - h)], fill=col)
    d.rectangle([x - 4, y - h, x + w + 4, y - h + 6], fill=col)
    n = 6
    for i in range(n):
        cx = x + i * w / (n - 1)
        d.rectangle([cx - 3, y - h + 6, cx + 3, y], fill=col)
    d.rectangle([x - 8, y, x + w + 8, y + 5], fill=col)


def _picture(kind):
    w, h = 210, 176
    rnd = random.Random(kind)
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    dark = (38, 26, 20)
    if kind == "senate":
        _sky(d, w, h, (168, 120, 78), (222, 188, 132), (120, 92, 64), 120)
        _temple(d, 30, 128, 150, 70, (226, 214, 190))
        for i in range(7):
            _figure(d, 18 + i * 29, 172, 0.75 + rnd.random() * 0.1, (150 + i * 8, 40, 32) if i % 3 == 0 else (232, 224, 206))
    elif kind == "crowd":
        _sky(d, w, h, (120, 70, 50), (210, 150, 90), (96, 82, 54), 95)
        d.polygon([(0, 110), (70, 70), (150, 92), (210, 80), (210, h), (0, h)], fill=(92, 78, 50))
        for i in range(40):
            x = rnd.uniform(0, w)
            y = 100 + (x / w) * 10 + rnd.uniform(0, 70)
            _figure(d, x, y, 0.25 + (y - 90) / 160, (60 + rnd.randint(0, 40), 46, 36))
    elif kind == "war":
        _sky(d, w, h, (90, 60, 50), (200, 120, 70), (80, 64, 46), 110)
        for row, (yy, s) in enumerate(((128, 0.6), (150, 0.75), (178, 0.95))):
            for i in range(9):
                _figure(d, 10 + i * 24 + row * 7, yy, s, (50 + row * 10, 36, 28), toga=False, spear=True)
    elif kind == "vote":
        _sky(d, w, h, (186, 150, 100), (230, 206, 160), (150, 122, 84), 115)
        _temple(d, 120, 110, 70, 46, (214, 200, 176))
        d.polygon([(70, 160), (78, 110), (112, 110), (120, 160)], fill=(150, 90, 50))
        d.ellipse([72, 102, 118, 118], fill=(170, 106, 60))
        for i in range(5):
            _figure(d, 20 + i * 14, 170, 0.6, (230, 222, 204))
            d.rectangle([24 + i * 14, 128, 30 + i * 14, 136], fill=(200, 180, 120))
    elif kind == "king":
        _sky(d, w, h, (60, 30, 40), (130, 60, 60), (70, 40, 34), 130)
        d.rectangle([60, 60, 150, 150], fill=(110, 50, 40))
        d.rectangle([84, 96, 126, 140], fill=(150, 110, 40))
        d.polygon([(84, 96), (105, 64), (126, 96)], fill=(150, 110, 40))
        _figure(d, 105, 150, 1.0, (120, 30, 60), crown=True)
        d.line([(124, 150), (130, 80)], fill=(220, 180, 70), width=3)
        for i in (25, 185):
            _figure(d, i, 172, 0.95, (60, 40, 32), toga=False, spear=True)
    elif kind == "conspiracy":
        _sky(d, w, h, (10, 12, 30), (36, 40, 70), (24, 22, 28), 130)
        d.ellipse([150, 20, 176, 46], fill=(220, 220, 200))
        for i, x in enumerate((50, 90, 130, 165)):
            _figure(d, x, 165, 0.9, (18, 16, 22))
            d.line([(x + 6, 120), (x + 18, 96)], fill=(200, 200, 210), width=2)
    elif kind == "fire":
        _sky(d, w, h, (60, 20, 10), (230, 110, 40), (60, 36, 26), 120)
        _temple(d, 50, 120, 110, 50, (40, 28, 22))
        for i in range(30):
            x = rnd.uniform(20, 190)
            d.polygon([(x - 6, 120), (x, 120 - rnd.uniform(20, 60)), (x + 6, 120)], fill=(250, 160 + rnd.randint(0, 60), 40))
        for i in range(10):
            _figure(d, 10 + i * 21, 172, 0.7, (30, 20, 16), toga=False, spear=i % 2 == 0)
    # fresco look: soft blur, grain, darker edges, a painted border
    im = im.filter(ImageFilter.GaussianBlur(0.7))
    px = im.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            n = rnd.randint(-10, 10)
            v = 1 - 0.35 * (((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) ** 1.5
            px[x, y] = tuple(max(0, min(255, int((c + n) * v))) for c in (r, g, b))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], outline=dark, width=3)
    return im.convert("RGBA")


def write_all():
    def write(rel, text, bom=False):
        p = MOD / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8-sig" if bom else "utf-8", newline="\n")

    write("common/dynamic_modifiers/ROM_dynamic_modifiers.txt", DYNAMIC)
    write("common/scripted_effects/ROM_scripted_effects.txt", EFFECTS)
    write("common/scripted_localisation/ROM_scripted_localisation.txt", SCRIPTED_LOC)
    write("events/ROM_events.txt", "# Generated by tools/rome_story.py\nadd_namespace = ante_rome\n\n" + "\n\n".join(EVENTS) + "\n")
    write("common/decisions/ROM_decisions.txt", "# Generated by tools/rome_story.py\nROM_res_romana = {\n"
          + "\n\n".join(DECISIONS) + "\n}\n\nROM_latin_culture = {\n" + integrate_decision() + "\n}\n")
    write("common/decisions/categories/ROM_categories.txt", CATEGORY)
    out = MOD / "gfx" / "event_pictures"
    out.mkdir(parents=True, exist_ok=True)
    sprites = ["# Generated by tools/rome_story.py - event pictures (own art, CC0)", "spriteTypes = {"]
    for kind in ("senate", "crowd", "war", "vote", "king", "conspiracy", "fire"):
        _picture(kind).save(out / f"ante_rome_{kind}.dds")
        sprites.append(f'\tspriteType = {{ name = "GFX_ante_event_{kind}" texturefile = "gfx/event_pictures/ante_rome_{kind}.dds" }}')
    sprites.append("}")
    write("interface/ante_events.gfx", "\n".join(sprites) + "\n")
    return len(EVENTS), len(DECISIONS)
