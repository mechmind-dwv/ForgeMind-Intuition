"""Controlled subprocess execution for probes and oracle adapters.

This module provides resource limits and an audit record. It is not a
container or kernel sandbox; untrusted multi-tenant execution still requires a
separate isolation boundary such as a container or worker VM.
"""

from __future__ import annotations

import os
import signal
import subprocess
import time
from dataclasses import dataclass
from typing import Sequence

try:
    import resource
except ImportError:  # pragma: no cover - non-POSIX fallback
    resource = None  # type: ignore[assignment]


@dataclass(frozen=True)
class ExecutionPolicy:
    timeout_seconds: float = 5.0
    cpu_seconds: int = 5
    memory_bytes: int = 512 * 1024 * 1024
    max_output_bytes: int = 1 * 1024 * 1024

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0 or self.cpu_seconds <= 0 or self.memory_bytes <= 0 or self.max_output_bytes <= 0:
            raise ValueError("execution limits must be positive")


@dataclass(frozen=True)
class ExecutionAudit:
    argv: tuple[str, ...]
    return_code: int | None
    timed_out: bool
    duration_ms: float
    stdout_bytes: int
    stderr_bytes: int
    limit_exceeded: bool = False


@dataclass(frozen=True)
class ExecutionResult:
    stdout: bytes
    stderr: bytes
    audit: ExecutionAudit


def _limit_child(policy: ExecutionPolicy) -> None:
    if resource is None:
        return
    resource.setrlimit(resource.RLIMIT_CPU, (policy.cpu_seconds, policy.cpu_seconds))
    resource.setrlimit(resource.RLIMIT_AS, (policy.memory_bytes, policy.memory_bytes))
    resource.setrlimit(resource.RLIMIT_FSIZE, (policy.max_output_bytes, policy.max_output_bytes))


def run_controlled(argv: Sequence[str], *, input_bytes: bytes = b"", policy: ExecutionPolicy | None = None) -> ExecutionResult:
    """Run an argv vector with limits and return output plus an audit record."""
    if not argv or any(not str(part) for part in argv):
        raise ValueError("argv must contain at least one non-empty argument")
    policy = policy or ExecutionPolicy()
    command = tuple(str(part) for part in argv)
    started = time.perf_counter()
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
        preexec_fn=lambda: _limit_child(policy) if os.name == "posix" else None,
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(input=input_bytes, timeout=policy.timeout_seconds)
    except subprocess.TimeoutExpired as error:
        timed_out = True
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
        stderr = stderr or str(error).encode()
    duration_ms = (time.perf_counter() - started) * 1000
    limit_exceeded = process.returncode in {-signal.SIGXCPU, -signal.SIGKILL}
    audit = ExecutionAudit(command, process.returncode, timed_out, duration_ms, len(stdout), len(stderr), limit_exceeded)
    return ExecutionResult(stdout, stderr, audit)


__all__ = ["ExecutionAudit", "ExecutionPolicy", "ExecutionResult", "run_controlled"]
