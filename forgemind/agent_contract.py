"""Versioned, transport-neutral contracts for coding-agent integrations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Mapping

AGENT_CONTRACT_VERSION = "1.0"
AGENT_OPERATIONS = frozenset(
    {
        "register_hypothesis",
        "top_k",
        "propose_probe",
        "record_evidence",
        "explain",
        "park",
        "unpark",
        "restore_snapshot",
    }
)


@dataclass(frozen=True)
class AgentToolRequest:
    """Validated request envelope for an explicit agent operation."""

    operation: str
    project_id: str
    payload: Mapping[str, Any]
    contract_version: str = AGENT_CONTRACT_VERSION
    request_id: str | None = None

    def __post_init__(self) -> None:
        if self.contract_version != AGENT_CONTRACT_VERSION:
            raise ValueError(f"unsupported agent contract version: {self.contract_version}")
        if self.operation not in AGENT_OPERATIONS:
            raise ValueError(f"unsupported agent operation: {self.operation}")
        if not self.project_id.strip():
            raise ValueError("project_id must not be empty")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a mapping")

    def as_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "operation": self.operation,
            "project_id": self.project_id,
            "payload": dict(self.payload),
            "request_id": self.request_id,
        }


@dataclass(frozen=True)
class AgentToolResponse:
    """Auditable response envelope; data never represents proof by itself."""

    operation: str
    ok: bool
    data: Mapping[str, Any] | None = None
    error: Mapping[str, Any] | None = None
    contract_version: str = AGENT_CONTRACT_VERSION
    request_id: str | None = None

    def __post_init__(self) -> None:
        if self.contract_version != AGENT_CONTRACT_VERSION:
            raise ValueError(f"unsupported agent contract version: {self.contract_version}")
        if self.ok and self.error is not None:
            raise ValueError("successful responses cannot contain error")
        if not self.ok and self.error is None:
            raise ValueError("failed responses must contain error")

    def as_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "operation": self.operation,
            "ok": self.ok,
            "data": dict(self.data or {}),
            "error": dict(self.error) if self.error is not None else None,
            "request_id": self.request_id,
        }


__all__ = ["AGENT_CONTRACT_VERSION", "AGENT_OPERATIONS", "AgentToolRequest", "AgentToolResponse"]
