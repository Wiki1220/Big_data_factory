from __future__ import annotations

from pathlib import Path

import yaml

from .models import BuildPlan
from .utils import build_id


DEFAULT_STAGES = [
    "requested",
    "planned",
    "building",
    "verifying",
    "exporting",
    "published",
]


def load_spec(spec_path: str | Path) -> dict:
    path = Path(spec_path)
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def make_plan(spec_path: str | Path) -> BuildPlan:
    raw_spec = load_spec(spec_path)
    builder = raw_spec["target"]["builder"]
    nodes = raw_spec["cluster"]["nodes"]
    return BuildPlan(
        build_id=build_id(),
        spec_path=str(Path(spec_path)),
        builder=builder,
        node_count=len(nodes),
        stages=DEFAULT_STAGES,
        raw_spec=raw_spec,
    )
