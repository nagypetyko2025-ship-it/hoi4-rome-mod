# Róma fókuszfája – terv (előkészítve 2026-11-13)

Állapot (19. kör, 2026-11-14): **a fa kész, mindkét úttal; mögötte két mérő, 12 esemény és 8 döntés**
(`common/national_focus/ROM_focus.txt` a `tools/national_trees.py`-ból, a rendszerek a `tools/rome_story.py`-ból –
részletek lent, „A két út rendszerei”). Hiányzik még: saját fókuszikonok, a manipulusos légió saját egységtípusai
(most szellem adja a bónuszt), Coriolanus- és Allia-esemény.

Időkeret: Kr. e. 509 (245 AUC, a köztársaság kezdete) → Kr. e. 264 (490 AUC, az első pun háború, a második kezdés).
A fa a valós történelmet követi, de minden ágban van mozgástér a játékosnak.

## Ágak

### 1. Res Publica – belpolitika (bal oldal)
- **Regifugium** (gyökér, kész) – a királyok elűzése.
- **Consulok és szenátus** (kész) → **A plebs kivonulása** (kész, Kr. e. 494) → **Néptribunusok** (kész)
- → **Decemvirek és a Tizenkét táblás törvény** (Kr. e. 451) → **Lex Canuleia** (patríciusok és plebejusok házassága)
- → **Licinius–Sextius-törvények** (Kr. e. 367, plebejus consul) → **Censori hivatal**, **Lex Hortensia** (Kr. e. 287)
- Kimenet: állandó nemzeti szellemek (stabilitás, politikai erő), a „patríciusok és plebejusok rendi harca”
  szellem fokozatos megszüntetése.

### 2. Az istenek Rómája – vallás (közép-bal)
- **Jupiter temploma a Capitoliumon** (kész) → **Sibylla-könyvek** (kész, +1 kutatóhely)
- → **Pontifex maximus**, **Vesta-szüzek**, **Ludi Romani** (játékok: háborús támogatottság)
- → **Evocatio** (az ellenséges város isteneinek „áthívása” – Veii ostrománál; háborús bónusz ostromra)

### 3. A légió születése – hadsereg (közép)
- **Osztályok és centuriák** (kész, servius-i hoplita falanx)
- → **Zsold (stipendium)** a veii háború alatt → **Camillus reformjai** → **Manipulusos légió**
  (új egységsablon: hastati / principes / triarii – ehhez külön egységtípusok kellenek)
- → **Római utak**: **Via Appia** (Kr. e. 312) és **Aqua Appia** – infrastruktúra, ellátás
- → **Coloniák** (latin gyarmatvárosok: manpower és magok az elfoglalt államokra)

### 4. Latium és Etrúria – külpolitika, háborúk (jobb oldal)
- **Horatius a hídon** (kész, Porsenna) → **Regillus-tavi csata** (kész, háborús cél a Latin Liga ellen)
- → **Foedus Cassianum** (kész, Kr. e. 493) – később: szövetség a latinokkal (frakció)
- → **Az aequusok és volscusok ellen** (kész, háborús célok) → **Coriolanus**
- → **Veii ostroma** (Kr. e. 406–396, Camillus) → **Etrúria déli városai** (Caere, Tarquinii, Falerii)

### 5. A gall vész és újjászületés (külön ág, eseményekkel)
- **Allia, Kr. e. 390** – esemény: Brennus gall serege (ha a gallok erősek) → **„Vae victis!”**
- → **A Servius-fal** (Kr. e. 378, erődök Rómában) → **Camillus, a második alapító**

### 6. Itália ura (alul, hosszú távon)
- **Latin háború** (Kr. e. 340–338) → **Samnis háborúk** (Caudium, Sentinum) → **Tarentum és Pyrrhus**
- → **Itália egyesítése** → **Szicília felé** – kapcsolódás a 264-es kezdéshez (Karthágó)

