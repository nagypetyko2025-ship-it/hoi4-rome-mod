"""Athens' story systems (round 55, plan docs/athens_focus_tree.md) - used by tools/content.py.

Peti: a peaceful Athens of allies and puppets, an enlightened nation, and a NEW kind of mechanic - not again two roads
and one number to keep down with political power. Four systems instead:

  1. Silver (ATH_silver, talents): Athens' own currency. Income every week (a quarter of the monthly sum): 2 base,
     +4 the mines of Laurion, +1 every League member, +2 every tributary (puppet), +10 % the Owls. Spent on influence
     and on the Great Works (decisions with a silver price: custom_cost_trigger / custom_cost_text).
  2. The proxenia web: every Greek city (47 on the map, Italy and the Black Sea included) has ATH_influence 0-100,
     stored on that country. Country-targeted decisions raise it (a proxenos, funding the democrats, Pontic grain, a
     fleet to protect them), the Panathenaia raise all, the golden age raises all a little every week; it decays when
     neglected, faster in a rival league or at war with Athens. At 50 a city can be invited into the Delian League;
     at 80 a League member becomes a tributary (puppet, more silver, the others take fright) or an honoured free ally
     (ships for Athens, no decay); small neighbours at 100 can become Athenian (peaceful annexation, a late focus).
  3. The Great Works: Parthenon, theatre, Long Walls, Piraeus, Academy, Stoa, Odeion - bought with silver, built over
     months (days_remove), a lasting bonus each. 3 works: the dawn of a golden age, 6: the Age of Pericles.
  4. The election of the strategos: every year an event offers two to five candidates (Themistocles, Miltiades,
     Aristides, Pericles, Ephialtes - by the focuses taken); the winner gives a one-year spirit. Ostracism (decision,
     once in ten years) sends the year's man away for stability.
  Goal: the decision The School of Hellas - the Age of Pericles, a League of at least 12 (members and tributaries),
  one of them in Italy or Sicily and one on the Black Sea - with a victory screen (tools/victory.py).
The AI uses everything the player can (ai_will_do).

Writes (content.py calls write_all): common/decisions/ATH_decisions.txt, common/decisions/categories/ATH_categories.txt,
events/ATH_events.txt, common/scripted_effects/ATH_scripted_effects.txt.
"""
import re
from pathlib import Path

import victory

MOD = Path(__file__).resolve().parent.parent
LOC = {}
IDEAS = {}


def idea(key, name, pic, **mods):
    IDEAS[key] = (name, "generic_" + pic, mods)


def _ind(text, tabs):
    pad = "\t" * tabs
    return "\n".join(pad + l if l.strip() else l for l in text.splitlines())


# ------------------------------------------------------------------ the Greek world
def greek_tags():
    src = (MOD / "tools" / "data" / "world_509bc.py").read_text(encoding="utf-8")
    core = (MOD / "tools" / "data" / "world_245.py").read_text(encoding="utf-8")
    tags = re.findall(r'C\("(\w+)", "[^"]*", "[^"]*", "greek"', src)
    tags += re.findall(r'"(\w+)": dict\(name="[^"]*", adj="[^"]*", culture="greek"', core)
    return [t for t in dict.fromkeys(tags) if t != "ATH"]


GREEKS = greek_tags()
WEST = ["CUM", "POS", "TAS", "MET", "KRO", "LOK", "RHE", "SYR", "GEL", "AKR", "ZAN", "KAT", "MAS", "EMP", "EPD", "KRK"]
PONTUS = ["OLB", "TYS", "PNT", "ITR", "APP", "BYZ", "HER", "SNP"]
SMALL = ["EUB", "NAX", "EPI", "THS"]           # neighbours that can become Athenian
PELOPONNESE = ["LAK", "ARK", "EIS", "AKH", "KRN", "AGS", "EPI"]
GREEK_OR = "OR = { " + " ".join(f"tag = {t}" for t in GREEKS) + " }"


