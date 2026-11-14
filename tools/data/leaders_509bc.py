# Country leaders at the start (509 BC = 245 AUC) for the larger / historically important countries.
# Read by tools/world.py (recruit_character in history/countries) and tools/content.py (common/characters,
# leader traits, localisation). Everybody else still gets a random leader from common/names.
#
# (tag, character key suffix, name, trait, female, attested, description)
#   trait:    key in TRAITS below (one per leader)
#   attested: True = a real person of about this time (ancient sources); False = an invented chieftain for a people
#             whose rulers are not known by name - the description says so.
# The sub-ideology is chosen from the country's ruling party (tools/content.py).

LEADERS = [
    # --- attested rulers
    ("ROM", "brutus", "Lucius Junius Brutus", "ante_liberator", False, True,
     "Drove out Tarquinius Superbus, the last king, and became one of the first two consuls of the Republic."),
    ("CAR", "hamilcar", "Hamilcar", "ante_merchant_prince", False, True,
     "Of the house of Mago, which leads Carthage and its fleets in the late sixth century BC."),
    ("PRS", "darius", "Darius I", "ante_king_of_kings", False, True,
     "Dārayavauš, King of Kings since 522 BC, who organised the empire into satrapies and built the Royal Road."),
    ("ATH", "cleisthenes", "Cleisthenes", "ante_lawgiver", False, True,
     "The Alcmaeonid who, after the fall of the tyrants, reorganised the Athenians into ten tribes."),
    ("LAK", "cleomenes", "Cleomenes I", "ante_spartan_king", False, True,
     "Agiad king of Sparta, who helped to expel the Peisistratids from Athens in 510 BC."),
    ("CLU", "porsenna", "Lars Porsenna", "ante_lucumo", False, True,
     "King of Clusium, who according to the Romans marched on Rome to restore the Tarquins."),
    ("LAT", "mamilius", "Octavius Mamilius", "ante_war_leader", False, True,
     "Lord of Tusculum and son-in-law of Tarquinius Superbus, leader of the Latins against Rome."),
    ("MKD", "amyntas", "Amyntas I", "ante_shrewd_vassal", False, True,
     "Argead king of Macedon, who gave earth and water to the envoys of Darius."),
    ("SCY", "idanthyrsus", "Idanthyrsus", "ante_horse_lord", False, True,
     "King of the Royal Scythians, who drew Darius' army deep into the steppe and wore it down."),
    ("KSH", "amaniastabarqo", "Amaniastabarqo", "ante_king_of_kings", False, True,
     "King of Kush at Napata, heir of the pharaohs of the Twenty-fifth Dynasty."),
    ("KYR", "battus", "Battus IV", "ante_shrewd_vassal", False, True,
     "Battiad king of Cyrene, ruling under the shadow of Persian Egypt."),
    ("SAK", "skunkha", "Skunkha", "ante_horse_lord", False, True,
     "Chief of the pointed-hat Saka, defeated by Darius and shown on the Behistun relief."),
    ("AGA", "spargapeithes", "Spargapeithes", "ante_war_leader", False, True,
     "King of the Agathyrsi, named by Herodotus."),
    ("KRO", "milo", "Milo", "ante_war_leader", False, True,
     "Milo of Croton, six times Olympic victor, who led the army that destroyed Sybaris in 510 BC."),
    ("ROM", "tarquinius", "Lucius Tarquinius Superbus", "ante_king_of_kings", False, True,
     "The seventh and last king of Rome, builder of the great temple and the sewers - and a tyrant. Leads the (non-ruling) royalists at the start; the focus 'The King Remains' puts him in power."),
    ("SEN", "brennos", "Brennos the Elder", "ante_war_leader", False, False,
     "Invented: no chief of the Senones is known before the Brennus who sacked Rome in 390 BC - this is his forefather."),
    ("SYR", "gamoroi", "Kallikrates of the Gamoroi", "ante_merchant_prince", False, False,
     "Invented: the landowning Gamoroi, heirs of the Corinthian settlers, ruled Syracuse before the tyrants; no single ruler of 509 BC is known."),
    ("THL", "thorax", "Thorax of Larisa", "ante_horse_lord", False, True,
     "Head of the Aleuadae of Larisa, the leading house of Thessaly; attested a generation later, at the time of Xerxes."),
    ("ODR", "teres", "Teres", "ante_war_leader", False, True,
     "Founder of the power of the Odrysian Thracians."),
    ("MSG", "tomyris", "Tomyris", "ante_horse_lord", True, True,
     "Queen of the Massagetae, remembered for the defeat of Cyrus the Great."),
    # --- invented chieftains (rulers unknown by name)
    ("SAU", "aspakos", "Aspakos", "ante_horse_lord", False, False,
     "Chief of the Sauromatae. (Invented: their rulers of this age are not known by name.)"),
    ("NEU", "vaidevutis", "Vaidevutis", "ante_tribal_chief", False, False,
     "Elder of the Neuri. (Invented, after a figure of Baltic legend.)"),
    ("FEN", "kaleva", "Kaleva", "ante_tribal_chief", False, False,
     "Elder of the Fenni. (Invented, after a figure of Finnic legend.)"),
    ("SIG", "artaios", "Artaios", "ante_horse_lord", False, False,
     "Chief of the Sigynnae, who dress like Medes. (Invented name.)"),
    ("GTA", "zalmodegikos", "Zalmodegikos", "ante_war_leader", False, False,
     "King of the Getae. (Invented name in the Thracian manner.)"),
    ("PAN", "pinnes", "Pinnes", "ante_tribal_chief", False, False,
     "Chief of the Pannonii. (Invented name in the Illyrian manner.)"),
    ("BUD", "taxakis", "Taxakis", "ante_tribal_chief", False, False,
     "Chief of the Budini. (Invented name.)"),
    ("AES", "gintaras", "Gintaras", "ante_tribal_chief", False, False,
     "Elder of the Aestii, the amber gatherers. (Invented name.)"),
    ("GAE", "iarbas", "Iarbas", "ante_tribal_chief", False, False,
     "Chief of the Gaetuli. (Invented, after the Libyan king of the Dido legend.)"),
    ("LUG", "vannius", "Vannius", "ante_tribal_chief", False, False,
     "Chief of the Lugii. (Invented name.)"),
    ("THY", "arpoxais", "Arpoxais", "ante_horse_lord", False, False,
     "Chief of the Thyssagetae. (Invented, after a son of Targitaus in the Scythian origin legend.)"),
    ("ISS", "kolaxais", "Kolaxais", "ante_horse_lord", False, False,
     "Chief of the Issedones. (Invented, after a figure of the Scythian origin legend.)"),
]

