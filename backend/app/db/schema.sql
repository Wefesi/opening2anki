-- Reference schema for the application database (SQLite).
-- Foreign keys must be enabled at connection time: PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT,
    source TEXT NOT NULL DEFAULT 'manual',
    pgn TEXT NOT NULL,
    my_color TEXT NOT NULL DEFAULT 'white',
    result TEXT,
    time_control TEXT,
    played_at TEXT,
    imported_at TEXT NOT NULL,
    processed INTEGER NOT NULL DEFAULT 0,
    processed_at TEXT,
    CONSTRAINT uq_game_external_source UNIQUE (external_id, source)
);

CREATE TABLE IF NOT EXISTS opening_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fen TEXT NOT NULL UNIQUE,
    master_data_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS card_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_hash TEXT NOT NULL UNIQUE,
    card_type TEXT NOT NULL DEFAULT 'opening_deviation',
    anki_note_id INTEGER,
    source_game_id INTEGER REFERENCES games(id) ON DELETE SET NULL,
    fen TEXT NOT NULL,
    correct_move TEXT NOT NULL,
    played_move TEXT NOT NULL,
    deviation_ply INTEGER,
    centipawn_loss INTEGER,
    eval_before_cp INTEGER,
    eval_after_cp INTEGER,
    master_stats_json TEXT,
    created_at TEXT NOT NULL,
    last_synced_at TEXT
);

CREATE TABLE IF NOT EXISTS sync_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    username TEXT NOT NULL,
    last_synced_at TEXT,
    last_game_external_id TEXT,
    CONSTRAINT uq_sync_source_username UNIQUE (source, username)
);

-- Indexes for fast query execution
CREATE INDEX IF NOT EXISTS idx_games_source_processed ON games(source, processed);
CREATE INDEX IF NOT EXISTS idx_opening_cache_fen ON opening_cache(fen);
CREATE INDEX IF NOT EXISTS idx_card_mapping_hash ON card_mapping(card_hash);
CREATE INDEX IF NOT EXISTS idx_card_mapping_game ON card_mapping(source_game_id);

