from __future__ import annotations

import json
import random
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path

from forgemind.core import TARGETS, Node, run, evolve, xgen


@dataclass
class CaseResult:
    seed: int
    target: int
    random_accuracy: float
    adversarial_accuracy: float
    random_mismatches: int
    adversarial_mismatches: int
    first_counterexample: int | None
    discovery_tested: int
    discovery_found: int
    discovery_rate: float


def random_inputs(rng, count=200):
    return [xgen(rng) for _ in range(count)]


def adversarial_inputs(
    program,
    target,
    rng,
    count=200,
    candidates=100,
):
    found = []
    tested = 0

    while len(found) < count and tested < count * 20:
        batch = [xgen(rng) for _ in range(candidates)]
        tested += len(batch)

        for x in batch:
            if run(program, x) != run(target, x):
                found.append(x)

                if len(found) >= count:
                    break

    return found, tested


def accuracy(program, target, inputs):
    if not inputs:
        return 1.0

    return sum(
        run(program, x) == run(target, x)
        for x in inputs
    ) / len(inputs)


def first_counterexample(program, target, inputs):
    for i, x in enumerate(inputs):
        if run(program, x) != run(target, x):
            return i

    return None


def run_case(seed, target_index):
    target = TARGETS[target_index]

    search_seed = seed * 1000 + target_index

    best, history = evolve(
        search_seed,
        target,
        rounds=42,
        pop=70,
    )

    random_rng = random.Random(
        seed * 10000 + target_index
    )

    adversarial_rng = random.Random(
        seed * 20000 + target_index
    )

    # Candidate-independent evaluation suite.
    # It is generated independently from the discovery search.
    evaluation_rng = random.Random(
        seed * 30000 + target_index
    )

    random_set = random_inputs(
        random_rng,
        200,
    )

    adversarial_found, discovery_tested = adversarial_inputs(
        best.p,
        target,
        adversarial_rng,
        count=200,
    )

    # IMPORTANT:
    # Do NOT calculate adversarial accuracy on `adversarial_found`.
    #
    # `adversarial_found` contains only inputs where the candidate
    # already disagrees with the target. Accuracy on that set would
    # therefore be structurally biased toward zero.
    #
    # The adversarial accuracy suite is candidate-independent.
    adversarial_set = random_inputs(
        evaluation_rng,
        200,
    )

    random_acc = accuracy(
        best.p,
        target,
        random_set,
    )

    adversarial_acc = accuracy(
        best.p,
        target,
        adversarial_set,
    )

    discovery_found = len(adversarial_found)

    discovery_rate = (
        discovery_found / discovery_tested
        if discovery_tested
        else 0.0
    )

    combined = random_set + adversarial_set

    return CaseResult(
        seed=seed,
        target=target_index,
        random_accuracy=random_acc,
        adversarial_accuracy=adversarial_acc,
        random_mismatches=round(
            (1 - random_acc) * len(random_set)
        ),
        adversarial_mismatches=round(
            (1 - adversarial_acc) * len(adversarial_set)
        ),
        first_counterexample=first_counterexample(
            best.p,
            target,
            combined,
        ),
        discovery_tested=discovery_tested,
        discovery_found=discovery_found,
        discovery_rate=discovery_rate,
    )


def main():
    seeds = [3, 11, 29, 47]
    results = []

    for seed in seeds:
        for target_index in range(len(TARGETS)):
            print(
                f"[seed={seed} target={target_index}]",
                flush=True,
            )

            result = run_case(
                seed,
                target_index,
            )

            results.append(result)

            print(
                f"  random={result.random_accuracy:.3f} "
                f"adversarial={result.adversarial_accuracy:.3f} "
                f"discovery={result.discovery_found}/"
                f"{result.discovery_tested} "
                f"({result.discovery_rate:.4f})",
                flush=True,
            )

    random_scores = [
        r.random_accuracy
        for r in results
    ]

    adversarial_scores = [
        r.adversarial_accuracy
        for r in results
    ]

    summary = {
        "version": "0.9.1-adversarial",
        "cases": len(results),
        "random_mean": statistics.mean(
            random_scores
        ),
        "random_median": statistics.median(
            random_scores
        ),
        "adversarial_mean": statistics.mean(
            adversarial_scores
        ),
        "adversarial_median": statistics.median(
            adversarial_scores
        ),
        "equivalence_gap": (
            statistics.mean(random_scores)
            - statistics.mean(adversarial_scores)
        ),
        "perfect_random": sum(
            x == 1
            for x in random_scores
        ),
        "perfect_adversarial": sum(
            x == 1
            for x in adversarial_scores
        ),
        "discovery_tested": sum(
            r.discovery_tested
            for r in results
        ),
        "discovery_found": sum(
            r.discovery_found
            for r in results
        ),
        "discovery_rate": (
            sum(r.discovery_found for r in results)
            / sum(r.discovery_tested for r in results)
        ),
        "results": [
            asdict(r)
            for r in results
        ],
    }

    output = Path(
        "benchmarks/adversarial/results.json"
    )

    output.write_text(
        json.dumps(
            summary,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("===== FORGEMIND 0.9.1 ADVERSARIAL =====")
    print("cases =", summary["cases"])
    print(
        "random mean =",
        round(summary["random_mean"], 4),
    )
    print(
        "adversarial mean =",
        round(summary["adversarial_mean"], 4),
    )
    print(
        "equivalence gap =",
        round(summary["equivalence_gap"], 4),
    )
    print(
        "perfect random =",
        summary["perfect_random"],
        "/",
        summary["cases"],
    )
    print(
        "perfect adversarial =",
        summary["perfect_adversarial"],
        "/",
        summary["cases"],
    )
    print(
        "discovery found =",
        summary["discovery_found"],
        "/",
        summary["discovery_tested"],
    )
    print(
        "discovery rate =",
        round(summary["discovery_rate"], 6),
    )
    print()
    print("results:", output)


if __name__ == "__main__":
    main()
