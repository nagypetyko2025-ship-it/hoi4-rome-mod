# Ante Imperium – Hearts of Iron IV ókori mod

Teljes átalakító (total conversion) HoI4 mod: Európa, Észak-Afrika és a Közel-Kelet Róma felemelkedése
előtt és alatt. **Fejlesztés alatt: a váz elindul és fut (2026-11-12, ötödik kör), a tartalom kidolgozása
most kezdődik** (lásd a „…kör” szakaszokat lent).

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
| `tools/data/world_509bc.py` | **Forrásadat – a világ Kr. e. 509-ben** Itálián kívül: ~170 nép, ~210 régió, városok valódi földrajzi koordinátákkal (hosszúság, szélesség), népesség, kikötők, a járhatatlan vadon. Ezt szerkeszd, ha országot, határt, várost akarsz változtatni. |
| `tools/world.py` | **A világ generátora (játék nélkül fut)**: a fenti adatból és a kész térképből államokat, országokat, színeket, zászlókat, neveket, szövegeket, könyvjelzőt, ellátó csomópontokat és utakat ír, majd lefuttatja a `positions.py`-t. `--preview MAPPA`: politikai térkép képként. |
| `tools/geo.py` | Földrajzi koordináta → térképpixel (szigetek és tavak kimért helyére illesztett vetítés, ~5–10 pixel pontos). |
| `tools/data/core_states_245.json` | Itália, Szicília, Szardínia, Korzika és a pun Afrika kézzel összerakott 66 állama „befagyasztva” (a mostani tartományszámokkal). A `world.py` változatlanul veszi át. |
| `tools/data/world_245.py` | Itália 44 országának adatai (név, kultúra, szín) – a `world.py` innen veszi őket. Az államlista benne a régi, vanilla tartományszámos forrás (már csak a `build.py --legacy` használja). |
| `tools/data/names_509bc.py` | Névlisták az új kultúrákhoz (ibér, germán, északi, trák, szkíta, kaukázusi, anatóliai, perzsa, arab, núbiai). |
| `tools/collect_screenshots.ps1` | A játék saját (F11) képernyőképeit másolja a `docs/screenshots/` mappába. Nem indít játékot, nem mozgat egeret – a víruskereső nem bántja. |
| `docs/maps/*.jpg` | A `world.py --preview` képei az aktuális világról (így játék nélkül is látszik, mi hol van). |
| `tools/newmap.py` | **Régi (legacy)** térképgenerátor: a vanilla térképből vágta ki és nagyította fel a mostani térképet. Újrafuttatva minden tartományszám megváltozna, ezért csak `--regenerate` kapcsolóval indul. Kell hozzá a játék. |
| `tools/build.py` | **Régi (legacy)** összeállító (csak Itália, vanilla tartományszámokból). Csak `--legacy` kapcsolóval indul; az épületpozíció-íróját és az itáliai zászlófestőt a többi eszköz ma is használja. |
| `tools/mapdata.py` | Vanilla térképadat olvasása (csak olvas). |
| `tools/render_region.py` | Címkézett tartománytérkép-kép egy régióról (tervezéshez). |
| `tools/test_launch.ps1` | Automatikus tesztindítás (lásd lent). |
| `tools/validate.py` | **Statikus ellenőrző**: játék nélkül végignézi a térkép- és történelemfájlokat a lenti motorszabályok szerint. Minden generálás után futtasd. |
| `tools/positions.py` | A kész térképből újraírja a `buildings.txt` és az `unitstacks.txt` pozícióit – játék nélkül is fut. |
| `tools/colormap.py` | A szárazföld színtextúrája: játék nélkül megfesti a terepből, `--vanilla` kapcsolóval a játék sajátjából vágja ki. |
| `tools/daynight.py` | A játék térkép-shaderének másolata a mi térképünk nappal–éjszaka állandóival (`--off`: éjszaka nélkül). Kell hozzá a játék. |
| `tools/bisect_launch.ps1`, `tools/make_variants.py` | Automata felező teszt: egyszerűsített fájlváltozatokkal indítja a játékot, és táblát ír az eredményről. |
| `tools/data/names_245.py` | Ókori névlisták kultúránként (vezetők, tábornokok) → `common/names/ante_names.txt`. |
| `tutorial/tutorial.txt` | Üres `tutorial = { }` blokk (kötelező, lásd szabályok). Kézzel írt, nem generált. |
| `.gitattributes` | A `definition.csv` és az `adjacencies.csv` bájtra pontosan (CRLF sorvéggel) marad a repóban. |
| `common/national_focus/ante_generic_focus.txt` | Minimális alap fókuszfa (kötelező, lásd szabályok). |
| `common/defines/zz_ante_imperium.lua` | Kezdő-/végdátum felülírása. |
| `CLAUDE.md` | Rövid szabálylista a fejlesztéshez (AI asszisztensnek is). |
| `docs/design.md` | Terv és fázisok. |

A `world.py` írja (ne kézzel szerkeszd, hanem a forrást + futtasd újra): `history/states`,
`history/countries`, `common/country_tags/00_ante_countries.txt`, `common/countries`, `common/names`,
`common/bookmarks`, `gfx/flags`, `localisation/english/replace`, `map/supply_nodes.txt`, `map/railways.txt`,
és a `positions.py`-n át `map/buildings.txt`, `map/unitstacks.txt`.
A régi `newmap.py` írta (most kézben tartott, bevált állapot): a többi `map/*`, `common/ai_areas/default.txt`,
`common/defines/zz_ante_regions.lua`.

## Építés

```bash
python tools/world.py                      # a világ: államok, országok, zászlók, nevek, utak, pozíciók (~15 mp)
python tools/validate.py                   # statikus ellenőrzés (~1 perc); 0 hibával kell végeznie
python tools/world.py --preview docs/maps  # (nem kötelező) politikai térkép képként, a játék fájljaihoz nem nyúl
```

Mindhárom **játék nélkül fut**, csak a mod mappáját olvassa (Python 3.11, numpy, Pillow). A világot a
`tools/data/world_509bc.py` írja le: egy nép egy `C(...)` sor, egy régiója egy `R(...)` sor valódi
hosszúsággal–szélességgel. A `world.py` minden szárazföldi tartományt annak a régiónak ad, amelynek a magja
szárazföldön a leghamarabb odaér (a hegy, sivatag, mocsár lassít, a `power` gyorsít), a régiókat pedig
államokra vágja úgy, hogy egy állam egy stratégiai régióban maradjon.