# ------------------------------------------------------------------ silver
def silver(n):
    """a decision price in silver: (custom_cost_trigger + text, the effect that pays it)"""
    LOC[f"ATH_COST_SILVER_{n}"] = f"Silver: §Y{n}§! talents"
    LOC[f"ATH_COST_SILVER_{n}_blocked"] = f"Silver: §R{n}§! talents"
    return (f"custom_cost_trigger = {{ check_variable = {{ ATH_silver > {n - 0.01} }} }}\n"
            f"custom_cost_text = ATH_COST_SILVER_{n}",
            f"add_to_variable = {{ ATH_silver = -{n} }}")


def silver_gain(n):
    LOC[f"ATH_TT_SILVER_P{n}"] = f"Silver: §G+{n}§! talents"
    return f"custom_effect_tooltip = ATH_TT_SILVER_P{n}\nhidden_effect = {{ add_to_variable = {{ ATH_silver = {n} }} }}"


def influence_all(n, tags=None, text="every Greek city"):
    key = f"ATH_TT_INFL_{'ALL' if tags is None else 'SOME'}_{abs(n)}_{len(tags or [])}"
    LOC[key] = f"Athenian influence in {text}: {'§G+' if n > 0 else '§R'}{n}§!"
    lim = GREEK_OR if tags is None else "OR = { " + " ".join(f"tag = {t}" for t in tags) + " }"
    return (f"custom_effect_tooltip = {key}\nhidden_effect = {{ every_country = {{ limit = {{ {lim} }} "
            f"add_to_variable = {{ ATH_influence = {n} }} clamp_variable = {{ var = ATH_influence min = 0 max = 100 }} }} }}")


# ------------------------------------------------------------------ spirits
for k, (name, mods) in {
        "themistocles": ("Strategos Themistocles", dict(production_speed_dockyard_factor=0.15, navy_org_factor=0.05)),
        "miltiades": ("Strategos Miltiades", dict(army_defence_factor=0.10, army_org_factor=0.05)),
        "aristides": ("Strategos Aristides the Just", dict(political_power_gain=0.15, stability_factor=0.03)),
        "pericles": ("Strategos Pericles", dict(production_speed_buildings_factor=0.15, research_speed_factor=0.03)),
        "ephialtes": ("Strategos Ephialtes", dict(stability_factor=0.07, political_power_gain=0.10))}.items():
    idea(f"ATH_strategos_{k}_spirit", name, "political_support", **mods)
STRATEGOI = [f"ATH_strategos_{k}_spirit" for k in ("themistocles", "miltiades", "aristides", "pericles", "ephialtes")]
REMOVE_STRATEGOS = "\n".join(f"if = {{ limit = {{ has_idea = {i} }} remove_ideas = {i} }}" for i in STRATEGOI)

WORKS = [   # key, name, desc, silver, days, picture, permanent modifiers, focus that unlocks it
    ("parthenon", "The Parthenon", "Marble from Pentelicus, gold and ivory for the Maiden: the temple of Athena on the Acropolis.",
     60, 365, "pp_unity_bonus", dict(stability_factor=0.08, political_power_gain=0.15), "ATH_patronage"),
    ("theatre", "The Theatre of Dionysus", "Fifteen thousand seats cut into the slope of the Acropolis: every Greek knows the plays of Athens.",
     30, 180, "propaganda", dict(political_power_factor=0.05), "ATH_patronage"),
    ("long_walls", "The Long Walls", "City and harbour joined by walls: Athens becomes an island no army can starve.",
     40, 240, "fortify_the_borders", dict(army_core_defence_factor=0.10, army_defence_factor=0.05), "ATH_hoplites"),
    ("piraeus", "The Harbour of the Piraeus", "Three harbours, ship sheds for 372 triremes and the Emporion of the Greek world.",
     35, 180, "navy_bonus", dict(production_speed_dockyard_factor=0.15, trade_opinion_factor=0.15), "ATH_piraeus"),
    ("academy", "The Academy", "In the grove of Akademos the philosophers teach - and argue.",
     40, 240, "research_bonus", dict(research_speed_factor=0.07), "ATH_philosophy"),
    ("stoa", "The Painted Stoa", "A colonnade on the Agora where citizens meet, talk and decide.",
     25, 120, "political_support", dict(political_power_gain=0.10, stability_factor=0.03), "ATH_patronage"),
    ("odeion", "The Odeion of Pericles", "A great roofed hall for music - built, they say, from the masts of Persian ships.",
     25, 120, "pp_unity_bonus", dict(stability_factor=0.05, war_support_factor=0.03), "ATH_patronage"),
]
for _k, _n, _d, _s, _t, _p, _m, _f in WORKS:
    idea(f"ATH_work_{_k}_spirit", _n, _p, **_m)
