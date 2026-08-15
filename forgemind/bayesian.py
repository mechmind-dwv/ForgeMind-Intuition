"""Bayesian belief updates and explainable hypothesis elimination.

The hot path stores weights in log space. Public snapshots expose normal
posteriors and explicit decision provenance so callers can distinguish belief,
uncertainty, parking and hard falsification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from heapq import nlargest
from math import exp, isfinite, log
from typing import Any, Mapping


class HypothesisState(str, Enum):
    ACTIVE = "active"
    UNCERTAIN = "uncertain"
    PARKED = "parked"
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
        if not self.description.strip():
            raise ValueError("description must not be empty")
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
        if not self.hypothesis_id.strip():
            raise ValueError("hypothesis_id must not be empty")
        if not self.description.strip():
            raise ValueError("description must not be empty")
        if not isfinite(self.prior) or self.prior < 0.0:
            raise ValueError("prior must be a finite non-negative weight")
        if not isfinite(self.posterior) or self.posterior < 0.0:
            raise ValueError("posterior must be a finite non-negative weight")
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
    state: HypothesisState = HypothesisState.ACTIVE
    reversible: bool = True
    reason_code: str = "none"

    def as_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "eliminated": self.eliminated,
            "posterior": round(self.posterior, 8),
            "threshold": self.threshold,
            "reason": self.reason,
            "evidence_ids": list(self.evidence_ids),
            "state": self.state.value,
            "reversible": self.reversible,
            "reason_code": self.reason_code,
        }


class BayesianHypothesisSet:
    """Normalized belief distribution with stable log-space updates.

    A low posterior without enough evidence becomes ``UNCERTAIN`` rather than
    being removed. ``PARKED`` is a reversible, caller-controlled state for a
    hypothesis that should be hidden from the default top-k view. A hard oracle
    falsification is irreversible within this set and becomes ``ELIMINATED``.
    """

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

    def top_k(self, k: int, *, include_eliminated: bool = False, include_parked: bool = False) -> list[HypothesisBelief]:
        """Return the k highest posterior beliefs without a full sort."""
        if k < 1:
            raise ValueError("k must be positive")
        candidates = self._beliefs.values() if include_eliminated else (
            belief for belief in self._beliefs.values()
            if belief.state != HypothesisState.ELIMINATED and (include_parked or belief.state != HypothesisState.PARKED)
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
            if belief.state == HypothesisState.ELIMINATED:
                reason = belief.reasons[-1] if belief.reasons else "hard falsification"
                decisions.append(self._decision(belief, False, reason, "hard_falsification", reversible=False))
                continue
            if belief.state == HypothesisState.PARKED:
                reason = belief.reasons[-1] if belief.reasons else "parked by caller"
                decisions.append(self._decision(belief, False, reason, "parked", reversible=True))
                continue
            if belief.posterior < self.elimination_threshold and enough_evidence:
                belief.state = HypothesisState.ELIMINATED
                reason = f"posterior {belief.posterior:.4f} below elimination threshold {self.elimination_threshold:.4f} after {len(belief.evidence_ids)} evidence items"
                belief.reasons.append(reason)
                decisions.append(self._decision(belief, True, reason, "posterior_below_threshold", reversible=False))
            elif belief.posterior < self.elimination_threshold:
                belief.state = HypothesisState.UNCERTAIN
                reason = f"posterior {belief.posterior:.4f} below threshold; awaiting {self.min_evidence - len(belief.evidence_ids)} more evidence item(s)"
                if not belief.reasons or belief.reasons[-1] != reason:
                    belief.reasons.append(reason)
                decisions.append(self._decision(belief, False, reason, "insufficient_evidence", reversible=True))
            else:
                belief.state = HypothesisState.SURVIVOR
                reason = f"posterior {belief.posterior:.4f} meets threshold {self.elimination_threshold:.4f}"
                decisions.append(self._decision(belief, False, reason, "survives_threshold", reversible=True))
        return decisions

    def eliminate_hypothesis(self, hypothesis_id: str, *, reason: str, evidence_ids: tuple[str, ...] = (), threshold: float | None = None, reversible: bool = False) -> EliminationDecision:
        """Apply an explicit caller decision while preserving provenance."""
        belief = self._beliefs.get(hypothesis_id)
        if belief is None:
            raise KeyError(f"unknown hypothesis_id: {hypothesis_id}")
        if not reason.strip():
            raise ValueError("reason must not be empty")
        belief.state = HypothesisState.ELIMINATED
        belief.log_weight = float("-inf")
        belief.reasons.append(reason)
        belief.evidence_ids.extend(item for item in evidence_ids if item not in belief.evidence_ids)
        self._normalize()
        return self._decision(belief, True, reason, "explicit", reversible=reversible, threshold=threshold)

    def park(self, hypothesis_id: str, *, reason: str) -> EliminationDecision:
        """Park a hypothesis without treating it as falsified."""
        belief = self._beliefs.get(hypothesis_id)
        if belief is None:
            raise KeyError(f"unknown hypothesis_id: {hypothesis_id}")
        if belief.state == HypothesisState.ELIMINATED:
            raise ValueError("an eliminated hypothesis cannot be parked")
        if not reason.strip():
            raise ValueError("reason must not be empty")
        belief.state = HypothesisState.PARKED
        belief.reasons.append(reason)
        return self._decision(belief, False, reason, "parked", reversible=True)

    def unpark(self, hypothesis_id: str) -> HypothesisBelief:
        """Reactivate a parked hypothesis as uncertain for further evidence."""
        belief = self._beliefs.get(hypothesis_id)
        if belief is None:
            raise KeyError(f"unknown hypothesis_id: {hypothesis_id}")
        if belief.state != HypothesisState.PARKED:
            raise ValueError("only parked hypotheses can be unparked")
        belief.state = HypothesisState.UNCERTAIN
        belief.reasons.append("reactivated from parked state")
        return belief

    def _decision(self, belief: HypothesisBelief, eliminated: bool, reason: str, reason_code: str, *, reversible: bool, threshold: float | None = None) -> EliminationDecision:
        return EliminationDecision(
            hypothesis_id=belief.hypothesis_id,
            eliminated=eliminated,
            posterior=belief.posterior,
            threshold=self.elimination_threshold if threshold is None else threshold,
            reason=reason,
            evidence_ids=tuple(belief.evidence_ids),
            state=belief.state,
            reversible=reversible,
            reason_code=reason_code,
        )

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
