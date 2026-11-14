# Karthágó fókuszfája – terv (2026-11-14)

Állapot (30. kör): **a fa kész – 60 fókusz, két út a gyökérnél, kizáró párok minden ágban** (`tools/national_trees.py`,
CARTHAGE szakasz; feltételek a `TUNE`-ban). Még hátra van: a két mérő (a tanács gyanúja / a zsoldosok bére), a „Res
Punica” döntések (zsoldosfogadás) és az események (`events/CAR_events.txt`) – a következő körben.

Időkeret: Kr. e. 509 (245 AUC, az első római–karthágói szerződés éve) → Kr. e. 264 (490 AUC, Messana, az első pun
háború – a második kezdés). Karthágó Róma fő ellenfele: a két fa a végén ugyanoda fut (Szicília).

Kiinduló helyzet a térképen: 11 állam, 5 hadosztály, a legerősebb flotta; szomszédok Afrikában: Libyans (LIB),
Massylii (MSY), Masaesyli (MSS), Mauri, Gaetuli, Garamantes; tengeren túl: Gadir (GDR), Elymians (ELY), Szardínia
(SAR), Szürakuszai (SYR), Akragasz, Gela, Tartessos (TTS), Küréné (KYR).

## A két út (gyökér, kizárják egymást)

| | **A Mago-ház** (dinasztia) | **A Száznégy Bíró tanácsa** (oligarchia) |
|---|---|---|
| Történet | Mago fiai és unokái hadvezérként és „királyként” uralkodnak (Kr. e. 550–370) | Kr. e. 4. század eleje: a tanács bíróság elé állítja a hadvezéreket, a kereskedő-családok uralma |
| Erőssége | szárazföldi hadsereg, hódítás, gyors döntések | kereskedelem, flotta, gyarmatok, gazdagság |
| Gyengesége | a tanács gyanakszik: puccsveszély | lassú háborúk, a hadvezérek keresztre feszítése |
| Mérő | **A tanács gyanúja** (0–100): győzelmek és hódítások növelik, ajándékok, áldozatok csökkentik; 80 felett összeesküvés, 100-nál a tanács átveszi a hatalmat (az oligarchia útjára vált) | **A zsoldosok bére** (0–100): háború és zsoldosfogadás növeli, ezüst és béke csökkenti; 80 felett zsoldoslázadás (Kr. e. 240 előképe) |

Mindkét mérő **két irányba mozog** (döntés és esemény is növeli, csökkenti) – Róma tanulsága: egyirányú mérőre nem
lehet fókuszfeltételt építeni.

## Ágak

### 1. Állam és tanács (bal oldal, mindkét út, más tartalommal)
- Dinasztia: Mago reformjai → a „király” címe → a hadvezér-családok → Hamilkar öröksége → katonai monarchia
- Oligarchia: a suffetek → a Száznégyek bírósága → a Nagy Hanno pártja (földbirtokosok) ↔ a tengeri párt (kizáró pár)
  → a nép gyűlése → „Karthágó, a kereskedők köztársasága”

### 2. Tanit és Baal Hammon – vallás
- Melqart tizede Türoszba ↔ Karthágó saját istenei (kizáró pár: kapcsolat az anyavárossal vagy függetlenség)
- A tophet (válságban áldozat – csak esemény, nagy stabilitás/háborús támogatottság, ára van)
- Démétér és Koré kultusza (Kr. e. 396, a szicíliai pestis után: görög istenek befogadása)

### 3. A tenger úrnője – flotta
- Kóthón (kész) → hadiflotta (kész) → **Mare Clausum** (a szerződések lezárják a tengert idegen hajók elől)
- → quinqueremék (technológiával együtt) → tengeri uralom a Tirrén-tengeren → a flotta mint diplomácia
- Kizáró pár: **ramming tactics** (gyors, könnyű hajók) ↔ **tengerészgyalogság** (nehéz hajók, partraszállás)

### 4. Kereskedelem és gyarmatok
- Bíborfestés és kézművesség → Gadir és Ebusus (Ibiza) → Málta, Pantelleria
- **Hanno útja** (kész) – Atlanti-parti gyarmatvárosok (kutatás + bónusz); **Himilkón útja** – az ón útja Britanniába
- Tartessos ezüstje (kész: „ibériai ezüst”) → ibériai bányák → Új-Karthágó előképe
- Szaharai karavánok a garamantészekkel (arany, rabszolgák) – döntés
- Kizáró pár: **a Phoenician League** (Gadir, Ebusus szövetségesek) ↔ **közvetlen uralom** (annektálás)

