"""World state at 245 AUC (509 BC). Source of truth for tools/build.py.

COUNTRIES: tag -> dict
  name, adj        English display name / adjective
  culture          key into CULTURES (gfx + flag style + map hue family)
  gov              republic | monarchy | tyranny | tribal   (mapped to vanilla ideologies for now)
  color            optional explicit map colour (r, g, b)
STATES: list of (key, name, owner, [provinces], population, {extras})
  extras: capital=True (country capital), vp={prov: (value, "City")}, cores=[tags], port=[provs]
Provinces are vanilla province ids (see tools/render_region.py for maps).
Every land province not listed here becomes impassable wasteland owned by WASTELAND_TAG.
"""

WASTELAND_TAG = "WLD"

CULTURES = {
    "latin":     {"gfx": "western_european_gfx", "gfx2d": "western_european_2d", "flag": "latin"},
    "italic":    {"gfx": "western_european_gfx", "gfx2d": "western_european_2d", "flag": "italic"},
    "etruscan":  {"gfx": "western_european_gfx", "gfx2d": "western_european_2d", "flag": "etruscan"},
    "greek":     {"gfx": "eastern_european_gfx", "gfx2d": "eastern_european_2d", "flag": "greek"},
    "iapygian":  {"gfx": "eastern_european_gfx", "gfx2d": "eastern_european_2d", "flag": "italic"},
    "punic":     {"gfx": "middle_eastern_gfx",   "gfx2d": "middle_eastern_2d",   "flag": "punic"},
    "libyan":    {"gfx": "african_gfx",          "gfx2d": "african_2d",          "flag": "tribal"},
    "celtic":    {"gfx": "western_european_gfx", "gfx2d": "western_european_2d", "flag": "tribal"},
    "island":    {"gfx": "western_european_gfx", "gfx2d": "western_european_2d", "flag": "tribal"},
    "none":      {"gfx": "western_european_gfx", "gfx2d": "western_european_2d", "flag": "none"},
}

