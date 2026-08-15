"""Benchmark reversible upper-bound pruning for Bayesian hypotheses."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from typing import Any

from forgemind.bayesian import BayesianHypothesisSet, HypothesisState


def run(size: int, repeats: int, threshold: float, remaining_evidence: int, minimum_likelihood: float) -> dict[str, Any]:
    hypotheses = {f"H{i}": f"candidate {i}" for i in range(size)}
    priors = {hypothesis_id: float((index % 17) + 1) for index, hypothesis_id in enumerate(hypotheses)}
    timings: list[float] = []
    parked_counts: list[int] = []
    for repeat in range(repeats):
        store = BayesianHypothesisSet.from_priors(hypotheses, priors=priors, elimination_threshold=1e-12)
        started = time.perf_counter()
        decisions = store.prune_by_upper_bound(
            threshold=threshold,
            remaining_evidence=remaining_evidence,
            minimum_likelihood=minimum_likelihood,
        )
        timings.append((time.perf_counter() - started) * 1000)
        parked_counts.append(sum(decision.state == HypothesisState.PARKED for decision in decisions))
    return {
        "hypotheses": size,
        "repeats": repeats,
        "threshold": threshold,
        "remaining_evidence": remaining_evidence,
        "minimum_likelihood": minimum_likelihood,
        "upper_bound_prune_ms_median": round(statistics.median(timings), 4),
        "parked_hypotheses": max(parked_counts),
        "reversible_decisions": max(parked_counts),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypotheses", type=int, default=10_000)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--threshold", type=float, default=0.02)
    parser.add_argument("--remaining-evidence", type=int, default=3)
    parser.add_argument("--minimum-likelihood", type=float, default=0.9)
    args = parser.parse_args()
    print(json.dumps(run(args.hypotheses, args.repeats, args.threshold, args.remaining_evidence, args.minimum_likelihood), indent=2))


if __name__ == "__main__":
    main()
