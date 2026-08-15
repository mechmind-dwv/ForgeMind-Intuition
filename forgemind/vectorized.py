"""Compact NumPy-backed hypothesis storage for large ForgeMind searches.

Numeric state lives in contiguous arrays. Text descriptions and explanations stay
in sidecar dictionaries so the hot path avoids one Python object per hypothesis.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log
from typing import Iterable, Mapping

try:
    import numpy as np
except ImportError as error:  # pragma: no cover - exercised only without optional extra
    raise ImportError("VectorizedStore requires `pip install forgemind[vectorized]`") from error


ACTIVE = np.uint8(0)
SURVIVOR = np.uint8(1)
ELIMINATED = np.uint8(2)


@dataclass(frozen=True)
class VectorizedBelief:
    hypothesis_id: str
    description: str
    prior: float
    posterior: float
    log_weight: float
    state: int
    evidence_count: int


class VectorizedHypothesisStore:
    """Dense numeric belief state with sparse explanation metadata."""

    def __init__(self, hypotheses: Mapping[str, str], priors: Mapping[str, float] | None = None, *, families: Mapping[str, str] | None = None, elimination_threshold: float = 0.02, min_evidence: int = 1) -> None:
        if not hypotheses:
            raise ValueError("at least one hypothesis is required")
        if not 0.0 < elimination_threshold < 1.0:
            raise ValueError("elimination_threshold must be between 0 and 1")
        if min_evidence < 1:
            raise ValueError("min_evidence must be positive")
        self.ids = tuple(hypotheses)
        self.index = {hypothesis_id: index for index, hypothesis_id in enumerate(self.ids)}
        self.descriptions = dict(hypotheses)
        self.family_by_id = {hypothesis_id: (families or {}).get(hypothesis_id, "default") for hypothesis_id in self.ids}
        if families is not None and set(families) != set(hypotheses):
            raise ValueError("families and hypotheses must contain the same ids")
        if any(not family.strip() for family in self.family_by_id.values()):
            raise ValueError("family names must not be empty")
        self.family_positions: dict[str, np.ndarray] = {}
        for family in dict.fromkeys(self.family_by_id.values()):
            self.family_positions[family] = np.asarray([self.index[hypothesis_id] for hypothesis_id in self.ids if self.family_by_id[hypothesis_id] == family], dtype=np.intp)
        raw_priors = np.asarray([float((priors or {}).get(hypothesis_id, 1.0)) for hypothesis_id in self.ids], dtype=np.float64)
        if priors is not None and set(priors) != set(hypotheses):
            raise ValueError("hypotheses and priors must contain the same ids")
        if np.any(raw_priors < 0) or not np.any(raw_priors > 0):
            raise ValueError("priors must contain positive mass")
        self.priors = raw_priors
        self.log_weights = np.log(raw_priors)
        self.posteriors = np.zeros(len(self.ids), dtype=np.float64)
        self.states = np.full(len(self.ids), ACTIVE, dtype=np.uint8)
        self.evidence_counts = np.zeros(len(self.ids), dtype=np.uint32)
        self.elimination_threshold = float(elimination_threshold)
        self.min_evidence = int(min_evidence)
        self.explanations: dict[int, list[str]] = {}
        self.evidence_ids: set[str] = set()
        self.last_update_count = 0
        self.last_update_families: tuple[str, ...] = ()
        self._normalize()

    @staticmethod
    def _logsumexp(values: np.ndarray) -> float:
        finite = values[np.isfinite(values)]
        if finite.size == 0:
            raise ValueError("posterior mass must be positive")
        pivot = np.max(finite)
        return float(pivot + np.log(np.exp(finite - pivot).sum()))

    def _normalize(self) -> None:
        active = self.states != ELIMINATED
        normalizer = self._logsumexp(self.log_weights[active])
        self.posteriors.fill(0.0)
        self.posteriors[active] = np.exp(self.log_weights[active] - normalizer)
        self.log_weights[active] -= normalizer

    def _apply_numeric_update(self, positions: np.ndarray, values: np.ndarray, hard_positions: np.ndarray) -> np.ndarray:
        """Mutate only contiguous numeric arrays; return active positions touched."""
        active_mask = self.states[positions] != ELIMINATED
        active_positions = positions[active_mask]
        active_values = values[active_mask]
        self.last_update_count = int(active_positions.size)
        log_values = np.full(active_values.shape, -np.inf, dtype=np.float64)
        positive = active_values > 0
        log_values[positive] = np.log(active_values[positive])
        self.log_weights[active_positions] += log_values
        self.evidence_counts[active_positions] += 1
        if hard_positions.size:
            self.states[hard_positions] = ELIMINATED
            self.log_weights[hard_positions] = -np.inf
        self._normalize()
        eligible = (self.states != ELIMINATED) & (self.evidence_counts >= self.min_evidence) & (self.posteriors < self.elimination_threshold)
        self.states[eligible] = ELIMINATED
        self.log_weights[eligible] = -np.inf
        if np.any(eligible):
            self._normalize()
        return active_positions

    def observe(self, likelihoods: Mapping[str, float], evidence_id: str, *, reason: str = "", hard_falsification: Iterable[str] = (), affected_families: Iterable[str] | None = None) -> None:
        """Apply a sparse observation; optionally restrict work to affected families.

        The posterior normalizer remains global, but likelihood multiplication,
        evidence bookkeeping and explanation writes touch only the selected family
        positions. This makes repeated updates cheap when evidence is localized.
        """
        if evidence_id in self.evidence_ids:
            raise ValueError(f"evidence_id already observed: {evidence_id}")
        selected_families = tuple(dict.fromkeys(affected_families)) if affected_families is not None else tuple(self.family_positions)
        unknown_families = set(selected_families).difference(self.family_positions)
        if unknown_families:
            raise ValueError(f"unknown family names: {sorted(unknown_families)}")
        allowed_positions = np.concatenate([self.family_positions[family] for family in selected_families]) if selected_families else np.asarray([], dtype=np.intp)
        allowed_ids = {self.ids[int(position)] for position in allowed_positions.tolist()}
        ids = [hypothesis_id for hypothesis_id in likelihoods if hypothesis_id in self.index and hypothesis_id in allowed_ids]
        positions = np.asarray([self.index[hypothesis_id] for hypothesis_id in ids], dtype=np.intp)
        values = np.asarray([float(likelihoods[hypothesis_id]) for hypothesis_id in ids], dtype=np.float64)
        if np.any(values < 0) or np.any(values > 1):
            raise ValueError("likelihoods must be between 0 and 1")
        hard_positions = np.asarray([self.index[hypothesis_id] for hypothesis_id in hard_falsification if hypothesis_id in allowed_ids], dtype=np.intp)
        active_positions = self._apply_numeric_update(positions, values, hard_positions)
        self.last_update_families = selected_families
        self.evidence_ids.add(evidence_id)
        if reason:
            for position in active_positions.tolist():
                self.explanations.setdefault(position, []).append(f"{evidence_id}: {reason}")

    def observe_arrays(
        self,
        likelihoods: np.ndarray,
        evidence_id: str,
        *,
        reason: str = "",
        hard_positions: Iterable[int] = (),
        affected_families: Iterable[str] | None = None,
    ) -> None:
        """Apply likelihoods already aligned with ``self.ids`` without Python mappings.

        ``likelihoods`` must be a one-dimensional float array with one value per
        hypothesis. Metadata is touched only after the numeric update, and only
        for positions that were active and selected. This is the preferred path
        for large array-native callers; :meth:`observe` remains the compatible
        ID-oriented adapter.
        """
        if evidence_id in self.evidence_ids:
            raise ValueError(f"evidence_id already observed: {evidence_id}")
        values = np.asarray(likelihoods, dtype=np.float64)
        if values.ndim != 1 or values.size != len(self.ids):
            raise ValueError("likelihoods must be a one-dimensional array aligned with hypotheses")
        if np.any(~np.isfinite(values)) or np.any(values < 0) or np.any(values > 1):
            raise ValueError("likelihoods must be finite values between 0 and 1")
        selected_families = tuple(dict.fromkeys(affected_families)) if affected_families is not None else tuple(self.family_positions)
        unknown_families = set(selected_families).difference(self.family_positions)
        if unknown_families:
            raise ValueError(f"unknown family names: {sorted(unknown_families)}")
        positions = np.concatenate([self.family_positions[family] for family in selected_families]) if selected_families else np.asarray([], dtype=np.intp)
        hard = np.asarray(tuple(hard_positions), dtype=np.intp)
        if np.any(hard < 0) or np.any(hard >= len(self.ids)):
            raise ValueError("hard_positions must refer to valid hypothesis positions")
        if hard.size and not np.all(np.isin(hard, positions)):
            raise ValueError("hard_positions must belong to the selected families")
        active_positions = self._apply_numeric_update(positions, values[positions], hard)
        self.last_update_families = selected_families
        self.evidence_ids.add(evidence_id)
        if reason:
            for position in active_positions.tolist():
                self.explanations.setdefault(int(position), []).append(f"{evidence_id}: {reason}")

    def update_families(self, likelihoods: Mapping[str, float], evidence_id: str, families: Iterable[str], *, reason: str = "", hard_falsification: Iterable[str] = ()) -> None:
        """Explicit alias for localized updates used by family-aware callers."""
        self.observe(likelihoods, evidence_id, reason=reason, hard_falsification=hard_falsification, affected_families=families)

    def top_k(self, k: int, *, include_eliminated: bool = False) -> list[VectorizedBelief]:
        """Return top-k beliefs using argpartition instead of a full sort."""
        if k < 1:
            raise ValueError("k must be positive")
        candidates = np.arange(len(self.ids), dtype=np.intp)
        if not include_eliminated:
            candidates = candidates[self.states != ELIMINATED]
        if candidates.size == 0:
            return []
        count = min(k, candidates.size)
        scores = self.posteriors[candidates]
        selected = candidates[np.argpartition(scores, -count)[-count:]]
        selected = selected[np.argsort(self.posteriors[selected])[::-1]]
        return [self._belief_at(int(position)) for position in selected]

    def _belief_at(self, position: int) -> VectorizedBelief:
        return VectorizedBelief(self.ids[position], self.descriptions[self.ids[position]], float(self.priors[position]), float(self.posteriors[position]), float(self.log_weights[position]), int(self.states[position]), int(self.evidence_counts[position]))

    def posterior_sum(self) -> float:
        return float(self.posteriors.sum())

    def memory_bytes(self) -> int:
        return int(sum(array.nbytes for array in (self.priors, self.log_weights, self.posteriors, self.states, self.evidence_counts)))


__all__ = ["ACTIVE", "ELIMINATED", "SURVIVOR", "VectorizedBelief", "VectorizedHypothesisStore"]
