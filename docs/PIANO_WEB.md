# Livingdex Web — Piano d'azione

Data: 2026-11-10. Obiettivo: versione web del livingdex con le stesse funzioni della CLI
(`livingdex_query.py`), più visuale, senza perdere nessun dato.

## Stato attuale (rilevato)

- **Fonte di verità oggi:** `data/pokemon_livingdex/livingdex_09042026.csv`
  — 1426 slot, 65 box, 1388 catturati, 38 mancanti, 0 shiny.
  Colonne: `id,name,captured,shiny,box,ref_name,variant,box_prefix,box_group`
  (`box_prefix`/`box_group` sono derivate: le scrive `stats()` nel CSV a ogni `save`).
- **Disponibilità per gioco:** `data/availability.csv` — 1094 righe × 39 giochi (Gen I → Scarlatto/Violetto),
  join su `ref_name` (copertura 100%). Codici (`C`, `E`, `T`, `Ev`, `CD`, `DW`, `FS`…) **senza legenda scritta**.
- **Storico:** 8 snapshot datati in `data/pokemon_livingdex/` + `livingdex.json` (export app esterna, formato `boxes[].pokemon[]`).
- CLI: `p` pokemon, `n` next, `b` box, `f` find fuzzy (jellyfish), `m` mancanti, `g` gioco, `a`/`d` add/delete, `stats 0|1|2`, `save`.
- Coordinate box: `[pagina/riga/colonna]`, 30 slot per box (6×5), calcolate dall'ordine dei box.

### Anomalie da chiarire PRIMA di migrare (rischio perdita dati)

1. ~~Shiny azzerati nel tempo~~ — **risolto (10/11/2026):** rimossi volutamente dall'utente, conservati a parte.
   Decisione: due living dex con la stessa disposizione, **normale** e **shiny**; lo shiny parte vuoto.
2. **Forme rimosse:** `zygarde-10_power_construct`, `zygarde-power_construct` (05/2025), `alcremie`/`unown`/`vivillon` base (08/2025). Volute?
3. `gigamax` usato da `search()` ma la colonna non esiste più.
4. `livingdex.csv` (senza data) è vecchio (1423 righe, colonne diverse): non è la fonte attuale.

## Scelte tecniche

- **Zero build, zero framework:** `web/index.html` + `app.js` + `style.css` in JS vanilla.
- **Server locale stdlib:** `server.py` (`http.server`, nessuna dipendenza) — serve i file statici, `GET /api/dex`,
  `POST /api/slot` (una modifica alla volta). Come il classificatore di Tasca: raggiungibile dal **telefono sulla stessa Wi-Fi**,
  risponde solo a indirizzi privati e alla propria pagina (richieste da altre origini rifiutate).
  Ogni salvataggio scrive prima un backup datato in `data/backups/`, poi sovrascrive in modo atomico (file temporaneo + rename).
- **Dati:** resta un CSV canonico unico `data/livingdex.csv` (colonne pulite, niente derivate) letto sia dalla CLI che dal web.
  Diff leggibili in git.
- **Immagini:** sprite HOME da PokeAPI (`PokeAPI/sprites`, `other/home/{id}.png` + `shiny/`), fallback
  `pokemondb` per forme mancanti, poi placeholder (cerchio grigio con numero). Verificato: base, unown, vivillon OK;
  alcremie da controllare. Sprite scaricati una volta in `web/sprites/` (offline, niente hotlink).
- **Riuso da TCG Collections:** `work/forms-catalog.json` (forme con ID PokeAPI, gruppo mega/gmax/regionale…, nomi in
  italiano) per mappare gli sprite, mostrare i nomi italiani e trovare le forme mancanti (Fase 5);
  `outputs/national-dex-forme-extra/REPORT.md` come elenco di forme già ragionate.

## Regole di interfaccia (prese da Tasca: dashboard 0.7.x e classificatore)

Valgono per ogni vista. In fase di review si controllano una per una.

**Aspetto**
- Colori solo come token su `:root`; tema chiaro e scuro automatici (`prefers-color-scheme`), mai fondo bianco al buio.
  Si parte dalla palette di Tasca (fondo `#f6f5f0` / `#101413`, accento `#244e43` / `#5fd0a5`, token danger/warn/info/ok).
- Font di sistema, raggi coerenti (16/10/6 px), titoli `text-wrap: balance`, contrasto alto.
- Numeri con `font-variant-numeric: tabular-nums`, allineati a destra nelle tabelle.
- Intestazione con titolo specifico, niente manifesto, badge o etichette superflue. Favicon SVG inline.
- `prefers-reduced-motion` spegne tutte le animazioni.