A térkép maga (tartományháló, domborzat, folyók, stratégiai régiók) **nem generálódik újra** – az a változat
van a repóban, amelyik a játékban bizonyítottan betölt és fut. A régi, vanilla-alapú `newmap.py` / `build.py`
csak külön kapcsolóval indul (lásd a táblázatot), és kell hozzájuk az alapjáték.

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
powershell -ExecutionPolicy Bypass -File tools/test_launch.ps1                         # megáll a FŐMENÜBEN
powershell -ExecutionPolicy Bypass -File tools/test_launch.ps1 -Continue -KeepRunning  # betölti az utolsó mentést
```

- Ideiglenesen csak ezt a modot kapcsolja be (`dlc_load.json`), elindítja a játékot, majd **visszaállítja az eredeti modlistát**.
  A játékot magától megkeresi (bármelyik meghajtó Steam-könyvtárában; különben `-Game "X:\…\Hearts of Iron IV"`
  vagy `HOI4_DIR`), és a `Documents\…\mod\ante_imperium.mod` leírót is ő írja meg.
- **Így nézd meg a térképet:** első alkalommal a főmenüből indíts játékot (Single Player → Start), engedd el az
  órát a következő hónap elsejéig (ekkor a játék magától ment: `autosave.hoi4`). Ettől kezdve a `-Continue`
  kattintás nélkül egyből ebbe a játékba tölt be. Ha a `tools/world.py` után megváltozott a világ, indíts új
  játékot a menüből (a régi mentés a régi világot tartalmazza).
- **A motor saját `-quickstart` kapcsolóját NE használd a térkép megnézésére:** a gyorsindított játék
  **egyáltalán nem rajzol országszíneket** (csupasz terep nevekkel – az alapjáték is így viselkedik). A 6–8.
  kör összes „szürke / színtelen országok” jelentése ebből jött, nem a modból (kiderült: 2026-11-13).
  Összeomlás-tesztre továbbra is jó (`tools/bisect_launch.ps1` ezt használja).
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
12. **`weatherpositions.txt`: a méret `big` vagy `small`.** Régiónként mindkettő kell. (A wiki szövege „large”-ot
    ír, de a valódi játékfájlokban – pl. a Kaiserreich `map/weatherpositions.txt`-jében – `big` áll. A második kör
    ezt tévesen `large`-ra írta át, a harmadik visszaállította.)
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
20. **`rivers.bmp`**: a folyó 1 pixel széles, 4-szomszédosan összefüggő vonal. Minden összefüggő folyórendszernek
    **pontosan egy forráspixele** (0-s index) van, egy szabad végen; a mellékfolyó utolsó pixele a torkolat előtt
    befolyásjelölő (1), az elágazás első pixele kifolyásjelölő (2), és a jelölőnek **érintenie kell a torkolatot**.
    Nem lehet hurok, csak átlós érintkezés, 8 pixelnél rövidebb csonk, és a folyó nem érhet a bitkép széléig.
    A felnagyítás és a kivágás mindezt elrontja – a `newmap.py` `repair_rivers()` függvénye javítja.
21. **Stratégiai régiók fajtája**: a tengeri régióba csak tengeri tartomány kerüljön, a szárazföldibe csak
    szárazföld és tó. (A vanilla/Kaiserreich tengeri régiókban előfordul egy-egy apró sziget, de egész játszható
    államok tengeri régióban – nálunk Szardínia, Korzika, Málta – nem.) A `newmap.py` `settle_regions()` intézi.
22. **`common/ai_areas`**: az a terület, amelynek a térképen nem marad régiója vagy kontinense (Csendes-óceán,
    Japán, Amerika…), kimarad – üres `strategic_regions = { }` blokk nem maradhat.
23. A `Failed allocate data buffer` sor az `error.log` végén **nem a hiba oka**: működő játékok naplójában is
    megjelenik minden indításkor (a játéklobbi egy elkapott kivétele).
24. **Formátumot ne fejből és ne csak a wiki szövegéből írj**: előbb nézd meg egy működő mod valódi fájlját
    (pl. Kaiserreich `map/` mappa a GitHubon).
25. **A vanilla define-ok között van stratégiairégió-azonosító lista**:
    `NDefines.NGeography.MEDITERRANEAN_SEA_REGIONS = { 29, 68, 69, 168, 169, 202 }` (vanilla régiószámok). A mi
    régióink át vannak számozva és kevesebb van belőlük, tehát ezt **kötelező felülírni** létező tengeri régiókkal –
    a `newmap.py` írja a `common/defines/zz_ante_regions.lua` fájlba, a `validate.py` ellenőrzi. Ez az egyetlen
    ilyen lista a `00_defines.lua`-ban (1.17+); a Millennium Dawn is a saját régióira írja át.
26. **Pozíció → tartomány: a motor a `floor(x)` oszlopot és a `H − 1 − floor(z)` sort nézi** (0. sor = felül).
    Egész számú `z = H − y` ezért **egy sorral a szánt pixel fölé** esik – a tengerre vagy a szomszéd tartományba.
    Minden pozíciót a pixel **közepére** kell tenni: `x + 0.5`, `z = H − y − 0.5`. Ha egy parti tartomány
    kikötő-pozíciója (`naval_base_spawn`) nem a saját tartományába esik, a motor ezt írja a naplóba (csak
    `-debug` vagy `-crash_data_log` mellett!): *„Province N is setup as coastal but has no port building in the
    nudger. This will likely crash the game.”* – és játékindításkor összeomlik. A `validate.py` ezzel a
    számítással ellenőriz.
27. **`colormap_rgb_cityemissivemask_a.dds`**: az RGB a szárazföld színe (ezt szorozza a motor mindenre, az
    országszínekre is), az alfa a városfények maszkja. **RGBA-ként tilos átméretezni**: a Pillow ilyenkor az
    alfával előszoroz, az alfa pedig szinte mindenhol 0, így a szín feketére vált – fekete-fehér térkép, színtelen
    országokkal. A színt és az alfát külön kell átméretezni (`newmap.py`), a `validate.py` jelzi a fekete textúrát.
28. **Nappal–éjszaka**: a térkép-shaderbe **be van égetve** a vanilla térkép greenwichi oszlopa
    (`GMT_OFFSET = 2793`) és déli „hiánya” (`SOUTH_POLE_OFFSET = 0.17`); a térkép szélességét a motor 360°-nak veszi.
    A mi térképünkön Greenwich a 631. oszlop, így Itália a shader szerint **pontosan fél napot késik**: déli 12-kor
    – amikor minden játék indul – ott éjfél van. Az éjszakai oldal sötét (fele fényerő) és fakó (a talaj 80%-ban
    szürkített). Define-nal ez nem állítható, csak a shader módosított másolatával: `tools/daynight.py`.
    Ugyanebben a fájlban van a `//#define NO_NIGHT` kapcsoló, ami az egész éjszakai árnyalást kikapcsolja.
29. A vízszín-textúrák (`colormap_water_0/1/2.dds`) a játékban és minden működő modban **tömörítetlen 32 bitesek**
    (nem DXT5), és a `colormap_rgb_cityemissivemask_a.dds` alfája (városfények) nálunk üres – Kr. e. 509-ben nincs
    villanyfény.

## Állapot (2026-11-12, második kör – statikus javítás, játékban még NEM tesztelve)

Ezen a körön nem volt elérhető a játék, ezért a hibákat a `tools/validate.py` statikus ellenőrzővel és a
HoI4-wiki (Map modding, Troubleshooting) dokumentált szabályaival kerestük meg. A generált fájlokat helyben
javítottuk, és ugyanezek a javítások bekerültek a `newmap.py`-ba és a `build.py`-ba is.

Javítva (zárójelben a szabály száma):

- **Összeomlás játékindításkor**: üres `tutorial/tutorial.txt` (13). ~~`weatherpositions.txt` `big` → `large`~~ –
  **ez tévedés volt**, a harmadik kör visszaállította (12. szabály). A játékbeli teszt szerint a fagyást egyik sem
  szüntette meg.
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

## Játékbeli teszt a második kör után (2026-11-12 19:24) – MÉG MINDIG ÖSSZEOMLIK

A `10fa1db` commit (második kör) letöltve, `tools/validate.py`: **0 hiba, 0 figyelmeztetés**, a leírók egyeznek.
Ennek ellenére a játék **indításkor összeomlik** („Initializing game” után, kb. 15 mp).

- Indítás: `tools/test_launch.ps1 -ExtraArgs "-quickstart -start_tag=ROM"`. Ugyanez történt korábban kézzel
  is (főmenü → 245 AUC → Róma vagy Karthágó → Start Game), tehát nem a gyorsindítás okozza.
- Térképhiba a naplóban: **nincs** (0 X crossing / MAP_ERROR / fractioned). A főmenüig hibátlanul betölt.
- **Ugyanaz a memóriacím, mint a javítások előtt**: `EXCEPTION_ACCESS_VIOLATION at 0x00007FF74DDA4370`
  (verem: `PHYSFS_swapULE64 +11816992, +11811451, +11828402, +12719596, +9971520, +9960447, +34099909`).
  Az időjárás- és az oktatójavítás tehát nem ezt a hibát szüntette meg.
- Furcsaság a `meta.yml`-ben: `LaunchArguments: --gdpr-compliant --quickstart --start_tag=""` – a tag üresen
  érkezett meg (a PowerShell idézőjelezése miatt?). A kézi indítás ettől függetlenül ugyanígy összeomlott.
- A teljes jelentés szöveges része: [`docs/crash_reports/2026-11-12_game_start/`](docs/crash_reports/2026-11-12_game_start/)
  - `exception.txt` – veremlista, `meta.yml` – verzió, rendszer, indítási paraméterek
  - `game.log`, `error_log_tail.txt` (az `error.log` utolsó 40 sora), `error_log_filtered.txt` (az `error.log` a
    hiányzó vanilla tagekre/fókuszokra vonatkozó zaj nélkül)
  - A 45 MB-os `minidump.dmp` nincs feltöltve (szimbólumok nélkül nem olvasható, és memóriaadat van benne);
    ezen a gépen megvan: `Documents/Paradox Interactive/Hearts of Iron IV/crashes/hoi4_20261112_192409/`.
- Legerősebb nyom (első kör felezéses tesztje, „identity” térkép = vanilla tartományok a saját íróinkon át):
  a régi, vanilla-alapú `buildings.txt` mellett a játék **elindult és futott**; amikor abban csak az
  **államszintű épületsorokat** (air_base, anti_air_building, arms_factory, industrial_complex, fuel_silo,
  nuclear_reactor_spawn, radar_station, rocket_site_spawn, stronghold_network, synthetic_refinery) cseréltük a
  generáltakra, **összeomlott**. (Ez még az „inside points” javítás előtti generálással volt.) Érdemes ugyanezt
  a felezést a mostani fájlokkal megismételni.

## Harmadik kör (2026-11-12 este) – javítások a crash report alapján, játékban még NEM tesztelve

A crash report (`docs/crash_reports/2026-11-12_game_start/`) a hiba helyét nem nevezi meg: a verem szimbólumok
nélküli, a `meta.yml`-ben nincs „utoljára olvasott fájl”, az `error.log` utolsó sora pedig ártalmatlan (23. szabály).
Ezért azt kerestük, miben tér el az új térkép attól az „identity” változattól, ami játékban futott (vanilla
térképgeometria a saját íróinkon át). Az alábbiak **csak az új térképen** léteztek, és mind ki lettek javítva – a
kész fájlokban és a generátorban is:

- **Folyók** (20. szabály): 38 folyórendszernek nem volt forrása, 75 mellékfolyó-jelölő 1–2 pixellel elcsúszott a
  torkolattól, volt egy hurok, 4 átlós érintkezés, 17 csonk és 70 pixel a térkép szélén. A játék ezzel a
  folyóréteggel még sosem futott (az „identity” térképen a vanilla folyók voltak). Most 131 szabályos rendszer van.
