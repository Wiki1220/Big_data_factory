from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_id() -> str:
    return f"build-{uuid4().hex[:12]}"
