from pathlib import Path

from forgemind import export_snapshot


def test_export_snapshot_creates_obsidian_project(tmp_path: Path) -> None:
    snapshot = {
        "elimination_threshold": 0.02,
        "min_evidence": 1,
        "beliefs": [
            {
                "hypothesis_id": "h/alpha",
                "description": "Alpha candidate",
                "prior": 0.5,
                "posterior": 0.75,
                "state": "survivor",
                "evidence_ids": ["e-1"],
                "reasons": ["e-1: P(E|H)=0.900 from test"],
                "metadata": {"language": "python"},
            }
        ],
    }

    project_dir = export_snapshot(snapshot, tmp_path, project_name="Demo", project_id="demo project")

    assert project_dir == tmp_path / "ForgeMind" / "Projects" / "demo-project"
    readme = (project_dir / "README.md").read_text(encoding="utf-8")
    note = (project_dir / "hypotheses" / "h-alpha.md").read_text(encoding="utf-8")
    snapshot_json = (project_dir / "snapshot.json").read_text(encoding="utf-8")

    assert "type: \"forgemind-project\"" in readme
    assert "[[hypotheses/h-alpha|h/alpha]]" in readme
    assert "type: \"forgemind-hypothesis\"" in note
    assert "[[../evidence/e-1|e-1]]" in note
    assert '"project_name": "Demo"' in snapshot_json


def test_export_snapshot_rejects_empty_beliefs(tmp_path: Path) -> None:
    try:
        export_snapshot({"beliefs": []}, tmp_path)
    except ValueError as error:
        assert "non-empty beliefs" in str(error)
    else:
        raise AssertionError("empty snapshots must be rejected")