- **Stratégiai régiók** (21.): a régi „szétszakadt régió” javítás 142 szárazföldi tartományt tett tengeri régióba,
  köztük hat teljes játszható államot (Karalis, Tharros, Malta, Nuragic North, Nuragic Highlands, Corsica) és 13
  pusztaság-államot. Ezek most a legközelebbi szárazföldi régióban vannak.
- **Időjárás-méret** (12.): vissza `big`-re. A második kör `large` átírása hiba volt – az én hibám, a wiki szövegére
  hagyatkoztam a valódi fájl helyett. (A fagyást nem ez okozta: előtte és utána ugyanott omlott össze.)
- **AI-területek** (22.): 24 üres terület törölve.
- **Magasságtérkép**: 621 pixel nem egyezett a tartománya típusával (szárazföld a vízszint alatt és fordítva).
- A `tools/validate.py` mostantól a folyókat, a régiók fajtáját és az AI-területeket is ellenőrzi; a feltöltött
  (hibás) változaton 17 hibát jelez, a mostanin 0-t.

**Őszintén:** egyik pontról sem tudjuk bizonyosan, hogy ez okozta a fagyást. Ha a játék még mindig összeomlik,
ne találgassunk tovább, hanem futtasd az automata felezést:

```powershell
powershell -ExecutionPolicy Bypass -File tools/bisect_launch.ps1
```

- Kb. 13 változatot próbál végig (változatonként ~1 perc): mindegyiknél egy-egy generált fájl leegyszerűsített
  változatát cseréli be (folyók nélkül, államszintű épületsorok nélkül, kikötők nélkül, lapos domborzat stb.),
  elindítja a játékot, feljegyzi, hogy fut-e, majd `git checkout`-tal visszaállítja az eredetit.
- Ha már az első (`baseline`) fut, megáll – akkor kész vagyunk.
- Az eredménytáblát a `docs/crash_reports/bisect_<dátum>.md` fájlba írja: **ezt commitold és told fel**. Ebből
  egyértelműen kiderül, melyik fájl a hibás (vagy az `all_min` sor alapján az, hogy a tartománykiosztás, a
  térképméret, az államok vagy a régiók).
- A `map/` és a `history/states` mappában ne legyen commitolatlan változás (a szkript ellenőrzi).
- A változatok listája: `python tools/make_variants.py --list`.

A felezés `-crash_data_log` kapcsolóval indít, így a crash report `meta.yml`-je az utoljára olvasott fájlt is
megnevezi. Kézi teszthez ugyanez: `tools/test_launch.ps1 -ExtraArgs "-quickstart -start_tag=ROM -crash_data_log"`.

Ami továbbra is gyanús, ha a felezés `all_min` sora is összeomlik:

- a térkép mérete (3328×3072): a wiki szerint szabályos, de ezzel a mérettel a játék még sosem futott –
  `ANTE_MAP=wide` (5632×2048, vanilla méret) generálással ellenőrizhető;
- a keleti térképszél szárazföld, a nyugati tenger: 91 pusztaság-tartomány csak a varraton át „partmenti”.

## Negyedik kör (2026-11-12 éjjel) – a bisect eredménye és a javítás, játékban még NEM tesztelve

**A bisect eredménye** (`docs/crash_reports/bisect_20261112_2015.md`): mind a 13 változat ugyanazon a címen
omlott össze (`0x00007FF74DDA4370`, `LastRead: start_game_command`), az `all_min` is. Ez kizárja a folyókat, az
épületpozíciókat, a kikötőket, az ellátást, a szomszédságokat, a fákat, a városokat, a domborzatot és az
időjárás-méretet. Maradt: valami, ami **a tartalomtól független**, de az új térképhez kötődik.

> **Utólag (ötödik kör):** a játékbeli teszt szerint nem ez volt az ok – lásd lent. A felülírás helyes, bent marad.

**A legvalószínűbb ok** (25. szabály): a vanilla `NGeography.MEDITERRANEAN_SEA_REGIONS` define a 29, 68, 69, 168,
169, 202-es vanilla régiókra mutat. Az új térképen 119 régió van, tehát a 168, 169 és 202 **nem létezik**, a 68
és a 69 pedig szárazföldi régió. Ez megmagyaráz mindent, amit eddig láttunk:

- a vanilla térképes és az „identity” változat futott (ott megvan minden vanilla régió, ugyanazzal a számmal);
- az új térkép minden változata ugyanott fagy, bármit cserélünk a tartalmon;
- a hiba a játék indításakor jön, amikor a motor ezeket a régiókat előkeresi.

Bizonyíték, hogy ez számít: a Millennium Dawn (1.19-es mod) ugyanezt a listát a saját régióira írja át. Ellenjel:
egy 68 régiós 1.18-as mod nem írja felül – erről nem tudjuk, fut-e. Tehát **erős gyanú, nem bizonyosság**.

Javítás:

- `common/defines/zz_ante_regions.lua` (generált): a lista a mi régióinkkal – `{ 28, 45, 46, 71, 72, 82 }`, ezek
  ugyanazok a tengerek (Nyugat-, Közép-, Kelet-Mediterráneum, Tirrén-tenger stb.), csak az új sorszámukkal.
- `common/defines/zz_ante_imperium.lua`: `HANDS_OFF_START_TAG = "ROM"` (a vanilla „HAI” tag nálunk nincs), és a
  világfeszültség kezdődátuma az újabb verziók `NDiplomacy` táblájában is 245.
- A `newmap.py` a régiók átszámozásakor írja a fájlt, a `validate.py` hibát jelez, ha hiányzik vagy nem létező,
  illetve nem tengeri régióra mutat.

Teszt: ugyanaz, mint eddig – `tools/bisect_launch.ps1`. Ha a `baseline` fut, megáll. Megerősítéshez érdemes
`-All` kapcsolóval is lefuttatni: a `no_region_defines` sor (a javítás nélküli állapot) akkor **összeomlik**, a
`baseline` pedig fut – ez bizonyítja, hogy ez volt az ok. Három új változat is van (`no_region_defines`,
`unitstacks_min`, `no_impassable`) arra az esetre, ha mégsem.

Amit ebben a körben **nem** csináltam meg, pedig felmerült: a térkép átültetése a vanilla 5632×2048-as keretbe,
kétoldalt óceánsávval. Egy 4096×3072-es, 1.19-en futó mod (Magna Europa) azt mutatja, hogy nem a méret a gond,
ezért egy ekkora, kipróbálhatatlan átalakítás most több kockázatot hozna, mint hasznot. Ha a fenti javítás után is
fagy, ez a következő lépés (a varrat miatt: a keleti szél szárazföld, a nyugati tenger).

## Ötödik kör (2026-11-12 éjjel) – a hiba megvan: kikötő-pozíciók, játékban még NEM tesztelve

A negyedik kör tesztje (`docs/crash_reports/2026-11-12_round4_baseline/`, `bisect_20261112_2041/2042.md`) szerint
a régió-define javítása **nem** szüntette meg a fagyást (a kontroll és a javított változat ugyanott omlott össze).
A felülírás ettől még helyes és bent marad, de nem ez volt az ok.

A `-crash_data_log` kapcsoló viszont bekapcsolta a hibakereső naplózást, és az `error.log` végén megjelent a
motor saját üzenete, soronként egy tartományra:

> Province 9092 is setup as coastal but has no port building in the nudger. This will likely crash the game.

**Az ok** (26. szabály): a parti pozíciók (`naval_base_spawn`, `floating_harbor`, `coastal_bunker`,
`naval_headquarters`, `naval_supply_hub`, `dockyard`, valamint az egységpozíciók 19-es és 20-as típusa) egész
számú koordinátára kerültek. A motor az ilyen pozíciót egy pixelsorral feljebb keresi, így az **1586 parti
tartományból 686-nak a motor szemében nem volt kikötője** – köztük 11 olyannak, ahol már áll kikötő (Róma is).

Bizonyíték: a naplóvégen szereplő 39 tartomány mind benne van az így kiszámolt 686-ban, és a napló utolsó 24
sora sorrendre is egyezik a számított lista végével.

Ez megmagyarázza az egész eddigi történetet:

- a vanilla-alapú `buildings.txt`-vel a játék futott (ott a vanilla kikötő-pozíciók voltak);
- minden generált változat ugyanott fagyott, és a bisect egyik változata sem segített, mert a parti sorokat
  egyik sem javította (a `buildings_ports_only` és az `all_min` is a hibás sorokat tartotta meg);
- a korábbi `validate.py` nem vette észre, mert `int(H − z)`-vel számolt, ami egész `z`-nél más sort ad, mint
  a motor. Ez az én hibám volt; az ellenőrző most a motor számítását használja.

Javítás:

- `newmap.py` `coast_points()` újraírva: minden parti tartomány a leghosszabb partszakaszának közepén kap pontot,
  a pixel **közepén**; nincs többé mintavételezés és súlypont-tartalék (a régi minden 7. határpixelt nézte, a
  kimaradt szigetek a súlypontjukra kerültek).
