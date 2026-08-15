import numpy as np

from forgemind import BlockExactHypothesisSet, VectorizedHypothesisStore


def test_block_exact_matches_vectorized_for_posterior_and_top_k():
    size = 10_000
    priors = ((np.arange(size) % 23) + 1).astype(np.float64)
    likelihoods = 0.8 + ((np.arange(size) * 37) % 100_000) * 0.000001
    blocked = BlockExactHypothesisSet(priors, ids=[f"H{i}" for i in range(size)], block_size=257, elimination_threshold=1e-12, min_evidence=2)
    vectorized = VectorizedHypothesisStore({f"H{i}": "candidate" for i in range(size)}, priors={f"H{i}": float(value) for i, value in enumerate(priors)}, elimination_threshold=1e-12, min_evidence=2)
    blocked.observe_arrays(likelihoods, "e1")
    vectorized.observe_arrays(likelihoods, "e1")
    np.testing.assert_allclose(blocked.posteriors, vectorized.posteriors, rtol=0, atol=1e-18)
    assert {belief.hypothesis_id for belief in blocked.top_k(25)} == {belief.hypothesis_id for belief in vectorized.top_k(25)}


def test_block_exact_matches_nonempty_eliminations():
    size = 20_000
    priors = np.ones(size, dtype=np.float64)
    likelihoods = np.full(size, 0.9, dtype=np.float64)
    likelihoods[:1000] = 1e-9
    blocked = BlockExactHypothesisSet(priors, ids=[f"H{i}" for i in range(size)], block_size=511, elimination_threshold=1e-6, min_evidence=1)
    vectorized = VectorizedHypothesisStore({f"H{i}": "candidate" for i in range(size)}, priors={f"H{i}": 1.0 for i in range(size)}, elimination_threshold=1e-6, min_evidence=1)
    blocked.observe_arrays(likelihoods, "e1")
    vectorized.observe_arrays(likelihoods, "e1")
    np.testing.assert_array_equal(blocked.states, vectorized.states)
    assert blocked.memory_bytes() == vectorized.memory_bytes()
