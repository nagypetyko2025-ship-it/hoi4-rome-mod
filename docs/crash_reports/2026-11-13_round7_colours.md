# Teszt a hetedik kör után (2026-11-13, commit 5ef0c1f)

## Mi futott le

1. `git pull` → `5ef0c1f`, `python tools/validate.py`: **0 hiba, 0 figyelmeztetés**, a leírók egyeznek.
2. `python tools/daynight.py --off` – lefutott, mindhárom sort megtalálta és átírta
   (`gfx/FX/standardfuncsgfx.fxh`, ez a fájl ebben a commitban fel van töltve):
   - `//#define NO_NIGHT` → `#define NO_NIGHT`
   - `GMT_OFFSET = 2793.0f` → `631.2f`
   - `SOUTH_POLE_OFFSET = 0.17f` → `0.455f`
3. `tools/screenshot.ps1` – **NEM futott le**: a Windows víruskeresője (Defender / AMSI) blokkolta:
   `This script contains malicious content and has been blocked by your antivirus software.`
   Valószínűleg a `mouse_event` / `SetCursorPos` / `CopyFromScreen` P/Invoke együttes miatt (kártevő-minta).
   A tiltást nem kerültük meg. → Képernyőkép nincs. Ötlet: a játék saját képernyőképe (gyorsbillentyű, a képek a
   `Documents/Paradox Interactive/Hearts of Iron IV/Screenshots` mappába kerülnek) vagy egeret nem vezérlő megoldás.
4. Indítás Rómával (`tools/test_launch.ps1 -ExtraArgs "-quickstart -start_tag=ROM"`, a fenti shader-másolattal):
   **GAME RUNNING**, nincs összeomlás.

## Eredmény (a játékos szemével)

- **Az országok még mindig szürkék** – a 7. kör javításai (seasons.txt, színmódosító define-ok, MSY) és a
  nappal–éjszaka kikapcsolása (`NO_NIGHT` shader) után is.
- Tehát a nappal–éjszaka árnyalás önmagában nem az ok (vagy nem csak az).
- A `-Variants colour` képsorozatot a fenti víruskereső-tiltás miatt nem tudtuk lefuttatni.
