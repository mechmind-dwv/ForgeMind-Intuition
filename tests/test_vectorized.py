import pytest

pytest.importorskip("numpy")
from forgemind import VectorizedHypothesisStore


def test_vectorized_store_normalizes_and_ranks():
    store = VectorizedHypothesisStore(
        {"H1": "candidate A", "H2": "candidate B", "H3": "candidate C"},
        priors={"H1": 1.0, "H2": 3.0, "H3": 2.0},
    )
    assert store.posterior_sum() == pytest.approx(1.0)
    assert [belief.hypothesis_id for belief in store.top_k(2)] == ["H2", "H3"]


def test_vectorized_sparse_observation_preserves_omitted_hypotheses():
    store = VectorizedHypothesisStore({"H1": "a", "H2": "b", "H3": "c"})
    store.observe({"H1": 0.9}, "probe-1", reason="property test")
    assert store.posterior_sum() == pytest.approx(1.0)
    assert store.top_k(1)[0].hypothesis_id in {"H2", "H3"}
    assert store.evidence_counts[store.index["H2"]] == 0
    assert store.evidence_counts[store.index["H3"]] == 0


def test_vectorized_hard_falsification_eliminates_and_renormalizes():
    store = VectorizedHypothesisStore({"H1": "a", "H2": "b"})
    store.observe({"H1": 0.0, "H2": 0.8}, "counterexample", hard_falsification={"H1"})
    assert store.top_k(1)[0].hypothesis_id == "H2"
    assert store.posterior_sum() == pytest.approx(1.0)


def test_vectorized_duplicate_evidence_is_rejected():
    store = VectorizedHypothesisStore({"H1": "a", "H2": "b"})
    store.observe({"H1": 0.8}, "same")
    with pytest.raises(ValueError, match="already observed"):
        store.observe({"H1": 0.8}, "same")
