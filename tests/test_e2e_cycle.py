from pathlib import Path

from benchmarks.e2e_project_cycle import run_cycle


ROOT = Path(__file__).resolve().parents[1]


def test_reproducible_project_evidence_archive_snapshot_cycle(tmp_path):
    result = run_cycle(
        ROOT / "fixtures/e2e/project.json",
        ROOT / "fixtures/e2e/evidence.json",
        tmp_path,
    )

    assert result["project"] == "sorting-pipeline-e2e"
    assert result["candidate_count"] == 3
    assert result["evidence_count"] == 2
    assert result["posterior_ranking"][0] == "stable-sort"
    assert result["archive"]["size_bytes"] > 0
    assert len(result["archive"]["sha256"]) == 64
    assert result["restoration_verified"] is True
    assert result["engine_contract_version"] == "1.0"
    assert (tmp_path / "snapshot.json").exists()