idea("ATH_golden_dawn_spirit", "The Dawn of a Golden Age", "research_bonus", research_speed_factor=0.05, stability_factor=0.03)
idea("ATH_age_of_pericles_spirit", "The Age of Pericles", "research_bonus", research_speed_factor=0.10, stability_factor=0.05,
     political_power_gain=0.10)
idea("ATH_school_of_hellas_goal_spirit", "The School of Hellas", "research_bonus", research_speed_factor=0.10,
     political_power_gain=0.25, stability_factor=0.10, trade_opinion_factor=0.25)


# ------------------------------------------------------------------ events: the election of the strategos
EVENTS = []


def event(eid, title, desc, pic, options, immediate=""):
    n = f"ante_athens.{eid}"
    LOC[f"{n}.t"] = title
    LOC[f"{n}.d"] = desc
    lines = ["country_event = {", f"\tid = {n}", f"\ttitle = {n}.t", f"\tdesc = {n}.d",
             f"\tpicture = GFX_ante_event_{pic}", "\tis_triggered_only = yes"]
    if immediate:
        lines += ["\timmediate = {", _ind(immediate, 2), "\t}"]
    for i, (text, eff, ai, trig) in enumerate(options):
        key = f"{n}.{'abcdefg'[i]}"
        LOC[key] = text
        lines += ["\toption = {", f"\t\tname = {key}"]
        if trig:
            lines += ["\t\ttrigger = {", _ind(trig, 3), "\t\t}"]
        lines += [f"\t\tai_chance = {{ factor = {ai} }}", _ind(eff, 2), "\t}"]
    lines.append("}")
    EVENTS.append("\n".join(lines))


def candidate(k):
    return REMOVE_STRATEGOS + f"\nadd_timed_idea = {{ idea = ATH_strategos_{k}_spirit days = 365 }}"


event(1, "The Assembly Elects the Strategos",
      "On the Pnyx the citizens of Athens raise their hands. Which man shall lead the ten generals - and the city - "
      "this year?", "vote", [
          ("Themistocles: ships, more ships.", candidate("themistocles"), 3, ""),
          ("Miltiades: the hoplites must be ready.", candidate("miltiades"), 2, ""),
          ("Aristides the Just: honest dealing with our allies.", candidate("aristides"), 3,
           "has_completed_focus = ATH_delian_league"),
          ("Pericles: build, teach, lead.", candidate("pericles"), 4, "has_completed_focus = ATH_patronage"),
          ("Ephialtes: the power belongs to the people.", candidate("ephialtes"), 2,
           "has_completed_focus = ATH_reforms_of_ephialtes"),
      ])

# ------------------------------------------------------------------ weekly: silver, influence, elections
LEAGUE_SIZE = ("set_variable = { ATH_league_size = 0 }\n"
               "every_country = { limit = { is_in_faction_with = ROOT NOT = { tag = ROOT } } "
               "ROOT = { add_to_variable = { ATH_league_size = 1 } } }\n"
               "every_subject_country = { limit = { NOT = { is_in_faction_with = ROOT } } "
               "ROOT = { add_to_variable = { ATH_league_size = 1 } } }")


