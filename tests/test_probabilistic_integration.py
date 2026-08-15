import pytest

from forgemind.bayesian import BayesianHypothesisSet, EvidenceObservation, HypothesisState


def make_beliefs() -> BayesianHypothesisSet:
    return BayesianHypothesisSet.from_priors(
        {"H1": "candidate one", "H2": "candidate two", "H3": "candidate three"},
        priors={"H1": 0.5, "H2": 0.3, "H3": 0.2},
        elimination_threshold=0.1,
        min_evidence=2,
    )


def test_multi_step_evidence_preserves_normalization_and_provenance():
    beliefs = make_beliefs()
    first = beliefs.observe(EvidenceObservation(
        "probe-1",
        "first discriminative probe",
        {"H1": 0.9, "H2": 0.05, "H3": 0.7},
        source="integration-test",
    ))
    second = beliefs.observe(EvidenceObservation(
        "probe-2",
        "repeat confirmation probe",
        {"H1": 0.9, "H2": 0.05, "H3": 0.7},
        source="integration-test",
    ))

    by_id = {belief.hypothesis_id: belief for belief in beliefs.beliefs()}
    h2 = by_id["H2"]
    assert beliefs.posterior_sum() == pytest.approx(1.0)
    assert by_id["H1"].state == HypothesisState.SURVIVOR
    assert h2.state == HypothesisState.ELIMINATED
    assert h2.evidence_ids == ["probe-1", "probe-2"]
    assert any("posterior" in reason for reason in h2.reasons)
    assert second[1].reason_code == "posterior_below_threshold"
    assert second[1].evidence_ids == ("probe-1", "probe-2")
    assert all(decision.hypothesis_id for decision in first + second)
    assert "H2" not in {belief.hypothesis_id for belief in beliefs.top_k(3)}


def test_hard_falsification_exposes_irreversible_decision_trace():
    beliefs = BayesianHypothesisSet.from_priors(
        {"H1": "candidate one", "H2": "candidate two"},
        priors={"H1": 0.6, "H2": 0.4},
    )
    decisions = beliefs.observe(EvidenceObservation(
        "oracle-1",
        "counterexample found",
        {"H1": 0.0, "H2": 0.8},
        source="oracle",
        hard_falsification=frozenset({"H1"}),
    ))

    decision = next(item for item in decisions if item.hypothesis_id == "H1")
    assert decision.eliminated is False
    assert decision.reason_code == "hard_falsification"
    assert decision.reversible is False
    assert decision.state == HypothesisState.ELIMINATED
    assert decision.evidence_ids == ("oracle-1",)
    assert "hard falsification" in decision.reason
    assert beliefs.posterior_sum() == pytest.approx(1.0)


def test_parking_and_reactivation_keep_traceable_states_separate_from_falsification():
    beliefs = BayesianHypothesisSet.from_priors(
        {"H1": "candidate one", "H2": "candidate two"},
        priors={"H1": 0.6, "H2": 0.4},
    )

    parked = beliefs.park("H2", reason="defer until a targeted probe is available")
    assert parked.reason_code == "parked"
    assert parked.reversible is True
    assert parked.state == HypothesisState.PARKED
    assert [belief.hypothesis_id for belief in beliefs.top_k(2)] == ["H1"]

    reactivated = beliefs.unpark("H2")
    assert reactivated.state == HypothesisState.UNCERTAIN
    assert reactivated.reasons[-1] == "reactivated from parked state"
    assert [belief.hypothesis_id for belief in beliefs.top_k(2)] == ["H1", "H2"]


def test_duplicate_evidence_is_rejected_without_mutating_trace():
    beliefs = make_beliefs()
    observation = EvidenceObservation("probe-1", "single probe", {"H1": 0.9, "H2": 0.2, "H3": 0.8})
    beliefs.observe(observation)
    before = beliefs.snapshot()

    with pytest.raises(ValueError, match="evidence_id already observed"):
        beliefs.observe(observation)

    assert beliefs.snapshot() == before
