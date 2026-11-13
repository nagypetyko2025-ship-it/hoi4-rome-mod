# Ante Imperium – HoI4 total conversion (ancient Europe)

## Hard rules
- Only edit files inside this mod folder (and the descriptor `Documents/Paradox Interactive/Hearts of Iron IV/mod/ante_imperium.mod`). NEVER modify the base game in `D:/SteamLibrary/steamapps/common/Hearts of Iron IV` outside `mod/ante_imperium`.
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
- Test: `powershell -ExecutionPolicy Bypass -File tools/test_launch.ps1` (swaps dlc_load.json to this mod only, restores it).
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
- Impassable states are not painted in their owner's colour (the terrain shows, also in the diplomacy view), and the
  game starts on 1 January (snowy, pale terrain). A world that is mostly one impassable placeholder country therefore
  looks grey - the likely cause of "the countries are grey" in rounds 6-7 (not confirmed by a screenshot).
- STATUS 2026-11-13 (round 8): the whole world rebuilt for 509 BC - 214 countries, 634 states (573 playable).
  Validates clean, NOT yet tested in the game. `docs/maps/*.jpg` show what it should look like.
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
- Run `python tools/validate.py` after every generation: it checks all of the above without the game.
- Pipeline: `python tools/world.py` then `python tools/validate.py` (0 errors). Neither needs the game.
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