**Stato e conferme**
- Nessun indicatore «Salvato» fisso: compare una pillola solo con salvataggi in corso, offline o errori.
- Conferma di una scelta: piccolo segnale animato (~0,9 s) che non copre il contenuto. Avvisi: toast (2,5 s info, 6 s errore).
- Ogni caricamento ha uno stato visibile (immagini con shimmer, barra di attività); `role=status`/`aria-live` per lo stato,
  `role=alert` per gli errori.
- Stati vuoti con un'istruzione concreta («Nessun mancante in questo box», non una pagina vuota).
- **Nessuna modifica persa:** coda di salvataggio nel browser (`localStorage`) finché il server conferma, nuovi tentativi
  con attesa crescente, ricarica dello stato quando la pagina torna visibile.
- **Annulla** (pila delle ultime modifiche) e **Indietro** (cronologia di navigazione) sempre disponibili.

**Telefono (sotto 820 px)**
- Tutto in una schermata: barra in alto con contatore e barra di avanzamento, contenuto al centro, barra in basso con
  tre pulsanti (← Indietro · Annulla · Avanti →). `100dvh` e margini `safe-area`.
- Tasti ≥ 48 px, `touch-action: manipulation`, etichette brevi; scorrimento a sinistra/destra = successivo/precedente.
- Dettagli secondari richiudibili («Dettagli»). Provare a 375×812 e 360×640.

**Computer**
- Scorciatoie da tastiera (ignorate dentro campi di testo): `/` cerca, ←/→ risultato o box precedente/successivo,
  `C` catturato, `S` shiny, `U` annulla, `Esc` chiude.
- Immagine successiva precaricata; se un'immagine manca si passa alla fonte di ripiego, poi al placeholder.
- Filtri e ordinamento ricordati nel browser.

**Struttura**
- Pannelli richiudibili (`<details>`) con il conteggio nel titolo; tabelle con «Precedenti / Successive».
- Quando qualcosa è escluso o non disponibile, il motivo è consultabile (es. «perché non è ottenibile in questo gioco»).
- **Modalità Rivedi**: miniature raggruppate (per box o per stato), tocco = apri e correggi; «Riprendi» torna dove eri.
- Testi in italiano, pulsanti con verbi, spiegazioni brevi accanto ai controlli. Il piè di pagina dice dove stanno i dati.

## Fasi

### Fase 0 — Messa in sicurezza (bloccante)
- [ ] `git init` + primo commit con TUTTO com'è (snapshot, notebook, json) prima di toccare nulla.
- [ ] Archivio dei dati: **lo fornisce l'utente**. Prima di toccare qualunque file, controllare che contenga tutti i file
  di `data/` (lista e numero di righe confrontati con la cartella).
- [ ] Riorganizzazione root (regola repo): `notebooks/`, `scripts/`, `data/snapshots/`, file non-livingdex (`pokeguess`, `donut`, `bacche`, `ciambelle`, `unisci_testi…`) in `other/`.
- [ ] Risolvere le anomalie 2–4 sopra con l'utente.

**Fatto quando:** repo versionato, archivio verificato, anomalie decise.

### Fase 1 — Dati canonici
- [ ] `scripts/migrate.py`: `livingdex_09042026.csv` → `data/livingdex.csv` (drop derivate, + campi nuovi vuoti: `dex_no`, `sprite`).
- [ ] **Due dex, stessa disposizione:** colonne `captured` (dex normale, valori attuali) e `captured_shiny` (dex shiny, tutto
  `False`). La vecchia colonna `shiny` (oggi tutta `False`) sparisce: nessun dato perso, il check lo verifica.
- [ ] Check automatico (assert): stesso numero di righe, stessi `name`, stessi `captured`, `shiny` originale tutto `False`,
  stesso ordine box.
- [ ] CLI: `a`/`d` agiscono sul dex normale; il secondo argomento shiny di `a` diventa «aggiungi al dex shiny».
- [ ] `data/availability_legend.csv`: codice → significato → "ottenibile oggi?" (sostituisce la lista hardcoded `not_available_values`).
- [ ] CLI puntata al nuovo file; `stats()` smette di scrivere colonne derivate.

**Fatto quando:** CLI funziona identica sul nuovo file, check passa.

### Fase 2 — Immagini
- [ ] `scripts/fetch_sprites.py`: mappa `name` → ID PokeAPI (prima `forms-catalog.json` di TCG Collections, poi lista `/pokemon?limit=2000` + `/pokemon-form`), tabella override manuale `data/sprite_overrides.csv` per i casi strani (`_alola`, `-m`/`-f`, `_gmax`, alcremie, cap pikachu).
- [ ] Download normale + shiny in `web/sprites/`, report copertura (quanti trovati / placeholder).

**Fatto quando:** report copertura ≥ 95%, il resto ha placeholder.

