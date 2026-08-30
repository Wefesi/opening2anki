# opening2anki – Component Overview (with AnkiConnect & Master Database)

Architecture overview: Instead of building a custom scheduling and review engine, **Anki** (via AnkiConnect) handles flashcard storage and spaced-repetition scheduling. The application focuses on game ingestion, opening analysis, and card generation.

### Core Card-Creation Principles:
- **Zero-Config Opening Analysis:** No manual repertoire setup required by default.
- **Master Opening Database + Stockfish:** Played moves are matched against a Master Games Opening Database (e.g., Lichess Masters Explorer API / Polyglot book with local SQLite caching).
- **First Bad Deviation in Opening:** When a move leaves established theory, Stockfish calculates the centipawn loss. If it exceeds a configurable threshold (inaccuracy/mistake), exactly **one** Anki card is created for that position (first opening mistake of the game).
- **No Midgame/Endgame Blunder Cards:** Once the opening phase concludes (or the first deviation occurs), no further cards are generated for that game.
- **Modularity:** Opening theory queries use a modular `OpeningBookProvider` interface, allowing optional personal repertoire trees (PGN) to be plugged in seamlessly.

## Analysis Pipeline

| Component | Responsibility | Technology |
|---|---|---|
| PGN Importer | Ingests PGN files/strings, normalizes games | Python, `python-chess` |
| Opening Book Provider | Modular interface: Master Database (Lichess Masters API + local cache) or optional personal repertoire | Python (`OpeningBookProvider` interface) |
| Engine Analyzer | Calculates centipawn loss & best moves when leaving theory | Stockfish (binary) + `python-chess` UCI wrapper |
| Deviation Detector | Identifies the first bad opening deviation (book exit + CP loss $\ge$ threshold) | Python |
| Card Generator | Builds question/answer card content with board diagram (SVG before deviation) | Python, `python-chess` SVG export |

## Integration & Automation

| Component | Responsibility | Technology |
|---|---|---|
| Platform Client | Fetches new games from Lichess / Chess.com | Python `requests`, Lichess / Chess.com REST API |
| Sync Service | Triggers the pipeline periodically or on-demand | `APScheduler` or cron job |
| AnkiConnect Client | Creates/updates notes in Anki without altering scheduling state | Python `requests` → AnkiConnect add-on (`localhost:8765`) |

## Data Persistence

| Component | Responsibility | Technology |
|---|---|---|
| `games` | Ingested games and processing status | SQLite |
| `opening_cache` | Cache for Master DB position queries & theoretical stats | SQLite |
| `repertoires` / `repertoire_entries` | *(Optional)* Repertoire variation trees for users providing custom PGNs | SQLite |
| `card_mapping` | Stable ID (hash of FEN + move + type) → Anki note ID, preventing duplicate cards | SQLite |
| Anki Collection | Flashcard content and full spaced-repetition scheduling (SM-2/FSRS) | Anki itself (`.anki2`), local desktop |

**Why SQLite:** Fits the self-hosted, zero-config distribution model (no separate database server required). All access goes through `SQLModel` / `SQLAlchemy` ORM classes, making a future Postgres migration a one-line connection string change if ever needed.

## Dashboard UI (Graphical)

| Component | Responsibility | Technology |
|---|---|---|
| Dashboard API | Exposes sync, game analysis, settings, and statistics | FastAPI |
| Dashboard UI | Graphical interface: trigger syncs, inspect analyzed games & deviations, configure thresholds | React (Vite) + Tailwind CSS, `Recharts` for charts |

## Packaging & Sharing (Open-Source Tool)

To allow other users to clone and run the tool locally with their own Anki + Stockfish:

| Component | Purpose |
|---|---|
| `README.md` | Setup steps, prerequisites (Python, Stockfish binary, Anki + AnkiConnect add-on), quickstart |
| `config.yaml` / `.env` | User config: Lichess/Chess.com usernames, threshold settings, Stockfish path, Anki deck name |
| `pyproject.toml` | Packaging (`pip install -e .`), dependency declarations (`python-chess`, `requests`, etc.) |
| Anki Note Type Template | Included `.json` definition for the card format (board diagram, played move, correct move, stats) |
| License (e.g., MIT) | Open-source distribution license |