- **Új eszköz: `tools/positions.py`** – a kész térképből (játék és `tools/cache` nélkül) újraírja a
  `map/buildings.txt` és a `map/unitstacks.txt` fájlt ugyanazokkal a függvényekkel, amiket a generátor használ.
  Ezzel készültek a most feltöltött fájlok.
- `validate.py`: a motor pixelszámítása; hibát jelez, ha egy pozíció két tartomány határára esik, ha egy parti
  tartománynak nincs kikötő-pozíciója, vagy ha egy megépített kikötőhöz nincs pozíció. Az előző commiton 29
  hibát talál (pontosan a 686 tartományt), a mostanin 0-t.

Teszt: `tools/bisect_launch.ps1` (ha a `baseline` fut, megáll). Ha mégis fagy, a `crashes/<dátum>/` mappából az
`error.log` **utolsó 300 sora** kell – a „Province … has no port building” sorokat most már nem szabad látnunk.

## Hatodik kör (2026-11-12 éjjel) – A JÁTÉK FUT; a fekete-fehér térkép javítva (játékban még nem láttuk)

Az ötödik kör után a játék elindul és fut (`docs/crash_reports/bisect_20261112_2055.md`: `GAME RUNNING`).
A fagyás oka tehát a kikötő-pozíciók elcsúszása volt (26. szabály).

Új hiba volt: **az egész térkép fekete-fehér, egyik országnak sincs színe.** Az ok (27. szabály): a szárazföld
színtextúrája (`map/terrain/colormap_rgb_cityemissivemask_a.dds`) szinte teljesen fekete volt (átlagszín 4/255),
mert a generátor egyben, RGBA-ként méretezte át a vanilla fájlt. Az országszínek fájljaiban (`colors.txt`,
országfájlok) nem volt hiba.

Javítás:

- **`tools/colormap.py`** (új): játék nélkül megfesti a színtextúrát a `terrain.bmp` tereptípusaiból és a
  `heightmap.bmp` domborzatából (természetes színek, délre szárazabb, északon szürkébb, domborzati árnyékolás);
  a városfény-maszk (alfa) megmarad. A most feltöltött fájl ezzel készült.
- Aki előtt ott a játék, az **eredeti vanilla színeket** is visszakaphatja egyetlen paranccsal, a térkép többi
  részének újragenerálása nélkül: `python tools/colormap.py --vanilla` (ezt a részét itt nem tudtam kipróbálni).
- `newmap.py`: a színt és az alfát külön méretezi át, a vízszín-textúráknál is.
- `validate.py`: hibát jelez, ha a színtextúra fekete vagy nem fél térképméretű.

Amit érdemes tudni a színekről: a térkép kb. 90%-a „Terra Incognita” (WLD), ami szürke (90, 90, 90) és
járhatatlan, ezért csíkozva jelenik meg – a játszható országok egyelőre csak Itáliában és Észak-Afrikában
vannak. Ez nem hiba, hanem a váz állapota; a kidolgozásnál érdemes lesz a pusztaságnak barátságosabb megjelenést adni.

## Hetedik kör (2026-11-13) – szürke országok: nappal–éjszaka hiba + képernyőképes teszt

A hatodik kör után a térkép már nem fekete-fehér, de **minden ország szürke**, a Terra Incognita nem csíkos, és
jobb kattintásra sem jelennek meg a diplomáciai színek (zöld / piros / kék).

Amit biztosan tudunk:

- A színfájlok jók: a `colors.txt` és az országfájlok formátuma betűre megegyezik a működő 1.19-es modokéval
  (Magna Europa, Kaiserreich). Nem a színek megadása a hibás.
- **Valódi hiba (28. szabály):** a shaderbe égetett vanilla Greenwich-oszlop miatt a mi térképünkön Itáliában
  déli 12-kor éjfél van. A játék 12:00-kor indul és szünetel, tehát induláskor az egész játszható terület az
  éjszakai oldalon van: sötét és fakó.
- **Évszak-utóhatás:** a vanilla `map/seasons.txt` mind a négy évszakban `hsv_north = { 0 0.1 1 }` – ahol a
  nézet havas, ott a motor az **egész képkocka** telítettségének 90%-át elveszi. A mi térképünk Európa-súlyú és
  január 1-jén indul. Ez az országszíneket és a diplomáciai zöld/piros/kék színt is szürkíti.
- **Országszín-fakítás:** a motor minden országszínt rajzolás előtt megszoroz (telítettség ×0,6, fényerő ×0,8).
  A paletta átlagos telítettsége 0,52 volt, ebből 0,31 maradt – pasztellszürke. Két ország (Szardínia, Korzika)
  színe eleve szürke volt.
- Amit nem tudunk: a három közül melyik mennyit számít. Ezt csak képről lehet eldönteni.

Gyors próba játékban, eszköz nélkül (bármelyik segít, megvan az ok): a jobb alsó eszköztáron a **nappal–éjszaka
kapcsoló** (vagy a konzolban `night`); konzol `debug_postfx` (kikapcsolja az utóhatásokat); konzol `tag_color`.

Teendő a játékos gépen (a shader másolatához kell a játék, itt nem lehetett előállítani):

```powershell
python tools/daynight.py --off
powershell -ExecutionPolicy Bypass -File tools/screenshot.ps1
```

1. Az első parancs a játék saját térkép-shaderének másolatát teszi a mod `gfx/FX/` mappájába úgy, hogy az
   éjszakai árnyalás ki van kapcsolva (és a Greenwich-oszlop a miénk). Kiírja, mely sorokat írta át. Ha azt írja,
   hogy nem talált semmit, azt jelezd – akkor az 1.19-es shader másképp néz ki, mint a régi.
2. A második elindítja a játékot Rómával, négy nagyítási fokon képet ment, majd a képernyő közepére jobb
   kattintva a diplomáciai nézetről is; a képek a `docs/screenshots/` mappába kerülnek.
3. Ha a színek rendben vannak: `git add gfx docs/screenshots`, commit, push – a shader-másolat a mod része marad.
   (Játékfrissítés után a `daynight.py`-t újra le kell futtatni.)
4. **Ha még mindig szürke**, akkor futtasd a változatos tesztet, és azt töltsd fel (kb. 12 perc, 7 indítás):

```powershell
powershell -ExecutionPolicy Bypass -File tools/screenshot.ps1 -Variants colour
```

   Ez változatonként készít képeket: alapállapot, 01:00-s indítás, éjszaka kikapcsolva, éjszaka a helyén,
   1936-os dátum, rikító országszínek, járható pusztaság. A képekből egyértelműen látszik majd, mi számít.

Ebben a körben javítva (játék nélkül is megoldható részek):

- **`map/seasons.txt` (új, semleges):** nincs többé teljes képernyős színtelenítés.
- **`common/defines`:** `COUNTRY_COLOR_SATURATION_MODIFIER = 1.0`, `COUNTRY_COLOR_BRIGHTNESS_MODIFIER = 0.9` – az
  országok a `colors.txt`-ben megadott színükkel jelennek meg. Szardínia és Korzika új, nem szürke színt kapott.
- `common/defines`: `GMT_OFFSET = 631`, `SOUTH_POLE_OFFSET = 0.455` – a motor számoló része (pl. éjszakai harc)
  ezekkel dolgozik; a kirajzolást csak a shader-másolat javítja.
- **`NUM` → `MSY`:** a `NUM` foglalt szó a játék szkriptnyelvében (a wiki szerint az ellenállás-rendszert is
  elrontja), ezért a Massylii országkódja `MSY` lett mindenhol (kód, fájlnevek, zászlók, szövegek).
- A vízszín-textúrák tömörítetlenek lettek, a városfény-maszk üres (29. szabály).
- A Terra Incognita színe sötétszürke (90, 90, 90) helyett világos pergamenszín (176, 164, 138), hogy a
  járhatatlan terület csíkozása látsszon rajta.
- **`tools/screenshot.ps1`**: mostantól ezzel lehet „megmutatni” a játékot annak, aki előtt nincs ott – a
  kidolgozásnál minden látványváltozás után érdemes futtatni és a képeket feltölteni.

## Teszt a hetedik kör után (2026-11-13) – MÉG SZÜRKE

Részletek: [`docs/crash_reports/2026-11-13_round7_colours.md`](docs/crash_reports/2026-11-13_round7_colours.md).
Röviden: a `daynight.py --off` lefutott (a shader-másolat a `gfx/FX/` mappában fel van töltve), a játék fut, de
**az országok még mindig szürkék**. A `tools/screenshot.ps1`-et a **Windows víruskeresője blokkolta**
(„malicious content”), ezért képek nincsenek.

## Nyolcadik kör (2026-11-13) – az egész világ újraépítve Kr. e. 509-re (játékban még NEM tesztelve)

> **Helyesbítés (9. kör):** az alábbi magyarázat csak részben állt meg. A színek hiányának valódi oka a
> `-quickstart` tesztindítás volt (lásd a 9. kört); a járhatatlan vadonra viszont tényleg nem kerül szín.

