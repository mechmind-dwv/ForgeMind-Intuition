"""Bayesian belief updates and explainable hypothesis elimination.

The hot path stores weights in log space. Public snapshots still expose normal
posteriors so existing callers remain compatible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from heapq import nlargest
from math import exp, isfinite, log
from typing import Any, Mapping


class HypothesisState(str, Enum):
    ACTIVE = "active"
    SURVIVOR = "survivor"
    ELIMINATED = "eliminated"


@dataclass(frozen=True)
class EvidenceObservation:
    """One observation with likelihoods P(E|H) for each hypothesis."""

    evidence_id: str
    description: str
    likelihoods: Mapping[str, float]
    source: str = "oracle"
    hard_falsification: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not self.evidence_id.strip():
            raise ValueError("evidence_id must not be empty")
        if not self.likelihoods:
            raise ValueError("likelihoods must not be empty")
        if any(not 0.0 <= value <= 1.0 for value in self.likelihoods.values()):
            raise ValueError("likelihoods must be between 0 and 1")


@dataclass
class HypothesisBelief:
    hypothesis_id: str
    description: str
    prior: float
    posterior: float
    state: HypothesisState = HypothesisState.ACTIVE
    evidence_ids: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    log_weight: float | None = None

    def __post_init__(self) -> None:
        if self.log_weight is None:
            self.log_weight = log(self.posterior) if self.posterior > 0.0 else float("-inf")

    def as_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "description": self.description,
            "prior": round(self.prior, 8),
            "posterior": round(self.posterior, 8),
            "state": self.state.value,
            "evidence_ids": list(self.evidence_ids),
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class EliminationDecision:
    hypothesis_id: str
    eliminated: bool
    posterior: float
    threshold: float
    reason: str
    evidence_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "eliminated": self.eliminated,
            "posterior": round(self.posterior, 8),
            "threshold": self.threshold,
            "reason": self.reason,
            "evidence_ids": list(self.evidence_ids),
        }


class BayesianHypothesisSet:
    """Normalized belief distribution with stable log-space updates."""

    def __init__(self, beliefs: list[HypothesisBelief], *, elimination_threshold: float = 0.02, min_evidence: int = 1) -> None:
        if not beliefs:
            raise ValueError("at least one hypothesis is required")
        if not 0.0 < elimination_threshold < 1.0:
            raise ValueError("elimination_threshold must be between 0 and 1")
        if min_evidence < 1:
            raise ValueError("min_evidence must be positive")
        self.elimination_threshold = elimination_threshold
        self.min_evidence = min_evidence
        self._beliefs = {belief.hypothesis_id: belief for belief in beliefs}
        if len(self._beliefs) != len(beliefs):
            raise ValueError("hypothesis ids must be unique")
        self._seen_evidence_ids: set[str] = set()
        self._normalize()

    @classmethod
    def from_priors(cls, hypotheses: Mapping[str, str], priors: Mapping[str, float] | None = None, **kwargs: Any) -> "BayesianHypothesisSet":
        priors = priors or {key: 1.0 for key in hypotheses}
        if set(hypotheses) != set(priors):
            raise ValueError("hypotheses and priors must contain the same ids")
        beliefs = [HypothesisBelief(key, hypotheses[key], float(priors[key]), float(priors[key])) for key in hypotheses]
        return cls(beliefs, **kwargs)

    @staticmethod
    def _logsumexp(values: list[float]) -> float:
        finite = [value for value in values if isfinite(value)]
        if not finite:
            raise ValueError("posterior mass must be positive")
        pivot = max(finite)
        return pivot + log(sum(exp(value - pivot) for value in finite))

    def _normalize(self) -> None:
        active = [belief for belief in self._beliefs.values() if belief.state != HypothesisState.ELIMINATED]
        normalizer = self._logsumexp([belief.log_weight if belief.log_weight is not None else float("-inf") for belief in active])
        for belief in self._beliefs.values():
            if belief.state == HypothesisState.ELIMINATED:
                belief.posterior = 0.0
                belief.log_weight = float("-inf")
            else:
                belief.log_weight = (belief.log_weight if belief.log_weight is not None else float("-inf")) - normalizer
                belief.posterior = exp(belief.log_weight)

    def beliefs(self) -> tuple[HypothesisBelief, ...]:
        return tuple(self._beliefs.values())

    def top_k(self, k: int, *, include_eliminated: bool = False) -> list[HypothesisBelief]:
        """Return the k highest posterior beliefs without a full sort."""
        if k < 1:
            raise ValueError("k must be positive")
        candidates = self._beliefs.values() if include_eliminated else (
            belief for belief in self._beliefs.values() if belief.state != HypothesisState.ELIMINATED
        )
        return nlargest(k, candidates, key=lambda belief: belief.posterior)

    def ranked(self) -> list[HypothesisBelief]:
        """Return all beliefs in descending posterior order for compatibility."""
        return sorted(self._beliefs.values(), key=lambda belief: belief.posterior, reverse=True)

    def observe(self, observation: EvidenceObservation) -> list[EliminationDecision]:
        """Apply Bayes' rule in log space and eliminate conservatively."""
        if observation.evidence_id in self._seen_evidence_ids:
            raise ValueError(f"evidence_id already observed: {observation.evidence_id}")
        self._seen_evidence_ids.add(observation.evidence_id)
        for hypothesis_id, belief in self._beliefs.items():
            if belief.state == HypothesisState.ELIMINATED:
                continue
            likelihood = float(observation.likelihoods.get(hypothesis_id, 1.0))
            belief.log_weight = (belief.log_weight if belief.log_weight is not None else float("-inf")) + (log(likelihood) if likelihood > 0.0 else float("-inf"))
            belief.evidence_ids.append(observation.evidence_id)
            belief.reasons.append(f"{observation.evidence_id}: P(E|H)={likelihood:.3f} from {observation.source}")
            if hypothesis_id in observation.hard_falsification:
                belief.log_weight = float("-inf")
                belief.state = HypothesisState.ELIMINATED
                belief.reasons.append("hard falsification supplied by an oracle")
        self._normalize()
        return self.eliminate()

    def eliminate(self) -> list[EliminationDecision]:
        decisions: list[EliminationDecision] = []
        for belief in self._beliefs.values():
            enough_evidence = len(belief.evidence_ids) >= self.min_evidence
            should_eliminate = belief.state != HypothesisState.ELIMINATED and enough_evidence and belief.posterior < self.elimination_threshold
            if should_eliminate:
                belief.state = HypothesisState.ELIMINATED
                belief.reasons.append(f"posterior {belief.posterior:.4f} below elimination threshold {self.elimination_threshold:.4f}")
            elif belief.state != HypothesisState.ELIMINATED:
                belief.state = HypothesisState.SURVIVOR if belief.posterior >= self.elimination_threshold else HypothesisState.ACTIVE
            decisions.append(EliminationDecision(belief.hypothesis_id, should_eliminate, belief.posterior, self.elimination_threshold, belief.reasons[-1] if belief.reasons else "no elimination", tuple(belief.evidence_ids)))
        return decisions

    def snapshot(self) -> dict[str, Any]:
        return {
            "elimination_threshold": self.elimination_threshold,
            "min_evidence": self.min_evidence,
            "beliefs": [belief.as_dict() for belief in self.ranked()],
        }

    def posterior_sum(self) -> float:
        return sum(belief.posterior for belief in self._beliefs.values())


__all__ = [
    "BayesianHypothesisSet",
    "EliminationDecision",
    "EvidenceObservation",
    "HypothesisBelief",
    "HypothesisState",
]
