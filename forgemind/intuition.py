"""Explainable, non-ML intuition scoring for candidate programs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .core import Hyp, canon, complexity
from .knowledge import KnowledgeBase, MemoryType


@dataclass(frozen=True)
class IntuitionScore:
    total: float
    novelty: float
    structural_similarity: float
    compression: float
    falsification_value: float
    compositional_value: float
    complexity_penalty: float
    historical_failure: float = 0.0
    reasons: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "novelty": self.novelty,
            "structural_similarity": self.structural_similarity,
            "compression": self.compression,
            "falsification_value": self.falsification_value,
            "compositional_value": self.compositional_value,
            "complexity_penalty": self.complexity_penalty,
            "historical_failure": self.historical_failure,
            "reasons": list(self.reasons),
        }


def _program(candidate):
    return list(candidate.p) if isinstance(candidate, Hyp) else list(candidate)


def intuition_score(candidate, *, knowledge_base: KnowledgeBase) -> IntuitionScore:
    p = _program(candidate)
    key = canon(p)
    similar = knowledge_base.similar(p, limit=5)
    survivors = knowledge_base.survivors()
    failed = knowledge_base.failed_patterns(p)

    exact_match = any(r.hypothesis == key for r in similar)
    structural_similarity = min(1.0, sum(r.confidence for r in similar) / max(1, len(similar)))
    novelty = 0.15 if exact_match else min(1.0, 0.35 + 0.08 * len(key))
    compression = min(1.0, 1.0 / max(1.0, complexity(p) / 2.0))
    compositional_value = min(1.0, len({part[1] for part in key}) / 3.0) if key else 0.0
    falsification_value = min(1.0, 0.25 + 0.1 * len(survivors))
    historical_failure = min(1.0, len(failed) / 3.0)
    complexity_penalty = min(1.0, complexity(p) / 8.0)

    total = (
        novelty + structural_similarity + compression + falsification_value
        + compositional_value - complexity_penalty - historical_failure
    )
    reasons = []
    if similar:
        reasons.append("structurally similar to recorded hypotheses")
    if any(r.memory_type == MemoryType.REWRITE_RULE for r in similar):
        reasons.append("matches a reusable rewrite-rule family")
    if compression >= 0.7:
        reasons.append("high compression potential")
    if failed:
        reasons.append("contains a historically falsified pattern")
    reasons.append("score is experimental evidence, not truth probability")

    return IntuitionScore(
        round(total, 6), round(novelty, 6), round(structural_similarity, 6),
        round(compression, 6), round(falsification_value, 6),
        round(compositional_value, 6), round(complexity_penalty, 6),
        round(historical_failure, 6), tuple(reasons),
    )
