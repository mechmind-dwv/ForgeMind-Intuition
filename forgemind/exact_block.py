"""Memory-bounded exact semantics for million-hypothesis comparisons."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

try:
    import numpy as np
except ModuleNotFoundError:  # NumPy is an optional dependency for the base package.
    np = None  # type: ignore[assignment]

ACTIVE = np.uint8(0) if np is not None else 0
ELIMINATED = np.uint8(2) if np is not None else 2


def _require_numpy():
    if np is None:
        raise ImportError("BlockExactHypothesisSet requires `pip install forgemind[vectorized]`")
    return np


@dataclass(frozen=True)
class BlockBelief:
    hypothesis_id: str
    posterior: float
    state: int
    evidence_count: int


class BlockExactHypothesisSet:
    """Exact log-space Bayes updates without one Python belief object per item.

    The class preserves the scalar engine's update semantics while storing only
    contiguous numeric state. IDs and explanations are optional sidecars; callers
    that already work with positions can omit them entirely.
    """

    def __init__(self, priors: np.ndarray, *, ids: Iterable[str] | None = None, block_size: int = 65_536, elimination_threshold: float = 0.02, min_evidence: int = 1) -> None:
        numpy = _require_numpy()
        values = numpy.asarray(priors, dtype=numpy.float64)
        if values.ndim != 1 or values.size == 0 or numpy.any(~numpy.isfinite(values)) or numpy.any(values < 0) or not numpy.any(values > 0):
            raise ValueError("priors must be a non-empty one-dimensional array with positive mass")
        if block_size < 1 or min_evidence < 1 or not 0.0 < elimination_threshold < 1.0:
            raise ValueError("invalid block_size, min_evidence, or elimination_threshold")
        if ids is not None and len(ids) != values.size:
            raise ValueError("ids must align with priors")
        self.block_size = int(block_size)
        self.elimination_threshold = float(elimination_threshold)
        self.min_evidence = int(min_evidence)
        self.ids = tuple(ids) if ids is not None else None
        self.priors = values.copy()
        self.log_weights = np.log(values)
        self.posteriors = np.zeros(values.size, dtype=np.float64)
        self.states = np.full(values.size, ACTIVE, dtype=np.uint8)
        self.evidence_counts = np.zeros(values.size, dtype=np.uint32)
        self.evidence_ids: set[str] = set()
        self.reasons: dict[int, list[str]] = {}
        self._normalize()

    def _logsumexp(self, values: np.ndarray) -> float:
        finite = values[np.isfinite(values)]
        if finite.size == 0:
            raise ValueError("posterior mass must be positive")
        pivot = float(np.max(finite))
        total = 0.0
        for start in range(0, finite.size, self.block_size):
            total += float(np.exp(finite[start : start + self.block_size] - pivot).sum())
        return pivot + float(np.log(total))

    def _normalize(self) -> None:
        active = self.states != ELIMINATED
        normalizer = self._logsumexp(self.log_weights[active])
        self.posteriors.fill(0.0)
        self.posteriors[active] = np.exp(self.log_weights[active] - normalizer)
        self.log_weights[active] -= normalizer

    def observe_arrays(self, likelihoods: np.ndarray, evidence_id: str, *, reason: str = "", hard_positions: Iterable[int] = ()) -> np.ndarray:
        if evidence_id in self.evidence_ids:
            raise ValueError(f"evidence_id already observed: {evidence_id}")
        values = np.asarray(likelihoods, dtype=np.float64)
        if values.ndim != 1 or values.size != self.posteriors.size or np.any(~np.isfinite(values)) or np.any(values < 0) or np.any(values > 1):
            raise ValueError("likelihoods must be a finite one-dimensional array aligned with priors")
        hard = np.asarray(tuple(hard_positions), dtype=np.intp)
        if np.any(hard < 0) or np.any(hard >= values.size):
            raise ValueError("hard_positions must refer to valid positions")
        active_positions = np.flatnonzero(self.states != ELIMINATED)
        for start in range(0, active_positions.size, self.block_size):
            positions = active_positions[start : start + self.block_size]
            likelihood_block = values[positions]
            positive = likelihood_block > 0
            updates = np.full(positions.size, -np.inf, dtype=np.float64)
            updates[positive] = np.log(likelihood_block[positive])
            self.log_weights[positions] += updates
            self.evidence_counts[positions] += 1
        if hard.size:
            self.states[hard] = ELIMINATED
            self.log_weights[hard] = -np.inf
        self._normalize()
        eligible = (self.states != ELIMINATED) & (self.evidence_counts >= self.min_evidence) & (self.posteriors < self.elimination_threshold)
        self.states[eligible] = ELIMINATED
        self.log_weights[eligible] = -np.inf
        if np.any(eligible):
            self._normalize()
        self.evidence_ids.add(evidence_id)
        if reason:
            for position in active_positions.tolist():
                self.reasons.setdefault(int(position), []).append(f"{evidence_id}: {reason}")
        return active_positions

    def top_k_positions(self, k: int) -> np.ndarray:
        if k < 1:
            raise ValueError("k must be positive")
        candidates = np.flatnonzero(self.states != ELIMINATED)
        if candidates.size == 0:
            return np.asarray([], dtype=np.intp)
        count = min(k, candidates.size)
        selected = candidates[np.argpartition(self.posteriors[candidates], -count)[-count:]]
        return selected[np.argsort(self.posteriors[selected])[::-1]]

    def top_k(self, k: int) -> list[BlockBelief]:
        positions = self.top_k_positions(k)
        return [BlockBelief(str(self.ids[position]) if self.ids is not None else str(position), float(self.posteriors[position]), int(self.states[position]), int(self.evidence_counts[position])) for position in positions]

    def memory_bytes(self) -> int:
        return int(sum(array.nbytes for array in (self.priors, self.log_weights, self.posteriors, self.states, self.evidence_counts)))
