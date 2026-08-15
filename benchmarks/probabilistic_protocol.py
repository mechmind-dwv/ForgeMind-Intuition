"""Stable probabilistic integration benchmark.

The benchmark uses deterministic evidence and emits a versioned JSON contract.
It is intended for local regression tracking, not as a cross-machine SLA.

Example:
    python benchmarks/probabilistic_protocol.py --hypotheses 10000 --rounds 3 --repeats 3
"""

from __future__ import annotations

import argparse
import json
import resource
import statistics
import time
import tracemalloc
from typing import Any

from forgemind.bayesian import BayesianHypothesisSet, EvidenceObservation, HypothesisState
from forgemind.vectorized import ELIMINATED, VectorizedHypothesisStore

PROTOCOL_VERSION = "1.0"


def rss_bytes() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)


def make_data(size: int, rounds: int) -> tuple[dict[str, str], dict[str, float], list[dict[str, float]]]:
    hypotheses = {f"H{i}": f"candidate {i}" for i in range(size)}
    priors = {hypothesis_id: float((index % 23) + 1) for index, hypothesis_id in enumerate(hypotheses)}
    observations = [
        {
            hypothesis_id: 0.8 + ((index * 37 + round_index * 13) % 100_000) * 0.000001
            for index, hypothesis_id in enumerate(hypotheses)
        }
        for round_index in range(rounds)
    ]
    return hypotheses, priors, observations


def run(size: int, rounds: int, top_k: int, repeats: int, elimination_threshold: float) -> dict[str, Any]:
    exact_times: list[float] = []
    vectorized_times: list[float] = []
    exact_memory_peaks: list[int] = []
    vectorized_memory_peaks: list[int] = []
    max_errors: list[float] = []
    mean_errors: list[float] = []
    top_k_overlaps: list[float] = []
    eliminated_matches: list[bool] = []
    trace_matches: list[bool] = []
    final_exact: BayesianHypothesisSet | None = None
    final_vectorized: VectorizedHypothesisStore | None = None

    for repeat in range(repeats):
        hypotheses, priors, observations = make_data(size, rounds)
        exact = BayesianHypothesisSet.from_priors(
            hypotheses, priors=priors, elimination_threshold=elimination_threshold, min_evidence=2
        )
        vectorized = VectorizedHypothesisStore(
            hypotheses, priors=priors, elimination_threshold=elimination_threshold, min_evidence=2
        )
        exact_round_times: list[float] = []
        vectorized_round_times: list[float] = []
        exact_peak = 0
        vectorized_peak = 0

        for round_index, likelihoods in enumerate(observations):
            evidence_id = f"protocol-{repeat}-{round_index}"
            observation = EvidenceObservation(
                evidence_id,
                "deterministic protocol evidence",
                likelihoods,
                source="benchmark",
            )
            tracemalloc.start()
            started = time.perf_counter()
            exact_decisions = exact.observe(observation)
            exact_round_times.append((time.perf_counter() - started) * 1000)
            _, exact_current_peak = tracemalloc.get_traced_memory()
            exact_peak = max(exact_peak, exact_current_peak)
            tracemalloc.stop()

            tracemalloc.start()
            started = time.perf_counter()
            vectorized.observe(likelihoods, evidence_id, reason="deterministic protocol evidence")
            vectorized_round_times.append((time.perf_counter() - started) * 1000)
            _, vectorized_current_peak = tracemalloc.get_traced_memory()
            vectorized_peak = max(vectorized_peak, vectorized_current_peak)
            tracemalloc.stop()

            exact_posteriors = {belief.hypothesis_id: belief.posterior for belief in exact.beliefs()}
            errors = [
                abs(exact_posteriors[hypothesis_id] - float(vectorized.posteriors[position]))
                for hypothesis_id, position in vectorized.index.items()
            ]
            max_errors.append(max(errors))
            mean_errors.append(statistics.fmean(errors))
            exact_top = {belief.hypothesis_id for belief in exact.top_k(top_k)}
            vector_top = {belief.hypothesis_id for belief in vectorized.top_k(top_k)}
            top_k_overlaps.append(len(exact_top & vector_top) / min(top_k, size))
            exact_eliminated = {
                belief.hypothesis_id for belief in exact.beliefs() if belief.state == HypothesisState.ELIMINATED
            }
            vector_eliminated = {
                hypothesis_id for hypothesis_id, position in vectorized.index.items() if vectorized.states[position] == ELIMINATED
            }
            eliminated_matches.append(exact_eliminated == vector_eliminated)
            exact_trace = {
                belief.hypothesis_id: tuple(belief.evidence_ids)
                for belief in exact.beliefs()
                if belief.evidence_ids
            }
            vector_trace = {
                vectorized.ids[position]: tuple(vectorized.explanations.get(position, ()))
                for position in range(size)
                if position in vectorized.explanations
            }
            trace_matches.append(
                set(exact_trace) == set(vector_trace)
                and all(len(ids) == round_index + 1 for ids in exact_trace.values())
                and all(len(reasons) == round_index + 1 for reasons in vector_trace.values())
            )
            assert len(exact_decisions) == size

        exact_times.extend(exact_round_times)
        vectorized_times.extend(vectorized_round_times)
        exact_memory_peaks.append(exact_peak)
        vectorized_memory_peaks.append(vectorized_peak)
        final_exact = exact
        final_vectorized = vectorized

    assert final_exact is not None and final_vectorized is not None
    return {
        "protocol_version": PROTOCOL_VERSION,
        "hypotheses": size,
        "rounds": rounds,
        "repeats": repeats,
        "top_k": top_k,
        "elimination_threshold": elimination_threshold,
        "exact_observe_ms_median": round(statistics.median(exact_times), 4),
        "vectorized_observe_ms_median": round(statistics.median(vectorized_times), 4),
        "exact_memory_peak_bytes_max": max(exact_memory_peaks),
        "vectorized_memory_peak_bytes_max": max(vectorized_memory_peaks),
        "rss_peak_bytes": rss_bytes(),
        "max_abs_posterior_error": max(max_errors),
        "mean_abs_posterior_error": statistics.fmean(mean_errors),
        "posterior_sum_exact": final_exact.posterior_sum(),
        "posterior_sum_vectorized": final_vectorized.posterior_sum(),
        "top_k_min_overlap": min(top_k_overlaps),
        "eliminated_sets_all_match": all(eliminated_matches),
        "traceability_all_match": all(trace_matches),
        "traceable_hypotheses_exact": sum(bool(belief.evidence_ids) for belief in final_exact.beliefs()),
        "traceable_hypotheses_vectorized": len(final_vectorized.explanations),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hypotheses", type=int, default=10_000)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=25, dest="top_k")
    parser.add_argument("--elimination-threshold", type=float, default=1e-12)
    args = parser.parse_args()
    if min(args.hypotheses, args.rounds, args.repeats, args.top_k) < 1:
        parser.error("hypotheses, rounds, repeats and top-k must be positive")
    print(json.dumps(run(args.hypotheses, args.rounds, args.top_k, args.repeats, args.elimination_threshold), indent=2))


if __name__ == "__main__":
    main()
