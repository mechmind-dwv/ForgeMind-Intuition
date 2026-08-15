"""Low-memory million-hypothesis exactness benchmark.

The reference keeps only dense numeric log-weights and generates one evidence
vector at a time. This avoids materializing a million Python belief objects while
preserving the exact log-space recurrence used by the scalar engine.
"""

from __future__ import annotations

import argparse
import json
import time
from typing import Any

import numpy as np

from forgemind.vectorized import ELIMINATED, VectorizedHypothesisStore


def run(size: int, rounds: int, top_k: int) -> dict[str, Any]:
    indices = np.arange(size, dtype=np.int64)
    hypothesis_ids = [f"H{i}" for i in range(size)]
    hypotheses = {hypothesis_id: "" for hypothesis_id in hypothesis_ids}
    prior_values = ((indices % 23) + 1).astype(np.float64)
    priors = {hypothesis_id: float(prior_values[index]) for index, hypothesis_id in enumerate(hypothesis_ids)}
    reference_log = np.log(prior_values)
    reference_log -= np.max(reference_log) + np.log(np.exp(reference_log - np.max(reference_log)).sum())
    store = VectorizedHypothesisStore(hypotheses, priors=priors, elimination_threshold=1e-12, min_evidence=2)
    max_errors: list[float] = []
    mean_errors: list[float] = []
    vector_times: list[float] = []
    reference_times: list[float] = []
    top_k_overlaps: list[float] = []

    for round_index in range(rounds):
        likelihood_values = 0.8 + ((indices * 37 + round_index * 13) % 100_000) * 0.000001
        log_likelihoods = np.log(likelihood_values)
        started = time.perf_counter()
        reference_log += log_likelihoods
        pivot = np.max(reference_log)
        reference_log -= pivot + np.log(np.exp(reference_log - pivot).sum())
        reference_posteriors = np.exp(reference_log)
        reference_times.append((time.perf_counter() - started) * 1000)
        started = time.perf_counter()
        store.observe_arrays(likelihood_values, f"million-probe-{round_index}")
        vector_times.append((time.perf_counter() - started) * 1000)
        errors = np.abs(reference_posteriors - store.posteriors)
        max_errors.append(float(np.max(errors)))
        mean_errors.append(float(np.mean(errors)))
        reference_top = set(np.argpartition(reference_posteriors, -top_k)[-top_k:].tolist())
        vector_top = {int(store.index[hypothesis_id]) for hypothesis_id in [belief.hypothesis_id for belief in store.top_k(top_k)]}
        top_k_overlaps.append(len(reference_top & vector_top) / top_k)

    return {
        "hypotheses": size,
        "rounds": rounds,
        "top_k": top_k,
        "max_abs_posterior_error": max(max_errors),
        "mean_abs_posterior_error": float(np.mean(mean_errors)),
        "posterior_sum_reference": float(reference_posteriors.sum()),
        "posterior_sum_vectorized": store.posterior_sum(),
        "top_k_min_overlap": min(top_k_overlaps),
        "eliminated_vectorized": int(np.count_nonzero(store.states == ELIMINATED)),
        "reference_ms_total": sum(reference_times),
        "vectorized_ms_total": sum(vector_times),
        "speedup_reference_over_vectorized": sum(reference_times) / sum(vector_times),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypotheses", type=int, default=1_000_000)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=25)
    args = parser.parse_args()
    print(json.dumps(run(args.hypotheses, args.rounds, args.top_k), indent=2))


if __name__ == "__main__":
    main()
