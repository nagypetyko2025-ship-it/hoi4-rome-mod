# Perzsia – a szatrapiák birodalma (40. kör)

Peti kérése: Perzsia élete ne legyen túl könnyű, a mérete legyen kisebb hátrány. Néhány ország (Anatólia, Egyiptom stb.)
ki akar válni, ezt döntésekkel kell kezelnie. Ha nem figyel és a feszültség túl magasra megy, az ország szétesik egy 3-4
oldalú polgárháborúba, és néhány ország függetlenedik. Perzsiának is legyen egy elérendő célja, mint Rómának vagy
Karthágónak.

## A szatrapiák lázongása (`tools/persia_story.py`)

Öt nyugtalan szatrapia, mindegyiknek saját mérője van (0–100). Az elszakadó országok (`tools/data/world_509bc.py`,
`RELEASABLE`) a játék elején nem birtokolnak földet, de magterületük van a régióikban:

| Szatrapia | Ország | Régiók | Kezdő érték |
|---|---|---|---|
| Egyiptom | KMT Egypt | Mudraya, Patoris | 30 |
| Babilon | BBL Babylon | Babirush, Athura | 25 |
| Iónia | ION Ionian League | Yauna, Lesbos, Chios, Samos, Karka | 40 (tíz évre a nagy felkeléstől) |
| Lüdia és Phrügia | LYD Lydia | Sparda, Phrygia, Daskyleion, Bithynia, Pamphylia, Katpatuka | 15 |
| Baktria | BKT Bactria | Bakhtrish, Suguda, Margush, Uvarazmish | 20 |

### Heti emelkedés
- **Alapból +0,18** (kb. 9 pont évente): ez a birodalom mérete.
- **Gyorsítja:**
  - háború: +0,12;
  - 50% alatti stabilitás: +0,12;
  - 100-nál több állam: +0,08.
- **Lassítják a fókuszok** (minden szatrapiára):
  - szatrapia-rendszer: −0,03;
  - a király szemei: −0,05;
  - királyi út: −0,02;
  - a király törvénye: −0,03;
  - minden nép istenei: −0,04;
  - a nagy cél: −0,10.
  - Ellenkező irányba hat a „szatrapák saját hadserege”: +0,03.
- **Regionális fókuszok** (csak az adott szatrapiára):
  - fáraó: Egyiptom −0,10;
  - Marduk keze: Babilon −0,10, Marduk szobrának beolvasztása viszont +0,08;
  - demokrácia az ión városoknak: Iónia −0,10, zsarnokok kinevezése viszont +0,05;
  - szardeiszi nemesek: Lüdia −0,08;
  - baktriai herceg: Baktria −0,10.

### Nemzeti szellem
A „Unrest of the Satrapies” szellem az átlagos lázongást követi:
- 0-nál +3% stabilitás és +0,05 politikai erő;
- 100-nál −17% stabilitás és −0,25 politikai erő.

### Döntések („The Satrapies” kategória)
Szatrapiánként három döntés:

| Döntés | Ár | Hatás | Újra elérhető |
|---|---|---|---|
| A király szeme | 50 PP | −15 | 90 nap múlva |
| Helyőrség | 25 PP és 3000 fő | −20 | 180 nap múlva |
| Az istenek és nemesek tisztelete | 100 PP | −30 | 365 nap múlva |

Az AI 45, 60, illetve 75 fölött használja őket.

### Küszöbök
- **60:** egy esemény figyelmeztet, választható megoldásokkal (sereg küldése, arany a nemeseknek, vagy a szatrapára bízza).
- **100:** a szatrapia fellázad.
  - Felszabadul a magterületein, és saját sereget kap (4–6 hadosztály, felszerelés, emberanyag).
  - Hadat üzen Perzsiának.
  - Perzsia leverheti, vagy elengedheti: fehér béke, de a többi szatrapia lázongása +10.
- **Ha egyszerre három szatrapia áll 70 fölött, a birodalom szétesik:**
  - minden 70 fölötti szatrapia fellázad;
  - Médiában és északon (Mada, Raga, Armina, Varkana, Parthava) egy trónkövetelő polgárháborút indít („Median Pretender”, saját zászló: szárnyas napkorong);
  - így négy- vagy többoldalú háború lesz belőle;
  - tíz évig nem történhet meg újra.

## A cél: „King of the Four Corners of the World” (döntés)
- **Feltételek:**
  - egész Hellász a király vagy alattvalói kezén van: Athén, Spárta, Théba, Korinthosz, Argosz, Euboia, Thesszália és Makedónia, összesen 11 állam;
  - Egyiptom és Babilon még a királyé.
- **Jutalom:**
  - nagy szellem (+15% stabilitás, +0,30 PP, +10% háborús támogatottság, +10% gyár, besorozás);
  - minden lázongás −40, és tartósan 0,10-zel lassabban nő;
  - magterület a görög államokon.
- A döntés a térképen kiemeli a szükséges államokat.

## A fókuszfa (55 fókusz, egy gyökér, nyolc ág)
1. **A szatrapiák** (x 0–4):
   - szatrapia-rendszer;
   - választás: a király szemei ↔ a szatrapák saját hadserege;
   - fix adó, a király törvénye;
   - választás: a hét ház ↔ királyi vérből való szatrapák.
2. **A kincstár** (x 7–11): dareikosz, királyi út, Perszepolisz, kanátok, paradicsomkertek, Szúsza palotája, a király kincstárai.
3. **Az istenek** (x 12–14):
   - Ahura Mazda;
   - választás: igazság a hazugság ellen ↔ minden nép istenei;
   - Behisztun (+1 kutatási hely), a mágusok.
