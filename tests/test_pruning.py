import pytest

from forgemind.bayesian import BayesianHypothesisSet, HypothesisState


def test_upper_bound_is_safe_and_does_not_mutate_state():
    store = BayesianHypothesisSet.from_priors(
        {"H1": "strong", "H2": "medium", "H3": "weak"},
        priors={"H1": 90.0, "H2": 9.0, "H3": 1.0},
        elimination_threshold=0.001,
    )
    before = store.snapshot()
    bound = store.upper_bound("H3", remaining_evidence=2, minimum_likelihood=0.9)
    assert 0.0 <= bound <= 1.0
    assert store.snapshot() == before


def test_pruning_parks_only_low_upper_bound_and_unpark_is_reversible():
    store = BayesianHypothesisSet.from_priors(
        {"H1": "strong", "H2": "medium", "H3": "weak"},
        priors={"H1": 90.0, "H2": 9.0, "H3": 1.0},
        elimination_threshold=0.001,
    )
    decisions = store.prune_by_upper_bound(threshold=0.02, remaining_evidence=2, minimum_likelihood=0.9)
    assert [decision.hypothesis_id for decision in decisions] == ["H3"]
    assert store._beliefs["H3"].state == HypothesisState.PARKED
    assert decisions[0].reason_code == "upper_bound_pruned"
    assert decisions[0].reversible is True
    assert "upper bound" in decisions[0].reason
    assert store.top_k(3)[-1].hypothesis_id != "H3"

    reactivated = store.unpark("H3")
    assert reactivated.state == HypothesisState.UNCERTAIN
    assert reactivated.reasons[-1] == "reactivated from parked state"
    assert store.top_k(3)[-1].hypothesis_id == "H3"


def test_upper_bound_validates_inputs_and_never_parks_eliminated():
    store = BayesianHypothesisSet.from_priors({"H1": "only", "H2": "other"}, priors={"H1": 1.0, "H2": 1.0})
    with pytest.raises(ValueError, match="remaining_evidence"):
        store.upper_bound("H1", remaining_evidence=-1)
    with pytest.raises(ValueError, match="minimum_likelihood"):
        store.upper_bound("H1", remaining_evidence=1, minimum_likelihood=1.1)
    store.eliminate_hypothesis("H2", reason="oracle falsification")
    assert store.upper_bound("H2", remaining_evidence=3) == 0.0
