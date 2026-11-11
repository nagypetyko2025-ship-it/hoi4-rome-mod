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

## Conventions
- Dates are AUC years (ab urbe condita): AUC = 754 - BC year. 509 BC = 245 AUC, 343 BC = 411 AUC, 264 BC = 490 AUC.
- Overrides of vanilla defines go in `common/defines/zz_ante_imperium.lua` (loads after vanilla).
- Localisation: `localisation/english/*_l_english.yml`, UTF-8 WITH BOM, `KEY:0 "text"`, one space indent.
- Prefix all new script keys with `ANTE_` / `ante_` unless they are country-tag scoped (`ROM_...`).
- Debug: game logs in `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log` – check after every test load.

## Status
See `docs/design.md` for the plan and phases.
