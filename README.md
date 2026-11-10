# Livingdex

Tracker personale del living dex Pokémon (Pokémon HOME): stato dei box, mancanti, statistiche e giochi da cui
ottenere i Pokémon che mancano. Oggi è una CLI Python; la versione web è in sviluppo
(piano in [docs/PIANO_WEB.md](docs/PIANO_WEB.md)).

## Uso

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python livingdex_query.py
```

Va lanciato dalla cartella principale del repo (i percorsi dei dati sono relativi). Comandi: `h` per l'elenco;
`p` pokemon, `n` successivo, `b` box, `f` ricerca, `m` mancanti, `g` gioco, `a`/`d` aggiungi/togli, `stats 0|1|2`,
`save`, `c` chiudi senza salvare.

## Struttura

| Percorso | Contenuto |
|---|---|
| `livingdex_query.py` | CLI principale |
| `utils/` | Funzioni di stampa usate dalla CLI |
| `data/pokemon_livingdex/` | Living dex: `livingdex_09042026.csv` è il file in uso, gli altri sono snapshot storici |
| `data/availability.csv` | Disponibilità per gioco (Gen I → Scarlatto/Violetto); `data/availability/` sono i file di partenza |
| `data/pokeguess/`, `data/donut/` | Dati dei notebook secondari |
| `notebooks/` | Notebook di costruzione del database ed esperimenti (`pokeguess`, `donut`) |
| `docs/` | Piano della versione web |
| `configs/` | Workspace VS Code |

I notebook usano percorsi relativi alla cartella principale: in VS Code `.vscode/settings.json` imposta già la
cartella di lavoro dei notebook sulla radice del repo. `create_my_database.ipynb` è storico e punta a percorsi non
più presenti.
