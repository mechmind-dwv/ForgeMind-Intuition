"""Reproducible latency and memory benchmark for BayesianHypothesisSet.

Example:
    python benchmarks/bayesian_latency.py --hypotheses 10000 --repeats 5
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
import tracemalloc
from typing import Any

from forgemind.bayesian import BayesianHypothesisSet, EvidenceObservation


def make_engine(size: int) -> BayesianHypothesisSet:
    hypotheses = {f"H{i}": f"candidate {i}" for i in range(size)}
    priors = {key: float((index % 11) + 1) for index, key in enumerate(hypotheses)}
    return BayesianHypothesisSet.from_priors(hypotheses, priors=priors, elimination_threshold=1e-12)


def benchmark(size: int, repeats: int, k: int) -> dict[str, Any]:
    observe_times: list[float] = []
    top_k_times: list[float] = []
    ranked_times: list[float] = []
    peak_bytes = 0
    for repeat in range(repeats):
        engine = make_engine(size)
        observation = EvidenceObservation(
            evidence_id=f"benchmark-{repeat}",
            description="deterministic latency probe",
            likelihoods={f"H{i}": 0.999 - (i % 17) * 0.0001 for i in range(size)},
            source="benchmark",
        )
        tracemalloc.start()
        started = time.perf_counter()
        engine.observe(observation)
        observe_times.append((time.perf_counter() - started) * 1000)
        started = time.perf_counter()
        top = engine.top_k(k)
        top_k_times.append((time.perf_counter() - started) * 1000)
        started = time.perf_counter()
        engine.ranked()
        ranked_times.append((time.perf_counter() - started) * 1000)
        _, peak = tracemalloc.get_traced_memory()
        peak_bytes = max(peak_bytes, peak)
        tracemalloc.stop()
        if len(top) != min(k, size):
            raise AssertionError("top_k returned an unexpected number of items")
        if abs(engine.posterior_sum() - 1.0) > 1e-9:
            raise AssertionError("posterior mass is not normalized")
    return {
        "hypotheses": size,
        "repeats": repeats,
        "top_k": k,
        "observe_ms_median": round(statistics.median(observe_times), 4),
        "observe_ms_p95_approx": round(sorted(observe_times)[max(0, int(len(observe_times) * 0.95) - 1)], 4),
        "top_k_ms_median": round(statistics.median(top_k_times), 4),
        "ranked_all_ms_median": round(statistics.median(ranked_times), 4),
        "ranked_to_top_k_ratio": round(statistics.median(ranked_times) / max(statistics.median(top_k_times), 1e-12), 4),
        "peak_traced_bytes": peak_bytes,
        "posterior_sum": round(engine.posterior_sum(), 12),
        "best_hypothesis": top[0].hypothesis_id,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hypotheses", type=int, default=10_000)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--top-k", type=int, default=20, dest="top_k")
    args = parser.parse_args()
    if args.hypotheses < 1 or args.repeats < 1 or args.top_k < 1:
        parser.error("hypotheses, repeats and top-k must be positive")
    print(json.dumps(benchmark(args.hypotheses, args.repeats, args.top_k), indent=2))


if __name__ == "__main__":
    main()
