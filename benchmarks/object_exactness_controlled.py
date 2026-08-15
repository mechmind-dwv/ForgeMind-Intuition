"""Controlled object-backed exact benchmark for scale feasibility."""
from __future__ import annotations

import argparse
import json
import os
import resource
import time
from math import log

from forgemind.bayesian import BayesianHypothesisSet, EvidenceObservation


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def run(size: int, rounds: int, top_k: int) -> dict[str, object]:
    started = time.perf_counter()
    hypotheses = {f"H{i}": "candidate" for i in range(size)}
    priors = {hypothesis_id: float((index % 23) + 1) for index, hypothesis_id in enumerate(hypotheses)}
    beliefs = BayesianHypothesisSet.from_priors(hypotheses, priors=priors, elimination_threshold=1e-12, min_evidence=2)
    init_ms = (time.perf_counter() - started) * 1000
    observe_ms: list[float] = []
    top_sets: list[set[str]] = []
    for round_index in range(rounds):
        likelihoods = {f"H{i}": 0.8 + ((i * 37 + round_index * 13) % 100_000) * 0.000001 for i in range(size)}
        observation = EvidenceObservation(f"object-probe-{round_index}", "controlled benchmark evidence", likelihoods)
        started = time.perf_counter()
        decisions = beliefs.observe(observation)
        observe_ms.append((time.perf_counter() - started) * 1000)
        top_sets.append({belief.hypothesis_id for belief in beliefs.top_k(top_k)})
    return {
        "hypotheses": size,
        "rounds": rounds,
        "top_k": top_k,
        "init_ms": init_ms,
        "observe_ms_total": sum(observe_ms),
        "rss_peak_mb": rss_mb(),
        "eliminated": sum(1 for decision in decisions if decision.eliminated),
        "top_k_size": len(top_sets[-1]),
        "status": "completed",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypotheses", type=int, required=True)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=25)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.hypotheses, args.rounds, args.top_k), indent=2))
    except (MemoryError, OSError) as error:
        payload = {"hypotheses": args.hypotheses, "status": "memory_limited", "error": type(error).__name__, "message": str(error), "rss_peak_mb": rss_mb()}
        try:
            output = json.dumps(payload, indent=2)
        except MemoryError:
            output = '{\"hypotheses\": %d, \"status\": \"memory_limited\", \"error\": \"MemoryError\"}\n' % args.hypotheses
        os.write(1, output.encode())
        raise SystemExit(137)


if __name__ == "__main__":
    main()
