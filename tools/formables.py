"""Formable nations: Italy united under Rome, the Punic empire of the western sea (no game needed, ~1 s).

Run AFTER tools/world.py (reads history/states for the state ids) - and after content.py, it only adds files:
  common/decisions/ante_formables.txt       the two decisions, in the categories ROM_latin_culture / CAR_punic_world
  common/ideas/ante_formable_ideas.txt      Italy United! / The Leader of the Western Mediterranean Sea!
  gfx/flags/(medium/, small/)<cosmetic>.tga  the new flags (own art)
  localisation/english/ante_formables_l_english.yml   names, decisions, spirits, tooltips

Rome:     controls all of peninsular Italy (the states of the 27 Italian peoples south of the Po) AND either all of
          Sicily or all of the Po valley -> 'Italia' (Republic) / 'Regnum Italiae' (Kingdom), cores on every state
          needed, Italy United!
Carthage: controls the land its focus tree goes for - Libya, Numidia, Sardinia, the Greek cities of Sicily and
          Tartessos (allies and subjects such as Gadir and the Elymians are not conquests and are not needed) ->
          'Punic Empire', cores, The Leader of the Western Mediterranean Sea!
"""
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw

MOD = Path(__file__).resolve().parent.parent

PENINSULA = "ROM LAT VOL AEQ SAB MAR SAM PIC UMB VEI CAE TAR CLU VLT ARR CAP CUM POS TAS MET KRO LOK RHE OEN DAU PEU MES".split()
PO = "FEL INS VEN".split()
SICILY = "SYR GEL AKR ZAN KAT SIC ELY".split()
PUNIC = "CAR LIB MSY MSS SAR TTS AKR GEL KAT SYR ZAN".split()

COSMETIC = {   # tag: (name, definite name, adjective, flag colours: field, emblem)
    "ROM_ITALIA": ("Italia", "Italia", "Italian", (122, 24, 40), (226, 182, 72)),
    "ROM_REGNUM_ITALIAE": ("Regnum Italiae", "the Kingdom of Italy", "Italian", (70, 24, 96), (226, 182, 72)),
    "CAR_PUNIC_EMPIRE": ("Punic Empire", "the Punic Empire", "Punic", (88, 20, 92), (232, 196, 96)),
}
IDEAS = {
    "ROM_italy_united_spirit": ("Italy United!", "generic_pp_unity_bonus",
                                {"stability_factor": 0.15, "political_power_gain": 0.25, "war_support_factor": 0.10,
                                 "conscription": 0.03, "production_speed_buildings_factor": 0.10,
                                 "industrial_capacity_factory": 0.05}),
    "CAR_western_sea_spirit": ("The Leader of the Western Mediterranean Sea!", "generic_navy_bonus",
                               {"stability_factor": 0.15, "political_power_gain": 0.25, "trade_opinion_factor": 0.25,
                                "production_speed_dockyard_factor": 0.15, "naval_damage_factor": 0.10,
                                "industrial_capacity_factory": 0.05}),
}


def states_of(tags):
    out = []
    for fp in (MOD / "history" / "states").glob("*.txt"):
        t = fp.read_text(encoding="utf-8-sig")
        m, o = re.search(r"\bid\s*=\s*(\d+)", t), re.search(r"\bowner\s*=\s*(\w+)", t)
        if m and o and o.group(1) in tags:
            out.append(int(m.group(1)))
    return sorted(out)


def controls(ids):
    return "\n".join(f"\tcontrols_state = {i}" for i in ids)