def weekly():
    return f"""if = {{
	limit = {{ original_tag = ATH }}
	if = {{
		limit = {{ NOT = {{ has_country_flag = ATH_started }} }}
		set_country_flag = ATH_started
		set_variable = {{ ATH_silver = 15 }}
		every_country = {{ limit = {{ {GREEK_OR} }} set_country_flag = ante_greek set_variable = {{ ATH_influence = 10 }} }}
	}}
	# silver: a quarter of the month's income every week
	set_variable = {{ ATH_silver_income = 2 }}
	if = {{ limit = {{ has_country_flag = ATH_laurion }} add_to_variable = {{ ATH_silver_income = 4 }} }}
	every_country = {{
		limit = {{ is_in_faction_with = ROOT NOT = {{ tag = ROOT }} is_subject = no }}
		ROOT = {{ add_to_variable = {{ ATH_silver_income = 1 }} }}
	}}
	every_subject_country = {{ ROOT = {{ add_to_variable = {{ ATH_silver_income = 2 }} }} }}
	if = {{ limit = {{ has_country_flag = ATH_owls }} multiply_variable = {{ ATH_silver_income = 1.1 }} }}
	set_variable = {{ ATH_silver_week = ATH_silver_income }}
	divide_variable = {{ ATH_silver_week = 4 }}
	add_to_variable = {{ ATH_silver = ATH_silver_week }}
{_ind(LEAGUE_SIZE, 1)}
	# influence: decay when neglected, faster in a rival league or at war; the golden age spreads it
	set_variable = {{ ATH_influence_drift = -0.15 }}
	if = {{ limit = {{ has_idea = ATH_golden_dawn_spirit }} add_to_variable = {{ ATH_influence_drift = 0.25 }} }}
	if = {{ limit = {{ has_idea = ATH_age_of_pericles_spirit }} add_to_variable = {{ ATH_influence_drift = 0.45 }} }}
	if = {{ limit = {{ has_idea = ATH_work_theatre_spirit }} add_to_variable = {{ ATH_influence_drift = 0.15 }} }}
	every_country = {{
		limit = {{ has_country_flag = ante_greek }}
		if = {{
			limit = {{ OR = {{ is_in_faction_with = ROOT is_subject_of = ROOT has_country_flag = ATH_honoured }} }}
			if = {{ limit = {{ check_variable = {{ ROOT.ATH_influence_drift > 0 }} }} add_to_variable = {{ ATH_influence = ROOT.ATH_influence_drift }} }}
		}}
		else = {{
			add_to_variable = {{ ATH_influence = ROOT.ATH_influence_drift }}
			if = {{ limit = {{ OR = {{ has_war_with = ROOT AND = {{ is_in_faction = yes NOT = {{ is_in_faction_with = ROOT }} }} }} }} add_to_variable = {{ ATH_influence = -0.35 }} }}
		}}
		if = {{ limit = {{ tag = LAK ROOT = {{ has_country_flag = ATH_sparta_rival }} }} set_variable = {{ ATH_influence = 0 }} }}
		clamp_variable = {{ var = ATH_influence min = 0 max = 100 }}
	}}
	# the yearly election of the strategos
	if = {{
		limit = {{ has_completed_focus = ATH_reforms_of_cleisthenes NOT = {{ has_country_flag = ATH_term }} }}
		set_country_flag = {{ flag = ATH_term days = 365 value = 1 }}
		country_event = {{ id = ante_athens.1 }}
	}}
}}"""


# ------------------------------------------------------------------ decisions
DECISIONS = {"ATH_silver_category": [], "ATH_proxenia_category": [], "ATH_works_category": [], "ATH_school_category": []}


