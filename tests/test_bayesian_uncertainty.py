import pytest

from forgemind.bayesian import BayesianHypothesisSet, EvidenceObservation, HypothesisState


def test_low_posterior_without_enough_evidence_becomes_uncertain_not_eliminated():
    beliefs = BayesianHypothesisSet.from_priors(
        {"H1": "likely", "H2": "uncertain"},
        priors={"H1": 0.9, "H2": 0.1},
        elimination_threshold=0.05,
        min_evidence=2,
    )
    decisions = beliefs.observe(EvidenceObservation("probe-1", "weak signal", {"H1": 0.99, "H2": 0.01}))
    h2 = next(item for item in beliefs.beliefs() if item.hypothesis_id == "H2")
    decision = next(item for item in decisions if item.hypothesis_id == "H2")
    assert h2.state == HypothesisState.UNCERTAIN
    assert decision.eliminated is False
    assert decision.reason_code == "insufficient_evidence"
    assert decision.reversible is True


def test_parked_hypothesis_is_hidden_from_default_top_k_and_can_be_reactivated():
    beliefs = BayesianHypothesisSet.from_priors({"H1": "A", "H2": "B"})
    decision = beliefs.park("H1", reason="defer until a discriminative probe exists")
    assert decision.state == HypothesisState.PARKED
    assert [item.hypothesis_id for item in beliefs.top_k(2)] == ["H2"]
    restored = beliefs.unpark("H1")
    assert restored.state == HypothesisState.UNCERTAIN
    assert {item.hypothesis_id for item in beliefs.top_k(2)} == {"H1", "H2"}


def test_explicit_elimination_requires_reason_and_preserves_provenance():
    beliefs = BayesianHypothesisSet.from_priors({"H1": "A", "H2": "B"})
    with pytest.raises(ValueError, match="reason must not be empty"):
        beliefs.eliminate_hypothesis("H1", reason="")
    decision = beliefs.eliminate_hypothesis(
        "H1",
        reason="counterexample violates the declared invariant",
        evidence_ids=("counterexample-1",),
    )
    assert decision.eliminated is True
    assert decision.reason_code == "explicit"
    assert decision.reversible is False
    h1 = next(item for item in beliefs.beliefs() if item.hypothesis_id == "H1")
    assert h1.state == HypothesisState.ELIMINATED
    assert "counterexample-1" in h1.evidence_ids
    assert beliefs.posterior_sum() == pytest.approx(1.0)