def flag(key, field, gold):
    """a purple/red field with a golden emblem: a laurel wreath (Italy) or the sign of Tanit (Carthage)"""
    S = 4
    W, H = 82 * S, 52 * S
    im = Image.new("RGBA", (W, H), field + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W - 1, 5 * S), fill=gold + (255,))
    d.rectangle((0, H - 5 * S, W - 1, H - 1), fill=gold + (255,))
    cx, cy = W // 2, H // 2
    if key.startswith("CAR"):     # the sign of Tanit: a triangle, a bar with raised ends, a disc
        d.polygon([(cx, cy - 6 * S), (cx - 11 * S, cy + 16 * S), (cx + 11 * S, cy + 16 * S)], fill=gold + (255,))
        d.rectangle((cx - 13 * S, cy - 6 * S, cx + 13 * S, cy - 3 * S), fill=gold + (255,))
        d.rectangle((cx - 13 * S, cy - 12 * S, cx - 10 * S, cy - 3 * S), fill=gold + (255,))
        d.rectangle((cx + 10 * S, cy - 12 * S, cx + 13 * S, cy - 3 * S), fill=gold + (255,))
        d.ellipse((cx - 6 * S, cy - 18 * S, cx + 6 * S, cy - 7 * S), fill=gold + (255,))
    else:                        # a laurel wreath around a star (Italy) / a crown above it (the kingdom)
        for deg in range(-235, 56, 15):   # leaves all round, open at the top
            a = math.radians(deg)
            x = cx + math.cos(a) * 15 * S
            y = cy - 2 * S - math.sin(a) * 15 * S
            d.ellipse((x - 3 * S, y - 2 * S, x + 3 * S, y + 2 * S), fill=gold + (255,))
        pts = []
        for i in range(10):
            r = (7 if i % 2 == 0 else 3) * S
            a = math.pi / 2 + math.pi * i / 5
            pts.append((cx + r * math.cos(a), cy - 2 * S - r * math.sin(a)))
        d.polygon(pts, fill=gold + (255,))
        if "REGNUM" in key:
            d.polygon([(cx - 8 * S, cy - 14 * S), (cx - 8 * S, cy - 20 * S), (cx - 4 * S, cy - 17 * S), (cx, cy - 21 * S),
                       (cx + 4 * S, cy - 17 * S), (cx + 8 * S, cy - 20 * S), (cx + 8 * S, cy - 14 * S)], fill=gold + (255,))
    big = im.resize((82, 52), Image.LANCZOS)
    for sub, size in (("", (82, 52)), ("medium", (41, 26)), ("small", (10, 7))):
        p = MOD / "gfx" / "flags" / sub / f"{key}.tga" if sub else MOD / "gfx" / "flags" / f"{key}.tga"
        p.parent.mkdir(parents=True, exist_ok=True)
        big.resize(size, Image.LANCZOS).convert("RGBA").save(p)