## Megjegyzések a kidolgozáshoz
- A kultúra-szellem („Roman Virtus: We Never Give Up!”) már él: +40% kapitulációs határ, magas besorozás.
- Háborús célok csak létező, nem háborúzó célpontra (`wargoal()` segédfüggvény a content.py-ban).
- Ikonok egyelőre az alapjáték általános fókuszikonjai; saját, ókori fókuszikonokat később rajzolunk.
- Események (Lucretia, Horatius, Coriolanus, Allia) a fókuszokhoz kötve – külön `events/ROM_events.txt`.

## A két út rendszerei (19. kör, `tools/rome_story.py`)

A fa dönti el, **mivé** lesz Róma; a rendszerek teszik egyenetlenné az utat. Mindkét úton egy 0–100-as mérő áll a
középpontban, amelyet a játékos a saját döntéseivel (fókuszok, események, döntések), és amelyet a világ is mozgat
(háború, vereség, idő). A mérő egy dinamikus nemzeti szellemet hajt: a hatása a mérő értékével folyamatosan nő vagy
csökken, a címében ott a szám („Struggle of the Orders (52)”). A „Res Romana” döntéskategória leírása mindig az
aktuális állást mutatja.

### A köztársaság: a rendi harc (`ROM_discord`)
- A **Regifugium** 40-ről indítja. Háborúban hetente **+0,35** (a katonák földje parlagon, eladósodnak), békében
  **−0,12**. Az Atyák uralma hetente +0,12, a néptribunusok −0,12, a Forumon kiontott vér +0,06.
- Hatás 0-nál: +10% stabilitás, +0,2 politikai erő/nap; 40-nél nagyjából semleges; 100-nál −20% stabilitás,
  −0,3 PP/nap, −10% háborús támogatottság, −20% besorozható népesség.
- **80-nál a plebs kivonul** (20-as esemény, legfeljebb 540 naponként): engedsz (−35, de −100 PP), kivárod (éhség,
  −15), vagy a légiókkal hozatod vissza (csak az Atyák uralma vagy diktátor alatt: −45, de vér a Forumon).
- A „Plebs szerveződik” fókusz csak a kivonulás után vagy 55-ös viszálynál érhető el, a **Lex Hortensia** csak 30
  alatt – a végén eltűnik a mérő, és jön a Concordia Ordinum. A plebs felé tett lépések (tribunusok, Tizenkét tábla,
  Lex Canuleia, Licinius–Sextius, gyarmatok, zsold) csökkentik, a patrícius lépések (Atyák uralma, nobilitas)
  növelik a viszályt, cserébe több politikai erőt adnak.
- **Események:** a száműzött Tarquiniusok földje (a népnek vagy a kincstárnak); **Porsenna** (25 nap + 150–210 nap
  múlva: harc – Clusium valóban hadat üzen, bábállam-céllal –, vagy a feltételek elfogadása 540 napos szellemmel);
  **évenkénti consulválasztás** (patrícius, népszerű vagy katonai tribunusok – évre szóló szellem); Spurius Cassius
  földtörvénye (a Foedus Cassianum után egy évvel); a diktátor letegye-e a fasces-t.
- **Döntések:** adósságelengedés, gabona Szicíliából, földosztás (az Ager Publicus fókusz és 5 állam után), a nép
  fegyverbe hívása (háborúban: +3000 fő, de +8 viszály), diktátor kinevezése (veszélyben: 180 nap, utána 30-as esemény).
- A katonai ág is a helyzethez kötött: **Horatius a hídon** csak Porsenna lépése után, a **Regillus-tavi csata**
  után a Latin Liga **tényleg hadat üzen** (a Dioszkuroszok fél évig Róma oldalán), a Foedus Cassianum csak békében köthető.

