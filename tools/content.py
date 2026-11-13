"""Hand-designed content that is the same for every people (no game needed, ~1 s).

Writes:
  common/national_focus/ante_generic_focus.txt   the generic focus tree (default = yes; must always exist)
  common/ideas/ante_generic_ideas.txt            national spirits granted by that tree
  common/characters/ante_leaders.txt             country leaders of tools/data/leaders_509bc.py
  common/country_leader/ante_traits.txt          their traits
  localisation/english/ante_content_l_english.yml

Run AFTER tools/world.py (the leaders' sub-ideology is read from history/countries, and world.py writes the
recruit_character lines). Icons and modifiers are base-game ones (checked against the game files).
"""
import re
import sys
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data.leaders_509bc import LEADERS, TRAITS  # noqa: E402

SUB_IDEOLOGY = {"democratic": "conservatism", "neutrality": "despotism", "fascism": "fascism_ideology",
                "communism": "marxism"}
SUB_OVERRIDE = {"ATH": "liberalism", "KRO": "conservatism", "CAR": "conservatism"}

# ------------------------------------------------------------------ building rewards (base-game pattern)
def build(building, extra=""):
    return f"""random_owned_controlled_state = {{
	limit = {{
		impassable = no
		{extra}
		free_building_slots = {{ building = {building} size > 0 include_locked = yes }}
	}}
	add_extra_state_shared_building_slots = 1
	add_building_construction = {{ type = {building} level = 1 instant_build = yes }}
}}"""


def infra():
    return """random_owned_controlled_state = {
	limit = { impassable = no }
	add_building_construction = { type = infrastructure level = 1 instant_build = yes }
}"""


def tech(category, name):
    return f"add_tech_bonus = {{ name = {name} bonus = 0.5 uses = 1 category = {category} }}"


# ------------------------------------------------------------------ national spirits
IDEAS = {
    "ante_favour_of_the_gods": ("Favour of the Gods", "generic_pp_unity_bonus",
                                {"stability_factor": 0.05, "war_support_factor": 0.05}),
    "ante_tribute_collectors": ("Tribute Collectors", "generic_political_support", {"political_power_gain": 0.15}),
    "ante_granaries": ("Granaries", "generic_agrarian_society", {"monthly_population": 0.10, "stability_factor": 0.03}),
    "ante_working_mines": ("Working the Mines", "generic_exploit_mines",
                           {"production_speed_buildings_factor": 0.10}),
    "ante_mounted_nobles": ("Mounted Nobles", "generic_morale_bonus", {"army_attack_factor": 0.05}),
    "ante_hillforts_spirit": ("Hillforts", "generic_fortify_the_borders", {"army_defence_factor": 0.10}),
    "ante_war_bands_spirit": ("War Bands", "generic_manpower_bonus", {"conscription": 0.01}),
    "ante_ambition_of_conquest": ("Ambition of Conquest", "generic_war_preparation",
                                  {"justify_war_goal_time": -0.25, "war_support_factor": 0.05}),
    "ante_one_people_spirit": ("One People", "generic_constitutional_guarantees",
                        {"stability_factor": 0.10, "political_power_gain": 0.10}),
}

# ------------------------------------------------------------------ the tree
# (id, name, description, icon, x, y, prerequisites [AND of OR-groups], reward, extra lines, ai factor)
F = []


def focus(fid, name, desc, icon, x, y, pre, reward, extra="", ai=1, filters="FOCUS_FILTER_POLITICAL"):
    F.append(dict(id=fid, name=name, desc=desc, icon=icon, x=x, y=y, pre=pre, reward=reward, extra=extra, ai=ai,
                  filters=filters))


P, I, R, M = "FOCUS_FILTER_POLITICAL", "FOCUS_FILTER_INDUSTRY", "FOCUS_FILTER_RESEARCH", "FOCUS_FILTER_MANPOWER"
COAST = "available = { any_owned_state = { is_coastal = yes } }"

# --- statecraft and the gods (x 0..4)
focus("ante_council_of_elders", "Council of the Elders", "The heads of the great families meet to decide the course of our people.",
      "GFX_goal_generic_political_pressure", 2, 0, [], "add_political_power = 50", filters=P)
focus("ante_codify_customs", "Codify the Customs", "Write down - or recite before all - the laws of our fathers.",
      "GFX_goal_generic_national_unity", 1, 1, [["ante_council_of_elders"]], "add_stability = 0.05", filters=P)
focus("ante_honour_the_gods", "Honour the Gods", "Raise altars and keep the festivals, so that the gods stand with us.",
      "GFX_goal_generic_propaganda", 3, 1, [["ante_council_of_elders"]], "add_ideas = ante_favour_of_the_gods", filters=P)
