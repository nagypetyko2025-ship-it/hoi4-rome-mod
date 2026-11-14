"""Country focus trees (Rome in full, base trees for Macedon, Sparta, Athens, Persia and Carthage).

Used by tools/content.py: define(...) gets the shared helpers and returns
  TREES   tag -> dict(focuses=[...], show=<first focus>, note=<header comment>)
  IDEAS   national spirits granted by these trees   key -> (name, picture, modifiers)
  LOC     extra localisation (faction names, bookmark texts)

Rules: an idea key never equals a focus id (one localisation namespace) - every spirit here ends in _spirit.
Tech bonuses are named after their focus, so the bonus shows the focus name (no extra localisation).
Icons and modifiers are base-game ones (GFX_goal_generic_*, modifiers_documentation.md).
Rome's plan: docs/rome_focus_tree.md. Dates in the texts are BC (the game counts AUC).
"""

import rome_story as RS   # Rome's meters, events and decisions (tools/rome_story.py)

P, I, R, M = "FOCUS_FILTER_POLITICAL", "FOCUS_FILTER_INDUSTRY", "FOCUS_FILTER_RESEARCH", "FOCUS_FILTER_MANPOWER"
COAST = "available = { any_owned_state = { is_coastal = yes } }"
disc, hate = RS.discord, RS.hatred


REALM_N = set()   # thresholds used, for the tooltip localisation


def realm(n):
    """at least n states controlled by us AND our subjects (puppets count). The variable ante_realm_states is
    recomputed at the start and every week (common/on_actions/ante_on_actions.txt, written by content.py)."""
    REALM_N.add(n)
    return (f"custom_trigger_tooltip = {{ tooltip = ANTE_REALM_STATES_{n} "
            f"check_variable = {{ ante_realm_states > {n - 1} }} }}")


def faction(name, *members):
    out = [f"if = {{ limit = {{ is_in_faction = no }} create_faction = {name} }}"]
    for t in members:
        out.append(f"if = {{ limit = {{ is_faction_leader = yes country_exists = {t} NOT = {{ has_war_with = {t} }} "
                   f"{t} = {{ is_in_faction = no is_subject = no }} }} add_to_faction = {t} }}")
    return "\n".join(out)


def puppet(*tags):
    return "\n".join(f"if = {{ limit = {{ country_exists = {t} NOT = {{ has_war_with = {t} }} "
                     f"{t} = {{ is_subject = no is_in_faction = no }} }} puppet = {t} }}" for t in tags)


def submit(*tags):
    """a treaty if it can be made (the people becomes our subject), war if it cannot (round 21): Peti's republican
    treaty focuses gave nothing at all when the target was at war with us (Porsenna's Clusium!), already somebody's
    subject or in a faction - and the republic had no other way to those peoples"""
    out = []
    for t in tags:
        out.append(f"if = {{ limit = {{ country_exists = {t} NOT = {{ has_war_with = {t} }} "
                   f"{t} = {{ is_subject = no is_in_faction = no }} }} puppet = {t} }}\n"
                   f"else_if = {{ limit = {{ country_exists = {t} NOT = {{ has_war_with = {t} }} "
                   f"NOT = {{ {t} = {{ is_subject_of = ROOT }} }} NOT = {{ is_in_faction_with = {t} }} }}\n"
                   f"\tcreate_wargoal = {{ type = annex_everything target = {t} }}\n}}")
    return "\n".join(out)


def claims(*tags):
    return "\n".join(f"every_state = {{ limit = {{ is_owned_by = {t} }} add_claim_by = ROOT }}" for t in tags)


def cores(n=1):
    one = ("random_owned_controlled_state = { limit = { impassable = no NOT = { is_core_of = ROOT } } "
           "add_core_of = ROOT }")
    return "\n".join([one] * n)


def doctrine(fid):
    return f"add_doctrine_cost_reduction = {{ name = {fid} cost_reduction = 0.5 uses = 1 category = land_doctrine }}"


def swap(old, new):
    return f"swap_ideas = {{ remove_idea = {old} add_idea = {new} }}"


