import json
import random
from pathlib import Path

from forgemind.core import TARGETS, run, canon
from forgemind.active import build_distractors


SEEDS = (3, 11, 29, 47)
BUDGETS = (1, 2, 4, 8, 12, 16, 24, 32)


def signature(program, probes):
    return tuple(
        repr(run(program, x))
        for x in probes
    )


def _program(obj):
    """
    Normalize a hypothesis/program object for execution.

    Hyp exposes the actual program through .p; raw programs
    are already iterable Node sequences.
    """
    return obj.p if hasattr(obj, "p") else obj


def disagreement(programs, x):
    values = {
        repr(run(_program(p), x))
        for p in programs
    }
    return max(0, len(values) - 1)


def choose_active(programs, candidates):
    return max(
        candidates,
        key=lambda x: disagreement(programs, x),
    )


def choose_passive(rng, candidates):
    return rng.choice(candidates)


def eliminate(programs, target, x):
    y = repr(run(target, x))

    survivors = [
        p for p in programs
        if repr(run(_program(p), x)) == y
    ]

    return survivors


def run_trial(seed, target_index, budget):
    rng = random.Random(seed)

    target = TARGETS[target_index]

    # Probe space used only by the experiment.
    probes = [
        [-5, -2, 0, 3, 7],
        [-3, -1, 4],
        [0, 1, 2],
        [1, 2, 3],
        [5, 0, -2, 7],
        [9, -4, 2, 6],
    ]

    # Additional random candidate experiments.
    candidates = [
        [rng.randint(-12, 12) for _ in range(rng.randint(2, 8))]
        for _ in range(128)
    ]

    candidates.extend(probes)

    distractors = build_distractors(
        target,
        seed=seed,
        count=80,
    )

    # Remove exact structural duplicate of target.
    target_key = canon(target)
    distractors = [
        p for p in distractors
        if canon(p.p) != target_key
    ]

    pool = [target] + distractors

    active_pool = list(pool)
    passive_pool = list(pool)

    active_trace = []
    passive_trace = []

    for q in range(1, budget + 1):
        if len(active_pool) > 1:
            x = choose_active(active_pool, candidates)
            before = len(active_pool)
            active_pool = eliminate(active_pool, target, x)

            active_trace.append({
                "query": q,
                "before": before,
                "after": len(active_pool),
                "eliminated": before - len(active_pool),
                "probe": x,
            })

        if len(passive_pool) > 1:
            x = choose_passive(rng, candidates)
            before = len(passive_pool)
            passive_pool = eliminate(passive_pool, target, x)

            passive_trace.append({
                "query": q,
                "before": before,
                "after": len(passive_pool),
                "eliminated": before - len(passive_pool),
                "probe": x,
            })

    return {
        "seed": seed,
        "target": target_index,
        "budget": budget,
        "initial_hypotheses": len(pool),
        "active_survivors": len(active_pool),
        "passive_survivors": len(passive_pool),
        "active_eliminations": len(pool) - len(active_pool),
        "passive_eliminations": len(pool) - len(passive_pool),
        "active_isolated": len(active_pool) == 1,
        "passive_isolated": len(passive_pool) == 1,
        "active_trace": active_trace,
        "passive_trace": passive_trace,
    }


def main():
    rows = []

    print("===== FORGEMIND ACTIVE DISCOVERY V2 =====")

    for seed in SEEDS:
        for target_index in range(len(TARGETS)):
            for budget in BUDGETS:
                row = run_trial(
                    seed,
                    target_index,
                    budget,
                )

                rows.append(row)

    out = Path("benchmarks/discovery/results.json")
    out.write_text(
        json.dumps(rows, indent=2),
        encoding="utf-8",
    )

    print()
    print("===== SUMMARY BY BUDGET =====")

    for budget in BUDGETS:
        subset = [
            r for r in rows
            if r["budget"] == budget
        ]

        active_survivors = sum(
            r["active_survivors"] for r in subset
        ) / len(subset)

        passive_survivors = sum(
            r["passive_survivors"] for r in subset
        ) / len(subset)

        active_isolation = sum(
            r["active_isolated"] for r in subset
        ) / len(subset)

        passive_isolation = sum(
            r["passive_isolated"] for r in subset
        ) / len(subset)

        active_eliminations = sum(
            r["active_eliminations"] for r in subset
        ) / len(subset)

        passive_eliminations = sum(
            r["passive_eliminations"] for r in subset
        ) / len(subset)

        ratio = (
            active_eliminations / passive_eliminations
            if passive_eliminations
            else float("inf")
        )

        print(
            f"budget={budget:2d} "
            f"active_survivors={active_survivors:.2f} "
            f"passive_survivors={passive_survivors:.2f} "
            f"active_isolation={active_isolation:.3f} "
            f"passive_isolation={passive_isolation:.3f} "
            f"elim_ratio={ratio:.3f}x"
        )

    print()
    print(f"results: {out}")


if __name__ == "__main__":
    main()
