# Kaj je preverjeno

Izdaja 2026-09-12-v4.2. Preverjanje je potekalo na macOS v začasnih mapah z umetnimi podatki. Uporabnikova navodila, AIOS, službeni dokumenti in rutine niso bili spremenjeni.

## Izvedeno lokalno

**53 avtomatskih preizkusov: uspešno.**

- 16 preizkusov osnovnega popisa ter branja DOCX/PDF: izključitve, poškodovane datoteke, obseg PDF-strani, vizualna opozorila in izvor.
- 17 preizkusov vsebinskega indeksa: priprava, potrjevanje, iskanje, branje, odtisi, XLSX-celice in formule, dnevna omejitev, nadaljevanje dolgega dokumenta, izključitve ter lokalni zaklep.
- 15 preizkusov prenosa paketa: popolna razširitev, ponovitev brez sprememb, nevarne poti, kontrolni odtisi, konflikti, odobrena nadgradnja znane izdaje z varnostno kopijo in pogodba za samodejno ustvarjanje rutine.
- 5 preizkusov osebne namestitve: potrebna odobritev, ohranitev globalnih navodil, ponovitev, varna migracija znane kopije in zavrnitev prilagojenega skilla.

Drugi umetni uporabnik na drugi lokalni poti ponovno uporabi isti skupni paket brez novega izvlečka ali povzetka. To je simulacija sinhronizacije s kopiranjem podatkov, ne preizkus dejanskega Nextclouda.

Po spremembi, izbrisu, izključitvi ali nedostopnosti izvirnika se stari zadetek ne vrne. Delni ali poškodovani paketi se ne uporabijo. Dolg dokument do dokončanja vseh kosov ni iskalni zadetek.

Uporabljeni različici knjižnic: pypdf 6.10.0 in openpyxl 3.1.5. Namestitveni seznam je pripet na ti preizkušeni različici.

## Popravki po Windows preverjanju

Prvi CI-preizkus je na macOS uspel, na Windows pa odkril odprte SQLite povezave, neprepoznan prazen odgovor PDF-pretvornika ter neprenosljive predpostavke testov o kodiranju in poteh. V4.1 izrecno zapira SQLite, zavrne prazen odgovor pretvornika in uporablja UTF-8 izhod; testi uporabljajo UTF-8 ter prenosljive relativne poti. Dodan je regresijski preizkus praznega PDF-odgovora. Različica postopka priprave je povečana, zato paketi iz v4 niso tiho uporabljeni kot na novo preverjeni.

## Samodejna postavitev rutine

V4.2 zamenja običajno ročno izpolnjevanje obrazca z navodilom, da Claude po potrditvi v isti Desktop Code seji prek uradne zmožnosti sam preveri obstoječe rutine ter ustvari ali posodobi `osvezi-dokumente`. Regresijski preizkus preveri ime, dnevni urnik ob 9.00, minimalno različico aplikacije in prepoved neposrednega pisanja internih nastavitev. To preverja pogodbo paketa, ne dejanske namestitve ali zagona na računalniku zaposlenega.

## Pravi Claudeov preizkus

**En resničen modelni povzetek umetnega zapisnika: uspešno.** Claude CLI je prek obstoječega prijavljenega računa brez orodij prejel samo umetni primer. Vrnil je strukturiran slovenski povzetek; pripomoček ga je sprejel, objavil lokalni paket in našel dokument z vsebinskim iskanjem.

Povzetek je pravilno ohranil datum 20. oktobra, nalogo koordinatorja, rok petek, znesek 120 EUR ter dejstvo, da naročilo še ni potrjeno. To je pregled enega majhnega primera, ne ocena kakovosti na celotni zbirki. Prvi poskus v omejenem okolju ni videl prijave; po preverjanju dostopa do obstoječe prijave je bil preizkus uspešen. Nova prijava ali API-ključ nista bila ustvarjena.

Ta preizkus ne dokazuje samodejne izbire osebnega skilla, nalaganja globalnih navodil ali načrtovanega zagona v Desktopu.

## Ponovitev

```sh
python -m unittest discover -s preverjanje -v
```

Testno okolje potrebuje odvisnosti iz dokumenti/requirements.txt ter reportlab in Pillow. PDF-bralnik preizkusi tudi nadomestno pot s pypdf; preizkus argumentov pdftotext je izoliran. Testi ne kličejo modela.

Ločen opt-in preizkus `python preverjanje/preizkus_claude.py --run` uporablja obstoječo prijavo v Claude CLI in lahko porabi naročniško kvoto. Uporabi samo umetni dokument in ne spreminja osebnih nastavitev. Brez zastavice se ne izvede. Ne zaganjaj ga rutinsko ali brez potrebe ponavljaj pri napakah.

Avtomatsko preverjanje na Windows in macOS je določeno v [GitHub Actions](https://github.com/LukaLeskovsek/claude-work-starter/actions). Rezultat konkretne izdaje preveri pri ustreznem commitu; sama definicija CI ni dokaz uspešnega zagona.

## Kaj še zahteva preizkus pri zaposlenem

- Celoten intervju in združevanje z dejanskim AIOS/globalnimi navodili.
- Samodejna izbira osebnega /dokumenti v novem pogovoru brez izrecnega priklica, tudi iz podmap.
- Namestitev odvisnosti, pravice in poti na službenem Windows oziroma macOS računalniku.
- Resnična sinhronizacija Nextclouda, delni prenosi, offline datoteke in različni strežniški dostopi.
- Ustvarjena lokalna Desktop rutina, ozke trajne odobritve, dejanski samodejni zagon in nadomestni zagon po prebujanju.
- Kakovost povzetkov na odobrenem vzorcu dejanskih DOCX, PDF in XLSX.
- Potrjena organizacijska pravila obdelave, deljenja, hrambe in čiščenja izpeljane vsebine.

OCR, grafi in preračunavanje Excelovih formul niso vključeni. Kontrolni odtisi preverjajo različico in celovitost, ne resničnosti povzetkov ali strežniških dovoljenj. Indeks je pomoč pri iskanju, ne zamenjava izvirnikov.
