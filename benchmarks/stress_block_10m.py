"""Memory-bounded 10-million hypothesis stress test for BlockExactHypothesisSet."""
from __future__ import annotations

import json
import os
import resource
import time

import numpy as np

from forgemind import BlockExactHypothesisSet


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def main() -> None:
    size = 10_000_000
    rounds = 3
    block_size = 65_536
    started = time.perf_counter()
    try:
        indices = np.arange(size, dtype=np.int64)
        priors = ((indices % 23) + 1).astype(np.float64)
        store = BlockExactHypothesisSet(priors, block_size=block_size, elimination_threshold=1e-12, min_evidence=2)
        rss_after_init = rss_mb()
        round_ms: list[float] = []
        for round_index in range(rounds):
            likelihoods = 0.8 + ((indices * 37 + round_index * 13) % 100_000) * 0.000001
            round_started = time.perf_counter()
            store.observe_arrays(likelihoods, f"stress-{round_index}")
            round_ms.append((time.perf_counter() - round_started) * 1000)
            del likelihoods
        top_positions = store.top_k_positions(25)
        result = {
            "status": "completed",
            "hypotheses": size,
            "rounds": rounds,
            "block_size": block_size,
            "posterior_sum": float(store.posteriors.sum()),
            "top_k_size": int(top_positions.size),
            "eliminated": int(np.count_nonzero(store.states == 2)),
            "numeric_state_bytes": store.memory_bytes(),
            "rss_after_init_mb": rss_after_init,
            "rss_peak_mb": rss_mb(),
            "round_ms": round_ms,
            "total_ms": (time.perf_counter() - started) * 1000,
            "note": "Numeric-only block stress test; no Python IDs, descriptions, or dictionaries are materialized.",
        }
    except (MemoryError, OSError) as error:
        result = {
            "status": "memory_limited",
            "hypotheses": size,
            "block_size": block_size,
            "error": type(error).__name__,
            "message": str(error),
            "rss_peak_mb": rss_mb(),
        }
    try:
        print(json.dumps(result, indent=2))
    except MemoryError:
        os.write(1, b'{"status":"memory_limited","hypotheses":10000000,"error":"MemoryError"}\n')
        raise SystemExit(137)


if __name__ == "__main__":
    main()