**Miért volt „szürke” minden?** Kép nélkül nem bizonyított, de a legvalószínűbb magyarázat nem színhiba,
hanem a tartalom: a szárazföld ~90%-a egyetlen, **járhatatlan** helykitöltő ország volt (Terra Incognita).
A játék a járhatatlan államokra **nem fest országszínt** – ott a terep látszik, a diplomáciai nézetben
(jobb kattintás) is –, a kezdés pedig január 1., vagyis a terep jó része havas, fakó. Valódi, színes ország
csak Itáliában, a szigeteken és Tunéziában volt, a térkép töredékén.

**Mi változott:** a térképhez kötődő tartalom teljesen új, egy játék nélkül futó generátorból
(`tools/world.py`, forrás: `tools/data/world_509bc.py`):

- **214 ország + a vadon** (eddig 44 + Terra Incognita): gall, brit, ír, ibér, germán, balti és finnugor
  törzsek, a hallstatti fejedelemségek, illírek, trákok, géták, szkíták és szauromaták, a pontuszi és
  nyugati görög gyarmatvárosok (Massalia, Emporion, Olbia, Pantikapaion, Byzantion, Kyréné…), a hellén
  poliszok (Athén, Spárta, Korinthosz, Argosz, Thébai, Thesszália, Makedónia…), Kolkhisz, a föníciai
  városok, Tartésszosz és Gadir, a líbiai törzsek, a garamantok, Kús, D'mt, Sába és a dél-arábiai
  királyságok, a masszagéták és szakák – és I. Dareiosz **Perzsa Birodalma** Trákiától Egyiptomon át
  Baktriáig, szatrapiánként felosztva (Parsa, Mada, Babirush, Mudraya, Sparda, Yauna…).
- **634 állam** (573 játszható, 61 járhatatlan vadon: Szahara, Arab-sivatag, sós sivatagok, a messzi észak).
  A szárazföld ~74%-a mostantól játszható, színes ország. Itália 66 állama változatlan.
- **Városok a valódi helyükön**: a győzelmi pontok földrajzi koordinátából kerülnek a tartományokra
  (`tools/geo.py`), kikötőkkel. Minden ország fővárosa a történelmi székhelye.
- **Színek**: kultúránként színcsalád (kelták zöld, görögök kék, szkíták narancs, illírek lila, trákok
  rózsaszín, germánok türkiz, Perzsia arany…), a szomszédok mindig jól elütnek egymástól. A vadon homokszínű.
- **Zászlók** (procedurális, kultúránként más jelkép), **névlisták** az új kultúrákhoz.
- **Úthálózat**: minden játszható államban ellátó csomópont, országon belül a fővárosból kiinduló úthálóval
  (1-es szintű „vasút”), és minden szárazföldi határon át egy összekötő úttal – eddig csak csonkok voltak.
- **Gazdaság**: a műhelyek száma országonként, a népességgel lassulva nő (Róma 2, Athén 5, Karthágó 14,
  Perzsia 74 civil), hogy a nagy birodalmak erősek legyenek, de ne nyomjanak agyon mindent.
- A régi generátorok (`newmap.py`, `build.py`) véletlen futtatás ellen védve; a víruskereső által blokkolt
  `tools/screenshot.ps1` törölve, helyette `tools/collect_screenshots.ps1` (csak a játék saját F11-képeit másolja).

**Ami szándékosan maradt:** a tartományháló és minden raszter (domborzat, folyók, terep), a stratégiai
régiók, az átkelők, az időjárás – ez a változat tölt be és fut bizonyítottan a játékban.

**Ismert korlátok:** a tartományháló Görögországban durva (Attika egyetlen tartomány), ezért Megara és
Aigina kimaradt; a térkép keleti szélén (Indus, Közép-Ázsia) a régi generátor apró, négyzetrácsos
kitöltő tartományai megmaradtak; a népességek nagyságrendi becslések; seregek továbbra sincsenek
(`history/units` üres), mindenki békében kezd.

**Teszt:** lásd a „Tesztelés” részt fent (a 8. körben még `-quickstart`-tal kértem – az volt a hiba).
Ha fut: nyomj **F11**-et teljesen kizoomolva, Itáliára közelítve, és egy országra jobb kattintás után, majd
`powershell -ExecutionPolicy Bypass -File tools/collect_screenshots.ps1`, és `git add docs/screenshots`,
commit, push. Ha nem indul: az `error.log` **vége** és az `exception.txt` kell, mint eddig.

## Kilencedik kör (2026-11-13 este) – A SZÍNEK JÓK; a hibát a gyorsindítás okozta. Játékban ellenőrizve.

Simnek is lett HoI4-e (1.19.5), így ezt a kört már **játékban néztük meg** – képek: `docs/screenshots/20261113_round9_*.jpg`.

**Mi derült ki**

- **Az országszínek működnek.** A főmenüből indított játékban (és az országválasztó képernyőn is) a mod
  térképe teljes színekben jelenik meg, a diplomáciai nézet zöld/piros/kék jelölése is megy.
- **A „színtelen / szürke országok” oka a `-quickstart` volt.** A motor gyorsindítása nem rajzolja ki a
  politikai színréteget – az alapjáték ugyanígy néz ki vele, mod nélkül is. Minden eddigi teszt (a
  `test_launch.ps1 -ExtraArgs "-quickstart …"`) ezzel indult, ezért látszott három körön át hibásnak a térkép.
- Kizárva (helyben, kísérlettel): a textúrák illesztése a térképre jó (rácsmintás próbatextúra pontosan a
  partvonalakra esett), a dátum, a járhatatlan vadon és a shader-másolat sem befolyásolta.

**Mi változott**

- **Tesztindító** (`tools/test_launch.ps1`): nincs többé gyorsindítás. Alapból a főmenüig indít; a
  `-Continue` a játék `--continuelastsave` kapcsolójával kattintás nélkül betölti az utolsó mentést (ott a
  színek rendben vannak). A játékot magától megkeresi, a Documents-beli leírót ő írja.
- **Nappal–éjszaka** (valódi hiba volt): a shader a térkép teljes szélességét 360 foknak veszi, a miénk csak
  88,6 fok. Emiatt a nappal–éjszaka határ éles függőleges vonalként állt a térkép közepén, a fele mindig
  éjszakában volt. A shader-másolat (`gfx/FX/standardfuncsgfx.fxh`) mostantól a hosszúságot is arányosítja
  (`LONGITUDE_SHARE`), az éjszaka-kikapcsolás (`NO_NIGHT`) kikerült: a napszakok úgy váltakoznak, mint az
  alapjátékban Európa fölött. A `tools/daynight.py` ugyanezt állítja elő (1.19.4 és 1.19.5 alatt azonos).
- **Zászlók és pártnevek**: ahol a mi országkódunk egyezik egy alapjátékbelivel (36 ilyen van), a játék az
  alapjáték ideológiás zászlóját vette elő – Róma (ROM) a **román zászlót** viselte, a pártja „PNL” volt.
  A `world.py` ezekhez megírja a négy ideológiás zászlót is, és minden országnak ókori „pártneveket” ad
  (Róma: Senatus Populusque Romanus).
- A `tools/mapdata.py` bármelyik meghajtón megtalálja a játékot (`HOI4_DIR` felülírja).

**Ismert, még nyitott**

- Az `error.log` ~34 ezer sora szinte mind az alapjáték szkriptjeiből jön, amelyek nem létező országokra
  (GER, FRA…) hivatkoznak – ártalmatlan, de zajos; kitakarítása külön feladat.
- A vezetők arcképe és sok felirat még az alapjátéké (1936-os öltönyös urak); seregek nincsenek.
- A tartománytipp „helyi idő” sora a motor számítása, a mi térképünkön pontatlan.

## Tervezett fázisok

0. Alapozás – kész.
1. Váz: államok, országok, modern tartalom kiürítése – a játék fut, a teljes világ (214 ország) kész és játékban ellenőrizve (2026-11-13).
2. Technológiák, egységek (hoplita, manipulus, harci elefánt…), felszerelés, ipar.
3. Róma és szomszédai teljesen játszhatóan (Kr. e. 509).
4. A többi nép és fókuszfa (egész Európa: kelták, germánok, szkíták, ibérek, görögök, Perzsia…).
5. Második kezdés: 490 AUC (Kr. e. 264).
6. AI, egyensúly, grafika, magyar/angol szöveg. (A HoI4-ben nincs magyar nyelv; magyar szöveg csak az angol fájlok helyén lehet.)

## Szabályok a fejlesztéshez

- **Az alapjáték fájljait soha nem módosítjuk**, csak ezt a mod mappát.
- Más modok (pl. „Total War Rome 2 in HOI4”) grafikáját nem másoljuk. Saját/procedurális vagy CC0 grafika.
- Vanilla fájlokat a mod olvashat és módosított másolatként felhasználhat (ez normál modolás).

## Teszt a nyolcadik kör után (2026-11-13) – fut, de a színek még hiányoznak

A játék Rómával elindul és fut. A nevek, határok és városok a helyükön vannak, de országszín-kitöltés sehol nincs, a játszható országokon sem. Részletek: `docs/crash_reports/2026-11-13_round8_test.md`, képek: `docs/screenshots/20261113_*.jpg`.

