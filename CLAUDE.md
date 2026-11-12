# Ante Imperium – HoI4 total conversion (ancient Europe)

## Hard rules
- Only edit files inside this mod folder (and the descriptor `Documents/Paradox Interactive/Hearts of Iron IV/mod/ante_imperium.mod`). NEVER modify the base game in `D:/SteamLibrary/steamapps/common/Hearts of Iron IV` outside `mod/ante_imperium`.
- Base game files are read-only references. Do not copy assets from other mods (e.g. the user's "Total War Rome 2 in HOI4"). Art must be our own/procedural or CC0, noted in `docs/ASSET_LICENSES.md`.
- Keep `descriptor.mod` and the Documents `.mod` file in sync (the Documents copy additionally has `path=`). Every `replace_path` goes into BOTH.
- Game version 1.19.4.2. Owned/integrated DLC: Together for Victory, Death or Dishonor, Waking the Tiger, Man the Guns (+cosmetic packs). Do not depend on other DLC mechanics.

## Generated files – edit the source, not the output
- `tools/data/world_245.py` is the source of truth for countries and states; `python tools/build.py` regenerates
  history/states, history/countries, map/buildings.txt, railways, supply nodes, country files, flags, state/country
  localisation (`localisation/english/replace/`), the bookmark and BOTH descriptors (incl. `replace_path`s).
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
- Pipeline: `python tools/newmap.py` (map, ~2 min) then `python tools/build.py` (states/countries, translated from
  vanilla province ids in world_245.py to the new provinces).

## Conventions
- Dates are AUC years (ab urbe condita): AUC = 754 - BC year. 509 BC = 245 AUC, 343 BC = 411 AUC, 264 BC = 490 AUC.
- Overrides of vanilla defines go in `common/defines/zz_ante_imperium.lua` (loads after vanilla).
- Localisation: `localisation/english/*_l_english.yml`, UTF-8 WITH BOM, `KEY:0 "text"`, one space indent.
- Prefix all new script keys with `ANTE_` / `ante_` unless they are country-tag scoped (`ROM_...`).
- Debug: game logs in `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log` – check after every test load.

## Status
See `docs/design.md` for the plan and phases.
