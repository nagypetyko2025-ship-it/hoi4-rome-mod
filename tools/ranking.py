"""Great Powers screen (round 56/57): a "Powers" button in the top right corner opens a big window, laid out like the
research screen: five lanes, one per tier, each holding the cards (flag, name, strength) of the countries in it.

Once a month (and at game start) every country gets a strength score; the TOP best are sorted into the global array
`global.ante_ranking` and get a tier from their score measured against the strongest (the 509 BC world has one
giant, Persia, about four times Carthage, so the steps are steep):

    I   Hegemon         >= 50 % of the leader
    II  Great Power     >= 20 %
    III Major Power     >= 10.5 %
    IV  Regional Power  >= 7.5 %
    V   Minor Power     the rest of the top TOP

Score = 2 x battalions + 3 x military workshops + 2 x civilian workshops + 2 x shipyards + 2 x ships + controlled states.

Two scripted GUIs (the reliable way to open and close a window): `ante_ranking_button` (always there) and
`ante_ranking_screen` (visible while the player's country has the flag ANTE_rank_open).

Writes common/scripted_effects, common/on_actions, common/scripted_guis, common/scripted_localisation,
interface/ante_ranking.gui and localisation. Run after content.py (independent of world.py).
"""
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent
TOP = 15
TIERS = [  # (min % of the leader, name, colour)
    (50, "Hegemon", "Y"),
    (20, "Great Power", "H"),
    (10.5, "Major Power", "G"),
    (7.5, "Regional Power", "W"),
    (0, "Minor Power", "g"),
]
ROMAN = ["I", "II", "III", "IV", "V"]
SCORE = [("num_battalions", 2), ("num_of_military_factories", 3), ("num_of_civilian_factories", 2),
         ("num_of_naval_factories", 2), ("num_ships", 2), ("num_of_controlled_states", 1)]
COUNTED = "exists = yes NOT = { tag = WLD } num_of_controlled_states > 0"

# layout of the big window
W, H = 1060, 720
LANE_X, LANE_W, LANE_GAP = 20, 198, 6
LANE_Y = 96
CARD_W, CARD_H = LANE_W - 8, 44
BUTTON_X = -400  # left edge of the button, measured from the right edge of the screen


