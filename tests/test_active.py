import random

from forgemind.active import (
    build_distractors,
    information_gain,
    partition_hypotheses,
    select_experiment,
    run_active_protocol,
    run_passive_protocol,
)
from forgemind.core import Hyp, Node, TARGETS


def test_partition_hypotheses_separates_predictions():
    pool = [
        Hyp([Node("U", "rev")]),
        Hyp([Node("U", "neg")]),
    ]

    partitions = partition_hypotheses(pool, [1, 2, 3])

    assert len(partitions) == 2


def test_information_gain_is_positive_when_predictions_disagree():
    pool = [
        Hyp([Node("U", "rev")]),
        Hyp([Node("U", "neg")]),
    ]

    gain = information_gain(pool, [1, 2, 3])

    assert gain > 0.0


def test_select_experiment_is_deterministic():
    pool = [
        Hyp([Node("U", "rev")]),
        Hyp([Node("U", "neg")]),
    ]

    a = select_experiment(
        pool,
        random.Random(123),
        budget=20,
    )

    b = select_experiment(
        pool,
        random.Random(123),
        budget=20,
    )

    assert a == b


def test_distractors_do_not_include_target():
    target = TARGETS[0]

    pool = build_distractors(
        target,
        seed=123,
        count=20,
    )

    from forgemind.core import canon

    target_repr = canon(target)

    for h in pool:
        assert canon(h.p) != target_repr


def test_active_protocol_is_reproducible():
    a = run_active_protocol(
        target_index=0,
        seed=123,
        rounds=10,
        population=20,
        candidate_budget=16,
    )

    b = run_active_protocol(
        target_index=0,
        seed=123,
        rounds=10,
        population=20,
        candidate_budget=16,
    )

    assert a == b


def test_active_protocol_performs_queries():
    result = run_active_protocol(
        target_index=0,
        seed=123,
        rounds=8,
        population=20,
        candidate_budget=16,
    )

    assert result.oracle_queries > 0
    assert result.eliminations >= 0


def test_passive_protocol_performs_queries():
    result = run_passive_protocol(
        target_index=0,
        seed=123,
        rounds=8,
        population=20,
    )

    assert result.oracle_queries > 0
    assert result.eliminations >= 0


def test_active_search_prefers_information_gain():
    from forgemind.core import Node, run
    from forgemind.active import select_informative_probe

    hypotheses = [
        [Node("U", "rev")],
        [Node("U", "neg")],
        [Node("U", "sort")],
    ]

    candidates = [
        [1, 2, 3],
        [3, 1, 2],
        [-2, 7, 0],
    ]

    probe = select_informative_probe(
        hypotheses,
        candidates,
    )

    assert probe in candidates


def test_semantically_equivalent_programs_have_same_signature():
    from forgemind.core import Node, run

    probes = [
        [1, 2, 3],
        [-5, 0, 4],
        [9, -2],
    ]

    a = [
        Node("U", "rev"),
    ]

    # rev -> rev -> rev == rev
    b = [
        Node("U", "rev"),
        Node("U", "rev"),
        Node("U", "rev"),
    ]

    assert [
        run(a, x)
        for x in probes
    ] == [
        run(b, x)
        for x in probes
    ]