def main():
    pen, po, sic, pun = states_of(PENINSULA), states_of(PO), states_of(SICILY), states_of(PUNIC)
    loc = {}
    rome_needed = sorted(set(pen + po + sic))
    rome = f"""ROM_latin_culture = {{
	ROM_form_italia = {{
		icon = GFX_decision_generic_formable_nations
		allowed = {{ original_tag = ROM }}
		visible = {{ NOT = {{ has_country_flag = ROM_italy_formed }} }}
		available = {{
			custom_trigger_tooltip = {{
				tooltip = ROM_TT_ITALY_PENINSULA
{_ind(controls(pen), 3)}
			}}
			custom_trigger_tooltip = {{
				tooltip = ROM_TT_SICILY_OR_PO
				OR = {{
					AND = {{
{_ind(controls(sic), 5)}
					}}
					AND = {{
{_ind(controls(po), 5)}
					}}
				}}
			}}
		}}
		fire_only_once = yes
		cost = 50
		complete_effect = {{
			set_country_flag = ROM_italy_formed
			if = {{ limit = {{ has_country_flag = ROM_kingdom }} set_cosmetic_tag = ROM_REGNUM_ITALIAE }}
			else = {{ set_cosmetic_tag = ROM_ITALIA }}
			every_state = {{
				limit = {{ is_owned_by = ROOT OR = {{ {" ".join(f"state = {i}" for i in rome_needed)} }} }}
				add_core_of = ROOT
			}}
			add_ideas = ROM_italy_united_spirit
		}}
		ai_will_do = {{ base = 100 }}
	}}
}}
"""
    carthage = f"""CAR_punic_world = {{
	CAR_form_punic_empire = {{
		icon = GFX_decision_generic_formable_nations
		allowed = {{ original_tag = CAR }}
		visible = {{ NOT = {{ has_country_flag = CAR_empire_formed }} }}
		available = {{
			custom_trigger_tooltip = {{
				tooltip = CAR_TT_PUNIC_LANDS
{_ind(controls(pun), 3)}
			}}
		}}
		fire_only_once = yes
		cost = 50
		complete_effect = {{
			set_country_flag = CAR_empire_formed
			set_cosmetic_tag = CAR_PUNIC_EMPIRE
			every_state = {{
				limit = {{ is_owned_by = ROOT OR = {{ {" ".join(f"state = {i}" for i in pun)} }} }}
				add_core_of = ROOT
			}}
			add_ideas = CAR_western_sea_spirit
		}}
		ai_will_do = {{ base = 100 }}
	}}
}}
"""
    (MOD / "common" / "decisions" / "ante_formables.txt").write_text(
        "# Generated by tools/formables.py - Italy united, the Punic empire\n" + rome + "\n" + carthage,
        encoding="utf-8", newline="\n")
    ideas = ["# Generated by tools/formables.py", "ideas = {", "\tcountry = {"]
    for key, (name, pic, mods) in IDEAS.items():
        ideas += [f"\t\t{key} = {{", f"\t\t\tpicture = {pic}", "\t\t\tallowed = { always = no }", "\t\t\tremoval_cost = -1",
                  "\t\t\tmodifier = {"] + [f"\t\t\t\t{k} = {v}" for k, v in mods.items()] + ["\t\t\t}", "\t\t}"]
        loc[key] = name
    ideas += ["\t}", "}"]
    (MOD / "common" / "ideas" / "ante_formable_ideas.txt").write_text("\n".join(ideas) + "\n", encoding="utf-8", newline="\n")
    for key, (name, defn, adj, field, gold) in COSMETIC.items():
        flag(key, field, gold)
        for suf in ("", "_democratic", "_neutrality", "_fascism", "_communism"):
            loc[f"{key}{suf}"] = name
            loc[f"{key}{suf}_DEF"] = defn
            loc[f"{key}{suf}_ADJ"] = adj
    loc.update({
        "ROM_form_italia": "Italia",
        "ROM_form_italia_desc": "From the Strait to the Po - or to the Strait of Messana: all the peoples of Italy obey Rome. "
                                "Let the world call this land by one name.",
        "ROM_TT_ITALY_PENINSULA": f"Controls all of peninsular Italy ({len(pen)} states, from Etruria and Picenum to the Strait)",
        "ROM_TT_SICILY_OR_PO": f"Controls all of Sicily ({len(sic)} states) or all of the Po valley ({len(po)} states)",
        "CAR_form_punic_empire": "The Punic Empire",
        "CAR_form_punic_empire_desc": "Libya and Numidia, Sardinia, the Greek cities of Sicily and the silver land of "
                                      "Tartessos: the western sea is a Punic lake.",
        "CAR_TT_PUNIC_LANDS": f"Controls Libya, Numidia, Sardinia, the Greek cities of Sicily and Tartessos ({len(pun)} states)",
    })
    (MOD / "localisation" / "english" / "ante_formables_l_english.yml").write_text(
        "l_english:\n" + "".join(f' {k}:0 "{v}"\n' for k, v in loc.items()), encoding="utf-8-sig", newline="\n")
    print(f"written: Italia ({len(pen)} + {len(sic)} Sicily or {len(po)} Po), Punic Empire ({len(pun)} states), flags")


def _ind(text, tabs):
    return "\n".join("\t" * tabs + l.lstrip("\t") if l.strip() else l for l in text.splitlines())


if __name__ == "__main__":
    main()
