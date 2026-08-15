import sys

import pytest

from forgemind import ExecutionPolicy, run_controlled


def test_controlled_execution_returns_output_and_audit():
    result = run_controlled([sys.executable, "-c", "print('probe-ok')"], policy=ExecutionPolicy(timeout_seconds=2))
    assert result.stdout.strip() == b"probe-ok"
    assert result.audit.return_code == 0
    assert result.audit.timed_out is False
    assert result.audit.stdout_bytes == len(result.stdout)


def test_controlled_execution_records_nonzero_oracle_result():
    result = run_controlled([sys.executable, "-c", "import sys; print('oracle-error', file=sys.stderr); raise SystemExit(7)"], policy=ExecutionPolicy(timeout_seconds=2))
    assert result.audit.return_code == 7
    assert result.audit.timed_out is False
    assert result.stderr


def test_controlled_execution_kills_timeout_process_group():
    result = run_controlled([sys.executable, "-c", "import time; time.sleep(2)"], policy=ExecutionPolicy(timeout_seconds=0.05))
    assert result.audit.timed_out is True
    assert result.audit.return_code is not None
    assert result.audit.duration_ms < 1000


def test_controlled_execution_rejects_invalid_policy_and_argv():
    with pytest.raises(ValueError, match="limits"):
        ExecutionPolicy(timeout_seconds=0)
    with pytest.raises(ValueError, match="argv"):
        run_controlled([])
