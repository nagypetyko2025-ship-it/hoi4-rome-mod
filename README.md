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
| `tools/data/world_245.py` | **Forrásadat**: Kr. e. 509 népei (45 ország) és államai, népesség, városok, kikötők. Az alapjáték (vanilla) tartományszámaival. |
| `tools/newmap.py` | Térképgenerátor: kivágja és felnagyítja a vanilla térképet, új, sűrűbb tartományhálót növeszt. Ír: `map/**`, `common/ai_areas/default.txt`, `tools/cache/newmap.*`. |
| `tools/build.py` | Összeállító: a `world_245.py`-ból államok, országok, zászlók, épületpozíciók, ellátás, szövegek, könyvjelző, leírók. A vanilla tartományszámokat lefordítja az új térkép tartományaira. |
| `tools/mapdata.py` | Vanilla térképadat olvasása (csak olvas). |
| `tools/render_region.py` | Címkézett tartománytérkép-kép egy régióról (tervezéshez). |
| `tools/test_launch.ps1` | Automatikus tesztindítás (lásd lent). |
| `tools/validate.py` | **Statikus ellenőrző**: játék nélkül végignézi a térkép- és történelemfájlokat a lenti motorszabályok szerint. Minden generálás után futtasd. |
| `tools/positions.py` | A kész térképből újraírja a `buildings.txt` és az `unitstacks.txt` pozícióit – játék nélkül is fut. |
| `tools/colormap.py` | A szárazföld színtextúrája: játék nélkül megfesti a terepből, `--vanilla` kapcsolóval a játék sajátjából vágja ki. |
| `tools/bisect_launch.ps1`, `tools/make_variants.py` | Automata felező teszt: egyszerűsített fájlváltozatokkal indítja a játékot, és táblát ír az eredményről. |
| `tools/data/names_245.py` | Ókori névlisták kultúránként (vezetők, tábornokok) → `common/names/ante_names.txt`. |
| `tutorial/tutorial.txt` | Üres `tutorial = { }` blokk (kötelező, lásd szabályok). Kézzel írt, nem generált. |
| `.gitattributes` | A `definition.csv` és az `adjacencies.csv` bájtra pontosan (CRLF sorvéggel) marad a repóban. |
| `common/national_focus/ante_generic_focus.txt` | Minimális alap fókuszfa (kötelező, lásd szabályok). |
| `common/defines/zz_ante_imperium.lua` | Kezdő-/végdátum felülírása. |
| `CLAUDE.md` | Rövid szabálylista a fejlesztéshez (AI asszisztensnek is). |
| `docs/design.md` | Terv és fázisok. |

Generált (ne kézzel szerkeszd, hanem a forrást + futtasd újra): `history/states`, `history/countries`,
`history/units`, `map/*`, `common/defines/zz_ante_regions.lua`, `common/country_tags`, `common/countries`,
`common/names`, `common/bookmarks`, `gfx/flags`,
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