focus("ante_tribute", "Collect the Tribute", "Dues in grain, cattle and silver flow to the hall of the rulers.",
      "GFX_goal_generic_trade", 0, 2, [["ante_codify_customs"]], "add_ideas = ante_tribute_collectors", filters=P)
focus("ante_envoys", "Envoys and Guest-Friends", "Gifts and oaths bind the great houses of our neighbours to ours.",
      "GFX_goal_generic_improve_relations", 2, 2, [["ante_codify_customs", "ante_honour_the_gods"]],
      "add_political_power = 75\nadd_stability = 0.03", filters=P)
focus("ante_oracles", "Consult the Oracles", "Seers, priests and wise men read the will of the gods - and much else.",
      "GFX_goal_generic_scientific_exchange", 4, 2, [["ante_honour_the_gods"]],
      "add_research_slot = 1", filters=R, ai=3)
focus("ante_scribes", "Scribes and Teachers", "Letters borrowed from the traders of the sea record our accounts and our deeds.",
      "GFX_goal_generic_neutrality_focus", 1, 3, [["ante_tribute"], ["ante_envoys"]],
      tech("industry", "ante_scribes_bonus") + "\nadd_political_power = 50", filters=R)
focus("ante_festivals", "Games and Festivals", "Contests of strength and song draw every clan to the sanctuary.",
      "GFX_goal_generic_consumer_goods", 3, 3, [["ante_envoys", "ante_oracles"]],
      "add_stability = 0.05\nadd_war_support = 0.05", filters=P)
focus("ante_one_people", "One People", "Many clans, one assembly, one name.",
      "GFX_goal_generic_major_alliance", 2, 4, [["ante_scribes"], ["ante_festivals"]],
      "add_ideas = ante_one_people_spirit", filters=P)

# --- land and labour (x 6..10)
focus("ante_tame_the_land", "Tame the Land", "Drain the marshes, clear the scrub and mark the fields.",
      "GFX_goal_generic_construct_infrastructure", 8, 0, [], infra() + "\nadd_political_power = 25", filters=I, ai=3)
focus("ante_markets", "Markets and Trade", "A market place under the protection of the gods brings traders from afar.",
      "GFX_goal_generic_construct_civ_factory", 7, 1, [["ante_tame_the_land"]], build("industrial_complex"),
      filters=I, ai=4)
focus("ante_clear_forests", "Clear the Forests", "Axe and fire open new land for the plough.",
      "GFX_goal_generic_construction", 9, 1, [["ante_tame_the_land"]],
      infra() + "\nadd_ideas = ante_granaries", filters=I, ai=3)
focus("ante_craftsmen", "Craftsmen's Quarter", "Potters, weavers and carpenters settle by the walls.",
      "GFX_goal_generic_construct_civilian", 6, 2, [["ante_markets"]], build("industrial_complex"), filters=I, ai=4)
focus("ante_mines", "Mines of the Hills", "Copper, tin and the new iron are dug from the hills.",
      "GFX_goal_generic_production", 8, 2, [["ante_markets", "ante_clear_forests"]],
      "add_ideas = ante_working_mines\n" + tech("industry", "ante_mines_bonus"), filters=I, ai=3)
focus("ante_roads", "Paths and Fords", "Tracks between the settlements, fords and ferries over the rivers.",
      "GFX_goal_generic_construct_infrastructure", 10, 2, [["ante_clear_forests"]], infra() + "\n" + infra(),
      filters=I, ai=2)
focus("ante_smithies", "Smithies", "The smiths' fires burn day and night: spearheads, helmets, shields.",
      "GFX_goal_generic_construct_mil_factory", 7, 3, [["ante_craftsmen"], ["ante_mines"]], build("arms_factory"),
      filters=I, ai=4)
focus("ante_great_works", "Great Works", "Walls, temples and harbours that will outlast their builders.",
      "GFX_goal_generic_construct_civ_factory", 9, 3, [["ante_mines", "ante_roads"]],
      build("industrial_complex") + "\n" + tech("construction_tech", "ante_great_works_bonus"), filters=I, ai=3)
focus("ante_city_of_stone", "A City of Stone", "Our capital grows into a true city.",
      "GFX_goal_generic_construction2", 8, 4, [["ante_smithies"], ["ante_great_works"]],
      build("industrial_complex") + "\n" + build("arms_factory"), filters=I, ai=3)

# --- war (x 12..16)
focus("ante_warrior_levy", "Levy of the Warriors", "Every free man owes his spear when the horn sounds.",
      "GFX_goal_generic_allies_build_infantry", 14, 0, [], "army_experience = 15\nadd_manpower = 2000", filters=M, ai=2)
