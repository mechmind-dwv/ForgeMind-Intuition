"""Agent-facing advice layer for ForgeMind.

This is intentionally model-agnostic: an LLM or coding agent can submit
candidate programs and receive ranked, evidence-based recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .adaptive import AdaptiveIntuitionModel
from .intuition import IntuitionScore, intuition_score
from .knowledge import KnowledgeBase


@dataclass(frozen=True)
class CandidateAdvice:
    candidate_index: int
    score: IntuitionScore
    calibrated_score: float
    experimental_value: float
    recommendation: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate_index": self.candidate_index,
            "intuition": self.score.as_dict(),
            "calibrated_score": self.calibrated_score,
            "experimental_value": self.experimental_value,
            "recommendation": self.recommendation,
        }


def advise(candidates: Iterable[Any], *, knowledge_base: KnowledgeBase,
           calibration: AdaptiveIntuitionModel | None = None) -> list[CandidateAdvice]:
    """Rank hypotheses by expected value of testing them next."""
    candidates = list(candidates)
    model = calibration or AdaptiveIntuitionModel()
    advice: list[CandidateAdvice] = []
    for index, candidate in enumerate(candidates):
        score = intuition_score(candidate, knowledge_base=knowledge_base)
        calibrated = model.calibrate(score)
        experimental_value = (
            score.falsification_value + score.novelty + score.compositional_value
            - score.complexity_penalty - score.historical_failure
        )
        advice.append(CandidateAdvice(
            index, score, calibrated.calibrated_score, round(experimental_value, 6),
            "Prueba esta hipótesis primero: maximiza valor experimental esperado."
            if experimental_value > 0 else
            "Retrasa esta hipótesis: su evidencia experimental actual es débil.",
        ))
    return sorted(advice, key=lambda item: (item.experimental_value, item.calibrated_score), reverse=True)
