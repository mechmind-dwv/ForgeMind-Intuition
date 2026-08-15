from __future__ import annotations

import pytest

from forgemind.bayesian import BayesianHypothesisSet, EvidenceObservation


def test_log_weight_survives_many_small_likelihood_updates():
    beliefs = BayesianHypothesisSet.from_priors(
        {"winner": "stable", "other": "fragile"},
        priors={"winner": 0.5, "other": 0.5},
        elimination_threshold=1e-12,
    )
    for index in range(120):
        beliefs.observe(EvidenceObservation(f"e-{index}", "repeated probe", {"winner": 0.99, "other": 0.97}))
    assert beliefs.posterior_sum() == pytest.approx(1.0)
    assert beliefs.ranked()[0].hypothesis_id == "winner"
    assert beliefs.ranked()[0].posterior > 0.9


def test_top_k_returns_only_requested_best_beliefs():
    hypotheses = {f"H{i}": f"candidate {i}" for i in range(100)}
    priors = {key: float(index + 1) for index, key in enumerate(hypotheses)}
    beliefs = BayesianHypothesisSet.from_priors(hypotheses, priors=priors)
    result = beliefs.top_k(3)
    assert [item.hypothesis_id for item in result] == ["H99", "H98", "H97"]


def test_duplicate_evidence_is_rejected_before_double_counting():
    beliefs = BayesianHypothesisSet.from_priors({"H1": "a", "H2": "b"})
    observation = EvidenceObservation("same", "one probe", {"H1": 0.8, "H2": 0.2})
    beliefs.observe(observation)
    try:
        beliefs.observe(observation)
    except ValueError as error:
        assert "already observed" in str(error)
    else:
        raise AssertionError("duplicate evidence must be rejected")
