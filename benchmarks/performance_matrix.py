"""Versioned performance regression matrix for probabilistic integration.

Example:
    python benchmarks/performance_matrix.py --sizes 10000,50000,100000
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.probabilistic_protocol import run  # noqa: E402

MATRIX_VERSION = "1.0"


def evaluate_row(
    result: dict[str, Any],
    *,
    max_vectorized_ms: float,
    max_rss_mb: float,
    max_posterior_error: float,
    min_top_k_overlap: float,
) -> dict[str, Any]:
    checks = {
        "latency": result["vectorized_observe_ms_median"] <= max_vectorized_ms,
        "rss": result["rss_peak_bytes"] <= max_rss_mb * 1024 * 1024,
        "exactness": result["max_abs_posterior_error"] <= max_posterior_error,
        "top_k": result["top_k_min_overlap"] >= min_top_k_overlap,
        "eliminations": result["eliminated_sets_all_match"],
        "traceability": result["traceability_all_match"],
    }
    return {
        "hypotheses": result["hypotheses"],
        "vectorized_observe_ms_median": result["vectorized_observe_ms_median"],
        "rss_peak_mb": round(result["rss_peak_bytes"] / (1024 * 1024), 4),
        "max_abs_posterior_error": result["max_abs_posterior_error"],
        "top_k_min_overlap": result["top_k_min_overlap"],
        "checks": checks,
        "passed": all(checks.values()),
    }


def run_matrix(
    sizes: list[int],
    *,
    rounds: int,
    repeats: int,
    top_k: int,
    max_vectorized_ms: float,
    max_rss_mb: float,
    max_posterior_error: float,
    min_top_k_overlap: float,
) -> dict[str, Any]:
    rows = []
    for size in sizes:
        result = run(size, rounds, top_k, repeats, 1e-12)
        rows.append(evaluate_row(
            result,
            max_vectorized_ms=max_vectorized_ms,
            max_rss_mb=max_rss_mb,
            max_posterior_error=max_posterior_error,
            min_top_k_overlap=min_top_k_overlap,
        ))
    return {
        "matrix_version": MATRIX_VERSION,
        "rounds": rounds,
        "repeats": repeats,
        "top_k": top_k,
        "thresholds": {
            "max_vectorized_observe_ms_median": max_vectorized_ms,
            "max_rss_mb": max_rss_mb,
            "max_abs_posterior_error": max_posterior_error,
            "min_top_k_overlap": min_top_k_overlap,
        },
        "rows": rows,
        "passed": all(row["passed"] for row in rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", default="10000,50000,100000")
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=25, dest="top_k")
    parser.add_argument("--max-vectorized-ms", type=float, default=5000.0)
    parser.add_argument("--max-rss-mb", type=float, default=1024.0)
    parser.add_argument("--max-posterior-error", type=float, default=1e-12)
    parser.add_argument("--min-top-k-overlap", type=float, default=1.0)
    args = parser.parse_args()
    sizes = [int(item.strip()) for item in args.sizes.split(",") if item.strip()]
    if not sizes or min(sizes) < 1:
        parser.error("sizes must contain positive integers")
    result = run_matrix(
        sizes,
        rounds=args.rounds,
        repeats=args.repeats,
        top_k=args.top_k,
        max_vectorized_ms=args.max_vectorized_ms,
        max_rss_mb=args.max_rss_mb,
        max_posterior_error=args.max_posterior_error,
        min_top_k_overlap=args.min_top_k_overlap,
    )
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
