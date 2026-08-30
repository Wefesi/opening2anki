# Database Schema (SQLite)

Reference documentation for the SQL database schema (`schema.sql`). Tables for imported games, master opening cache, generated Anki flashcards, sync bookmarks, and optional personal repertoires.

## games

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Internal ID |
| external_id | TEXT | Game ID from Lichess / Chess.com |
| source | TEXT | `lichess` \| `chesscom` \| `manual` |
| pgn | TEXT | Full PGN game string |
| my_color | TEXT | `white` \| `black` |
| result | TEXT | `1-0` \| `0-1` \| `1/2-1/2` \| `*` |
| time_control | TEXT | `bullet` \| `blitz` \| `rapid` \| `classical` |
| played_at | TEXT | Game timestamp (ISO-8601) |
| imported_at | TEXT | Import timestamp |
| processed | INTEGER | 0/1 – whether the opening analysis pipeline has run |
| processed_at | TEXT | Processing completion timestamp |

**Constraint:** `UNIQUE(external_id, source)` – prevents duplicate imports of the same game.

## card_mapping

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Internal ID |
| card_hash | TEXT | Hash of (fen + correct_move + card_type) – **unique**, prevents duplicate flashcards |
| card_type | TEXT | `opening_deviation` \| `repertoire_deviation` |
| anki_note_id | INTEGER | Note ID returned by AnkiConnect |
| source_game_id | INTEGER (FK → games.id, nullable) | Game that produced the card |
| fen | TEXT | Board position FEN before the first bad deviation |
| correct_move | TEXT | Best move (from Master DB or Stockfish) |
| played_move | TEXT | The inaccurate / mistake move actually played |
| deviation_ply | INTEGER | Half-move number of the deviation |
| centipawn_loss | INTEGER | Calculated evaluation loss via Stockfish |
| eval_before_cp | INTEGER | Position evaluation before the played move |
| eval_after_cp | INTEGER | Position evaluation after the played move |
| master_stats_json | TEXT | JSON string with Master DB candidate moves & stats (optional) |
| created_at / last_synced_at | TEXT | Timestamps |

## opening_cache

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Internal ID |
| fen | TEXT (UNIQUE) | Normalized board position FEN (excluding move counters) |
| master_data_json | TEXT | Cached Master DB move options & frequency stats (e.g. Lichess Masters Explorer) |
| created_at | TEXT | Creation timestamp |
| updated_at | TEXT | Last update timestamp |

## repertoires *(Optional)*

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Internal ID |
| name | TEXT | e.g. "Najdorf against 1.e4" |
| color | TEXT | `white` \| `black` |
| source_pgn_path | TEXT | Source PGN file path |
| created_at / updated_at | TEXT | Timestamps |

## repertoire_entries *(Optional)*

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Internal ID |
| repertoire_id | INTEGER (FK → repertoires.id) | Associated repertoire ID |
| parent_id | INTEGER (FK → repertoire_entries.id, nullable) | Parent move node in the variation tree |
| ply | INTEGER | Half-move number in the line |
| fen_before | TEXT | Board position before the move |
| move_uci | TEXT | Move in UCI notation, e.g. `e2e4` |
| move_san | TEXT | Move in SAN notation, e.g. `e4` |
| is_main_line | INTEGER | 0/1 – main line vs subvariation |

## sync_state

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Internal ID |
| source | TEXT | `lichess` \| `chesscom` |
| username | TEXT | Account username |
| last_synced_at | TEXT | Last sync timestamp |
| last_game_external_id | TEXT | Last processed game ID bookmark |

**Constraint:** `UNIQUE(source, username)` – one sync cursor per platform account.

## Relationships

- `games` 1 → 0..1 `card_mapping` (via `source_game_id`): at most one flashcard per game (first bad opening deviation)
- `repertoires` 1 → N `repertoire_entries` (via `repertoire_id`, optional)
- `repertoire_entries` self-references via `parent_id` → builds the variation tree
- Deduplication is enforced directly in the schema: `games.UNIQUE(external_id, source)` and `card_mapping.card_hash UNIQUE`

