"""
ForgeMind 0.9.2 research benchmark.

Experimental question:

    Does active counterexample selection eliminate competing
    hypotheses faster than passive random testing?

Active:
    choose x maximizing prediction entropy.

Passive:
    choose x randomly.

The oracle target is never inserted into the competing population.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from forgemind.active import (
    run_active_protocol,
    run_passive_protocol,
)
from forgemind.core import TARGETS, complexity


SEEDS = (3, 11, 29, 47)
ROUNDS = 32
POPULATION = 64
CANDIDATE_BUDGET = 32


def run():
    rows = []

    print("===== FORGEMIND 0.9.2 ACTIVE FALSIFICATION =====")
    print()

    for seed in SEEDS:
        print(f"SEED {seed}")

        for target_index, target in enumerate(TARGETS):
            active = run_active_protocol(
                target_index=target_index,
                seed=seed * 1000 + target_index,
                rounds=ROUNDS,
                population=POPULATION,
                candidate_budget=CANDIDATE_BUDGET,
            )

            passive = run_passive_protocol(
                target_index=target_index,
                seed=seed * 1000 + target_index,
                rounds=ROUNDS,
                population=POPULATION,
            )

            row = {
                "seed": seed,
                "target": target_index,
                "target_complexity": complexity(target),

                "active_survivors": active.survivor_count,
                "active_eliminations": active.eliminations,
                "active_queries": active.oracle_queries,
                "active_complexity": active.complexity,

                "passive_survivors": passive.survivor_count,
                "passive_eliminations": passive.eliminations,
                "passive_queries": passive.oracle_queries,
                "passive_complexity": passive.complexity,

                "active_program": active.program,
                "passive_program": passive.program,
            }

            rows.append(row)

            print(
                f" target={target_index:2d} "
                f"active_elim={active.eliminations:2d} "
                f"passive_elim={passive.eliminations:2d} "
                f"active_survivors={active.survivor_count:2d} "
                f"passive_survivors={passive.survivor_count:2d}"
            )

        print()

    active_elim = [
        r["active_eliminations"]
        for r in rows
    ]

    passive_elim = [
        r["passive_eliminations"]
        for r in rows
    ]

    active_survivors = [
        r["active_survivors"]
        for r in rows
    ]

    passive_survivors = [
        r["passive_survivors"]
        for r in rows
    ]

    active_gain = [
        r["active_eliminations"] / max(r["active_queries"], 1)
        for r in rows
    ]

    passive_gain = [
        r["passive_eliminations"] / max(r["passive_queries"], 1)
        for r in rows
    ]

    print("===== SUMMARY =====")

    print(
        f"active mean eliminations  = "
        f"{statistics.mean(active_elim):.3f}"
    )

    print(
        f"passive mean eliminations = "
        f"{statistics.mean(passive_elim):.3f}"
    )

    print(
        f"active mean survivors     = "
        f"{statistics.mean(active_survivors):.3f}"
    )

    print(
        f"passive mean survivors    = "
        f"{statistics.mean(passive_survivors):.3f}"
    )

    print(
        f"active elimination/query  = "
        f"{statistics.mean(active_gain):.4f}"
    )

    print(
        f"passive elimination/query = "
        f"{statistics.mean(passive_gain):.4f}"
    )

    if statistics.mean(passive_gain) > 0:
        ratio = (
            statistics.mean(active_gain)
            / statistics.mean(passive_gain)
        )
    else:
        ratio = float("inf")

    print(
        f"active/passive efficiency = {ratio:.3f}x"
    )

    result = {
        "version": "0.9.2",
        "protocol": {
            "seeds": list(SEEDS),
            "rounds": ROUNDS,
            "population": POPULATION,
            "candidate_budget": CANDIDATE_BUDGET,
        },
        "rows": rows,
        "summary": {
            "active_mean_eliminations": statistics.mean(active_elim),
            "passive_mean_eliminations": statistics.mean(passive_elim),
            "active_mean_survivors": statistics.mean(active_survivors),
            "passive_mean_survivors": statistics.mean(passive_survivors),
            "active_elimination_per_query": statistics.mean(active_gain),
            "passive_elimination_per_query": statistics.mean(passive_gain),
            "active_passive_efficiency_ratio": ratio,
        },
    }

    output = Path(
        "benchmarks/active_vs_passive/results.json"
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        json.dumps(
            result,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print()
    print(f"results: {output}")


if __name__ == "__main__":
    run()
