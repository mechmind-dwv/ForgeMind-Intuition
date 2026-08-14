from forgemind.adaptive import AdaptiveIntuitionModel
from forgemind.core import Node
from forgemind.intuition import intuition_score
from forgemind.knowledge import KnowledgeBase, MemoryType


def program(*nodes):
    return [Node("U" if name in {"rev", "sort", "neg"} else "P", name, arg) for name, arg in nodes]


def test_knowledge_memory_preserves_bounded_provenance():
    kb = KnowledgeBase()
    rev = program(("rev", None))
    sort = program(("sort", None))
    record = kb.remember_equivalence(rev, sort, probes=[[1, 2], [3, 1]], provenance={"method": "bounded"})
    assert record.memory_type == MemoryType.EQUIVALENCE
    assert record.status == "BOUNDED"
    assert record.provenance["method"] == "bounded"
    assert record.confidence == 1.0
    assert kb.related_rules(rev) == []


def test_intuition_is_explainable_and_not_truth_probability():
    kb = KnowledgeBase()
    rev = program(("rev", None))
    kb.remember_rule(rev, rule="rev(rev(x)) = x", probes=[[1, 2]], confidence=0.8)
    score = intuition_score(rev, knowledge_base=kb)
    assert 0 <= score.complexity_penalty <= 1
    assert any("experimental evidence" in reason for reason in score.reasons)
    assert score.as_dict()["total"] == score.total


def test_weighted_evidence_prevents_routine_failures_dominating():
    kb = KnowledgeBase()
    score = intuition_score(program(("rev", None)), knowledge_base=kb)
    model = AdaptiveIntuitionModel()
    for _ in range(30):
        model.observe(score, success=False, weight=0.25)
    model.observe(score, success=True, weight=1.0)
    assert model.feature_weights()["novelty"] > -0.8
    result = model.calibrate(score)
    assert result.complexity_penalty == score.complexity_penalty
    assert result.reasons


def test_rank_is_deterministic_and_penalizes_complexity():
    kb = KnowledgeBase()
    simple = intuition_score(program(("rev", None)), knowledge_base=kb)
    complex_score = intuition_score(program(("rev", None), ("sort", None), ("neg", None)), knowledge_base=kb)
    model = AdaptiveIntuitionModel()
    ranked = model.rank([complex_score, simple])
    assert [index for index, _ in ranked] == [0, 1] or ranked[0][1].calibrated_score >= ranked[1][1].calibrated_score
