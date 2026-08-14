"""Experimental knowledge memory for ForgeMind's intuition layer.

The knowledge base stores bounded experimental evidence.  It never represents
confidence as a probability of global truth: confidence is only support inside
the observed domain and cases recorded in the evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable

from .core import Hyp, canon, complexity, run


class MemoryType(str, Enum):
    DISCOVERED = "DISCOVERED"
    EQUIVALENCE = "EQUIVALENCE"
    FALSIFICATION = "FALSIFICATION"
    REWRITE_RULE = "REWRITE_RULE"


@dataclass
class KnowledgeRecord:
    memory_type: MemoryType
    hypothesis: tuple
    behavior_signature: tuple = ()
    complexity: float = 0.0
    evidence: float = 0.0
    counterexamples: list[Any] = field(default_factory=list)
    validated_cases: list[Any] = field(default_factory=list)
    rule: str | None = None
    confidence: float = 0.0
    provenance: dict[str, Any] = field(default_factory=dict)
    status: str = "EXPERIMENTAL"

    @property
    def program_key(self) -> tuple:
        return self.hypothesis


class KnowledgeBase:
    """Small deterministic store for bounded experimental knowledge."""

    def __init__(self, records: Iterable[KnowledgeRecord] | None = None):
        self.records: list[KnowledgeRecord] = list(records or [])

    @staticmethod
    def _program(program: Any) -> list:
        return list(program.p) if isinstance(program, Hyp) else list(program)

    @staticmethod
    def _signature(program: Any, probes: Iterable[Any] | None) -> tuple:
        if probes is None:
            return ()
        p = KnowledgeBase._program(program)
        return tuple(repr(run(p, probe)) for probe in probes)

    def remember_hypothesis(self, program: Any, *, probes=None, evidence=0.0,
                            validated_cases=None, counterexamples=None,
                            confidence=0.0, provenance=None, status="EXPERIMENTAL") -> KnowledgeRecord:
        p = self._program(program)
        record = KnowledgeRecord(
            MemoryType.DISCOVERED, canon(p), self._signature(p, probes),
            complexity(p), float(evidence), list(counterexamples or []),
            list(validated_cases or []), None, float(confidence),
            dict(provenance or {}), status,
        )
        return self._upsert(record)

    def remember_equivalence(self, left: Any, right: Any, *, probes=None,
                             evidence=0.0, provenance=None, status="BOUNDED") -> KnowledgeRecord:
        left_p, right_p = self._program(left), self._program(right)
        record = KnowledgeRecord(
            MemoryType.EQUIVALENCE, canon(left_p), self._signature(left_p, probes),
            complexity(left_p), float(evidence), [], list(probes or []),
            f"{canon(left_p)} == {canon(right_p)}", 1.0 if probes else 0.0,
            dict(provenance or {}), status,
        )
        record.provenance.setdefault("equivalent_to", canon(right_p))
        return self._upsert(record)

    def remember_falsification(self, program: Any, *, counterexample,
                               provenance=None) -> KnowledgeRecord:
        p = self._program(program)
        record = KnowledgeRecord(
            MemoryType.FALSIFICATION, canon(p), (), complexity(p), 0.0,
            [counterexample], [], None, 1.0,
            dict(provenance or {}), "FALSIFIED",
        )
        return self._upsert(record)

    def remember_rule(self, program: Any, *, rule: str, probes=None,
                      evidence=0.0, confidence=0.0, provenance=None,
                      status="EXPERIMENTAL") -> KnowledgeRecord:
        p = self._program(program)
        record = KnowledgeRecord(
            MemoryType.REWRITE_RULE, canon(p), self._signature(p, probes),
            complexity(p), float(evidence), [], list(probes or []), rule,
            float(confidence), dict(provenance or {}), status,
        )
        return self._upsert(record)

    def _upsert(self, record: KnowledgeRecord) -> KnowledgeRecord:
        for i, old in enumerate(self.records):
            if old.memory_type == record.memory_type and old.program_key == record.program_key and old.rule == record.rule:
                self.records[i] = record
                return record
        self.records.append(record)
        return record

    def similar(self, program: Any, limit: int = 5) -> list[KnowledgeRecord]:
        key = canon(self._program(program))
        def distance(record):
            a, b = key, record.hypothesis
            return abs(len(a) - len(b)) + sum(x != y for x, y in zip(a, b))
        return sorted(self.records, key=distance)[:limit]

    def related_rules(self, program: Any) -> list[KnowledgeRecord]:
        return [r for r in self.similar(program) if r.memory_type == MemoryType.REWRITE_RULE]

    def failed_patterns(self, program: Any | None = None) -> list[KnowledgeRecord]:
        failed = [r for r in self.records if r.memory_type == MemoryType.FALSIFICATION]
        if program is None:
            return failed
        key = canon(self._program(program))
        return [r for r in failed if r.hypothesis == key or any(part in key for part in r.hypothesis)]

    def survivors(self) -> list[KnowledgeRecord]:
        return [r for r in self.records if r.status not in {"FALSIFIED", "REJECTED"}]

    def suggest(self, program: Any, limit: int = 5) -> list[dict[str, Any]]:
        """Return explainable suggestions without claiming global truth."""
        similar = self.similar(program, limit=limit)
        return [{
            "type": record.memory_type.value,
            "program": record.hypothesis,
            "rule": record.rule,
            "confidence": record.confidence,
            "status": record.status,
            "reason": "bounded experimental similarity",
        } for record in similar]
