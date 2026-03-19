from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class BuildPlan:
    build_id: str
    spec_path: str
    builder: str
    node_count: int
    stages: list[str]
    raw_spec: dict[str, Any]
