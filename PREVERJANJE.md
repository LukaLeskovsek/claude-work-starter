# Kaj je preverjeno

9. 9. 2026. Preverjanje je potekalo na macOS, v začasnih mapah z umetnimi podatki. Noben osebni profil ni bil ustvarjen in uporabnikova dejanska navodila ali službeni dokumenti niso bili spremenjeni.

**15 avtomatskih preizkusov pomožnega skripta: uspešno.**

- Štetje vrst datotek, tudi `.DOCX` z velikimi črkami, brez zapisovanja med popisom.
- Izključene, skrite in tehnične mape; izključitve ne razlikujejo velikih/malih črk in se po shranitvi kazala ohranijo pri naslednjih klicih.
- Zavrnitev relativnega izhoda iz dovoljene mape, absolutne poti dokumenta in simbolnih povezav.
- Vidna napaka pri nedostopni podmapi; simulirana napaka dovoljenja, ne preizkus organizacijskega sistema dostopov.
- Ločeni zapisi za enako poimenovani datoteki v različnih podmapah.
- Osveževanje kazala in uporaba iste zbirke na drugi lokalni poti.
- Ohranitev tuje vsebine v obstoječi mapi `.claude-docs`.
- DOCX: vrstni red odstavka, tabele in naslednjega odstavka, navedba izvora, nespremenjen izvirnik.
- Poškodovan DOCX po predhodnem uspešnem branju ne vrne stare vsebine.
- PDF z besedilom, prazna stran in PDF s sliko brez besedila; opozorilo na vizualni pregled.
- Izbrani obseg PDF-strani in zavrnitev neobstoječe strani; obseg se preda pretvorniku.
- Nadomestno branje s `pypdf`, ko `pdftotext` ni na voljo.

YAML-glava skilla je bila preverjena z lokalnim YAML bralnikom. Standardni validator skillov ni stekel zaradi manjkajočega PyYAML; zaradi tega nismo nameščali novih odvisnosti. Ime, opis in dovoljeni polji so bili preverjeni z nadomestnim bralnikom in ročnim pregledom.

Astra je pregledala navodila in pomožni skript. Na podlagi pregleda so bile popravljene izključitve glede velikosti črk, prenosljivost lokalne poti, zavajajoče sporočilo ob napaki in pretvorba samo zahtevanih PDF-strani; popravljeno je bilo tudi nekaj formulacij.

Pri pripravi samostojnega GitHub repozitorija so bila navodila nato usklajena z vnaprej določenim osnovnim setupom: manj tehničnih odločitev za zaposlenega, preprosta navodila za uporabo in pregled konkretnih primerov po nekaj dneh. Te zadnje uredniške spremembe niso bile ponovno pregledane z Astro. Pomožni skript je ostal nespremenjen; vseh 15 preizkusov je bilo ponovno uspešnih.

## Kaj še ni potrjeno

10. 9. 2026: dodan pomočnik za prenos celotnega javnega ZIP-a neposredno v izbrano delovno mapo. **12 lokalnih avtomatskih preizkusov priprave paketa je uspešnih**: vseh deset datotek na pravih mestih, ponovitev brez sprememb, ohranitev obstoječih dokumentov in osebnih navodil, ustavitev pred zapisom ob konfliktu, kontrolni odtisi, zavrnitev manjkajočih/podvojenih/nevarnih poti in simbolnih povezav. Testi uporabljajo začasne mape na macOS; ne izvajajo intervjuja ali spreminjajo uporabnikovih nastavitev. Ponovitev: `python3 preverjanje/test_pripravi.py`. To ne potrjuje delovanja na Windows ali uporabnikovem računalniku.

Celoten intervju, zapis globalnih datotek, nalaganje skilla ter vnos nastavitev Chat/Cowork **še niso bili izvedeni v Claude Code na zaposlenčevem računalniku**. Navodila predpisujejo ta zaključni preizkus. Prav tako ni opravljen preizkus na Windows, dejanskem skupnem Drive ali zapletenih strankinih dokumentih. Dovoljenja in dovoljenost obdelave je treba potrditi ločeno.

Ta osnovni bralnik ne preverja popolnosti vsebine, ne izvaja OCR in ni vsebinski ali semantični iskalnik. Kontrolni odtis pove, katero različico datoteke je prebral, ne dokazuje pravilnega razumevanja dokumenta.

Za ponovitev tehničnih preizkusov uporabi `preverjanje/test_dokumenti.py` s Python. Testno okolje potrebuje `reportlab`, `Pillow`, `pypdf` in za preizkus prve PDF-poti tudi `pdftotext`; za vsakdanji popis in DOCX te dodatne knjižnice niso potrebne.