focus("ante_drill", "Drill the Spearmen", "Shoulder to shoulder: the close order of the phalanx.",
      "GFX_goal_generic_army_doctrines", 13, 1, [["ante_warrior_levy"]],
      "army_experience = 15\nadd_doctrine_cost_reduction = { name = ante_drill_bonus cost_reduction = 0.5 uses = 1 category = land_doctrine }",
      filters=R, ai=2)
focus("ante_bronze_and_iron", "Bronze and Iron", "Better blades and armour from the smiths.",
      "GFX_goal_generic_small_arms", 15, 1, [["ante_warrior_levy"]], tech("infantry_weapons", "ante_weapons_bonus"),
      filters=R, ai=2)
focus("ante_horsemen", "Mounted Nobles", "The sons of the great houses ride to war.",
      "GFX_goal_generic_cavalry", 12, 2, [["ante_drill"]], "add_ideas = ante_mounted_nobles", filters=M, ai=2)
focus("ante_hillforts", "Hillforts", "Earth ramparts and timber walls on every height.",
      "GFX_goal_generic_fortify_city", 14, 2, [["ante_drill", "ante_bronze_and_iron"]], "add_ideas = ante_hillforts_spirit",
      filters=M, ai=2)
focus("ante_seafarers", "Seafarers", "Ships for fishing, trade - and raids along the coast.",
      "GFX_goal_generic_construct_naval_dockyard", 16, 2, [["ante_bronze_and_iron"]],
      build("dockyard", "is_coastal = yes") + "\nnavy_experience = 15", extra=COAST, filters=I, ai=2)
focus("ante_war_bands", "Sworn War Bands", "Companions who live and die with their lord.",
      "GFX_goal_generic_special_forces", 13, 3, [["ante_horsemen", "ante_hillforts"]], "add_ideas = ante_war_bands_spirit",
      filters=M, ai=2)
focus("ante_ambition", "Ambition of Conquest", "Our neighbours' fields are rich and their walls are low.",
      "GFX_goal_generic_territory_or_war", 15, 3, [["ante_hillforts", "ante_seafarers"]],
      "add_ideas = ante_ambition_of_conquest\nadd_war_support = 0.05", filters=P, ai=1)
focus("ante_host_of_the_people", "Host of the People", "The whole people under arms: a power to be feared.",
      "GFX_goal_generic_major_war", 14, 4, [["ante_war_bands"], ["ante_ambition"]],
      "army_experience = 25\nadd_manpower = 5000\nadd_war_support = 0.05", filters=M, ai=2)

# --- crown of the tree
focus("ante_rise_to_greatness", "Rise to Greatness", "Lawgivers, builders and warriors have made us great. The world will know our name.",
      "GFX_goal_generic_national_unity", 8, 5, [["ante_one_people"], ["ante_city_of_stone"], ["ante_host_of_the_people"]],
      "add_political_power = 100\nadd_stability = 0.10\nadd_war_support = 0.10", filters=P, ai=3)


# ------------------------------------------------------------------ writers
def indent(text, tabs):
    pad = "\t" * tabs
    return "\n".join(pad + line if line.strip() else line for line in text.splitlines())


def esc(s):
    return s.replace('"', "'")


def modifier_block(mods, tabs):
    pad = "\t" * tabs
    return "\n".join(f"{pad}{k} = {v}" for k, v in mods.items())


def write(rel, text, bom=False):
    p = MOD / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8-sig" if bom else "utf-8", newline="\n")


def check_tree():
    ids = {f["id"] for f in F}
    pos = set()
    for f in F:
        for group in f["pre"]:
            for p in group:
                assert p in ids, f"{f['id']}: unknown prerequisite {p}"
        assert (f["x"], f["y"]) not in pos, f"{f['id']}: two focuses at {f['x']},{f['y']}"
        pos.add((f["x"], f["y"]))
        for idea in re.findall(r"add_ideas = (\w+)", f["reward"]):
            assert idea in IDEAS, f"{f['id']}: unknown idea {idea}"


