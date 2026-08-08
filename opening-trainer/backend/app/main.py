"""FastAPI entrypoint for the opening trainer backend."""

from fastapi import FastAPI

app = FastAPI(title="opening-trainer", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
