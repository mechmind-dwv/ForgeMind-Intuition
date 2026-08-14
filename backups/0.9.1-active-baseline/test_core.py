import random
from forgemind.core import (
    Node,
    TARGETS,
    complexity,
    evolve,
    run,
)
def test_compose():
    p = [Node("U", "rev"), Node("U", "neg")]
    assert run(p, [1, -2, 3]) == [-3, 2, -1]


def test_param():
    assert run([Node("P", "add", 2)], [1, 3]) == [3, 5]


def test_deterministic():
    a = evolve(
        5,
        [Node("U", "rev")],
        8,
        25,
    )[1]

    b = evolve(
        5,
        [Node("U", "rev")],
        8,
        25,
    )[1]

    assert a == b


def test_evolution_returns_evaluated_hypothesis():
    best, history = evolve(
        5,
        [Node("U", "rev")],
        8,
        25,
    )

    assert best.evaluated
    assert best.evaluations > 0


def test_exact_target_can_survive():
    target = [
        Node("U", "abs"),
        Node("P", "add", 1),
    ]

    best, history = evolve(
        29 * 100 + 4,
        target,
        42,
        70,
    )

    probes = [
        [0, 1, 2],
        [-3, -1, 4],
        [5, 0, -2, 7],
    ]

    assert best.evaluated
    assert all(run(best.p, x) == run(target, x) for x in probes)


def test_elite_evaluation_is_preserved():
    target = [Node("U", "rev")]

    best, history = evolve(
        5,
        target,
        8,
        25,
    )

    assert best.evaluated
    assert best.evaluations > 0
    assert best.support + best.failures == best.evaluations


def test_adversarial_accuracy_is_not_failure_only():
    from benchmarks.adversarial.arena import accuracy

    target = [Node("U", "rev")]
    program = [Node("U", "neg")]

    inputs = [
        [1, 2, 3],
        [3, 2, 1],
    ]

    # The suite is an independent evaluation set.
    # It must not be constructed by filtering only mismatches.
    assert accuracy(program, target, inputs) == 0.0


def test_behavior_distance_exact():
    from forgemind.core import behavior_distance

    assert behavior_distance([1, 2, 3], [1, 2, 3]) == 0.0


def test_behavior_distance_prefers_closer_output():
    from forgemind.core import behavior_distance

    close = behavior_distance(
        [1, 2, 4],
        [1, 2, 3],
    )

    far = behavior_distance(
        [10, 20, 30],
        [1, 2, 3],
    )

    assert close < far


def test_behavior_distance_detects_length_difference():
    from forgemind.core import behavior_distance

    assert behavior_distance(
        [1, 2],
        [1, 2, 3],
    ) > 0.0

def test_discovery_rate_records_zero_when_nothing_found():
    from benchmarks.adversarial.arena import adversarial_inputs

    target = [Node("U", "rev")]
    program = target

    found, tested = adversarial_inputs(
        program,
        target,
        random.Random(123),
        count=10,
        candidates=5,
    )

    assert found == []
    assert tested > 0


def test_behaviorally_correct_solution_prefers_lower_complexity():
    from forgemind.core import complexity, behavior_distance

    target = [
        Node("U", "abs"),
        Node("P", "add", 1),
    ]

    redundant = [
        Node("U", "abs"),
        Node("U", "abs"),
        Node("P", "add", 1),
    ]

    assert behavior_distance(
        run(target, [-3, -1, 4]),
        run(redundant, [-3, -1, 4]),
    ) == 0.0

    assert complexity(target) < complexity(redundant)


def test_behaviorally_equivalent_neg_and_mul_minus_one():
    from forgemind.core import behavior_distance

    a = [
        Node("U", "neg"),
    ]

    b = [
        Node("P", "mul", -1),
    ]

    probes = [
        [0, 1, 2],
        [-3, -1, 4],
        [5, 0, -2, 7],
    ]

    assert all(
        behavior_distance(run(a, x), run(b, x)) == 0.0
        for x in probes
    )


def test_parsimony_prefers_simpler_equivalent_program():
    target = [
        Node("U", "rev"),
    ]

    best, history = evolve(
        3,
        target,
        42,
        70,
    )

    assert best.accuracy == 1.0
    assert run(best.p, [1, 2, 3]) == [3, 2, 1]

    # The synthesized solution should not contain gratuitous
    # operations when a simpler equivalent program exists.
    assert complexity(best.p) <= complexity(target) + 0.2


def test_parsimony_prefers_minimal_add():
    target = [
        Node("P", "add", 2),
    ]

    best, history = evolve(
        3 * 100 + 2,
        target,
        42,
        70,
    )

    assert best.accuracy == 1.0
    assert run(best.p, [1, 3, -2]) == [3, 5, 0]
    assert complexity(best.p) <= complexity(target) + 0.2


def test_target_behavior_is_preserved_after_synthesis():
    probes = [
        [-5, -2, 0, 3, 7],
        [-3, -1, 4],
        [0, 1, 2],
        [1, 2, 3],
        [5, 0, -2, 7],
        [9, -4, 2, 6],
    ]

    for i, target in enumerate(TARGETS):
        best, history = evolve(
            3 * 100 + i,
            target,
            42,
            70,
        )

        assert best.accuracy == 1.0

        for x in probes:
            assert run(best.p, x) == run(target, x)
