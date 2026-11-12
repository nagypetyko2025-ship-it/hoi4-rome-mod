# Ante Imperium – Hearts of Iron IV ókori mod

Teljes átalakító (total conversion) HoI4 mod: Európa, Észak-Afrika és a Közel-Kelet Róma felemelkedése
előtt és alatt. **Fejlesztés alatt, jelenleg NEM játszható** (lásd: „Ismert hibák”).

- Játékverzió: **1.19.4.2** (Operation Postern). Csak a beépített DLC-kre épít
  (Together for Victory, Death or Dishonor, Waking the Tiger, Man the Guns).
- Dátumok **AUC**-ban (ab urbe condita = Róma alapításától): `AUC = 754 − Kr. e. év`.
  - 1. kezdés: **245 AUC = Kr. e. 509** (a köztársaság születése, Róma városállam) – ez készül.
  - 2. kezdés: **490 AUC = Kr. e. 264** (Róma uralja Itáliát, első pun háború) – később.
  - A motor elfogadja a korai dátumot (tesztelve: a 245.1.1.12 kezdés betölt).

## Telepítés / helyi használat

A mod mappája: `D:/SteamLibrary/steamapps/common/Hearts of Iron IV/mod/ante_imperium`
(bárhova klónozható). A launcher a `Documents/Paradox Interactive/Hearts of Iron IV/mod/ante_imperium.mod`
leírót olvassa; ez ugyanaz, mint a `descriptor.mod`, plusz egy `path="…"` sor a mod mappájára.
A `tools/build.py` mindkettőt automatikusan megírja.

**Figyelem:** a Steam a játék eltávolításakor/újratelepítésekor a teljes játékmappát törli – a GitHub a mentés.

## Mappaszerkezet

| Hely | Mi van benne |
|---|---|
| `tools/data/world_245.py` | **Forrásadat**: Kr. e. 509 népei (45 ország) és államai, népesség, városok, kikötők. Az alapjáték (vanilla) tartományszámaival. |
| `tools/newmap.py` | Térképgenerátor: kivágja és felnagyítja a vanilla térképet, új, sűrűbb tartományhálót növeszt. Ír: `map/**`, `common/ai_areas/default.txt`, `tools/cache/newmap.*`. |
| `tools/build.py` | Összeállító: a `world_245.py`-ból államok, országok, zászlók, épületpozíciók, ellátás, szövegek, könyvjelző, leírók. A vanilla tartományszámokat lefordítja az új térkép tartományaira. |
| `tools/mapdata.py` | Vanilla térképadat olvasása (csak olvas). |
| `tools/render_region.py` | Címkézett tartománytérkép-kép egy régióról (tervezéshez). |
| `tools/test_launch.ps1` | Automatikus tesztindítás (lásd lent). |
| `common/national_focus/ante_generic_focus.txt` | Minimális alap fókuszfa (kötelező, lásd szabályok). |
| `common/defines/zz_ante_imperium.lua` | Kezdő-/végdátum felülírása. |
| `CLAUDE.md` | Rövid szabálylista a fejlesztéshez (AI asszisztensnek is). |
| `docs/design.md` | Terv és fázisok. |

Generált (ne kézzel szerkeszd, hanem a forrást + futtasd újra): `history/states`, `history/countries`,
`history/units`, `map/*`, `common/country_tags`, `common/countries`, `common/bookmarks`, `gfx/flags`,
`localisation/english/replace`, `descriptor.mod`.

## Építés

```bash
python tools/newmap.py     # térkép (~3-5 perc), Pillow + numpy kell
python tools/build.py      # államok, országok, minden más (~10 mp)
```

Térképméret választása a `ANTE_MAP` környezeti változóval (`tools/newmap.py` eleje):

| `ANTE_MAP` | Méret | Megjegyzés |
|---|---|---|
| *(üres, alapértelmezett)* | 3328×3072, 2,4× nagyítás | betölt a főmenüig |
| `small` | 2304×2048, 1,6× | betölt a főmenüig |
| `wide` | 5632×2048 (vanilla méret), 1,6× | teszthez |
| `identity` | vanilla tartományok a saját íróinkon át | hibakereséshez |
| `big` | 4096×3840, 3× | **összeomlik a „loading textures”-nél** (motorkorlát) |

Jelenleg kb. 8000 szárazföldi tartomány (Itáliában ~400, a vanillában 115), 1050 tengeri, 52 tó.

## Tesztelés

```powershell
powershell -ExecutionPolicy Bypass -File tools/test_launch.ps1 -ExtraArgs "-quickstart -start_tag=ROM"
```

