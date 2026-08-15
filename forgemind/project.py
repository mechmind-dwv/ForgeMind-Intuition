"""Portable project contracts for using ForgeMind in coding workflows."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from .core import Node
from .knowledge import KnowledgeBase


PROJECT_SCHEMA_VERSION = "1.0"


class ProjectValidationError(ValueError):
    """Raised when an external project does not satisfy the input contract."""



def _node_from_dict(value: Any, *, path: str) -> Node:
    if not isinstance(value, Mapping):
        raise ProjectValidationError(f"{path} must be an object with name and optional arg")
    if "name" not in value or not str(value["name"]).strip():
        raise ProjectValidationError(f"{path}.name must be a non-empty string")
    return Node(str(value.get("kind", "U")), str(value["name"]), value.get("arg"))


@dataclass(frozen=True)
class CandidateInput:
    """One externally supplied program candidate with stable identity."""

    candidate_id: str
    description: str
    program: tuple[Node, ...]
    source: str = "external"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Any, *, index: int) -> "CandidateInput":
        path = f"candidates[{index}]"
        if isinstance(payload, list):
            candidate_id = f"candidate-{index + 1}"
            description = f"Imported candidate {index + 1}"
            program_payload = payload
            source = "legacy"
            metadata: Mapping[str, Any] = {}
        elif isinstance(payload, Mapping):
            candidate_id = str(payload.get("id", payload.get("candidate_id", f"candidate-{index + 1}"))).strip()
            description = str(payload.get("description", candidate_id)).strip()
            program_payload = payload.get("program", payload.get("nodes", []))
            source = str(payload.get("source", "external")).strip() or "external"
            metadata = payload.get("metadata", {})
            if not isinstance(metadata, Mapping):
                raise ProjectValidationError(f"{path}.metadata must be an object")
        else:
            raise ProjectValidationError(f"{path} must be a list or object")
        if not candidate_id:
            raise ProjectValidationError(f"{path}.id must be a non-empty string")
        if not description:
            raise ProjectValidationError(f"{path}.description must be a non-empty string")
        if not isinstance(program_payload, list) or not program_payload:
            raise ProjectValidationError(f"{path}.program must be a non-empty list")
        program = tuple(_node_from_dict(node, path=f"{path}.program[{node_index}]") for node_index, node in enumerate(program_payload))
        return cls(candidate_id, description, program, source, dict(metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.candidate_id,
            "description": self.description,
            "program": [{"kind": node.kind, "name": node.name, "arg": node.arg} for node in self.program],
            "source": self.source,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ProjectInput:
    """Validated, portable input contract accepted from an external project."""

    name: str
    candidates: tuple[CandidateInput, ...]
    probes: tuple[tuple[int, ...], ...] = ()
    targets: tuple[Any, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = PROJECT_SCHEMA_VERSION

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ProjectInput":
        if not isinstance(payload, Mapping):
            raise ProjectValidationError("project payload must be an object")
        name = str(payload.get("name", "untitled")).strip()
        if not name:
            raise ProjectValidationError("name must be a non-empty string")
        schema_version = str(payload.get("schema_version", PROJECT_SCHEMA_VERSION))
        if schema_version != PROJECT_SCHEMA_VERSION:
            raise ProjectValidationError(f"unsupported schema_version: {schema_version}")
        candidates_payload = payload.get("candidates", [])
        if not isinstance(candidates_payload, list) or not candidates_payload:
            raise ProjectValidationError("candidates must be a non-empty list")
        candidates = tuple(CandidateInput.from_dict(item, index=index) for index, item in enumerate(candidates_payload))
        candidate_ids = [item.candidate_id for item in candidates]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ProjectValidationError("candidate ids must be unique")
        probes_payload = payload.get("probes", [])
        if not isinstance(probes_payload, list):
            raise ProjectValidationError("probes must be a list")
        probes: list[tuple[int, ...]] = []
        for index, probe in enumerate(probes_payload):
            if not isinstance(probe, list) or not probe:
                raise ProjectValidationError(f"probes[{index}] must be a non-empty list")
            try:
                probes.append(tuple(int(value) for value in probe))
            except (TypeError, ValueError) as error:
                raise ProjectValidationError(f"probes[{index}] must contain integers") from error
        targets_payload = payload.get("targets", [])
        if not isinstance(targets_payload, list):
            raise ProjectValidationError("targets must be a list")
        metadata = payload.get("metadata", {})
        if not isinstance(metadata, Mapping):
            raise ProjectValidationError("metadata must be an object")
        return cls(name, candidates, tuple(probes), tuple(targets_payload), dict(metadata), schema_version)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "name": self.name,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "probes": [list(probe) for probe in self.probes],
            "targets": list(self.targets),
            "metadata": dict(self.metadata),
        }


@dataclass
class ForgeMindProject:
    """Serializable project contract shared by the CLI and future frontend."""

    name: str = "untitled"
    candidates: list[list[Node]] = field(default_factory=list)
    probes: list[list[int]] = field(default_factory=list)
    knowledge: list[dict[str, Any]] = field(default_factory=list)
    targets: list[Any] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    candidate_specs: list[CandidateInput] = field(default_factory=list)
    schema_version: str = PROJECT_SCHEMA_VERSION

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ForgeMindProject":
        project_input = ProjectInput.from_dict(payload)
        knowledge = payload.get("knowledge", [])
        if not isinstance(knowledge, list):
            raise ProjectValidationError("knowledge must be a list")
        return cls(
            name=project_input.name,
            candidates=[list(candidate.program) for candidate in project_input.candidates],
            probes=[list(probe) for probe in project_input.probes],
            knowledge=list(knowledge),
            targets=list(project_input.targets),
            metadata=dict(project_input.metadata),
            candidate_specs=list(project_input.candidates),
            schema_version=project_input.schema_version,
        )

    @classmethod
    def load(cls, path: str | Path) -> "ForgeMindProject":
        file_path = Path(path)
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ProjectValidationError(f"cannot read project {file_path}: {error}") from error
        try:
            return cls.from_dict(payload)
        except ProjectValidationError as error:
            raise ProjectValidationError(f"invalid project {file_path}: {error}") from error

    def to_dict(self) -> dict[str, Any]:
        specs = self.candidate_specs or [
            CandidateInput(f"candidate-{index + 1}", f"Candidate {index + 1}", tuple(program), "local")
            for index, program in enumerate(self.candidates)
        ]
        return {
            "schema_version": self.schema_version,
            "name": self.name,
            "candidates": [candidate.to_dict() for candidate in specs],
            "probes": self.probes,
            "targets": self.targets,
            "metadata": self.metadata,
            "knowledge": self.knowledge,
        }

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")

    def as_input(self) -> ProjectInput:
        return ProjectInput(
            name=self.name,
            candidates=tuple(self.candidate_specs or [CandidateInput(f"candidate-{index + 1}", f"Candidate {index + 1}", tuple(program), "local") for index, program in enumerate(self.candidates)]),
            probes=tuple(tuple(probe) for probe in self.probes),
            targets=tuple(self.targets),
            metadata=self.metadata,
            schema_version=self.schema_version,
        )

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
    candidates = [
        [Node("U", "rev"), Node("U", "sort"), Node("U", "neg"), Node("U", "rev")],
        [Node("U", "neg"), Node("U", "rev"), Node("U", "abs")],
        [Node("U", "sort"), Node("U", "sort")],
    ]
    specs = [
        CandidateInput("candidate-1", "reverse, sort, negate, reverse", tuple(candidates[0]), "example"),
        CandidateInput("candidate-2", "negate, reverse, absolute value", tuple(candidates[1]), "example"),
        CandidateInput("candidate-3", "sort composed with sort", tuple(candidates[2]), "example"),
    ]
    return ForgeMindProject(
        name="intuition-playground",
        candidates=candidates,
        candidate_specs=specs,
        probes=[[-5, -2, 0, 3, 7], [3, 1, 2], [9, -4, 2, 6]],
        targets=[],
        knowledge=[{"type": "rule", "program": [{"kind": "U", "name": "sort"}, {"kind": "U", "name": "sort"}], "rule": "sort(sort(x)) = sort(x)", "confidence": 0.8}],
    )


__all__ = [
    "CandidateInput",
    "ForgeMindProject",
    "PROJECT_SCHEMA_VERSION",
    "ProjectInput",
    "ProjectValidationError",
    "example_project",
]
