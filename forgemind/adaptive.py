"""Calibrated adaptive intuition model for ForgeMind 0.16.

The model learns a ranking signal from weighted evidence.  Negative routine
observations can be down-weighted, while a surviving hypothesis contributes
full evidence.  The output is a calibrated score, not a probability of truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .intuition import IntuitionScore


FEATURES = (
    "novelty",
    "structural_similarity",
    "compression",
    "falsification_value",
    "compositional_value",
)


@dataclass
class FeatureEvidence:
    successes: float = 0.0
    failures: float = 0.0

    def observe(self, success: bool, weight: float, alpha: float) -> None:
        if weight < 0:
            raise ValueError("weight must be non-negative")
        if success:
            self.successes += weight
        else:
            self.failures += weight

    def signal(self, alpha: float = 1.0, shrinkage: float = 4.0) -> float:
        total = self.successes + self.failures
        posterior = (self.successes + alpha) / (total + 2 * alpha)
        weight = 2 * posterior - 1
        return weight * (total / (total + shrinkage)) if total else 0.0


@dataclass(frozen=True)
class CalibrationResult:
    raw_score: float
    calibrated_score: float
    feature_contributions: dict[str, float]
    complexity_penalty: float
    reasons: tuple[str, ...] = field(default_factory=tuple)


class AdaptiveIntuitionModel:
    """Explainable calibration over IntuitionScore feature observations."""

    def __init__(self, *, alpha: float = 1.0, shrinkage: float = 4.0):
        if alpha <= 0 or shrinkage < 0:
            raise ValueError("alpha must be positive and shrinkage non-negative")
        self.alpha = alpha
        self.shrinkage = shrinkage
        self.evidence = {name: FeatureEvidence() for name in FEATURES}
        self.observations = 0

    def observe(self, score: IntuitionScore, *, success: bool, weight: float = 1.0) -> None:
        """Update feature evidence; routine failures may use weight < 1."""
        for name in FEATURES:
            self.evidence[name].observe(success, weight, self.alpha)
        self.observations += 1

    def feature_weights(self) -> dict[str, float]:
        return {name: data.signal(self.alpha, self.shrinkage) for name, data in self.evidence.items()}

    def calibrate(self, score: IntuitionScore) -> CalibrationResult:
        values = {
            "novelty": score.novelty,
            "structural_similarity": score.structural_similarity,
            "compression": score.compression,
            "falsification_value": score.falsification_value,
            "compositional_value": score.compositional_value,
        }
        weights = self.feature_weights()
        contributions = {name: values[name] * weights[name] for name in FEATURES}
        raw = sum(contributions.values())
        complexity_penalty = score.complexity_penalty
        calibrated = raw - complexity_penalty - score.historical_failure
        reasons = [
            f"{name}: contribution {value:+.3f} from weighted evidence"
            for name, value in contributions.items() if abs(value) > 1e-9
        ]
        if not self.observations:
            reasons.append("neutral prior: no calibration observations yet")
        reasons.append("complexity is an explicit negative signal")
        return CalibrationResult(
            score.total, round(calibrated, 6),
            {k: round(v, 6) for k, v in contributions.items()},
            complexity_penalty, tuple(reasons),
        )

    def rank(self, scores: Iterable[IntuitionScore]) -> list[tuple[int, CalibrationResult]]:
        ranked = [(i, self.calibrate(score)) for i, score in enumerate(scores)]
        return sorted(ranked, key=lambda item: item[1].calibrated_score, reverse=True)
