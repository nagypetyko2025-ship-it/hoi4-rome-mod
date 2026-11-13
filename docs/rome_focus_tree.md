# Róma fókuszfája – terv (előkészítve 2026-11-13)

Állapot (13. kör): **a fa kész, 38 fókusz, mind a hat ág** (`common/national_focus/ROM_focus.txt`, generálja a
`tools/national_trees.py`). Hiányzik még: saját fókuszikonok, események (Lucretia, Horatius, Coriolanus, Allia),
a manipulusos légió saját egységtípusai (most szellem adja a bónuszt).

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
