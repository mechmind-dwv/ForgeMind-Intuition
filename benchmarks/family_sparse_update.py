"""Benchmark localized family updates in the vectorized hypothesis store.

The benchmark reports implementation-level work avoided. It is not a product SLA.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from typing import Any

from forgemind.vectorized import VectorizedHypothesisStore


def make_data(size: int, family_count: int) -> tuple[dict[str, str], dict[str, str], dict[str, float]]:
    hypotheses = {f"H{i}": f"candidate {i}" for i in range(size)}
    families = {hypothesis_id: f"family-{index % family_count}" for index, hypothesis_id in enumerate(hypotheses)}
    likelihoods = {hypothesis_id: 0.95 - (index % 13) * 0.001 for index, hypothesis_id in enumerate(hypotheses)}
    return hypotheses, families, likelihoods


def median_ms(values: list[float]) -> float:
    return round(statistics.median(values), 4)


def run(size: int, family_count: int, repeats: int) -> dict[str, Any]:
    hypotheses, families, likelihoods = make_data(size, family_count)
    target_family = "family-0"
    target_likelihoods = {hypothesis_id: value for hypothesis_id, value in likelihoods.items() if families[hypothesis_id] == target_family}
    dense_likelihoods = {hypothesis_id: (value if families[hypothesis_id] == target_family else 1.0) for hypothesis_id, value in likelihoods.items()}
    global_times: list[float] = []
    family_times: list[float] = []
    global_updates: list[int] = []
    family_updates: list[int] = []

    for repeat in range(repeats):
        global_store = VectorizedHypothesisStore(hypotheses, families=families, elimination_threshold=1e-12)
        started = time.perf_counter()
        global_store.observe(dense_likelihoods, f"global-{repeat}", reason="family-local evidence")
        global_times.append((time.perf_counter() - started) * 1000)
        global_updates.append(global_store.last_update_count)

        family_store = VectorizedHypothesisStore(hypotheses, families=families, elimination_threshold=1e-12)
        started = time.perf_counter()
        family_store.update_families(target_likelihoods, f"family-{repeat}", [target_family], reason="family-local evidence")
        family_times.append((time.perf_counter() - started) * 1000)
        family_updates.append(family_store.last_update_count)

        if family_store.posteriors.tolist() != global_store.posteriors.tolist():
            raise AssertionError("localized update diverged from sparse global update")

    return {
        "hypotheses": size,
        "families": family_count,
        "target_family": target_family,
        "repeats": repeats,
        "global_dense_observe_ms_median": median_ms(global_times),
        "family_update_ms_median": median_ms(family_times),
        "global_dense_updated_hypotheses": max(global_updates),
        "family_updated_hypotheses": max(family_updates),
        "updated_work_reduction_ratio": round(1 - (max(family_updates) / max(global_updates)), 6),
        "posterior_sum": round(float(family_store.posterior_sum()), 12),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypotheses", type=int, default=10_000)
    parser.add_argument("--families", type=int, default=10)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(run(args.hypotheses, args.families, args.repeats), indent=2))


if __name__ == "__main__":
    main()