- Ideiglenesen csak ezt a modot kapcsolja be (`dlc_load.json`), elindítja a játékot, majd **visszaállítja az eredeti modlistát**.
- `-quickstart -start_tag=ROM` a főmenü nélkül, egyből Rómával indít → kattintás nélkül tesztelhető a játékindítás.
- Eredmény: `MENU`, `GAME RUNNING`, `CRASHED …`, `FAILED: Failed to load the map`.
- `-ExtraArgs "-debug"`: csak így kerülnek be a térképhibák az `error.log`-ba.
- Naplók: `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log`; összeomlások:
  `…/crashes/<dátum>/exception.txt` (+ a naplók másolata).

## Motorszabályok, amiket kitapasztaltunk (fontos!)

1. Egy **állam csak egy stratégiai régióban** lehet, különben „Failed to load the map”.
2. A vanilla államokban lévő **tavaknak** államban kell maradniuk.
3. A `common/national_focus` **nem lehet üres** (kell legalább egy `default = yes` fókuszfa), különben összeomlik.
4. Állam-azonosítók folytonosan 1..N; minden szárazföldi tartomány pontosan egy államban.
5. Térkép-bitkép: egy tartomány pixelei **nem érhetnek össze csak átlósan**, **4 tartomány nem találkozhat
   egy sarokpontban**, nem lehet **1 pixeles folt**. A generátor javítja.
6. **Tengeri stratégiai régió nem lehet szétszakadt** („fractioned”). Szárazföldinél ez nem gond.
7. A térkép **kelet–nyugat irányban körbeér** (a bal és jobb szél szomszédos) – ez a partmenti jelzést is érinti.
8. A 8 bites BMP-ket (`rivers`, `terrain`, `cities`, `trees`) vanilla-stílusú fejléccel kell írni
   (`save_bmp8`), különben „Palette in rivers.bmp is probably not correct”.
9. Térképmagasság: **3840 összeomlik** a textúrák betöltésénél, **3072 működik**.
10. `unitstacks.txt`: tartományfajtánként más pozíciótípusok kellenek (szárazföld 0–10, 21–29, 38;
    part 19–20; tenger 0–18, 21–38; tó lásd kód).
11. Teljesen üres `railways.txt` gyanús – a build minden fővárosba ír egy rövid „vasút” csonkot (később utak lesznek).

## Ismert hibák / állapot (2026-11-12)

- **A játék indításkor („Initializing game”) összeomlik az új térképpel**, bármelyik országgal.
  - A főmenüig betölt.
  - A régi, vanilla-térképes változat (commit `0869843`) elindul és fut.
  - Felezéses keresés eredménye: a hiba a **`tools/build.py` által generált `map/buildings.txt`
    államszintű épületpozícióiban** van (air_base, arms_factory, industrial_complex stb.). Ha csak ezeket
    cseréltük a működő fájlban, összeomlott.
  - Valószínű ok: a pozíciók a tartomány **súlypontja** köré kerültek, ami íves/partmenti tartománynál
    a tartományon kívülre (tengerbe vagy más államba) esik.
  - **Utolsó, még NEM TESZTELT javítás:** a `newmap.py` `inside_points()` függvénye garantáltan
    tartományon belüli pontokat (`c`, `pts`) számol, és ezeket használja minden pozíció (épületek,
    unitstacks, időjárás). Első teendő: `newmap.py` + `build.py`, majd quickstart-teszt.
- Egy korábbi tesztnél (régi változat) **az országoknak nem volt színe** a térképen – még nincs kivizsgálva.
- Vezetőnevek hiányoznak (nincs ókori névlista `common/names`-ben) → hibák a naplóban, nem összeomlás.
- Az `error.log` tele van a vanilla modern tartalom (spanyol tanácsadók, ötletek, hajónevek…) hibáival – kiürítendő.
- Egy tartomány (pár pixeles beékelt darab) még több részből állhat a generálás után (`fragments round 2: 1 pieces`).

## Tervezett fázisok

0. Alapozás – kész.
1. Váz: államok, országok, modern tartalom kiürítése – folyamatban (új térkép + indítási hiba).
2. Technológiák, egységek (hoplita, manipulus, harci elefánt…), felszerelés, ipar.
3. Róma és szomszédai teljesen játszhatóan (Kr. e. 509).
4. A többi nép és fókuszfa (egész Európa: kelták, germánok, szkíták, ibérek, görögök, Perzsia…).
5. Második kezdés: 490 AUC (Kr. e. 264).
6. AI, egyensúly, grafika, magyar/angol szöveg. (A HoI4-ben nincs magyar nyelv; magyar szöveg csak az angol fájlok helyén lehet.)

## Szabályok a fejlesztéshez

- **Az alapjáték fájljait soha nem módosítjuk**, csak ezt a mod mappát.
- Más modok (pl. „Total War Rome 2 in HOI4”) grafikáját nem másoljuk. Saját/procedurális vagy CC0 grafika.
- Vanilla fájlokat a mod olvashat és módosított másolatként felhasználhat (ez normál modolás).