def decision(cat, key, name, desc, icon, visible, available, effect, ai, cost=None, days_re_enable=0, extra="",
             target=None, pp=0):
    LOC[key] = name
    LOC[f"{key}_desc"] = desc
    lines = [f"\t{key} = {{", f"\t\ticon = {icon}", "\t\tallowed = { original_tag = ATH }"]
    if target:
        tags, trig = target
        lines += ["\t\ttargets = { " + " ".join(tags) + " }", "\t\ttarget_trigger = {", "\t\t\tFROM = {",
                  _ind(trig, 4), "\t\t\t}", "\t\t}", "\t\ton_map_mode = map_and_decisions_view"]
    lines += ["\t\tvisible = {", _ind(visible, 3), "\t\t}"]
    if available:
        lines += ["\t\tavailable = {", _ind(available, 3), "\t\t}"]
    pay = ""
    if cost:
        trig, pay = silver(cost)
        lines.append(_ind(trig, 2))
    if pp:
        lines.append(f"\t\tcost = {pp}")
    if days_re_enable:
        lines.append(f"\t\tdays_re_enable = {days_re_enable}")
    if extra:
        lines.append(_ind(extra, 2))
    lines += ["\t\tcomplete_effect = {", _ind((pay + "\n" if pay else "") + effect, 3), "\t\t}",
              "\t\tai_will_do = {", _ind(ai, 3), "\t\t}", "\t}"]
    DECISIONS[cat].append("\n".join(lines))


def infl(n):
    LOC[f"ATH_TT_INFL_FROM_{n}"] = f"Athenian influence in [FROM.GetName]: §G+{n}§!"
    return (f"custom_effect_tooltip = ATH_TT_INFL_FROM_{n}\nhidden_effect = {{ FROM = {{ add_to_variable = {{ ATH_influence = {n} }} "
            "clamp_variable = { var = ATH_influence min = 0 max = 100 } } }")


OPEN = "has_completed_focus = ATH_proxenia"
FRIEND = "exists = yes\nNOT = { tag = ROOT }\nNOT = { has_war_with = ROOT }"
NOW = " (Athenian influence now: [?FROM.ATH_influence|0].)"
decision("ATH_proxenia_category", "ATH_send_proxenos", "Send a Proxenos to [FROM.GetName]",
         "A citizen of [FROM.GetName] becomes the friend and host of every Athenian in his city." + NOW,
         "GFX_decision_generic_political_discourse", OPEN, "", infl(10),
         "base = 1\nmodifier = { add = 4 FROM = { check_variable = { ATH_influence > 25 } check_variable = { ATH_influence < 50 } } }"
         "\nmodifier = { factor = 0 check_variable = { ATH_silver < 15 } }",
         cost=5, days_re_enable=90, target=(GREEKS, FRIEND + "\ncheck_variable = { ATH_influence < 100 }"))
decision("ATH_proxenia_category", "ATH_fund_democrats", "Fund the Democrats of [FROM.GetName]",
         "Silver for the people's party of [FROM.GetName]: one day they will rule - and remember who helped them." + NOW,
         "GFX_decision_generic_civil_support", OPEN, "", infl(25),
         "base = 1\nmodifier = { add = 3 FROM = { check_variable = { ATH_influence > 30 } } }"
         "\nmodifier = { factor = 0 check_variable = { ATH_silver < 30 } }",
         cost=15, days_re_enable=180,
         target=(GREEKS, FRIEND + "\nNOT = { has_government = democratic }\ncheck_variable = { ATH_influence < 100 }"))
decision("ATH_proxenia_category", "ATH_grain_trade", "Grain Trade with [FROM.GetName]",
         "The grain ships of the Black Sea sail to the Piraeus - and Athenian silver and pottery sail back." + NOW,
         "GFX_decision_generic_fundraising", "has_completed_focus = ATH_pontic_grain", "", infl(15) + "\n" + silver_gain(3),
         "base = 3\nmodifier = { factor = 0 check_variable = { ATH_silver < 20 } }",
         cost=10, days_re_enable=120, target=(PONTUS, FRIEND + "\ncheck_variable = { ATH_influence < 100 }"))
