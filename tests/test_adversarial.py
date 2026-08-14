from forgemind.core import Node, run
from benchmarks.adversarial.arena import (
    accuracy,
    first_counterexample,
)


def test_accuracy_perfect_program():
    target = [Node("U", "rev")]
    inputs = [[1, 2, 3], [4, 5], [-1, 7, 9]]

    assert accuracy(target, target, inputs) == 1.0


def test_counterexample_is_found():
    target = [Node("U", "rev")]
    wrong = [Node("U", "neg")]

    inputs = [
        [1, 2, 3],
        [-4, 5],
    ]

    assert first_counterexample(wrong, target, inputs) == 0


def test_accuracy_detects_failure():
    target = [Node("U", "rev")]
    wrong = [Node("U", "neg")]

    inputs = [[1, 2, 3]]

    assert accuracy(wrong, target, inputs) == 0.0
