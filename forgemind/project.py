"""Project files for using ForgeMind in real coding workflows."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .core import Node
from .knowledge import KnowledgeBase


@dataclass
class ForgeMindProject:
    """Serializable project contract shared by the CLI and future frontend."""

    name: str = "untitled"
    candidates: list[list[Node]] = field(default_factory=list)
    probes: list[list[int]] = field(default_factory=list)
    knowledge: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ForgeMindProject":
        candidates = []
        for program in payload.get("candidates", []):
            candidates.append([
                Node(str(node.get("kind", "U")), str(node["name"]), node.get("arg"))
                for node in program
            ])
        return cls(
            name=str(payload.get("name", "untitled")),
            candidates=candidates,
            probes=[list(map(int, probe)) for probe in payload.get("probes", [])],
            knowledge=list(payload.get("knowledge", [])),
        )

    @classmethod
    def load(cls, path: str | Path) -> "ForgeMindProject":
        file_path = Path(path)
        return cls.from_dict(json.loads(file_path.read_text(encoding="utf-8")))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "candidates": [[
                {"kind": node.kind, "name": node.name, "arg": node.arg}
                for node in program
            ] for program in self.candidates],
            "probes": self.probes,
            "knowledge": self.knowledge,
        }

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")

    def knowledge_base(self) -> KnowledgeBase:
        kb = KnowledgeBase()
        for item in self.knowledge:
            kind = item.get("type", "hypothesis")
            program = [Node(str(node.get("kind", "U")), str(node["name"]), node.get("arg")) for node in item.get("program", [])]
            if kind == "rule":
                kb.remember_rule(program, rule=str(item.get("rule", "")), probes=self.probes, confidence=float(item.get("confidence", 0.0)))
            elif kind == "falsification":
                kb.remember_falsification(program, counterexample=item.get("counterexample"))
            else:
                kb.remember_hypothesis(program, probes=self.probes, confidence=float(item.get("confidence", 0.0)))
        return kb


def example_project() -> ForgeMindProject:
    return ForgeMindProject(
        name="intuition-playground",
        candidates=[
            [Node("U", "rev"), Node("U", "sort"), Node("U", "neg"), Node("U", "rev")],
            [Node("U", "neg"), Node("U", "rev"), Node("U", "abs")],
            [Node("U", "sort"), Node("U", "sort")],
        ],
        probes=[[-5, -2, 0, 3, 7], [3, 1, 2], [9, -4, 2, 6]],
        knowledge=[{"type": "rule", "program": [{"kind": "U", "name": "sort"}, {"kind": "U", "name": "sort"}], "rule": "sort(sort(x)) = sort(x)", "confidence": 0.8}],
    )
