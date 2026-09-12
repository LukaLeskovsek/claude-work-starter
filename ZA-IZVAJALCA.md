# Za izvajalca

## Kaj namestimo

Izdaja 2026-09-12-v4.2 pripravi osebni skill /dokumenti, lokalni vsebinski indeks in navodila za dnevno rutino. Zaposleni odpre dejansko delovno mapo ter prilepi javno navodilo. Ne potrebuje GitHuba ali upravljanja tehničnih datotek.

- Osebna navodila in profil: zasebno v uporabnikovi Claude konfiguraciji; ne v Nextcloudu.
- Pripomoček: `~/.claude/skills/dokumenti/`.
- Osebno stanje: `~/.claude-work-starter/`, z `nastavitve.json`, `KAZALO.md`, `iskanje.sqlite` in `stanje.json`.
- Skupni izvlečki in povzetki: `.claude-index/` v zbirki, samo po potrditvi enakega kroga dostopa in dovoljenja pisanja. Sicer lokalno pod osebno mapo.
- Poslovna pravila in poslovni skilli: potrjeni projektni dokumenti v Nextcloudu. Osebni /dokumenti naj ne bo podvojen kot projektni skill.

SQLite je ponovno zgradljiva lokalna iskalna datoteka, ne strežnik. Vsebuje kopijo dovoljene vsebine in je občutljiv. Skrita mapa ni varnostna meja; preveri dejansko zasebnost in izključitev iz sinhronizacije. Pri skupnem računalniškem računu nastavitev odloži.

## Celoten potek na enem računalniku

1. Potrdi koren, izključitve, obdelavo pri Claudu in zasebno lokacijo. Za skupno shranjevanje posebej preveri dostope. Izvirnikov ne premikaj.
2. Agent opravi intervju o vlogi, sodelovanju, lokacijah in povezavah. Ne izvaja popisa problematičnih procesov.
3. Po potrditvi zažene pomočnika za osebni skill, združi profil ter globalna navodila iz `predloge/GLOBALNA-NAVODILA.md`. Obstoječi AIOS ostane.
4. Registrira zbirke s stabilnimi ID-ji in vsemi izključitvami. Privzeti nabor je spremenjeno od 2026-01-01, ne »vse veljavno od 2026«. Starejši dokumenti se izrecno vključijo.
5. Pripravi majhno serijo. Claude vrne resnične povzetke v zasebni odgovori.json; pripomoček potrdi rezultat in objavi dokončane pakete. Ročno primerjaj pomembna dejstva z izvirnikom.
6. V novem pogovoru brez omembe /dokumenti preveri samodejno izbiro osebnega skilla, pravi obseg in vir. Preveri tudi podmapo in nepovezano mapo.
7. Agent v isti Desktop Code seji sam ustvari ali posodobi eno lokalno rutino po `predloge/DNEVNA-RUTINA.md`; ročni obrazec je samo nadomestna pot. Preveri Run now, naslednji zagon brez ponovne obdelave in dejanski samodejni zagon.
8. Zaposlenemu ostane kratek napotek za delo in povratno informacijo po nekaj dneh, ne tehnično poročilo.

## Predpogoji

Python 3.9+ s SQLite FTS5. DOCX in osnovni popis ne potrebujeta dodatnih knjižnic; PDF uporablja pdftotext ali pypdf, XLSX uporablja openpyxl. Namestitveni seznam je `dokumenti/requirements.txt`. Po odobritvi uporabi ločeni venv v zasebni mapi indeksatorja, ne globalnih paketov. Odvisnosti se ne nameščajo med iskanjem.

Če manjkajo orodja ali odobritve, nadaljuj neodvisni del, blokado pa pokaži. Ne spreminjaj varnostnih nastavitev ali prijav, da bi test navidezno uspel.

## Dnevno delovanje

