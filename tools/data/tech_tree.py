"""The ancient tech tree (read by tools/tech.py; tools/world.py reads START/START_CIVILISED for the history files).

(key, name, description, folder, x, AUC year, [prerequisites], effects, icon, cost)
  folder: the base game's tech screen pages, renamed (tools/tech.py FOLDERS)
  AUC year: the row is snapped to the nearest year label of that page (tools/tech.py YEAR_AUC)
  effects: script lines (modifiers, enable_equipments, enable_subunits, unit stat blocks)
  icon: "eq:<equipment archetype or hull>" = the production picture (large tech box), else a glyph (small box)
Years: 245 AUC = 509 BC (start), 305 = 449 BC, 365 = 389 BC, 425 = 329 BC, 485 = 269 BC.
"""

INF, SUP, ARM, ART, NAV, LRN, IND = ("infantry_folder", "support_folder", "armour_folder", "artillery_folder",
                                     "naval_folder", "electronics_folder", "industry_folder")
FOOT = ("ante_levy", "ante_spearmen", "ante_hoplites", "ante_skirmishers", "ante_archers")


def units(keys, **stats):
    return "\n".join(f"{k} = {{ " + " ".join(f"{s} = {v}" for s, v in stats.items()) + " }" for k in keys)


TECHS = [
    # ------------------------------------------------------------------ arms and armour
    ("ante_bronze_weapons", "Bronze Weapons", "Cast bronze spearheads, daggers and axes: the arms of the age of heroes.",
     INF, 0, 245, [], "", "eq:ante_arms_equipment", 1),
    ("ante_iron_weapons", "Iron Weapons", "Iron is harder to work but everywhere to be found: every man can now carry a good blade.",
     INF, 0, 305, ["ante_bronze_weapons"], "enable_equipments = { ante_arms_equipment_2 }", "eq:ante_arms_equipment", 1.5),
    ("ante_forged_steel", "Forged Steel", "Hammered, folded and quenched: the swords of Noricum and Iberia.",
     INF, 0, 395, ["ante_iron_weapons"], "enable_equipments = { ante_arms_equipment_3 }", "eq:ante_arms_equipment", 2),
    ("ante_short_sword", "The Short Sword", "A short, stabbing sword for the press of battle - the Iberian blade that Rome will make its own.",
     INF, 0, 485, ["ante_forged_steel"], units(FOOT, soft_attack=0.10), "sword", 2),
    ("ante_bronze_armour", "Bronze Armour", "Helmet, cuirass and greaves beaten from bronze sheet.",
     INF, 2, 245, [], "", "eq:ante_panoply_equipment", 1),
    ("ante_linothorax", "Linothorax", "Layers of glued linen: lighter than bronze, almost as strong.",
     INF, 2, 320, ["ante_bronze_armour"], "enable_equipments = { ante_panoply_equipment_2 }", "eq:ante_panoply_equipment", 1.5),
    ("ante_chain_mail", "Mail and the Long Shield", "Rings of iron, invented by the Celts, and the curved oval shield.",
     INF, 2, 425, ["ante_linothorax"], "enable_equipments = { ante_panoply_equipment_3 }", "eq:ante_panoply_equipment", 2),
    ("ante_simple_bows", "Bows and Slings", "The hunter's bow and the shepherd's sling go to war.",
     INF, 4, 245, [], "", "eq:ante_ranged_equipment", 1),
    ("ante_composite_bows", "Composite Bows", "Horn, wood and sinew: the bow of the steppe shoots twice as far.",
     INF, 4, 335, ["ante_simple_bows"], "enable_equipments = { ante_ranged_equipment_2 }", "eq:ante_ranged_equipment", 1.5),
    ("ante_lead_shot", "Lead Sling Shot", "Cast lead bullets, some inscribed with insults for the enemy.",
     INF, 4, 455, ["ante_composite_bows"], "enable_equipments = { ante_ranged_equipment_3 }", "eq:ante_ranged_equipment", 2),
    ("ante_close_order", "Close Order", "Shield overlapping shield: the phalanx moves as one body.",
     INF, 6, 290, [], units(("ante_hoplites", "ante_spearmen"), defense=0.10), "helmet", 1.5),
    ("ante_open_order", "Open Order", "Javelin men and peltasts who strike and withdraw before the heavy foot can close.",
     INF, 6, 365, ["ante_close_order"], units(("ante_skirmishers", "ante_archers"), soft_attack=0.10, defense=0.05), "helmet", 1.5),
    ("ante_maniples", "Maniples", "Small, flexible units in three lines that relieve each other in battle.",
     INF, 6, 425, ["ante_open_order"], units(FOOT, max_organisation=5, breakthrough=0.10), "helmet", 2),
    # ------------------------------------------------------------------ logistics and auxiliaries
    ("ante_pack_animals", "Pack Animals and Carts", "Mules, donkeys and ox-carts carry the grain behind the army.",
     SUP, 0, 245, [], "enable_equipments = { train_equipment_1 }", "wheel", 1),
    ("ante_supply_wagons", "Supply Trains", "Organised columns of wagons and depots along the line of march.",
     SUP, 0, 335, ["ante_pack_animals"], "attrition = -0.05\nsupply_consumption_factor = -0.05", "wheel", 1.5),
    ("ante_military_roads", "Military Roads", "Straight, paved, drained: the army marches a day's journey further.",
     SUP, 0, 425, ["ante_supply_wagons"], "army_speed_factor = 0.05\nattrition = -0.05", "wheel", 2),
    ("ante_scouting", "Scouts and Outriders", "Light horsemen ahead of the column find the enemy before he finds us.",
     SUP, 2, 290, [], units(("ante_scouts",), recon=1), "eye", 1),
    ("ante_spies", "Spies and Informers", "Traders, deserters and bribed slaves tell what the enemy plans.",
     SUP, 2, 365, ["ante_scouting"], "planning_speed = 0.10", "eye", 1.5),
    ("ante_field_camps", "Fortified Camps", "Every evening a ditch and a palisade: the army sleeps safe in enemy country.",
     SUP, 4, 305, [], "max_dig_in = 2\nland_reinforce_rate = 0.02", "tent", 1.5),
    ("ante_army_surgeons", "Army Surgeons", "Physicians in the camp: fewer men die of their wounds.",
     SUP, 4, 395, ["ante_field_camps"], "land_reinforce_rate = 0.03\nattrition = -0.05", "cup", 1.5),
    # ------------------------------------------------------------------ horse and chariot
    ("ante_riding", "Horsemanship", "Riding to war, not only to the battlefield.",
     ARM, 0, 245, [], "", "eq:ante_horse_equipment", 1),
    ("ante_horse_breeding", "Horse Breeding", "Stud farms of Thessaly and Media breed taller, stronger horses.",
     ARM, 0, 320, ["ante_riding"], "enable_equipments = { ante_horse_equipment_2 }", "eq:ante_horse_equipment", 1.5),
    ("ante_horned_saddle", "The Horned Saddle", "A saddle with four horns holds the rider firm in the charge.",
     ARM, 0, 455, ["ante_horse_breeding"], "enable_equipments = { ante_horse_equipment_3 }", "eq:ante_horse_equipment", 2),
    ("ante_chariotry", "Chariotry", "The old war car of kings and heroes.",
     ARM, 2, 245, [], "", "eq:ante_chariot_equipment", 1),
    ("ante_scythed_chariots", "Scythed Chariots", "Blades on the axles: a terror for infantry in open order.",
     ARM, 2, 365, ["ante_chariotry"], "enable_equipments = { ante_chariot_equipment_2 }", "eq:ante_chariot_equipment", 1.5),
    ("ante_horse_archery", "Horse Archery", "Shooting at the gallop, even backwards: the art of the steppe.",
     ARM, 4, 290, ["ante_riding"], units(("ante_horse_archers",), soft_attack=0.10, defense=0.05), "horse", 1.5),
    ("ante_heavy_cavalry", "Heavy Cavalry", "Armoured riders with the long lance: the Companions of Macedon.",
     ARM, 4, 425, ["ante_horse_archery", "ante_horse_breeding"], units(("ante_cavalry",), soft_attack=0.10, breakthrough=0.15), "horse", 2),
    ("ante_war_elephants_tech", "War Elephants", "Indian elephants, their drivers and towers: the beasts that terrified the West.",
     ARM, 6, 455, ["ante_riding"], "enable_equipments = { ante_elephant_equipment_1 }\nenable_subunits = { ante_war_elephants }",
     "eq:ante_elephant_equipment", 2.5),
    # ------------------------------------------------------------------ siege craft
    ("ante_rams_and_ladders", "Rams and Ladders", "The oldest way into a city: break the gate or climb the wall.",
     ART, 0, 245, [], "", "eq:ante_siege_equipment", 1),
    ("ante_siege_towers", "Siege Towers", "Moving towers taller than the walls, covered in wet hides.",
     ART, 0, 320, ["ante_rams_and_ladders"], "enable_equipments = { ante_siege_equipment_2 }", "eq:ante_siege_equipment", 1.5),
    ("ante_torsion_engines", "Torsion Engines", "Twisted sinew throws stones and bolts: the catapult of Dionysius of Syracuse.",
     ART, 0, 395, ["ante_siege_towers"], "enable_equipments = { ante_siege_equipment_3 }", "eq:ante_siege_equipment", 2),
    ("ante_field_artillery", "Field Engines", "Bolt-throwers that move with the army and sweep the field.",
     ART, 0, 455, ["ante_torsion_engines"], units(("ante_siege_engines",), soft_attack=0.15), "wheel", 2),
    ("ante_earthworks", "Earthworks", "Ramparts, ditches and stakes that hold an enemy at bay.",
     ART, 2, 290, ["ante_rams_and_ladders"], "max_dig_in = 2", "wall", 1),
    ("ante_stone_walls", "Stone Walls", "Ashlar walls with towers around the whole city.",
     ART, 2, 365, ["ante_earthworks"], "army_core_defence_factor = 0.05", "wall", 1.5),
    ("ante_poliorcetics", "Poliorcetics", "The science of sieges: mines, counter-mines, circumvallation.",
     ART, 2, 425, ["ante_stone_walls", "ante_torsion_engines"], "army_attack_factor = 0.03", "wall", 2),
    # ------------------------------------------------------------------ seafaring
    ("ante_seafaring", "Seafaring", "Oared ships that carry warriors along the coasts and across the straits.",
     NAV, 0, 245, [], "naval_invasion_capacity = 100\nnaval_invasion_prep_days = -30\nnaval_invasion_division_cap = 2\n"
     "naval_invasion_plan_cap = 2", "ship", 1),
    ("ante_ramming", "The Bronze Ram", "Row hard, strike the enemy's side, back oars: the ship itself is the weapon.",
     NAV, 0, 290, ["ante_seafaring"], "naval_damage_factor = 0.05", "ship", 1.5),
    ("ante_diekplous", "Diekplous", "Break through the enemy line, turn and ram from behind - the manoeuvre of the best crews.",
     NAV, 0, 335, ["ante_ramming"], "naval_damage_factor = 0.05\nnavy_org_factor = 0.05", "ship", 1.5),
    ("ante_quinquereme_tech", "The Quinquereme", "Five rowers to each column of oars: heavier ships for marines and war engines.",
     NAV, 0, 455, ["ante_diekplous"], "enable_equipments = { ante_quinquereme_hull_1 }\nenable_subunits = { ante_quinquereme }",
     "eq:ante_quinquereme_hull", 2.5),
    ("ante_ship_sheds", "Ship Sheds", "Long sheds on the shore where ships are built and kept dry in winter.",
     NAV, 2, 290, ["ante_seafaring"], "production_speed_dockyard_factor = 0.10", "ship", 1),
    ("ante_marines", "Marines", "Soldiers on deck who board the enemy and lead the landings.",
     NAV, 2, 335, ["ante_ship_sheds"], "naval_invasion_capacity = 100\nnaval_invasion_prep_days = -15", "helmet", 1.5),
    ("ante_lighthouses", "Lighthouses", "Fires on headlands and towers at harbour mouths: ships sail by night and far from home.",
     NAV, 2, 455, ["ante_marines"], "navy_max_range_factor = 0.15\nnaval_speed_factor = 0.05", "tower", 1.5),
    # ------------------------------------------------------------------ learning
    ("ante_writing", "Writing", "Letters borrowed from the Phoenicians: accounts, laws and treaties on stone, bronze and leather.",
     LRN, 0, 245, [], "research_speed_factor = 0.02", "scroll", 1),
    ("ante_schools", "Schools", "Teachers of letters and numbers for the sons of citizens.",
     LRN, 0, 305, ["ante_writing"], "research_speed_factor = 0.03", "scroll", 1.5),
    ("ante_philosophy", "Philosophy", "Questions about nature, the gods and the good life, asked in public.",
     LRN, 0, 365, ["ante_schools"], "research_speed_factor = 0.03\npolitical_power_factor = 0.05", "column", 1.5),
    ("ante_academy", "The Academy", "A grove outside Athens where philosophers teach and argue for life.",
     LRN, 0, 425, ["ante_philosophy"], "research_speed_factor = 0.05", "column", 2),
    ("ante_museion", "The Museion", "A royal house of the Muses with a library of all the books in the world.",
     LRN, 0, 485, ["ante_academy"], "research_speed_factor = 0.05", "scroll", 2.5),
    ("ante_mathematics", "Geometry", "Measuring fields, angles and the heights of walls.",
     LRN, 2, 320, ["ante_writing"], "production_factory_efficiency_gain_factor = 0.05", "star", 1.5),
    ("ante_astronomy", "Astronomy", "The stars and the calendar: sailors steer and farmers sow by them.",
     LRN, 2, 395, ["ante_mathematics"], "navy_max_range_factor = 0.10\nmonthly_population = 0.03", "star", 1.5),
    ("ante_mechanics", "Mechanics", "Levers, pulleys, screws and gears: the machines of Archimedes.",
     LRN, 2, 455, ["ante_astronomy"], "production_factory_max_efficiency_factor = 0.05", "wheel", 2),
    ("ante_medicine", "Medicine", "Herbs, surgery and the temple of Asclepius.",
     LRN, 4, 335, ["ante_writing"], "monthly_population = 0.05", "cup", 1.5),
    ("ante_hippocratic_medicine", "Hippocratic Medicine", "Disease has natural causes: observe, record, and do no harm.",
     LRN, 4, 410, ["ante_medicine"], "attrition = -0.05\nmonthly_population = 0.05", "cup", 2),
    ("ante_rhetoric", "Rhetoric", "The art of persuading an assembly - or a jury.",
     LRN, 6, 290, ["ante_writing"], "political_power_gain = 0.05", "laurel", 1),
    ("ante_written_law", "Written Law", "The law on public tablets binds the judges as well as the judged.",
     LRN, 6, 365, ["ante_rhetoric"], "stability_factor = 0.03", "scroll", 1.5),
    # ------------------------------------------------------------------ crafts and building
    ("ante_bronze_casting", "Bronze Casting", "Copper and tin melted together and poured into moulds.",
     IND, 0, 245, [], "", "anvil", 1),
    ("ante_iron_smelting", "Iron Smelting", "Bloomeries in every valley with ore and wood.",
     IND, 0, 305, ["ante_bronze_casting"], "production_factory_max_efficiency_factor = 0.05\nlocal_resources_factor = 0.10", "anvil", 1.5),
    ("ante_bellows_furnace", "Bellows and Shaft Furnace", "Hotter fires, more iron, better iron.",
     IND, 0, 395, ["ante_iron_smelting"], "production_factory_efficiency_gain_factor = 0.10", "anvil", 2),
    ("ante_state_workshops", "State Workshops", "Arsenals and workshops owned by the state turn out arms by the thousand.",
     IND, 0, 455, ["ante_bellows_furnace"], "industrial_capacity_factory = 0.05", "anvil", 2),
    ("ante_masonry", "Masonry", "Cut stone laid without mortar: walls, temples and terraces.",
     IND, 2, 245, [], "", "column", 1),
    ("ante_lime_mortar", "Lime Mortar", "Burnt lime binds stone to stone: building is faster and higher.",
     IND, 2, 320, ["ante_masonry"], "production_speed_buildings_factor = 0.10", "wall", 1.5),
    ("ante_opus_caementicium", "Opus Caementicium", "Volcanic ash, lime and rubble: a stone that is poured.",
     IND, 2, 455, ["ante_lime_mortar"], "production_speed_buildings_factor = 0.10\nproduction_speed_infrastructure_factor = 0.10", "wall", 2),
    ("ante_irrigation", "Irrigation", "Canals, dams and water-lifting wheels make the dry land green.",
     IND, 4, 290, [], "monthly_population = 0.05\nglobal_building_slots_factor = 0.10", "wheat", 1.5),
    ("ante_heavy_plough", "The Iron Ploughshare", "Iron shares turn the heavy soils of the river valleys.",
     IND, 4, 380, ["ante_irrigation"], "monthly_population = 0.05\nindustrial_capacity_factory = 0.05", "wheat", 1.5),
    ("ante_mining", "Deep Mining", "Shafts and galleries follow the vein deep into the mountain.",
     IND, 6, 335, ["ante_bronze_casting"], "local_resources_factor = 0.10", "pick", 1.5),
    ("ante_water_mills", "Water Mills", "The river grinds the grain: hands are free for other work.",
     IND, 6, 485, ["ante_mining"], "industrial_capacity_factory = 0.05", "wheel", 2),
    ("ante_coinage", "Coinage", "Stamped metal of fixed weight: trade without weighing silver.",
     IND, 8, 305, [], "production_speed_buildings_factor = 0.05\npolitical_power_gain = 0.05", "coin", 1),
]

# researched at the start by everybody / by the peoples with cities and writing (world.py, culture "names" key)
START = ["ante_bronze_weapons", "ante_bronze_armour", "ante_simple_bows", "ante_pack_animals", "ante_riding",
         "ante_chariotry", "ante_rams_and_ladders", "ante_seafaring", "ante_bronze_casting"]
START_CIVILISED = ["ante_writing", "ante_masonry"]
CIVILISED = {"greek", "latin", "etruscan", "punic", "persian", "anatolian", "nilotic", "roman"}