### Fase 3 — Web MVP in sola lettura
Una pagina, quattro viste. In alto un selettore **Normale / Shiny** decide su quale dex lavorano tutte le viste
(sprite shiny nel dex shiny, statistiche separate, preferenza ricordata). Il dex shiny vuoto mostra uno stato vuoto con
istruzione, non errori.
- [ ] **Dashboard:** totale / catturati / mancanti / shiny con %, barre per gruppo (kanto, johto… forms) e per box (= `stats 0/1/2`).
- [ ] **Box:** griglia 6×5 con sprite, colori catturato / mancante / shiny, coordinate `[pag/riga/col]`, frecce box precedente/successivo.
- [ ] **Ricerca:** campo unico fuzzy su pokemon e box, lista risultati scorribile, ←/→ per passare al risultato successivo (= `p` + `n`), click apre il box con lo slot evidenziato.
- [ ] **Mancanti:** lista filtrabile per box/gruppo + **"dove prenderli"**: per ogni mancante i giochi in cui è ottenibile; filtro per gioco (= `g`) e classifica "giochi che coprono più mancanti".

- [ ] Nomi italiani accanto a quelli inglesi (da `forms-catalog.json` / PokeAPI), ricerca su entrambi.
- [ ] Layout secondo le «Regole di interfaccia», tema chiaro e scuro.

**Fatto quando:** ogni comando CLI di lettura ha un equivalente nel web (checklist parità) e le pagine superano le
regole di interfaccia a 375×812, 360×640 e su computer.

### Fase 4 — Modifica dal web
- [ ] Tocco su slot: segna/togli catturato nel dex attivo (normale o shiny), conferma animata. I due dex non si toccano a vicenda.
- [ ] Salvataggio immediato di ogni modifica tramite la coda nel browser (niente pulsante Salva); backup automatico lato server;
  Annulla e Indietro come nel classificatore.
- [ ] Log modifiche `data/changes.log` (data, nome, campo, prima → dopo).

**Fatto quando:** add/delete/save della CLI sostituibili dal web; test: modifica + salvataggio + ricarica = dato identico, backup creato.

### Fase 5 — Ampliamento database: forme
- [ ] Confronto automatico con `forms-catalog.json` e PokeAPI (`/pokemon-species` → varietà + forme) per elencare forme memorizzabili in HOME non presenti nel dex
  (es. Zygarde 10%/Perfetta, già tolte dal dex nel 05/2025: decidere).
- [ ] Revisione manuale della lista (cosa entra nel living dex, cosa no: mega, forme battaglia, ecc.).
- [ ] Inserimento nuove righe in box nuovi o esistenti; giochi usciti dopo S/V (es. Leggende Z-A) da valutare.

### Fase 6 — Ampliamento database: provenienza
- [ ] Colonne giochi mancanti in `availability.csv` (giochi recenti, DLC, HOME/GO come fonte).
- [ ] Disponibilità **per forma** (oggi è per `ref_name`: le forme ereditano quella del base, spesso sbagliato).
- [ ] Per ogni gioco: compatibile con HOME sì/no, percorso di trasferimento (Bank, GO, diretto).
- [ ] Fonte annotata per ogni dato (Bulbapedia / Serebii / PokeAPI) + legenda completa.
- [ ] Facoltativo: campo `origin` sui catturati (da quale gioco viene il mio esemplare).
- [ ] Nel web: scheda pokemon con "come ottenerlo" leggibile (non codici grezzi).

### Fase 7 — Review
- [ ] **Dati:** confronto finale `data/livingdex.csv` vs snapshot 09/04/2026 (nessuna riga persa, differenze solo volute); campione di 30 pokemon verificati a mano su HOME.
- [ ] **Provenienza:** controllo a campione di 20 voci contro Bulbapedia.
- [ ] **Codice:** review del server (salvataggio atomico, backup, input validato) e del JS.
- [ ] **Interfaccia:** checklist «Regole di interfaccia» voce per voce; prova browser headless a 375×812, 360×640 e
  computer, tema chiaro e scuro, zero errori in console, zero richieste esterne (sprite locali).
- [ ] **UX:** uso reale per una settimana, anche da telefono; lista correzioni.
- [ ] Ogni consegna ha un `docs/VERIFICA-<versione>.md` come in Tasca: cosa cambia, verifiche eseguite, **non ancora provato**.
  Le prove non devono mai modificare i dati reali (si lavora su una copia).
- [ ] Checklist parità CLI ↔ web completa; decidere se ritirare la CLI.

## Ordine e dipendenze

0 → 1 → (2 e 3 in parallelo) → 4 → 7a (review intermedia) → 5 → 6 → 7.
Le fasi 5–6 arricchiscono i dati senza toccare la UI di base.

## Fuori scope per ora
Hosting online/multiutente, login, framework frontend, database SQL. Il telefono è coperto dalla rete di casa;
fuori casa si valuta dopo la fase 4 (es. GitHub Pages in sola lettura).