COUNTRIES = {
    # --- Latium and its neighbours
    "ROM": dict(name="Rome", adj="Roman", culture="latin", gov="republic", color=(150, 25, 30)),
    "LAT": dict(name="Latin League", adj="Latin", culture="latin", gov="republic", color=(205, 120, 110)),
    "VOL": dict(name="Volsci", adj="Volscian", culture="italic", gov="tribal", color=(120, 140, 70)),
    "AEQ": dict(name="Aequi", adj="Aequian", culture="italic", gov="tribal", color=(95, 120, 60)),
    "SAB": dict(name="Sabini", adj="Sabine", culture="italic", gov="tribal", color=(150, 160, 90)),
    "MAR": dict(name="Marsic Peoples", adj="Marsic", culture="italic", gov="tribal", color=(110, 150, 110)),
    "SAM": dict(name="Samnium", adj="Samnite", culture="italic", gov="tribal", color=(60, 110, 60)),
    "PIC": dict(name="Picenum", adj="Picene", culture="italic", gov="tribal", color=(140, 175, 120)),
    "UMB": dict(name="Umbria", adj="Umbrian", culture="italic", gov="tribal", color=(170, 190, 100)),
    # --- Etruscan city-states
    "VEI": dict(name="Veii", adj="Veientine", culture="etruscan", gov="monarchy", color=(200, 140, 50)),
    "CAE": dict(name="Caere", adj="Caeritan", culture="etruscan", gov="monarchy", color=(220, 170, 80)),
    "TAR": dict(name="Tarquinii", adj="Tarquinian", culture="etruscan", gov="monarchy", color=(180, 110, 40)),
    "CLU": dict(name="Clusium", adj="Clusine", culture="etruscan", gov="monarchy", color=(160, 90, 30)),
    "VLT": dict(name="Volaterrae", adj="Volaterran", culture="etruscan", gov="monarchy", color=(210, 155, 100)),
    "ARR": dict(name="Arretium", adj="Arretine", culture="etruscan", gov="monarchy", color=(190, 125, 75)),
    "FEL": dict(name="Etruria Padana", adj="Padane Etruscan", culture="etruscan", gov="monarchy", color=(225, 190, 110)),
    "CAP": dict(name="Capua", adj="Capuan", culture="etruscan", gov="monarchy", color=(175, 135, 60)),
    # --- Greeks of Italy and Sicily
    "CUM": dict(name="Kyme", adj="Kymaean", culture="greek", gov="tyranny", color=(70, 120, 200)),
    "POS": dict(name="Poseidonia", adj="Poseidonian", culture="greek", gov="republic", color=(110, 160, 220)),
    "TAS": dict(name="Taras", adj="Tarantine", culture="greek", gov="monarchy", color=(40, 90, 180)),
    "MET": dict(name="Metapontion", adj="Metapontine", culture="greek", gov="republic", color=(130, 175, 230)),
    "KRO": dict(name="Kroton", adj="Crotoniate", culture="greek", gov="republic", color=(50, 100, 160)),
    "LOK": dict(name="Lokroi", adj="Locrian", culture="greek", gov="republic", color=(90, 140, 190)),
    "RHE": dict(name="Rhegion", adj="Rhegine", culture="greek", gov="republic", color=(100, 120, 210)),
    "SYR": dict(name="Syrakousai", adj="Syracusan", culture="greek", gov="republic", color=(30, 60, 150)),
    "GEL": dict(name="Gela", adj="Geloan", culture="greek", gov="tyranny", color=(80, 110, 170)),
    "AKR": dict(name="Akragas", adj="Akragantine", culture="greek", gov="republic", color=(60, 140, 200)),
    "ZAN": dict(name="Zankle", adj="Zanclean", culture="greek", gov="republic", color=(120, 150, 200)),
    "KAT": dict(name="Katane", adj="Catanaean", culture="greek", gov="republic", color=(150, 180, 230)),
    # --- other Italic / Iapygian / island peoples
    "OEN": dict(name="Oenotria", adj="Oenotrian", culture="italic", gov="tribal", color=(130, 110, 80)),
    "DAU": dict(name="Daunia", adj="Daunian", culture="iapygian", gov="monarchy", color=(160, 120, 160)),
    "PEU": dict(name="Peucetia", adj="Peucetian", culture="iapygian", gov="monarchy", color=(180, 140, 180)),
    "MES": dict(name="Messapia", adj="Messapian", culture="iapygian", gov="monarchy", color=(140, 90, 140)),
    "SIC": dict(name="Sikels", adj="Sikel", culture="italic", gov="tribal", color=(170, 130, 100)),
    "ELY": dict(name="Elymia", adj="Elymian", culture="italic", gov="monarchy", color=(190, 150, 120)),
    "SAR": dict(name="Nuragic Sardinia", adj="Nuragic", culture="island", gov="tribal", color=(150, 150, 130)),
    "COR": dict(name="Corsi", adj="Corsican", culture="island", gov="tribal", color=(120, 120, 110)),
    # --- northern Italy
    "LIG": dict(name="Ligures", adj="Ligurian", culture="celtic", gov="tribal", color=(70, 140, 140)),
    "INS": dict(name="Insubres", adj="Insubrian", culture="celtic", gov="tribal", color=(40, 120, 110)),
    "RAE": dict(name="Raeti", adj="Raetian", culture="celtic", gov="tribal", color=(100, 130, 150)),
    "VEN": dict(name="Veneti", adj="Venetic", culture="italic", gov="monarchy", color=(80, 160, 90)),
    # --- Africa
    "CAR": dict(name="Carthage", adj="Carthaginian", culture="punic", gov="republic", color=(110, 40, 120)),
    "LIB": dict(name="Libyans", adj="Libyan", culture="libyan", gov="tribal", color=(200, 180, 120)),
    "NUM": dict(name="Massylii", adj="Massylian", culture="libyan", gov="tribal", color=(170, 150, 90)),
    # --- placeholder owner of everything outside the playable area (phase 1 only)
    "WLD": dict(name="Terra Incognita", adj="Unknown", culture="none", gov="tribal", color=(90, 90, 90)),
}

S = []  # (key, name, owner, provinces, population, extras)
def st(key, name, owner, provs, pop, **ex):
    S.append((key, name, owner, provs, pop, ex))

# Latium
st("roma", "Roma", "ROM", [9904, 13413], 40_000, capital=True, vp={9904: (20, "Roma")}, port=[13413])
st("latium_vetus", "Latium Vetus", "LAT", [11846, 11882], 70_000, capital=True,
   vp={11846: (5, "Aricia"), 11882: (3, "Praeneste")}, port=[11846])
