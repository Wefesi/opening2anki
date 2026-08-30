"""SQLModel definitions for the application."""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint


def utc_now_iso() -> str:
    """Return the current UTC timestamp formatted as ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


class Game(SQLModel, table=True):
    """Stores imported and synced chess games."""

    __tablename__ = "games"
    __table_args__ = (
        UniqueConstraint("external_id", "source", name="uq_game_external_source"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: Optional[str] = Field(default=None, index=True)
    source: str = Field(default="manual")  # lichess | chesscom | manual
    pgn: str
    my_color: str = Field(default="white")  # white | black
    result: Optional[str] = None  # 1-0 | 0-1 | 1/2-1/2 | *
    time_control: Optional[str] = None  # bullet | blitz | rapid | classical
    played_at: Optional[str] = None
    imported_at: str = Field(default_factory=utc_now_iso)
    processed: int = Field(default=0)  # 0 = pending, 1 = processed
    processed_at: Optional[str] = None

    cards: list["CardMapping"] = Relationship(back_populates="game")


class OpeningCache(SQLModel, table=True):
    """Caches theoretical master database responses per position FEN."""

    __tablename__ = "opening_cache"

    id: Optional[int] = Field(default=None, primary_key=True)
    fen: str = Field(unique=True, index=True)
    master_data_json: str  # JSON payload with book moves and master statistics
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)


class CardMapping(SQLModel, table=True):
    """Tracks generated Anki flashcards and maps them to Anki note IDs."""

    __tablename__ = "card_mapping"

    id: Optional[int] = Field(default=None, primary_key=True)
    card_hash: str = Field(unique=True, index=True)  # SHA256(fen + correct_move + card_type)
    card_type: str = Field(default="opening_deviation")
    anki_note_id: Optional[int] = Field(default=None, index=True)
    source_game_id: Optional[int] = Field(
        default=None, foreign_key="games.id", ondelete="SET NULL"
    )
    fen: str  # Pre-deviation board position FEN
    correct_move: str  # Best theoretical master / engine move
    played_move: str  # The inaccurate / bad deviation move played
    deviation_ply: Optional[int] = None  # Half-move number where deviation occurred
    centipawn_loss: Optional[int] = None  # Stockfish CP loss vs best move
    eval_before_cp: Optional[int] = None
    eval_after_cp: Optional[int] = None
    master_stats_json: Optional[str] = None  # Summary of master games for this position
    created_at: str = Field(default_factory=utc_now_iso)
    last_synced_at: Optional[str] = None

    game: Optional[Game] = Relationship(back_populates="cards")


class SyncState(SQLModel, table=True):
    """Tracks platform synchronization cursors."""

    __tablename__ = "sync_state"
    __table_args__ = (
        UniqueConstraint("source", "username", name="uq_sync_source_username"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    source: str  # lichess | chesscom
    username: str
    last_synced_at: Optional[str] = None
    last_game_external_id: Optional[str] = None
