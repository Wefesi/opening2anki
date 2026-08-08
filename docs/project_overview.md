# Eröffnungstrainer – Komponentenübersicht v2 (mit AnkiConnect)

Update gegenüber v1: Statt eines eigenen Scheduling- und Review-Systems übernimmt **Anki** (via AnkiConnect) die Kartenverwaltung und das Spaced-Repetition-Scheduling. Das eigene System fokussiert sich auf Import, Analyse und Card-Generierung.

## Analyse-Pipeline

| Komponente | Verantwortung | Technologie |
|---|---|---|
| PGN-Importer | Liest PGN-Dateien/-Strings ein, normalisiert Partien | Python, `python-chess` |
| Repertoire-Loader | Baut Repertoire-Baum aus PGN mit Haupt-/Nebenvarianten | Python, `python-chess` |
| Deviation-Detector | Findet ersten Abweichungspunkt vom Repertoire | Python (eigene Logik) |
| Engine-Analyzer | Berechnet Centipawn-Verlust pro Zug | Stockfish (Binary) + `python-chess` UCI-Wrapper |
| Card-Generator | Erstellt Frage/Antwort-Inhalt inkl. Stellungsbild | Python, `python-chess` SVG-Export bzw. `cairosvg` |

## Integration & Automatisierung

| Komponente | Verantwortung | Technologie |
|---|---|---|
| API-Client | Holt neue Partien von Lichess/Chess.com | Python `requests`, Lichess-/Chess.com-REST-API |
| Sync-Service | Triggert die Pipeline periodisch oder manuell | `APScheduler` oder Cron-Job |
| AnkiConnect-Client | Legt Karten in Anki an/aktualisiert sie, ohne Scheduling anzufassen | Python `requests` → AnkiConnect-Add-on (`localhost:8765`) |

## Datenhaltung

| Komponente | Verantwortung | Technologie |
|---|---|---|
| games | Importierte Partien, Verarbeitungsstatus | SQLite |
| repertoire_entries | Knoten des Repertoire-Baums | SQLite |
| card_mapping | Stabile ID (Hash aus FEN + Zug) → Anki-Note-ID, verhindert Duplikate | SQLite |
| Anki-Collection | Karteninhalte & komplettes Scheduling (SM-2/FSRS) | Anki selbst (`.anki2`), lokal auf dem Rechner |

**Warum SQLite statt Postgres:** Passt zu Option A (Zero-Config-Installation für andere Nutzer – kein zusätzlicher DB-Server nötig). Zugriff über ein ORM (`SQLAlchemy` oder `SQLModel`), damit ein späterer Wechsel auf Postgres (z. B. bei Option B/Hosting) nur eine geänderte Connection-String-Zeile ist, kein Rewrite.

## Dashboard-UI (grafisch)

| Komponente | Verantwortung | Technologie |
|---|---|---|
| Dashboard-API | Stellt Sync, Repertoire-Verwaltung und Statistiken als REST-Endpunkte bereit | FastAPI |
| Dashboard-UI | Grafische Oberfläche: Sync anstoßen, Repertoire pflegen, Statistiken & Repertoire-Baum ansehen | React (Vite) + Tailwind CSS, `Recharts` für Diagramme |

*Alternative mit weniger Kontextwechsel:* Falls ein separates React-Frontend zu viel JS-Aufwand ist, baut `Reflex` (reines Python, kompiliert zu einer modernen React-Oberfläche) dieselbe Funktionalität ohne eigenen JS-Code.

## Entfallene Komponenten (durch Anki ersetzt)

- Eigener SM-2-Scheduler
- Eigene Review-Session-UI mit Schachbrett-Widget
- Eigene `cards`-/`review_log`-Tabellen mit Scheduling-Feldern

## Packaging & Sharing (Open-Source-Tool)

Damit andere das Projekt selbst installieren und mit ihrem eigenen Anki nutzen können:

| Baustein | Zweck |
|---|---|
| `README.md` | Installationsschritte, Voraussetzungen (Python, Stockfish-Binary, Anki + AnkiConnect-Add-on), Quickstart |
| `config.yaml` / `.env` | Nutzerspezifisch: Lichess-/Chess.com-Username, Pfad zur Repertoire-PGN, Blunder-Schwellenwert, Stockfish-Pfad |
| `pyproject.toml` | Sauberes Packaging (`pip install -e .`), definierte Dependencies (`python-chess`, `requests`, etc.) |
| Anki-Note-Type-Vorlage | Mitgelieferte `.json`-Definition für das erwartete Kartenformat (Feld für Stellungsbild, Zug, Kontext), damit AnkiConnect-Client und Anki-Deck zusammenpassen |
| `examples/` | Beispiel-Repertoire-PGN, damit Neulinge das Tool direkt ausprobieren können, bevor sie ihr eigenes Repertoire hinterlegen |
| Lizenz (z. B. MIT) | Klarheit, dass/wie andere den Code nutzen und verändern dürfen |

## Gesamt-Tech-Stack

- Python 3.x
- `python-chess`
- Stockfish (lokale Binary)
- SQLite (Zugriff über `SQLAlchemy` oder `SQLModel`)
- `requests`
- AnkiConnect (Anki-Add-on – Anki muss lokal installiert und geöffnet sein)
- `APScheduler` für periodischen Sync
- `FastAPI` (Dashboard-Backend)
- React (Vite) + Tailwind CSS + `Recharts` (Dashboard-Frontend) – alternativ `Reflex` (reines Python)
- Alternative zu AnkiConnect: `genanki` für einmaligen `.apkg`-Export statt Live-Sync