### 5. Afrika – a hátország
- Adófizetés a líbiaiaknak (kezdőhelyzet: Karthágó fizet!) → **adófizetés vége** (háborús cél LIB ellen)
- → Líbiai földek: líbiai sorozott gyalogság (manpower), libüphoinikai városok
- Numidák: **szövetség a massziliaiakkal** ↔ **hódítás** (MSY, MSS) – kizáró pár
- → A Philainosz-oltárok: határ Kürénével (diplomáciai határvonal vagy háború KYR ellen)

### 6. Szicília (Róma fájának másik oldala)
- Elümoszi szövetség (Motüé, Panormosz) → **Himera, Kr. e. 480** – esemény: Gelón legyőzi Hamilkart; választás:
  bosszú ↔ béke és jóvátétel
- → Szelinusz és Akragasz (Kr. e. 409–406, Hannibal Mago) → Dionüsziosz háborúi (Motüé ostroma, Kr. e. 397)
- → **Agathoklész partraszállása** (Kr. e. 310, esemény: ellenség Afrikában) → Pürrhosz (Kr. e. 278)
- → **Messana** (Kr. e. 264) – kapcsolódás Róma „Towards Sicily” fókuszához
- Háborús célok csak elérhető célpontra (`reach` – Karthágónál tengeren át is: flotta + kikötő), `gone()` szövetségesre is.

### 7. A sereg
- Szent Csapat (kész) → líbiai gyalogság → **zsoldosok** (döntések: ibériai, gall, baleári parittyások, numida lovasság)
- → harci elefántok (Pürrhosz után; technológia + fókusz) → Xanthipposz reformja (Kr. e. 255 előképe)
- Kizáró pár: **zsoldoshadsereg** (gyors, drága, a bér-mérőt növeli) ↔ **polgárhadsereg** (lassú, olcsó, kevesebb manpower)

### 8. Róma (diplomácia, a végén)
- Az 1. szerződés (Kr. e. 509, kész fókusz) → a 2. szerződés (Kr. e. 348) → Pürrhosz ellen Rómával (Kr. e. 279)
- Mindháromnál választás: betartani ↔ megszegni (háborús támogatottság, Róma véleménye)
- → „Messana kérdése” → első pun háború (a 264-es kezdés)

## Döntések (saját kategória: „Res Punica”)
- Zsoldosok fogadása (típusonként: hadosztályt ad, a bér-mérőt növeli)
- Melqart tizede Türoszba; ajándék a tanácsnak (gyanú csökken); ezüstkonvoj Ibériából
- Karavánexpedíció a garamantészekhez; líbiai sorozás (manpower, líbiai elégedetlenség)
- Tophet-áldozat (csak válságban: kapitulációs veszély)

## Események (`events/CAR_events.txt`)
Malkhosz (bukott hadvezér), Himera és Gelón, Hanno és Himilkón visszatérése, a Száznégyek bírósága (hadvezér a
bíróság előtt), a szicíliai pestis és a líbiai lázadás (Kr. e. 396), Nagy Hanno puccskísérlete (Kr. e. 350 körül),
Agathoklész Afrikában, Bomilkar puccsa (Kr. e. 308), Pürrhosz Szicíliában, a mamertinusok hívása (Kr. e. 264).

## Szabályok a kidolgozáshoz (Róma tanulságai)
- Minden háborús cél fókusza csak elérhető célpontra vehető fel (szomszéd, vagy tengeren át: flotta + kikötő).
- Nincs olyan fókuszfeltétel, amely csak egy irányba mozgó számra épül.
- A kizáró párok mindkét fele továbbvisz.
- Esemény nem lehet egy fókusz egyetlen kulcsa; ha az esemény elmarad, a fókusz maga indítja el.
- Új országok hadat csak szomszédként üzennek (Porsenna-hiba).
- Ikonok: egyelőre az alapjáték fókuszikonjai; saját ókori fókuszikonok később.

## Becsült méret
~55–65 fókusz (Róma: 93 a két úttal), 2 mérő, ~10 döntés, ~12 esemény, saját nemzeti szellemek.
