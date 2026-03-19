from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT_DIR / "state"
STATE_DB = STATE_DIR / "factory.db"
SCHEMA_FILE = STATE_DIR / "schema.sql"
