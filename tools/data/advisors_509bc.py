"""Advisors of 509 BC (read by tools/government.py).

TRAITS: key -> (name, slot group, modifiers). slot group: pol = political advisor, army = army chief,
        navy = navy chief, hc = member of the war council (high command).
NAMED:  real people of about 509-490 BC, each with the trait of what they really did.
        (tag, key, name, slot, trait, female, description)
        slot: political_advisor, army_chief, navy_chief, high_command
Everybody else gets advisors made up from the people's own name list (government.py), with traits that fit the
people: the city peoples get lawgivers, merchants and philosophers, the tribes elders, priests and bards.
"""

TRAITS = {
    # --- counsellors (political advisors)
    "ante_adv_lawgiver": ("Lawgiver", "pol", {"stability_factor": 0.10}),
    "ante_adv_orator": ("Orator of the Assembly", "pol", {"political_power_gain": 0.15}),
    "ante_adv_high_priest": ("High Priest", "pol", {"stability_factor": 0.05, "war_support_factor": 0.05}),
    "ante_adv_augur": ("Augur and Seer", "pol", {"war_support_factor": 0.10}),
    "ante_adv_merchant": ("Merchant Prince", "pol", {"trade_opinion_factor": 0.25, "production_speed_buildings_factor": 0.05}),
    "ante_adv_treasurer": ("Keeper of the Treasury", "pol", {"industrial_capacity_factory": 0.05, "political_power_gain": 0.05}),
    "ante_adv_architect": ("Master Builder", "pol", {"production_speed_buildings_factor": 0.10}),
    "ante_adv_philosopher": ("Philosopher", "pol", {"research_speed_factor": 0.05}),
    "ante_adv_physician": ("Physician", "pol", {"monthly_population": 0.10, "attrition": -0.05}),
    "ante_adv_geographer": ("Geographer and Explorer", "pol", {"navy_max_range_factor": 0.15, "research_speed_factor": 0.02}),
    "ante_adv_envoy": ("Envoy and Guest-Friend", "pol", {"opinion_gain_monthly_factor": 0.25}),
    "ante_adv_spymaster": ("Keeper of Secrets", "pol", {"intel_network_gain_factor": 0.25, "enemy_operative_detection_chance_factor": 0.15}),
    "ante_adv_shipwright": ("Master Shipwright", "pol", {"production_speed_dockyard_factor": 0.15}),
    "ante_adv_poet": ("Poet of the City", "pol", {"war_support_factor": 0.05, "stability_factor": 0.05}),
    "ante_adv_druid": ("Druid", "pol", {"stability_factor": 0.07, "research_speed_factor": 0.02}),
    "ante_adv_elder": ("Elder of the Clans", "pol", {"political_power_gain": 0.10, "stability_factor": 0.03}),
    "ante_adv_land_reformer": ("Friend of the Landless", "pol", {"monthly_population": 0.05, "stability_factor": 0.05}),
    "ante_adv_oligarch": ("Leader of the Few", "pol", {"political_power_gain": 0.15, "war_support_factor": -0.03}),
    "ante_adv_exiled_tyrant": ("Exiled Tyrant", "pol", {"political_power_gain": 0.10, "justify_war_goal_time": -0.20}),
    # --- the war council (military staff)
    "ante_staff_strategos": ("Strategos", "army", {"army_attack_factor": 0.05, "army_defence_factor": 0.03}),
    "ante_staff_master_of_horse": ("Master of the Horse", "army", {"army_speed_factor": 0.08, "army_attack_factor": 0.03}),
    "ante_staff_defender": ("Defender of the Walls", "army", {"army_defence_factor": 0.10}),
    "ante_staff_drillmaster": ("Drillmaster", "army", {"experience_gain_army_factor": 0.15, "army_org_factor": 0.03}),
    "ante_staff_navarch": ("Navarch", "navy", {"naval_damage_factor": 0.10}),
    "ante_staff_master_of_rowers": ("Master of the Rowers", "navy", {"naval_speed_factor": 0.10}),
    "ante_staff_explorer": ("Explorer of the Seas", "navy", {"navy_max_range_factor": 0.20}),
    "ante_staff_quartermaster": ("Quartermaster", "hc", {"supply_consumption_factor": -0.05}),
    "ante_staff_siege_master": ("Master of Sieges", "hc", {"army_attack_factor": 0.04}),
    "ante_staff_guard_captain": ("Captain of the Guard", "hc", {"army_org_factor": 0.05}),
    "ante_staff_scout_master": ("Master of Scouts", "hc", {"army_speed_factor": 0.05}),
}