st("volscia", "Volscia", "VOL", [923, 9826], 50_000, capital=True, vp={923: (2, "Velitrae"), 9826: (2, "Anxur")}, port=[9826])
st("aequia", "Aequia", "AEQ", [3910], 20_000, capital=True, vp={3910: (1, "Carsioli")})
st("sabina", "Sabina", "SAB", [6926, 11790], 45_000, capital=True, vp={6926: (2, "Cures")})
st("marsica", "Marsica", "MAR", [9838, 6831], 35_000, capital=True, vp={6831: (1, "Marruvium")}, port=[9838])
# Samnium
st("samnium", "Samnium", "SAM", [963, 3923], 80_000, capital=True, vp={963: (3, "Bovianum")})
st("hirpinia", "Hirpinia", "SAM", [3958], 30_000, vp={3958: (1, "Maloenton")})
st("frentania", "Frentania", "SAM", [3966], 20_000, port=[3966])
st("picenum", "Picenum", "PIC", [967, 925], 50_000, capital=True, vp={925: (2, "Asculum")}, port=[967])
st("umbria", "Umbria", "UMB", [9924, 11861], 50_000, capital=True, vp={11861: (2, "Iguvium")}, port=[9924])
# Etruria
st("veii", "Veii", "VEI", [9794], 30_000, capital=True, vp={9794: (8, "Veii")})
st("caere", "Caere", "CAE", [11751], 30_000, capital=True, vp={11751: (6, "Caere")}, port=[11751])
st("tarquinii", "Tarquinii", "TAR", [6862, 6875], 40_000, capital=True, vp={6862: (6, "Tarquinii"), 6875: (3, "Vulci")}, port=[6862])
st("clusium", "Clusium", "CLU", [9750, 910], 45_000, capital=True, vp={9750: (8, "Clusium")})
st("perusia", "Perusia", "CLU", [3885], 20_000, vp={3885: (3, "Perusia")})
st("volaterrae", "Volaterrae", "VLT", [6946, 1616], 35_000, capital=True, vp={6946: (5, "Volaterrae"), 1616: (2, "Pisae")}, port=[6946])
st("vetulonia", "Vetulonia", "VLT", [11833], 15_000, vp={11833: (3, "Vetulonia")}, port=[11833])
st("arretium", "Arretium", "ARR", [9879], 25_000, capital=True, vp={9879: (5, "Arretium")})
st("faesulae", "Faesulae", "ARR", [9907, 11889], 20_000, vp={9907: (2, "Faesulae")})
st("felsina", "Felsina", "FEL", [6606, 3976, 9752, 3773], 50_000, capital=True, vp={6606: (6, "Felsina")})
st("spina", "Spina", "FEL", [6985, 6793, 782], 25_000, vp={6793: (4, "Spina")}, port=[6793])
st("mantua", "Mantua", "FEL", [11734, 3776], 20_000, vp={11734: (2, "Mantua")})
st("campania_etrusca", "Campania", "CAP", [11803, 955], 60_000, capital=True, vp={11803: (8, "Capua"), 955: (2, "Nuceria")})
# Magna Graecia
st("kyme", "Kyme", "CUM", [819], 25_000, capital=True, vp={819: (8, "Kyme")}, port=[819])
st("poseidonia", "Poseidonia", "POS", [851], 15_000, capital=True, vp={851: (4, "Poseidonia")}, port=[851])
st("oenotria", "Oenotria", "OEN", [3968, 6972], 25_000, capital=True, vp={3968: (1, "Pandosia")})
st("bruttium", "Bruttium", "OEN", [3901], 15_000)
st("taras", "Taras", "TAS", [11837], 30_000, capital=True, vp={11837: (10, "Taras")}, port=[11837])
st("metapontion", "Metapontion", "MET", [9856], 15_000, capital=True, vp={9856: (4, "Metapontion")}, port=[9856])
st("kroton", "Kroton", "KRO", [12098], 35_000, capital=True, vp={12098: (8, "Kroton")}, port=[12098])
st("sybaritis", "Sybaritis", "KRO", [10027], 15_000, vp={10027: (3, "Sybaris")}, port=[10027])
st("lokroi", "Lokroi", "LOK", [12066], 15_000, capital=True, vp={12066: (4, "Lokroi")}, port=[12066])
st("rhegion", "Rhegion", "RHE", [9990], 15_000, capital=True, vp={9990: (4, "Rhegion")}, port=[9990])
st("daunia", "Daunia", "DAU", [883, 6939, 6980], 45_000, capital=True, vp={883: (2, "Arpi")}, port=[6980])
st("peucetia", "Peucetia", "PEU", [9784, 6843], 35_000, capital=True, vp={9784: (2, "Caelia")}, port=[9784])
st("messapia", "Messapia", "MES", [11998, 6979], 40_000, capital=True, vp={11998: (3, "Brentesion")}, port=[11998])
# Sicily
st("syrakousai", "Syrakousai", "SYR", [13256], 30_000, capital=True, vp={13256: (12, "Syrakousai")}, port=[13256])
st("gela", "Gela", "GEL", [1009], 20_000, capital=True, vp={1009: (6, "Gela")}, port=[1009])
st("akragas", "Akragas", "AKR", [7147], 20_000, capital=True, vp={7147: (6, "Akragas")}, port=[7147])
st("zankle", "Zankle", "ZAN", [4159, 1156], 20_000, capital=True, vp={4159: (5, "Zankle")}, port=[4159])
st("himera", "Himera", "ZAN", [3857], 10_000, vp={3857: (3, "Himera")}, port=[3857])
st("katane", "Katane", "KAT", [4014], 20_000, capital=True, vp={4014: (4, "Katane")}, port=[4014])
st("sikelia", "Sikelia", "SIC", [12047], 40_000, capital=True, vp={12047: (2, "Henna")})
st("elymia", "Elymia", "ELY", [7059], 20_000, capital=True, vp={7059: (3, "Segesta")}, port=[7059])
st("panormos", "Panormos", "CAR", [10074], 30_000, vp={10074: (6, "Ziz")}, port=[10074])
# Islands
st("karalis", "Karalis", "CAR", [11773, 902], 25_000, vp={11773: (4, "Karalis")}, port=[11773])
st("tharros", "Tharros", "CAR", [11874], 15_000, vp={11874: (3, "Tharros")}, port=[11874])
st("malta", "Malta", "CAR", [12003], 8_000, vp={12003: (2, "Melite")}, port=[12003])
st("sardinia_septentrionalis", "Nuragic North", "SAR", [6891, 9772, 9863], 45_000, capital=True, vp={9772: (1, "Barumini")})
st("sardinia_centralis", "Nuragic Highlands", "SAR", [11824, 11755], 35_000)
st("corsica", "Corsica", "COR", [9851, 11804, 3838], 30_000, capital=True, vp={11804: (2, "Alalia")}, port=[11804])
# Northern Italy
st("taurinia", "Taurinia", "LIG", [611, 3782, 6780, 11570, 6635, 9738, 11730, 9741, 11726, 776, 6790], 40_000,
   vp={6780: (2, "Taurasia")})
