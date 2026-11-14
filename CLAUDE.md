# Ante Imperium – HoI4 total conversion (ancient Europe)

## Hard rules
- Only edit files inside this mod folder (and the descriptor `Documents/Paradox Interactive/Hearts of Iron IV/mod/ante_imperium.mod`). NEVER modify the base game install (Peti: `D:/SteamLibrary/...`, Sim: `E:/SteamLibrary/steamapps/common/Hearts of Iron IV`).
- Base game files are read-only references. Do not copy assets from other mods (e.g. the user's "Total War Rome 2 in HOI4"). Art must be our own/procedural or CC0, noted in `docs/ASSET_LICENSES.md`.
- Keep `descriptor.mod` and the Documents `.mod` file in sync (the Documents copy additionally has `path=`). Every `replace_path` goes into BOTH.
- Game version 1.19.4.2. Owned/integrated DLC: Together for Victory, Death or Dishonor, Waking the Tiger, Man the Guns (+cosmetic packs). Do not depend on other DLC mechanics.

## Generated files – edit the source, not the output
- **`tools/data/world_509bc.py` is the source of truth for the world** (peoples, regions, cities with real
  longitude/latitude, populations, the impassable wilds). `python tools/world.py` (no game needed, ~15 s) regenerates
  history/states, history/countries, country files + colors.txt, country tags, names, flags, state/country localisation
  (`localisation/english/replace/`), the bookmark, supply nodes, the road net (railways.txt) and - through
  `tools/positions.py` - map/buildings.txt and map/unitstacks.txt. `--preview DIR` draws political maps instead.
- Italy, Sicily, Sardinia, Corsica and Punic Africa (66 states, 44 countries) are frozen in
  `tools/data/core_states_245.json` (province ids of the committed map) and `tools/data/world_245.py` (countries).
  To change them, edit the JSON by hand.
- `tools/geo.py`: longitude/latitude -> map pixel (fitted, about 5-10 px off). The province grid is coarse in places
  (Attica is one province): when two capitals fall into one province the more important one keeps it.
- The map itself (provinces.bmp, definition.csv, rasters, strategic regions, adjacencies, weather) is NOT regenerated:
  it is the version proven to load and run. `tools/newmap.py` (needs the game) would renumber every province and
  break the frozen states - it refuses to run without `--regenerate`. `tools/build.py` is the old Italy-only
  generator (`--legacy`); positions.py and world.py still use its buildings writer and flag painter.
- `tools/render_region.py` / `tools/mapdata.py`: labelled province maps for planning (read-only on the base game).
- Test: `powershell -ExecutionPolicy Bypass -File tools/test_launch.ps1` (swaps dlc_load.json to this mod only, restores it;
  stops at the main menu). `-Continue` loads the last save game without a click (`--continuelastsave`), `-KeepRunning`
  leaves the game open. The game is found on any drive (`-Game` / `HOI4_DIR` override).
- **NEVER judge the map from a `-quickstart` session: the engine's quickstart draws no country colours at all** (the base
  game too). Rounds 6-8 chased "grey countries" that only existed in quickstart. Start through the menu, or `-Continue`.
  Crash dumps: `Documents/.../crashes/<date>/` (exception.txt + logs copy).

## Engine rules learned the hard way (map/crash)
- Every state must lie inside ONE strategic region, else "Failed to load the map" (build.py enforces it).
- Lakes listed in vanilla states must stay in some state (build.py attaches them).
- `common/national_focus` must contain at least one focus tree (`ante_generic_focus`, default = yes) or the game crashes.
- State ids contiguous 1..N; every land province in exactly one state.
- Custom map (`tools/newmap.py`, 3328x3072 = 2.4x zoom of vanilla Europe): height 3840 crashes at "loading textures";
  3072 works. Province pixels may not touch only diagonally, 4 provinces may not meet at one vertex, no 1-pixel
  spots; naval strategic regions must be contiguous; the map wraps east-west (affects coastal flags).