def bom(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8-sig")


def plain(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def update_effect():
    score = ["\t\t\tset_variable = { ante_power = 0 }"]
    for var, w in SCORE:
        score.append(f"\t\t\tset_temp_variable = {{ ante_t = {var} }} multiply_temp_variable = {{ ante_t = {w} }} "
                     "add_to_variable = { ante_power = ante_t }")
    lines = ["ANTE_update_ranking = {",
             "\tclear_array = global.ante_ranking"]
    lines += [f"\tclear_array = global.ante_tier_{i}" for i in range(1, len(TIERS) + 1)]
    lines += ["\tset_variable = { global.ante_top_power = 0 }",
              "\tevery_country = {",
              "\t\tset_variable = { ante_rank_prev = ante_rank }",
              "\t\tset_variable = { ante_rank = 0 }",
              "\t\tclr_country_flag = ante_ranked",
              f"\t\tif = {{ limit = {{ {COUNTED} }}"] + score + ["\t\t}", "\t}"]
    for k in range(1, TOP + 1):
        lines += [
            "\tset_variable = { global.ante_best = 0 }",
            f"\tevery_country = {{ limit = {{ {COUNTED} NOT = {{ has_country_flag = ante_ranked }} }}",
            "\t\tif = { limit = { check_variable = { ante_power > global.ante_best } }",
            "\t\t\tset_variable = { global.ante_best = ante_power }",
            "\t\t\tset_variable = { global.ante_pick = THIS }",
            "\t\t}",
            "\t}",
            "\tif = { limit = { check_variable = { global.ante_best > 0 } }",
            "\t\tvar:global.ante_pick = {",
            "\t\t\tset_country_flag = ante_ranked",
            f"\t\t\tset_variable = {{ ante_rank = {k} }}",
            "\t\t\tadd_to_array = { global.ante_ranking = THIS }",
            "\t\t}",
        ]
        if k == 1:
            lines.append("\t\tset_variable = { global.ante_top_power = global.ante_best }")
        lines.append("\t}")
    # tiers (in rank order, so every lane is sorted) and the movement since last month
    tier = []
    for i, (pct, *_rest) in enumerate(TIERS, 1):
        kw = "if" if i == 1 else "else_if"
        put = f"set_variable = {{ ante_tier = {i} }} add_to_array = {{ global.ante_tier_{i} = THIS }}"
        if pct:
            tier.append(f"\t\t{kw} = {{ limit = {{ check_variable = {{ ante_t > {pct - 0.01:g} }} }} {put} }}")
        else:
            tier.append(f"\t\telse = {{ {put} }}")
    lines += ["\tfor_each_scope_loop = {",
              "\t\tarray = global.ante_ranking",
              "\t\tset_temp_variable = { ante_t = ante_power }",
              "\t\tmultiply_temp_variable = { ante_t = 100 }",
              "\t\tif = { limit = { check_variable = { global.ante_top_power > 0 } }",
              "\t\t\tdivide_temp_variable = { ante_t = global.ante_top_power }",
              "\t\t}"] + tier + [
              "\t\tset_variable = { ante_rank_move = ante_rank_prev }",
              "\t\tsubtract_from_variable = { ante_rank_move = ante_rank }",
              "\t}",
              "\tadd_to_variable = { global.ante_rank_version = 1 }",
              "}"]
    return "\n".join(lines) + "\n"


ON_ACTIONS = """# Generated by tools/ranking.py - the Great Powers are recounted once a month (WLD, the wilds, always exists)
on_actions = {
	on_startup = {
		effect = {
			WLD = { ANTE_update_ranking = yes }
		}
	}
	on_monthly = {
		effect = {
			if = { limit = { tag = WLD } ANTE_update_ranking = yes }
		}
	}
}
"""


def scripted_gui():
    lanes = "\n".join(f"""			ante_rank_lane_{i} = {{
				array = global.ante_tier_{i}
				change_scope = yes
				entry_container = "ante_rank_card"
			}}""" for i in range(1, len(TIERS) + 1))
    return f"""# Generated by tools/ranking.py - the Great Powers button and screen
scripted_gui = {{
	ante_ranking_button = {{
		context_type = player_context
		window_name = "ante_ranking_button_window"
		visible = {{ always = yes }}
		effects = {{
			ante_rank_button_click = {{
				if = {{ limit = {{ has_country_flag = ANTE_rank_open }} clr_country_flag = ANTE_rank_open }}
				else = {{ set_country_flag = ANTE_rank_open }}
			}}
		}}
		ai_enabled = {{ always = no }}
	}}

	ante_ranking_screen = {{
		context_type = player_context
		window_name = "ante_ranking_screen_window"
		visible = {{ has_country_flag = ANTE_rank_open }}
		effects = {{
			ante_rank_close_click = {{
				clr_country_flag = ANTE_rank_open
			}}
		}}
		dynamic_lists = {{
{lanes}
		}}
		properties = {{
			ante_rank_flag = {{
				image = "[This.GetFlag]"
			}}
		}}
		ai_enabled = {{ always = no }}
	}}
}}
"""


def gui():
    lanes = []
    for i in range(1, len(TIERS) + 1):
        x = LANE_X + (i - 1) * (LANE_W + LANE_GAP)
        lanes.append(f"""
		containerWindowType = {{
			name = "ante_rank_lane_box_{i}"
			position = {{ x = {x} y = {LANE_Y} }}
			size = {{ width = {LANE_W} height = {H - LANE_Y - 24} }}
			clipping = yes
			background = {{
				name = "ante_rank_lane_bg_{i}"
				quadTextureSprite = "GFX_tiled_window_transparent"
			}}
			instantTextBoxType = {{
				name = "ante_rank_lane_numeral_{i}"
				position = {{ x = 0 y = 6 }}
				font = "hoi_36header"
				text = "ANTE_RANK_NUMERAL_{i}"
				format = centre
				maxWidth = {LANE_W}
				maxHeight = 40
				fixedsize = yes
			}}
			instantTextBoxType = {{
				name = "ante_rank_lane_name_{i}"
				position = {{ x = 0 y = 48 }}
				font = "hoi_20bs"
				text = "ANTE_RANK_TIER_{i}"
				format = centre
				maxWidth = {LANE_W}
				maxHeight = 24
				fixedsize = yes
				pdx_tooltip = "ANTE_RANK_LANE_TT_{i}"
			}}
			instantTextBoxType = {{
				name = "ante_rank_lane_rule_{i}"
				position = {{ x = 0 y = 72 }}
				font = "hoi_16mbs"
				text = "ANTE_RANK_RULE_{i}"
				format = centre
				maxWidth = {LANE_W}
				maxHeight = 20
				fixedsize = yes
			}}
			gridboxtype = {{
				name = "ante_rank_lane_{i}"
				position = {{ x = 4 y = 100 }}
				size = {{ width = {CARD_W} height = {H - LANE_Y - 24 - 104} }}
				slotsize = {{ width = {CARD_W} height = {CARD_H + 4} }}
				max_slots_horizontal = 1
				format = "UPPER_LEFT"
			}}
		}}""")
    return f"""# Generated by tools/ranking.py - the Great Powers button (top right corner, left of the music and army buttons)
# and the screen it opens (centre of the screen, five lanes like the research screen)
guiTypes = {{
	containerWindowType = {{
		name = "ante_ranking_button_window"
		orientation = upper_right
		position = {{ x = {BUTTON_X} y = 44 }}
		size = {{ width = 94 height = 31 }}
		buttonType = {{
			name = "ante_rank_button"
			quadTextureSprite = "GFX_button_94x31"
			position = {{ x = 0 y = 0 }}
			buttonText = "ANTE_RANK_BUTTON"
			buttonFont = "hoi_16mbs"
			pdx_tooltip = "ANTE_RANK_BUTTON_TT"
		}}
	}}

	containerWindowType = {{
		name = "ante_ranking_screen_window"
		orientation = center
		position = {{ x = {-W // 2} y = {-H // 2} }}
		size = {{ width = {W} height = {H} }}
		moveable = yes
		background = {{
			name = "ante_rank_screen_bg"
			quadTextureSprite = "GFX_tiled_window_2b_border"
		}}
		instantTextBoxType = {{
			name = "ante_rank_title"
			position = {{ x = 0 y = 14 }}
			font = "hoi_36header"
			text = "ANTE_RANK_TITLE"
			format = centre
			maxWidth = {W}
			maxHeight = 40
			fixedsize = yes
		}}
		instantTextBoxType = {{
			name = "ante_rank_subtitle"
			position = {{ x = 0 y = 58 }}
			font = "hoi_16mbs"
			text = "ANTE_RANK_SUBTITLE"
			format = centre
			maxWidth = {W}
			maxHeight = 22
			fixedsize = yes
			pdx_tooltip = "ANTE_RANK_BUTTON_TT"
		}}
		buttonType = {{
			name = "ante_rank_close"
			quadTextureSprite = "GFX_closebutton"
			position = {{ x = {W - 46} y = 12 }}
		}}
{"".join(lanes)}
	}}

	containerWindowType = {{
		name = "ante_rank_card"
		position = {{ x = 0 y = 0 }}
		size = {{ width = {CARD_W} height = {CARD_H} }}
		background = {{
			name = "ante_rank_card_bg"
			quadTextureSprite = "GFX_tiled_window_1b_thin_border"
		}}
		instantTextBoxType = {{
			name = "ante_rank_number"
			position = {{ x = 2 y = 13 }}
			font = "hoi_16mbs"
			text = "ANTE_RANK_NUMBER"
			format = right
			maxWidth = 24
			maxHeight = 20
			fixedsize = yes
		}}
		iconType = {{
			name = "ante_rank_flag"
			quadTextureSprite = "GFX_player_flag"
			position = {{ x = 30 y = 6 }}
			scale = 0.6
			pdx_tooltip = "ANTE_RANK_ENTRY_TT"
		}}
		instantTextBoxType = {{
			name = "ante_rank_name"
			position = {{ x = 84 y = 4 }}
			font = "hoi_16mbs"
			text = "ANTE_RANK_NAME"
			format = left
			maxWidth = {CARD_W - 88}
			maxHeight = 18
			fixedsize = yes
			pdx_tooltip = "ANTE_RANK_ENTRY_TT"
		}}
		instantTextBoxType = {{
			name = "ante_rank_strength"
			position = {{ x = 84 y = 22 }}
			font = "hoi_16mbs"
			text = "ANTE_RANK_STRENGTH"
			format = left
			maxWidth = {CARD_W - 88}
			maxHeight = 18
			fixedsize = yes
			pdx_tooltip = "ANTE_RANK_ENTRY_TT"
		}}
	}}
}}
"""


def scripted_loc():
    tier = [f"\ttext = {{ trigger = {{ check_variable = {{ ante_tier = {i} }} }} localization_key = ANTE_RANK_TIER_{i} }}"
            for i in range(1, len(TIERS) + 1)]
    move = ["\ttext = { trigger = { check_variable = { ante_rank_prev = 0 } } localization_key = ANTE_RANK_MOVE_NEW }",
            "\ttext = { trigger = { check_variable = { ante_rank_move > 0 } } localization_key = ANTE_RANK_MOVE_UP }",
            "\ttext = { trigger = { check_variable = { ante_rank_move < 0 } } localization_key = ANTE_RANK_MOVE_DOWN }",
            "\ttext = { localization_key = ANTE_RANK_MOVE_SAME }"]
    return ("# Generated by tools/ranking.py\n"
            "defined_text = {\n\tname = GetAnteRankTier\n" + "\n".join(tier) + "\n}\n"
            "defined_text = {\n\tname = GetAnteRankMove\n" + "\n".join(move) + "\n}\n")


def loc():
    rule = "2 per battalion, 3 per military workshop, 2 per civilian workshop, 2 per shipyard, 2 per ship, 1 per state"
    rows = [
        'ANTE_RANK_BUTTON:0 "Powers"',
        f'ANTE_RANK_BUTTON_TT:0 "§YGreat Powers of the Known World§!\\nThe {TOP} strongest countries, recounted on the '
        f'first of every month.\\nStrength: {rule}.\\n\\n§GClick§! to open or close."',
        'ANTE_RANK_TITLE:0 "Great Powers of the Known World"',
        f'ANTE_RANK_SUBTITLE:0 "The {TOP} strongest countries, measured against the strongest of all. Recounted on the '
        'first of every month."',
        'ANTE_RANK_NUMBER:0 "[?This.ante_rank|0]."',
        'ANTE_RANK_NAME:0 "[This.GetName]"',
        'ANTE_RANK_STRENGTH:0 "Strength §Y[?This.ante_power|0]§! [This.GetAnteRankMove]"',
        'ANTE_RANK_ENTRY_TT:0 "§Y[This.GetName]§!: [This.GetAnteRankTier]\\nStrength: §Y[?This.ante_power|0]§! '
        '(the strongest: [?global.ante_top_power|0])\\n' + rule + '"',
        'ANTE_RANK_MOVE_NEW:0 "§G(new)§!"',
        'ANTE_RANK_MOVE_UP:0 "§G(+[?This.ante_rank_move|0])§!"',
        'ANTE_RANK_MOVE_DOWN:0 "§R([?This.ante_rank_move|0])§!"',
        'ANTE_RANK_MOVE_SAME:0 ""',
    ]
    for i, (p, n, c) in enumerate(TIERS, 1):
        rows += [f'ANTE_RANK_TIER_{i}:0 "§{c}{n}§!"',
                 f'ANTE_RANK_NUMERAL_{i}:0 "§{c}{ROMAN[i - 1]}§!"',
                 f'ANTE_RANK_RULE_{i}:0 "' + (f"at least {p:g}% of the strongest" if p else f"the rest of the top {TOP}") + '"',
                 f'ANTE_RANK_LANE_TT_{i}:0 "§{c}{ROMAN[i - 1]} {n}§!: '
                 + (f"at least {p:g}% of the strength of the strongest country." if p
                    else f"the other countries of the top {TOP}.") + '"']
    return "l_english:\n" + "".join(f" {r}\n" for r in rows)


def main():
    plain(MOD / "common/scripted_effects/ante_ranking_effects.txt",
          "# Generated by tools/ranking.py - the monthly count behind the Great Powers screen\n" + update_effect())
    plain(MOD / "common/on_actions/ante_ranking_on_actions.txt", ON_ACTIONS)
    plain(MOD / "common/scripted_guis/ante_ranking_scripted_gui.txt", scripted_gui())
    plain(MOD / "common/scripted_localisation/ante_ranking_scripted_localisation.txt", scripted_loc())
    plain(MOD / "interface/ante_ranking.gui", gui())
    bom(MOD / "localisation/english/ante_ranking_l_english.yml", loc())
    print(f"Great Powers screen: top {TOP} in {len(TIERS)} lanes")


if __name__ == "__main__":
    main()
