from benchmarks.ranking_metrics import (
    best_equivalent_rank,
    exact_rank,
    reciprocal_rank,
    summarize_ranks,
    top_k,
)
from forgemind.core import Node


def test_best_equivalent_rank_is_not_exact_program_rank():
    target = [Node("U", "rev")]
    equivalent = [Node("U", "rev"), Node("U", "rev"), Node("U", "rev")]
    distractor = [Node("U", "neg")]
    candidates = [distractor, equivalent]
    probes = [[1, 2], [3, -1, 4]]
    assert exact_rank(candidates, target) is None
    assert best_equivalent_rank(candidates, target, probes) == 2


def test_ranking_summary_reports_mrr_and_top_k():
    summary = summarize_ranks([1, 2, None, 8])
    assert summary["mean_rank"] == (1 + 2 + 8) / 3
    assert summary["mrr"] == (1 + 0.5 + 0 + 0.125) / 4
    assert summary["top_1"] == 0.25
    assert summary["top_5"] == 0.5
    assert top_k(None, 5) is False
    assert reciprocal_rank(None) == 0.0
