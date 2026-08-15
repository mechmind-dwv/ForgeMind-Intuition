"""Compare object-backed and NumPy-backed hypothesis stores.

This benchmark reports implementation-level measurements, not a product SLA.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
import tracemalloc
from typing import Any

from forgemind.bayesian import BayesianHypothesisSet, EvidenceObservation
from forgemind.vectorized import VectorizedHypothesisStore


def make_data(size: int) -> tuple[dict[str, str], dict[str, float], dict[str, float]]:
    hypotheses = {f"H{i}": f"candidate {i}" for i in range(size)}
    priors = {key: float((index % 11) + 1) for index, key in enumerate(hypotheses)}
    likelihoods = {key: 0.999 - (index % 17) * 0.0001 for index, key in enumerate(hypotheses)}
    return hypotheses, priors, likelihoods


def median_ms(values: list[float]) -> float:
    return round(statistics.median(values), 4)


def run(size: int, repeats: int, k: int) -> dict[str, Any]:
    hypotheses, priors, likelihoods = make_data(size)
    object_observe: list[float] = []
    object_top_k: list[float] = []
    vector_observe: list[float] = []
    vector_top_k: list[float] = []
    object_peak = 0
    vector_peak = 0
    vector_numeric = 0
    for repeat in range(repeats):
        observation = EvidenceObservation(f"compare-{repeat}", "benchmark", likelihoods, source="benchmark")
        tracemalloc.start()
        object_store = BayesianHypothesisSet.from_priors(hypotheses, priors=priors, elimination_threshold=1e-12)
        started = time.perf_counter(); object_store.observe(observation); object_observe.append((time.perf_counter() - started) * 1000)
        started = time.perf_counter(); object_store.top_k(k); object_top_k.append((time.perf_counter() - started) * 1000)
        _, peak = tracemalloc.get_traced_memory(); object_peak = max(object_peak, peak); tracemalloc.stop()

        tracemalloc.start()
        vector_store = VectorizedHypothesisStore(hypotheses, priors=priors, elimination_threshold=1e-12)
        started = time.perf_counter(); vector_store.observe(likelihoods, f"compare-{repeat}", reason="benchmark"); vector_observe.append((time.perf_counter() - started) * 1000)
        started = time.perf_counter(); vector_store.top_k(k); vector_top_k.append((time.perf_counter() - started) * 1000)
        _, peak = tracemalloc.get_traced_memory(); vector_peak = max(vector_peak, peak); tracemalloc.stop()
        vector_numeric = vector_store.memory_bytes()
    return {
        "hypotheses": size,
        "repeats": repeats,
        "top_k": k,
        "object_observe_ms_median": median_ms(object_observe),
        "vectorized_observe_ms_median": median_ms(vector_observe),
        "object_top_k_ms_median": median_ms(object_top_k),
        "vectorized_top_k_ms_median": median_ms(vector_top_k),
        "object_peak_traced_bytes": object_peak,
        "vectorized_peak_traced_bytes": vector_peak,
        "vectorized_numeric_bytes": vector_numeric,
        "posterior_sum_object": round(object_store.posterior_sum(), 12),
        "posterior_sum_vectorized": round(vector_store.posterior_sum(), 12),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypotheses", type=int, default=10_000)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=20)
    args = parser.parse_args()
    print(json.dumps(run(args.hypotheses, args.repeats, args.top_k), indent=2))


if __name__ == "__main__":
    main()