## Teszt a kilencedik kör után (2026-11-13) – AZ ORSZÁGOK SZÍNESEK

Menüből indítva (gyorsindítás nélkül) minden ország színes, Róma zászlaja és pártja saját, nincs összeomlás. Részletek: `docs/crash_reports/2026-11-13_round9_test.md`, képek: `docs/screenshots/20261113_1854*.jpg`.

## Tizedik kör (2026-11-13, Claude) – nagyobb általános fókuszfa, saját vezetők, gyorsítás

- **Általános fókuszfa** (`common/national_focus/ante_generic_focus.txt`, 28 fókusz, generálja a `tools/content.py`):
  három ág + csúcs. *Államvezetés és istenek* (Vének tanácsa, Szokásjog, Az istenek tisztelete, Adó, Követek,
  Jóslatok = +1 kutatóhely, Írnokok, Játékok és ünnepek, Egy nép), *Föld és munka* (Piacok, Erdőirtás, Kézművesek,
  Bányák, Utak, Kovácsműhelyek = hadiüzem, Nagy építkezések, Kőváros), *Háború* (Hadfelkelés, Lándzsások
  kiképzése, Bronz és vas, Lovas nemesek, Erődített dombok, Tengerjárók = hajógyár, csak tengerparti
  országnak, Felesküdött kíséret, Hódító szándék, A nép hadserege), csúcs: *Felemelkedés*. 9 új nemzeti szellem
  (`common/ideas/ante_generic_ideas.txt`), csak alapjátékos ikonokkal és módosítókkal.
- **Saját vezetők** 28 országnak (`tools/data/leaders_509bc.py` → `common/characters/ante_leaders.txt`,
  tulajdonságok: `common/country_leader/ante_traits.txt`). Valódi személyek: Róma – Lucius Junius Brutus,
  Karthágó – Hamilcar, Perzsia – I. Dareiosz, Athén – Kleiszthenész, Spárta – I. Kleomenész, Clusium – Lars
  Porsenna, Latin Liga – Octavius Mamilius, Makedónia – I. Amüntasz, szkíták – Idanthürszosz, Kús – Amaniastabarqo,
  Küréné – IV. Battosz, szakák – Szkunkha, agathürszoszok – Szpargapeithész, Kroton – Milón, odrüszök – Térész,
  masszagéták – Tomürisz. A nagy törzseknek, amelyek uralkodóit nem ismerjük név szerint, kitalált (a leírásban
  jelölt) vezetők. A `world.py` írja a `recruit_character` sorokat. Portrék még nincsenek (az alapjáték általános
  képei látszanak).
- **Lassulás:** a mod térképe minden mérőszámban kisebb az alapjátékénál (8041 vs 10155 szárazföldi tartomány,
  634 vs 1081 állam, 119 vs 304 stratégiai régió), és futás közben sincs hibaáradat a naplóban. Ami több: **~215
  gépi ország egyszerre** (az alapjáték 1936-ban ~70–90). Ezért a `zz_ante_imperium.lua` ritkábban futtatja azokat
  az AI-rutinokat, amelyeknek Kr. e. 509-ben nincs dolguk (szerepek, tengeri célok, sablonok, felszerelés, piac,
  légierő, portyák, kereskedelmi útvonalak). Továbbá: a `-crash_data_log` / `-debug` kapcsoló maga is lassít
  (sok extra naplózás), sebességet ezek nélkül érdemes nézni.
- Pipeline: `python tools/world.py` → `python tools/content.py` → `python tools/validate.py` (0 hiba).
  Betöltési teszt a főmenüig: az új fájlokra nincs hibaüzenet az error.log-ban.
- **Portrék** (2026-11-13): a 28 vezetőnek saját, festményszerű portréja van (`gfx/leaders/ante/`, rajzolja a
  `python tools/portraits.py`, saját kód, külső kép nélkül, CC0). Népenként más viselet: római babérkoszorú és
  tóga, perzsa csipkés korona, pun kúpos süveg, spártai korinthoszi sisak, makedón kausia, kusita sapkakorona
  két ureusszal, szkíta/szaka csúcsos sapka, trák rókaprém sapka, líbiai tollak, északi népeknél hosszú haj és
  torques. `--preview FÁJL` egy áttekintő képet is ír. Pipeline: world.py → portraits.py → content.py → validate.py.

## Tizenegyedik kör (2026-11-13, Claude) – általános portrék, ókori egységek, kezdő seregek

- **Általános portrék népenként** (`tools/portraits.py`): 16 nép × 4 arc (kelta, görög, latin, etruszk, ibér, északi,
  szkíta, szaka, trák, illír, perzsa, pun, líbiai, kusita, arab, anatóliai, kaukázusi, nuragikus szárd). **Ezek csak
  általános portrék**: minden vezető és tábornok, akinek nincs saját képe, a népe arcai közül kap egyet
  (`portraits/00_portraits.txt` felülírja az alapjáték modern arcait, országonként a kultúrája szerint).
- **Ókori egységek** (`tools/army.py` → `common/units/ante_units.txt`): Levies (népfelkelők), Spearmen (lándzsások),
  Hoplites (hopliták), Skirmishers (parittyások, gerelyvetők), Archers (íjászok), Cavalry (lovasság), Horse Archers
  (lovasíjászok), Chariots (harci szekerek), War Elephants (harci elefántok – még zárolva, a 264-es kezdéshez),
  támogatók: Siege Train (ostromgépek), Mounted Scouts (lovas felderítők). Saját felszerelés: lándzsa és pajzs,
  hoplita fegyverzet, íj és parittya, ló, harci szekér, ostromgép, elefánt.
- **A modern egységek kikerültek**: a tank, gépesített, motoros, modern tüzérség, páncélautó, mérnök stb.
  alapjátékos fájljai üres felülírást kaptak; a puska (infantry equipment) nem gyártható. Az alapjáték saját
  szkriptjei emiatt betöltéskor „Invalid subunit” sorokat írnak a naplóba – ártalmatlan. A hajók és repülők
  egyelőre maradtak (következő lépés: triérészek stb.).
- **Ikonok a HoI4 stílusában, ókori változatban**: zöld sziluett + katonai jelkép a hadosztálytervezőben, barna
  sziluett a felszereléseknél (sisak forgóval, ló, harci szekér, íj, gerelyek, ostromtorony, elefánt) – saját rajz, CC0.
- **Kezdő seregek erő szerint**: 411 hadosztály, országonként 1–24 a hadra fogható népesség alapján (Perzsia 24,
  Karthágó, Spárta, Athén több, a kis városállamok 1–2). Kultúránként más sablon: görög „Phalanx” (hopliták +
  könnyűgyalogság), római „Legio” (archaikus, hoplita alapú), itáliai „Touta”, kelta/germán „Warband”, szkíta
  „Horde” (lovasíjászok), perzsa „Hazarabam” (lándzsások + íjászok + ostromgépek), pun „Host”, líbiai „Raiders”,
  kusita „Bowmen”; Thesszália, Makedónia lovas, a garamantok és kaledónok szekeres alakulatokkal.
- Teszt: validate 0 hiba; gyorsindítással Rómával GAME RUNNING (a seregek betöltenek, nincs összeomlás); menüből
  indítva a főmenüig hibátlan.

## Tizenkettedik kör (2026-11-13, Claude) – hajók, gyártási ikonok, manpower, kultúra-szellemek, Róma fája előkészítve

- **Ókori hajók** (`tools/army.py`): Penteconter (ötvenevezős, könnyű „screen”), Trireme (triérész, a sorhajó),
  Quinquereme (zárolva, a pun háborúk korára). A modern hadihajók (csatahajó, cirkáló, romboló, tengeralattjáró,
  anyahajó) üres felülírást kaptak. **140 hajó** a kezdésre a tengeri hagyomány szerint: Karthágó, a görög
  városok és az etruszkok nagyobb, Perzsia 20 hajós (föníciai és ión) flottával, a többi kikötős ország 0–2
  ötvenevezőssel. Fájl: `history/units/<TAG>_245_naval.txt` (`set_naval_oob`).
- **Gyártási ikonok**: minden gyártható felszerelésnek és hajónak saját, színes tárgyképe van
  (`gfx/interface/technologies/*_1.dds`, `GFX_<felszerelés>_1_medium`), plusz hajóikonok a flottanézethez.
- **Manpower**: az ok a „volunteer only” törvény (a népesség 1,5%-a) volt – Róma 40 000 lakosából ~600 fő, miközben a
  seregei ~9000-et kötöttek le. Javítás: a zászlóaljak 500 fősek (ókori lépték), és a kultúra-szellemek
  +4…+15% besorozást adnak (Róma +15%).
