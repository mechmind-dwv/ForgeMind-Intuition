__version__ = "0.16.0"

from .adaptive import AdaptiveIntuitionModel, CalibrationResult
from .agent_contract import AGENT_CONTRACT_VERSION, AGENT_OPERATIONS, AgentToolRequest, AgentToolResponse
from .bayesian import BayesianHypothesisSet, EliminationDecision, EvidenceObservation, HypothesisBelief, HypothesisState
from .advisor import CandidateAdvice, advise
from .intuition import IntuitionScore, intuition_score
from .knowledge import KnowledgeBase, KnowledgeRecord, MemoryType
from .project import CandidateInput, ForgeMindProject, ProjectInput, ProjectValidationError
from .exact_block import BlockBelief, BlockExactHypothesisSet
from .execution import ExecutionAudit, ExecutionPolicy, ExecutionResult, run_controlled

__all__ = [
    "AdaptiveIntuitionModel",
    "AGENT_CONTRACT_VERSION",
    "AGENT_OPERATIONS",
    "AgentToolRequest",
    "AgentToolResponse",
    "BayesianHypothesisSet",
    "EliminationDecision",
    "EvidenceObservation",
    "HypothesisBelief",
    "HypothesisState",
    "CandidateAdvice",
    "advise",
    "CalibrationResult",
    "IntuitionScore",
    "CandidateInput",
    "ForgeMindProject",
    "KnowledgeBase",
    "KnowledgeRecord",
    "MemoryType",
    "ProjectInput",
    "ProjectValidationError",
    "BlockBelief",
    "BlockExactHypothesisSet",
    "ExecutionAudit",
    "ExecutionPolicy",
    "ExecutionResult",
    "run_controlled",
    "intuition_score",
    "VectorizedBelief",
    "VectorizedHypothesisStore",
]


def __getattr__(name: str):
    if name in {"VectorizedBelief", "VectorizedHypothesisStore"}:
        from .vectorized import VectorizedBelief, VectorizedHypothesisStore
        return {"VectorizedBelief": VectorizedBelief, "VectorizedHypothesisStore": VectorizedHypothesisStore}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
