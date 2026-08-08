# Datenbank-Schema (SQLite)

Referenz-Dokumentation zum SQL-Schema (`schema.sql`). Fünf Tabellen: Partien, Repertoire (als Baum), generierte Karten und der Sync-Stand pro Quelle.

## games

| Spalte | Typ | Beschreibung |
|---|---|---|
| id | INTEGER (PK) | Interne ID |
| external_id | TEXT | Partie-ID von Lichess/Chess.com |
| source | TEXT | `lichess` \| `chesscom` \| `manual` |
| pgn | TEXT | Vollständiges PGN |
| my_color | TEXT | `white` \| `black` |
| result | TEXT | `1-0` \| `0-1` \| `1/2-1/2` |
| time_control | TEXT | `bullet` \| `blitz` \| `rapid` \| `classical` |
| played_at | TEXT | Zeitpunkt der Partie (ISO-8601) |
| imported_at | TEXT | Zeitpunkt des Imports |
| processed | INTEGER | 0/1 – ob die Analyse-Pipeline gelaufen ist |
| processed_at | TEXT | Zeitpunkt der Verarbeitung |

**Constraint:** `UNIQUE(external_id, source)` – verhindert doppelten Import derselben Partie.

## repertoires

| Spalte | Typ | Beschreibung |
|---|---|---|
| id | INTEGER (PK) | Interne ID |
| name | TEXT | z. B. "Najdorf gegen 1.e4" |
| color | TEXT | `white` \| `black` |
| source_pgn_path | TEXT | Ursprungsdatei |
| created_at / updated_at | TEXT | Zeitstempel |

## repertoire_entries

| Spalte | Typ | Beschreibung |
|---|---|---|
| id | INTEGER (PK) | Interne ID |
| repertoire_id | INTEGER (FK → repertoires.id) | Zugehöriges Repertoire |
| parent_id | INTEGER (FK → repertoire_entries.id, nullable) | Vorgänger-Zug (Baumstruktur) |
| ply | INTEGER | Halbzug-Nummer in der Linie |
| fen_before | TEXT | Stellung vor dem Zug |
| move_uci | TEXT | Zug in UCI-Notation, z. B. `e2e4` |
| move_san | TEXT | Zug in SAN-Notation, z. B. `e4` |
| is_main_line | INTEGER | 0/1 – Haupt- oder Nebenvariante |

## card_mapping

| Spalte | Typ | Beschreibung |
|---|---|---|
| id | INTEGER (PK) | Interne ID |
| card_hash | TEXT | Hash aus (fen + correct_move + card_type) – **eindeutig**, verhindert doppelte Karten |
| card_type | TEXT | `deviation` \| `blunder` |
| anki_note_id | INTEGER | Von AnkiConnect zurückgegebene Note-ID |
| source_game_id | INTEGER (FK → games.id, nullable) | Partie, aus der die Karte entstand |
| fen | TEXT | Stellung |
| correct_move | TEXT | Korrekter Zug (aus Repertoire oder Engine) |
| played_move | TEXT | Tatsächlich gespielter Zug |
| eval_before_cp / eval_after_cp | INTEGER | Bewertung in Centipawns vor/nach dem Zug (bei `blunder`) |
| centipawn_loss | INTEGER | Berechneter Verlust |
| created_at / last_synced_at | TEXT | Zeitstempel |

## sync_state

| Spalte | Typ | Beschreibung |
|---|---|---|
| id | INTEGER (PK) | Interne ID |
| source | TEXT | `lichess` \| `chesscom` |
| username | TEXT | Account-Name |
| last_synced_at | TEXT | Letzter Sync-Zeitpunkt |
| last_game_external_id | TEXT | Letzte verarbeitete Partie-ID |

**Constraint:** `UNIQUE(source, username)` – ein Sync-Cursor pro Account.

## Beziehungen

- `games` 1 → N `card_mapping` (über `source_game_id`): eine Partie kann mehrere Karten erzeugen
- `repertoires` 1 → N `repertoire_entries` (über `repertoire_id`)
- `repertoire_entries` referenziert sich selbst über `parent_id` → bildet den Repertoire-Baum
- Duplikat-Vermeidung liegt direkt im Schema: `games.UNIQUE(external_id, source)` und `card_mapping.card_hash UNIQUE`

Vollständiges, ausführbares SQL: siehe `schema.sql`.