# leader traits: key -> (name, modifiers). Country modifiers, as in the base game's common/country_leader.
TRAITS = {
    "ante_liberator": ("Liberator of the City", {"stability_factor": 0.10, "drift_defence_factor": 0.25}),
    "ante_merchant_prince": ("Merchant Prince", {"political_power_factor": 0.10, "production_speed_buildings_factor": 0.10}),
    "ante_king_of_kings": ("King of Kings", {"political_power_factor": 0.20, "stability_factor": 0.05}),
    "ante_lawgiver": ("Lawgiver", {"stability_factor": 0.05, "political_power_factor": 0.15}),
    "ante_spartan_king": ("King of the Spartans", {"army_defence_factor": 0.10, "war_support_factor": 0.10}),
    "ante_lucumo": ("Lucumo", {"army_attack_factor": 0.05, "political_power_factor": 0.10}),
    "ante_war_leader": ("War Leader", {"army_attack_factor": 0.05, "war_support_factor": 0.05}),
    "ante_shrewd_vassal": ("Shrewd Vassal", {"political_power_factor": 0.10, "stability_factor": 0.05}),
    "ante_horse_lord": ("Lord of Horsemen", {"army_attack_factor": 0.05, "army_org_factor": 0.05}),
    "ante_tribal_chief": ("Chief of the Clans", {"stability_factor": 0.05, "conscription": 0.005}),
}

# leaders of a party that does not rule at the start (recruited in history like everybody, so a focus can
# promote_character them); value = their sub-ideology (overrides the one taken from the ruling party)
LATER = {"ROM_tarquinius": "despotism"}
