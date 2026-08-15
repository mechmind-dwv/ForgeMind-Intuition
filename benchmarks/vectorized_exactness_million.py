"""Low-memory million-hypothesis exactness benchmark."""

from __future__ import annotations

import argparse
import json
import resource
import time
from typing import Any

import numpy as np

from forgemind.vectorized import ELIMINATED, VectorizedHypothesisStore


def rss_mb() -> float:
    """Return Linux process high-water RSS in MiB."""
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def blocked_logsumexp(values: np.ndarray, block_size: int) -> float:
    """Compute logsumexp with bounded temporary arrays."""
    pivot = float(np.max(values))
    total = 0.0
    for start in range(0, values.size, block_size):
        block = values[start : start + block_size]
        total += float(np.exp(block - pivot).sum())
    return pivot + float(np.log(total))


def run(size: int, rounds: int, top_k: int, elimination_threshold: float = 1e-12, block_size: int = 65_536) -> dict[str, Any]:
    rss_before_mb = rss_mb()
    indices = np.arange(size, dtype=np.int64)
    hypothesis_ids = [f"H{i}" for i in range(size)]
    hypotheses = {hypothesis_id: "" for hypothesis_id in hypothesis_ids}
    prior_values = ((indices % 23) + 1).astype(np.float64)
    priors = {hypothesis_id: float(prior_values[index]) for index, hypothesis_id in enumerate(hypothesis_ids)}
    reference_log = np.log(prior_values)
    reference_eliminated = np.zeros(size, dtype=bool)
    reference_log -= blocked_logsumexp(reference_log, block_size)
    store = VectorizedHypothesisStore(hypotheses, priors=priors, elimination_threshold=elimination_threshold, min_evidence=2)
    rss_after_init_mb = rss_mb()
    rss_peak_mb = rss_after_init_mb
    max_errors: list[float] = []
    mean_errors: list[float] = []
    vector_times: list[float] = []
    reference_times: list[float] = []
    top_k_overlaps: list[float] = []
    eliminated_matches: list[bool] = []

    for round_index in range(rounds):
        likelihood_values = 0.8 + ((indices * 37 + round_index * 13) % 100_000) * 0.000001
        started = time.perf_counter()
        for start in range(0, size, block_size):
            stop = min(start + block_size, size)
            reference_log[start:stop] += np.log(likelihood_values[start:stop])
        reference_log -= blocked_logsumexp(reference_log, block_size)
        reference_posteriors = np.exp(reference_log)
        if round_index + 1 >= 2:
            newly_eliminated = (~reference_eliminated) & (reference_posteriors < elimination_threshold)
            if np.any(newly_eliminated):
                reference_eliminated |= newly_eliminated
                reference_log[newly_eliminated] = -np.inf
                pivot = np.max(reference_log)
                reference_log -= pivot + np.log(np.exp(reference_log - pivot).sum())
                reference_posteriors = np.exp(reference_log)
        reference_times.append((time.perf_counter() - started) * 1000)
        started = time.perf_counter()
        store.observe_arrays(likelihood_values, f"million-probe-{round_index}")
        vector_times.append((time.perf_counter() - started) * 1000)
        rss_peak_mb = max(rss_peak_mb, rss_mb())
        errors = np.abs(reference_posteriors - store.posteriors)
        max_errors.append(float(np.max(errors)))
        mean_errors.append(float(np.mean(errors)))
        reference_top = set(np.argpartition(reference_posteriors, -top_k)[-top_k:].tolist())
        vector_top = {int(store.index[hypothesis_id]) for hypothesis_id in [belief.hypothesis_id for belief in store.top_k(top_k)]}
        top_k_overlaps.append(len(reference_top & vector_top) / top_k)
        reference_eliminated_set = set(np.flatnonzero(reference_eliminated).tolist())
        vector_eliminated = set(np.flatnonzero(store.states == ELIMINATED).tolist())
        eliminated_matches.append(reference_eliminated_set == vector_eliminated)

    return {
        "hypotheses": size,
        "rounds": rounds,
        "top_k": top_k,
        "elimination_threshold": elimination_threshold,
        "reference_block_size": block_size,
        "max_abs_posterior_error": max(max_errors),
        "mean_abs_posterior_error": float(np.mean(mean_errors)),
        "posterior_sum_reference": float(reference_posteriors.sum()),
        "posterior_sum_vectorized": store.posterior_sum(),
        "top_k_min_overlap": min(top_k_overlaps),
        "eliminated_sets_all_rounds_match": all(eliminated_matches),
        "eliminated_reference": int(np.count_nonzero(reference_eliminated)),
        "eliminated_vectorized": int(np.count_nonzero(store.states == ELIMINATED)),
        "numeric_state_bytes": store.memory_bytes(),
        "likelihood_input_bytes_per_round": int(likelihood_values.nbytes),
        "rss_before_mb": rss_before_mb,
        "rss_after_init_mb": rss_after_init_mb,
        "rss_peak_mb": rss_peak_mb,
        "reference_ms_total": sum(reference_times),
        "vectorized_ms_total": sum(vector_times),
        "speedup_reference_over_vectorized": sum(reference_times) / sum(vector_times),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypotheses", type=int, default=1_000_000)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=25)
    parser.add_argument("--elimination-threshold", type=float, default=1e-12)
    parser.add_argument("--block-size", type=int, default=65_536)
    args = parser.parse_args()
    print(json.dumps(run(args.hypotheses, args.rounds, args.top_k, args.elimination_threshold, args.block_size), indent=2))


if __name__ == "__main__":
    main()