Vsak zaposleni ima svojo lokalno rutino, praviloma ob 9.00. Računalnik mora biti buden in Claude Desktop odprt. Rutina uporablja obstoječi Claudeov račun; lokalno izvajanje ne pomeni lokalnega modela ali brezplačne porabe.

Pripomoček najprej poišče veljavne pakete glede na odtis izvirnika in različico postopka. Drugi računalnik lahko povzetek ponovno uporabi. Obstoj kazala ali datum mape nista dokaz svežine.

Na dan izda največ 10 dokumentov oziroma 20 kosov po največ 12.000 znakov. To ni natančna omejitev tokenov. Paket, ki čaka na povzetke, se ponovno uporabi do potrditve; daljši dokument se nadaljuje naslednji dan. Delni dokument še ni iskalni zadetek. Nespremenjeni dokumenti ne potrebujejo novega povzemanja.

Sočasna obdelava na dveh računalnikih je dovoljena. Paketi so ločeni in kontrolno preverjeni; delni prenosi se preskočijo. Ne zagotavljamo obdelave natanko enkrat. Skupno kazalo je zamenljiva orientacija, ne vir dovoljenj ali popolnosti.

Lokalni `izvajanje.lock` prepreči sočasno pisanje dveh lokalnih vzdrževalnih ukazov. Po sesutju preveri, da proces ne teče več, šele nato odstrani točno to zaklepno datoteko. Ne briši porabe ali delovnih paketov za obhod omejitev.

## Meje in odprte preverbe

- OCR, interpretacija grafov in preračunavanje XLSX niso vključeni. Formule in shranjeni rezultati so ločeni; rezultat je lahko zastarel ali manjka.
- Bralnik ima omejitve velikosti. Prevelik ali poškodovan dokument je vidna napaka, ne popoln rezultat.
- Izključitve se uveljavijo tudi pri branju; omejitev v navodilih ni isto kot tehnično dovoljenje.
- Pri izgubi dostopa oziroma spremembi vira se stari zadetek ne vrne. Brez sinhroniziranih sprememb Nextclouda lokalni pripomoček ne pozna novih strežniških ACL-jev.
- Rutine ne brišejo skupnih paketov. Skrbnik ureja hrambo in čiščenje; umik iz iskanja ni izbris vseh kopij, dnevnikov ali varnostnih kopij.
- Povzetki so modelni izhod. Preverjanje JSON-a in kontrolnih odtisov ne zagotavlja resničnosti.
- Skupne skille objavlja skrbnik. Za prvi Intrix primer uporabi `predloge/IZ-NALOGE-V-SKILL.md`; generična predloga ni že preizkušen CRM skill.
- Osebni skill ne omogoči samodejnega dostopa iz spletnega Chata ali Coworka. To nista površini pilotne integracije.

## Nadgradnja in vrnitev

Prenosni pomočnik z `--upgrade` nadgradi samo nespremenjene datoteke znane prejšnje izdaje in ustvari kopijo pod .claude-starter-backups v delovni mapi. Pri drugih spremembah se ustavi pred zapisovanjem.

Osebni namestitveni pomočnik ima ločen korak migracije projektnega skilla. Samodejno umakne samo prepoznano nespremenjeno kopijo, v zasebno obnovljivo mapo. Prilagojene omejitve pregleda in prenese izvajalec; ne prepiši jih na slepo.

Za vrnitev najprej ustavi lokalno rutino, preveri vsebino konkretne varnostne kopije ter obnovi le datoteke tega starterja po potrditvi. Ne ponastavljaj celotne .claude ali AIOS. Lokalni SQLite lahko obnoviš z ukazom kazalo brez novega povzemanja.

## Dokaz izvedbe

Aktualni rezultati in manjkajoči preizkusi so v PREVERJANJE.md. Testi v začasnih mapah ne dokazujejo delovanja dejanskega Nextclouda, Windows dovoljenj, samodejne izbire skilla ali Desktop rutine. Ti preizkusi so pogoj zaključene namestitve pri zaposlenem.
