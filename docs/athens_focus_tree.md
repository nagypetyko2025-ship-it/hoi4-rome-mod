# Athén – a hellászi iskola (terv)

Peti kérése (2026-11-15):
- **Békésebb Athén**, amely bábokra és szövetségekre épít, nem hódításra.
- **Új, saját mechanika.** Ne megint az legyen, hogy két oldal között egy számot kell politikai erőért kordában
  tartani. Ez Róma, Karthágó és Perzsia mintája volt.
- **Modernebb, felvilágosultabb nemzet.**

A kiinduló helyzet (Kr. e. 509, 245 AUC):
- Kleiszthenész épp most adta a hatalmat a népnek. Athén kicsi, de ezüst, tenger és eszmék várnak rá.
- A térképen **47 görög nép él**: a görög anyaországban, az Égei-szigeteken, Itáliában és Szicíliában (Magna Graecia),
  valamint a Fekete-tenger partján.
- Athén befolyása így mindkét súlyponthoz eljut, Itáliába és a keleti, görög–perzsa világba is.

---

## 1. Új pénznem: az athéni ezüst (talentum)

Athén nem politikai erővel fizet a saját rendszereiért, hanem **ezüsttel**. Ez egy saját változó (`ATH_silver`), és a
döntés-kategória fejléce mindig mutatja.

**Havi bevétel:**
| Forrás | Talentum havonta |
|---|---|
| Alap (kikötői vámok, a város adója) | +2 |
| A laurioni ezüstbányák (fókusz) | +4 |
| Minden szövetséges a Déloszi Szövetségben (phorosz) | +1 |
| Minden adófizető báb | +2 |
| A „Baglyok” (athéni pénz, fókusz) | +10% minden bevételre |

**Mire költi:**
- a befolyásra (2. pont);
- a nagy építkezésekre (3. pont);
- néhány katonai és flottadöntésre.

A politikai erő megmarad a szokásos dolgokra (törvények, tanácsadók).

---

## 2. A proxenia-háló: befolyás a görög városokban

Minden görög városnak saját **athéni befolyás**-értéke van (0–100). Ezt az adott ország tárolja (`ATH_influence`),
és a térképen is látszik, mert a döntések kiemelik a célpontokat.

**Célzott döntések ezüstért** (bármelyik görög városra):
| Döntés | Ár | Befolyás | Feltétel |
|---|---|---|---|
| Proxenoszt küldünk (athéni barát a városban) | 5 talentum | +10 | – |
| A demokraták támogatása | 15 talentum | +25 | a város nem demokrácia |
| Gabona a Pontoszról | 10 talentum | +15 | a fekete-tengeri gabonaút fókusz |
| Flotta a védelmükre | 20 talentum | +20 | a város háborúban áll valakivel |

**Mindenkire ható dolgok:**
- **Panathénaia:** évente egyszer, 20 talentumért. Minden görög város befolyása +5.
- **Az aranykor:** a nagy építkezések passzívan, havonta emelik minden görög város befolyását.

**Csökkenés:**
- ha nem foglalkozol egy várossal, a befolyás havonta lassan csökken;
- gyorsabban csökken, ha a város más szövetségben van (például a Peloponnészoszi Szövetségben), vagy háborúban áll
  Athénnal.

**Küszöbök:**
- **50:** meghívható a **Déloszi Szövetségbe** (szövetség, nem háború). Onnantól havonta 1 talentumot fizet.
- **80, ha már szövetséges, választani kell:**
  - **Adófizető báb:** havi 2 talentum. Viszont a többi tag megijed, és a befolyásod náluk −5.
  - **Megbecsült szövetséges:** marad szabad. A befolyás 100-ig nőhet, és a város hajókat ad Athénnak (flotta-bónusz).
- **100, kis szomszédoknál** (Euboia, Naxosz, Aigina-szerű szigetek): **„Athéni polgárjog”** döntés. A város békésen
  beolvad Athénba, egy késői fókusz után.

**Ez a mechanika lényege:** Athén nem hódít, hanem behálózza a görög világot. Taraszban, Szürakúszaiban,
Büzantionban és Olbiában is lehetnek barátai. Ez Rómának és Perzsiának is komoly akadály, mert Athén
szövetségesei ellen nehezebb terjeszkedni.

---

## 3. Az aranykor: a nagy építkezések

Ezüstből épülő **nagy művek**. Mindegyik döntés hónapokig tart (az építés idejére aktív marad), és a végén
**végleges** bónuszt ad:

| Mű | Ár | Idő | Végleges hatás |
|---|---|---|---|
| A Parthenón | 60 talentum | 1 év | stabilitás, politikai erő |
| Dionüszosz színháza | 30 talentum | 6 hónap | a befolyás gyorsabban nő mindenhol |
| A hosszú falak | 40 talentum | 8 hónap | Athén és Pireusz védelme |
| A Pireusz kikötője | 35 talentum | 6 hónap | hajógyár, kereskedelem |
| Az Akadémia | 40 talentum | 8 hónap | kutatás |
| A Tarka Csarnok (Stoa Poikilé) | 25 talentum | 4 hónap | politikai erő, tanácsadók olcsóbbak |
| Az Ódeion | 25 talentum | 4 hónap | stabilitás, befolyás |

**Az aranykor szintjei:**
- **3 kész mű:** „Az aranykor hajnala” (kutatás +5%, havi befolyás minden görög városban).
- **6 kész mű:** „Periklész kora” (kutatás +10%, erősebb befolyás, olcsóbb célzott döntések).

---

## 4. A sztratégoszok választása (demokrácia és vezetés)

Nem egy mérő, hanem **évenkénti választás**. Athénban a tíz sztratégoszt minden évben a nép választja.

- Minden év elején esemény: **2–3 jelölt** közül választasz, és a győztes egy évre ad bónuszt (évi szellem).
- A jelöltek a kortól és a fókuszoktól függnek:

| Jelölt | Mikor | Egy évre ad |
|---|---|---|
| Themisztoklész | kezdettől, főleg a flotta fókusz után | flotta, hajógyártás |
| Arisztidész „az Igazságos” | a Déloszi Szövetség után | olcsóbb befolyás, több phorosz |
| Miltiadész / Kimón | ha Perzsia fenyeget | hadsereg, a szövetségesek védelme |
| Periklész | az aranykor fókuszai után | olcsóbb és gyorsabb nagy művek |
| Ephialtész | a demokrácia ág után | stabilitás, politikai erő |

- **Osztrakiszmosz:** döntés, legfeljebb tízévente egyszer. A népgyűlés száműzi az év sztratégoszát: a bónusz
  azonnal elveszik, de a stabilitás jelentősen nő, és a következő választás ingyen ad egy plusz jelöltet.
- A vezetés így folyamatosan változik, ahogy egy demokráciához illik. Nincs kiegyensúlyozandó szám.

---

## 5. Békés, de nem védtelen: a perzsa háborúk

Athén nem indít hódító háborúkat, de ha Perzsia megtámadja, védekező fókuszok nyílnak (csak ha Perzsia háborúban
áll Athénnal vagy egy szövetségesével):
- **Marathón:** nagy védekező bónusz a szárazföldön.
- **Themisztoklész flottája és Szalamisz:** tengeri csatabónusz.
- **A Hellén Szövetség:** ideiglenes szövetség Spártával és a többi görög várossal Perzsia ellen.

Háborús célt szinte sehol nem ad a fa. Egyetlen kivétel a Khalkisz elleni háború (Kr. e. 506). Ezt is lehet
választással elkerülni: háború Khalkisz ellen ↔ szövetség Khalkisszal.

---

## 6. A fókuszfa (kb. 45 fókusz, egy gyökér, öt ág)

**Gyökér:** Kleiszthenész reformjai (megnyitja az ezüstöt és a sztratégosz-választást).

1. **Demokrácia** (x 0–4):
   - a tíz phülé, az Ötszázak Tanácsa, osztrakiszmosz, a sztratégoszok;
   - az esküdtbíróságok, Ephialtész reformja;
   - **választás:**
     - **nyitott polgárjog:** több emberanyag, és a „polgárjog” döntés olcsóbb;
     - **Periklész polgárjogi törvénye:** stabilitás, és a nagy művek olcsóbbak.
   - Zárás: a demokrácia, amely tanít.
2. **Ezüst és tenger** (x 5–9):
   - Laurion ezüstje (+4 talentum havonta), a „Baglyok” (athéni pénz);
   - Pireusz, Themisztoklész flottája, a háromevezősor-sorok flottája;
   - hajóépítő műhelyek, az Égei-tenger kereskedelme.
3. **A Szövetség** (x 10–15):
   - proxenia (megnyitja a befolyás-döntéseket), segítség az ión városoknak;
   - a Déloszi Szövetség (létrejön a szövetség);
   - **választás:**
     - **a kincstár Déloszon marad:** a szövetségesek elégedettebbek, a befolyás lassabban csökken;
     - **a kincstárat Athénba visszük:** több ezüst, de a tagok kevésbé lelkesek.
   - Kleruchiák (telepesek a kis szigeteken);
   - a pontoszi gabonaút (a fekete-tengeri városok, gabonadöntés);
   - nyugati barátok (Magna Graecia: Thurioi alapítása, szövetség Szegesztával);
   - Kalliasz békéje (megnemtámadási szerződés Perzsiával).
