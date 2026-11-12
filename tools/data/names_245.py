"""Personal names per culture for common/names (generated leaders, generals, admirals).

NAMES: culture key (see CULTURES in world_245.py) -> dict
  male, female   given names
  surnames       family names / clan names / epithets (the engine shows "<given> <surname>")
  callsigns      pilot nicknames; the engine wants the list to exist
Plain ASCII on purpose. Sources: attested names of the 6th-3rd century BC where they exist,
otherwise names of the same language family.
"""

CALLSIGNS = ["Aquila", "Lupus", "Falco", "Ursus", "Leo", "Corvus", "Taurus", "Aper", "Vulpes", "Draco",
             "Fulmen", "Ventus", "Sagitta", "Hasta", "Scutum", "Gladius", "Ferrum", "Ignis"]

NAMES = {
    "latin": dict(
        male=["Lucius", "Marcus", "Gaius", "Publius", "Quintus", "Titus", "Aulus", "Gnaeus", "Spurius", "Manius",
              "Servius", "Appius", "Numerius", "Decimus", "Tiberius", "Sextus", "Kaeso", "Postumus", "Agrippa",
              "Opiter", "Vopiscus", "Proculus", "Hostus", "Volesus", "Mamercus", "Tullus", "Ancus", "Numa"],
        female=["Lucretia", "Verginia", "Cloelia", "Tullia", "Valeria", "Horatia", "Claudia", "Fabia", "Cornelia",
                "Aemilia", "Iulia", "Tarquinia", "Veturia", "Volumnia", "Hersilia", "Tanaquil", "Egeria"],
        surnames=["Iunius", "Valerius", "Horatius", "Lucretius", "Tarquinius", "Claudius", "Fabius", "Cornelius",
                  "Aemilius", "Furius", "Manlius", "Postumius", "Verginius", "Menenius", "Sulpicius", "Servilius",
                  "Quinctius", "Larcius", "Cassius", "Cominius", "Aebutius", "Veturius", "Minucius", "Nautius",
                  "Geganius", "Sempronius", "Papirius", "Sergius", "Herminius", "Cloelius", "Tullius", "Mamilius",
                  "Atilius", "Genucius", "Sicinius", "Icilius"]),
    "italic": dict(
        male=["Gavius", "Gellius", "Herennius", "Statius", "Ovius", "Numerius", "Paccius", "Minatus", "Trebius",
              "Vibius", "Decius", "Marius", "Oppius", "Stenius", "Maras", "Salvius", "Novius", "Pacuvius",
              "Papius", "Lucius", "Titus", "Attus", "Mettius", "Nerius", "Pontius", "Dekis", "Niumsis",
              "Kaisis", "Upfals", "Heirens"],
        female=["Vibia", "Paculla", "Salvia", "Ovia", "Gavia", "Herennia", "Statia", "Trebia", "Minia", "Oppia",
                "Maria", "Decia", "Novia", "Pacuvia", "Ahvdia", "Saluta"],
        surnames=["Pontius", "Egnatius", "Papius", "Mutilus", "Staius", "Betitius", "Magius", "Satrius", "Decitius",
                  "Calavius", "Herennius", "Numisius", "Ofillius", "Popidius", "Trebatius", "Vettius", "Asinius",
                  "Poppaedius", "Vidacilius", "Lafrenius", "Afranius", "Tuditanus", "Attius", "Cluvius",
                  "Marcius", "Tullius", "Tatius", "Curtius", "Clausus", "Pompilius", "Volusius", "Annius"]),
    "etruscan": dict(
        male=["Larth", "Arnth", "Vel", "Aule", "Laris", "Sethre", "Tarchun", "Thefarie", "Caile", "Marce", "Avle",
              "Velthur", "Lars", "Vipe", "Lucumo", "Thucer", "Tite", "Cneve", "Spurie", "Venel",
              "Arath", "Mamarce", "Laucie", "Larce", "Pesna", "Rasce", "Uchtave", "Karcuna"],
        female=["Thanchvil", "Ramtha", "Larthia", "Velia", "Thana", "Arnthi", "Fasti", "Hastia", "Sethra",
                "Ravnthu", "Tita", "Velelia", "Culni", "Larthi", "Aulia", "Seianti"],
        surnames=["Velianas", "Porsenna", "Tulumnes", "Vipinas", "Spurinna", "Tarchna", "Velcha", "Matuna", "Pumpu",
                  "Cilnie", "Leinie", "Ceicna", "Curuna", "Apaiatru", "Alethna", "Hulchnie", "Tetnie", "Satie",
                  "Camna", "Cutu", "Velimna", "Pulena", "Partunu", "Murina", "Tarna", "Aninas", "Cumere",
                  "Thurmna", "Felsna", "Plecu", "Saties", "Tute", "Vuisina", "Petrui"]),
    "greek": dict(
        male=["Hieron", "Gelon", "Theron", "Dionysios", "Aristodemos", "Anaxilas", "Hippokrates", "Kleandros",
              "Milon", "Phalaris", "Terillos", "Polyzalos", "Thrasyboulos", "Phalanthos", "Archytas", "Pythagoras",
              "Empedokles", "Timoleon", "Agathokles", "Hermokrates", "Leontios", "Nikias", "Philistos",
              "Diokles", "Kallias", "Lysandros", "Demaretos", "Theokles", "Antiphemos", "Ainesidemos",
              "Skythes", "Kadmos", "Xenokrates", "Deinomenes", "Chromios", "Mikythos"],
        female=["Damarete", "Theano", "Aristomache", "Doris", "Arete", "Kleopatra", "Philistis", "Nossis",
                "Lanassa", "Myia", "Timycha", "Kleoboule", "Eurydike", "Phintys", "Melissa", "Kallisto"],
        surnames=["Deinomenous", "Ainesidemou", "Pantareos", "Xenokratous", "Hermokratous", "Molossou",
                  "Kleandrou", "Hipparinou", "Theodorou", "Lysiou", "Philippou", "Nikandrou", "Aristonos",
                  "Timonos", "Kallikratous", "Herakleidou", "Sosistratou", "Menekratous", "Diodorou",
                  "Antiochou", "Epikratous", "Polyxenou", "Archedamou", "Leptinou", "Andronos", "Eukleidou",
                  "Thrasonos", "Kratippou", "Dionos", "Mnasonos", "Zenonos", "Charondou"]),
    "iapygian": dict(
        male=["Opis", "Artas", "Dazos", "Plator", "Blattius", "Dasius", "Baledonas", "Graivas", "Dazimas",
              "Platur", "Staboas", "Morkos", "Taotor", "Kordomaos", "Artorres", "Dazomas", "Etthis", "Moldas",
              "Kailias", "Dazet", "Vallas", "Bostahes", "Laparedonas", "Solas", "Thotor", "Mazzes"],
        female=["Dazima", "Platura", "Etheta", "Tabara", "Lahona", "Baolihi", "Graiva", "Moldatthehia",
                "Theotoria", "Vallaidi", "Kazareihi", "Damatira", "Aprodita", "Venas"],
        surnames=["Dazihonas", "Platorrihi", "Artahias", "Moldahias", "Balakrahiaihi", "Staboaos", "Kraapati",
                  "Dazohonnihi", "Blatthihi", "Graivaihi", "Laparedonihi", "Taotorrihi", "Morkihi", "Kailomaihi",
                  "Solahiaihi", "Bostahiaihi", "Mazzihi", "Vallaihi", "Etthetaos", "Kordomaihi", "Arpanos",
                  "Salapinos", "Kanusinos", "Brentesinos", "Rudinos", "Hyretinos"]),
    "punic": dict(
        male=["Hanno", "Hamilcar", "Hasdrubal", "Mago", "Hannibal", "Bomilcar", "Himilco", "Gisco", "Adherbal",
              "Carthalo", "Bostar", "Maharbal", "Abdmelqart", "Eshmunazar", "Baalhanno", "Azrubaal", "Sophonba",
              "Bodashtart", "Abdeshmun", "Mattan", "Ithobaal", "Baalyaton", "Germelqart", "Shafat", "Milkyaton",
              "Arish", "Yehawmilk", "Bodmelqart", "Malchus", "Synalos"],
        female=["Elissa", "Sophonisba", "Arishat", "Batbaal", "Muttunbaal", "Amotmilkat", "Shiboulet",
                "Hannibaal", "Yzebel", "Tanit", "Sapanbaal", "Abibaal", "Kabdat", "Imilce"],
        surnames=["Magonid", "Barca", "bin Hanno", "bin Mago", "bin Gisco", "bin Hamilcar", "bin Bomilcar",
                  "bin Himilco", "bin Adherbal", "bin Bostar", "bin Mattan", "bin Arish", "bin Abdmelqart",
                  "bin Eshmunazar", "bin Baalhanno", "bin Carthalo", "bin Azrubaal", "bin Shafat",
                  "bin Bodashtart", "bin Milkyaton", "bin Ithobaal", "bin Malchus", "bin Germelqart",
                  "bin Abdeshmun", "bin Baalyaton", "bin Hasdrubal"]),
    "libyan": dict(
        male=["Gaia", "Zelalsen", "Iarbas", "Masinissa", "Syphax", "Micipsa", "Gulussa", "Mastanabal", "Naravas",
              "Oxyntas", "Hiempsal", "Jugurtha", "Gauda", "Massiva", "Capussa", "Lacumazes", "Mazaetullus",
              "Oezalces", "Ailymas", "Tychaeus", "Vermina", "Bocchus", "Baga", "Arabion", "Isalcas", "Zilalsan",
              "Medzes", "Aderbal"],
        female=["Tin Hinan", "Kahina", "Cyria", "Sophonba", "Tala", "Thiya", "Taninna", "Tiziri", "Dihya",
                "Markunda", "Tadla", "Tafsut", "Tamilla", "Damya"],
        surnames=["Massylian", "Masaesylian", "of Thugga", "of Cirta", "of Zama", "of Sicca", "of Theveste",
                  "of Capsa", "of Thysdrus", "of Mactar", "of Bulla", "of Hippo", "of Tacape", "of Leptis",
                  "of Sabratha", "of the Musulamii", "of the Gaetuli", "of the Nasamones", "of the Macae",
                  "of the Garamantes", "of the Zauekes", "of the Maxyes", "of the Gyzantes", "of the Auseans"]),
    "celtic": dict(
        male=["Brennus", "Ambigatus", "Bellovesus", "Segovesus", "Britomarus", "Viridomarus", "Aneroestus",
              "Concolitanus", "Ducarius", "Boiorix", "Catumandus", "Elitovius", "Lingonus", "Ariovistus",
              "Atepomarus", "Magalus", "Corolamus", "Dorulatus", "Vertamocorus", "Cincibilus", "Balanos",
              "Congonnetiacus", "Gargenus", "Etitovius", "Luernius", "Catmelus", "Moritasgus", "Esanekoti",
              "Uvamokozis", "Tanotalos", "Ateporix", "Komoneos"],
        female=["Brigindona", "Eponina", "Litavica", "Namantobogia", "Rosmerta", "Sirona", "Nantosuelta",
                "Adiatumara", "Bodua", "Camma", "Chiomara", "Esumagia", "Vlatucia", "Banona", "Sapsuta"],
        surnames=["Brennios", "Ambigatios", "Segomarios", "Viridomarios", "Boiorigios", "Atepomarios",
                  "Luernios", "Magalios", "Tanotaliknos", "Dannotaliknos", "Anarevisheos", "Uvamokozios",
                  "Koisios", "Trutiknos", "Lekatos", "Esopnios", "Plialethu", "Metelios", "Maeshilalos",
                  "Slanios", "Verkalos", "Kituios", "Rupelos", "Namunatios", "Piuonios", "Asouios"]),
    "island": dict(
        male=["Hampsicora", "Hostus", "Sardus", "Norax", "Iolaos", "Sidon", "Gargoris", "Habis", "Kyrnos",
              "Torbenus", "Bacoru", "Nispeni", "Tarsalia", "Urseti", "Asadiso", "Beviranus",
              "Carinius", "Gocaras", "Miaricora", "Nercau", "Ospitone", "Sisinnius", "Tubmar", "Cursius"],
        female=["Sardara", "Nora", "Olbia", "Tharra", "Kyrnia", "Ittiri", "Orune", "Lugula",
                "Barbara", "Antine", "Losa", "Arzana", "Desula"],
        surnames=["of Barumini", "of Nora", "of Sulci", "of Tharros", "of Olbia", "of Cornus", "of Bithia",
                  "of Alalia", "of Aleria", "of the Balari", "of the Iolei", "of the Corsi", "of the Ilienses",
                  "of the Vanacini", "of the Cervini", "of the Tibulati", "of Orgosolo", "of Serri", "of Abini",
                  "of Palmavera", "of Arrubiu", "of Losa", "of Santu Antine", "of Monte Prama"]),
}

# the wasteland placeholder has no culture of its own
NAMES["none"] = NAMES["latin"]