decision("ATH_proxenia_category", "ATH_protection_fleet", "A Fleet to Protect [FROM.GetName]",
         "Athenian triremes in the harbour of [FROM.GetName] while it is at war: friends in need are friends indeed." + NOW,
         "GFX_decision_generic_naval", OPEN, "has_navy_size = { size > 2 }", infl(20),
         "base = 1\nmodifier = { factor = 0 check_variable = { ATH_silver < 40 } }",
         cost=20, days_re_enable=180, target=(GREEKS, FRIEND + "\nhas_war = yes\ncheck_variable = { ATH_influence < 100 }"))
LOC["ATH_TT_JOIN_LEAGUE"] = "[FROM.GetName] joins the §YDelian League§! and pays a tribute of §Y1§! talent a month."
decision("ATH_proxenia_category", "ATH_invite_to_league", "Invite [FROM.GetName] into the Delian League",
         "The envoys of [FROM.GetName] swear on sunken iron: as long as the iron stays at the bottom of the sea, the "
         "oath holds." + NOW,
         "GFX_decision_generic_form_nation", "has_completed_focus = ATH_delian_league", "is_subject = no",
         "custom_effect_tooltip = ATH_TT_JOIN_LEAGUE\nhidden_effect = {\n"
         "\tif = { limit = { is_in_faction = no } create_faction = ante_faction_delian_league }\n"
         "\tif = { limit = { is_faction_leader = yes } add_to_faction = FROM }\n}",
         "base = 10", target=(GREEKS, FRIEND + "\ncheck_variable = { ATH_influence > 49.99 }\nis_in_faction = no\n"
                              "is_subject = no\nNOT = { has_country_flag = ATH_honoured }"))
LOC["ATH_TT_TRIBUTARY"] = ("[FROM.GetName] becomes a §Ytributary§! (puppet): §G+2§! talents a month - but the other "
                           "members of the League take fright (influence §R-5§!).")
decision("ATH_proxenia_category", "ATH_make_tributary", "Make [FROM.GetName] a Tributary",
         "No more ships of their own: [FROM.GetName] pays silver instead, and Athens decides for it." + NOW,
         "GFX_decision_generic_political_discourse", "has_completed_focus = ATH_delian_league", "",
         "custom_effect_tooltip = ATH_TT_TRIBUTARY\nhidden_effect = {\n\tpuppet = FROM\n"
         "\tevery_country = { limit = { is_in_faction_with = ROOT NOT = { tag = ROOT } is_subject = no } "
         "add_to_variable = { ATH_influence = -5 } }\n}",
         "base = 2\nmodifier = { add = 3 has_country_flag = ATH_treasury_in_athens }",
         target=(GREEKS, "is_in_faction_with = ROOT\nNOT = { tag = ROOT }\nis_subject = no\n"
                         "check_variable = { ATH_influence > 79.99 }\nNOT = { has_country_flag = ATH_honoured }"))
LOC["ATH_TT_HONOURED"] = ("[FROM.GetName] stays free and becomes an §Yhonoured ally§!: its influence never decays, and "
                          "its ships sail with Athens (navy experience).")
decision("ATH_proxenia_category", "ATH_honour_ally", "Honour [FROM.GetName] as a Free Ally",
         "A golden crown for the city, its citizens honoured in the theatre of Dionysus: free friends serve better "
         "than subjects." + NOW,
         "GFX_decision_generic_civil_support", "has_completed_focus = ATH_delian_league", "",
         "custom_effect_tooltip = ATH_TT_HONOURED\nhidden_effect = { FROM = { set_country_flag = ATH_honoured } }\n"
         "navy_experience = 10", "base = 3\nmodifier = { add = 3 has_country_flag = ATH_treasury_at_delos }",
         target=(GREEKS, "is_in_faction_with = ROOT\nNOT = { tag = ROOT }\nis_subject = no\n"
                         "check_variable = { ATH_influence > 79.99 }\nNOT = { has_country_flag = ATH_honoured }"))
