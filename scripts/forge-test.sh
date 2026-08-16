#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENGINE_PORT="${FORGEMIND_ENGINE_PORT:-$(python - <<'PY'
import socket
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    print(sock.getsockname()[1])
PY
)}"
ENGINE_LOG="${ROOT}/.forgemind-test-engine.log"
ENGINE_PID=""

cleanup() {
  if [ -n "$ENGINE_PID" ] && kill -0 "$ENGINE_PID" 2>/dev/null; then
    kill "$ENGINE_PID" 2>/dev/null || true
    wait "$ENGINE_PID" 2>/dev/null || true
  fi
  rm -f "$ENGINE_LOG"
}
trap cleanup EXIT

cd "$ROOT"
python - <<'PY'
try:
    import fastapi  # noqa: F401
    import uvicorn  # noqa: F401
except ImportError as error:
    raise SystemExit(
        "Faltan FastAPI/Uvicorn. Ejecuta: python -m pip install -e '.[dev,vectorized]'"
    ) from error
PY
printf '%s\n' '== Python: suite completa =='
python -m pytest -q

printf '%s\n' '== Engine API: arranque temporal =='
python -m uvicorn services.engine_api:app --host 127.0.0.1 --port "$ENGINE_PORT" >"$ENGINE_LOG" 2>&1 &
ENGINE_PID=$!

python - "$ENGINE_PORT" <<'PY'
import json
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

port = sys.argv[1]
base = f"http://127.0.0.1:{port}"
for _ in range(50):
    try:
        with urlopen(f"{base}/health", timeout=1) as response:
            health = json.load(response)
        assert health["status"] == "ok"
        assert health["contract_version"] == "1.0", health
        break
    except Exception:
        time.sleep(0.2)
else:
    raise SystemExit("Engine API no respondió a /health")

project = {
    "schema_version": "1.0",
    "name": "termux-smoke",
    "candidates": [{
        "id": "candidate-1",
        "description": "Minimal smoke candidate",
        "program": [{"kind": "U", "name": "identity", "arg": None}],
        "source": "smoke",
        "metadata": {},
    }],
    "probes": [],
    "targets": [],
    "metadata": {},
    "knowledge": [],
}
request = Request(
    f"{base}/v1/evaluate",
    data=json.dumps({"project": project}).encode(),
    headers={"content-type": "application/json"},
    method="POST",
)
try:
    with urlopen(request, timeout=5) as response:
        payload = json.load(response)
except HTTPError as error:
    raise SystemExit(f"Engine API devolvió HTTP {error.code}") from error
assert payload["engine"] == "forgemind-python"
assert payload["contract_version"] == "1.0"
print("Engine API smoke: OK")
PY

printf '%s\n' '== Frontend: typecheck =='
(cd "$ROOT/frontend" && pnpm check)
printf '%s\n' '== Frontend: tests =='
(cd "$ROOT/frontend" && pnpm test)
printf '%s\n' '== Frontend: build =='
(cd "$ROOT/frontend" && pnpm build)
printf '%s\n' '== TODO CORRECTO: motor, API y frontend validados =='