4. **Az aranykor** (x 16–20):
   - a művészetek pártolása (megnyitja a nagy építkezéseket);
   - a tragédia (Aiszkhülosz, Szophoklész), a történetírás (Hérodotosz);
   - az orvoslás (Hippokratész), a filozófia (Szókratész), az Akadémia (Platón);
   - kutatási bónuszok és befolyás.
5. **Védelem** (x 21–24):
   - a hoplita phalanx, Marathón, Szalamisz, a Hellén Szövetség;
   - **választás:** Khalkisz ↔ szövetség Khalkisszal;
   - a hosszú falak védelme.
- **Zárás:** „Hellász iskolája”.

---

## 7. A cél: „Hellász iskolája” (döntés, győzelmi képernyővel)

**Feltételek:**
- **Periklész kora:** legalább 6 nagy mű elkészült;
- **a Déloszi Szövetség** legalább 12 tagot vagy adófizető bábot számlál, és ezek közül legalább egy Itáliában vagy
  Szicíliában, egy pedig a Fekete-tenger partján van;
- **Athén független**, és egyik nagyhatalom bábja sem.

**Jutalom:** nagy szellem (kutatás, befolyás, stabilitás), és győzelmi képernyő.
- Szöveget te adsz, ahogy a többi országnál.
- Kép: egy CC0 Akropolisz- vagy Parthenón-ábrázolás, például a Metropolitan Múzeum gyűjteményéből.

---

## 8. Mi kell hozzá technikailag (és mi új a modban)
- **Változók más országokon:** a befolyás az adott görög város változója, célzott döntésekkel (`targets`,
  `target_trigger`, `FROM`).
  A „Puns First!” már használt célzott döntést, de országra célzottat még nem.
- **Időben futó döntések** a nagy művekhez (`days_remove`, `remove_effect`). Ilyet még nem használtunk.
- **Szövetség és bábok békében:** `add_to_faction`, `puppet`, `set_autonomy`. Ezek már vannak.
- **Évenkénti választási esemény:** `on_actions` havi vagy évi ellenőrzéssel, a jelöltek feltételekkel.
- Az új rendszerek egy új `tools/athens_story.py` fájlba kerülnek, a fa pedig a `tools/national_trees.py`-ba.

## Nyitott kérdések Petihez
1. Spárta (amikor sorra kerül) **versenyezzen** a befolyásért a Peloponnészoszi Szövetséggel? Ez az athéni
   rendszerre épülne, és a peloponnészoszi háború a két befolyás-háló ütközése lenne.
2. Az AI-Athén is használja a befolyás-döntéseket, vagy csak a játékos?
3. A nagy műveknél maradjon az idő (hónapok), vagy legyen azonnali?

---

## Megvalósítva (55. kör)
Peti válaszai:
- Spárta barát vagy ellenség, ez egy választás.
- Az AI is ugyanazt csinálja, mint a játékos.
- A nagy művek időbe telnek.

**A rendszerek:** `tools/athens_story.py`. A fa a `tools/national_trees.py`-ban (41 fókusz).

**Döntés-kategóriák:**
- **The Athenian Silver:** ezüst és bevétel, osztrakiszmosz.
- **The Proxenia** (célzott döntések minden görög városra):
  - proxenosz küldése (5 talentum, +10), a demokraták támogatása (15 talentum, +25);
  - gabonakereskedelem a pontoszi városokkal (10 talentum, +15 befolyás, +3 ezüst), védőflotta (20 talentum, +20);
  - meghívás a Szövetségbe (50-nél), adófizető vagy megbecsült szövetséges (80-nál);
  - athéni polgárjog a kis szomszédoknak (100-nál);
  - Panathénaia (20 talentum, mindenhol +5).
- **The Great Works:** 7 nagy mű, 4–12 hónap építési idővel, ezüstért.
- **The School of Hellas:** a cél, győzelmi képernyővel.

**A spártai választás:**
- **Barátság Spártával:** megnemtámadási szerződés, és nő a befolyás a Peloponnészoszon.
- **Vetélytársság:** a spártai befolyás nullán marad, és nyílik a peloponnészoszi háború fókusz.

**A sztratégosz-választás:** minden évben esemény jön, 2–5 jelölttel (a fókuszoktól függ).
