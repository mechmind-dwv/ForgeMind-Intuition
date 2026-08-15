"""Reproducible project-to-snapshot E2E cycle using repository fixtures.

Run from the repository root:
    python benchmarks/e2e_project_cycle.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from forgemind.bayesian import BayesianHypothesisSet, EvidenceObservation
from forgemind.project import ForgeMindProject
from services.engine_api import EvaluateRequest, evaluate

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT = ROOT / "fixtures/e2e/project.json"
DEFAULT_EVIDENCE = ROOT / "fixtures/e2e/evidence.json"
DEFAULT_ARTIFACTS = ROOT / "artifacts/e2e"
SNAPSHOT_VERSION = "1.0"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_evidence(path: Path) -> list[EvidenceObservation]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0":
        raise ValueError("unsupported evidence schema_version")
    return [
        EvidenceObservation(
            item["evidence_id"],
            item["description"],
            {key: float(value) for key, value in item["likelihoods"].items()},
            source=item.get("source", "fixture-oracle"),
        )
        for item in payload["observations"]
    ]


def build_beliefs(project: ForgeMindProject) -> BayesianHypothesisSet:
    hypotheses = {candidate.candidate_id: candidate.description for candidate in project.candidate_specs}
    priors = {candidate_id: 1.0 for candidate_id in hypotheses}
    return BayesianHypothesisSet.from_priors(hypotheses, priors=priors, elimination_threshold=0.05, min_evidence=1)


def belief_snapshot(beliefs: BayesianHypothesisSet) -> list[dict[str, Any]]:
    return [belief.as_dict() for belief in beliefs.ranked()]


def replay(project: ForgeMindProject, observations: list[EvidenceObservation]) -> BayesianHypothesisSet:
    beliefs = build_beliefs(project)
    for observation in observations:
        beliefs.observe(observation)
    return beliefs


def run_cycle(project_path: Path, evidence_path: Path, artifact_dir: Path) -> dict[str, Any]:
    project_payload = json.loads(project_path.read_text(encoding="utf-8"))
    project = ForgeMindProject.from_dict(project_payload)
    observations = load_evidence(evidence_path)

    # Step 1–2: project and evidence enter the probabilistic engine.
    beliefs = replay(project, observations)
    posterior_ranking = [belief.hypothesis_id for belief in beliefs.top_k(len(project.candidate_specs))]
    if posterior_ranking[0] != "stable-sort":
        raise AssertionError(f"unexpected posterior winner: {posterior_ranking}")

    # Step 3: execute the public Python engine contract for the same project.
    engine_response = evaluate(EvaluateRequest(project=project.to_dict())).model_dump()
    advice_ranking = [
        project.candidate_specs[item["candidate_index"]].candidate_id
        for item in engine_response["results"]
    ]

    # Step 4: archive the evidence as a content-addressed local artifact.
    artifact_dir.mkdir(parents=True, exist_ok=True)
    archived_evidence = artifact_dir / evidence_path.name
    shutil.copy2(evidence_path, archived_evidence)
    archive_record = {
        "filename": archived_evidence.name,
        "source": "fixtures/e2e/evidence.json",
        "sha256": sha256(archived_evidence),
        "size_bytes": archived_evidence.stat().st_size,
        "mime_type": "application/json",
    }

    # Step 5: write a portable snapshot containing results and provenance.
    snapshot = {
        "snapshot_version": SNAPSHOT_VERSION,
        "project": project.to_dict(),
        "evidence": json.loads(evidence_path.read_text(encoding="utf-8")),
        "posterior_ranking": posterior_ranking,
        "posterior_state": belief_snapshot(beliefs),
        "advice_ranking": advice_ranking,
        "engine_response": engine_response,
        "archive": archive_record,
    }
    snapshot_path = artifact_dir / "snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # Step 6: restore by replaying the persisted project/evidence and verify identity.
    restored_project = ForgeMindProject.from_dict(snapshot["project"])
    restored_observations = [
        EvidenceObservation(
            item["evidence_id"],
            item["description"],
            {key: float(value) for key, value in item["likelihoods"].items()},
            source=item.get("source", "fixture-oracle"),
        )
        for item in snapshot["evidence"]["observations"]
    ]
    restored_beliefs = replay(restored_project, restored_observations)
    restored_state = belief_snapshot(restored_beliefs)
    if restored_state != snapshot["posterior_state"]:
        raise AssertionError("restored posterior state differs from snapshot")
    if sha256(archived_evidence) != snapshot["archive"]["sha256"]:
        raise AssertionError("archived evidence hash differs from snapshot")

    snapshot_reference = str(snapshot_path.relative_to(ROOT)) if snapshot_path.is_relative_to(ROOT) else str(snapshot_path)
    return {
        "cycle_version": SNAPSHOT_VERSION,
        "project": project.name,
        "candidate_count": len(project.candidate_specs),
        "evidence_count": len(observations),
        "posterior_ranking": posterior_ranking,
        "advice_ranking": advice_ranking,
        "archive": archive_record,
        "snapshot": snapshot_reference,
        "restoration_verified": True,
        "engine_contract_version": engine_response["contract_version"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--artifacts", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = run_cycle(args.project, args.evidence, args.artifacts)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
