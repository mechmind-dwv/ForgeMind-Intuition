import re

import pytest

from forgemind import CandidateInput, ProjectInput, ProjectValidationError
from forgemind.core import Node
from forgemind.project import ForgeMindProject


def test_external_project_contract_accepts_rich_candidates_and_round_trips():
    payload = {
        "schema_version": "1.0",
        "name": "external-sort-project",
        "candidates": [
            {
                "id": "sort-a",
                "description": "sort candidate",
                "source": "agent",
                "program": [{"kind": "U", "name": "sort"}],
                "metadata": {"language": "python"},
            }
        ],
        "probes": [[3, 1, 2]],
        "targets": [],
        "metadata": {"repository": "local"},
    }
    contract = ProjectInput.from_dict(payload)
    assert contract.candidates[0] == CandidateInput(
        "sort-a", "sort candidate", (Node("U", "sort"),), "agent", {"language": "python"}
    )
    restored = ForgeMindProject.from_dict(payload)
    assert restored.to_dict()["candidates"][0]["id"] == "sort-a"
    assert restored.as_input().probes == ((3, 1, 2),)


def test_legacy_candidate_lists_are_normalized_with_stable_ids():
    project = ForgeMindProject.from_dict({
        "name": "legacy",
        "candidates": [[{"kind": "U", "name": "rev"}]],
        "probes": [],
    })
    assert project.candidate_specs[0].candidate_id == "candidate-1"
    assert project.candidate_specs[0].source == "legacy"


@pytest.mark.parametrize("payload, message", [
    ({"name": "bad", "candidates": []}, "candidates must be a non-empty list"),
    ({"name": "bad", "candidates": [{"id": "x", "program": []}]}, "program must be a non-empty list"),
    ({"name": "bad", "candidates": [{"id": "x", "program": [{"name": "sort"}]}, {"id": "x", "program": [{"name": "rev"}]}]}, "candidate ids must be unique"),
    ({"name": "bad", "candidates": [{"id": "x", "program": [{"name": "sort"}]}], "probes": [["not-an-int"]]}, "probes[0] must contain integers"),
])
def test_external_contract_reports_actionable_validation_errors(payload, message):
    with pytest.raises(ProjectValidationError, match=re.escape(message)):
        ProjectInput.from_dict(payload)
