"""Ranking and statistical metrics for ForgeMind 0.16 benchmarks."""

from __future__ import annotations

from statistics import mean
from typing import Any, Callable, Iterable

from forgemind.core import canon, run


def behavior_signature(program: Any, probes: Iterable[Any]) -> tuple[str, ...]:
    p = program.p if hasattr(program, "p") else program
    return tuple(repr(run(p, probe)) for probe in probes)


def rank_of(candidates: list[Any], predicate: Callable[[Any], bool]) -> int | None:
    for index, candidate in enumerate(candidates, start=1):
        if predicate(candidate):
            return index
    return None


def best_equivalent_rank(candidates: list[Any], target: Any, probes: Iterable[Any]) -> int | None:
    target_signature = behavior_signature(target, probes)
    return rank_of(candidates, lambda candidate: behavior_signature(candidate, probes) == target_signature)


def exact_rank(candidates: list[Any], target: Any) -> int | None:
    target_key = canon(target.p if hasattr(target, "p") else target)
    return rank_of(candidates, lambda candidate: canon(candidate.p if hasattr(candidate, "p") else candidate) == target_key)


def reciprocal_rank(rank: int | None) -> float:
    return 0.0 if rank is None or rank <= 0 else 1.0 / rank


def top_k(rank: int | None, k: int) -> bool:
    return rank is not None and 1 <= rank <= k


def evaluations_until_solution(trace: Iterable[dict[str, Any]], *, solution_key: str = "solved") -> int | None:
    for row in trace:
        if row.get(solution_key):
            return int(row.get("query", row.get("evaluation", 0)))
    return None


def summarize_ranks(ranks: Iterable[int | None]) -> dict[str, float | int | None]:
    values = list(ranks)
    observed = [rank for rank in values if rank is not None]
    return {
        "count": len(values),
        "solved": len(observed),
        "mean_rank": mean(observed) if observed else None,
        "mrr": mean(reciprocal_rank(rank) for rank in values) if values else 0.0,
        "top_1": mean(top_k(rank, 1) for rank in values) if values else 0.0,
        "top_5": mean(top_k(rank, 5) for rank in values) if values else 0.0,
        "top_10": mean(top_k(rank, 10) for rank in values) if values else 0.0,
    }