P, A, N, H = "political_advisor", "army_chief", "navy_chief", "high_command"
NAMED = [
    # Rome
    ("ROM", "menenius", "Agrippa Menenius Lanatus", P, "ante_adv_orator", False,
     "Who talked the plebs back from the Sacred Mount with the fable of the belly and the limbs (494 BC)."),
    ("ROM", "pulvillus", "Marcus Horatius Pulvillus", P, "ante_adv_high_priest", False,
     "The consul who dedicated the temple of Jupiter on the Capitol in the first year of the Republic."),
    ("ROM", "cassius", "Spurius Cassius Vecellinus", P, "ante_adv_land_reformer", False,
     "Author of the first law to share out the public land (486 BC) - and killed for it."),
    ("ROM", "appius", "Appius Claudius Sabinus", P, "ante_adv_elder", False,
     "A Sabine noble who moved to Rome in 504 BC with five thousand clients: the first of the Claudii."),
    ("ROM", "cominius", "Postumus Cominius Auruncus", A, "ante_staff_strategos", False,
     "Consul in 501 and 493 BC; under him Corioli was taken."),
    ("ROM", "coriolanus", "Gnaeus Marcius Coriolanus", H, "ante_staff_siege_master", False,
     "The young soldier who broke into Corioli alone and took his name from it."),
    # Athens
    ("ATH", "isagoras", "Isagoras", P, "ante_adv_oligarch", False,
     "Cleisthenes' rival, the leader of the few, who called in Sparta in 508 BC - and lost."),
    ("ATH", "xanthippus", "Xanthippus", P, "ante_adv_orator", False,
     "Politician of the Alcmaeonid circle, prosecutor of Miltiades, father of Pericles."),
    ("ATH", "phrynichus", "Phrynichus", P, "ante_adv_poet", False,
     "The tragedian whose 'Capture of Miletus' made all Athens weep - he was fined for it."),
    ("ATH", "antenor", "Antenor", P, "ante_adv_architect", False,
     "Sculptor of the Tyrannicides in the Agora and of the great statues on the Acropolis."),
    # Sparta
    ("LAK", "gorgo", "Gorgo", P, "ante_adv_spymaster", True,
     "Daughter of Cleomenes. As a child she warned her father against the bribes of Aristagoras; later she found "
     "the message hidden under the wax of a tablet."),
    # Persia
    ("PRS", "democedes", "Democedes of Croton", P, "ante_adv_physician", False,
     "The Greek physician who healed the Great King's foot and the queen Atossa - and was never allowed to go home."),
    ("PRS", "hecataeus", "Hecataeus of Miletus", P, "ante_adv_geographer", False,
     "Traveller and geographer: his 'Journey round the World' and map described the empire's lands and peoples."),
    ("PRS", "parnakka", "Parnakka", P, "ante_adv_treasurer", False,
     "Uncle of Darius and head of the royal administration at Persepolis: thousands of his tablets survive."),
    ("PRS", "hippias", "Hippias", P, "ante_adv_exiled_tyrant", False,
     "The last tyrant of Athens, driven out in 510 BC. At the Persian court he waits for the day he returns."),
    ("PRS", "heraclitus", "Heraclitus of Ephesus", P, "ante_adv_philosopher", False,
     "'Everything flows.' The proud philosopher of Ephesus, a subject of the Great King."),
    ("PRS", "histiaeus", "Histiaeus of Miletus", P, "ante_adv_envoy", False,
     "The tyrant of Miletus who saved Darius' bridge on the Ister and was kept at Susa as the King's friend."),
    ("PRS", "gobryas", "Gobryas", A, "ante_staff_strategos", False,
     "One of the Seven who overthrew the false Smerdis; the King's spear-bearer and father of Mardonius."),
    ("PRS", "scylax", "Scylax of Caryanda", N, "ante_staff_explorer", False,
     "Sent by Darius down the Indus and round Arabia to the Red Sea: thirty months at sea."),
    ("PRS", "aspathines", "Aspathines", H, "ante_staff_quartermaster", False,
     "One of the Seven; the King's quiver-bearer."),
    # Italy and Sicily
    ("KRO", "pythagoras", "Pythagoras of Samos", P, "ante_adv_philosopher", False,
     "Philosopher, mathematician and master of a brotherhood that ruled Croton - until the city rose against it."),
    ("KRO", "alcmaeon", "Alcmaeon of Croton", P, "ante_adv_physician", False,
     "The physician who first said that the brain, not the heart, is the seat of thought."),
    ("POS", "xenophanes", "Xenophanes of Colophon", P, "ante_adv_philosopher", False,
     "Wandering poet and philosopher who settled at Elea near Poseidonia: if oxen had hands, they would draw gods "
     "like oxen."),
    ("VEI", "vulca", "Vulca of Veii", P, "ante_adv_architect", False,
     "The Etruscan sculptor who made the terracotta Jupiter for the Capitol of Rome."),
    ("LAT", "turnus", "Turnus Herdonius", P, "ante_adv_orator", False,
     "Of Aricia: he spoke against Tarquinius at the meeting of the Latins - and was drowned for it."),
    ("CUM", "aristodemus", "Aristodemus Malakos", A, "ante_staff_strategos", False,
     "Victor over the Etruscans at Aricia (504 BC), soon tyrant of Cumae."),
    ("GEL", "gelon", "Gelon son of Deinomenes", A, "ante_staff_master_of_horse", False,
     "Commander of the cavalry of Gela; one day master of Syracuse."),
]

# trait pools for the made-up counsellors: city peoples / tribes; the Celts have druids
CIVIL_POOL = ["ante_adv_lawgiver", "ante_adv_orator", "ante_adv_merchant", "ante_adv_architect", "ante_adv_philosopher",
              "ante_adv_high_priest", "ante_adv_treasurer", "ante_adv_envoy", "ante_adv_poet", "ante_adv_physician"]
TRIBAL_POOL = ["ante_adv_elder", "ante_adv_high_priest", "ante_adv_augur", "ante_adv_orator", "ante_adv_merchant",
               "ante_adv_envoy"]
ARMY_POOL = ["ante_staff_strategos", "ante_staff_master_of_horse", "ante_staff_defender", "ante_staff_drillmaster"]
NAVY_POOL = ["ante_staff_navarch", "ante_staff_master_of_rowers", "ante_staff_explorer"]
HC_POOL = ["ante_staff_quartermaster", "ante_staff_siege_master", "ante_staff_guard_captain", "ante_staff_scout_master"]
