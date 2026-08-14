"""Command-line interface for ForgeMind Intuition."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .advisor import advise
from .intuition import intuition_score
from .project import ForgeMindProject, example_project


def _project_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forgemind", description="Explainable experimental intuition for coding agents.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create a reproducible example project file.")
    init.add_argument("path", nargs="?", default="forgemind.project.json")

    for name, help_text in (("score", "Score every candidate in a project."), ("advise", "Recommend which candidate to test first.")):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("project", help="Path to a ForgeMind project JSON file.")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "init":
        path = Path(args.path).expanduser()
        example_project().save(path)
        print(f"created {path}")
        return 0

    project = ForgeMindProject.load(_project_path(args.project))
    kb = project.knowledge_base()
    if args.command == "score":
        payload = []
        for index, candidate in enumerate(project.candidates):
            payload.append({"candidate_index": index, "intuition": intuition_score(candidate, knowledge_base=kb).as_dict()})
    else:
        payload = [item.as_dict() for item in advise(project.candidates, knowledge_base=kb)]
    print(json.dumps({"project": project.name, "command": args.command, "results": payload}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
