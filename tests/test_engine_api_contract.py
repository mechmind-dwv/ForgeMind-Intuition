import pytest

from services.engine_api import ENGINE_API_CONTRACT_VERSION, EvaluateRequest, evaluate, health


def valid_project() -> dict:
    return {
        "schema_version": "1.0",
        "name": "contract-fixture",
        "candidates": [
            {
                "id": "candidate-1",
                "description": "minimal candidate",
                "source": "test",
                "program": [{"kind": "U", "name": "sort"}],
                "metadata": {"language": "python"},
            }
        ],
        "probes": [[3, 1, 2]],
        "targets": [],
        "metadata": {},
    }


def test_health_exposes_versioned_contract():
    response = health()
    assert response["status"] == "ok"
    assert response["engine"] == "forgemind-python"
    assert response["contract_version"] == ENGINE_API_CONTRACT_VERSION


def test_evaluate_exposes_versioned_contract_and_candidate_count():
    response = evaluate(EvaluateRequest(project=valid_project()))
    assert response.contract_version == ENGINE_API_CONTRACT_VERSION
    assert response.project == "contract-fixture"
    assert response.candidate_count == 1
    assert isinstance(response.results, list)


def test_evaluate_rejects_invalid_project_with_422_contract():
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as error:
        evaluate(EvaluateRequest(project={"schema_version": "1.0", "name": "invalid", "candidates": []}))

    assert error.value.status_code == 422
    assert isinstance(error.value.detail, str)