def define(focus, build, infra, tech, wargoal):
    TREES, IDEAS, LOC = {}, {}, {}

    def tree(tag, show, note):
        lst = []
        TREES[tag] = dict(focuses=lst, show=show, note=note)

        def f(fid, name, desc, icon, x, y, pre, reward, extra="", ai=1, filters=P, cost=10, avail=""):
            focus(fid, name, desc, "GFX_goal_generic_" + icon, x, y, pre, reward, extra=extra, ai=ai,
                  filters=filters, tree=lst, cost=cost, avail=avail)
        return f

    def idea(key, name, pic, **mods):
        assert key.endswith("_spirit"), key
        IDEAS[key] = (name, "generic_" + pic, mods)

    # ============================================================== ROME (ROM) - 509 BC to 264 BC
    # Two roots, mutually exclusive: the Republic (left, x 0..18) or the King Remains (right, x 21..31).
    # Every branch has a choice between two focuses (mx) that both lead on.
    f = tree("ROM", "ROM_regifugium", "# Rome's focus tree, 509 BC (245 AUC) to the eve of the First Punic War. Plan: docs/rome_focus_tree.md\n"
             "# Left: the Republic. Right: the King Remains (mutually exclusive roots). Pairs of mutually exclusive choices in every branch.")
    # (the Struggle of the Orders itself is a meter now: ROM_discord, tools/rome_story.py)
    idea("ROM_twelve_tables_spirit", "The Law of the Twelve Tables", "constitutional_guarantees",
         stability_factor=-0.03, political_power_gain=0.05)
    idea("ROM_concordia_ordinum_spirit", "Concordia Ordinum", "pp_unity_bonus",
         stability_factor=0.10, political_power_gain=0.15, conscription=0.02)
    idea("ROM_nobilitas_spirit", "The Nobilitas", "central_management",
         political_power_gain=0.25, stability_factor=0.03, army_morale_factor=0.05)
    idea("ROM_rule_of_the_fathers_spirit", "Rule of the Fathers", "political_support", political_power_gain=0.10, stability_factor=-0.03)
    idea("ROM_censors_spirit", "The Census", "central_management", political_power_factor=0.05, conscription=0.01)
    idea("ROM_pax_deorum_spirit", "Pax Deorum", "pp_unity_bonus", stability_factor=0.05, war_support_factor=0.05)
    idea("ROM_ludi_romani_spirit", "Ludi Romani", "political_support", war_support_factor=0.10, stability_factor=0.03)
    idea("ROM_evocatio_spirit", "Evocatio", "morale_bonus", army_attack_factor=0.05, justify_war_goal_time=-0.15)
    idea("ROM_greek_gods_spirit", "Apollo and Asclepius", "research_bonus", research_speed_factor=0.07, monthly_population=0.05)
    idea("ROM_mos_maiorum_spirit", "Mos Maiorum", "pp_unity_bonus", stability_factor=0.07, war_support_factor=0.07)
    idea("ROM_stipendium_spirit", "Stipendium", "manpower_bonus", army_org_factor=0.05, land_reinforce_rate=0.02)
    idea("ROM_manipular_legion_spirit", "The Manipular Legion", "infantry_bonus",
         army_attack_factor=0.10, army_defence_factor=0.05, army_org_factor=0.05)
    idea("ROM_citizen_phalanx_spirit", "The Citizen Phalanx", "fortify_the_borders",
         army_defence_factor=0.15, army_org_factor=0.05, army_speed_factor=-0.05)
    idea("ROM_roman_roads_spirit", "Roman Roads", "supply_line", supply_consumption_factor=-0.10, army_speed_factor=0.05)
    idea("ROM_coloniae_spirit", "Latin Colonies", "agrarian_society", monthly_population=0.10, conscription=0.02)
    idea("ROM_vae_victis_spirit", "Vae Victis - Never Again", "morale_bonus", war_support_factor=0.15, conscription=0.03)
    idea("ROM_servian_wall_spirit", "The Servian Wall", "fortify_the_borders", army_defence_factor=0.10)
    # the kingdom
    idea("ROM_rex_tarquinius_spirit", "Rex Tarquinius", "political_support",
         political_power_gain=0.15, stability_factor=-0.05, conscription=0.02)
    idea("ROM_tyranny_spirit", "Tyranny of Superbus", "political_support",
         political_power_gain=0.25, stability_factor=-0.10, war_support_factor=0.05, conscription=0.03)
    idea("ROM_good_king_spirit", "A King for the People", "pp_unity_bonus",
         political_power_gain=0.10, stability_factor=0.05, research_speed_factor=0.03)
    idea("ROM_celeres_spirit", "The Celeres", "morale_bonus", army_org_factor=0.10, army_attack_factor=0.05)
    idea("ROM_royal_army_spirit", "The Royal Army", "infantry_bonus", army_attack_factor=0.08, army_defence_factor=0.08)
    idea("ROM_etruscan_crafts_spirit", "Etruscan Craftsmen", "economic_increase",
         production_speed_buildings_factor=0.10, research_speed_factor=0.03)
    idea("ROM_regnum_spirit", "Regnum Italiae", "central_management", political_power_gain=0.10, stability_factor=0.10, conscription=0.02)

    def mx(*ids):
        return "mutually_exclusive = { " + " ".join(f"focus = {i}" for i in ids) + " }"

    f("ROM_regifugium", "Regifugium", "Tarquinius Superbus and his house are driven from the city. Rome will never again have a king - but the exiled king has friends in Etruria, and patricians and plebeians now fight over the Republic.",
      "political_pressure", 8, 0, [], "add_political_power = 50\n" + RS.START_REPUBLIC,
      extra=mx("ROM_the_king_remains"), ai=5)
    # --- 1. Res Publica: every step moves the Struggle of the Orders (ROM_discord)
    f("ROM_consuls_and_senate", "Consuls and Senate", "Two magistrates for one year, the fathers of the Senate to advise them.",
      "national_unity", 2, 1, [["ROM_regifugium"]], "add_political_power = 75\nadd_stability = 0.05")
    f("ROM_secession_of_the_plebs", "The Plebs Organise", "The plebeians hold their own assemblies and elect their own leaders. Either they have already marched out to the Sacred Mount - or the discord is so deep that they soon will.",
      "demand_territory", 2, 2, [["ROM_consuls_and_senate"]], "add_manpower = 2000\nadd_political_power = 50",
      avail="OR = {\n\thas_country_flag = ROM_seceded\n\t" + RS.discord_above(55).replace("\n", " ") + "\n}")
    f("ROM_tribunes_of_the_plebs", "Tribunes of the Plebs", "Give way: sacrosanct protectors of the common people, with the power to say: veto. The plebs will be quieter for ever after - and the fathers weaker.",
      "improve_relations", 1, 3, [["ROM_secession_of_the_plebs"]],
      "add_stability = 0.10\nadd_manpower = 2000\nset_country_flag = ROM_tribunes\n" + disc(-20),
      extra=mx("ROM_rule_of_the_fathers"))
    f("ROM_rule_of_the_fathers", "Rule of the Fathers", "Rule them: the patricians close ranks; Appius Claudius and the Senate yield nothing. Power and gold for the state - and a plebs that never stops grumbling.",
      "political_pressure", 3, 3, [["ROM_secession_of_the_plebs"]],
      "add_ideas = ROM_rule_of_the_fathers_spirit\nadd_political_power = 100\nset_country_flag = ROM_fathers_rule\n" + disc(10),
      extra=mx("ROM_tribunes_of_the_plebs"))
    f("ROM_twelve_tables", "The Twelve Tables", "451 BC: the Decemvirs write the law on bronze tablets in the Forum, for every citizen to read.",
      "neutrality_focus", 2, 4, [["ROM_tribunes_of_the_plebs", "ROM_rule_of_the_fathers"]],
      "add_ideas = ROM_twelve_tables_spirit\nadd_political_power = 50\n" + disc(-15))
    f("ROM_lex_canuleia", "Lex Canuleia", "445 BC: patricians and plebeians may marry. One people, slowly.",
      "national_unity", 1, 5, [["ROM_twelve_tables"]], "add_stability = 0.05\nadd_manpower = 3000\n" + disc(-10))
    f("ROM_censors", "The Censors", "Two censors count the citizens, judge their morals and let the public contracts.",
      "political_pressure", 3, 5, [["ROM_twelve_tables"]], "add_ideas = ROM_censors_spirit")
    f("ROM_licinian_sextian_laws", "Licinian-Sextian Laws", "367 BC: one of the two consuls may be a plebeian, and no man may hold more public land than five hundred iugera. A new nobility is born.",
      "political_pressure", 2, 6, [["ROM_lex_canuleia"], ["ROM_censors"]], "add_political_power = 100\nadd_stability = 0.05\n" + disc(-15))
    f("ROM_lex_hortensia", "Lex Hortensia", "287 BC: the votes of the plebs bind the whole people. The struggle of the orders ends in concord - but only where there is concord to seal.",
      "major_alliance", 1, 7, [["ROM_licinian_sextian_laws"]],
      swap("ROM_twelve_tables_spirit", "ROM_concordia_ordinum_spirit") + "\n" + RS.END_DISCORD, extra=mx("ROM_the_nobilitas"),
      avail=RS.discord_below(30))
    f("ROM_the_nobilitas", "The Nobilitas", "The great families, old and new, share the consulships among themselves. The Senate rules Rome - and the plebs are never quite at peace.",
      "political_pressure", 3, 7, [["ROM_licinian_sextian_laws"]],
      swap("ROM_twelve_tables_spirit", "ROM_nobilitas_spirit") + "\n" + disc(5), extra=mx("ROM_lex_hortensia"))
    # --- 2. the gods of Rome
    f("ROM_capitoline_temple", "Temple of Jupiter on the Capitol", "The great temple vowed by the kings is dedicated in the first year of the Republic.",
      "propaganda", 6, 1, [["ROM_regifugium"]], "add_stability = 0.05\nadd_war_support = 0.05")
    f("ROM_sibylline_books", "The Sibylline Books", "The prophetic books, kept by the priests, are consulted in every crisis.",
      "scientific_exchange", 5, 2, [["ROM_capitoline_temple"]], "add_research_slot = 1", ai=3, filters=R)
    f("ROM_pontifex_maximus", "Pontifex Maximus", "The highest priest keeps the calendar, the records and the peace with the gods.",
      "political_pressure", 7, 2, [["ROM_capitoline_temple"]], "add_political_power = 100")
    f("ROM_vestal_virgins", "The Vestal Virgins", "As long as the fire of Vesta burns, Rome stands.",
      "national_unity", 5, 3, [["ROM_sibylline_books"]], "add_ideas = ROM_pax_deorum_spirit")
    f("ROM_ludi_romani", "Ludi Romani", "Races and contests in the valley of the Circus, in honour of Jupiter Best and Greatest.",
      "consumer_goods", 7, 3, [["ROM_pontifex_maximus"]], "add_ideas = ROM_ludi_romani_spirit\n" + disc(-5))
    f("ROM_evocatio", "Evocatio", "Before Veii falls, Camillus calls on Juno of Veii to leave the city and come to Rome. She comes.",
      "propaganda", 6, 4, [["ROM_vestal_virgins"], ["ROM_ludi_romani"]], "add_ideas = ROM_evocatio_spirit")
    f("ROM_greek_gods", "Apollo and Asclepius", "Open the city to the gods of the Greeks: the healer of Epidaurus comes to the Tiber island.",
      "scientific_exchange", 5, 5, [["ROM_evocatio"]], "add_ideas = ROM_greek_gods_spirit", extra=mx("ROM_mos_maiorum"), filters=R)
    f("ROM_mos_maiorum", "Mos Maiorum", "The ways of the ancestors are enough. Foreign rites have no place in Rome.",
      "national_unity", 7, 5, [["ROM_evocatio"]], "add_ideas = ROM_mos_maiorum_spirit", extra=mx("ROM_greek_gods"))
    # --- 3. the birth of the legion
    f("ROM_servian_centuries", "Classes and Centuries", "Every citizen serves according to his property: the hoplite phalanx of Rome.",
      "army_doctrines", 10, 1, [["ROM_regifugium"]], "army_experience = 15\n" + doctrine("ROM_servian_centuries"), filters=M)
    f("ROM_stipendium", "Stipendium", "For the long siege of Veii the soldiers are paid for the first time. The army can stay in the field all winter.",
      "allies_build_infantry", 10, 2, [["ROM_servian_centuries"]], "add_ideas = ROM_stipendium_spirit\nadd_manpower = 2000\nadd_political_power = -25\n" + disc(-8), filters=M)
    f("ROM_camillus_reforms", "Reforms of Camillus", "Long shields, iron-rimmed helmets, the heavy javelin. Now: break up the phalanx, or perfect it?",
      "small_arms", 10, 3, [["ROM_stipendium"]], tech("infantry_weapons", "ROM_camillus_reforms") + "\narmy_experience = 20", filters=R)
    f("ROM_manipular_legion", "The Manipular Legion", "Hastati, principes and triarii in three lines of maniples: an army that bends but does not break.",
      "army_doctrines", 9, 4, [["ROM_camillus_reforms"]], "add_ideas = ROM_manipular_legion_spirit\n" + doctrine("ROM_manipular_legion"),
      extra=mx("ROM_citizen_phalanx"), ai=3, filters=M)
    f("ROM_citizen_phalanx", "The Citizen Phalanx", "The old way, made perfect: a wall of bronze that no charge can break - on level ground.",
      "defence", 11, 4, [["ROM_camillus_reforms"]], "add_ideas = ROM_citizen_phalanx_spirit\n" + doctrine("ROM_citizen_phalanx"),
      extra=mx("ROM_manipular_legion"), filters=M)
    f("ROM_via_appia", "Via Appia", "312 BC: Appius Claudius paves the road from Rome to Capua. The legions march on stone.",
      "construct_infrastructure", 9, 5, [["ROM_manipular_legion", "ROM_citizen_phalanx"]],
      infra() + "\n" + infra() + "\nadd_ideas = ROM_roman_roads_spirit", filters=I)
    f("ROM_aqua_appia", "Aqua Appia", "The first aqueduct brings fresh water to a growing city.",
      "construction", 11, 5, [["ROM_manipular_legion", "ROM_citizen_phalanx"]],
      build("industrial_complex") + "\n" + build("industrial_complex"), filters=I, ai=3)
    f("ROM_coloniae", "Latin Colonies", "Settlers of Rome and Latium hold the conquered land: every colony a garrison, every colonist a soldier.",
      "construct_civilian", 10, 6, [["ROM_via_appia"], ["ROM_aqua_appia"]], "add_ideas = ROM_coloniae_spirit\n" + cores(2) + "\n" + disc(-10), filters=M)
    # --- 4. Latium and Etruria
    f("ROM_horatius_at_the_bridge", "Horatius at the Bridge", "Lars Porsenna marches on Rome; one man holds the Sublician bridge until it falls behind him. (Comes after Porsenna has made his move - at war with Clusium or after his peace.)",
      "defence", 14, 1, [["ROM_regifugium"]], "army_experience = 20\nadd_war_support = 0.10\n"
      "if = { limit = { has_war_with = CLU } add_timed_idea = { idea = ROM_defend_the_city_spirit days = 180 } }",
      avail="OR = {\n\thas_war_with = CLU\n\thas_country_flag = ROM_porsenna_done\n}")
    f("ROM_lake_regillus", "Battle of Lake Regillus", "The Thirty Latin towns take up arms for the exiled Tarquins. THE LATIN LEAGUE WILL DECLARE WAR - but the Dioscuri ride with Rome for half a year. Choose the moment.",
      "major_war", 12, 2, [["ROM_horatius_at_the_bridge"]],
      "army_experience = 25\nadd_war_support = 0.05\nadd_timed_idea = { idea = ROM_dioscuri_spirit days = 180 }\n"
      "if = { limit = { country_exists = LAT LAT = { is_subject = no } NOT = { has_war_with = LAT is_in_faction_with = LAT } }\n"
      "\tLAT = { declare_war_on = { target = ROM type = annex_everything } }\n}",
      avail="has_country_flag = ROM_porsenna_done\nNOT = { has_war_with = CLU }")
    f("ROM_foedus_cassianum", "Foedus Cassianum", "493 BC: peace and alliance with the Latins - one army against the hill peoples.",
      "alliance", 12, 3, [["ROM_lake_regillus"]], "add_political_power = 100\n" + faction("ante_faction_latin_alliance", "LAT")
      + "\ncountry_event = { id = ante_rome.25 days = 365 }",
      extra=mx("ROM_latium_by_the_sword"), avail="NOT = { has_war_with = LAT }")
    f("ROM_latium_by_the_sword", "Latium by the Sword", "No treaty: the Latin towns will be Rome's subjects, not its equals.",
      "territory_or_war", 14, 3, [["ROM_lake_regillus"]], wargoal("LAT") + "\n" + claims("LAT") + "\narmy_experience = 15",
      extra=mx("ROM_foedus_cassianum"))
    f("ROM_aequi_and_volsci", "Against the Aequi and Volsci", "Every summer the hill tribes raid Latium. Every summer Rome marches.",
      "territory_or_war", 16, 2, [["ROM_horatius_at_the_bridge"]], wargoal("VOL") + "\n" + wargoal("AEQ"))
    f("ROM_coriolanus", "Coriolanus", "The proud hero of Corioli, exiled, leads the Volsci against his own city - and turns back at his mother's word.",
      "position_armies", 16, 3, [["ROM_aequi_and_volsci"]], "add_war_support = 0.05\narmy_experience = 15\n" + claims("VOL", "AEQ"))
    f("ROM_siege_of_veii", "The Siege of Veii", "Ten years before the walls of the rich Etruscan city across the Tiber.",
      "major_war", 14, 4, [["ROM_foedus_cassianum", "ROM_latium_by_the_sword", "ROM_coriolanus"]], wargoal("VEI") + "\nadd_war_support = 0.05", ai=2)
    f("ROM_southern_etruria", "The Cities of Southern Etruria", "Caere, Tarquinii and Falerii: after Veii the road to Etruria lies open.",
      "more_territorial_claims", 14, 5, [["ROM_siege_of_veii"]], wargoal("CAE") + "\n" + wargoal("TAR") + "\n" + claims("CAE", "TAR"))
    # --- 5. the Gallic disaster
    f("ROM_battle_of_the_allia", "The Allia", "390 BC: Brennus and the Senones rout the legions; Rome burns, only the Capitol holds. Brennus names his price.",
      "defence", 17, 5, [["ROM_siege_of_veii"]], "add_manpower = 3000\nadd_war_support = 0.05")
    f("ROM_pay_the_gold", "Pay the Gold", "A thousand pounds of gold, weighed on the Gauls' false scales. Vae victis - but the city is saved, and rebuilt in peace.",
      "trade", 16, 6, [["ROM_battle_of_the_allia"]], "add_political_power = -50\nadd_stability = 0.05\n" + build("industrial_complex"),
      extra=mx("ROM_not_with_gold"), filters=I)
    f("ROM_not_with_gold", "Not with Gold, but with Iron", "Camillus arrives as the gold is weighed: Rome buys its freedom with iron. Never again.",
      "major_war", 18, 6, [["ROM_battle_of_the_allia"]], "add_ideas = ROM_vae_victis_spirit\n" + wargoal("SEN"),
      extra=mx("ROM_pay_the_gold"), filters=M)
    f("ROM_servian_wall", "The Servian Wall", "378 BC: eleven kilometres of tufa blocks. No barbarian will take the city again.",
      "fortify_city", 17, 7, [["ROM_pay_the_gold", "ROM_not_with_gold"]], "add_ideas = ROM_servian_wall_spirit\n" + build("arms_factory"), filters=I)
    f("ROM_second_founder", "Camillus, the Second Founder", "The city is rebuilt; the Gauls are driven back. Rome rises again from its ashes.",
      "national_unity", 17, 8, [["ROM_servian_wall"], ["ROM_camillus_reforms"]], "add_stability = 0.10\nadd_political_power = 100")
    # --- 6. master of Italy
    f("ROM_latin_war", "The Latin War", "340-338 BC: the Latins demand equal rights - and lose everything. Rome dissolves the League.",
      "occupy_start_war", 13, 7, [["ROM_southern_etruria"], ["ROM_manipular_legion", "ROM_citizen_phalanx"]],
      wargoal("LAT") + "\n" + claims("LAT"), ai=2)
    f("ROM_samnite_wars", "The Samnite Wars", "Three wars for central Italy: the yoke of the Caudine Forks, and victory at last.",
      "major_war", 13, 8, [["ROM_latin_war"]], wargoal("SAM") + "\n" + claims("SAM") + "\narmy_experience = 25", ai=2)
    f("ROM_sentinum", "Sentinum", "295 BC: Samnites, Gauls, Etruscans and Umbrians against Rome - the Battle of the Nations of Italy.",
      "major_war", 15, 9, [["ROM_samnite_wars"]], wargoal("UMB") + "\n" + wargoal("PIC") + "\nadd_war_support = 0.05")
    f("ROM_tarentum_and_pyrrhus", "Tarentum and Pyrrhus", "Tarentum calls the King of Epirus and his elephants. Rome loses battles - and wins the war.",
      "territory_or_war", 11, 9, [["ROM_samnite_wars"]], wargoal("TAS") + "\n" + claims("TAS", "MES", "KRO"),
      extra=mx("ROM_treaty_with_tarentum"))
    f("ROM_treaty_with_tarentum", "Treaty with Tarentum", "The richest Greek city of Italy is worth more as a friend: its fleet, its coin, its harbour - under Rome.",
      "improve_relations", 13, 9, [["ROM_samnite_wars"]], puppet("TAS") + "\nadd_political_power = 50",
      extra=mx("ROM_tarentum_and_pyrrhus"))
    f("ROM_italia", "Italia", "From the Arno to the Strait, the peoples of Italy are Rome's allies - or Rome's. Where next: the sea, or the north?",
      "national_unity", 13, 10, [["ROM_sentinum"], ["ROM_tarentum_and_pyrrhus", "ROM_treaty_with_tarentum"]],
      "add_political_power = 150\nadd_stability = 0.10\nadd_war_support = 0.10\n" + cores(3), ai=3)
    f("ROM_towards_sicily", "Towards Sicily", "264 BC: the Mamertines of Messana call for help. Across the Strait waits Carthage.",
      "occupy_states_coastal", 12, 11, [["ROM_italia"]],
      claims("ZAN", "SYR") + "\n" + build("dockyard", "is_coastal = yes") + "\nnavy_experience = 25", extra=COAST)
    f("ROM_cisalpine_gaul", "Gallia Cisalpina", "Avenge the Allia for ever: the plain of the Po, from the Senones to the Insubres, becomes Roman land.",
      "more_territorial_claims", 14, 11, [["ROM_italia"]],
      wargoal("INS") + "\n" + wargoal("SEN") + "\n" + wargoal("LIG") + "\n" + wargoal("FEL") + "\n" + wargoal("VEN") + "\n" + claims("INS", "FEL", "VEN", "LIG", "SEN") +
      "\narmy_experience = 20")

    # --- Italy for the Republic: what the kingdom conquers, the Republic wins by treaty, surrender or war
    f("ROM_civitas_sine_suffragio", "Civitas sine Suffragio", "The Sabines and the Marsi become Romans - citizens without the vote, soldiers with the duty to serve.",
      "improve_relations", 16, 4, [["ROM_coriolanus"]], submit("SAB", "MAR") + "\nadd_political_power = -50")
    f("ROM_etruscan_truces", "The Forty-Year Truces", "After Veii the northern Etruscan cities buy peace from Rome - and end as its allies.",
      "alliance", 12, 6, [["ROM_southern_etruria"]], submit("CLU", "VLT", "ARR") + "\nadd_political_power = -100")
    f("ROM_deditio_of_capua", "The Surrender of Capua", "343 BC: beset by the Samnites, Capua gives itself and all it has into the hands of the Roman people.",
      "alliance", 11, 8, [["ROM_latin_war"]], submit("CAP", "CUM") + "\nadd_war_support = 0.05")
    f("ROM_apulian_allies", "The Apulian Allies", "Teanum Apulum and the Daunians stand with Rome against the Samnites, from behind.",
      "alliance", 9, 10, [["ROM_samnite_wars"]], submit("DAU", "PEU") + "\nadd_political_power = -50")
    f("ROM_lucania_and_bruttium", "Lucania and Bruttium", "The forests of the south and the Greek towns of the coast: the last of Italy to bow.",
      "territory_or_war", 11, 10, [["ROM_tarentum_and_pyrrhus", "ROM_treaty_with_tarentum"]],
      wargoal("OEN") + "\n" + wargoal("MES") + "\n" + wargoal("MET") + "\n" + wargoal("LOK") + "\n" + wargoal("RHE") + "\n" +
      wargoal("POS") + "\n" + wargoal("KRO") + "\n" + claims("OEN", "MES", "MET", "LOK", "RHE", "POS", "KRO"), ai=2)

    # --- 7. the King Remains (right side): Tarquinius crushes the conspiracy of Brutus and Collatinus
    f("ROM_the_king_remains", "The King Remains", "The conspiracy of Brutus and Collatinus is betrayed. Tarquinius Superbus stays on the throne, and Rome stays a kingdom - a kingdom whose people hate their king. Keep the hatred down, or Rome will rise.",
      "political_pressure", 26, 0, [],
      "set_politics = { ruling_party = neutrality elections_allowed = no }\n"
      "set_popularities = { democratic = 15 fascism = 0 communism = 0 neutrality = 85 }\n"
      "promote_character = ROM_tarquinius\n"
      "add_ideas = ROM_rex_tarquinius_spirit\nadd_political_power = 50\n" + RS.START_KINGDOM,
      extra=mx("ROM_regifugium"), ai=1)
    f("ROM_purge_the_conspirators", "Purge the Conspirators", "The sons of Brutus, the Vitellii, the Aquilii: every house that plotted pays with blood or exile.",
      "political_pressure", 23, 1, [["ROM_the_king_remains"]], "add_political_power = 100\nadd_stability = -0.03\n" + hate(5))
    f("ROM_tyranny_of_superbus", "Tyranny of Superbus", "The king rules without the Senate, judges without counsel and takes what he likes. Fear is enough.",
      "political_pressure", 22, 2, [["ROM_purge_the_conspirators"]], swap("ROM_rex_tarquinius_spirit", "ROM_tyranny_spirit") + "\nset_country_flag = ROM_tyranny\n" + hate(5),
      extra=mx("ROM_a_king_for_the_people"))
    f("ROM_a_king_for_the_people", "A King for the People", "Like Servius Tullius before him, the king takes the side of the poor against the great houses.",
      "improve_relations", 24, 2, [["ROM_purge_the_conspirators"]], swap("ROM_rex_tarquinius_spirit", "ROM_good_king_spirit") + "\nadd_stability = 0.05\nset_country_flag = ROM_good_king\n" + hate(-5),
      extra=mx("ROM_tyranny_of_superbus"))
    f("ROM_the_celeres", "The Celeres", "Three hundred horsemen, the king's own guard since Romulus.",
      "cavalry", 23, 3, [["ROM_tyranny_of_superbus", "ROM_a_king_for_the_people"]], "add_ideas = ROM_celeres_spirit\narmy_experience = 15", filters=M)
    f("ROM_cloaca_maxima", "Cloaca Maxima", "The great sewer drains the Forum valley: the works of the Tarquins go on, built by the people's labour.",
      "construction", 26, 1, [["ROM_the_king_remains"]], build("industrial_complex") + "\n" + infra(), filters=I, ai=3)
    f("ROM_books_of_the_sibyl", "The Books of the Sibyl", "An old woman offers the king nine books, then six, then three, for the same price. Tarquinius pays.",
      "scientific_exchange", 26, 2, [["ROM_cloaca_maxima"]], "add_research_slot = 1", filters=R, ai=3)
    f("ROM_etruscan_craftsmen", "Etruscan Craftsmen", "Builders, smiths and painters from Etruria work for the Etruscan king of Rome.",
      "construct_civ_factory", 26, 3, [["ROM_books_of_the_sibyl"]], "add_ideas = ROM_etruscan_crafts_spirit\n" + build("arms_factory"), filters=I)
    f("ROM_head_of_the_latin_league", "Head of the Latin League", "The kings of Rome lead the festival on the Alban Mount: the Latins follow Rome - or else.",
      "alliance", 29, 1, [["ROM_the_king_remains"]], submit("LAT") + "\nadd_political_power = 50")
    f("ROM_stratagem_of_gabii", "The Stratagem of Gabii", "Sextus, the king's son, takes Gabii by treachery; Suessa Pometia of the Volsci falls to the king's army.",
      "position_armies", 29, 2, [["ROM_head_of_the_latin_league"]], wargoal("VOL") + "\n" + wargoal("AEQ") + "\narmy_experience = 15\n" + hate(-5))
    # the Etruscan cities next door first (Veii borders Rome), Clusium only when Rome reaches it (it lies far
    # north: a war goal on a country we could not reach locked the tree up to round 16)
    f("ROM_the_twelve_cities", "The Twelve Cities", "Veii, Caere and Tarquinii, the Etruscan cities nearest Rome, must bow to the Etruscan king of Rome.",
      "more_territorial_claims", 29, 3, [["ROM_stratagem_of_gabii"]],
      claims("VEI", "CAE", "TAR") + "\n" + wargoal("VEI") + "\n" + wargoal("CAE") + "\n" + wargoal("TAR") + "\nadd_war_support = 0.05\n" + hate(-10), ai=2)
    f("ROM_royal_army", "The Royal Army", "The king's phalanx, his Celeres and the levies of Latium and Etruria under one command.",
      "army_doctrines", 23, 4, [["ROM_the_celeres"]], "add_ideas = ROM_royal_army_spirit\n" + doctrine("ROM_royal_army"), filters=M)
    f("ROM_royal_roads", "The King's Roads", "Roads radiate from Rome to the subject towns, so that the king's army is everywhere in days.",
      "construct_infrastructure", 26, 4, [["ROM_etruscan_craftsmen"]], infra() + "\n" + infra() + "\nadd_ideas = ROM_roman_roads_spirit", filters=I)
    f("ROM_king_of_the_etruscans", "Lucumo of Etruria", "Now that our borders reach him, Porsenna of Clusium stands between the king of Rome and the crown of all Etruria.",
      "major_war", 29, 4, [["ROM_the_twelve_cities"]], wargoal("CLU") + "\n" + claims("CLU") + "\n" + cores(1) + "\n" + hate(-10), ai=2)
    f("ROM_sabine_wars", "War with the Sabines", "As Tarquinius Priscus did before him, the king marches up the Anio against the Sabines and the Marsi.",
      "territory_or_war", 31, 3, [["ROM_stratagem_of_gabii"]], wargoal("SAB") + "\n" + wargoal("MAR") + "\n" + claims("SAB", "MAR") + "\narmy_experience = 10", ai=2)
    f("ROM_northern_etruria", "Northern Etruria", "Volaterrae on its rock and Arretium of the bronze-smiths: the rest of the twelve cities.",
      "more_territorial_claims", 29, 5, [["ROM_king_of_the_etruscans"]], wargoal("VLT") + "\n" + wargoal("ARR") + "\n" + claims("VLT", "ARR"), ai=2)
    f("ROM_regnum_italiae", "Regnum Italiae", "A kingdom, not a city: Latins, Etruscans and Italians under one crown.",
      "national_unity", 26, 5, [["ROM_royal_army"], ["ROM_royal_roads"], ["ROM_the_twelve_cities"]],
      "add_ideas = ROM_regnum_spirit\n" + cores(2) + "\nadd_political_power = 100\n" + hate(-10), ai=3)
    f("ROM_the_samnite_mountains", "The Samnite Mountains", "The hill peoples of the south have never had a master.",
      "major_war", 24, 6, [["ROM_regnum_italiae"]], wargoal("SAM") + "\n" + wargoal("CAP") + "\n" + claims("SAM", "CAP") + "\narmy_experience = 25", ai=2)
    f("ROM_magna_graecia", "Magna Graecia", "Kyme, Taras, Kroton: the rich Greek cities of the south will pay tribute to the king.",
      "occupy_states_coastal", 28, 6, [["ROM_regnum_italiae"]], wargoal("CUM") + "\n" + wargoal("POS") + "\n" + wargoal("TAS") + "\n" + claims("TAS", "KRO", "CUM", "POS"))
    f("ROM_umbria_and_picenum", "Umbria and Picenum", "The hill towns of Umbria and the Picentes by the Adriatic: the king's road to the other sea.",
      "territory_or_war", 31, 6, [["ROM_regnum_italiae"]], wargoal("UMB") + "\n" + wargoal("PIC") + "\n" + claims("UMB", "PIC"), ai=2)
    f("ROM_apulia", "The Plains of Apulia", "Horses, wool and grain: Daunians, Peucetians and Messapians will pay the king's tribute.",
      "occupy_start_war", 22, 7, [["ROM_the_samnite_mountains"]], wargoal("DAU") + "\n" + wargoal("PEU") + "\n" + wargoal("MES") + "\n" + claims("DAU", "PEU", "MES"), ai=2)
    f("ROM_bruttium", "The Forests of Bruttium", "Oenotrians in the hills, Greeks on the coast, down to the Strait of Rhegion.",
      "occupy_states_coastal", 28, 7, [["ROM_magna_graecia"]],
      wargoal("OEN") + "\n" + wargoal("MET") + "\n" + wargoal("LOK") + "\n" + wargoal("RHE") + "\n" + wargoal("KRO") + "\n" + claims("OEN", "MET", "LOK", "RHE", "KRO"), ai=2)
    f("ROM_across_the_strait", "Across the Strait", "Zankle and Syracuse look across the water at the new king of Italy.",
      "occupy_states_coastal", 24, 9, [["ROM_king_of_italy"]],
      wargoal("ZAN") + "\n" + claims("ZAN", "SYR") + "\n" + build("dockyard", "is_coastal = yes") + "\nnavy_experience = 25",
      extra=COAST)
    f("ROM_kingdom_of_the_po", "Kingdom of the Po", "Etruscan Felsina, the Veneti, the Ligurians and the Gauls of the plain: the north joins the kingdom.",
      "more_territorial_claims", 28, 9, [["ROM_king_of_italy"]],
      wargoal("FEL") + "\n" + wargoal("SEN") + "\n" + wargoal("INS") + "\n" + wargoal("LIG") + "\n" + wargoal("VEN") + "\n" + claims("FEL", "VEN", "INS", "LIG", "SEN"),
      )
    f("ROM_king_of_italy", "King of Italy", "From the Alps to the Strait one king, one army, one law. The Republic is a dream nobody remembers.",
      "national_unity", 26, 8, [["ROM_the_samnite_mountains"], ["ROM_magna_graecia"]],
      "add_political_power = 150\nadd_stability = 0.10\nadd_war_support = 0.10\n" + cores(3) + "\nadd_research_slot = 1", ai=3)

    # --- 8. the hated king (only after The King Remains, x 35..37): every step lowers ROM_hatred; the
    #     last one needs it below 30. Crushing the riots is quick but leaves blood in the Forum (more plots).
    idea("ROM_loyal_subjects_spirit", "Loyal Subjects of the King", "pp_unity_bonus", stability_factor=0.05, conscription=0.01)
    f("ROM_royal_amnesty", "Amnesty for the Exiles", "Families fled to Veii, Gabii and Cumae. The king's heralds promise: come home, and nothing will be done to you.",
      "improve_relations", 35, 1, [["ROM_the_king_remains"]], "add_political_power = -50\nadd_manpower = 1000\n" + hate(-10))
    f("ROM_grain_from_cumae", "Grain from Cumae", "Empty fields, empty granaries: the king buys grain from the Greeks so the city does not starve. Aristodemus of Cumae sells - to friends.",
      "trade", 37, 1, [["ROM_the_king_remains"]], "add_stability = 0.05\nadd_political_power = -25\n" + hate(-8), filters=I,
      avail="NOT = { has_war_with = CUM }")
    f("ROM_call_back_the_settlers", "Call Back the Settlers", "Land and tax freedom for every family that returns to Rome.",
      "construct_civilian", 35, 2, [["ROM_royal_amnesty"], ["ROM_grain_from_cumae"]], "add_manpower = 1500\n" + hate(-12), cost=15)
    f("ROM_crush_the_riots", "Crush the Riots", "The Celeres clear the Forum. Order is restored at once - and remembered: the plots will come thicker.",
      "defence", 35, 3, [["ROM_call_back_the_settlers"]],
      "add_war_support = -0.05\nset_country_flag = ROM_blood_in_the_forum\n" + hate(-20),
      extra=mx("ROM_hear_the_people"))
    f("ROM_hear_the_people", "Hear the People", "The king sits in judgement in the Forum himself and hears every complaint - at a price to his pride and his treasury. The anger fades slowly, week by week.",
      "improve_relations", 37, 3, [["ROM_call_back_the_settlers"]],
      "add_political_power = -75\nadd_stability = 0.05\nset_country_flag = ROM_king_listens\n" + hate(-15),
      extra=mx("ROM_crush_the_riots"), cost=15)
    f("ROM_a_loyal_rome", "A Loyal Rome", "A generation grows up that knows no other ruler. The hatred fades into habit, and habit into loyalty.",
      "national_unity", 36, 4, [["ROM_crush_the_riots", "ROM_hear_the_people"]],
      "add_ideas = ROM_loyal_subjects_spirit\nadd_stability = 0.05\n" + RS.END_HATRED, cost=20, avail=RS.hatred_below(30))

    # --- 9. the economy of Rome (both roads, x 39..43)
    idea("ROM_coinage_spirit", "Aes Signatum", "economic_increase", production_speed_buildings_factor=0.10, political_power_gain=0.05)
    idea("ROM_ager_publicus_spirit", "Ager Publicus", "agrarian_society", monthly_population=0.10, conscription=0.01)
    idea("ROM_juno_moneta_spirit", "The Mint of Juno Moneta", "economic_increase",
         production_speed_buildings_factor=0.10, production_factory_max_efficiency_factor=0.05)
    root = [["ROM_regifugium", "ROM_the_king_remains"]]
    f("ROM_forum_boarium", "Forum Boarium", "The cattle market by the Tiber ford, where Latins, Etruscans and Greeks trade.",
      "construct_civ_factory", 41, 1, root, build("industrial_complex"), filters=I, ai=4)
    f("ROM_via_salaria", "Via Salaria", "The salt road: from the pans at the mouth of the Tiber up into the Sabine hills.",
      "construct_infrastructure", 39, 2, [["ROM_forum_boarium"]], infra() + "\n" + infra(), filters=I, ai=2)
    f("ROM_salt_pans", "The Salt Pans", "Whoever holds the salt of the Tiber mouth holds the trade of central Italy.",
      "production", 41, 2, [["ROM_forum_boarium"]], build("industrial_complex"), filters=I, ai=3)
    f("ROM_tiber_harbour", "Harbour on the Tiber", "Wharves below the Aventine and a port at the river mouth.",
      "construct_naval_dockyard", 43, 2, [["ROM_forum_boarium"]], build("dockyard", "is_coastal = yes"), extra=COAST, filters=I)
    f("ROM_aes_signatum", "Aes Signatum", "Bronze bars stamped by the state: the first money of Rome.",
      "trade", 40, 3, [["ROM_via_salaria", "ROM_salt_pans"]], "add_ideas = ROM_coinage_spirit", filters=I, cost=15)
    f("ROM_ager_publicus", "Ager Publicus", "Conquered land belongs to the Roman people - to be settled, leased or grazed.",
      "construct_civilian", 42, 3, [["ROM_salt_pans", "ROM_tiber_harbour"]], "add_ideas = ROM_ager_publicus_spirit",
      filters=I, avail=realm(3))
    f("ROM_smiths_of_rome", "Smiths of the Argiletum", "Helmets, spearheads and the iron-shod pilum by the thousand.",
      "construct_mil_factory", 40, 4, [["ROM_aes_signatum"]], build("arms_factory") + "\n" + build("arms_factory"), filters=I, ai=4, cost=15)
    f("ROM_juno_moneta", "The Mint of Juno Moneta", "Silver coins struck in the temple of Juno the Warner on the Capitol.",
      "production", 42, 4, [["ROM_aes_signatum"], ["ROM_ager_publicus"]], "add_ideas = ROM_juno_moneta_spirit",
      filters=I, cost=15, avail=realm(6))
    f("ROM_great_public_works", "Great Public Works", "Temples, basilicas, walls and roads: the censors spend the spoils of war on the city.",
      "construction2", 41, 5, [["ROM_smiths_of_rome"], ["ROM_juno_moneta"]],
      build("industrial_complex") + "\n" + build("industrial_complex") + "\n" + build("arms_factory"),
      filters=I, ai=3, cost=20, avail=realm(9))

    # ============================================================== ATHENS (ATH)
    f = tree("ATH", "ATH_reforms_of_cleisthenes", "# Athens, from the reforms of Cleisthenes to the school of Hellas (base tree)")
    idea("ATH_isonomia_spirit", "Isonomia", "constitutional_guarantees", political_power_gain=0.10, stability_factor=0.05)
    idea("ATH_thalassocracy_spirit", "Athenian Thalassocracy", "navy_bonus",
         production_speed_dockyard_factor=0.15, naval_damage_factor=0.10, navy_org_factor=0.05)
    idea("ATH_marathonomachai_spirit", "The Men of Marathon", "morale_bonus", army_defence_factor=0.10, army_morale_factor=0.05)
    idea("ATH_long_walls_spirit", "The Long Walls", "fortify_the_borders", army_defence_factor=0.10, stability_factor=0.05)
    idea("ATH_school_of_hellas_spirit", "The School of Hellas", "research_bonus", research_speed_factor=0.10, political_power_factor=0.10)
    f("ATH_reforms_of_cleisthenes", "Reforms of Cleisthenes", "508 BC: the tyrants are gone; Cleisthenes gives power to the people of Attica.",
      "political_pressure", 4, 0, [], "add_ideas = ATH_isonomia_spirit\nadd_political_power = 50")
    f("ATH_ten_tribes", "The Ten Tribes", "Every deme of city, coast and inland mixed into ten new tribes: the old clans lose their grip.",
      "national_unity", 2, 1, [["ATH_reforms_of_cleisthenes"]], "add_stability = 0.05\nadd_manpower = 1500")
    f("ATH_ostracism", "Ostracism", "Once a year the people may write a name on a potsherd - and send a man into exile for ten years.",
      "political_pressure", 2, 2, [["ATH_ten_tribes"]], "add_political_power = 100")
    f("ATH_strategoi", "The Ten Strategoi", "Each tribe elects a general; the generals answer to the Assembly.",
      "army_doctrines", 2, 3, [["ATH_ostracism"]], "army_experience = 15\n" + doctrine("ATH_strategoi"), filters=M)
    f("ATH_age_of_pericles", "The Age of Pericles", "The first citizen of a democracy at the height of its power.",
      "political_pressure", 2, 4, [["ATH_strategoi"]], "add_political_power = 100\nadd_stability = 0.05")
    f("ATH_laurion_silver", "Silver of Laurion", "A new, rich vein is struck in the mines of Laurion.",
      "production", 4, 1, [["ATH_reforms_of_cleisthenes"]], build("industrial_complex") + "\nadd_political_power = 25", filters=I, ai=3)
    f("ATH_piraeus", "The Piraeus", "Three natural harbours are walled into the port of Athens.",
      "construct_naval_dockyard", 4, 2, [["ATH_laurion_silver"]], build("dockyard", "is_coastal = yes"), extra=COAST, filters=I, ai=3)
    f("ATH_themistocles_fleet", "The Fleet of Themistocles", "The silver of Laurion is not shared out: it builds two hundred triremes.",
      "build_navy", 4, 3, [["ATH_piraeus"]], "add_ideas = ATH_thalassocracy_spirit\nnavy_experience = 25\n" + build("dockyard", "is_coastal = yes"),
      extra=COAST, filters=I, ai=3)
    f("ATH_war_with_chalcis", "War with Chalcis", "506 BC: the Boeotians and Chalcidians invade Attica and are beaten on one day.",
      "territory_or_war", 6, 1, [["ATH_reforms_of_cleisthenes"]], wargoal("EUB") + "\narmy_experience = 15")
    f("ATH_cleruchies", "Cleruchies", "Athenian citizens settle the conquered land and keep their citizenship.",
      "construct_civilian", 6, 2, [["ATH_war_with_chalcis"]], cores(1) + "\nadd_manpower = 1000", filters=M)
    f("ATH_aid_the_ionians", "Aid the Ionians", "Twenty ships sail to help the Greeks of Asia against the Great King. The beginning of evils.",
      "attack_allies", 8, 2, [["ATH_war_with_chalcis"]], "add_war_support = 0.10\nnavy_experience = 10")
    f("ATH_marathon", "Marathon", "490 BC: the hoplites of Athens run at the Persian line - and win.",
      "defence", 7, 3, [["ATH_cleruchies", "ATH_aid_the_ionians"]], "add_ideas = ATH_marathonomachai_spirit\narmy_experience = 20", filters=M)
    f("ATH_delian_league", "The Delian League", "The islands and the cities of the coast swear on sunken iron: a league against Persia, led by Athens.",
      "major_alliance", 5, 4, [["ATH_themistocles_fleet"], ["ATH_marathon"]],
      faction("ante_faction_delian_league", "NAX", "RHO", "CHK", "THS", "BYZ", "EUB"), ai=2)
    f("ATH_parthenon", "The Parthenon", "Marble from Pentelicus and gold of the League: a temple for the Maiden of Athens.",
      "construction2", 3, 5, [["ATH_age_of_pericles"]], build("industrial_complex") + "\nadd_stability = 0.05", filters=I)
    f("ATH_long_walls", "The Long Walls", "City and harbour joined by walls: Athens becomes an island that no army can starve.",
      "fortify_city", 5, 5, [["ATH_delian_league"]], "add_ideas = ATH_long_walls_spirit", filters=I)
    f("ATH_school_of_hellas", "The School of Hellas", "Philosophers, poets, historians and builders: all Greece learns from Athens.",
      "scientific_exchange", 4, 6, [["ATH_parthenon"], ["ATH_long_walls"]], "add_ideas = ATH_school_of_hellas_spirit\nadd_research_slot = 1",
      filters=R, ai=3)

    # ============================================================== SPARTA (LAK)
    f = tree("LAK", "LAK_lycurgan_order", "# Sparta, the Lycurgan order and the hegemony of the Peloponnese (base tree)")
    idea("LAK_agoge_spirit", "The Agoge", "infantry_bonus", army_org_factor=0.10, army_morale_factor=0.10)
    idea("LAK_spartiates_spirit", "Homoioi - the Equals", "morale_bonus", army_attack_factor=0.10, army_defence_factor=0.05)
    idea("LAK_helot_labour_spirit", "Helot Labour", "agrarian_society", production_speed_buildings_factor=0.10, stability_factor=-0.05)
    idea("LAK_krypteia_spirit", "The Krypteia", "fortify_the_borders", stability_factor=0.10)
    idea("LAK_molon_labe_spirit", "Molon Labe", "fortify_the_borders", army_defence_factor=0.15, surrender_limit=0.15, war_support_factor=0.05)
    f("LAK_lycurgan_order", "The Lycurgan Order", "The laws of Lycurgus: iron coins, common messes, and every citizen a soldier.",
      "political_pressure", 4, 0, [], "add_political_power = 50\nadd_war_support = 0.05")
    f("LAK_agoge", "The Agoge", "From the age of seven every Spartan boy is raised by the state - hungry, hardened, obedient.",
      "army_doctrines", 2, 1, [["LAK_lycurgan_order"]], "add_ideas = LAK_agoge_spirit\narmy_experience = 15", filters=M, ai=3)
    f("LAK_spartiates", "The Equals", "Few, but each one worth many: the Spartiates in their scarlet cloaks.",
      "special_forces", 2, 2, [["LAK_agoge"]], "add_ideas = LAK_spartiates_spirit\n" + doctrine("LAK_spartiates"), filters=M)
    f("LAK_two_kings", "Two Kings", "The Agiad and the Eurypontid kings: one leads the army, one stays at home.",
      "national_unity", 4, 1, [["LAK_lycurgan_order"]], "add_political_power = 75\nadd_stability = 0.05")
    f("LAK_ephors", "The Ephors", "Five overseers, elected every year, watch over the kings themselves.",
      "political_pressure", 4, 2, [["LAK_two_kings"]], "add_political_power = 100")
    f("LAK_helots", "The Helots", "The serfs of Laconia and Messenia till the land so that the Spartiates need do nothing but train.",
      "construct_civilian", 6, 1, [["LAK_lycurgan_order"]],
      "add_ideas = LAK_helot_labour_spirit\n" + build("industrial_complex"), filters=I, ai=3)
    f("LAK_krypteia", "The Krypteia", "Every autumn the ephors declare war on the helots, and the young men hunt the bravest of them.",
      "intelligence_exchange", 6, 2, [["LAK_helots"]], "add_ideas = LAK_krypteia_spirit")
    f("LAK_war_with_argos", "War with Argos", "494 BC: at Sepeia Cleomenes destroys the army of Argos, the old rival.",
      "major_war", 2, 3, [["LAK_spartiates"]], wargoal("AGS") + "\narmy_experience = 20")
    f("LAK_peloponnesian_league", "The Peloponnesian League", "Corinth, Arkadia, Elis and the Achaeans swear to have the same friends and enemies as Sparta.",
      "major_alliance", 4, 3, [["LAK_ephors"], ["LAK_spartiates"]],
      faction("ante_faction_peloponnesian_league", "KRN", "ARK", "EIS", "AKH", "EPI"), ai=3)
    f("LAK_messenia", "Hold Messenia", "The fertile land beyond Taygetus is Sparta's - and must be held by force.",
      "fortify_city", 6, 3, [["LAK_krypteia"]], cores(1) + "\nadd_manpower = 1500", filters=M)
    f("LAK_thermopylae", "Molon Labe", "Come and take them. A Spartan does not surrender.",
      "defence", 2, 4, [["LAK_war_with_argos"]], "add_ideas = LAK_molon_labe_spirit", filters=M)
    f("LAK_against_athens", "Against Athens", "The walls of Athens grow, and so does its fleet. Sparta cannot allow a second hegemon.",
      "territory_or_war", 5, 4, [["LAK_peloponnesian_league"]], wargoal("ATH") + "\n" + claims("ATH") + "\nadd_war_support = 0.05")
    f("LAK_hegemon_of_hellas", "Hegemon of Hellas", "All Greece looks to Sparta to lead it in war.",
      "national_unity", 4, 5, [["LAK_thermopylae"], ["LAK_against_athens", "LAK_messenia"]],
      "add_political_power = 100\nadd_stability = 0.10\narmy_experience = 25", ai=3)

    # ============================================================== MACEDON (MKD)
    f = tree("MKD", "MKD_argead_house", "# Macedon, from the Argead kings to the army of Philip (base tree)")
    idea("MKD_hetairoi_spirit", "Hetairoi - the Companions", "morale_bonus",
         cavalry_attack_factor=0.15, army_attack_factor=0.05)
    idea("MKD_pezhetairoi_spirit", "Pezhetairoi - the Foot Companions", "infantry_bonus", army_defence_factor=0.10, army_org_factor=0.05)
    idea("MKD_sarissa_spirit", "The Sarissa Phalanx", "infantry_bonus", army_attack_factor=0.10, army_defence_factor=0.05)
    idea("MKD_philhellene_spirit", "Philhellene Court", "research_bonus", research_speed_factor=0.05, political_power_factor=0.05)
    f("MKD_argead_house", "The Argead House", "Descendants of Herakles, say the kings of Aigai, and Greeks - whatever the southerners say.",
      "political_pressure", 4, 0, [], "add_political_power = 50\nadd_stability = 0.05")
    f("MKD_earth_and_water", "Earth and Water", "Amyntas gives earth and water to the envoys of Darius: Macedon bends, and survives.",
      "neutrality_focus", 2, 1, [["MKD_argead_house"]], "add_political_power = 100\nadd_stability = 0.05")
    f("MKD_philhellene", "Alexander the Philhellene", "A Macedonian king runs at Olympia: the court opens to Greek poets and craftsmen.",
      "scientific_exchange", 2, 2, [["MKD_earth_and_water"]], "add_ideas = MKD_philhellene_spirit", filters=R)
    f("MKD_hetairoi", "The Companions", "The nobles of Macedon ride beside their king - the finest heavy horse of the Greek world.",
      "cavalry", 4, 1, [["MKD_argead_house"]], "add_ideas = MKD_hetairoi_spirit\narmy_experience = 10", filters=M, ai=3)
    f("MKD_upper_macedonia", "Upper Macedonia", "The highland cantons and Paeonia must answer to Aigai.",
      "territory_or_war", 4, 2, [["MKD_hetairoi"]], wargoal("PAE") + "\n" + claims("PAE"))
    f("MKD_timber_and_silver", "Timber and Silver", "Ship timber for the fleets of the south and silver from the Thracian hills.",
      "production", 6, 1, [["MKD_argead_house"]], build("industrial_complex") + "\nadd_political_power = 25", filters=I, ai=3)
    f("MKD_mines_of_pangaion", "Mines of Mount Pangaion", "A thousand talents a year from the gold of Pangaion.",
      "construct_mil_factory", 6, 2, [["MKD_timber_and_silver"]], build("arms_factory") + "\n" + build("industrial_complex"), filters=I, ai=3)
    f("MKD_pezhetairoi", "The Foot Companions", "Shepherds become soldiers, honoured like the nobles.",
      "allies_build_infantry", 3, 3, [["MKD_upper_macedonia"]], "add_ideas = MKD_pezhetairoi_spirit\nadd_manpower = 2000", filters=M)
    f("MKD_chalkidike", "The Chalkidike", "The Greek cities of the three peninsulas block the sea. They must be ours.",
      "occupy_states_coastal", 5, 3, [["MKD_upper_macedonia", "MKD_mines_of_pangaion"]], wargoal("CHK") + "\n" + claims("CHK", "THS"))
    f("MKD_sarissa", "The Sarissa", "Pikes of eighteen feet, sixteen ranks deep: a hedge of iron.",
      "small_arms", 3, 4, [["MKD_pezhetairoi"]], "add_ideas = MKD_sarissa_spirit\n" + tech("infantry_weapons", "MKD_sarissa"), filters=R, ai=3)
    f("MKD_thessalian_alliance", "Archon of Thessaly", "The horse lords of Thessaly choose the king of Macedon as their leader.",
      "alliance", 5, 4, [["MKD_chalkidike"]], faction("ante_faction_macedonian_alliance", "THL"))
    f("MKD_hammer_and_anvil", "Hammer and Anvil", "The phalanx holds the enemy, the Companions break him.",
      "army_doctrines", 4, 5, [["MKD_sarissa"], ["MKD_thessalian_alliance"]], doctrine("MKD_hammer_and_anvil") + "\narmy_experience = 30", filters=M)
    f("MKD_hegemon_of_the_greeks", "Hegemon of the Greeks", "Athens and Thebes must learn who leads Greece now.",
      "major_war", 4, 6, [["MKD_hammer_and_anvil"]], wargoal("THB") + "\n" + wargoal("ATH") + "\nadd_war_support = 0.10")

    # ============================================================== PERSIA (PRS)
    f = tree("PRS", "PRS_king_of_kings", "# The Persian Empire of Darius I (base tree)")
    idea("PRS_satrapies_spirit", "The Satrapies", "central_management", political_power_gain=0.15, stability_factor=0.05)
    idea("PRS_royal_road_spirit", "The Royal Road", "supply_line", supply_consumption_factor=-0.10, army_speed_factor=0.05)
    idea("PRS_immortals_spirit", "The Ten Thousand Immortals", "morale_bonus", army_attack_factor=0.05, army_org_factor=0.10)
    idea("PRS_qanats_spirit", "Qanats", "agrarian_society", monthly_population=0.15, stability_factor=0.03)
    idea("PRS_asha_spirit", "Truth against the Lie", "pp_unity_bonus", stability_factor=0.10, war_support_factor=0.05)
    f("PRS_king_of_kings", "King of Kings", "Darius has crushed the rebel kings. From the Indus to the Aegean, one king rules.",
      "political_pressure", 5, 0, [], "add_political_power = 75\nadd_stability = 0.05")
    f("PRS_satrapies", "The Satrapies", "Twenty provinces, each with a satrap, a fixed tribute - and the King's Eyes and Ears watching.",
      "political_pressure", 3, 1, [["PRS_king_of_kings"]], "add_ideas = PRS_satrapies_spirit")
    f("PRS_royal_road", "The Royal Road", "From Sardis to Susa in seven days: neither snow nor rain stays the royal couriers.",
      "construct_infrastructure", 5, 1, [["PRS_king_of_kings"]], "add_ideas = PRS_royal_road_spirit\n" + infra() + "\n" + infra(), filters=I)
    f("PRS_immortals", "The Immortals", "Ten thousand picked spearmen; when one falls, another takes his place.",
      "special_forces", 7, 1, [["PRS_king_of_kings"]], "add_ideas = PRS_immortals_spirit\narmy_experience = 15", filters=M, ai=3)
    f("PRS_daric", "The Daric", "Gold coins with the archer king: the money of an empire.",
      "trade", 2, 2, [["PRS_satrapies"]], build("industrial_complex") + "\nadd_political_power = 50", filters=I, ai=3)
    f("PRS_persepolis", "Persepolis", "A new royal city on a terrace in the mountains of Persis.",
      "construction2", 4, 2, [["PRS_satrapies", "PRS_royal_road"]], build("industrial_complex") + "\n" + build("industrial_complex"),
      filters=I, ai=3)
    f("PRS_qanats", "The Qanats", "Underground channels carry the water of the mountains to the fields of the plateau.",
      "construction", 6, 2, [["PRS_royal_road"]], "add_ideas = PRS_qanats_spirit", filters=I)
    f("PRS_phoenician_fleet", "The Phoenician Fleet", "Sidon, Tyre and Arwad sail for the Great King.",
      "build_navy", 8, 2, [["PRS_immortals"]], puppet("SDN", "TYR", "ARW") + "\nnavy_experience = 20", ai=2)
    f("PRS_behistun", "The Inscription of Behistun", "On the cliff, in three languages: what Darius did, by the favour of Ahura Mazda.",
      "propaganda", 3, 3, [["PRS_daric"], ["PRS_persepolis"]], "add_ideas = PRS_asha_spirit")
    f("PRS_nile_canal", "The Canal of the Nile", "Ships sail from the Nile to the Red Sea, as Darius ordered.",
      "construct_naval_dockyard", 5, 3, [["PRS_persepolis", "PRS_qanats"]], build("dockyard", "is_coastal = yes") + "\n" + infra(),
      extra=COAST, filters=I)
    f("PRS_ionia", "Ionia Pacified", "The Ionian cities rose; they will learn obedience - and keep their own laws, under satraps.",
      "occupy_states_ongoing_war", 7, 3, [["PRS_phoenician_fleet", "PRS_qanats"]], cores(2) + "\nadd_stability = 0.05")
    f("PRS_scythian_campaign", "Beyond the Ister", "The Scythians withdrew before the King's army once. Next time they will not escape.",
      "territory_or_war", 9, 3, [["PRS_phoenician_fleet"]], wargoal("SCY") + "\n" + claims("SCY"))
    f("PRS_earth_and_water", "Earth and Water", "Envoys go to every Greek city: give earth and water, or face the King.",
      "major_war", 7, 4, [["PRS_ionia"]], wargoal("ATH") + "\n" + wargoal("EUB") + "\n" + claims("ATH", "EUB"), ai=2)
    f("PRS_king_of_the_world", "King of the Lands", "Darius, the Great King, King of Kings, King of the lands of all peoples.",
      "national_unity", 5, 5, [["PRS_behistun"], ["PRS_nile_canal"], ["PRS_earth_and_water", "PRS_scythian_campaign"]],
      "add_political_power = 150\nadd_stability = 0.10\nadd_research_slot = 1", ai=3)

    # ============================================================== CARTHAGE (CAR)
    f = tree("CAR", "CAR_magonid_dynasty", "# Carthage under the Magonids (base tree)")
    idea("CAR_merchant_princes_spirit", "Merchant Princes", "economic_increase",
         trade_opinion_factor=0.20, production_speed_buildings_factor=0.10, political_power_gain=0.05)
    idea("CAR_mistress_of_the_sea_spirit", "Mistress of the Sea", "navy_bonus",
         production_speed_dockyard_factor=0.15, naval_damage_factor=0.10, naval_speed_factor=0.05)
    idea("CAR_mercenaries_spirit", "Mercenary Armies", "manpower_bonus", conscription=0.04, army_attack_factor=0.05, stability_factor=-0.03)
    idea("CAR_libyan_levies_spirit", "Libyan Levies", "manpower_bonus", conscription=0.03)
    idea("CAR_sacred_band_spirit", "The Sacred Band", "morale_bonus", army_org_factor=0.10, army_morale_factor=0.10)
    f("CAR_magonid_dynasty", "The House of Mago", "Mago and his sons have made Carthage a power by land and sea.",
      "political_pressure", 5, 0, [], "add_political_power = 75\nadd_stability = 0.05")
    f("CAR_suffetes", "Suffetes and Council", "Two judges elected each year, a council of elders, and the court of the Hundred and Four.",
      "national_unity", 3, 1, [["CAR_magonid_dynasty"]], "add_political_power = 100")
    f("CAR_cothon", "The Cothon", "A harbour within the walls, where the war fleet lies hidden from every eye.",
      "construct_naval_dockyard", 5, 1, [["CAR_magonid_dynasty"]], build("dockyard", "is_coastal = yes") + "\nnavy_experience = 10",
      extra=COAST, filters=I, ai=3)
    f("CAR_libyan_levies", "Libyan Levies", "The Libyan farmers of the hinterland owe tribute - and soldiers.",
      "allies_build_infantry", 7, 1, [["CAR_magonid_dynasty"]], "add_ideas = CAR_libyan_levies_spirit\nadd_manpower = 2000", filters=M)
    f("CAR_treaty_with_rome", "Treaty with Rome", "509 BC: Rome and Carthage swear friendship. Romans keep away from Africa, Carthaginians from Latium.",
      "improve_relations", 2, 2, [["CAR_suffetes"]], "add_political_power = 100\nadd_stability = 0.05")
    f("CAR_merchant_princes", "Merchant Princes", "Purple, silver, tin and wine: the trade of the western sea passes through Carthage.",
      "trade", 4, 2, [["CAR_suffetes", "CAR_cothon"]], "add_ideas = CAR_merchant_princes_spirit\n" + build("industrial_complex"), filters=I, ai=3)
    f("CAR_war_fleet", "The War Fleet", "Quinqueremes and triremes enough to close the straits to every rival.",
      "build_navy", 6, 2, [["CAR_cothon"]], "add_ideas = CAR_mistress_of_the_sea_spirit\n" + build("dockyard", "is_coastal = yes"),
      extra=COAST, filters=I, ai=3)
    f("CAR_mercenaries", "Mercenary Armies", "Iberians, Gauls, Balearic slingers: silver buys the best soldiers of the West.",
      "position_armies", 8, 2, [["CAR_libyan_levies"]], "add_ideas = CAR_mercenaries_spirit", filters=M)
    f("CAR_sardinia", "Sardinia", "Malchus failed in Sardinia; the sons of Mago will not.",
      "occupy_states_coastal", 3, 3, [["CAR_treaty_with_rome", "CAR_merchant_princes"]], wargoal("SAR") + "\n" + claims("SAR"))
    f("CAR_sicily", "The Sicilian War", "The Greeks of Sicily push against the Punic west of the island. Drive them back.",
      "major_war", 6, 3, [["CAR_war_fleet"]], wargoal("AKR") + "\n" + wargoal("GEL") + "\n" + claims("AKR"), ai=2)
    f("CAR_masters_of_libya", "Masters of Libya", "No more tribute to the Libyans for the land of the city: the hinterland becomes Carthage's.",
      "territory_or_war", 8, 3, [["CAR_mercenaries"]], wargoal("LIB") + "\n" + claims("LIB"))
    f("CAR_periplus_of_hanno", "The Voyage of Hanno", "Sixty ships sail through the Pillars of Herakles and down the coast of Libya, to found cities and explore.",
      "scientific_exchange", 2, 4, [["CAR_sardinia"]], "add_research_slot = 1\nnavy_experience = 15", filters=R, ai=3)
    f("CAR_iberia", "The Silver of Iberia", "Tartessos falls silent; the mines of the south belong to the Phoenicians of Gadir - and Carthage.",
      "more_territorial_claims", 5, 4, [["CAR_sardinia", "CAR_sicily"]], faction("ante_faction_punic_league", "GDR") + "\n" + wargoal("TTS"))
    f("CAR_sacred_band", "The Sacred Band", "Two and a half thousand citizens of the best families: the heart of the army.",
      "special_forces", 8, 4, [["CAR_masters_of_libya"]], "add_ideas = CAR_sacred_band_spirit\n" + doctrine("CAR_sacred_band"), filters=M)
    f("CAR_queen_of_the_sea", "Queen of the Western Sea", "From the Pillars of Herakles to Sicily, no ship sails without the leave of Carthage.",
      "major_alliance", 5, 5, [["CAR_periplus_of_hanno", "CAR_iberia"], ["CAR_sacred_band", "CAR_sicily"]],
      "add_political_power = 150\nadd_stability = 0.10\nnavy_experience = 25", ai=3)

    # ============================================================== harder focuses: conditions, time, drawbacks
    # (fid) -> (cost, available trigger, extra reward lines). cost 10 = 70 days. Big steps need the land to be
    # taken first (gone(TAG): the rival no longer exists or is our subject), and some hurt.
    def gone(*tags):
        # beaten = gone, our subject, or our ally in a faction (an ally can never be beaten: no lock)
        return "\n".join(f"OR = {{ NOT = {{ country_exists = {t} }} {t} = {{ is_subject_of = ROOT }} "
                         f"is_in_faction_with = {t} }}" for t in tags)

    def reach(t):
        """a war goal focus only when the target can be reached by land (or is gone)"""
        return f"OR = {{ NOT = {{ country_exists = {t} }} is_neighbor_of = {t} }}"

    def states(n):
        return realm(n)

    TUNE = {
        # Rome - Republic
        "ROM_rule_of_the_fathers": (10, "", "add_stability = -0.03"),
        "ROM_twelve_tables": (15, "", ""),
        "ROM_licinian_sextian_laws": (15, "has_stability > 0.3", ""),
        "ROM_lex_hortensia": (20, "", ""),
        "ROM_the_nobilitas": (20, "has_political_power > 100", "add_political_power = -100"),
        "ROM_evocatio": (10, "has_war = yes", ""),
        "ROM_manipular_legion": (15, "has_army_experience > 20", ""),
        "ROM_citizen_phalanx": (15, "has_army_experience > 20", ""),
        "ROM_via_appia": (15, states(4), ""),
        "ROM_coloniae": (15, states(5), ""),
        "ROM_lake_regillus": (10, "", ""),
        "ROM_siege_of_veii": (20, states(2), "add_political_power = -50"),
        "ROM_southern_etruria": (15, gone("VEI"), ""),
        "ROM_battle_of_the_allia": (10, "", "add_stability = -0.10"),
        "ROM_not_with_gold": (10, "", "add_manpower = -2000"),
        "ROM_servian_wall": (20, "", ""),
        "ROM_latin_war": (15, states(5), ""),
        "ROM_samnite_wars": (20, gone("LAT") + "\n" + reach("SAM"), "add_war_support = -0.05"),
        "ROM_sentinum": (15, gone("SAM"), ""),
        "ROM_tarentum_and_pyrrhus": (15, gone("SAM"), "add_manpower = -3000"),
        "ROM_treaty_with_tarentum": (15, gone("SAM"), "add_political_power = -100"),
        "ROM_italia": (25, states(20) + "\n" + gone("SAM", "LAT"), ""),
        "ROM_towards_sicily": (20, "", ""),
        "ROM_cisalpine_gaul": (20, "", ""),
        # Rome - the King
        "ROM_purge_the_conspirators": (10, "", "add_war_support = -0.05"),
        "ROM_the_twelve_cities": (20, states(3), ""),
        "ROM_king_of_the_etruscans": (15, reach("CLU"), ""),
        # 9: Rome, Latium, Volsci, Aequi, Veii, Caere, Tarquinii, Sabines, Marsi - all neighbours, Clusium not needed
        "ROM_regnum_italiae": (20, states(9) + "\n" + gone("LAT"), ""),
        "ROM_the_samnite_mountains": (20, reach("SAM"), "add_manpower = -2000"),
        "ROM_sabine_wars": (15, "", ""),
        "ROM_northern_etruria": (15, "OR = {\n" + reach("VLT") + "\n" + reach("ARR") + "\n}", ""),
        "ROM_umbria_and_picenum": (15, "OR = {\n" + reach("UMB") + "\n" + reach("PIC") + "\n}", ""),
        "ROM_apulia": (15, "", ""),
        "ROM_bruttium": (20, "", ""),
        "ROM_across_the_strait": (20, "", ""),
        "ROM_kingdom_of_the_po": (20, "", ""),
        "ROM_civitas_sine_suffragio": (15, "OR = {\n" + reach("SAB") + "\n" + reach("MAR") + "\n}", ""),
        "ROM_etruscan_truces": (15, gone("VEI"), ""),
        "ROM_deditio_of_capua": (10, "", ""),
        "ROM_apulian_allies": (15, "", ""),
        "ROM_lucania_and_bruttium": (20, "", "add_manpower = -2000"),
        "ROM_magna_graecia": (20, "", ""),
        "ROM_king_of_italy": (25, states(20), ""),
        # Athens
        "ATH_themistocles_fleet": (15, "", "add_political_power = -50"),
        "ATH_marathon": (15, "", ""),
        "ATH_delian_league": (20, "has_navy_size = { size > 5 }", ""),
        "ATH_long_walls": (20, "", ""),
        "ATH_school_of_hellas": (20, states(4), ""),
        # Sparta
        "LAK_helots": (10, "", "add_stability = -0.03"),
        "LAK_peloponnesian_league": (15, gone("AGS"), ""),
        "LAK_against_athens": (15, "", "add_stability = -0.05"),
        "LAK_hegemon_of_hellas": (25, gone("ATH"), ""),
        # Macedon
        "MKD_earth_and_water": (10, "", "add_war_support = -0.05"),
        "MKD_chalkidike": (15, gone("PAE"), ""),
        "MKD_thessalian_alliance": (15, gone("CHK"), ""),
        "MKD_hammer_and_anvil": (20, "has_army_experience > 30", ""),
        "MKD_hegemon_of_the_greeks": (20, states(6) + "\n" + gone("THL"), ""),
        # Persia
        "PRS_phoenician_fleet": (15, "", "add_political_power = -75"),
        "PRS_scythian_campaign": (15, "", "add_war_support = -0.05"),
        "PRS_earth_and_water": (20, "", ""),
        "PRS_king_of_the_world": (25, "OR = {\n" + gone("SCY") + "\n" + gone("ATH") + "\n}", ""),
        # Carthage
        "CAR_mercenaries": (10, "", "add_political_power = -50"),
        "CAR_sicily": (20, gone("SAR"), ""),
        "CAR_iberia": (15, "", ""),
        "CAR_queen_of_the_sea": (25, gone("SAR", "AKR") + "\nhas_navy_size = { size > 10 }", ""),
    }
    allf = {fo["id"]: fo for t in TREES.values() for fo in t["focuses"]}
    for fid, (cost, avail, more) in TUNE.items():
        fo = allf[fid]
        fo["cost"] = cost
        if more:
            fo["reward"] += "\n" + more
        if avail:
            assert "available" not in fo["extra"], fid
            fo["extra"] = (fo["extra"] + "\n" if fo["extra"] else "") + "available = {\n" + \
                "\n".join("\t" + line for line in avail.splitlines()) + "\n}"

    # after a revolution (rome_story.REVOLUTION) Rome is a Republic: every focus that can only be reached
    # through The King Remains closes for good
    rom = {fo["id"]: fo for fo in TREES["ROM"]["focuses"]}
    king = {"ROM_the_king_remains"}
    while True:
        more = {fid for fid, fo in rom.items() if fid not in king
                and any(all(p in king for p in group) for group in fo["pre"])}
        if not more:
            break
        king |= more
    gate = "NOT = { has_country_flag = ROM_revolution }"
    for fid in king - {"ROM_the_king_remains"}:
        fo = rom[fid]
        assert fo["extra"].count("available = {") <= 1, fid
        if "available = {" in fo["extra"]:
            fo["extra"] = fo["extra"].replace("available = {", "available = { " + gate, 1)
        else:
            fo["extra"] = (fo["extra"] + "\n" if fo["extra"] else "") + "available = { " + gate + " }"

    # ============================================================== localisation
    LOC.update({
        "ante_faction_latin_alliance": "Foedus Cassianum",
        "ante_faction_delian_league": "Delian League",
        "ante_faction_peloponnesian_league": "Peloponnesian League",
        "ante_faction_macedonian_alliance": "Macedonian-Thessalian Alliance",
        "ante_faction_punic_league": "Punic League",
        # texts of the country selection screen (common/bookmarks, written by tools/world.py)
        "ANTE_BOOKMARK_ROM": "The kings are gone. The young Republic, small and surrounded by Latins, Etruscans and hill tribes, must survive its first year. Ahead: the conquest of Italy.",
        "ANTE_BOOKMARK_CAR": "The daughter of Tyre rules the western sea under the house of Mago. Sardinia, Sicily and the silver of Iberia beckon.",
        "ANTE_BOOKMARK_PRS": "Darius I rules the greatest empire the world has seen, from the Aegean to the Indus. Only the Scythians and a few Greek cities defy him.",
        "ANTE_BOOKMARK_ATH": "Cleisthenes has given power to the people. Athens is small, restless - and about to discover silver, the sea and the hatred of the Great King.",
        "ANTE_BOOKMARK_LAK": "King Cleomenes leads the finest soldiers of Greece. Sparta rules the Peloponnese, but the helots and Argos are never far from revolt.",
        "ANTE_BOOKMARK_MKD": "Amyntas I has given earth and water to Persia. A half-Greek kingdom of horsemen and highlanders waits for its time.",
        "ANTE_BOOKMARK_SYR": "The richest city of Sicily, founded by Corinth. Tyrants and Carthage will decide its fate.",
        "ANTE_BOOKMARK_CLU": "Lars Porsenna of Clusium, the greatest king of Etruria, marches on Rome.",
        "ANTE_BOOKMARK_LAT": "Thirty Latin towns, one festival, one army: the League will not bow to Rome.",
        "ANTE_BOOKMARK_SCY": "Royal Scythians of the steppe: the army of Darius found nothing to conquer here.",
        "ANTE_BOOKMARK_MSG": "Queen Tomyris' people, horse archers of the eastern steppe, who killed Cyrus the Great.",
        "ANTE_BOOKMARK_KSH": "The black pharaohs of Napata and Meroe, heirs of Egypt on the Nile.",
        "ANTE_BOOKMARK_KYR": "The Greek kingdom of Cyrene, rich in silphium and horses, between Egypt and Carthage.",
        "ANTE_BOOKMARK_THL": "The horse lords of Thessaly: the widest plain and the best cavalry of Greece.",
    })
    for n in sorted(REALM_N):
        LOC[f"ANTE_REALM_STATES_{n}"] = (f"Controls at least {n} states, the states of its subjects included "
                                         f"(now: [?ante_realm_states])")
    return TREES, IDEAS, LOC
