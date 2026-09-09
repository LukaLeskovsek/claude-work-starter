# Za izvajalca

Naš standard določa prvo raven nastavitve. Intervju zajame delovni profil, način sodelovanja, lokacije datotek ter uporabljena orodja in smiselne povezave. Ni odkrivanje težav ali popis procesov; ne iščemo najbolj zamudne naloge ali priložnosti za avtomatizacijo. Tehnične odločitve in odpravljanje težav so odgovornost izvajalca.

## Dogovorjeni standard

- Slovenščina, kratki odgovori, najprej uporaben rezultat; uporabnikove jezikovne želje imajo prednost.
- Vprašanja samo ob pomembni nejasnosti. Dejstva, predlogi in neznani podatki so jasno ločeni.
- Delo v dogovorjeni mapi; osebni profil zunaj skupnih map.
- Na podlagi dejansko uporabljene e-pošte, koledarja in dokumentnega okolja predlagaj smiselne povezave. Preveri podporo in dovoljenja; povezava se izvede šele po ločeni potrditvi. Predlagana povezava ni že vzpostavljen dostop.
- Nov osnutek v ločenem izhodu, ohranjeni izvirniki. Pred brisanjem, prepisovanjem, pošiljanjem, deljenjem ali širjenjem dostopa vprašaj.
- En popis dokumentov in sprotno branje izbranih izvirnikov. Dodatna navodila samo za podmape z drugačnimi pravili.
- Po zaključeni personalizaciji sledi kratek preizkus uporabe. Zadostuje pripravljen testni dokument; uporabniku ni treba opredeliti procesa za avtomatizacijo.
- Po nekaj dneh kratek pregled konkretnih primerov in ozkih popravkov nastavitve. Samodejni opomniki niso del paketa.

## Kaj Claude pripravi

| Lokacija | Namen |
| --- | --- |
| Zasebna lokalna mapa | `MOJ-DELOVNI-PROFIL.md` z načinom sodelovanja, lokacijami in stanjem povezav; besedili za nastavitve Chat/Cowork ter kratka navodila za uporabo |
| `~/.claude/CLAUDE.md` | Kratka osebna navodila za vse delovne mape v Claude Code |
| Izbrana delovna mapa | `CLAUDE.md`: namen mape, potrjeni viri, izhodi, način dela in meje |
| `.claude-docs/` | `KAZALO.md` s pregledom in `inventar.json` s potmi; brez kopije celotne vsebine |
| `.claude/skills/dokumenti/` | Ukaz `/dokumenti` za popis, iskanje po imenih in branje izbranih DOCX/PDF |
| Posamezne podmape po potrebi | `CLAUDE.md` samo za posebnosti; ločeno kazalo samo za samostojno zbirko |

Uporabnik potrdi vsebino profila in razumljiv povzetek sprememb. Celotni tehnični predlog in ciljne poti so na voljo na zahtevo; uporabniku jih ni treba urejati. Obstoječe nastavitve se ohranijo, spremembe varnostno kopirajo, konflikti pa se ne razrešujejo z ugibanjem.

## Priprava prvega srečanja

Preveri, ali so nameščeni Claude Code, Python 3.9+ in ustrezno lokalno orodje za PDF. Na Windows je lahko ukaz `py -3`, na macOS `python3`. DOCX in popis ne potrebujeta dodatnih Python knjižnic. Za PDF se uporabi `pdftotext` ali `pypdf`; manjkajoče odvisnosti namesti izvajalec po dogovoru. Ne pričakuj, da jih bodo zaposleni nameščali sredi intervjuja.

Potrdi račune, dovoljene podatke, namensko delovno mapo, izključitve in dostop do nje. Za prvo nalogo pripravi testni ali odobren primer. Če je računalniški račun skupen, najprej uredi ločene uporabnike ali omeji nastavitev na projekt. Spremembe skupnih pravil potrebujejo odgovorno osebo; osebni `CLAUDE.local.md` v skupnem Drive ni zaseben.

Pri povezavah preveri dejansko podprto možnost za uporabnikov račun in način uporabe Claude. Prednost ima najmanjši potreben dostop; če povezava zahteva širša dovoljenja, to razloži pred potrditvijo. Skrbniška blokada ne ustavi priprave osebnih navodil in lokalne mape. V profilu loči uporabljena orodja, predlagane povezave in dejansko preizkušen dostop. Ne pregleduj nabiralnika ali koledarja zato, da bi iz vsebine sestavil uporabnikov profil.

Ta repozitorij ne vsebuje že izpolnjenega profila. Namestitveni postopek je v [NASTAVI-CLAUDE.md](NASTAVI-CLAUDE.md); izvajaj ga samo na izrecno zahtevo uporabnika. Ne izvajaj ga avtomatsko med razvojem ali pregledom repozitorija.

## Meje

`CLAUDE.md` so navodila modelu, ne tehnične omejitve dostopa. Globalni `CLAUDE.md` velja za Claude Code, ne za nastavitve Chat in Cowork; tja je treba pripravljeni besedili dejansko vnesti. Za globalno datoteko je lahko potrebno dodatno dovoljenje zunaj odprte mape. Ne uporabljaj obhoda dovoljenj.

Kazalo vsebuje imena in poti, ne preiskane vsebine. Če imena ne zadostujejo, dogovori omejeno zbirko za vsebinski pregled. PDF-skeni, zahtevne tabele, grafi in pomembni zneski potrebujejo pregled izvirnika; ta paket ne izvaja OCR. Datum spremembe datoteke ni nujno datum dokumenta.

Skript ne uporablja omrežja in ne spreminja izvirnikov; njegov izpis pa Claude prejme v pogovor. Pregled brez pisanja datotek ni jamstvo, da storitev ne hrani pogovora. V ta repozitorij ne dodajaj strankinih dokumentov, profilov, inventarjev ali poverilnic. Zasebnost repozitorija ni nadomestilo za pregled vsebine pred nalaganjem.

Ni strežnika, baze, avtomatskega OCR, osebnih GBrain instanc ali nenadzorovanih opravil.

## Viri in preizkusi

Uradne reference, preverjene pri pripravi 9. 9. 2026; pred delavnico preveri morebitne spremembe vmesnika:

- [Obseg in nalaganje CLAUDE.md](https://code.claude.com/docs/en/memory)
- [Claude Code skilli in ukazi](https://code.claude.com/docs/en/skills)
- [Personalizacija Chat](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features)
- [Cowork in globalna navodila](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork)

Dokazi in še nepreverjeni deli: [PREVERJANJE.md](PREVERJANJE.md). Pred skupinsko delavnico izvedi celoten potek na testnem uporabniku.
