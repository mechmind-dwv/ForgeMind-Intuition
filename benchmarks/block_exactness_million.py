"""Compare block-exact semantics with the vectorized store at million scale."""
from __future__ import annotations

import json
import resource
import time

import numpy as np

from forgemind import BlockExactHypothesisSet, VectorizedHypothesisStore


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def run(size: int = 1_000_000, rounds: int = 3, top_k: int = 25, block_size: int = 65_536) -> dict[str, object]:
    indices = np.arange(size, dtype=np.int64)
    priors = ((indices % 23) + 1).astype(np.float64)
    ids = [f"H{i}" for i in range(size)]
    vectorized = VectorizedHypothesisStore({hypothesis_id: "candidate" for hypothesis_id in ids}, priors={hypothesis_id: float(priors[index]) for index, hypothesis_id in enumerate(ids)}, elimination_threshold=1e-12, min_evidence=2)
    blocked = BlockExactHypothesisSet(priors, ids=ids, block_size=block_size, elimination_threshold=1e-12, min_evidence=2)
    rss_after_init_mb = rss_mb()
    max_error = 0.0
    mean_errors: list[float] = []
    top_overlaps: list[float] = []
    eliminated_matches: list[bool] = []
    block_times: list[float] = []
    vector_times: list[float] = []
    for round_index in range(rounds):
        likelihoods = 0.8 + ((indices * 37 + round_index * 13) % 100_000) * 0.000001
        started = time.perf_counter()
        blocked.observe_arrays(likelihoods, f"block-probe-{round_index}")
        block_times.append((time.perf_counter() - started) * 1000)
        started = time.perf_counter()
        vectorized.observe_arrays(likelihoods, f"vector-probe-{round_index}")
        vector_times.append((time.perf_counter() - started) * 1000)
        errors = np.abs(blocked.posteriors - vectorized.posteriors)
        max_error = max(max_error, float(np.max(errors)))
        mean_errors.append(float(np.mean(errors)))
        block_top = {belief.hypothesis_id for belief in blocked.top_k(top_k)}
        vector_top = {belief.hypothesis_id for belief in vectorized.top_k(top_k)}
        top_overlaps.append(len(block_top & vector_top) / top_k)
        eliminated_matches.append(np.array_equal(blocked.states, vectorized.states))
    return {
        "hypotheses": size,
        "rounds": rounds,
        "top_k": top_k,
        "block_size": block_size,
        "max_abs_posterior_error": max_error,
        "mean_abs_posterior_error": float(np.mean(mean_errors)),
        "posterior_sum_block": float(blocked.posteriors.sum()),
        "posterior_sum_vectorized": vectorized.posterior_sum(),
        "top_k_min_overlap": min(top_overlaps),
        "eliminated_sets_all_rounds_match": all(eliminated_matches),
        "eliminated_block": int(np.count_nonzero(blocked.states == 2)),
        "eliminated_vectorized": int(np.count_nonzero(vectorized.states == 2)),
        "block_numeric_state_bytes": blocked.memory_bytes(),
        "vectorized_numeric_state_bytes": vectorized.memory_bytes(),
        "rss_after_init_mb": rss_after_init_mb,
        "rss_peak_mb": rss_mb(),
        "block_observe_ms_total": sum(block_times),
        "vectorized_observe_ms_total": sum(vector_times),
        "block_over_vectorized": sum(block_times) / sum(vector_times),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