def focus_file():
    out = ["# Generated by tools/content.py - edit that file, not this one.",
           "# Generic focus tree for every people without a tree of its own. The engine crashes when no tree exists.",
           "focus_tree = {", "\tid = ante_generic_focus", "\tcountry = {", "\t\tfactor = 1", "\t}", "\tdefault = yes",
           "\treset_on_civilwar = no", "", "\tinitial_show_position = {", "\t\tfocus = ante_tame_the_land", "\t}", ""]
    for f in F:
        out += ["\tfocus = {", f"\t\tid = {f['id']}", f"\t\ticon = {f['icon']}"]
        for group in f["pre"]:
            out.append("\t\tprerequisite = { " + " ".join(f"focus = {p}" for p in group) + " }")
        out += [f"\t\tx = {f['x']}", f"\t\ty = {f['y']}", "\t\tcost = 10",
                f"\t\tsearch_filters = {{ {f['filters']} }}", "\t\tavailable_if_capitulated = yes"]
        if f["extra"]:
            out.append(indent(f["extra"], 2))
        out += ["\t\tcompletion_reward = {", indent(f["reward"], 3), "\t\t}",
                f"\t\tai_will_do = {{ factor = {f['ai']} }}", "\t}", ""]
    out.append("}")
    return "\n".join(out) + "\n"


def ideas_file():
    out = ["# Generated by tools/content.py", "ideas = {", "\tcountry = {"]
    for key, (name, pic, mods) in IDEAS.items():
        out += [f"\t\t{key} = {{", f"\t\t\tpicture = {pic}", "\t\t\tallowed = { always = no }",
                "\t\t\tremoval_cost = -1", "\t\t\tmodifier = {", modifier_block(mods, 4), "\t\t\t}", "\t\t}"]
    out += ["\t}", "}"]
    return "\n".join(out) + "\n"


def ruling_parties():
    parties = {}
    for fp in (MOD / "history" / "countries").glob("*.txt"):
        m = re.search(r"ruling_party = (\w+)", fp.read_text(encoding="utf-8-sig"))
        if m:
            parties[fp.name[:3]] = m.group(1)
    return parties


def characters_file():
    parties = ruling_parties()
    out = ["# Generated by tools/content.py from tools/data/leaders_509bc.py", "characters = {"]
    for tag, key, name, trait, female, attested, desc in LEADERS:
        assert tag in parties, f"leader for unknown country {tag}"
        assert trait in TRAITS, f"unknown trait {trait}"
        ide = SUB_OVERRIDE.get(tag) or SUB_IDEOLOGY[parties[tag]]
        cid = f"{tag}_{key}"
        out += [f"\t{cid} = {{", f"\t\tname = {cid}"]
        if female:
            out.append("\t\tgender = female")
        out += ["\t\tcountry_leader = {", f"\t\t\tideology = {ide}",
                f"\t\t\ttraits = {{ {trait} }}", '\t\t\texpire = "999.1.1.1"', "\t\t\tid = -1", "\t\t}", "\t}"]
    out.append("}")
    return "\n".join(out) + "\n"


def traits_file():
    out = ["# Generated by tools/content.py", "leader_traits = {"]
    for key, (name, mods) in TRAITS.items():
        out += [f"\t{key} = {{", "\t\trandom = no", modifier_block(mods, 2), "\t\tai_will_do = { factor = 1 }", "\t}"]
    out.append("}")
    return "\n".join(out) + "\n"


def localisation():
    out = ["l_english:"]
    for f in F:
        out += [f' {f["id"]}:0 "{esc(f["name"])}"', f' {f["id"]}_desc:0 "{esc(f["desc"])}"']
    for key, (name, _, _) in IDEAS.items():
        out.append(f' {key}:0 "{esc(name)}"')
    for key, (name, _) in TRAITS.items():
        out.append(f' {key}:0 "{esc(name)}"')
    bonus_from = {"ante_scribes_bonus": "ante_scribes", "ante_mines_bonus": "ante_mines",
                  "ante_great_works_bonus": "ante_great_works", "ante_weapons_bonus": "ante_bronze_and_iron",
                  "ante_drill_bonus": "ante_drill"}
    names = {f["id"]: f["name"] for f in F}
    for bonus, fid in bonus_from.items():
        out.append(f' {bonus}:0 "{esc(names[fid])}"')
    for tag, key, name, trait, female, attested, desc in LEADERS:
        out += [f' {tag}_{key}:0 "{esc(name)}"', f' {tag}_{key}_desc:0 "{esc(desc)}"']
    return "\n".join(out) + "\n"


def main():
    check_tree()
    write("common/national_focus/ante_generic_focus.txt", focus_file())
    write("common/ideas/ante_generic_ideas.txt", ideas_file())
    write("common/characters/ante_leaders.txt", characters_file())
    write("common/country_leader/ante_traits.txt", traits_file())
    write("localisation/english/ante_content_l_english.yml", localisation(), bom=True)
    print(f"written: {len(F)} focuses, {len(IDEAS)} national spirits, {len(LEADERS)} leaders, {len(TRAITS)} traits")


if __name__ == "__main__":
    main()