- **Kultúra-szellemek** (nemzeti szellem minden népnek a valós kultúrája szerint, `ante_culture_*`): civilizáltak
  (görög, latin, etruszk, pun, perzsa, anatóliai) kutatás/rend/gazdaság; „barbárok” (kelta, germán, északi, ibér,
  trák, szkíta, líbiai) harc/besorozás/szívósság, lassabb kutatás. Latin kultúra csak Róma körül (Róma, Latin Liga).
  **Róma: „Roman Virtus: We Never Give Up!”** – +40% kapitulációs határ (sokkal több területet kell elveszítenie,
  hogy kapituláljon), +15% besorozás, háborús támogatottság, morál.
- **Róma fókuszfája előkészítve**: `common/national_focus/ROM_focus.txt` (11 fókuszos váz: Regifugium, consulok,
  a plebs kivonulása, néptribunusok, Capitoliumi templom, Sibylla-könyvek, centuriák, Horatius, Regillus-tó,
  Foedus Cassianum, aequusok és volscusok), terv: `docs/rome_focus_tree.md`.
- Teszt: validate 0 hiba; gyorsindítással Rómával GAME RUNNING (hajók, flották, szellemek betöltenek).

## Tizenharmadik kör (2026-11-13, Claude) – Róma teljes fókuszfája, öt nagyhatalom alapfája, kiválasztó képernyő, Nok
- **Róma fókuszfája kész (38 fókusz, 13 nemzeti szellem)** a `docs/rome_focus_tree.md` hat ága szerint:
  Res Publica (plebs kivonulása → Tizenkét tábla → Lex Hortensia; a „Rendi harc” büntető szellem lépésenként
  „Concordia Ordinum”-má válik), az istenek Rómája (Sibylla-könyvek, Vesta-szüzek, Ludi Romani, Evocatio),
  a légió születése (stipendium → Camillus → manipulusos légió → Via Appia, Aqua Appia → coloniák),
  Latium és Etrúria (Regillus, Foedus Cassianum = frakció a Latin Ligával, Coriolanus, Veii, Dél-Etrúria),
  a gall vész (Allia „Vae Victis” → Servius-fal → Camillus, a második alapító) és Itália ura
  (latin háború, szamnisz háborúk, Sentinum, Tarentum és Pyrrhus, Italia, Szicília felé).
- **Alap fókuszfák (13–16 fókusz, saját szellemek):** Athén (Kleiszthenész, Laurion ezüstje, Themisztoklész
  flottája, Marathón, Déloszi Szövetség, Parthenón), Spárta (agógé, helóták, krüpteia, Peloponnészoszi Szövetség,
  háború Argosz és Athén ellen, Molon labe), Makedónia (hetairoi, pezhetairoi, szarisza, Khalkidiké, thesszáliai
  szövetség), Perzsia (szatrapiák, királyi út, halhatatlanok, Perszepolisz, föníciai flotta = Szidón/Türosz/Arvad
  bábállam, Behisztun, „föld és víz”), Karthágó (Magonidák, kóthón, római szerződés, Szardínia, Szicília,
  Hanno útja, ibériai ezüst, Szent Csapat).
- Generátor: `tools/national_trees.py` (a `content.py` hívja). A régi Róma-váz innen jön, ugyanazokkal az azonosítókkal.
- **Kiválasztó képernyő:** a 7 nagy hely: Róma, Karthágó, Perzsia, Athén, Spárta, Makedónia, Szürakuszai; alattuk
  kisebbek: Clusium, Latin Liga, szkíták, masszagéták, Kús, Küréné, Thesszália. Mindegyik saját leírást és a
  kultúra-szellemét mutatja.
- **Nok törölve:** a Terra Incognita teljesen elzárta (se szomszéd, se kikötő). A földje a vadon része lett.
  Emiatt az államok azonosítói átszámozódtak (régi mentések nem tölthetők).
- Teszt: validate 0 hiba; `-quickstart -start_tag=ROM -crash_data_log` fut, az error.log-ban nincs hiba az új fákról.

## Tizennegyedik kör (2026-11-13, Claude) – Róma fája döntésekkel, a király megtartása
- **Két, egymást kizáró kezdés:** *Regifugium* (köztársaság, bal oldal) vagy *The King Remains* (jobb oldal,
  x 22–29): Tarquinius Superbus a trónon marad, Brutus visszavonul, a kormány egyeduralmi lesz, Tarquinius a vezető
  (saját portré; a kezdéstől a nem kormányzó királypárti párt vezetője, a fókusz `promote_character`-rel emeli hatalomra).
- **Döntéspárok a köztársasági ágakban** (mindkettő továbbvisz): néptribunusok ↔ az atyák uralma;
  Lex Hortensia (Concordia) ↔ Nobilitas; Apollón és Aszklépiosz ↔ Mos maiorum; manipulusos légió ↔ polgári
  phalanx; Foedus Cassianum ↔ Latium karddal; az Allia után: fizesd ki az aranyat ↔ „nem arannyal, vassal”;
  Pyrrhus-háború ↔ szerződés Tarentummal (bábállam); a végén Szicília felé ↔ Gallia Cisalpina.
- **A királyság ága** (16 fókusz): összeesküvők megtorlása → zsarnokság ↔ a nép királya; Celeres, Cloaca Maxima,
  a Sibylla könyveinek megvétele, etruszk mesterek, a Latin Liga feje (bábállam), Gabii csele, Etrúria lucumója
  (Porsenna ellen), a tizenkét város, Regnum Italiae, szamnisz hegyek / Magna Graecia → Itália királya.
- Róma most 66 fókusz, 20 kizáró pár. Validate 0 hiba; `-quickstart -start_tag=ROM` fut, az error.log tiszta (a fókusz effektjei: set_politics,
  promote_character, retire_character a „The King Remains”-ben).

## Tizenötödik kör (2026-11-13, Claude) – ókori ideológiák, hadvezérek, gazdaság, nehezebb fókuszok, épületek
- **Ideológiák ókori néven** (a kulcsok maradnak, csak a nevek): demokratikus = Köztársaság (arisztokratikus
  köztársaság / demokrácia / népgyűlés), semleges = Királyság (királyság, oligarchia, papkirályság, szatrapia),
  fasiszta = Türannisz, kommunista = Törzsi uralom (törzsfőség, harcos csapat, ősi szokás). A törzsi népek most a
  „törzsi” ideológiát kapják. Fájl: `localisation/english/replace/ante_ideologies_l_english.yml` (content.py).
- **Tarquinius koronát visel** (`roman_king` stílus, `LEADER_STYLE` a portraits.py-ban).
- **A folyamatos fókuszok doboza** a fa legalsó sora alá került (`continuous_focus_position`), nem takar ki fókuszt.
  A generikus fa írása kimaradt a content.py-ból a 13. körben (a régi fájl maradt meg) – visszatéve.
- **Hadvezérek:** `tools/commanders.py` – minden hadsereggel bíró népnek tábornok, 8+ hadosztálynál hadvezér
  (marsall), 4+ hajónál admirális: 6 marsall, 225 tábornok, 10 admirális. Történelmi nevek: Róma (Valerius
  Publicola, Larcius, Postumius, Horatius Cocles, Mucius Scaevola), Karthágó, Perzsia (Mardonios, Megabazos, Datis),
  Athén (Miltiadész, Kallimakhosz, Arisztidész, Themisztoklész), Spárta (Démaratosz, Dórieusz, Leónidász), stb.
- **Róma gazdasági ága** (x 35–39, mindkét útról elérhető): Forum Boarium, Via Salaria, sólepárlók, tiberisi kikötő,
  aes signatum, ager publicus, kovácsok, Juno Moneta pénzverde, nagy közmunkák.
- **A király megtartása most fáj:** „The People Hate the King” (−25% stabilitás, −30% népességnövekedés, −25%
  politikai erő és építés, …). Csak a királypárti ág (x 31–33) enyhíti fokozatosan: amnesztia, gabona Kümétől, a
  telepesek visszahívása, zavargások leverése ↔ a nép meghallgatása, végül „A Loyal Rome” (stabilitás > 40% kell).
- **Nehezebb fókuszok:** a nagy lépések hosszabbak (105–175 nap), feltételhez kötöttek (pl. Dél-Etrúria csak Veii
  bukása után, Italia 20 állam + a szamniszok és a latinok legyőzése után, a hellén hegemónia csak Athén/Argosz
  után) és némelyik hátránnyal jár (Pyrrhus-háború: −3000 ember, Allia: −10% stabilitás, …). `TUNE` a
  national_trees.py-ban.
- **Épületek:** `tools/buildings.py` – ókori nevek (Workshops, Armoury, Shipyard, Harbour, Roads, Fortifications,
  Sea Walls); a modern épületek (repülőtér, légvédelem, radar, szintetikus finomító, üzemanyagraktár, rakéta,
  atomreaktor, …) kikapcsolva (`dlc_allowed = { always = no }`). Ikonok még az alapjátékéi.
- Pipeline: world → portraits → army → buildings → content → commanders → validate (0 hiba). Játékban még nem
  futott ez a kör.
- Teszt: `-quickstart -start_tag=ROM -crash_data_log` fut, az error.log-ban nincs hiba a kör fájljairól. A Latium-ág
  két fókusza (Foedus Cassianum / Latium by the Sword) egymásra csúszott: szétrakva, és a `check_tree` most minden
  fában hibát ad, ha egy sorban két fókusz 2 egységnél közelebb van.