4. **A sereg** (x 16–18):
   - Halhatatlanok;
   - választás: perzsa lovasság ↔ minden nép hadereje;
   - királyi helyőrségek, kaszás harci szekerek, görög zsoldosok, Xerxész serege.
5. **A Nyugat és Hellász** (x 21–25):
   - szardeiszi nemesek, föníciai flotta;
   - választás: zsarnokok ↔ demokrácia az ión városoknak;
   - Thrákia és Makedónia;
   - az Iszteren túl (szkíták), föld és víz;
   - választás: Datisz és Artaphernész ↔ híd a Hellészpontoszon;
   - föld és víz egész Hellásztól.
6. **Egyiptom** (x 28–31): fáraó, Hibisz temploma, a Nílus-csatorna, a kataraktákon túl (Kús), Kürené és Barka.
7. **Babilon** (x 33–35):
   - Babilon királya;
   - választás: Marduk keze ↔ Marduk szobrának beolvasztása;
   - Babilon csatornái.
8. **A felső szatrapiák** (x 37–39): baktriai herceg, Hindus aranya, Kürosz megbosszulása (masszageták), a felső szatrapiák.
9. **Zárás:** a népek királya (Xerxész serege, a hét ház / királyi vér és a kincstár után).
10. **A szatrapiák rendezése** (41. kör, a fa legalja, a népek királya után). Szatrapiánként egy kizáró pár:
    - **integrálás:** csak ha a lázongás 20 alatt van, és a szatrapia nem szakadt el. A lázongás végleg megszűnik,
      soha többé nem lázadhat fel, az elszakadó ország magterületei törlődnek;
    - **vagy szabadon engedés** hűséges, legalacsonyabb autonómiájú bábként (integrated puppet). Ebben az esetben sincs
      többé lázongás, és a nagy célhoz a báb területe is a királyénak számít.

### A cél szigorúbb (45. kör)
Peti: a cél túl könnyű volt. Most minden kell, amit Perzsia a fókuszaival megszerezhet:
- Hellász (11 állam);
- a föníciai városok: Szidón, Türosz, Arwad;
- a sztyeppe: a szkíták és a masszageták;
- Afrika Egyiptomon túl: Kús, a Marmaridák (a Kürené-fókusz most háborús célt is ad ellenük) és Kürené;
- Egyiptom és Babilon megtartva.

Összesen 52 állam, a döntés mindet fehér körvonallal kiemeli. A király vagy az alattvalói kezében kell lenniük.

### Agresszívabb lázongás (46. kör)
Peti szerint a szatrapiák szinte sosem lázadtak fel, ezért a lázongás gyorsabban nő:
- **alap:** heti 0,40 (évente kb. 21 pont, eddig 0,18);
- **gyorsítók:** háború +0,25, 50% alatti stabilitás +0,25, 80-nál több állam +0,10, 100-nál több további +0,15;
- **fókuszok:** minden lassító és gyorsító fókusz hatása a duplája lett (pl. a király szemei −0,10, a fáraó −0,20),
  így egy jól vezetett birodalom kézben tudja tartani a szatrapiákat;
- **figyelmeztető esemény:** 60 fölött hetente 10% eséllyel jön (eddig 6%).

### Igazi kihívás (47. kör)
Peti szerint Perzsia több mint félmillió fős emberanyaggal indul, ezért a mérete ellene kell, hogy dolgozzon. Ha egy szatrapiára nem figyel, legfeljebb két hónapon belül lázadjon fel.

- **Kezdőértékek:** minden szatrapia 40-ről indul, Iónia 50-ről (ő lázad fel elsőként).
- **Heti emelkedés:** a Perzsia által ellenőrzött államok száma × 0,09. A kezdeti 81 államnál ez heti 7,3, ugyanannyi minden szatrapiánál.
  - Háború +2,5, 50% alatti stabilitás +2,5.
  - A fókuszok ennek egy részét elveszik (pl. a király szemei −1,0, a fáraó −2,0), de a heti emelkedés sosem megy 0,5 alá.
  - Figyelem nélkül Iónia kb. 7 hét alatt, a többi kb. 8 hét alatt lázad fel.
- **Döntések:**

| Döntés | Ár | Hatás | Újra elérhető |
|---|---|---|---|
| A király szeme | 25 PP | −25 | 30 nap múlva |
| Helyőrség | 10 PP és 15 000 fő | −40 | 45 nap múlva |
| Az istenek és nemesek tisztelete | 75 PP | −60 | 120 nap múlva |

  A félmilliós emberanyag így ára lesz a nyugalomnak.
- **Figyelmeztetés:** 60 fölött hetente 30% eséllyel jön, legfeljebb 120 naponként.
- **A felkelők** valódi sereggel kelnek fel:
  - hadosztályok: Egyiptom 16, Babilon 14, Lüdia 12, Baktria 12, Iónia 10;
  - egy évig tartó „Fighting for Freedom” szellem: +15% támadás és védekezés;
  - Perzsia hadosztályonként 6000 főt veszít, mert a szatrapia hadereje átáll.
- **A levert felkelés végleges:** ha a felkelő ország megszűnik, a szatrapia soha többé nem lázad fel. A magterületei törlődnek, és az integráló fókusza elérhető.

### Könnyítés az AI-nak (48. kör)
Ha Perzsiát az AI irányítja, a szatrapiák lázongása csak 30%-os ütemben nő: a kezdetén heti kb. 2,2, nem 7,3. Így az AI
is kezelni tudja őket a döntéseivel. A játékos Perzsiája marad a kemény tempónál.
