# Ante Imperium – Hearts of Iron IV ókori mod

Teljes átalakító (total conversion) HoI4 mod: Európa, Észak-Afrika és a Közel-Kelet Róma felemelkedése
előtt és alatt. **Fejlesztés alatt, jelenleg NEM játszható** (lásd: „Állapot”).

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
| `tools/validate.py` | **Statikus ellenőrző**: játék nélkül végignézi a térkép- és történelemfájlokat a lenti motorszabályok szerint. Minden generálás után futtasd. |
| `tools/data/names_245.py` | Ókori névlisták kultúránként (vezetők, tábornokok) → `common/names/ante_names.txt`. |
| `tutorial/tutorial.txt` | Üres `tutorial = { }` blokk (kötelező, lásd szabályok). Kézzel írt, nem generált. |
| `.gitattributes` | A `definition.csv` és az `adjacencies.csv` bájtra pontosan (CRLF sorvéggel) marad a repóban. |
| `common/national_focus/ante_generic_focus.txt` | Minimális alap fókuszfa (kötelező, lásd szabályok). |
| `common/defines/zz_ante_imperium.lua` | Kezdő-/végdátum felülírása. |
| `CLAUDE.md` | Rövid szabálylista a fejlesztéshez (AI asszisztensnek is). |
| `docs/design.md` | Terv és fázisok. |

Generált (ne kézzel szerkeszd, hanem a forrást + futtasd újra): `history/states`, `history/countries`,
`history/units`, `map/*`, `common/country_tags`, `common/countries`, `common/names`, `common/bookmarks`, `gfx/flags`,
`localisation/english/replace`, `descriptor.mod`.

## Építés

```bash
python tools/newmap.py     # térkép (~3-5 perc), Pillow + numpy kell
python tools/build.py      # államok, országok, minden más (~10 mp)
python tools/validate.py   # statikus ellenőrzés (~1 perc), játék nem kell hozzá; 0 hibával kell végeznie
```

A `validate.py` csak a mod mappáját olvassa (numpy kell, scipy-val gyorsabb), ezért olyan gépen is fut,
ahol nincs HoI4. A két generátorhoz viszont kell az alapjáték (a vanilla térképből dolgoznak).

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
12. **`weatherpositions.txt`: a méret csak `large` vagy `small` lehet.** Régiónként mindkettő kell; `large` nélkül
    a játék összeomlik (korábban `big` állt a fájlban).
13. **`tutorial/tutorial.txt` kötelező** (`tutorial = { }`): a vanilla oktatófájl vanilla államazonosítókra mutat,
    amik ezen a térképen nincsenek → összeomlás országválasztás után.
14. Az X-kereszteződést a motor **a térkép jobb és bal széle között is** ellenőrzi (a térkép körbeér):
    ott sem találkozhat 4 tartomány egy pontban.
15. `buildings.txt`: az utolsó mező (szomszédos tengeri tartomány) **csak `naval_base_spawn` és
    `floating_harbor`** sornál lehet nem nulla. Minden partmenti tartománynak kell `naval_base_spawn` sor,
    különben „has no port building in the nudger” → összeomlás.
16. `adjacencies.csv`: az utolsó sor kötelezően `-1;-1;-1;-1;-1;-1;-1;-1;-1`. Egy tartománypár csak egyszer
    szerepelhet; `impassable` csak ténylegesen szomszédos tartományok közt; `sea` (átkelő) csak két, egymással
    nem érintkező szárazföldi tartomány közt, olyan tengeri tartományon át, ami mindkettővel határos.
17. `definition.csv`: **CRLF sorvég** kell; a partmenti jelző a szárazfölddel érintkező **tengeri**
    tartományoknál is `true` (különben a motor „javított” másolatot ír és hibát naplóz).
18. A legfeljebb 8 pixeles tartomány hiba („has only N pixels”) – a generátor ezeket 12 pixelre növeszti.
19. `map/airports.txt` és `map/rocketsites.txt` az 1.15-ös javítás óta nem létezik; helyettük a
    `buildings.txt` `air_base` és `rocket_site_spawn` sorai számítanak.

## Állapot (2026-11-12, második kör – statikus javítás, játékban még NEM tesztelve)

Ezen a körön nem volt elérhető a játék, ezért a hibákat a `tools/validate.py` statikus ellenőrzővel és a
HoI4-wiki (Map modding, Troubleshooting) dokumentált szabályaival kerestük meg. A generált fájlokat helyben
javítottuk, és ugyanezek a javítások bekerültek a `newmap.py`-ba és a `build.py`-ba is.

Javítva (zárójelben a szabály száma):

- **Összeomlás játékindításkor**: `weatherpositions.txt` `big` → `large` (12); üres `tutorial/tutorial.txt` (13).
  Ez a kettő magyarázza, hogy a vanilla térképes változat miért futott, az új térképes miért nem: a régi a vanilla
  időjárásfájlt használta, és megvolt benne minden vanilla államazonosító.
- **Térképbetöltés**: egy X-kereszteződés a térkép varratán (14); 7 darab 8 pixeles vagy kisebb tartomány (18);
  hiányzó záró sor és 29 hibás/duplikált sor az `adjacencies.csv`-ben (16).
- **`buildings.txt`**: 4758 sorban tengeri tartomány állt olyan épülettípusnál, ami nem kaphat (15).
  Az épületpozíciók (az előző kör „inside points” javítása) az ellenőrző szerint mind a saját államukban vannak.
- **`definition.csv`**: 596 tengeri tartomány partmenti jelzője (17).
- **Vezetőnevek**: `common/names/ante_names.txt` mind a 45 országhoz, kultúránkénti ókori névlistával.
- **Töredékes tartomány**: a generátor javítólépései (apró tartományok, töredékek, X-kereszteződések, varrat) most
  addig ismétlődnek, amíg a térkép már nem változik; a `validate.py` a kész térképen ellenőrzi is.

Még nyitott:

- **Játékbeli teszt kell** (`tools/test_launch.ps1 -ExtraArgs "-quickstart -start_tag=ROM"`). Ha még összeomlik:
  az `error.log` vége és a `crashes/<dátum>/exception.txt` mutatja meg, melyik fájlnál.
- **Az országoknak nem volt színe** (régi teszt): a fájlokban nem találtunk hibát – a `common/countries/colors.txt`
  és az országfájlok formátuma megegyezik a vaniláéval, minden országnak van színe. Gyanú: közelre nagyítva a
  politikai színezés a motorban elhalványul, a kezdő államok pedig aprók. Játékban kell megnézni.
- **Az `error.log` vanilla hibái** (spanyol tanácsadók, ötletek, hajónevek…): ehhez a tényleges `error.log` kell,
  mert abból derül ki, mely vanilla fájlokat kell felülírni vagy `replace_path`-szal kiváltani. Vaktában nem
  cseréltünk le mappát: ha egy adatbázistípusból egy bejegyzés sem marad, a játék összeomlik.
- A térkép keleti széle szárazföld, a nyugati tenger, így a varraton át „partmenti” a keleti szél. Ez szabályos,
  de szokatlan; ha a varrat környékén furcsaság látszik, a keleti szélre érdemes tengersávot tenni.

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
