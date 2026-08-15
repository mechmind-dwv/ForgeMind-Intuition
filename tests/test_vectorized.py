import pytest

np = pytest.importorskip("numpy")
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


def test_family_update_matches_sparse_exact_update_and_skips_unaffected_family():
    hypotheses = {"H1": "a1", "H2": "a2", "H3": "b1", "H4": "b2"}
    families = {"H1": "family-a", "H2": "family-a", "H3": "family-b", "H4": "family-b"}
    exact = VectorizedHypothesisStore(hypotheses)
    sparse = VectorizedHypothesisStore(hypotheses, families=families)
    likelihoods = {"H1": 0.9, "H2": 0.2}

    exact.observe(likelihoods, "probe-a", reason="family evidence")
    sparse.update_families(likelihoods, "probe-a", ["family-a"], reason="family evidence")

    assert sparse.posteriors == pytest.approx(exact.posteriors)
    assert sparse.last_update_count == 2
    assert sparse.last_update_families == ("family-a",)
    assert sparse.evidence_counts[sparse.index["H3"]] == 0
    assert sparse.evidence_counts[sparse.index["H4"]] == 0
    assert sparse.explanations[sparse.index["H1"]] == ["probe-a: family evidence"]
    assert sparse.index["H3"] not in sparse.explanations


def test_family_update_does_not_falsify_hypothesis_outside_selected_family():
    store = VectorizedHypothesisStore(
        {"H1": "a", "H2": "b"},
        families={"H1": "family-a", "H2": "family-b"},
    )
    store.update_families({"H1": 0.5, "H2": 0.0}, "probe-a", ["family-a"], hard_falsification={"H2"})
    assert store.states[store.index["H2"]] != 2
    assert store.evidence_counts[store.index["H2"]] == 0


def test_direct_array_observation_matches_id_adapter_and_records_reason():
    hypotheses = {"H1": "a", "H2": "b", "H3": "c"}
    mapped = VectorizedHypothesisStore(hypotheses)
    direct = VectorizedHypothesisStore(hypotheses)
    mapped.observe({"H1": 0.9, "H2": 0.4, "H3": 0.7}, "probe", reason="array path")
    direct.observe_arrays(np.asarray([0.9, 0.4, 0.7]), "probe", reason="array path")
    assert direct.posteriors == pytest.approx(mapped.posteriors)
    assert direct.evidence_counts.tolist() == mapped.evidence_counts.tolist()
    assert direct.explanations == mapped.explanations


def test_direct_array_observation_supports_family_selection_and_rejects_bad_shape():
    store = VectorizedHypothesisStore(
        {"H1": "a", "H2": "b", "H3": "c"},
        families={"H1": "a", "H2": "a", "H3": "b"},
    )
    store.observe_arrays(np.asarray([0.5, 0.2, 0.0]), "family-probe", affected_families=["a"])
    assert store.last_update_count == 2
    assert store.evidence_counts.tolist() == [1, 1, 0]
    with pytest.raises(ValueError, match="one-dimensional array"):
        store.observe_arrays(np.asarray([[0.5, 0.2, 0.0]]), "bad-shape")


def test_array_native_constructor_avoids_id_metadata_and_matches_array_observation():
    priors = np.asarray([1.0, 3.0, 2.0], dtype=np.float64)
    direct = VectorizedHypothesisStore.from_arrays(priors, elimination_threshold=1e-12)
    mapped = VectorizedHypothesisStore({"H1": "a", "H2": "b", "H3": "c"}, priors={"H1": 1.0, "H2": 3.0, "H3": 2.0}, elimination_threshold=1e-12)

    direct.observe_arrays(np.asarray([0.9, 0.4, 0.7]), "probe", reason="array-native")
    mapped.observe({"H1": 0.9, "H2": 0.4, "H3": 0.7}, "probe", reason="array-native")

    assert direct.ids is None
    assert direct.index == {}
    assert direct.descriptions == {}
    assert direct.posteriors == pytest.approx(mapped.posteriors)
    assert direct.top_k_positions(2).tolist() == [2, 1]
    assert [belief.hypothesis_id for belief in direct.top_k(2)] == ["2", "1"]
    with pytest.raises(ValueError, match="ID-backed"):
        direct.observe({"0": 0.5}, "mapping-probe")
