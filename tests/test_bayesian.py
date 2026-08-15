import pytest

from forgemind.bayesian import (
    BayesianHypothesisSet,
    EvidenceObservation,
    HypothesisState,
)


def test_bayes_update_prefers_hypothesis_with_higher_likelihood():
    beliefs = BayesianHypothesisSet.from_priors(
        {"H1": "sort preserves order", "H2": "reverse preserves order"},
        priors={"H1": 0.5, "H2": 0.5},
    )
    decisions = beliefs.observe(EvidenceObservation(
        evidence_id="probe-01",
        description="ordered input remains ordered after sort",
        likelihoods={"H1": 0.9, "H2": 0.2},
        source="property-test",
    ))
    assert beliefs.posterior_sum() == pytest.approx(1.0)
    assert beliefs.ranked()[0].hypothesis_id == "H1"
    assert beliefs.ranked()[0].posterior > 0.8
    assert decisions[0].evidence_ids == ("probe-01",)


def test_hard_falsification_eliminates_hypothesis_and_renormalizes():
    beliefs = BayesianHypothesisSet.from_priors(
        {"H1": "candidate A", "H2": "candidate B"},
        priors={"H1": 0.6, "H2": 0.4},
    )
    beliefs.observe(EvidenceObservation(
        evidence_id="counterexample-7",
        description="counterexample found",
        likelihoods={"H1": 0.0, "H2": 0.8},
        hard_falsification=frozenset({"H1"}),
        source="oracle",
    ))
    by_id = {belief.hypothesis_id: belief for belief in beliefs.beliefs()}
    assert by_id["H1"].state == HypothesisState.ELIMINATED
    assert by_id["H1"].posterior == 0.0
    assert by_id["H2"].state == HypothesisState.SURVIVOR
    assert beliefs.posterior_sum() == pytest.approx(1.0)


def test_low_posterior_is_explained_and_eliminated_after_minimum_evidence():
    beliefs = BayesianHypothesisSet.from_priors(
        {"H1": "likely", "H2": "unlikely"},
        priors={"H1": 0.9, "H2": 0.1},
        elimination_threshold=0.05,
        min_evidence=2,
    )
    observation = EvidenceObservation("weak-1", "weak support", {"H1": 0.99, "H2": 0.01})
    beliefs.observe(observation)
    assert beliefs.beliefs()[1].state != HypothesisState.ELIMINATED
    decisions = beliefs.observe(EvidenceObservation("weak-2", "repeat weak support", {"H1": 0.99, "H2": 0.01}))
    h2 = next(item for item in beliefs.beliefs() if item.hypothesis_id == "H2")
    assert h2.state == HypothesisState.ELIMINATED
    assert any("threshold" in reason for reason in h2.reasons)
    assert any(decision.eliminated for decision in decisions)
