"""
ForgeMind Active Falsification Engine.

Experimental layer for studying active program synthesis.

Core loop:

    hypotheses
        ↓
    discriminative input
        ↓
    oracle evaluation
        ↓
    falsification
        ↓
    survivor set
        ↓
    recombination / mutation

The module deliberately keeps the experimental protocol separate from
the production evolution loop in core.py.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Iterable

from .core import (
    Hyp,
    Node,
    TARGETS,
    canon,
    complexity,
    disagreement,
    generator,
    mutate,
    run,
    xgen,
)


@dataclass
class ActiveRound:
    round_id: int
    x: list[int]
    target_output: Any
    hypotheses_before: int
    hypotheses_after: int
    eliminated: int
    disagreement: float
    information_gain: float


@dataclass
class ActiveResult:
    target_index: int
    survivor_count: int
    rounds: int
    oracle_queries: int
    eliminations: int
    program: tuple
    complexity: float
    rounds_data: list[ActiveRound]


def _safe_output(value: Any) -> Any:
    """
    Convert outputs into a stable comparable representation.
    """
    if isinstance(value, list):
        return tuple(_safe_output(v) for v in value)

    if isinstance(value, tuple):
        return tuple(_safe_output(v) for v in value)

    if isinstance(value, dict):
        return tuple(
            sorted(
                (k, _safe_output(v))
                for k, v in value.items()
            )
        )

    return value


def _prediction_signature(h: Hyp, x: list[int]) -> Any:
    """
    Canonical prediction used to partition hypotheses.
    """
    try:
        return _safe_output(run(h.p, x))
    except Exception as exc:
        return ("__ERROR__", type(exc).__name__, str(exc))


def partition_hypotheses(
    pool: Iterable[Hyp],
    x: list[int],
) -> dict[Any, list[Hyp]]:
    """
    Partition hypotheses according to their prediction on x.
    """
    partitions: dict[Any, list[Hyp]] = {}

    for h in pool:
        key = _prediction_signature(h, x)
        partitions.setdefault(key, []).append(h)

    return partitions


def information_gain(
    pool: Iterable[Hyp],
    x: list[int],
) -> float:
    """
    Shannon entropy of the prediction partition.

    High entropy means that x strongly separates the current
    hypothesis population.
    """
    pool = list(pool)

    if not pool:
        return 0.0

    partitions = partition_hypotheses(pool, x)

    n = len(pool)
    entropy = 0.0

    for group in partitions.values():
        p = len(group) / n
        entropy -= p * math.log2(p)

    return entropy


def select_experiment(
    pool: Iterable[Hyp],
    rng: random.Random,
    budget: int = 32,
) -> tuple[list[int], float]:
    """
    Actively select the input expected to provide the most
    information about the current hypothesis population.

    Selection is based on prediction entropy, not merely on
    random sampling.
    """
    pool = list(pool)

    if not pool:
        raise ValueError("Cannot select an experiment from an empty pool")

    candidates = [xgen(rng) for _ in range(budget)]

    best_x = candidates[0]
    best_gain = information_gain(pool, best_x)

    for x in candidates[1:]:
        gain = information_gain(pool, x)

        if gain > best_gain:
            best_x = x
            best_gain = gain

    return best_x, best_gain


def passive_experiment(
    rng: random.Random,
) -> list[int]:
    """
    Passive baseline: select an input uniformly from the generator.
    """
    return xgen(rng)


def falsify_once(
    pool: list[Hyp],
    target: list[Node],
    x: list[int],
) -> tuple[Any, int]:
    """
    Evaluate the oracle once and eliminate every hypothesis
    that disagrees with it.
    """
    y = run(target, x)

    before = len(pool)

    survivors: list[Hyp] = []

    for h in pool:
        try:
            prediction = run(h.p, x)
        except Exception:
            prediction = object()

        h.evaluations += 1

        if _safe_output(prediction) == _safe_output(y):
            h.support += 1
            survivors.append(h)
        else:
            h.failures += 1

    pool[:] = survivors

    return y, before - len(pool)


def build_distractors(
    target: list[Node],
    seed: int,
    count: int = 64,
) -> list[Hyp]:
    """
    Generate mutated competitors around the target.

    The target itself is intentionally NOT inserted here.
    """
    rng = random.Random(seed)

    pool: list[Hyp] = []

    seen: set[tuple] = set()

    attempts = 0
    max_attempts = count * 20

    while len(pool) < count and attempts < max_attempts:
        attempts += 1

        candidate = list(target)
        candidate = mutate(candidate, rng)

        key = canon(candidate)

        if key in seen:
            continue

        if key == canon(target):
            continue

        seen.add(key)
        pool.append(Hyp(candidate))

    return pool


def run_active_protocol(
    target_index: int,
    seed: int,
    rounds: int = 32,
    population: int = 64,
    candidate_budget: int = 32,
) -> ActiveResult:
    """
    Run active falsification against a population of distractors.
    """
    target = TARGETS[target_index]

    pool = build_distractors(
        target,
        seed=seed,
        count=population,
    )

    rng = random.Random(seed + 100_003)

    rounds_data: list[ActiveRound] = []
    total_eliminated = 0

    for r in range(rounds):
        if not pool:
            break

        before = len(pool)

        x, gain = select_experiment(
            pool,
            rng,
            budget=candidate_budget,
        )

        y, eliminated = falsify_once(
            pool,
            target,
            x,
        )

        after = len(pool)

        total_eliminated += eliminated

        rounds_data.append(
            ActiveRound(
                round_id=r,
                x=x,
                target_output=y,
                hypotheses_before=before,
                hypotheses_after=after,
                eliminated=eliminated,
                disagreement=disagreement(pool, x) if pool else 0.0,
                information_gain=gain,
            )
        )

    if pool:
        best = min(
            pool,
            key=lambda h: complexity(h.p),
        )

        program = canon(best.p)
        best_complexity = complexity(best.p)
    else:
        program = ()
        best_complexity = float("inf")

    return ActiveResult(
        target_index=target_index,
        survivor_count=len(pool),
        rounds=len(rounds_data),
        oracle_queries=len(rounds_data),
        eliminations=total_eliminated,
        program=program,
        complexity=best_complexity,
        rounds_data=rounds_data,
    )


def run_passive_protocol(
    target_index: int,
    seed: int,
    rounds: int = 32,
    population: int = 64,
) -> ActiveResult:
    """
    Random-input baseline.
    """
    target = TARGETS[target_index]

    pool = build_distractors(
        target,
        seed=seed,
        count=population,
    )

    rng = random.Random(seed + 100_003)

    rounds_data: list[ActiveRound] = []
    total_eliminated = 0

    for r in range(rounds):
        if not pool:
            break

        before = len(pool)

        x = passive_experiment(rng)

        y, eliminated = falsify_once(
            pool,
            target,
            x,
        )

        after = len(pool)

        total_eliminated += eliminated

        rounds_data.append(
            ActiveRound(
                round_id=r,
                x=x,
                target_output=y,
                hypotheses_before=before,
                hypotheses_after=after,
                eliminated=eliminated,
                disagreement=0.0,
                information_gain=information_gain(pool, x) if pool else 0.0,
            )
        )

    if pool:
        best = min(
            pool,
            key=lambda h: complexity(h.p),
        )

        program = canon(best.p)
        best_complexity = complexity(best.p)
    else:
        program = ()
        best_complexity = float("inf")

    return ActiveResult(
        target_index=target_index,
        survivor_count=len(pool),
        rounds=len(rounds_data),
        oracle_queries=len(rounds_data),
        eliminations=total_eliminated,
        program=program,
        complexity=best_complexity,
        rounds_data=rounds_data,
    )

def select_informative_probe(
    hypotheses,
    candidates,
):
    """
    Select the most informative probe from an explicit candidate set.

    Unlike select_experiment(), this function does not generate probes.
    It evaluates the supplied candidates directly using prediction entropy.

    API:
        select_informative_probe(hypotheses, candidates) -> probe
    """
    hypotheses = list(hypotheses)
    candidates = list(candidates)

    if not hypotheses:
        raise ValueError("hypotheses cannot be empty")

    if not candidates:
        raise ValueError("candidates cannot be empty")

    best_probe = candidates[0]
    best_gain = information_gain(
        [h if isinstance(h, Hyp) else Hyp(list(h)) for h in hypotheses],
        best_probe,
    )

    for candidate in candidates[1:]:
        gain = information_gain(
            [h if isinstance(h, Hyp) else Hyp(list(h)) for h in hypotheses],
            candidate,
        )

        if gain > best_gain:
            best_probe = candidate
            best_gain = gain

    return best_probe

def select_informative_probe(
    hypotheses,
    candidates,
):
    """
    Select the most informative probe from an explicit candidate set.

    Unlike select_experiment(), this function does not generate probes.
    It evaluates the supplied candidates directly using prediction entropy.

    API:
        select_informative_probe(hypotheses, candidates) -> probe
    """
    hypotheses = list(hypotheses)
    candidates = list(candidates)

    if not hypotheses:
        raise ValueError("hypotheses cannot be empty")

    if not candidates:
        raise ValueError("candidates cannot be empty")

    best_probe = candidates[0]
    best_gain = information_gain(
        [h if isinstance(h, Hyp) else Hyp(list(h)) for h in hypotheses],
        best_probe,
    )

    for candidate in candidates[1:]:
        gain = information_gain(
            [h if isinstance(h, Hyp) else Hyp(list(h)) for h in hypotheses],
            candidate,
        )

        if gain > best_gain:
            best_probe = candidate
            best_gain = gain

    return best_probe
