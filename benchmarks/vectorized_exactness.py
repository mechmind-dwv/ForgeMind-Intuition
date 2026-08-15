"""Compare exact object-backed Bayes updates with the vectorized store."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from typing import Any

from forgemind.bayesian import BayesianHypothesisSet, EvidenceObservation, HypothesisState
from forgemind.vectorized import ELIMINATED, VectorizedHypothesisStore


def make_data(size: int, rounds: int) -> tuple[dict[str, str], dict[str, float], list[dict[str, float]]]:
    hypotheses = {f"H{i}": f"candidate {i}" for i in range(size)}
    priors = {hypothesis_id: float((index % 23) + 1) for index, hypothesis_id in enumerate(hypotheses)}
    observations: list[dict[str, float]] = []
    for round_index in range(rounds):
        observations.append({
            hypothesis_id: 0.8 + ((index * 37 + round_index * 13) % 100_000) * 0.000001
            for index, hypothesis_id in enumerate(hypotheses)
        })
    return hypotheses, priors, observations


def run(size: int, rounds: int, top_k: int, elimination_threshold: float) -> dict[str, Any]:
    hypotheses, priors, observations = make_data(size, rounds)
    exact = BayesianHypothesisSet.from_priors(
        hypotheses,
        priors=priors,
        elimination_threshold=elimination_threshold,
        min_evidence=2,
    )
    vectorized = VectorizedHypothesisStore(
        hypotheses,
        priors=priors,
        elimination_threshold=elimination_threshold,
        min_evidence=2,
    )
    max_errors: list[float] = []
    mean_errors: list[float] = []
    exact_times: list[float] = []
    vector_times: list[float] = []
    top_k_matches: list[bool] = []
    top_k_overlaps: list[float] = []
    eliminated_matches: list[bool] = []

    for round_index, likelihoods in enumerate(observations):
        evidence_id = f"massive-probe-{round_index}"
        observation = EvidenceObservation(evidence_id, "deterministic benchmark evidence", likelihoods, source="benchmark")
        started = time.perf_counter()
        exact.observe(observation)
        exact_times.append((time.perf_counter() - started) * 1000)
        started = time.perf_counter()
        vectorized.observe(likelihoods, evidence_id, reason="benchmark")
        vector_times.append((time.perf_counter() - started) * 1000)

        exact_posteriors = {belief.hypothesis_id: belief.posterior for belief in exact.beliefs()}
        errors = [abs(exact_posteriors[hypothesis_id] - float(vectorized.posteriors[position])) for hypothesis_id, position in vectorized.index.items()]
        max_errors.append(max(errors))
        mean_errors.append(statistics.fmean(errors))
        exact_top = [belief.hypothesis_id for belief in exact.top_k(top_k)]
        vector_top = [belief.hypothesis_id for belief in vectorized.top_k(top_k)]
        exact_top_set = set(exact_top)
        vector_top_set = set(vector_top)
        top_k_matches.append(exact_top_set == vector_top_set)
        top_k_overlaps.append(len(exact_top_set & vector_top_set) / top_k)
        exact_eliminated = {belief.hypothesis_id for belief in exact.beliefs() if belief.state == HypothesisState.ELIMINATED}
        vector_eliminated = {hypothesis_id for hypothesis_id, position in vectorized.index.items() if vectorized.states[position] == ELIMINATED}
        eliminated_matches.append(exact_eliminated == vector_eliminated)

    return {
        "hypotheses": size,
        "rounds": rounds,
        "top_k": top_k,
        "elimination_threshold": elimination_threshold,
        "max_abs_posterior_error": max(max_errors),
        "mean_abs_posterior_error": statistics.fmean(mean_errors),
        "posterior_sum_exact": round(exact.posterior_sum(), 12),
        "posterior_sum_vectorized": round(vectorized.posterior_sum(), 12),
        "top_k_sets_all_rounds_match": all(top_k_matches),
        "top_k_min_overlap": min(top_k_overlaps),
        "eliminated_sets_all_rounds_match": all(eliminated_matches),
        "exact_observe_ms_total": round(sum(exact_times), 4),
        "vectorized_observe_ms_total": round(sum(vector_times), 4),
        "speedup": round(sum(exact_times) / sum(vector_times), 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypotheses", type=int, default=100_000)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=25)
    parser.add_argument("--elimination-threshold", type=float, default=1e-12)
    args = parser.parse_args()
    print(json.dumps(run(args.hypotheses, args.rounds, args.top_k, args.elimination_threshold), indent=2))


if __name__ == "__main__":
    main()
