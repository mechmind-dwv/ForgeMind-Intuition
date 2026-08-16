#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${FORGEMIND_RUN_DIR:-$ROOT/.forgemind-run}"
ENGINE_HOST="${FORGEMIND_ENGINE_HOST:-127.0.0.1}"
ENGINE_PORT="${FORGEMIND_ENGINE_PORT:-8787}"
WEB_PORT="${FORGEMIND_WEB_PORT:-3000}"
MODE="${1:-dev}"

mkdir -p "$RUN_DIR"
cd "$ROOT"

port_in_use() {
  python - "$1" <<'PY'
import socket
import sys
with socket.socket() as sock:
    raise SystemExit(0 if sock.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0 else 1)
PY
}

require_engine_dependencies() {
  python - <<'PY'
try:
    import fastapi  # noqa: F401
    import uvicorn  # noqa: F401
except ImportError as error:
    raise SystemExit(
        "Faltan dependencias del Engine API. Ejecuta: "
        "python -m pip install -e '.[dev,vectorized]'"
    ) from error
PY
}

start_process() {
  local name="$1"; shift
  local pid_file="$RUN_DIR/$name.pid"
  local log_file="$RUN_DIR/$name.log"
  if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
    printf '%s ya está activo (PID %s)\n' "$name" "$(cat "$pid_file")"
    return 0
  fi
  rm -f "$pid_file"
  nohup "$@" >"$log_file" 2>&1 &
  echo $! >"$pid_file"
  printf '%s iniciado (PID %s, log %s)\n' "$name" "$(cat "$pid_file")" "$log_file"
}

command -v python >/dev/null || { echo 'Falta python.' >&2; exit 1; }
command -v pnpm >/dev/null || { echo 'Falta pnpm.' >&2; exit 1; }
require_engine_dependencies

if port_in_use "$ENGINE_PORT"; then
  echo "El puerto del motor $ENGINE_PORT ya está ocupado. Ejecuta forge-stop.sh o usa FORGEMIND_ENGINE_PORT=otro_puerto." >&2
  exit 1
fi
if port_in_use "$WEB_PORT"; then
  echo "El puerto web $WEB_PORT ya está ocupado. Ejecuta forge-stop.sh o usa FORGEMIND_WEB_PORT=otro_puerto." >&2
  exit 1
fi

if [ "$MODE" = "production" ]; then
  (cd "$ROOT/frontend" && pnpm build)
  start_process engine python -m uvicorn services.engine_api:app --host "$ENGINE_HOST" --port "$ENGINE_PORT"
  start_process web env NODE_ENV=production PORT="$WEB_PORT" FORGEMIND_ENGINE_URL="http://$ENGINE_HOST:$ENGINE_PORT" pnpm --dir "$ROOT/frontend" start
elif [ "$MODE" = "dev" ]; then
  start_process engine python -m uvicorn services.engine_api:app --host "$ENGINE_HOST" --port "$ENGINE_PORT"
  start_process frontend pnpm --dir "$ROOT/frontend" dev --host "$ENGINE_HOST" --port "$WEB_PORT" --strictPort
else
  echo "Uso: $0 [dev|production]" >&2
  exit 2
fi

printf '\nMotor:   http://%s:%s/health\n' "$ENGINE_HOST" "$ENGINE_PORT"
printf 'Frontend: http://%s:%s/\n' "$ENGINE_HOST" "$WEB_PORT"
printf 'Estado:  bash scripts/forge-status.sh\n'
printf 'Parar:   bash scripts/forge-stop.sh\n'
