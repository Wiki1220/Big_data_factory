from __future__ import annotations

import argparse
import json

from .actions import describe_actions
from .state import init_db


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="big-data-factory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-state", help="Initialize lifecycle database.")
    subparsers.add_parser("describe-actions", help="Print action contracts for AI consumption.")

    plan_parser = subparsers.add_parser("plan", help="Generate a build plan from spec.")
    plan_parser.add_argument("--spec", required=True, help="Path to cluster spec YAML.")
    return parser


def handle_init_state() -> int:
    db_path = init_db()
    print(f"Initialized state database: {db_path}")
    return 0


def handle_plan(spec: str) -> int:
    try:
        from .planner import make_plan
    except ModuleNotFoundError as exc:
        if exc.name == "yaml":
            print("Missing dependency: PyYAML. Run `pip install -e .` first.")
            return 1
        raise

    plan = make_plan(spec)
    payload = {
        "build_id": plan.build_id,
        "spec_path": plan.spec_path,
        "builder": plan.builder,
        "node_count": plan.node_count,
        "stages": plan.stages,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def handle_describe_actions() -> int:
    print(json.dumps(describe_actions(), indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init-state":
        return handle_init_state()
    if args.command == "describe-actions":
        return handle_describe_actions()
    if args.command == "plan":
        return handle_plan(args.spec)
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
