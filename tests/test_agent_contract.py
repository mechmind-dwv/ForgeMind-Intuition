import pytest

from forgemind import AGENT_CONTRACT_VERSION, AGENT_OPERATIONS, AgentToolRequest, AgentToolResponse


def test_agent_request_is_versioned_and_serializable():
    request = AgentToolRequest("top_k", "project-1", {"k": 5}, request_id="req-1")
    assert request.as_dict() == {
        "contract_version": AGENT_CONTRACT_VERSION,
        "operation": "top_k",
        "project_id": "project-1",
        "payload": {"k": 5},
        "request_id": "req-1",
    }
    assert "record_evidence" in AGENT_OPERATIONS


@pytest.mark.parametrize("operation", ["unknown", "execute_arbitrary_code", "delete_project"])
def test_agent_request_rejects_unsupported_operations(operation):
    with pytest.raises(ValueError, match="unsupported agent operation"):
        AgentToolRequest(operation, "project-1", {})


def test_agent_request_rejects_wrong_version_and_empty_project():
    with pytest.raises(ValueError, match="unsupported agent contract version"):
        AgentToolRequest("top_k", "project-1", {}, contract_version="2.0")
    with pytest.raises(ValueError, match="project_id"):
        AgentToolRequest("top_k", "", {})


def test_agent_response_requires_consistent_success_or_error_envelope():
    success = AgentToolResponse("explain", True, data={"reason": "evidence-backed"}, request_id="req-1")
    failure = AgentToolResponse("record_evidence", False, error={"code": "INVALID_EVIDENCE"})
    assert success.as_dict()["ok"] is True
    assert failure.as_dict()["error"]["code"] == "INVALID_EVIDENCE"
    with pytest.raises(ValueError, match="successful responses"):
        AgentToolResponse("top_k", True, error={"code": "invalid"})
    with pytest.raises(ValueError, match="failed responses"):
        AgentToolResponse("top_k", False)
