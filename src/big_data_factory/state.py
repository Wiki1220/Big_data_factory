from __future__ import annotations

import sqlite3
from pathlib import Path

from .config import SCHEMA_FILE, STATE_DB, STATE_DIR


def ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def init_db(db_path: Path = STATE_DB) -> Path:
    ensure_state_dir()
    schema = SCHEMA_FILE.read_text(encoding="utf-8")
    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema)
        conn.commit()
    return db_path