decision("ATH_proxenia_category", "ATH_citizenship", "Athenian Citizenship for [FROM.GetName]",
         "[FROM.GetName] has been Athenian in all but name for years: let it be Athenian in law." + NOW,
         "GFX_decision_generic_form_nation", "has_completed_focus = ATH_cleruchies", "", "annex_country = { target = FROM transfer_troops = yes }",
         "base = 10", pp=50,
         target=(SMALL, "exists = yes\nNOT = { tag = ROOT }\nOR = { is_subject_of = ROOT is_in_faction_with = ROOT }\n"
                        "check_variable = { ATH_influence > 99.9 }"))
decision("ATH_proxenia_category", "ATH_panathenaia", "The Great Panathenaia",
         "Every four years the whole Greek world comes to Athens: the procession, the games, the new robe for Athena.",
         "GFX_decision_generic_political_discourse", OPEN, "", influence_all(5),
         "base = 5\nmodifier = { factor = 0 check_variable = { ATH_silver < 30 } }", cost=20, days_re_enable=365)

# the Great Works
LOC["ATH_TT_GOLDEN"] = "Great Works finished: [?ATH_works|0]. At §Y3§!: the Dawn of a Golden Age; at §Y6§!: the Age of Pericles."
for k, name, desc, cost, days, pic, mods, focus in WORKS:
    finish = (f"add_ideas = ATH_work_{k}_spirit\nadd_to_variable = {{ ATH_works = 1 }}\nATH_golden_age_update = yes\n"
              f'log = "ANTE|[GetDateText]|work|ATH|{k}"')
    LOC[f"ATH_TT_WORK_{k.upper()}"] = f"Built in §Y{days // 30}§! months: §Y{name}§! (a lasting national spirit)."
    decision("ATH_works_category", f"ATH_build_{k}", name, desc + f" ({days // 30} months to build.)",
             "GFX_decision_generic_construction", f"has_completed_focus = {focus}\nNOT = {{ has_country_flag = ATH_built_{k} }}",
             "", f"set_country_flag = ATH_built_{k}\ncustom_effect_tooltip = ATH_TT_WORK_{k.upper()}\ncustom_effect_tooltip = ATH_TT_GOLDEN",
             "base = 5\nmodifier = { factor = 0 check_variable = { ATH_silver < " + str(cost + 10) + " } }", cost=cost,
             extra=f"days_remove = {days}\nremove_effect = {{\n{_ind(finish, 1)}\n}}")
EFFECTS = """# Generated by tools/athens_story.py
ATH_golden_age_update = {
	if = {
		limit = { check_variable = { ATH_works > 5.9 } NOT = { has_idea = ATH_age_of_pericles_spirit } }
		if = { limit = { has_idea = ATH_golden_dawn_spirit } remove_ideas = ATH_golden_dawn_spirit }
		add_ideas = ATH_age_of_pericles_spirit
	}
	else_if = {
		limit = { check_variable = { ATH_works > 2.9 } NOT = { has_idea = ATH_golden_dawn_spirit } NOT = { has_idea = ATH_age_of_pericles_spirit } }
		add_ideas = ATH_golden_dawn_spirit
	}
}
"""

# ostracism
decision("ATH_silver_category", "ATH_ostracism_vote", "Ostracism",
         "The citizens write a name on a potsherd. The man with the most sherds leaves Athens for ten years - and with "
         "him the year's quarrels.", "GFX_decision_generic_political_discourse",
         "has_completed_focus = ATH_ostracism", "OR = { " + " ".join(f"has_idea = {i}" for i in STRATEGOI) + " }",
         REMOVE_STRATEGOS + "\nadd_stability = 0.10\nadd_political_power = 50\nset_country_flag = { flag = ATH_term days = 1 value = 1 }",
         "base = 0\nmodifier = { add = 3 has_stability < 0.4 }", pp=25, days_re_enable=3650)