### A királyság: a nép gyűlöli a királyt (`ROM_hatred`)
- **A király marad** 70-ről indítja. Hatás 70-nél: −21% stabilitás, −0,28 PP/nap, −14% háborús támogatottság, −21%
  besorozás, −28% népességnövekedés, −21% építési sebesség – vagyis a királyság erős kezdés (több PP, király-szellemek),
  de súlyos teherrel, amíg a gyűlöletet le nem dolgozod.
- Hetente: zsarnokság +0,25, a nép királya −0,12, „meghallgatja a népet” −0,1, vesztésre álló háború +0,6.
- **50 fölött összeesküvések** (40-es esemény, heti 4%, a Forumon kiontott vér után kétszer): kivégzés, száműzés vagy
  kegyelem – a kegyelmet 30% eséllyel tőrdöfés követi (41-es esemény).
- **Brutus, a bolond** (60 nap): ha udvarban marad, 80-as gyűlöletnél leveti az álarcot (43-as esemény). Megölni +10
  gyűlölet. **Lucretia** (200 nap): a király fia felett nincs törvény (+18), száműzés (−12) vagy a nép ítélete (−25, −150 PP).
- **100-nál Róma fellázad** (45-ös esemény). Ha Rómának már legalább 3 állama van: polgárháború. Előtte – Róma
  kezdetben egyetlen állam, és ott a játék nem tud polgárháborút indítani (játékban kipróbálva) – **forradalom**: a király
  elmenekül, a Regifugium mégis megtörténik, a viszály 55-ről indul, a királyi fókuszok örökre lezárulnak
  (`ROM_revolution` jelző, a national_trees.py automatikusan teszi rá minden csak a királyságon át elérhető fókuszra).
- **A gyűlölt király ága** minden lépése csökkenti a mérőt (amnesztia −10, gabona Kümétől −8, telepesek vissza −12,
  aztán választás: a lázadások leverése −20 azonnal, de vér a Forumon, vagy a nép meghallgatása −15 és hetente
  tovább), a végén a **Hű Róma** csak 30 alatt vehető fel – ekkor a mérő eltűnik, jön a „Hű alattvalók” szellem.
  A hódítások (Gabii, a tizenkét város, Lucumo, Regnum) is csökkentik: a győzelem kibékít.
- **Döntések:** a király játékai (−8), kémek minden házban (egy évig nincs összeesküvés, de terror és +4), robotmunka
  (azonnali gyár, de +12).

### Egyensúly – amit a játékban mértem (2026-11-14, Sim gépén, 1.19.5)
- A köztársaság a 40-es kezdésnél nagyjából semleges; egy hosszú háború (egy év ≈ +18) a 80-as kivonulás felé
  sodorja, ha közben nem enged. A királyság 70-nél érezhetően gyenge, de a gyűlölt király ágával és két-három jó
  eseménydöntéssel 1–2 év alatt 30 alá vihető.
- Kipróbálva: a mérők hetente frissülnek, a szellem értékei követik őket; az 1, 2, 10, 42, 43, 44, 45-ös esemény
  lefut; a forradalom után Róma demokratikus, a Regifugium kész, a viszály 55-ről indul. Az error.log-ban nincs hiba
  a saját fájlokból.

### Átnézés, 21. kör (Peti 20. köre után)
- Géppel ellenőrizve: nincs átfedés, az előfeltételek feljebb vannak, a kizárások kölcsönösek; mindkét ág eléri a 30
  itáliai népet. A köztársaság szerződéses fókuszai (Civitas sine Suffragio, a negyvenéves fegyverszünetek, Capua
  önátadása, az apuliai szövetségesek) és a királyság Latin Ligája most `submit()`-ot használnak: szerződés, ha
  köthető, különben háborús cél – eddig ilyenkor semmit sem adtak.
- Egyensúly, nyitott kérdés Petinek: a szerződések olcsók (pl. Clusium + Volaterrae + Arretium, 6 állam 100 PP-ért), és
  a bábállamok beleszámítanak az Italia 20 államába – a köztársaság így könnyebben ér célba, mint a király.