st("liguria", "Liguria", "LIG", [771, 6788, 770, 11723, 3772, 11721, 11891, 6973], 50_000,
   capital=True, vp={6788: (3, "Genua")}, port=[6788])
st("insubria", "Insubria", "INS", [607, 6661, 9584, 3780, 969, 773], 50_000, capital=True, vp={3780: (4, "Mediolanum")})
st("raetia", "Raetia", "RAE", [656, 6675, 9630, 11598, 11615, 6631, 9598, 11568, 11587], 40_000, capital=True,
   vp={6631: (1, "Tridentum")})
st("venetia", "Venetia", "VEN", [3604, 3657, 628, 9613, 11584, 6656], 45_000, capital=True,
   vp={3604: (5, "Ateste"), 11584: (2, "Altinum")}, port=[11584])
st("venetia_occidentalis", "Western Venetia", "VEN", [603, 9582], 25_000, vp={603: (2, "Verona")})
# Africa
st("carthago", "Carthago", "CAR", [11969, 10091], 100_000, capital=True, vp={11969: (25, "Qart-Hadasht")}, port=[11969])
st("utica", "Utica", "CAR", [9994, 4163, 1046], 30_000, vp={9994: (5, "Utica")}, port=[9994])
st("libya_punica", "Punic Hinterland", "CAR", [7180, 7077, 4061, 1037], 60_000)
st("byzacium", "Byzacium", "CAR", [7162, 4129, 11921], 40_000, vp={11921: (3, "Hadrumetum")}, port=[11921])
st("libya_septentrionalis", "Libya", "LIB", [11935, 10026, 7005, 11957], 35_000, capital=True, vp={10026: (1, "Thysdrus")})
st("libya_australis", "Inner Libya", "LIB", [3987, 10082, 9983, 12000, 1105, 4992], 25_000)
st("massylia", "Massylia", "NUM", [1160, 1058, 11953, 7081, 12051], 50_000, capital=True, vp={11953: (2, "Thugga")})
st("massylia_interior", "Massylian Highlands", "NUM", [1141, 9943, 12034], 30_000)

STATES = S

BOOKMARK_COUNTRIES = ["ROM", "CAR", "CLU", "LAT", "VEI", "SAM", "SYR", "TAS"]