- An empty railways.txt is suspected to crash on game start; build.py writes placeholder rail stubs.
- 8-bit BMPs must be written with vanilla-style headers (`save_bmp8`), else "Palette in rivers.bmp is probably not correct".
- Debug a "Failed to load the map" dialog by launching with `-ExtraArgs "-debug"`: only then map errors reach error.log.
- `weatherpositions.txt` sizes are `big` / `small` (as in the real game files; the wiki's "large" is wrong), one of each
  per strategic region.
- A strategic region is either naval (sea provinces only) or land (land + lakes only). Never put a land province – let
  alone a whole state – into a naval region (`settle_regions()` in newmap.py enforces it).
- rivers.bmp: every 4-connected river system needs exactly one source (index 0) at an open end; flow-in/out markers
  (1/2) must touch their junction; no loops, no diagonal-only contacts (`repair_rivers()` in newmap.py).
- Vanilla defines hard-code strategic region ids: `NDefines.NGeography.MEDITERRANEAN_SEA_REGIONS` (vanilla ids 29, 68,
  69, 168, 169, 202). They MUST be overridden with region ids that exist on this map (generated into
  `common/defines/zz_ante_regions.lua` by newmap.py) – prime suspect for the crash at session start that no content
  change could move (bisect 2026-11-12: every variant crashed at the same address).
- When a crash survives every content change, look for vanilla files/defines that reference ids of the vanilla map.
- **Position -> province: the engine uses column floor(x) and row H - 1 - floor(z).** A whole-number z = H - y lands one
  row ABOVE the intended pixel. Always write pixel centres (x + 0.5, z = H - y - 0.5). Coastal positions on whole
  numbers left 686 of 1586 coastal provinces without a port in the engine's eyes ("Province N is setup as coastal but
  has no port building in the nudger. This will likely crash the game") = the crash at session start (found 2026-11-12).
- That log line only appears with `-debug` or `-crash_data_log`: always test with `-crash_data_log` and read the END of
  error.log (the last few hundred lines), not a filtered excerpt.
- `python tools/positions.py` rewrites buildings.txt / unitstacks.txt from the committed map without the game.
- Never resize `colormap_rgb_cityemissivemask_a.dds` as one RGBA image: Pillow premultiplies by alpha (the city light
  mask, 0 almost everywhere) and the land colour turns black = black and white map, colourless countries. Resize RGB and
  A separately. `python tools/colormap.py` repaints it from terrain.bmp + heightmap.bmp (no game), `--vanilla` crops the
  game's own.
- Day/night: the map shader has the VANILLA Greenwich column compiled in (`GMT_OFFSET = 2793`, plus
  `SOUTH_POLE_OFFSET = 0.17`) and treats the map width as 360 degrees. On this map Greenwich is column 631, so Italy is
  half a day off: midnight at 12:00, when every game starts - dark, desaturated land. Only a patched copy of the game's
  shader fixes it: `python tools/daynight.py [--off]` (needs the game; rerun after game updates).
- Other things that grey the map: vanilla `map/seasons.txt` (`hsv_north = { 0 0.1 1 }`: whole-frame saturation x0.1 in
  snowy views - the mod ships a neutral seasons.txt) and `NGraphics.COUNTRY_COLOR_SATURATION_MODIFIER = 0.6` /
  `..._BRIGHTNESS_MODIFIER = 0.8` (the mod sets 1.0 / 0.9).
- Country tags must not be script keywords: `NUM` and `RED` are reserved (Massylii is `MSY`).
- Visual problems cannot be judged from files: ask for the game's own F11 screenshots, collected with
  `tools/collect_screenshots.ps1` (docs/screenshots/*.jpg), and LOOK at the pictures before changing anything.
  Do not script the mouse, keyboard or screen capture: Windows Defender blocked the earlier `screenshot.ps1` for that.
- Impassable states are not painted in their owner's colour (the terrain shows, also in the diplomacy view).
- Day/night: the shader takes the map width for 360 degrees; this map is 88.6 degrees wide. The mod's copy of
  `gfx/FX/standardfuncsgfx.fxh` scales the longitude (`LONGITUDE_SHARE`) and moves Greenwich (`GMT_OFFSET` 631.2,
  `SOUTH_POLE_OFFSET` 0.455); `python tools/daynight.py` writes it from the game's file. Without it a hard day/night
  edge stands in the middle of the map.
- A mod tag that also exists in the base game inherits the base game's `TAG_<ideology>.tga` flags and party names
  (ROM flew Romania's flag). world.py writes ideology flags for the tags in `tools/data/vanilla_flag_tags.py` and party
  names for every country.
- STATUS 2026-11-13 (round 9): verified IN THE GAME (1.19.5): the world of 509 BC shows in full colour when the game
  is started through the menu or with `-Continue`; day/night fixed; `docs/screenshots/20261113_round9_*.jpg`.
- Tech screen (tools/tech.py writes a copy of the game's interface/countrytechtreeview.gui): never DELETE elements of
  that file - the game looks some up by name and then does not open the research screen at all; blank them (empty
  sprite `GFX_ante_blank`, empty text, position -9000). A tech that enables equipment gets the big box (icon centred),
  every other one the small 72x72 box (icon's corner at 3,3: icons must be 64x64). A grid box with a size lays its
  tree out from its MIDDLE. Lane headings, tab glyphs and icon sizes: `LANES`, `TABS` in tools/data/tech_tree.py.
- Testing in the game on Sim's machine (2026-11-14): the game ignores SendKeys - only hardware scan codes reach it
  (keybd_event with the scan code). Entering the tech tree needs a mouse click on a research slot (ask Sim; mouse
  scripts are blocked by Windows Defender and must not be worked around). Pages: keys 1-7 once the tree is open.
- Resources (tools/resources.py, round 21): the base game's 7 resource KEYS stay (engine defines and base-game
  scripts use them) with ancient meanings: steel = iron, aluminium = copper, tungsten = tin, rubber = timber,
  chromium = horses, oil = pitch, coal = grain (the engine's energy resource). Names in
  localisation/english/replace/ante_resources_l_english.yml, icons replace gfx/interface/(missing_)resources_strip.dds.
  State amounts come from DEPOSITS (lon/lat of real ancient sources) + terrain, written by world.py into history/states.
  The game adds infrastructure bonuses on top, so the map shows more than the files.
- Tech timeline: tools/tech.py FIRST..LAST (245..280 AUC since round 21) and BASE_TECH_COST in common/defines go together:
  the whole tree should take about as many years to research as it spans.
- Rome's story systems (tools/rome_story.py, round 19): two 0-100 meters (`ROM_discord` for the Republic,
  `ROM_hatred` for the Kingdom) drive dynamic modifiers through scripted effects (`ROM_*_update`); events
  `ante_rome.*`, decisions in category `ROM_res_romana`. Rome starts with ONE state: `start_civil_war` then does
  nothing, so the uprising is a revolution until Rome holds 3+ states. `complete_national_focus` completes a
  mutually exclusive focus (tested). Test such systems in a variant copy with `log = "...[?var]"` lines and read
  game.log; the trigger is `num_of_controlled_states` (`num_owned_controlled_states` is only a variable).
- Do not write HoI4 file formats from memory or from wiki prose alone: check a real file of a working mod
  (e.g. Kaiserreich's `map/` on GitHub) first.
- `tutorial/tutorial.txt` must exist with `tutorial = { }` (the vanilla one references vanilla state ids → crash after
  country selection).
- `buildings.txt`: last field (adjacent sea province) non-zero ONLY for `naval_base_spawn` and `floating_harbor`; every
  coastal land province needs a `naval_base_spawn` line.
- `adjacencies.csv` ends with `-1;-1;-1;-1;-1;-1;-1;-1;-1`; no duplicate pairs; `impassable` only between touching
  provinces. `definition.csv` needs CRLF line endings; sea provinces touching land are `coastal = true` too.
- X crossings are also checked across the east-west seam. Provinces of 8 px or less are an error.
- `map/airports.txt` / `map/rocketsites.txt` no longer exist (removed in 1.15).
- Session logging: `python tools/watch.py` (run while playing; report in docs/session_logs/, personal paths removed) reads the ANTE| lines that tools/eventlog.py (on_actions) and content.py (focus rewards) write to game.log. Rerun eventlog.py after changing it; content.py writes the focus lines.
- Run `python tools/validate.py` after every generation: it checks all of the above without the game.
- Pipeline (since round 15): world.py, portraits.py, army.py, buildings.py (modern buildings off, ancient names; reads the game), tech.py (ancient tech tree from tools/data/tech_tree.py, AUC year labels in a copy of the game's countrytechtreeview.gui, folders in technology_tags; reads the game), content.py, commanders.py (generals/admirals, appends recruit lines to history - rerun after world.py), validate.py. Older note: `python tools/world.py`, then `python tools/portraits.py` (named + generic culture portraits, portraits/00_portraits.txt), then `python tools/army.py` (ancient units/equipment/icons, empties the base game's land unit files, history/units/<TAG>_245.txt; reads the game once), then `python tools/content.py` (generic focus tree, national spirits, named leaders + traits from `tools/data/leaders_509bc.py`), then `python tools/validate.py` (0 errors). None needs the game.
- Focus/idea/trait keys share one localisation namespace: an idea may not have the same key as a focus (ideas end in `_spirit` where they would clash).
- Performance: ~215 AI countries at once; `zz_ante_imperium.lua` slows AI routines that have nothing to do yet (no units). Do not test speed with `-crash_data_log` / `-debug` (extra logging).
- Country tags: three capitals, unique, not a script keyword (world.py checks a list). Country industry is set per
  country with a sublinear rule (`industry()` in world.py), not per head.

## Conventions
- Dates are AUC years (ab urbe condita): AUC = 754 - BC year. 509 BC = 245 AUC, 343 BC = 411 AUC, 264 BC = 490 AUC.
- Overrides of vanilla defines go in `common/defines/zz_ante_imperium.lua` (loads after vanilla).
- Localisation: `localisation/english/*_l_english.yml`, UTF-8 WITH BOM, `KEY:0 "text"`, one space indent.
- Prefix all new script keys with `ANTE_` / `ante_` unless they are country-tag scoped (`ROM_...`).
- Debug: game logs in `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log` – check after every test load.

## Status
See `docs/design.md` for the plan and phases.
- Units: vanilla land sub-units are REMOVED by empty same-name overrides in common/units (only `fake_intel_unit` kept);
  the base game's scripts then log "Invalid subunit" at load - harmless. Ancient units are `ante_*`, active from the
  start (elephants inactive). `common/ai_templates` and `common/ai_equipment` are replace_path'ed (AI uses the OOB templates).
  Ships and aircraft are still vanilla (next step: triremes etc.). Crash-test armies with `-quickstart` (units load at game start, not at the menu).
- Ships: vanilla naval sub-units emptied too; ancient ships are `ante_penteconter/trireme/quinquereme` with hulls
  `<key>_hull` (no module slots). Fleets: history/units/<TAG>_245_naval.txt via `set_naval_oob` (always written).
- Production pictures: the engine shows `GFX_<equipment variant>_medium` (e.g. GFX_ante_arms_equipment_1_medium).
- Manpower: battalions are 500 men; culture spirits (`ante_culture_<culture>`, Rome `ante_culture_roman`) add
  conscription. Country trees: `tools/national_trees.py` (ROM full, ATH/LAK/MKD/PRS/CAR base), called by content.py; spirits end in `_spirit`,
  tech/doctrine bonuses are named after their focus. Bookmark: 7 major slots (`BOOKMARK_COUNTRIES`) + `BOOKMARK_MINORS`, text `ANTE_BOOKMARK_<TAG>`.