# the goal: The School of Hellas
LOC["ATH_TT_SCHOOL_WORKS"] = "The Age of Pericles: at least §Y6§! Great Works finished (now: [?ATH_works|0])"
LOC["ATH_TT_SCHOOL_LEAGUE"] = "The Delian League counts at least §Y12§! members and tributaries (now: [?ATH_league_size|0])"
LOC["ATH_TT_SCHOOL_WEST"] = "At least one of them in Italy, Sicily or the far West"
LOC["ATH_TT_SCHOOL_PONTUS"] = "At least one of them on the Black Sea"
LEAGUE_OF = "OR = { is_in_faction_with = ROOT is_subject_of = ROOT }"
decision("ATH_school_category", "ATH_school_of_hellas_goal", "The School of Hellas",
         "Our city is the school of Hellas: from Sicily to the Black Sea the Greeks learn from Athens, trade with Athens "
         "and stand with Athens.", "GFX_decision_generic_form_nation", "NOT = { has_country_flag = ATH_school_done }",
         "custom_trigger_tooltip = { tooltip = ATH_TT_SCHOOL_WORKS check_variable = { ATH_works > 5.9 } }\n"
         "custom_trigger_tooltip = { tooltip = ATH_TT_SCHOOL_LEAGUE check_variable = { ATH_league_size > 11.9 } }\n"
         "custom_trigger_tooltip = { tooltip = ATH_TT_SCHOOL_WEST any_country = { " + LEAGUE_OF + " OR = { "
         + " ".join(f"tag = {t}" for t in WEST) + " } } }\n"
         "custom_trigger_tooltip = { tooltip = ATH_TT_SCHOOL_PONTUS any_country = { " + LEAGUE_OF + " OR = { "
         + " ".join(f"tag = {t}" for t in PONTUS) + " } } }\nis_subject = no",
         "set_country_flag = ATH_school_done\nadd_ideas = ATH_school_of_hellas_goal_spirit\n" + victory.FIRE["ATH"],
         "base = 100", extra="fire_only_once = yes")

CATEGORIES = {
    "ATH_silver_category": ("The Athenian Silver",
                            "Silver in the treasury: §Y[?ATH_silver|0]§! talents (income §Y[?ATH_silver_income|1]§! a month). "
                            "The mines of Laurion, the harbour and the tribute of the League pay for Athens' influence and "
                            "its Great Works.", 100),
    "ATH_proxenia_category": ("The Proxenia",
                              "Silver: §Y[?ATH_silver|0]§! talents. Every Greek city has an Athenian influence of 0-100: at "
                              "§Y50§! it can join the Delian League, at §Y80§! a member becomes a tributary or an honoured "
                              "ally. Neglected cities forget Athens.", 95),
    "ATH_works_category": ("The Great Works",
                           "Silver: §Y[?ATH_silver|0]§! talents. Great Works finished: §Y[?ATH_works|0]§!. At 3 the "
                           "Dawn of a Golden Age, at 6 the Age of Pericles.", 90),
    "ATH_school_category": ("The School of Hellas",
                            "The goal of Athens: the Age of Pericles and a League of twelve, from the West to the Black Sea.", 85),
}


def write_all():
    def write(rel, text):
        p = MOD / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")

    cats = ["# Generated by tools/athens_story.py"]
    for key, (name, desc, prio) in CATEGORIES.items():
        LOC[key] = name
        LOC[f"{key}_desc"] = desc
        cats += [f"{key} = {{", "\ticon = generic_political_actions", "\tallowed = { original_tag = ATH }",
                 "\tvisible = { has_completed_focus = ATH_reforms_of_cleisthenes }", f"\tpriority = {prio}", "}"]
    write("common/decisions/categories/ATH_categories.txt", "\n".join(cats) + "\n")
    write("common/decisions/ATH_decisions.txt", "# Generated by tools/athens_story.py\n" + "\n".join(
        f"{cat} = {{\n" + "\n\n".join(lst) + "\n}\n" for cat, lst in DECISIONS.items()))
    write("events/ATH_events.txt", "# Generated by tools/athens_story.py\nadd_namespace = ante_athens\n\n" + "\n\n".join(EVENTS) + "\n")
    write("common/scripted_effects/ATH_scripted_effects.txt", EFFECTS)
    return len(EVENTS), sum(len(v) for v in DECISIONS.values())


WEEKLY = weekly()
