"""Profile Python metadata allocations during million-hypothesis store construction."""
from __future__ import annotations

import argparse
import gc
import json
import resource
import tracemalloc
from pathlib import Path

import numpy as np

from forgemind.vectorized import VectorizedHypothesisStore


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def snapshot_delta(before: tracemalloc.Snapshot, after: tracemalloc.Snapshot) -> dict[str, object]:
    stats = after.compare_to(before, "lineno")
    positive = [stat for stat in stats if stat.size_diff > 0]
    return {
        "python_bytes_delta": sum(stat.size_diff for stat in positive),
        "python_blocks_delta": sum(stat.count_diff for stat in positive),
        "top_allocations": [
            {"location": str(stat.traceback[0]), "bytes": stat.size_diff, "blocks": stat.count_diff}
            for stat in positive[:12]
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypotheses", type=int, default=1_000_000)
    args = parser.parse_args()
    tracemalloc.start(25)
    stages: list[dict[str, object]] = []
    previous = tracemalloc.take_snapshot()
    stages.append({"stage": "baseline", "rss_mb": rss_mb(), "python_current_bytes": sum(stat.size for stat in previous.statistics("filename"))})

    ids = [f"H{i}" for i in range(args.hypotheses)]
    current = tracemalloc.take_snapshot()
    stages.append({"stage": "ids_list", "rss_mb": rss_mb(), **snapshot_delta(previous, current)})
    previous = current

    hypotheses = {hypothesis_id: "" for hypothesis_id in ids}
    current = tracemalloc.take_snapshot()
    stages.append({"stage": "hypotheses_descriptions_dict", "rss_mb": rss_mb(), **snapshot_delta(previous, current)})
    previous = current

    prior_values = ((np.arange(args.hypotheses, dtype=np.int64) % 23) + 1).astype(np.float64)
    priors = {hypothesis_id: float(prior_values[index]) for index, hypothesis_id in enumerate(ids)}
    current = tracemalloc.take_snapshot()
    stages.append({"stage": "priors_dict_and_source_array", "rss_mb": rss_mb(), **snapshot_delta(previous, current)})
    previous = current

    store = VectorizedHypothesisStore(hypotheses, priors=priors, elimination_threshold=1e-12, min_evidence=2)
    current = tracemalloc.take_snapshot()
    stages.append({"stage": "store_constructor_complete", "rss_mb": rss_mb(), "numeric_state_bytes": store.memory_bytes(), **snapshot_delta(previous, current)})

    # Hold references until the final stage so the profile describes the actual construction footprint.
    metadata = {
        "ids_tuple_bytes_estimate": sum(len(value.encode()) for value in store.ids),
        "index_entries": len(store.index),
        "description_entries": len(store.descriptions),
        "family_entries": len(store.family_by_id),
        "family_position_arrays": len(store.family_positions),
        "explanation_entries": len(store.explanations),
    }
    current = tracemalloc.take_snapshot()
    stages.append({"stage": "metadata_inventory", "rss_mb": rss_mb(), **metadata, **snapshot_delta(previous, current)})

    result = {
        "hypotheses": args.hypotheses,
        "stages": stages,
        "numeric_state_bytes": store.memory_bytes(),
        "rss_peak_mb": max(float(stage["rss_mb"]) for stage in stages),
        "tracemalloc_current_bytes": sum(stat.size for stat in current.statistics("filename")),
        "note": "tracemalloc excludes native NumPy buffers; RSS includes Python objects, NumPy buffers, allocator overhead and imported runtime state.",
    }
    print(json.dumps(result, indent=2))
    del store, priors, hypotheses, ids, prior_values
    gc.collect()


if __name__ == "__main__":
    main()
