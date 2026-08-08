"""SQLModel definitions for the application."""

from sqlmodel import SQLModel


class Game(SQLModel, table=True):
    id: int | None = None
    source: str | None = None