- A fókuszok államszám-feltételei most a **bábállamok államait is beszámítják**: `ante_realm_states` változó
  (saját + minden alattvaló ellenőrzött állama), a kezdéskor és hetente számolva
  (`common/on_actions/ante_on_actions.txt`, content.py), saját tooltippel („… the states of its subjects included”).
- **Elakadás javítva (Clusium):** a királysági ágban a „Lucumo of Etruria” háborús célt adott Clusiumra, mielőtt Róma
  határos lett volna vele, a következő fókusz pedig Clusium bukását kérte → elakadt a fa. Most előbb „The Twelve
  Cities” jön (Veii, Caere, Tarquinii – a szomszédok), utána a Lucumo, és csak akkor vehető fel, ha Róma már határos
  Clusiummal (vagy Clusium nincs többé); a Regnum Italiae már nem függ tőle. Általános szabályok a `TUNE`-ban:
  `reach(TAG)` = határos vagy nem létezik (a szamnisz háborúknál is), `gone(TAG)` most a szövetséges (frakciótárs)
  ellenfelet is „legyőzöttnek” veszi (pl. Makedónia–Thesszália), Perzsia koronája a szkíták VAGY Athén legyőzését kéri.

## Tizenhetedik kör (2026-11-13, Claude) – ókori technológiafa, AUC évszámok
- **Az alapjáték technológiái eltávolítva** (`replace_path="common/technologies"`), helyettük **66 ókori technológia**
  (`tools/data/tech_tree.py` → `tools/tech.py`), 7 oldalon, az alapjáték felületét használva, ókori névvel:
  Arms and Armour, Auxiliaries and Supply, Horse and Chariot, Siege Craft, Seafaring, Learning, Crafts and Building.
  A légierő oldalai és a DLC-s duplikátumok (NSB páncélos, MtG haditengerészet) elrejtve – mindenki ugyanazt látja.
- **Évszámok AUC-ban:** a technológiaképernyő évfeliratai 245–485 AUC (Kr. e. 509–269), oldalanként egyenletesen;
  a technológiák `start_year`-je ugyanez, így a felirat, a sor és az „idő előtti” büntetés egyezik.
  `zz_ante_imperium.lua`: 1 kutatási pont = 365 nap, évenkénti előrekutatási büntetés 8% (a sorok 20–40 évre vannak).
- **Új felszerelés-változatok** (army.py `VARIANTS`): vasfegyverek, kovácsolt acél; linothorax, láncing és scutum;
  összetett íj, ólom parittyagolyó; tenyésztett harci lovak, szarvas nyereg; kaszás harci kocsi; ostromtorony,
  torziós gépek. A harci elefántot és a quinqueremét technológia nyitja.
- Egyéb technológiák: zárt/nyitott rend, manipulusok, rövid kard, ellátóoszlopok, katonai utak, felderítők, kémek,
  megerősített tábor, tábori orvosok, lovasíjászat, nehézlovasság, földsánc, kőfal, poliorkétika, kos, diekplous,
  hajószínek, tengerészgyalogság, világítótornyok, írás, iskolák, filozófia, Akadémia, Múszeion, geometria,
  csillagászat, mechanika, orvoslás, retorika, írott jog, vasolvasztás, fújtatós kemence, állami műhelyek,
  mészhabarcs, opus caementicium, öntözés, vasekevas, mélybányászat, vízimalom, pénzverés.
- Kezdő technológiák (history, world.py): mindenkinek a bronzkori alapok; a városias népeknek az írás és a
  kőművesség is. Ikonok: saját rajz (tech.py, CC0).
- Validate 0 hiba. Játékban még NEM futott.
- **Javítás a játékbeli teszt után:** a technológiák nem látszottak („Found no grid box for tech”): minden fa
  gyökerének kell egy `<gyökér>_tree` rácsdoboz az oldal felületén – a tech.py most egy alapjátékbeli doboz helyére
  másolja őket (`ANCHOR`). A függőleges oldalakon (ló, ostrom, tudás, mesterség) a nagy dobozok 3 rácsegységre
  kerültek (egymásba lógtak). **Egyensúly:** a fa 245–365 AUC közé sűrítve (a 40 éves sorközök miatt az elején alig
  lehetett kutatni), 1 kutatási pont = 180 nap, évenkénti előrekutatási büntetés 5%.

## Tizennyolcadik kör (2026-11-14, Claude) – a technológiafa finomítása, játékban ellenőrizve
Képek: `docs/screenshots/20261114_techtree_*.jpg` (Sim gépén, 1.19.5).
- **Ókori kategóriacímek** a sávok fölött a modern „WEAPONS & EQUIPMENT”, „MOBILE INFANTRY”, „LIGHT”, „ANTI-AIR”,
  „DESTROYERS”, „SYNTHETIC OIL” … helyett: Blades, Armour, Bows and Slings, Drill and Order of Battle; Baggage and Roads,
  Scouts and Spies, Camp and Surgeon; Horses, Chariots, Riders, Elephants; Engines, Walls; Oared Warships, Harbours;
  Letters, Natural Philosophy, Medicine, Law and Oratory; Metalwork, Building, Farming, Mining, Coin
  (`LANES` a `tools/data/tech_tree.py`-ban). A „Civilian Train” felszerelés neve „Mules and Carts”.
- **Kikerült, ami nem odaillő:** a háttérfotók (katonák, rádiós, tankok, ágyú, tengeralattjáró, gyár), a támogatás oldal
  üres „Trains” keretei, a Tudomány oldal második (az alapjáték csodafegyver-fájához tartozó) évszám-oszlopa, és a
  lapfülek modern ikonjai – helyettük sisak, kerék, ló, katapult, gálya, tekercs, üllő (`TABS`, a játék keretére festve).
  A rejtett oldalak lapfülei utáni rés is eltűnt.
- **Ikonok középen, semmi nem lóg ki:** a kis dobozban (72×72) a játék a bal felső sarokhoz (3,3) igazítja az ikont, a
  nagyban középre. Eddig minden ikon 109×30-as vagy 61×54-es volt; most a kis dobozokba 64×64-es, a nagyokba
  oldalanként méretezett kép kerül (`tech_icon` a `tools/tech.py`-ban).
- Tanulság: a felület elemeit **nem szabad törölni** (a játék név szerint keresi őket, és törlés után meg sem nyitja a
  kutatási képernyőt) – a tech.py üres képre, üres feliratra cseréli vagy a képernyőn kívülre tolja őket. Egy méretezett
  rácsdoboz a fáját a saját **közepéhez** igazítja (ezért áll a ló- és ostromfa a képernyő közepén).

## Tizenkilencedik kör (2026-11-14, Claude) – Róma két útja: mérők, események, döntések, játékban ellenőrizve
A fókuszfa eddig egyenes sor volt („most X, aztán Y”); most mindkét út mögött egy élő rendszer áll
(`tools/rome_story.py`, részletek: `docs/rome_focus_tree.md`, „A két út rendszerei”).
- **Köztársaság – a rendi harc mérője** (0–100, a Regifugium 40-ről indítja): háború hetente növeli, béke csökkenti,
  a plebs felé tett lépések csökkentik, a patrícius lépések növelik (cserébe PP). A szellem az értékkel skálázódik
  (+10% stabilitás 0-nál, −20% 100-nál). 80-nál a plebs kivonul (esemény, három válasz); a Lex Hortensia csak 30 alatt.
- **Királyság – a nép gyűlöli a királyt** (0–100, 70-ről indul): −stabilitás, −PP, −besorozás, −népesség, −építés az
  értékkel arányosan. 50 fölött összeesküvések, Brutus 80-nál leveti az álarcot, 100-nál Róma fellázad: polgárháború,
  ha már 3+ állam az övé, előtte forradalom (a király elmenekül, Róma mégis köztársaság lesz, a királyi fókuszok
  lezárulnak). A gyűlölt király ága és a hódítások csökkentik; a Hű Róma csak 30 alatt.
- **12 esemény:** Tarquiniusok száműzetésben, Porsenna (Clusium valóban hadat üzen), évenkénti consulválasztás, a plebs
  kivonulása, Spurius Cassius, a diktátor és a fasces; összeesküvés, tőrök a Forumon, Brutus a bolond, Brutus
  leleplezi magát, Lucretia, Róma fellázad. Saját, procedurálisan rajzolt eseményképek (`gfx/event_pictures/ante_rome_*`).
- **8 döntés** a „Res Romana” kategóriában (adósságelengedés, gabona, földosztás, a nép fegyverbe hívása, diktátor;
  a király játékai, kémek, robotmunka).
- A fa feltételei a helyzethez kötöttek: Horatius csak Porsenna lépése után, a Regillus-tavi csatánál a Latin Liga
  tényleg hadat üzen, a Foedus Cassianum csak békében köthető.
- Tanulságok: Róma kezdetben **egyetlen állam**, és egy államnál a `start_civil_war` semmit sem csinál; a
  `complete_national_focus` viszont a kizáró fókuszt is teljesíti. A triggernév `num_of_controlled_states`
  (a `num_owned_controlled_states` csak változóként létezik).
